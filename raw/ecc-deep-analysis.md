# ECC 深度研究：AI 编码增强框架的架构、生态与实战模式

> [!info] 来源
> 基于 GitHub [affaan-m/ECC](https://github.com/affaan-m/ECC) 源码分析、[Longform Guide](https://x.com/affaan/status/2014040193557471352) 长文、Codex 源码 `codex-rs/hooks/`，以及 GitHub 生态调研。

> [!tip] 配套笔记
> 落地视角：[[ecc-one-month-learning-plan|ECC 一个月学习计划]]（HTML）——把本篇研究结论拆成 4 周 30 天可执行任务，并对两份笔记做了张力点对比和融合改造路径。

## Summary

ECC（Everything Claude Code）是当前最成熟的 AI 编码增强框架，182K+ Star，提供 63 个 Agent、249 个 Skill、79 个命令。但它的真正价值不在代码量，而在 10+ 月日常使用提炼的实战模式——记忆持久化、Token 优化、策略压缩、并行化编排。这些模式是可迁移的，任何有对应 Hook 的工具（包括 Codex）都能复用。

## Core Question

**AI 编码增强框架的核心竞争力是什么？是代码/配置，还是实战经验提炼的模式？**

答案：==模式 > 代码==。ECC 的护城河是"10 个月日常使用提炼的实战模式"，不是 63 个 Agent 定义文件。

---

## 一、ECC 是什么

ECC = Everything Claude Code，一个 harness-native operator system，为 AI 编程工具提供专业 Agent、技能、Hook 自动化和持续学习能力。

- **作者**：Affaan Mustafa，Anthropic x Forum Ventures 黑客松冠军
- **版本**：2.0.0-rc.1
- **核心组成**：63 Agents + 249 Skills + 79 Commands + Hook 系统 + 持续学习 v2.1

### 核心能力一览

| 能力 | 说明 |
|------|------|
| 63 个专业 Agent | planner、architect、code-reviewer、security-reviewer、各语言 build-error-resolver |
| 249 个技能 | TDD、安全审查、前后端模式、Django/Spring Boot/Laravel/Go/Rust 等领域技能 |
| 79 个命令 | `/plan`、`/code-review`、`/build-fix`、`/security-scan`、`/quality-gate` |
| Hook 自动化 | 会话开始/结束、自动格式化、密钥检测、策略压缩建议 |
| 持续学习 v2.1 | 本能提取 → 置信度评分 → 项目隔离 → 演化为技能 |
| AgentShield | 安全审计器，102 条规则，1282 测试，98% 覆盖率 |
| 跨工具支持 | Claude Code、Cursor、Codex、OpenCode、Copilot、Zed、Gemini |

---

## 二、架构设计：DRY Adapter 模式

```
            ┌─────────────────────────────────┐
            │         共享核心层               │
            │  agents/ skills/ rules/ hooks/   │
            └──────────┬──────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
  Claude Code      Cursor        Codex
   适配器          适配器         适配器
  (原生)      (adapter.js)   (sync 脚本)
```

**关键思路**：核心内容只写一份，每个工具写一个适配器做格式转换。

### 跨工具适配真实程度

| 工具 | Hook 支持 | Agent 支持 | 适配程度 |
|------|:---------:|:----------:|:--------:|
| Claude Code | 8 事件 | 63 Agents | 100% |
| Cursor | 15 事件 | 共享 | ~70% |
| OpenCode | 11 事件 | 12 Agents | ~50% |
| Codex | ==10 事件== | 3 角色 | ~40% |
| Copilot | 无 | 无 | ~20% |

> [!warning] 关键纠正
> ECC 声称"Codex 没有 Hook"是==不准确的==。Codex 有 10 个 Hook 事件（比 Claude Code 的 8 个还多），而且是 Rust 原生实现。更准确的说法是"ECC 还没有适配 Codex 的 Hook 系统"。

### Codex Hook 系统（来自 `codex-rs/hooks/src/lib.rs`）

| # | 事件名 | 说明 | Claude Code 有无 |
|---|--------|------|:---------------:|
| 1 | `SessionStart` | 会话开始 | ✅ |
| 2 | `UserPromptSubmit` | 用户提交 prompt | ❌ Codex 独有 |
| 3 | `PreToolUse` | 工具调用前 | ✅ |
| 4 | `PermissionRequest` | 权限请求决策 | ❌ Codex 独有 |
| 5 | `PostToolUse` | 工具调用后 | ✅ |
| 6 | `PreCompact` | 上下文压缩前 | ✅ |
| 7 | `PostCompact` | 上下文压缩后 | ✅ |
| 8 | `SubagentStart` | 子代理启动 | ❌ Codex 独有 |
| 9 | `SubagentStop` | 子代理停止 | ❌ Codex 独有 |
| 10 | `Stop` | Agent 停止 | ✅ |

Codex Hook 的架构特点：
- **Rust 原生实现**（不是 shell 脚本）
- **Request → Outcome 结构化模式**（不是 exit code）
- **Plugin 声明式注册**
- **分层配置**（用户级/项目级/会话级）
- **受管 Hook 模式**（`allow_managed_hooks_only`）

---

## 三、持续学习系统深度拆解

### 三阶段流水线

```
会话活动 → Hook 捕获观察 → Observer Agent 分析 → 本能库 → 演化为技能
   ↓            ↓                ↓                ↓            ↓
 (实时)    (100%可靠)      (后台 Haiku)      (YAML 文件)   (SKILL.md)
```

### 第一阶段：观察捕获（observe.sh）

- 注册为 `PreToolUse` + `PostToolUse` Hook
- **为什么用 Hook 不用 Skill**：Hook 100% 触发，Skill 只有 50-80%
- 捕获内容：工具名、输入、输出、会话 ID、项目 ID
- **项目感知**：`git remote get-url origin` 哈希 → 项目 ID
- **隐私保护**：自动脱敏（api_key/token/secret → [REDACTED]）
- **反自观察**：5 层防护（入口过滤、Hook 配置、环境变量、agent_id、路径排除）
- **节流信号**：每 20 次观察才发 SIGUSR1

### 第二阶段：模式检测（Observer Agent）

检测 4 类模式：

| 模式 | 检测逻辑 | 产出 |
|------|---------|------|
| 用户纠正 | 后续消息纠正前一个动作 | "When doing X, prefer Y" |
| 错误解决 | 错误后跟修复，同类型多次 | "When encountering error X, try Y" |
| 重复工作流 | 相同工具序列多次使用 | "When doing X, follow steps Y, Z, W" |
| 工具偏好 | 某些工具一致偏好 | "When needing X, use tool Y" |

**置信度体系**：

| 观察次数 | 初始置信度 | 含义 |
|---------|-----------|------|
| 1-2 次 | 0.3 | 试探性 |
| 3-5 次 | 0.5 | 中等 |
| 6-10 次 | 0.7 | 强 |
| 11+ 次 | 0.85 | 非常强 |

动态调整：确认 +0.05，矛盾 -0.1，每周无观察 -0.02（衰减）

### 第三阶段：演化

命令：`/instinct-status`、`/evolve`、`/instinct-export`、`/instinct-import`、`/promote`、`/projects`

演化过程：多个相关本能 → 聚类分析 → 生成 skill/command/agent

**项目隔离**（v2.1 关键改进）：
- 语言/框架约定 → project 作用域
- 安全实践/通用最佳实践 → global 作用域
- 默认 project，拿不准就 project
- 自动提升：同一本能 2+ 项目 + 平均置信度 ≥ 0.8 → global

---

## 四、Longform Guide 实战模式

来源：[The Longform Guide to Everything Claude Code](https://x.com/affaan/status/2014040193557471352)（1,921 赞、4,264 收藏）

### 4.1 记忆持久化

**会话间记忆传递**：
- 每次会话结束创建状态摘要（`.tmp` 文件）
- 内容：什么有效（附证据）、什么无效、还有什么没试
- 下次会话加载该文件继续

**记忆持久化 Hook 链**：
- `PreCompact`：压缩前保存重要状态
- `SessionStart`：新会话加载前次上下文
- `SessionEnd`：会话结束持久化学习

**动态系统提示注入**（高级）：
- 用 `--system-prompt` 按场景注入，而非全部放 CLAUDE.md
- 系统提示 > 用户消息 > 工具结果的指令层级
- 三个场景文件：dev.md / review.md / research.md

### 4.2 Token 优化

**模型路由**：
- Haiku：重复性任务、多 Agent 中的 worker
- Sonnet：90% 日常编码
- Opus：架构决策、安全关键代码、首次失败后升级

> [!tip] Haiku + Opus 组合比 Sonnet + Opus 更省钱
> Haiku vs Opus 是 5 倍价差，Sonnet vs Opus 只有 1.67 倍。

**工具优化**：
- mgrep 替代 grep，平均减少约 50% token
- 后台进程用 tmux，只给 Claude 摘要
- MCP 功能转化为 Skill/Command 释放上下文窗口

**代码库优化**：
- 模块化（几百行而非几千行）= 更少 token + 更高首次成功率
- 精简代码库 = 更便宜的 token 成本

**系统提示瘦身**：18K → 10K token，节省 41% 静态开销

### 4.3 验证循环

**两种模式**：
- 检查点式：线性工作流，每个里程碑验证
- 连续式：每 N 分钟或重大变更后跑全量测试

**评分器类型**（来自 Anthropic）：
- 代码评分器：快、便宜、客观但脆弱
- 模型评分器：灵活但不确定且贵
- 人类评分器：金标准但慢且贵

### 4.4 并行化

- 主聊天做代码变更，分叉做研究/文档
- 大多数时候 2-3 个实例就够
- Git Worktree 隔离，`/rename` 命名避免混乱
- 级联法：新任务向右开，从左到右扫描，最多 3-4 个任务

### 4.5 Agent 编排层级

| 层级 | 模式 | 难度 | 价值 |
|------|------|------|------|
| Tier 1 | Subagent、元提示、多问用户 | 低 | 直接增益 |
| Tier 2 | 长运行 Agent、并行多 Agent、角色多 Agent | 高 | 高方差 |

> [!important] 建议
> 从 Tier 1 开始，只在真正需要时才上 Tier 2。

---

## 五、ECC vs Superpowers 对比

| 维度 | ECC | Superpowers |
|------|-----|-------------|
| **核心理念** | 实用主义（什么有效用什么） | 纪律主义（铁律、反合理化） |
| **编排方式** | 灵活分派（按任务类型选 Agent） | 严格链式（brainstorming → plan → TDD → review → finish） |
| **记忆系统** | 三层（会话日志 + 持续学习 + 本能库） | 无 |
| **Token 优化** | 系统性（模型路由 + 工具替换 + 代码模块化） | 无专门优化 |
| **验证** | 检查点式 + 连续式 + 三类评分器 | verification-before-completion（铁律式） |
| **TDD** | 灵活（RED→GREEN→IMPROVE） | 绝对铁律（无失败测试不写代码，11 条反合理化） |
| **审查** | 语言专属 reviewer（63 个） | 两阶段审查（规格合规 → 代码质量） |
| **Hook 利用** | 深度（4 个生命周期 Hook） | SessionStart 注入 using-superpowers |
| **跨工具** | 多平台适配 | 仅 Claude Code |

### 冲突点

1. **编排权争夺**：两者都想当"总指挥"，但编排逻辑不同
2. **TDD 严格度**：Superpowers 铁律 vs ECC 灵活
3. **审查流程**：两阶段 vs 语言专属
4. **Superpowers 的"1%规则"过于激进**：几乎任何编码任务都会触发完整链式流程

### 建议

保持 Superpowers 为主，选择性吸收 ECC 的独有能力：

| 借鉴什么 | 为什么值得 |
|---------|----------|
| 安全审计 | Superpowers 没有安全扫描 |
| 持续学习 | Superpowers 没有自我进化机制 |
| 语言专属 reviewer 知识 | Superpowers 的 code review 是通用的 |
| Token 优化 | Superpowers 没有成本控制 |

---

## 六、Codex 生态现状

### GitHub 1000+ Star 项目

| 项目 | Star | 类型 | Codex 适配程度 |
|------|------|------|:------------:|
| rohitg00/pro-workflow | 2,249 | 工作流 + 自纠正记忆 | 多平台兼容 |
| ciembor/agent-rules-books | 1,690 | AGENTS.md 规则集 | 多平台兼容 |
| CloudAI-X/claude-workflow-v2 | 1,364 | 工作流插件（Python） | 多平台兼容 |

> [!warning] 关键发现
> 1000+ Star 的项目==全部是多平台兼容==（Claude Code 为主，Codex 为辅），没有一个 Codex 原生框架达到 1000 Star。

### 值得关注的 Codex 原生项目

| 项目 | Star | 亮点 |
|------|------|------|
| agent-sh/agentsys | 832 | 24 插件 + 49 Agent + 44 Skill |
| fcakyon/claude-codex-settings | 710 | 实战配置，含自动 commit/PR/部署 |
| mturac/everything-openai-codex | 65 | ==Codex 版 ECC==，最接近的 Codex 原生方案 |
| GODGOD126/self-improving-for-codex | 125 | Codex 原生自改进系统 |

### Codex 生态瓶颈

1. **经验积累不足**：没有"10 个月日常使用提炼的实战模式"
2. **Hook 开发门槛高**：Rust 原生 vs Claude Code 的 shell 脚本
3. **ECC 的"Codex 没有 Hook"说法不准确**：Codex 有 10 个 Hook 事件，ECC 只是没适配

---

## 七、可迁移的模式资产

最有价值的不是代码，是==模式==：

| 模式 | 迁移条件 | Codex 可用性 |
|------|---------|:-----------:|
| 会话间记忆传递 | SessionStart/Stop Hook | ✅ Codex 有 |
| 策略压缩 | PreCompact Hook | ✅ Codex 有 |
| 模型路由 | 多模型支持 | ✅ Codex 有 |
| Agent 编排层级 | Subagent 支持 | ✅ Codex 有 SubagentStart/Stop |
| 持续学习 | PreToolUse/PostToolUse Hook | ✅ Codex 有 |
| 密钥检测 | UserPromptSubmit 或 PreToolUse | ✅ Codex 独有 UserPromptSubmit |

> [!success] 结论
> Codex 的 Hook 系统实际上比 Claude Code 更完善（10 事件 vs 8 事件，结构化 I/O），只是生态还没跟上。ECC 的实战模式理论上==全部可以迁移到 Codex==，需要的是适配层而非重新设计。

---

## 八、五大核心抽象与 Hermes 对照

> [!info] 来源

### 8.1 五大核心抽象的层次链

ECC 的 5 个抽象不是并列的，而是==有层次和演化方向的==：

```
Command（用户主动触发）→ Agent（角色分派）→ Skill（领域知识）→ Hook（物理拦截）→ Instinct（原子学习）
```

- **粒度**：从粗到细
- **触发**：从用户主动到系统自动
- **演化路径**：Instinct → Skill → Command/Agent（原子聚合为模块）

> [!important] 这条演化链是 ECC 最核心的设计观
> 远比组件数量更重要。Instinct 是最小学习单位，Skill 是聚合，Rule 是蒸馏——三者形成闭环。

### 8.2 Agent 路由的物理护栏

每个 Agent 的 YAML 前置元数据不只是描述，还有==物理约束==：

```yaml
name: planner
description: Expert planning specialist... Use PROACTIVELY when...
tools: ["Read", "Grep", "Glob"]  # 白名单：只能看不能写
model: opus                       # 模型偏好
```

- `tools` 白名单 = prompt injection 防御的物理护栏（planner 无法"顺手实现"）
- `description` 里的 "Use PROACTIVELY when..." = 路由依据，让主 agent 主动调度
- `model` = 成本控制（规划用 opus，review 用 sonnet，分类用 haiku）

### 8.3 Skill 的标准写法：决策清单而非教程

ECC skill 的结构模板（以 `agent-harness-construction` 为例，73 行）：

1. **开门见山**：何时使用，不超过 2 行
2. **核心模型**：1 段话给心智模型
3. **分主题展开**：每子主题 3-6 条 bullet，不超过半屏
4. **结尾一定有 anti-patterns**

> [!tip] 对比
> Hermes 的 skill 平均偏长，缺统一的 anti-patterns 段。可以以 ECC 的 73 行模板为目标进一步压缩。

### 8.4 三个值得单独读的 meta-skill

| Skill | 核心价值 |
|-------|---------|
| `agent-harness-construction` | "工具粒度三档制"——高风险用 micro-tool，read/edit/search 用 medium，round-trip 是瓶颈才用 macro-tool |
| `agentic-engineering` | "15 分钟单元规则"——每个 agent 子任务必须独立可验证、单一主导风险、有明确完成条件 |
| `context-budget` | 系统性上下文预算诊断：扫描所有组件 token 消耗，按"始终/偶尔/极少需要"三档分类 |

### 8.5 安全三层防护

| 层 | 机制 | 特点 |
|----|------|------|
| 第一层 | Prompt Defense Baseline | 每个 agent 文件开头注入 6 句防御基线，子 agent 也有最低防线 |
| 第二层 | Rules（始终遵循规则集） | 12 语言目录 + common/，rule 是"始终自动加载"，skill 是"按需触发" |
| 第三层 | Hooks 物理拦截 | 跟 LLM 听不听话无关，hook 退 2 直接阻断 |

> [!warning] 关键洞察
> 规则与 skill 的差异：**rule 是"始终自动加载"，skill 是"按需触发"**。`/rules-distill` 命令就是把 skill 共性蒸馏成 rule——先以 skill 形式进库，被多个 skill 引用后再升级为 rule。这提供了一种健康的演化路径。

### 8.6 Harness Optimizer：改 harness 不改产品代码

> "Raise agent completion quality by improving harness configuration, not by rewriting product code."

5 步工作流：
1. 跑 `/harness-audit` 拿基线分
2. 定位前 3 个杠杆区域（hook / eval / 路由 / 上下文 / 安全）
3. 提出最小、可回滚的配置改动
4. 应用改动并跑验证
5. 报告改动前后的 delta

> [!tip] 方法论价值
> 把"调 harness"和"写业务代码"分成两件事——前者用 meta-agent，后者用业务 agent，互不交叉。

---

## 九、Hermes 视角的 7 条改造建议

### 建议 1：写一份 context-budget skill 做体检（成本：1 天）

扫全部 skill，统计行数/token 估算/description 长度，找出 description > 30 字的、SKILL.md > 400 行的、内容重叠的。一次体检大概率能省下 30%+ system prompt 开销。

### 建议 2：把 Anti-Patterns 列为 skill 标准段（成本：渐进改）

ECC 每个 skill 末尾都有 anti-patterns 段，明确说"什么时候不要用 / 什么是常见误用"。建议把 anti-patterns 写进 skill authoring 的强制结构。

### 建议 3：加一层 Hook 中间件（成本：3-5 天，收益最大）

能解决的真实痛点：
- 禁止任何工具调用读 `~/.ssh/ ~/.aws/ .env` 等敏感路径——物理拦
- `rm -rf` / `git push --force` / `git reset --hard` 之前必须二次确认
- 调用 `send_message` 之前对消息做 PII 扫描
- 每 50 次工具调用提示一次"该 compact 了"

### 建议 4：把"专家 agent"沉淀成显式角色库（成本：每个半天）

不必照抄 63 个，挑真相关的：
1. **code-reviewer** — 已有 `webinfra-code-review` skill，可包成专家
2. **planner** — 已有 `writing-plans` skill，可升级成"必走 plan → confirm → execute"
3. **investment-analyst** — A 股/加密/全球 AI capex，固定数据源 skill
4. **content-editor** — 公众号/小红书风格，配规则降漂移

### 建议 5：试做"会话观察 → 候选 instinct"管线（成本：周级）

最小可行版本：
1. Hook 在每次工具调用后落一条 jsonl
2. 每天后台 cronjob 用便宜模型扫昨天的 jsonl，抽 5-10 条候选 instinct
3. 每周给用户看一次候选清单，勾选"采纳/改写/丢弃"
4. 采纳的写到 memory 或升级成 skill

> [!important] 为什么比"agent 自己决定 memory.add"更稳
> 后者已经踩过几次过期/偏题的坑。观察 + 候选 + 用户审核的渐进式管线更可控。

### 建议 6：把 SOUL.md 精简版注入所有子 agent prompt 头部（成本：当天）

子 agent 比主 agent 更容易被 prompt injection——它读的内容更脏。把 SOUL.md 的 Prompt Injection Defense 做成 100 字以内精简版，自动注入每次 delegate_task 的 context。

### 建议 7：把 always-on 规则升级为 rules.md（成本：1 天）

跨任务跨场景始终适用的规则（禁打印密钥、A 股 100 股整数倍铁律、AI 味句式黑名单、消息默认中文等），从 SOUL.md / memory / skill 中抽出来做一份 `rules.md` 自动注入。

> SOUL.md 是身份，rules.md 是硬约束——两者区分。

---

## 十、风险与槽点

| 问题 | 说明 |
|------|------|
| **维度膨胀** | 63 agents / 249 skills / 79 commands，没人能记住。先制造问题再造解药的模式。 |
| **一人维护** | commit 90%+ 来自 affaan-m，1.x → 2.0 大量 breaking change。当方法论参考，不要当依赖。 |
| **Skill 质量参差** | agent-harness-construction 等是真方法论；行业垂直 skill 明显凑数。不要照单全收。 |
| **Star ≠ DAU** | 18 万 star 但 npm 周下载远低于预期。不要把 star 数当工程质量证书。 |
| **ecc2 控制面是 alpha** | 官方说"real and usable for experimentation, but roadmap incomplete"。主要价值还是静态资产。 |
| **安全声明强，实际止步于 hook** | hook 之外的工具调用、子进程行为、数据外传仍靠 LLM 自觉。agent 安全本身是未解问题。 |

---

## 十一、一句话结论（综合两个来源）

> [!success] ECC 的最大价值
> **不在 249 个 skill，在它把"agent 应该怎么被治理"做成了一套层次分明、可装配的零件。**

三句话精华：
1. **5 抽象层次链**：Command → Agent → Skill → Hook → Instinct，粒度从粗到细，触发从主动到自动，演化从原子到聚合
2. **把准入门槛焊在工具调用上**：能 hook 拦的就别靠 LLM 自觉
3. **持续学习的真正含义不是"让 agent 变聪明"**，而是"让会话成为可重用资产"——观察 → 抽 instinct → 评估 → 升级 skill 的闭环

---

## Open Questions

1. Codex 的 Rust Hook 系统如何写适配层？需要 Rust 开发还是可以 shell 脚本桥接？
2. ECC 的 observe.sh 能否直接适配 Codex Hook 的输入/输出格式？
3. Superpowers + ECC 精华的融合方案具体怎么落地？
4. 持续学习系统的演化产物（skill/command/agent）质量如何自动验证？

## Next Expansion

- 实际在 Codex 上尝试实现一个 Hook 适配层
- 对比 Codex Hook 的 Request/Outcome 结构与 Claude Code 的 stdin/exit code 模式
- 研究 `everything-openai-codex` 的架构设计
- 探索 TraeCLI skill 体系如何吸收 ECC 的实战模式
- 落地 Hermes 视角的 7 条改造建议（优先：Hook 中间件 > context-budget 体检 > 会话观察管线）

## 参考资料

| 资料 | 链接 |
|------|------|
| ECC 主仓库 | [github.com/affaan-m/ECC](https://github.com/affaan-m/ECC) |
| ECC Longform Guide | [x.com/affaan/status/2014040193557471352](https://x.com/affaan/status/2014040193557471352) |
| Codex Hook 源码 | [github.com/openai/codex/tree/main/codex-rs/hooks](https://github.com/openai/codex/tree/main/codex-rs/hooks) |
| Codex 原生 ECC 等价物 | [github.com/mturac/everything-openai-codex](https://github.com/mturac/everything-openai-codex) |
