import { parseDocument } from "yaml";
import { KNOWLEDGE_SOURCE, type KnowledgeSnapshot, type Note, type NoteType } from "./notes";
import publication from "./knowledge-publication.json";

const API_ROOT = `https://api.github.com/repos/${KNOWLEDGE_SOURCE.repository}`;
const MAX_PAGES = 500;
const MAX_FILE_BYTES = 200_000;
const MAX_TOTAL_BYTES = 8_000_000;
const FOLDERS: Record<string, NoteType> = { concepts: "concept", entities: "entity", roadmaps: "roadmap", syntheses: "synthesis" };
type TreeEntry = { path: string; type: string; mode: string; size?: number };
type IndexEntry = { description: string; domain: string; order: number };

class SourceError extends Error {
  constructor(message: string, readonly status: "unavailable" | "rate_limited" = "unavailable", readonly retryAfterSeconds?: number, readonly authentication = false) { super(message); }
}

// Publish only knowledge pages; never read raw inputs, operation logs, or rules.
export function knowledgePageType(path: string): NoteType | null {
  if (path === "wiki/overview.md") return "overview";
  const match = /^wiki\/(concepts|entities|roadmaps|syntheses)\/[a-z0-9]+(?:-[a-z0-9]+)*\.md$/.exec(path);
  return match ? FOLDERS[match[1]] : null;
}

export function parseIndex(markdown: string): Map<string, IndexEntry> {
  const entries = new Map<string, IndexEntry>();
  let domain = "";
  for (const line of markdown.split(/\r?\n/)) {
    const heading = /^##\s+(.+)/.exec(line);
    if (heading) domain = heading[1].trim();
    const link = /^\s*-\s+\[[^\]]+\]\(([^)]+)\)\s*(?:—|–|-)\s*(.*)/.exec(line);
    if (!link) continue;
    const path = `wiki/${link[1].replace(/^\.\//, "")}`;
    if (knowledgePageType(path)) entries.set(path, { description: link[2].trim(), domain, order: entries.size });
  }
  return entries;
}

function stringList(value: unknown): string[] {
  if (!Array.isArray(value) || !value.every((item) => typeof item === "string")) throw new SourceError("知识页的标签或实体格式不符合知识库约定。");
  return [...new Set(value as string[])];
}

export function parseKnowledgePage(path: string, markdown: string, revision: string, entry?: IndexEntry): Note {
  const type = knowledgePageType(path);
  const frontmatter = /^\uFEFF?---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)([\s\S]*)$/.exec(markdown);
  if (!type || !frontmatter) throw new SourceError(`知识页 ${path} 缺少有效的页面头部。`);
  const document = parseDocument(frontmatter[1]);
  if (document.errors.length) throw new SourceError(`知识页 ${path} 的页面头部无法解析。`);
  const metadata = document.toJS({ maxAliasCount: 0 }) as Record<string, unknown>;
  if (!metadata || typeof metadata.title !== "string" || !metadata.title.trim() || metadata.type !== type) throw new SourceError(`知识页 ${path} 的标题或类型不符合知识库约定。`);
  const body = frontmatter[2].trim().replace(/^#\s+[^\n]+\n+/, "");
  const plain = body.replace(/<!--[^]*?-->/g, "").replace(/[`#>*_\[\]]/g, "").replace(/\s+/g, " ").trim();
  return {
    id: path.replace(/\.md$/, ""), slot: "", category: type, title: metadata.title.trim(),
    excerpt: entry?.description || plain.slice(0, 110), domain: entry?.domain || "",
    readTime: `${Math.max(1, Math.ceil(plain.length / 450))} 分钟`,
    tags: stringList(metadata.tags), entities: stringList(metadata.entities), markdown: body,
    sourceUrl: `${KNOWLEDGE_SOURCE.url}/blob/${revision}/${path}`,
  };
}

export function createKnowledgeSource(fetchImpl: typeof fetch = fetch, now: () => number = Date.now, publishedSnapshot?: KnowledgeSnapshot) {
  let cache: { token: string; snapshot: KnowledgeSnapshot; verifiedAt: number } | undefined;
  let pending: { token: string; promise: Promise<KnowledgeSnapshot> } | undefined;
  let currentToken: string | undefined;
  let generation = 0;

  async function github(path: string, token: string, raw = false): Promise<Response> {
    let response: Response;
    try {
      response = await fetchImpl(`${API_ROOT}${path}`, {
        headers: {
          Accept: raw ? "application/vnd.github.raw+json" : "application/vnd.github+json",
          Authorization: `Bearer ${token}`, "User-Agent": "SAVEPOINT-knowledge-reader", "X-GitHub-Api-Version": "2026-03-10",
        },
        signal: AbortSignal.timeout(15_000), redirect: "error",
      });
    } catch { throw new SourceError("暂时无法读取 GitHub，请稍后重新加载。"); }
    if (response.ok || response.status === 409) return response;
    if (response.status === 429 || (response.status === 403 && response.headers.get("x-ratelimit-remaining") === "0")) {
      const reset = Number(response.headers.get("x-ratelimit-reset"));
      const retry = Number(response.headers.get("retry-after")) || (reset ? Math.ceil(reset - now() / 1000) : 60);
      throw new SourceError("GitHub 读取次数暂时达到上限，请稍后重试。", "rate_limited", Math.max(1, retry));
    }
    if ([401, 403, 404].includes(response.status)) throw new SourceError("暂时无法访问知识库，请检查仓库的读取授权。", "unavailable", undefined, true);
    throw new SourceError("GitHub 暂时无法返回知识库内容，请稍后重试。");
  }

  async function readFile(path: string, revision: string, token: string) {
    const response = await github(`/contents/${path}?ref=${revision}`, token, true);
    const text = await response.text();
    if (!response.ok || new TextEncoder().encode(text).length > MAX_FILE_BYTES) throw new SourceError(`知识页 ${path} 无法读取或超过大小限制。`);
    return text;
  }

  async function readRemote(token: string): Promise<KnowledgeSnapshot> {
    const checkedAt = new Date(now()).toISOString();
    const headResponse = await github(`/commits/${KNOWLEDGE_SOURCE.branch}`, token);
    if (headResponse.status === 409) return { status: "empty", source: { ...KNOWLEDGE_SOURCE, checkedAt }, notes: [], message: "知识库还没有可读取的版本。内容合入后，重新加载即可。" };
    const head = await headResponse.json() as { sha: string; commit?: { committer?: { date?: string } } };
    if (!/^[a-f0-9]{40}$/.test(head.sha)) throw new SourceError("GitHub 返回的知识库版本无效。");
    if (cache?.token === token && cache.snapshot.source.revision === head.sha) return { ...cache.snapshot, status: cache.snapshot.notes.length ? "ready" : "empty", message: undefined, source: { ...cache.snapshot.source, checkedAt } };
    const tree = await (await github(`/git/trees/${head.sha}?recursive=1`, token)).json() as { tree: TreeEntry[]; truncated?: boolean };
    if (!Array.isArray(tree.tree) || tree.truncated) throw new SourceError("知识库目录无法完整读取，请稍后重试。");
    // A symlink or submodule is never treated as a knowledge page.
    const files = tree.tree.filter((file) => file.type === "blob" && /^100(644|755)$/.test(file.mode));
    const pages = files.filter((file) => knowledgePageType(file.path));
    if (pages.length > MAX_PAGES || pages.some((file) => (file.size ?? 0) > MAX_FILE_BYTES) || pages.reduce((size, file) => size + (file.size ?? 0), 0) > MAX_TOTAL_BYTES) throw new SourceError("知识库内容超过当前读取容量，请调整站点的读取配置。");
    const index = files.some((file) => file.path === "wiki/index.md") ? parseIndex(await readFile("wiki/index.md", head.sha, token)) : new Map<string, IndexEntry>();
    pages.sort((a, b) => (index.get(a.path)?.order ?? MAX_PAGES) - (index.get(b.path)?.order ?? MAX_PAGES) || a.path.localeCompare(b.path));
    const notes = new Array<Note>(pages.length);
    let cursor = 0;
    await Promise.all(Array.from({ length: Math.min(5, pages.length) }, async () => {
      while (cursor < pages.length) {
        const position = cursor++;
        const path = pages[position].path;
        const note = parseKnowledgePage(path, await readFile(path, head.sha, token), head.sha, index.get(path));
        notes[position] = { ...note, slot: String(position + 1).padStart(2, "0") };
      }
    }));
    return {
      status: notes.length ? "ready" : "empty",
      source: { ...KNOWLEDGE_SOURCE, revision: head.sha, committedAt: head.commit?.committer?.date, checkedAt, delivery: "live" }, notes,
      ...(!notes.length ? { message: "知识库正在准备中。知识页合入后，重新加载即可阅读。" } : {}),
    };
  }

  async function load(token?: string): Promise<KnowledgeSnapshot> {
    token = token?.trim() || undefined;
    if (currentToken !== token) {
      currentToken = token;
      generation++;
      cache = undefined;
      pending = undefined;
    }
    if (!token) {
      if (publishedSnapshot) return publishedSnapshot;
      return { status: "setup_required", source: KNOWLEDGE_SOURCE, notes: [], message: "知识库的读取连接尚未完成。连接完成后，这里会显示已整理的知识页。" };
    }
    if (cache?.token === token && now() - cache.verifiedAt < KNOWLEDGE_SOURCE.cacheSeconds * 1000) return cache.snapshot;
    if (pending?.token === token) return pending.promise;
    const requestGeneration = generation;
    const changedConnection = (): KnowledgeSnapshot => publishedSnapshot ?? ({ status: "unavailable", source: KNOWLEDGE_SOURCE, notes: [], message: "知识库的读取连接已变化，请重新加载。" });
    const promise = (async (): Promise<KnowledgeSnapshot> => {
      try {
        const snapshot = await readRemote(token);
        if (requestGeneration !== generation) return changedConnection();
        cache = { token, snapshot, verifiedAt: now() };
        return snapshot;
      } catch (error) {
        if (requestGeneration !== generation) return changedConnection();
        const failure = error instanceof SourceError ? error : new SourceError("知识库内容暂时无法读取，请稍后重试。");
        if (failure.authentication) cache = undefined;
        if (cache?.token === token) return { ...cache.snapshot, status: "stale", message: `${failure.message} 当前保留上次成功读取的内容。`, retryAfterSeconds: failure.retryAfterSeconds };
        if (publishedSnapshot) return { ...publishedSnapshot, message: "当前显示从 GitHub 同步的发布版本。", retryAfterSeconds: failure.retryAfterSeconds };
        return { status: failure.authentication ? "access_denied" : failure.status, source: KNOWLEDGE_SOURCE, notes: [], message: failure.message, retryAfterSeconds: failure.retryAfterSeconds };
      }
    })();
    pending = { token, promise };
    try { return await promise; } finally { if (pending?.promise === promise) pending = undefined; }
  }
  return { load };
}

const source = createKnowledgeSource(fetch, Date.now, publication as KnowledgeSnapshot);
export const loadKnowledge = source.load;
