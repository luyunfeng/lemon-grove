# LLM Wiki 模式学习笔记（Karpathy gist 摘录 + Google OKF）

## 一、Karpathy《LLM Wiki》原文节选

副标题："A pattern for building personal knowledge bases using LLMs."

核心思想（节选）：

> Instead of just retrieving from raw documents at query time, the LLM incrementally builds and maintains a persistent wiki — a structured, interlinked collection of markdown files that sits between you and the raw sources.

> The knowledge is compiled once and then kept current, not re-derived on every query.

三层架构：

- Raw sources —— 原始资料集合，LLM 只读不改。
- The wiki —— "a directory of LLM-generated markdown files. Summaries, entity pages, concept pages, comparisons, an overview, a synthesis. The LLM owns this layer entirely." "You read it; the LLM writes it."
- The schema —— "a document (e.g. CLAUDE.md for Claude Code or AGENTS.md for Codex) that tells the LLM how the wiki is structured, what the conventions are, and what workflows to follow when ingesting sources, answering questions, or maintaining the wiki." "You and the LLM co-evolve this over time as you figure out what works for your domain."

操作：

- Ingest："the LLM reads the source, discusses key takeaways with you, writes a summary page in the wiki, updates the index, updates relevant entity and concept pages across the wiki, and appends an entry to the log. A single source might touch 10-15 wiki pages."
- Query：先读 index 找相关页，再深入阅读并综合回答；好的答案可以回写进 wiki。
- Lint：检查矛盾、过时论断、孤儿页、缺失的概念页与交叉引用、资料缺口。

索引与日志：

> index.md is content-oriented. It's a catalog of everything in the wiki — each page listed with a link, a one-line summary, and optionally metadata like date or source count.

> This works surprisingly well at moderate scale (~100 sources, ~hundreds of pages) and avoids the need for embedding-based RAG infrastructure.

> log.md is chronological. It's an append-only record of what happened and when — ingests, queries, lint passes.

日志前缀示例：`## [2026-04-02] ingest | Article Title`，可用 `grep "^## \[" log.md | tail -5` 查看最近 5 条。

为什么有效：

> LLMs don't get bored, don't forget to update a cross-reference, and can touch 15 files in one pass.

## 二、Google Cloud：Open Knowledge Format（OKF）

- 2026-06-12，Google Cloud 博客《How the Open Knowledge Format can improve data sharing》介绍 OKF："an open specification that formalizes the LLM-wiki pattern into a portable, interoperable format"。
- OKF v0.1 形态："a directory of markdown files with YAML frontmatter"，附带少量约定（frontmatter 必填 `type`，可选 `index.md`、`log.md`，标准 Markdown 链接）。
- 博客称已更新 Google Cloud Knowledge Catalog 以摄取 OKF。
- 规范仓库：https://github.com/GoogleCloudPlatform/open-knowledge-format （后续 v0.2 增加 provenance、trust、lifecycle、attestation 等字段）。

## 三、我的初步想法

- 适合拿来做"个人学习记录"：每读一篇资料就 ingest 一次，让 AI 维护概念页和学习路线。
- 纯 Markdown + git，Codex 和 Claude Code 都能读写；中等规模内不需要向量库。
