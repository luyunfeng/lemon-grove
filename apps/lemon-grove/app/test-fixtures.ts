// Synthetic test data only; never import in production or load local knowledge files.
import { KNOWLEDGE_SOURCE, type KnowledgeSnapshot, type Note } from "./notes";
export function makeNote(overrides: Partial<Note> = {}): Note {
  return {
    id: "concepts/test-verification", slot: "01", category: "concept",
    title: "验证原则", excerpt: "用证据确认完成条件", domain: "测试工程",
    readTime: "1 分钟", tags: ["verification"], entities: ["test-runner"],
    markdown: "正文校验口令：EvidenceToken。",
    sourceUrl: `${KNOWLEDGE_SOURCE.url}/blob/main/wiki/concepts/test-verification.md`,
    ...overrides,
  };
}
export function makeSnapshot(overrides: Partial<KnowledgeSnapshot> = {}): KnowledgeSnapshot {
  return {
    status: "ready", source: { ...KNOWLEDGE_SOURCE, revision: "abcdef0123456789" },
    notes: [
      makeNote(),
      makeNote({ id: "concepts/test-context", slot: "02", title: "上下文隔离",
        excerpt: "控制输入范围", tags: ["context-engineering"], entities: [],
        markdown: "每项任务使用独立上下文。" }),
      makeNote({ id: "entities/test-runner", slot: "03", category: "entity", title: "合成工具",
        excerpt: "执行检查", tags: ["verification", "tool-interface"],
        markdown: "工具正文：可以运行检查。" }),
      makeNote({ id: "roadmaps/test-practice", slot: "04", category: "roadmap", title: "实践路线",
        excerpt: "分阶段练习", tags: ["learning-path"], entities: [],
        markdown: "从最小练习开始。" }),
    ],
    ...overrides,
  };
}
