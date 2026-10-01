---
title: Open Knowledge Format（OKF）
type: concept
tags: [knowledge-management]
entities: []
---

# Open Knowledge Format（OKF）

> 一种由 Google Cloud 提出的开放规范，把 LLM Wiki 模式规范成可移植、可互操作的格式。它解决的是各家 LLM wiki「各自为政」的问题：让不同生产者写的 wiki，能被不同的 Agent 和工具直接消费。

## 要点

- **形态极简（v0.1）**：一个由 Markdown 文件组成的目录，每个文件带 YAML frontmatter，外加少量约定：
  - frontmatter 里必填 `type`；
  - `index.md`、`log.md` 可选；
  - 页面之间用标准 Markdown 链接。
- **后续版本（v0.2）** 增加了 provenance（出自哪里）、trust（可信度）、lifecycle（生命周期）、attestation（证明 / 背书）等字段，方向是让知识能被机器判断「可不可信、还有没有效」。
- **已有消费方**：Google Cloud Knowledge Catalog 支持摄取 OKF 格式的知识。

## 怎么做 / 为什么

- **为什么格式要这么轻**：LLM wiki 的价值在内容和链接结构，而不是某个工具的私有格式。只约定「Markdown + frontmatter + 必填 type + 标准链接」，任何能读文件的 Agent 都能用，迁移成本几乎为零。
- **为什么必填 `type`**：消费方需要知道一页是概念、实体还是别的什么，才能决定怎么索引和展示。这也是一个 wiki 最小的结构信息。
- **为什么用标准 Markdown 链接**：wikilink 依赖特定编辑器解析，标准链接在 git 托管平台、普通 Markdown 渲染器和 Agent 里都能直接跳转。
- **一个 wiki 想兼容 OKF**：页面保持 Markdown + YAML frontmatter，frontmatter 带 `type`，链接统一用相对路径的标准 Markdown，保留 `index.md` / `log.md`。满足这些，基本就兼容 v0.1，将来可以直接导出。

## 边界与误区

- **它是格式，不是方法**：OKF 规定文件长什么样，不规定怎么录入、怎么体检、页面按什么组织。方法仍然是 LLM Wiki 模式本身。
- **v0.2 的追溯字段与「页面只写知识」的取舍**：把 provenance 写进每页 frontmatter，机器可以直接判断可信度，但页面会带上资料汇编的痕迹；另一种做法是页面只写知识本身，可追溯交给 git 历史和 raw 底稿。后者读起来干净，但导出到 v0.2 时需要从 git 和 raw 生成这些字段，而不是现成就有。
- **误区：兼容格式就等于能互通**。字段对上只是第一步，`type` 的取值、标签体系在不同 wiki 之间仍可能不一致，真要合并还要做映射。
- 规范版本号还很低（v0.x），字段会变，导出前以当时的规范为准。
