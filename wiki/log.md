# 操作日志（Log）

> 追加式记录，最新在最后，只记录写操作。格式：`## [YYYY-MM-DD] <ingest|lint|wiki|schema> | <标题>`。日期是写操作的时间，不是知识内容的时间线。
> 查看最近 5 条：`grep "^## \[" wiki/log.md | tail -5`

## [2026-09-26] wiki | 历史概述（重构前的记录压缩为本条）
- 建立知识库骨架（raw / wiki / AGENTS.md / skill），规则收敛到 AGENTS.md：写入先确认、查询只读、只走 MR。
- 收录 LLM Wiki 模式学习笔记，以及 AI Coding 方向的 43 篇学习笔记（已脱敏，HTML 转为 Markdown）。
- 当时的结构是资料摘要页 + 主题页 + 概念页，已被下一条的重构取代。

## [2026-09-26] schema | 按知识点重构：删除资料摘要页与主题页，页面不写作者、来源和日期
- 分诊: 重构（schema + wiki）
- Raw: raw/ 下 44 篇和 1 个附件一次性整理：用 git mv 去掉文件名日期前缀，删掉头部元数据（来源、作者、日期等），同步图片引用；正文不动
- 删除: wiki/sources/（44 页）、wiki/topics/（3 页）、roadmaps/llm-wiki-practice（并入 knowledge-base-design）
- 拆分 / 改名: post-training-verification → verifiable-rewards + verification；cli-as-agent-interface → agent-tool-interface；claude-code-goal-mode → goal-vs-plan；claude-code-and-codex-practices → entities/claude-code + entities/codex；everything-claude-code → entities/ecc；model-evaluation-arena → model-evaluation + entities/claude-models；ecc-one-month-learning → roadmaps/agent-workflow-practice；lilian-weng-lillog-learning-map → roadmaps/lillog-reading-path
- 新建: concepts/verification、rule-enforcement-layers、agent-skill、recursive-self-improvement、verifiable-rewards；entities/ 下 6 页（claude-code、codex、claude-models、ecc、superpowers、mattpocock-skills）
- 改写: 其余概念页按「一页一个知识点 + 关系小节」重写；index 改为按领域分组的知识地图；overview 去掉最近动态
- 规则: AGENTS.md（目录白名单、4 字段 frontmatter、写法规则 3.1、ingest 改为更新已有知识页、raw 命名与头部）、templates（删 source/topic，新增 entity）、tools/lint.py、README.md、CLAUDE.md
- 分支: wiki/20260926-restructure-by-knowledge

## [2026-09-26] schema | 关联改为标签 / 实体，去掉双向链接和关系小节；raw 拍平；修复写死路径
- 分诊: 规则调整（schema + wiki），回到更轻的 LLM Wiki 做法
- Raw: raw/ai-coding/ 与 raw/llm-wiki/ 下 44 篇用 git mv 移到 raw/ 一级目录（无重名），删掉空子目录；只改了 1 处图片路径（../assets/ → assets/），其余正文不动
- 更新: wiki/ 下全部 31 页头部改为 title / type / tags / entities 四项（删 status）；删掉「## 关系」「## 体现的概念」和正文里的全部站内链接，提到别的概念改写成纯文本名字；tags 统一收拢到 24 个标签的固定词表；entities 按原关系和正文填写实体 slug
- 更新: wiki/index.md（说明文字）、wiki/overview.md、wiki/concepts/knowledge-base-design.md（skill 按线索找仓库或克隆；关联靠标签和实体）
- 规则: AGENTS.md（仓库路径改为「在仓库根目录执行」；目录约定补 INSTALL.md、tools/related.py，raw 改为一级目录不分类；3.2 标签词表；3.3 怎么找关联及 rg 命令；ingest / lint 流程同步）、templates/、README.md、CLAUDE.md
- 工具: tools/lint.py（根目录从脚本位置推出；检查头部四项、标签词表、entities 对应实体页、正文无站内链接、raw 只允许 assets/ 子目录、敏感信息；去掉孤儿页和关系小节检查）；新增 tools/related.py
- 分支: wiki/20260926-tags-entities-relations

## [2026-09-26] ingest | 阿里AI Native研发范式实践手册
- 分诊: 新建（raw 单文件完整收录，暂不建 wiki 页）
- Raw: raw/ali-ai-native-handbook.md
- 新建: raw/assets/ali-ai-native-handbook-p*.png（17 张架构图）
- 更新: wiki/log.md
- 分支: wiki/20260926-ai-native-handbook

## [2026-10-01] lint | 清理公司环境与内部来源线索
- 分诊: 经用户确认执行脱敏；公开资料的作者、出处、公司及项目名称保留
- Raw: 7 篇资料清理内部来源痕迹；移除无法核实的公司内部模型与策略描述，保留公开研究及技术观点
- 更新: AGENTS.md、CLAUDE.md、README.md、skills/llm-wiki/SKILL.md、wiki/concepts/knowledge-base-design.md、tools/lint.py、wiki/log.md
- 验证: 内容扫描、图片目视检查与 lint；发布快照不携带旧 Git 历史
- 分支: wiki/20261001-sanitize-private-info
