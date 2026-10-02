// @vitest-environment node
import { describe, expect, it, vi } from "vitest";
import { createKnowledgeSource, knowledgePageType, parseIndex, parseKnowledgePage } from "./knowledge-source";
import { KNOWLEDGE_SOURCE } from "./notes";

// All fixtures are synthetic; no repository snapshot or real credentials are read.
const SHA = "a".repeat(40);
const NEXT_SHA = "b".repeat(40);
const TOKEN = "synthetic-test-token";
const ROOT = `https://api.github.com/repos/${KNOWLEDGE_SOURCE.repository}`;
const PAGE = "wiki/concepts/test-concept.md";
const START = Date.UTC(2026, 9, 1);
const TTL = 300_000;
const markdown = (title = "合成概念", type = "concept") =>
  `---\ntitle: ${title}\ntype: ${type}\ntags: [verification, verification]\nentities: []\n---\n# ${title}\n\n验证合成数据的正文。\n\n## 边界\n保留 Markdown。`;
const json = (value: unknown, status = 200, headers?: HeadersInit) =>
  new Response(JSON.stringify(value), { status, headers });
const blob = (path: string, mode = "100644") => ({ path, mode, type: "blob", size: 200 });

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((done) => { resolve = done; });
  return { promise, resolve };
}

function fixture() {
  let time = START;
  let revision = SHA;
  let headFailure: Response | undefined;
  const fetchMock = vi.fn<typeof fetch>(async (input) => {
    const url = String(input);
    if (url === `${ROOT}/commits/main`) return headFailure?.clone() ?? json({ sha: revision });
    if (url === `${ROOT}/git/trees/${revision}?recursive=1`) {
      return json({ tree: [blob("wiki/index.md"), blob(PAGE)] });
    }
    if (url === `${ROOT}/contents/wiki/index.md?ref=${revision}`) {
      return new Response("## 验证\n- [概念](concepts/test-concept.md) — 索引摘要");
    }
    if (url === `${ROOT}/contents/${PAGE}?ref=${revision}`) return new Response(markdown());
    throw new Error(`Unexpected mock request: ${url}`);
  });
  return {
    fetchMock,
    source: createKnowledgeSource(fetchMock, () => time),
    advance: (milliseconds = TTL) => { time += milliseconds; },
    setRevision: (sha: string) => { revision = sha; },
    failHead: (response?: Response) => { headFailure = response; },
  };
}

describe("GitHub knowledge parsing", () => {
  it("whitelists only flat knowledge pages and overview", () => {
    const allowed = {
      "wiki/overview.md": "overview",
      "wiki/concepts/test-concept.md": "concept",
      "wiki/entities/test-tool.md": "entity",
      "wiki/roadmaps/test-plan.md": "roadmap",
      "wiki/syntheses/test-result.md": "synthesis",
    };
    for (const [path, type] of Object.entries(allowed)) expect(knowledgePageType(path)).toBe(type);
    for (const path of ["raw/test.md", "wiki/log.md", "wiki/index.md", "AGENTS.md", "CLAUDE.md",
      "templates/concept.md", "wiki/unknown/test.md", "wiki/concepts/deep/test.md",
      "wiki/concepts/../secret.md", "wiki/concepts/Test.md", "wiki/concepts/test.txt"]) {
      expect(knowledgePageType(path), path).toBeNull();
    }
  });

  it("uses index headings, relative links and descriptions while rejecting nonknowledge targets", () => {
    const index = parseIndex("## 方法\r\n- [概念](./concepts/test-concept.md) — 索引摘要\r\n"
      + "- [raw](../raw/test.md) — 禁止\n- [外链](https://example.com/page.md) — 禁止\n"
      + "## 工具\n- [工具](entities/test-tool.md) - 工具说明\n- [日志](log.md) — 禁止");
    expect([...index.entries()]).toEqual([
      [PAGE, { domain: "方法", description: "索引摘要", order: 0 }],
      ["wiki/entities/test-tool.md", { domain: "工具", description: "工具说明", order: 1 }],
    ]);
    const note = parseKnowledgePage(PAGE, `\uFEFF${markdown().replace(/\n/g, "\r\n")}`, SHA, index.get(PAGE));
    expect(note).toMatchObject({ title: "合成概念", category: "concept", tags: ["verification"],
      entities: [], excerpt: "索引摘要", domain: "方法", readTime: "1 分钟" });
    expect(note.markdown).not.toContain("# 合成概念");
    expect(note.markdown).toContain("## 边界");
    expect(note.sourceUrl).toBe(`${KNOWLEDGE_SOURCE.url}/blob/${SHA}/${PAGE}`);
  });

  it.each([
    ["missing frontmatter", "# 正文"],
    ["wrong type", markdown("合成概念", "entity")],
    ["empty title", markdown().replace("title: 合成概念", "title: ''")],
    ["non-list tags", markdown().replace("tags: [verification, verification]", "tags: verification")],
    ["non-string entities", markdown().replace("entities: []", "entities: [42]")],
    ["invalid YAML", markdown().replace("entities: []", "entities: [")],
  ])("rejects %s instead of publishing malformed metadata", (_name, content) => {
    expect(() => parseKnowledgePage(PAGE, content, SHA)).toThrow();
  });
});

describe("GitHub snapshot and cache", () => {
  it("pins tree, index and all pages to one main SHA and never fetches excluded files", async () => {
    const pages = [PAGE, "wiki/entities/test-tool.md", "wiki/roadmaps/test-plan.md",
      "wiki/syntheses/test-result.md", "wiki/overview.md"];
    const excluded = ["raw/test.md", "raw/assets/test.md", "wiki/log.md", "AGENTS.md", "CLAUDE.md",
      "templates/test.md", "wiki/concepts/deep/test.md"];
    const fetchMock = vi.fn<typeof fetch>(async (input, init) => {
      expect(new Headers(init?.headers).get("Authorization")).toBe(`Bearer ${TOKEN}`);
      expect(init?.redirect).toBe("error");
      const url = String(input);
      if (url === `${ROOT}/commits/main`) return json({ sha: SHA });
      if (url === `${ROOT}/git/trees/${SHA}?recursive=1`) return json({ tree: [
        blob("wiki/index.md"), ...pages.map((path) => blob(path)), ...excluded.map((path) => blob(path)),
        blob("wiki/concepts/symlink.md", "120000"),
        { path: "wiki/concepts/submodule.md", mode: "160000", type: "commit" },
      ] });
      if (url === `${ROOT}/contents/wiki/index.md?ref=${SHA}`) {
        return new Response("## 工具\n- [工具](entities/test-tool.md) — 工具优先\n"
          + "## 概念\n- [概念](concepts/test-concept.md) — 概念其次");
      }
      const page = pages.find((path) => url === `${ROOT}/contents/${path}?ref=${SHA}`);
      if (page) {
        expect(new Headers(init?.headers).get("Accept")).toBe("application/vnd.github.raw+json");
        return new Response(markdown("合成知识", knowledgePageType(page)!));
      }
      throw new Error(`Unexpected mock request: ${url}`);
    });
    const snapshot = await createKnowledgeSource(fetchMock, () => START).load(TOKEN);
    expect(snapshot.status).toBe("ready");
    expect(snapshot.source.revision).toBe(SHA);
    expect(snapshot.notes).toHaveLength(5);
    expect(snapshot.notes.map((note) => note.slot)).toEqual(["01", "02", "03", "04", "05"]);
    expect(snapshot.notes.slice(0, 2).map((note) => note.id)).toEqual(["wiki/entities/test-tool", "wiki/concepts/test-concept"]);
    expect(snapshot.notes.every((note) => note.sourceUrl.includes(`/blob/${SHA}/`))).toBe(true);
    // Exact count detects even ignored/failed attempts to fetch forbidden paths.
    expect(fetchMock).toHaveBeenCalledTimes(8);
    expect(fetchMock.mock.calls.map(([url]) => String(url))).toEqual(expect.arrayContaining([
      `${ROOT}/commits/main`, `${ROOT}/git/trees/${SHA}?recursive=1`,
      `${ROOT}/contents/wiki/index.md?ref=${SHA}`, ...pages.map((path) => `${ROOT}/contents/${path}?ref=${SHA}`),
    ]));
  });

  it("makes no network request without credentials and clears previously cached data", async () => {
    const { source, fetchMock } = fixture();
    for (const token of [undefined, "", "  "]) {
      expect(await source.load(token)).toMatchObject({ status: "setup_required", notes: [] });
    }
    expect(fetchMock).not.toHaveBeenCalled();
    expect((await source.load(TOKEN)).status).toBe("ready");
    expect((await source.load()).status).toBe("setup_required");
    fetchMock.mockClear();
    expect((await source.load(TOKEN)).status).toBe("ready");
    expect(fetchMock).toHaveBeenCalledTimes(4);
  });

  it("treats an empty repository HTTP 409 as empty without fetching its tree", async () => {
    const { source, fetchMock, failHead } = fixture();
    failHead(json({ message: "Git Repository is empty." }, 409));
    expect(await source.load(TOKEN)).toMatchObject({ status: "empty", notes: [] });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("caches for exactly five minutes and rechecks unchanged SHA without rereading files", async () => {
    const { source, fetchMock, advance } = fixture();
    const first = await source.load(TOKEN);
    expect(KNOWLEDGE_SOURCE.cacheSeconds).toBe(300);
    fetchMock.mockClear();
    advance(TTL - 1);
    expect(await source.load(TOKEN)).toBe(first);
    expect(fetchMock).not.toHaveBeenCalled();
    advance(1);
    const refreshed = await source.load(TOKEN);
    expect(refreshed.status).toBe("ready");
    expect(refreshed.notes).toEqual(first.notes);
    expect(refreshed.source.checkedAt).toBe(new Date(START + TTL).toISOString());
    expect(fetchMock.mock.calls.map(([url]) => String(url))).toEqual([`${ROOT}/commits/main`]);
    fetchMock.mockClear();
    expect(await source.load(TOKEN)).toBe(refreshed);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("reads a changed SHA and preserves the previous complete snapshot when a new page fails", async () => {
    const { source, fetchMock, advance, setRevision } = fixture();
    const first = await source.load(TOKEN);
    advance();
    setRevision(NEXT_SHA);
    fetchMock.mockImplementationOnce(async () => json({ sha: NEXT_SHA }));
    fetchMock.mockImplementationOnce(async () => json({ tree: [blob(PAGE)] }));
    fetchMock.mockImplementationOnce(async () => new Response("invalid frontmatter"));
    const failed = await source.load(TOKEN);
    expect(failed).toMatchObject({ status: "stale", notes: first.notes, source: { revision: SHA } });
    expect(failed.message).toContain("上次成功读取");
    const recovered = await source.load(TOKEN);
    expect(recovered.status).toBe("ready");
    expect(recovered.source.revision).toBe(NEXT_SHA);
    expect(recovered.notes[0].sourceUrl).toContain(`/blob/${NEXT_SHA}/`);
  });

  it("keeps old data marked stale on transport failures and retries instead of caching the failure", async () => {
    const { source, fetchMock, advance } = fixture();
    const first = await source.load(TOKEN);
    advance();
    fetchMock.mockRejectedValueOnce(new TypeError("synthetic network failure"));
    expect(await source.load(TOKEN)).toMatchObject({ status: "stale", notes: first.notes });
    expect((await source.load(TOKEN)).status).toBe("ready");
    expect(fetchMock).toHaveBeenCalledTimes(6);
  });

  it("clears the cache after HTTP 401 so later failures cannot expose revoked data", async () => {
    const { source, fetchMock, advance, failHead } = fixture();
    await source.load(TOKEN);
    advance();
    failHead(json({}, 401));
    expect(await source.load(TOKEN)).toMatchObject({ status: "access_denied", notes: [] });
    failHead(json({}, 503));
    expect(await source.load(TOKEN)).toMatchObject({ status: "unavailable", notes: [] });
    expect(fetchMock).toHaveBeenCalledTimes(6);
  });

  it.each([
    [429, { "retry-after": "17" }, 17],
    [403, { "x-ratelimit-remaining": "0", "x-ratelimit-reset": String(START / 1000 + 45) }, 45],
  ])("reports HTTP %s rate limiting and its retry interval", async (status, headers, seconds) => {
    const { source, fetchMock, failHead } = fixture();
    failHead(json({}, status, headers));
    expect(await source.load(TOKEN)).toMatchObject({ status: "rate_limited", notes: [], retryAfterSeconds: seconds });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("deduplicates concurrent requests with the same credential", async () => {
    const { source, fetchMock } = fixture();
    const head = deferred<Response>();
    fetchMock.mockImplementationOnce(() => head.promise);
    const calls = [source.load(TOKEN), source.load(TOKEN), source.load(TOKEN)];
    expect(fetchMock).toHaveBeenCalledTimes(1);
    head.resolve(json({ sha: SHA }));
    const snapshots = await Promise.all(calls);
    expect(snapshots.every((snapshot) => snapshot.status === "ready")).toBe(true);
    expect(snapshots[0]).toBe(snapshots[1]);
    expect(snapshots[1]).toBe(snapshots[2]);
    expect(fetchMock).toHaveBeenCalledTimes(4);
  });

  it("bounds concurrent page reads to five while preserving the final slot order", async () => {
    const paths = Array.from({ length: 12 }, (_, i) => `wiki/concepts/page-${String(i).padStart(2, "0")}.md`);
    const gate = deferred<void>();
    const started = deferred<void>();
    let active = 0;
    let peak = 0;
    const fetchMock = vi.fn<typeof fetch>(async (input) => {
      const url = String(input);
      if (url === `${ROOT}/commits/main`) return json({ sha: SHA });
      if (url === `${ROOT}/git/trees/${SHA}?recursive=1`) return json({ tree: paths.map((path) => blob(path)) });
      const path = paths.find((candidate) => url === `${ROOT}/contents/${candidate}?ref=${SHA}`);
      if (!path) throw new Error(`Unexpected mock request: ${url}`);
      active += 1;
      peak = Math.max(peak, active);
      if (active === 5) started.resolve();
      await gate.promise;
      active -= 1;
      return new Response(markdown(path));
    });
    const loading = createKnowledgeSource(fetchMock, () => START).load(TOKEN);
    await started.promise;
    expect(active).toBe(5);
    expect(fetchMock).toHaveBeenCalledTimes(7);
    gate.resolve();
    const snapshot = await loading;
    expect(snapshot.status).toBe("ready");
    expect(peak).toBe(5);
    expect(snapshot.notes.map((note) => note.id)).toEqual(paths.map((path) => path.replace(/\.md$/, "")));
    expect(snapshot.notes.map((note) => note.slot)).toEqual(paths.map((_, i) => String(i + 1).padStart(2, "0")));
  });

  it("does not repopulate the credential cache from an in-flight request after credentials are removed", async () => {
    const { source, fetchMock } = fixture();
    const head = deferred<Response>();
    fetchMock.mockImplementationOnce(() => head.promise);
    const loading = source.load(TOKEN);
    expect(await source.load()).toMatchObject({ status: "setup_required", notes: [] });
    head.resolve(json({ sha: SHA }));
    await loading;
    fetchMock.mockClear();
    fetchMock.mockResolvedValue(json({}, 401));
    // Reintroducing a revoked token must consult GitHub rather than reuse an old request's result.
    expect(await source.load(TOKEN)).toMatchObject({ status: "access_denied", notes: [] });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});
