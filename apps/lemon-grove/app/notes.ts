export type NoteType = "concept" | "entity" | "roadmap" | "synthesis" | "overview";
export type Category = "all" | NoteType;

export const CATEGORY_LABELS: Record<Category, string> = {
  all: "全部", concept: "概念", entity: "工具与项目", roadmap: "学习路线", synthesis: "综合结论", overview: "概览",
};

export interface Note {
  id: string;
  slot: string;
  category: NoteType;
  title: string;
  excerpt: string;
  domain: string;
  readTime: string;
  tags: string[];
  entities: string[];
  markdown: string;
  sourceUrl: string;
}

export const KNOWLEDGE_SOURCE = {
  provider: "github" as const,
  repository: "luyunfeng/lemon-grove",
  branch: "main",
  url: "https://github.com/luyunfeng/lemon-grove",
  cacheSeconds: 300,
};

export interface KnowledgeSnapshot {
  status: "ready" | "empty" | "setup_required" | "access_denied" | "unavailable" | "rate_limited" | "stale";
  source: typeof KNOWLEDGE_SOURCE & { revision?: string; committedAt?: string; checkedAt?: string; delivery?: "published" | "live" };
  notes: Note[];
  message?: string;
  retryAfterSeconds?: number;
}

export function filterNotes(notes: readonly Note[], category: Category, query: string): Note[] {
  const needle = query.trim().toLocaleLowerCase("zh-CN");
  return notes.filter((note) => {
    const text = [note.title, note.excerpt, note.domain, note.markdown, ...note.tags, ...note.entities]
      .join(" ").toLocaleLowerCase("zh-CN");
    return (category === "all" || note.category === category) && (!needle || text.includes(needle));
  });
}
