// @vitest-environment node
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import publication from "./knowledge-publication.json";

type SourceModule = typeof import("./knowledge-source");
type PublishedSnapshot = NonNullable<
  Parameters<SourceModule["createKnowledgeSource"]>[2]
>;

const published = publication as PublishedSnapshot;
const repository = "luyunfeng/lemon-grove";
const publishedRevision = "d21eec3e56599f90c5bef6bdd2f6f482be20edf5";
const expectedIds = [
  "wiki/overview",
  "wiki/concepts/agentic-engineering",
  "wiki/concepts/context-engineering",
  "wiki/concepts/harness-engineering",
  "wiki/concepts/verification",
  "wiki/concepts/loop-engineering",
  "wiki/concepts/goal-vs-plan",
  "wiki/concepts/spec-driven-development",
  "wiki/concepts/sub-agent-orchestration",
  "wiki/concepts/rule-enforcement-layers",
  "wiki/concepts/compound-engineering",
  "wiki/concepts/confidence-in-prompts",
  "wiki/concepts/agent-tool-interface",
  "wiki/concepts/agent-native-doc",
  "wiki/concepts/agent-skill",
  "wiki/concepts/agent-skill-design",
  "wiki/concepts/skill-self-evolution",
  "wiki/concepts/recursive-self-improvement",
  "wiki/concepts/verifiable-rewards",
  "wiki/concepts/model-evaluation",
  "wiki/concepts/llm-wiki-pattern",
  "wiki/concepts/open-knowledge-format",
  "wiki/concepts/knowledge-base-design",
  "wiki/entities/claude-code",
  "wiki/entities/codex",
  "wiki/entities/claude-models",
  "wiki/entities/ecc",
  "wiki/entities/superpowers",
  "wiki/entities/mattpocock-skills",
  "wiki/roadmaps/agent-workflow-practice",
  "wiki/roadmaps/lillog-reading-path",
];

let createKnowledgeSource: SourceModule["createKnowledgeSource"];
let loadKnowledge: SourceModule["loadKnowledge"];
const blockedNetwork = vi.fn<typeof fetch>(async () => {
  throw new Error("Publication tests must not access the network");
});

beforeEach(async () => {
  blockedNetwork.mockClear();
  vi.stubGlobal("fetch", blockedNetwork);
  // Import after blocking fetch so the production singleton cannot capture it.
  vi.resetModules();
  ({ createKnowledgeSource, loadKnowledge } = await import("./knowledge-source"));
});

afterEach(() => {
  expect(blockedNetwork).not.toHaveBeenCalled();
  vi.unstubAllGlobals();
});

describe("GitHub publication", () => {
  it("identifies the published main revision with plausible source metadata", () => {
    expect(publication.status).toBe("ready");
    expect(publication.source).toMatchObject({
      provider: "github",
      repository,
      branch: "main",
      url: `https://github.com/${repository}`,
      delivery: "published",
      revision: publishedRevision,
    });
    expect(publication.source.revision).toMatch(/^[0-9a-f]{40}$/);
    const committedAt = Date.parse(publication.source.committedAt);
    const checkedAt = Date.parse(publication.source.checkedAt);
    expect(Number.isFinite(committedAt)).toBe(true);
    expect(Number.isFinite(checkedAt)).toBe(true);
    expect(checkedAt).toBeGreaterThanOrEqual(committedAt);
    expect(publication.source.cacheSeconds).toBeGreaterThan(0);
  });

  it("contains exactly the 31 allowed knowledge pages at that same revision", () => {
    const ids = publication.notes.map((note) => note.id);
    expect(ids).toHaveLength(31);
    expect(new Set(ids).size).toBe(31);
    expect([...ids].sort()).toEqual([...expectedIds].sort());
    const entityIds = new Set(
      ids.filter((id) => id.startsWith("wiki/entities/"))
        .map((id) => id.slice("wiki/entities/".length)),
    );

    for (const note of publication.notes) {
      expect(note.id).toMatch(
        /^wiki\/(?:overview|(?:concepts|entities|roadmaps|syntheses)\/[a-z0-9]+(?:-[a-z0-9]+)*)$/,
      );
      expect(note.sourceUrl).toBe(
        `https://github.com/${repository}/blob/${publishedRevision}/${note.id}.md`,
      );
      const expectedCategory = note.id === "wiki/overview" ? "overview"
        : note.id.startsWith("wiki/concepts/") ? "concept"
          : note.id.startsWith("wiki/entities/") ? "entity" : "roadmap";
      expect(note.category).toBe(expectedCategory);
      expect(note.title.trim().length).toBeGreaterThan(0);
      expect(note.excerpt.trim().length).toBeGreaterThan(0);
      expect(note.domain.trim().length).toBeGreaterThan(0);
      expect(note.markdown.trim().length).toBeGreaterThan(50);
      expect(note.readTime).toMatch(/^\d+ 分钟$/);
      expect(note.tags.length).toBeGreaterThan(0);
      for (const tag of note.tags) expect(tag).toMatch(/^[a-z0-9]+(?:-[a-z0-9]+)*$/);
      for (const entity of note.entities) expect(entityIds.has(entity)).toBe(true);
    }
  });

  it("loads the real 31-page production publication without a token or network", async () => {
    // No mock of the publication or loader: this exercises the production default.
    const result = await loadKnowledge();
    expect(result.status).toBe("ready");
    expect(result.source).toEqual(publication.source);
    expect(result.notes).toHaveLength(31);
    expect(result.notes).toEqual(publication.notes);
  });

  it("makes an explicitly supplied publication readable with no usable token", async () => {
    const source = createKnowledgeSource(blockedNetwork, Date.now, published);
    for (const token of [undefined, "", "   "]) {
      const result = await source.load(token);
      expect(result.status).toBe("ready");
      expect(result.source.delivery).toBe("published");
      expect(result.notes).toEqual(publication.notes);
    }
  });

  it.each(["401", "transport"])(
    "falls back to the publication after a live %s failure without a cache",
    async (failure) => {
      const transport = vi.fn<typeof fetch>(async () => {
        if (failure === "401") return new Response("Unauthorized", { status: 401 });
        throw new TypeError("Synthetic transport failure");
      });
      const source = createKnowledgeSource(transport, Date.now, published);
      const result = await source.load("synthetic-test-token");
      expect(transport).toHaveBeenCalledTimes(1);
      expect(result.status).toBe("ready");
      expect(result.source).toEqual(publication.source);
      expect(result.notes).toEqual(publication.notes);
    },
  );

  it("preserves the live cache ahead of the publication when refresh temporarily fails", async () => {
    // All live responses are synthetic; production publication data is never changed.
    const liveRevision = "1111111111111111111111111111111111111111";
    const pagePath = "wiki/concepts/publication-test.md";
    const liveBody = "这是合成 live 页面正文，用于验证缓存优先级。";
    const index = "# 知识地图\n\n## 测试\n- [发布测试](concepts/publication-test.md) — 合成夹具\n";
    const markdown = `---\ntitle: 发布测试\ntype: concept\ntags: [verification]\nentities: []\n---\n\n${liveBody}`;
    const api = `https://api.github.com/repos/${repository}`;
    const responses = new Map<string, () => Response>([
      [`${api}/commits/main`, () => Response.json({
        sha: liveRevision,
        commit: { committer: { date: "2026-10-02T00:00:00Z" } },
      })],
      [`${api}/git/trees/${liveRevision}?recursive=1`, () => Response.json({
        truncated: false,
        tree: ["wiki/index.md", pagePath].map((path) => ({
          path, type: "blob", mode: "100644", size: 200,
        })),
      })],
      [`${api}/contents/wiki/index.md?ref=${liveRevision}`, () => new Response(index)],
      [`${api}/contents/${pagePath}?ref=${liveRevision}`, () => new Response(markdown)],
    ]);
    const transport = vi.fn<typeof fetch>(async (input) => {
      const url = input instanceof Request ? input.url : String(input);
      const respond = responses.get(url);
      if (!respond) throw new Error(`Unexpected fixture request: ${url}`);
      return respond();
    });
    let now = Date.parse("2026-10-02T01:00:00Z");
    const source = createKnowledgeSource(transport, () => now, published);
    const live = await source.load("synthetic-test-token");
    expect(live.status).toBe("ready");
    expect(live.source).toMatchObject({ delivery: "live", revision: liveRevision });
    expect(live.notes).toHaveLength(1);
    expect(live.notes[0]).toMatchObject({
      id: "wiki/concepts/publication-test",
      markdown: liveBody,
      sourceUrl: `https://github.com/${repository}/blob/${liveRevision}/${pagePath}`,
    });

    now += live.source.cacheSeconds * 1_000 + 1;
    const callsBeforeRefresh = transport.mock.calls.length;
    transport.mockRejectedValueOnce(new TypeError("Synthetic temporary outage"));
    const fallback = await source.load("synthetic-test-token");
    expect(transport.mock.calls.length).toBeGreaterThan(callsBeforeRefresh);
    expect(fallback.source.delivery).toBe("live");
    expect(fallback.source.revision).toBe(liveRevision);
    expect(fallback.notes).toEqual(live.notes);
  });
});
