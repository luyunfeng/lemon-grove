---
title: ECC（Everything Claude Code）
type: entity
tags: [agent-framework, guardrails, compounding, agent-skill]
entities: [ecc, claude-code, superpowers]
---

# ECC（Everything Claude Code）

## 它是什么

一个 AI 编码增强框架，自称 harness-native operator system：把 Agent、Skill、Command、Hook、Rule 和持续学习打包成一套跨工具的「行为层」，让团队里反复要解释的事情（编码风格、测试规则、回滚机制、依赖识别）有一个稳定的形状。

规模很大：v2.0.0-rc.1 有 63 个 Agent、249 个 Skill、79 个命令，外加 Hook 系统、持续学习 v2.1 和安全审计器 AgentShield。但**规模不是重点**。它真正的价值在于把「Agent 应该怎么被治理」拆成了层次分明、可以装配的零件，以及长期日常使用提炼出的模式（记忆持久化、Token 优化、策略压缩、并行编排）。模式比代码更值得学，也更容易迁移。

## 核心机制

### 1. 一条层次链

`Command（用户主动触发）→ Agent（角色分派）→ Skill（领域知识）→ Hook（物理拦截）→ Instinct（原子学习）`

- 粒度从粗到细，触发从「用户主动」到「系统自动」；
- 演化方向反过来：Instinct（最小学习单位）聚合成 Skill，再沉淀为 Command / Agent；
- Rule 是蒸馏产物：`/rules-distill` 把被多个 Skill 共用的内容提炼成 Rule。

这条链比组件数量重要。另一种切法是按治理要素分五个原语：

| 原语 | 作用 | 触发方式 |
|---|---|---|
| Skill | 告诉 Agent「好的工作长什么样」 | 按需触发，可链式调用 |
| Rule | 「永远遵循 X」 | 常驻，每次都加载 |
| Hook | 运行时强制 | 必然触发，不依赖模型判断 |
| Memory | 总结先前决策 | 跨会话恢复上下文 |
| Eval | 测试、冒烟检查、证据 | 质量门禁 |

三组容易混的区分：

- **Rule vs Skill**：Rule 常驻、跨任务都成立；Skill 靠描述被挑中，服务单一任务。
- **Command vs Agent**：Command 只做入口和路由，Agent 干活，业务逻辑不写在 Command 里。
- **Hook vs Skill**：Hook 100% 触发、能阻断；Skill 只有约 50-80% 的触发率。「必须发生」的交给 Hook，「按场景判断」的交给 Skill。

### 2. 架构：一份核心，多个适配器

agents / skills / rules / hooks 只写一份，每个工具写一个适配器做格式转换。但各工具的适配程度差别很大：Claude Code 约 100%，Cursor 约 70%，OpenCode 约 50%，Codex 约 40%，Copilot 约 20%。Codex 适配低不是因为 Codex 没有 Hook（它有 10 个事件，比 Claude Code 多），而是还没适配。Skill 的增删主要影响适配器层，不动核心层。

Agent 的 YAML 头里有物理约束：`tools` 白名单（例如 planner 只有 Read / Grep / Glob，想「顺手实现」也做不到）、`description` 里的 "Use PROACTIVELY when..." 作为路由依据、`model` 做成本控制。

### 3. 持续学习 v2.1

流水线：会话活动 → Hook 捕获观察 → 后台 Observer Agent（Haiku）分析 → 本能库（YAML）→ 演化为 SKILL.md。

- 用 Hook 而不是 Skill 来捕获，因为 Hook 必然触发；捕获时自动脱敏，并有 5 层防止「观察自己」的防护。
- 识别四类模式：用户纠正、错误解决、重复工作流、工具偏好。
- 置信度按观察次数定初值：1-2 次 0.3，3-5 次 0.5，6-10 次 0.7，11 次以上 0.85；之后确认一次 +0.05，出现矛盾 -0.1，每周无新观察 -0.02。
- 默认放在项目作用域；同一本能在 2 个以上项目出现且平均置信度 ≥ 0.8 时，自动提升为全局。

它的真正含义不是「让 Agent 变聪明」，而是**让会话变成可复用的资产**：上下文不够就改进记忆，重复犯错就变成规则。

### 4. 安全

- 三层防护：每个 agent 文件开头注入 6 句 Prompt Defense 基线；Rules 常驻；Hooks 物理拦截（退出码 2 直接阻断，跟模型听不听话无关）。
- AgentShield：102 条规则、1282 个测试、98% 覆盖率。安全循环是 Scan → Classify → Route → Gate → Report；原则是危险动作必须获批、最小工具加最小权限、全量留下可审查的证据。
- 一句话：**能用 Hook 拦的，就别靠模型自觉。** 但 Hook 之外的工具调用、子进程和数据外传仍然靠模型自觉。

### 5. 值得迁移的实战模式

- **记忆持久化**：会话结束时写状态摘要（什么有效、什么无效、什么还没试），用 PreCompact / SessionStart / SessionEnd 三个 Hook 串起来。
- **Token 优化**：Haiku 做重复任务和 worker、Sonnet 做日常、Opus 做架构和首次失败后的升级；系统提示从 18K 瘦身到 10K token，省下约 41% 的静态开销；能用 Skill / Command 替代的 MCP 就替掉。
- **验证循环**：检查点式（每个里程碑验）和连续式（每 N 分钟或重大改动后全量跑）；评分器分代码（快、便宜、脆弱）、模型（灵活、不确定、贵）、人类（金标准、慢）三类。
- **编排分层**：Tier 1 是子代理、元提示、多问用户，门槛低、收益直接；Tier 2 是长运行、并行、多角色 Agent，方差高。从 Tier 1 开始。
- **Harness Optimizer**：通过改 harness 配置而不是改产品代码来提升完成质量——先跑 `/harness-audit` 拿基线，找前 3 个杠杆点（hook / eval / 路由 / 上下文 / 安全），做最小、可回滚的改动，再报告前后差值。
- **Skill 写法像决策清单**：开头不超过 2 行说明何时用，一段心智模型，每个子主题 3-6 条要点，结尾必有 anti-patterns。值得精读的三个 meta-skill：`agent-harness-construction`（工具粒度三档：高风险用 micro-tool，读 / 改 / 搜用 medium，往返次数是瓶颈才用 macro-tool）、`agentic-engineering`（「15 分钟单元」：每个子任务独立可验证、只有一个主导风险、有明确完成条件）、`context-budget`（按「始终 / 偶尔 / 极少需要」给所有组件的 token 开销分档体检）。

### 6. 命令面

命令统一带 `/ecc:` 前缀，和 Claude Code 内置命令区分。最常用的一条链：

`/ecc:prp-plan` → `/ecc:prp-implement`（带严格验证循环）→ `/ecc:review` → `/ecc:prp-commit` → `/ecc:pr`

按用途大致分为 PR 与审查、项目管理、产品开发、工程实现、安全合规、数据研究、运维部署、Prompt 优化几类。接入项目用 `/ecc:project-init`（默认 dry-run，不改文件）；`/ecc:projects`、`/ecc:promote` 管理项目级和全局 instinct；此外有 `/ecc:build-fix`、`/ecc:checkpoint`、`/ecc:prompt-optimizer` 等。执行命令时会自动激活相关 Skill。

## 怎么用

**学法是做减法：把它当协作层，不当新框架。**

- 先学 Claude 的原生入口（skill、命令、hook、agent 何时进入上下文），再看 ECC 的安装、校验和跨工具映射。
- 先复刻最小闭环 plan → change → verify → review → handoff，配 6 个轻量 skill（plan / verify / review / build-fix / docs-lookup / handoff），高级自动化放后面。
- 验证输出固定五段：运行了什么、结果是什么、失败如何处理、没跑为什么、残余风险。没有验证证据，就不说「完成」。
- 安装走插件入口（`/plugin install ecc@ecc`）。装好插件后**不要**再跑 `install.sh --profile full`，否则重复触发、命名冲突。也不要把 249 个 skill 全量复制进 `~/.claude/skills/`。
- Hook 按风险递增来加：先 Stop / PreCompact 提示型，再 PostToolUse 检查型，最后才 PreToolUse 阻断型。
- 能用 CLI 明确完成的不上 MCP；工具列表太长时，关掉无关 MCP 比换模型更直接。
- 持续学习先别整套搬：用「会话观察 → 候选 instinct → 人工审核后采纳」的渐进管线，比让 Agent 自己决定写入记忆更稳。「知道有什么」和「什么时候做」是两件事。
- 单个工具还没跑通就做跨工具投影，等于把混乱复制 N 份。

**和 Superpowers 的取舍**：ECC 走实用主义，灵活分派，有三层记忆和系统的 Token 优化，支持多平台；Superpowers 走纪律主义，铁律加反合理化，严格链式编排，没有记忆，只支持 Claude Code。两者都想当「总指挥」，一起装会抢编排权。一个可行的组合是以 Superpowers 为主干，选择性吸收 ECC 独有的安全审计、持续学习、语言专属 reviewer 知识和 Token 优化；已有类似体系时，重点是对齐输出契约，而不是再建一套 skill。

**风险**：维度膨胀，没人记得住所有组件；提交高度集中在一人、大版本间有大量 breaking change，适合借鉴方法论，不适合当依赖；行业垂直 skill 明显凑数；star 数不等于日活；新控制面仍是 alpha。「效率提升 300%」是平均值，强者的提升接近指数、弱者接近对数，Agent 工具会拉大差距。
