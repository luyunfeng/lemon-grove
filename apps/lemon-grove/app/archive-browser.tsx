"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { CATEGORY_LABELS, KNOWLEDGE_SOURCE, filterNotes, type Category, type KnowledgeSnapshot, type Note } from "./notes";

const CATEGORIES = Object.keys(CATEGORY_LABELS) as Category[];
const STATUS_LABELS = { ready: "已读取", stale: "显示上次内容", empty: "等待知识页", setup_required: "等待连接", access_denied: "读取授权失效", unavailable: "暂时无法读取", rate_limited: "稍后重试" };

function NoteCard({ note, selected, onSelect }: { note: Note; selected: boolean; onSelect: (id: string) => void }) {
  return (
    <button type="button" className="note-card" aria-label={`打开：${note.title}`} aria-pressed={selected} onClick={() => onSelect(note.id)}>
      <span className="note-card-console"><span className="note-slot" aria-hidden="true">SLOT {note.slot}</span><span className="note-category">{CATEGORY_LABELS[note.category]}</span></span>
      <span className="note-card-title">{note.title}</span>
      <span className="note-excerpt">{note.excerpt}</span>
      <span className="note-meta"><span>{note.domain || CATEGORY_LABELS[note.category]}</span><span>{note.readTime}</span></span>
      <span className="note-tags" aria-hidden="true">{note.tags.slice(0, 3).map((tag) => <span key={tag}>#{tag}</span>)}{note.tags.length > 3 ? <span>+{note.tags.length - 3}</span> : null}</span>
    </button>
  );
}

function ReaderPanel({ note, onTagSelect }: { note: Note; onTagSelect: (tag: string) => void }) {
  return (
    <article className="reader-panel" aria-labelledby={`reader-${note.slot}`}>
      <header className="reader-header">
        <p>SLOT {note.slot} · {CATEGORY_LABELS[note.category]}</p>
        <h2 id={`reader-${note.slot}`}>{note.title}</h2>
        <div className="reader-meta"><span>{note.readTime}</span>{note.domain ? <span>{note.domain}</span> : null}<a href={note.sourceUrl} target="_blank" rel="noreferrer">在 GitHub 阅读</a></div>
        <ul className="reader-tags" aria-label="标签">{note.tags.map((tag) => <li key={tag}><button type="button" aria-label={`按 ${tag} 筛选`} onClick={() => onTagSelect(tag)}>#{tag}</button></li>)}</ul>
        {note.entities.length ? <p className="reader-entities">涉及：{note.entities.join(" · ")}</p> : null}
      </header>
      <div className="reader-body">
        <ReactMarkdown remarkPlugins={[remarkGfm]} skipHtml components={{
          a: ({ children, href }) => <a href={href} target="_blank" rel="noreferrer">{children}</a>,
          table: ({ children }) => <div className="markdown-table"><table>{children}</table></div>,
        }}>{note.markdown}</ReactMarkdown>
      </div>
    </article>
  );
}

function isSnapshot(value: unknown): value is KnowledgeSnapshot {
  if (!value || typeof value !== "object") return false;
  const data = value as KnowledgeSnapshot;
  return Object.hasOwn(STATUS_LABELS, data.status) && data.source?.repository === KNOWLEDGE_SOURCE.repository && data.source?.branch === KNOWLEDGE_SOURCE.branch && Array.isArray(data.notes) && data.notes.every((note) =>
    typeof note.id === "string" && typeof note.title === "string" && typeof note.markdown === "string" && Object.hasOwn(CATEGORY_LABELS, note.category) && note.category !== ("all" as string) && Array.isArray(note.tags) && Array.isArray(note.entities));
}

export default function ArchiveBrowser({ initialSnapshot }: { initialSnapshot: KnowledgeSnapshot }) {
  const [snapshot, setSnapshot] = useState(initialSnapshot);
  const [loading, setLoading] = useState(false);
  const [category, setCategory] = useState<Category>("all");
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState(initialSnapshot.notes[0]?.id ?? "");
  const activeRequest = useRef<AbortController | null>(null);
  const lastAttempt = useRef(0);
  const retryAt = useRef(0);

  const reload = useCallback(async () => {
    if (Date.now() < retryAt.current) return;
    activeRequest.current?.abort();
    const controller = new AbortController();
    activeRequest.current = controller;
    lastAttempt.current = Date.now();
    setLoading(true);
    const timeout = setTimeout(() => controller.abort(), 60_000);
    try {
      const response = await fetch("/api/knowledge", { signal: controller.signal, cache: "no-store" });
      const data: unknown = await response.json();
      if (!isSnapshot(data)) throw new Error("Invalid knowledge response");
      if (controller !== activeRequest.current) return;
      retryAt.current = data.retryAfterSeconds ? Date.now() + data.retryAfterSeconds * 1000 : 0;
      setSnapshot((previous) => {
        if (["unavailable", "rate_limited"].includes(data.status) && !data.notes.length && previous.notes.length) {
          return { ...previous, status: "stale", message: `${data.message ?? "这次读取没有完成。"} 当前保留上次成功读取的内容。`, retryAfterSeconds: data.retryAfterSeconds };
        }
        return data;
      });
    } catch {
      if (controller !== activeRequest.current) return;
      setSnapshot((previous) => ({ ...previous, status: previous.notes.length ? "stale" : "unavailable", message: previous.notes.length ? "这次读取没有完成，保留上次成功读取的内容。" : "暂时无法读取知识库，请稍后重新加载。" }));
    } finally {
      clearTimeout(timeout);
      if (controller === activeRequest.current) setLoading(false);
    }
  }, []);

  useEffect(() => {
    lastAttempt.current = Date.now();
    function refreshIfDue() {
      if (!document.hidden && Date.now() - lastAttempt.current >= KNOWLEDGE_SOURCE.cacheSeconds * 1000) void reload();
    }
    const timer = setInterval(refreshIfDue, KNOWLEDGE_SOURCE.cacheSeconds * 1000);
    document.addEventListener("visibilitychange", refreshIfDue);
    return () => { clearInterval(timer); document.removeEventListener("visibilitychange", refreshIfDue); activeRequest.current?.abort(); activeRequest.current = null; };
  }, [reload]);

  const visibleNotes = useMemo(() => filterNotes(snapshot.notes, category, query), [snapshot.notes, category, query]);
  const selectedNote = visibleNotes.find((note) => note.id === selectedId) ?? visibleNotes[0];
  const total = snapshot.notes.length;
  const tagCount = new Set(snapshot.notes.flatMap((note) => note.tags)).size;
  const typeCount = new Set(snapshot.notes.map((note) => note.category)).size;
  const hasData = snapshot.status === "ready" || snapshot.status === "stale" || snapshot.status === "empty";

  function resetFilters() { setCategory("all"); setQuery(""); setSelectedId(snapshot.notes[0]?.id ?? ""); }

  return (
    <div className="savepoint-shell">
      <header className="top-bar">
        <div className="brand-lockup"><span className="brand-mark" aria-hidden="true">L</span><div><p className="brand-name">LEMON GROVE</p><p className="brand-name-cn">柠檬林</p></div></div>
        <nav className="category-nav" aria-label="笔记分类">{CATEGORIES.map((item) => <button type="button" key={item} aria-pressed={category === item} onClick={() => setCategory(item)}>{CATEGORY_LABELS[item]}</button>)}</nav>
        <div className="console-status" aria-label="控制台状态"><span>{hasData ? String(total).padStart(2, "0") : "—"} SLOTS</span><span>READ ONLY</span></div>
      </header>

      <main>
        <section className="intro-panel" aria-labelledby="intro-title">
          <p className="intro-kicker">PERSONAL KNOWLEDGE ARCHIVE</p>
          <h1 id="intro-title">把理解存进这里</h1>
          <p className="intro-copy">概念、工具与学习路线，随知识库一起更新。</p>
          <dl className="intro-metrics" aria-label="存档概览"><div><dt>知识页</dt><dd>{hasData ? String(total).padStart(2, "0") : "—"}</dd></div><div><dt>类型</dt><dd>{hasData ? String(typeCount).padStart(2, "0") : "—"}</dd></div><div><dt>标签</dt><dd>{hasData ? String(tagCount).padStart(2, "0") : "—"}</dd></div></dl>
        </section>

        <section className="source-panel" aria-label="知识库数据源">
          <div className="source-identity"><span className="source-mark" aria-hidden="true">GH</span><div><a href={snapshot.source.url} target="_blank" rel="noreferrer">{snapshot.source.repository}</a><p>GitHub · {snapshot.source.branch}{snapshot.source.revision ? ` · ${snapshot.source.revision.slice(0, 7)}` : ""}</p></div></div>
          <div className="source-actions"><span className="source-state" role="status">{loading ? "正在读取…" : snapshot.status === "ready" && snapshot.source.delivery === "published" ? "GitHub 已同步" : STATUS_LABELS[snapshot.status]}</span><button className="reset-button" type="button" disabled={loading} onClick={() => void reload()}>{loading ? "读取中" : "重新加载"}</button></div>
          {snapshot.source.checkedAt ? <p className="source-checked">{snapshot.source.delivery === "published" ? "同步于" : "上次检查"}：{new Date(snapshot.source.checkedAt).toLocaleString("zh-CN", { timeZone: "Asia/Shanghai", hour12: false })} · {snapshot.source.delivery === "published" ? "当前显示 GitHub 发布版本" : "每 5 分钟检查更新"}</p> : null}
        </section>

        <section className="search-panel" aria-label="筛选存档"><div className="search-control"><label htmlFor="archive-search">搜索存档</label><input id="archive-search" type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="标题、标签、实体或正文" /></div><p className="result-count" aria-live="polite">显示 {visibleNotes.length} 个存档</p><button type="button" className="reset-button" onClick={resetFilters}>清除筛选</button></section>

        {total > 0 && snapshot.message ? <p className="source-notice" role="status">{snapshot.message}</p> : null}
        {selectedNote ? <div className="archive-console"><section className="note-list-panel" aria-label="存档列表"><ol className="note-list">{visibleNotes.map((note) => <li key={note.id}><NoteCard note={note} selected={note.id === selectedNote.id} onSelect={setSelectedId} /></li>)}</ol></section><ReaderPanel note={selectedNote} onTagSelect={(tag) => { setCategory("all"); setQuery(tag); }} /></div> :
          <section className="empty-state" aria-labelledby="empty-title"><p aria-hidden="true">{total ? "NO MATCHING SLOT" : "KNOWLEDGE ARCHIVE"}</p><h2 id="empty-title">{total ? "没有找到这个存档" : snapshot.status === "setup_required" ? "等待知识库连接" : snapshot.status === "empty" ? "等待第一份知识存档" : "知识库暂时无法读取"}</h2><p>{total ? "换一个关键词，或者清除筛选查看全部知识页。" : snapshot.message}</p>{total ? <button type="button" onClick={resetFilters}>清除筛选</button> : <a href={KNOWLEDGE_SOURCE.url} target="_blank" rel="noreferrer">打开 GitHub 知识库</a>}</section>}
      </main>
      <footer className="console-footer"><span>END OF ARCHIVE</span><span>{String(visibleNotes.length).padStart(2, "0")} / {hasData ? String(total).padStart(2, "0") : "—"} SLOTS</span><span>GITHUB · READ ONLY</span></footer>
    </div>
  );
}
