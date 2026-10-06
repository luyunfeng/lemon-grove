# AGENTS.md — 个人学习知识库（LLM Wiki）规则

> **本文件是本知识库唯一的规则来源。** 全局 skill `llm-wiki` 只负责找到（或克隆）本仓库并定位到这里；CLAUDE.md 通过 `@AGENTS.md` 引入本文件。规则有冲突时，以本文件为准。

- 位置：本仓库可能克隆在任意目录。下文所有命令都**在仓库根目录执行**（即本文件所在目录）。
- 远端：`https://github.com/luyunfeng/lemon-grove.git`；`main` **只通过 PR 合入**
- 语言：中文为主，专有名词保留英文（首次出现时可写作 `中文（English）`）

## 0. 硬性规则（优先于下文所有内容）

1. **写入前先确认。** 任何写入请求（炼化、收录、ingest、整理、lint 修复、改 schema），第一步都是向用户说明：
   - 打算写什么内容（要点）；
   - 要新建或修改哪些文件（逐个列出路径，包括 raw、wiki 页、index.md、log.md）；
   - 要用的分支名，以及 PR 标题。
   然后**停下来等用户明确同意**（如"确认""可以""同意""写吧"）。没有得到明确同意就不创建、不修改任何文件，也不执行任何 git 写操作。用户要求调整时，改好计划再确认一次。在非交互模式（如 `codex exec`、`claude -p`）里，只输出计划就结束。
2. **读取、查询严格只读。** 查询时：不改任何文件、不回写答案、不写 log、不执行任何 git 写操作（commit、push、pull、fetch、checkout、switch、stash 都不行）。只允许读文件、`rg`/`grep`、`git log`、`git status`、`git show`、`git diff`。如果某个答案值得沉淀，只能在回答末尾**建议**（例如"可以说『炼化一下这个结论』来收录"），由用户另行发起写入请求。
3. **Git 只走 PR。** 永远不要直接 push `main`，永远不要 `--force` 或改写已推送的历史，**不要合并 PR**（合并由用户在网页上完成）。流程见第 5 节。
4. `raw/` 正文只增不改：已提交的 raw 正文不能修改或删除，需要更正时新增一份资料，并把更正后的认识写进 wiki。raw 的文件名和头部格式由本文件统一规定，规范调整时可以经确认后一次性整理（`git mv`）并记入 log。
5. 不提交密钥、token、公司内部地址、个人环境路径、私人联系方式或公司敏感数据。脱敏修改 raw 正文需要用户明确批准例外，不能借普通收录改写已提交资料。公开资料中的作者、人物观点、机构与项目名称不是敏感信息，应在 raw 中保留；不能仅凭出现公司或人名进行脱敏。

## 1. 三层结构

| 层 | 路径 | 谁写 | 规则 |
|---|---|---|---|
| 原始资料 raw | `raw/` | 人投放，或 AI 经确认后代为保存 | 一级目录不分类；正文只增不改；只作底稿，wiki 不链接它 |
| 知识页 wiki | `wiki/` | AI 经确认后维护，人阅读、把关 | 按知识点组织；关联靠头部的标签和实体来找，正文不放站内链接；index、log 保持一致 |
| 规则 schema | `AGENTS.md`（CLAUDE.md 引用它） | 人与 AI 共同演进（改动同样要确认并走 PR） | 唯一规则来源 |

## 2. 目录约定

```
AGENTS.md                         唯一规则来源（本文件）
CLAUDE.md                         Claude Code 入口，@AGENTS.md 引入本文件
README.md                         简要用法
raw/<slug>.md                     原始资料（文章、论文摘录、课程笔记、对话记录…），全部放在 raw/ 一级目录，不分类；文件名不带日期
raw/assets/<slug>.<ext>           图片等附件（raw/ 下唯一允许的子目录）
wiki/index.md                     知识地图：按领域分组，每页一行（链接 + 一句话）；wiki/ 内唯一允许放站内链接的页面
wiki/log.md                       追加式写入日志（只记录写操作：ingest / lint / schema / wiki）
wiki/overview.md                  概览：在学什么、掌握到什么程度、待解问题
wiki/concepts/<slug>.md           概念页：一个知识点（概念、方法、原则）一页
wiki/entities/<slug>.md           实体页：一个具体工具、产品或项目一页
wiki/roadmaps/<slug>.md           学习路线：按阶段组织的学习与实践步骤
wiki/syntheses/<slug>.md          综合结论：只有用户明确要求沉淀时才写
templates/                        各类页面模板
tools/lint.py                     机械体检脚本（只读）
tools/related.py                  按页面、标签或实体列出相关页面（只读）
skills/README.md                 技能清单、安装方式与新增约定
skills/<skill-name>/SKILL.md      技能入口：触发条件、执行规则与按需读取的资源
skills/<skill-name>/README.md     配套说明：用途、安装、调用示例、验证与维护
skills/<skill-name>/references/   可选的格式约定、评分标准、研究依据等参考资料
skills/<skill-name>/agents/       可选的宿主界面元数据
skills/llm-wiki/SKILL.md          知识库定位入口；知识库规则仍只以本文件为准
```

- 文件名用小写英文 kebab-case（不超过 60 字符）；标题写在 frontmatter 的 `title` 里，可以用中文。
- wiki 只允许上面这几个一级子目录（concepts / entities / roadmaps / syntheses），不再往下嵌套；不设按资料或按主题拼出来的页面。领域只作为 index 里的分组标题。
- **wiki 正文不放站内链接**（Markdown 链接和 `[[wikilink]]` 都不用），提到别的概念直接写名字。`wiki/` 内只有 `wiki/index.md` 用相对路径的标准 Markdown 链接指向各页。
- 文件移动或重命名用 `git mv`，保留历史。

### 技能源码

- `skills/` 保存可复用技能源码，每个技能独立放在 `skills/<skill-name>/`；在 `skills/README.md` 登记，新加入的技能配套 `README.md`。
- 技能包遵循宿主的文件格式，保留 `SKILL.md`、`README.md` 等标准文件名；不套用 wiki 的四字段 frontmatter 和知识页写法。包内文档可用相对链接引用自身资源，研究依据可保留公开来源链接；根目录 README 可链接技能清单。
- 仓库中的技能源码通过本文件规定的确认和 PR 流程维护。安装副本或软链接使用完整技能目录，保持资源的相对路径；不得把凭据、个人机器路径、公司敏感材料或私人对话原文打包入库。

## 3. 页面 frontmatter 与写法

wiki/ 下除 index.md、log.md 外，每页都要有 frontmatter，**只有 4 项**：

```yaml
---
title: LLM Wiki 模式
type: concept                  # concept | entity | roadmap | synthesis | overview
tags: [knowledge-management]   # 只能用 3.2 词表里的标签，一行写完
entities: [claude-code, codex] # 这页涉及的实体，值是 wiki/entities/ 下的文件名（不含 .md）；没有就写 []
---
```

- `tags` 表达主题，`entities` 表达涉及的具体工具、产品或项目。两者都写成一行的列表，便于用 `rg` 搜索。
- 实体页的 `entities` 要包含它自己。
- 不写 `status`、`sources`、`related`、`created`、`updated`、`author` 等字段；时间信息看 git 历史。

### 3.2 标签词表（唯一来源，lint 从这里读取）

标签一律用小写英文 kebab-case。**新标签必须先加进这张表（同一个 PR 里也行），才能在页面里使用**；能用已有标签表达的，不新增。

<!-- tags:begin -->
| 标签 | 说明 |
|---|---|
| `agentic-engineering` | Agent 成为主要执行者之后的工程范式，以及人的角色与判断 |
| `context-engineering` | 上下文管理：给模型什么信息、何时给、怎么给（渐进式披露、隔离、分层入口） |
| `harness` | 包裹模型的控制系统：上下文供给、约束、工具、状态和反馈回路 |
| `verification` | 验证与完成条件：maker/checker 分离、证据、可回归的检查 |
| `agent-loop` | 驱动 Agent 的外层循环：目标驱动、自动触发、谁判定完成 |
| `spec` | 执行前校准：需求澄清、计划、规格与任务拆分 |
| `multi-agent` | 子 Agent 与多 Agent 编排、跨模型分工 |
| `guardrails` | 约束的落点与强制力度：入口文件、规则、Skill、Hook |
| `compounding` | 把经验沉淀成可复用资产，让下一次更容易 |
| `prompting` | 提示词写法，包括让模型输出置信度 |
| `tool-interface` | Agent 的工具接口：CLI、MCP、面向 Agent 的 API 设计 |
| `agent-docs` | 写给 Agent 读的文档与领域知识 |
| `agent-skill` | Agent Skill 的概念、设计、测试、发现与安装 |
| `self-improvement` | 系统改进自身：Skill 自进化、递归自我改进 |
| `post-training` | 后训练与强化学习，包括可验证奖励 |
| `evaluation` | 模型与系统评测：Arena、基准、自有评测 |
| `llm-models` | 具体模型的能力、定位与发布解读 |
| `inference` | 模型推理与 serving 基础设施：KV cache、prefix/prompt/semantic caching、成本 |
| `ai-safety` | 对齐、奖励作弊、失控风险与治理 |
| `coding-agent` | 终端 Coding Agent 工具本身的机制与用法 |
| `agent-framework` | 构建在 Coding Agent 之上的方法框架与 Skill 组合 |
| `workflow` | 端到端的开发协作流程与闭环实践 |
| `knowledge-management` | 个人知识管理与 LLM Wiki |
| `learning-path` | 按阶段组织的学习路线 |
| `meta` | 本知识库自身的说明与概览 |
<!-- tags:end -->

### 3.3 怎么找关联

页面之间不建链接，关联靠标签和实体来找（在仓库根目录执行）：

1. 先读 `wiki/index.md`，按领域找候选页面。
2. 按标签或实体搜所有页面的头部：

```bash
rg -l '^tags:.*[\[ ]verification[,\]]' wiki/          # 打了 verification 标签的页面
rg -l '^entities:.*[\[ ]claude-code[,\]]' wiki/       # 涉及 Claude Code 的页面（含实体页本身）
rg -n '^(tags|entities):' wiki/concepts/harness-engineering.md   # 看某页的标签和实体
rg -o --no-filename '^tags: .*' wiki/ | tr -d '[]' | sed 's/^tags: //' | tr ',' '\n' | sed 's/^ //' | sort | uniq -c | sort -rn   # 标签使用频次
```

3. 也可以用脚本，一次列出有交集的页面（按共享的标签和实体数排序）：

```bash
python3 tools/related.py wiki/concepts/verification.md   # 与某页标签或实体有交集的页面
python3 tools/related.py --tag agent-skill               # 某个标签下的页面
python3 tools/related.py --entity codex                  # 涉及某个实体的页面
```

4. 找到相关页面后再读正文。收录新资料时也用这个办法先找已有页面去更新，不新开页面。

### 3.1 写法规则（页面不写作者和来源，不放站内链接）
- **只写知识本身。** 正文里不出现作者、人名、出处，也不写「某笔记 / 某文章 / 某人认为」「多个来源提到」；没有「来源 / 资料 / 参考 / 延伸阅读」小节；不放外链；不放站内链接，也不链接 `raw/`。产品、公司、项目名可以作为讲述对象出现，但不作为「谁说的」的归属。
- **不写时间线。** 不写「认识演进」「早期 / 后来」「某月」、发布日期或 `YYYY-MM` 这类日期；版本号只作为实体的属性。
- **分歧写成取舍。** 观点不同时写「两种做法：……各自适用于……」，不写「A 说、B 说」。被推翻的结论直接改写；需要保留提醒时用 `> [!disputed] …` 或 `> [!outdated] …`，只写知识层面的原因。
- **一页一个知识点。** 概念页骨架：一句话（是什么、解决什么）→ 要点 → 怎么做 / 为什么 → 边界与误区。实体页骨架：它是什么 → 核心机制 → 怎么用。页面末尾不列相关页面清单，关联交给 `tags` 和 `entities`。
- **提到别的概念写名字。** 直接写对方页面的名称（纯文本，必要时加「」），保证句子通顺。
- **事实可靠。** 数字、术语和引述写入前在 raw 里核对（`rg` 定位），但页面上不标出处。

raw 文件只保留标题行和正文（见 `templates/raw.md`），不写作者、来源、原文链接、日期等元数据。

## 4. 操作

每次操作开始时：进入仓库根目录，先读 `wiki/index.md`，再用 `grep "^## \[" wiki/log.md | tail -5` 看最近 5 条日志。

### 4.1 Query（查询，只读）
触发示例：查知识库、查 wiki、"我的知识库里关于 X 有什么"、"基于我的笔记对比 A 和 B"。
1. 先读 `wiki/index.md` 找候选页，再按 3.3 用标签和实体找相关页，然后对 `wiki/` 和 `raw/` 做全文搜索，关键词要带上同义词和英文名（`rg -il "<关键词>|<同义词>|<英文>" wiki/ raw/`；`rg` 在 `~/.local/bin`，找不到时用 `grep -rilE`）。两者都搜不到，才能说"库里没有"，并说明搜了哪些词。
2. 读命中的页面（必要时追到 raw 核对原文），综合回答。以库内知识为主；用到库外知识时在回答里说明（只在对话中说明，不写进页面）。
3. 引用时写相对仓库根的路径，例如 `wiki/concepts/llm-wiki-pattern.md`。
4. **遵守硬性规则 2：不写任何文件，不记 log，不做 git 写操作。** 值得沉淀的内容只提建议。

### 4.2 Ingest / 炼化 / 收录（写入）
触发示例：炼化、收录、录入、记到知识库、存到 wiki。
1. **确认（硬性规则 1）**：先读资料并分诊，判断是新建、更新、冲突还是无新增（先读 index，再按 3.3 用标签和实体找已有页面，再全文搜索关键词和同义词）。然后列出计划：raw 保存路径、要新建或更新的 wiki 页、index/log 的改动、分支名、PR 标题。**等用户明确同意。**
2. 同意后按第 5 节从最新的 `origin/main` 开分支。
3. 保存 raw：路径为 `raw/<slug>.md`，放在 raw/ 一级目录，不分类（重名时加一个能区分内容的简短后缀，不加日期）；图片放 `raw/assets/`，笔记里用 `assets/<文件名>` 引用。头部只写标题，不写作者、来源、链接和日期；正文保留原文，只清理格式噪音和敏感信息。
4. **拆知识点，更新已有页面。** 把资料拆成一个个知识点，逐点对照已有页面：能并入的就改写进已有概念页或实体页；只有出现新的独立知识点或新工具时才新建页面。**不写资料摘要页，不按资料建页。** 写法遵守 3.1；数字和引述先在 raw 里核对。
5. 级联更新：按 3.3 找出受影响的页面一并修改；新页和改过的页都要填好 `tags`（只用词表里的）和 `entities`。涉及新工具时先建实体页。
6. 更新 `wiki/index.md`（新页放进对应领域分组），必要时更新 `wiki/overview.md`，并在 `wiki/log.md` 末尾追加一条记录（格式见第 6 节）。
7. 跑 `python3 tools/lint.py`，ERROR 必须为 0。然后按第 5 节提交、推分支、建 PR。
8. 如果分诊结果是"无新增"：同样先确认，经同意后只保存 raw 并写一条 log，再走 PR。

### 4.3 Lint（体检）
1. 只读检查：`python3 tools/lint.py`，检查头部四项是否齐全、标签是否都在词表里、entities 是否都有实体页、正文有没有站内链接、index 是否登记了所有页面且没有死链、目录白名单、raw 是否只有 assets/ 一个子目录、作者 / 来源 / 日期 / 人名痕迹、外链、raw 头部元数据和文件名日期。再加上判断类检查：页面间矛盾、过时结论、标签或实体漏填、被频繁提及却没有独立页的概念、资料缺口。
2. 先把报告给用户看。如果需要修复（index 补漏、修死链等），按硬性规则 1 列出修复计划，**等用户同意后**再开分支修复。修复后在 log 追加 `## [YYYY-MM-DD] lint | 发现 N 项，修复 M 项`，然后走 PR。事实性问题只报告，不擅自修改。

## 5. Git 与 PR 流程（所有写入都走这个流程）

分支命名：`wiki/<YYYYMMDD>-<英文主题-slug>`，例如 `wiki/20260926-rag-basics`。

```bash
# 在仓库根目录执行
git status --short                     # 必须干净；不干净就停下来告诉用户
git fetch origin
git switch --no-track -c wiki/<YYYYMMDD>-<slug> origin/main
# …按已确认的计划写文件…
python3 tools/lint.py                  # 0 ERROR
git add -A
git commit -m "<ingest|lint|wiki|schema>: <中文摘要>"
git push -u origin HEAD
gh pr create --base main --title "<同 commit 摘要>" --body-file <描述文件>
git switch main                        # 回到本地 main，不在 main 上提交
```

- 使用 GitHub CLI `gh pr create` 或已授权的 GitHub 连接创建 PR；描述列出改动文件、要点及验证结果。
- 命令行未认证时使用 `gh auth login`；认证失败时保留本地分支，报告原因，不修改其他工具的认证配置。
- **不要合并 PR**，不直接 push main，不 force push；合并由用户在网页上完成。
- 查看 PR：`gh pr list`、`gh pr view <编号>`（只读）。
- 用户合并后，下次写入前先 fetch，再从最新的 `origin/main` 开分支。本地 main 只在写入流程中、工作区干净时以 fast-forward 同步；查询时不同步。
- 同一轮写入只开一个分支、只建一个 PR。推送或建 PR 失败时保留本地分支并报告原因。
- 迁移资料时使用经过脱敏检查的内容快照；旧提交历史中的个人身份与公司信息不会随文件清理而消失，不能直接随快照上传。

## 6. log.md 格式

log 只记录写操作。每条以固定前缀开头，便于 `grep "^## \[" wiki/log.md | tail -5` 查看：

```
## [YYYY-MM-DD] ingest | <资料的主题>
- 分诊: 更新为主 / 新建
- Raw: raw/<slug>.md
- 新建: wiki/concepts/<slug>.md, ...
- 更新: wiki/index.md, wiki/overview.md
- 分支: wiki/<YYYYMMDD>-<slug>
```

类型：`ingest` | `lint` | `wiki`（手工整理）| `schema`（规则或 skill 变更）。

## 7. 本库自身的设计说明
见 [wiki/concepts/knowledge-base-design.md](wiki/concepts/knowledge-base-design.md)。
