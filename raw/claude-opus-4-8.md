# 评价 Claude Opus 4.8

## 概要

Anthropic 于 2026 年 5 月 28 日发布 Claude Opus 4.8，这是 Opus 级别模型的又一次迭代升级。同日 Anthropic 宣布完成 650 亿美元 H 轮融资，投后估值 9650 亿美元。

## 核心更新

### 1. 诚实性与可靠性提升

早期测试者反馈 Opus 4.8 更愿意标注不确定性，更少做出无根据的断言。评估显示：**它让代码中的缺陷被忽视的概率比前代降低了约 4 倍**。这对编程和代码审查场景意义重大——模型不再"装懂"，而是主动暴露问题。

### 2. Effort Control（投入度控制）

claude.ai 和 Cowork 中新增投入度控制，用户可以调节 Claude 回复的投入程度。四个级别：

| 级别 | 说明 |
|------|------|
| **Default（High）** | 质量与体验的最佳平衡，编程任务消耗 token 与 Opus 4.7 相当但效果更好 |
| **Extra（xhigh）** | 推荐用于困难任务和长时间异步工作流 |
| **Max** | 模型投入更多 token 追求最佳结果 |
| **Low** | 快速响应，消耗更少速率限额 |

Claude Code 中速率限额已上调以适配更高投入级别的 token 消耗。

### 3. Dynamic Workflows（研究预览）

> [!note] Claude Code v2.1.154+，所有付费计划可用
> Dynamic Workflows 是 Claude Code 的功能，Pro / Max / Team / Enterprise 均可使用（Pro 需在 `/config` 中手动开启）。支持 CLI、Desktop、IDE 扩展、非交互模式（`claude -p`）和 Agent SDK。

#### 核心架构

Dynamic Workflows 本质是 **JavaScript 脚本编排器**。Claude 根据你的任务描述自动编写 JS 脚本，由独立于主会话的运行时在后台执行。关键设计：

- **中间结果留在脚本变量中，不占用 Claude 上下文窗口**——只有最终答案回到主对话
- **可恢复性**：在同一会话内，已完成的代理返回缓存结果，未完成的继续运行
- **编排逻辑被代码化**，可重复执行，而非依赖 Claude 逐轮决策

与 Subagents / Skills 的对比：

| 维度 | Subagents | Skills | Workflows |
|------|-----------|--------|-----------|
| 编排者 | Claude 逐轮决定 | Claude 按提示执行 | 脚本决定 |
| 中间存储 | Claude 上下文 | Claude 上下文 | 脚本变量 |
| 可重复性 | Worker 定义 | 指令 | 编排本身 |
| 规模 | 每轮几个任务 | 同 Subagents | **数十到数百个代理** |
| 中断恢复 | 重启当前轮 | 重启当前轮 | 同会话内可恢复 |

#### 并行子代理体系

Claude Code 现有三层并行机制：

1. **Subagents**：主代理按需委派，结果回到主对话。适合聚焦任务。
2. **Agent Teams**：多个独立 Claude Code 实例协作，通过共享任务列表和邮箱通信。适合需要讨论和协调的复杂工作。实验性功能，需 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` 启用。
3. **Dynamic Workflows**：脚本驱动的规模化编排，适合可分解为大量独立子任务的工作。

#### 触发方式

- 在 prompt 中包含 "workflow" 关键词，Claude 会自动编写工作流脚本（按 `alt+w` 可忽略）
- Ultracode 模式（`/effort ultracode`）：结合 `xhigh` 推理投入 + 自动工作流编排，Claude 自主判断何时启动工作流
- 内置命令 `/deep-research`：多角度搜索、交叉验证来源、投票筛选声明、返回带引用的报告

#### 限制

| 约束 | 原因 |
|------|------|
| 运行中不可接受用户输入 | 仅代理权限提示可暂停；需阶段签收则分多次运行 |
| 脚本无直接文件系统/Shell 访问 | 代理读写执行，脚本只做协调 |
| 最多 16 个并发代理（CPU 核心少则更少） | 限制本地资源 |
| 单次运行最多 1,000 个代理 | 防止失控循环 |
| 仅同一会话内可恢复 | 退出 Claude Code 后下次需重新开始 |

#### 成本考量

单次运行可能消耗大量 token。建议：运行前检查 `/model`，让 Claude 将不需要最强模型的阶段路由到更小的模型，随时可停止而不丢失已完成的工作。

#### 保存与复用

按 `s` 保存脚本为命令，存放在 `.claude/workflows/`（项目级，可版本控制）或 `~/.claude/workflows/`（个人级，跨项目）。保存后以 `/<command-name>` 调用。

### 4. API 更新

Messages API 现在允许在 messages 数组中插入 system 条目，开发者可以在任务中途更新指令而不破坏 prompt cache，也无需通过 user turn 来传递更新。典型场景：代理运行时动态更新权限、token 预算或环境上下文。

### 5. Fast Mode 降价

Opus 4.8 的 fast mode（2.5× 速度）比前代模型**便宜 3 倍**。定价：

| 模式 | 输入 | 输出 |
|------|------|------|
| Standard | $5/M tokens | $25/M tokens |
| Fast mode | $10/M tokens | $50/M tokens |

Standard 价格与 Opus 4.7 持平。

## 基准测试

Opus 4.8 在编程、代理技能、推理和知识工作任务上全面超越 Opus 4.7 和 GPT-5.5。亮点：

- Online-Mind2Web（浏览器代理）得分 **84%**，显著超越 Opus 4.7 和 GPT-5.5
- Terminal-Bench 2.1：使用 Terminus-2 公共测试框架评测（GPT-5.5 使用 Codex CLI 框架得分为 83.4%）
- OSWorld-Verified：评测方法更新以更好反映真实性能，Opus 4.7 分数更新为 82.3%
- 法律代理基准测试：**首次突破 10% 的全通过标准**，创下最高分
- 金融代理基准测试 v2：取得最高分（Gemini 3.5 Flash 为 57.9%）
- Databricks Genie 代理：Opus 4.8 解锁了"代理推理的阶跃变化"，且 token 成本比 Opus 4.7 **低 61%**

### 早期测试者反馈精选

- **Tom Pritchard（Staff Engineer）**："会问对的问题，能发现自己的错误，当计划不合理时会反驳"
- **Kay Zhu（Co-Founder & CTO）**：在 Super-Agent 基准上"唯一完成所有端到端用例的模型"，在同等成本下超越前代 Opus 和 GPT-5.5
- **Michael Truell（Cursor CEO）**：在 CursorBench 上"在所有投入级别上都超越前代 Opus 模型"，工具调用更高效
- **Scott Wu（Cognition CEO）**："工具使用干净，指令遵循一致"，修复了 Opus 4.7 的注释冗余和工具调用问题
- **Miguel Gonzalez（Tech Lead）**："我们测试过的最强计算机使用和浏览器代理模型"
- **Hanlin Tang（Databricks CTO）**：多模态能力（PDF/图表）在比 Opus 4.7 便宜 61% 的 token 成本下解锁代理推理阶跃变化

## 安全与对齐

Anthropic 对齐团队评估结论：Opus 4.8 在"亲社会特质"指标上达到新高（支持用户自主性、以用户最佳利益行事）。失对齐行为率（欺骗、配合滥用等）显著低于 Opus 4.7，与 Claude Mythos Preview 相当。完整评估见 System Card。

## Subagents 架构补充

Claude Code 的子代理体系在 Opus 4.8 发布时同步成熟，核心设计：

### 内置子代理

| 代理 | 模型 | 工具 | 用途 |
|------|------|------|------|
| Explore | Haiku | 只读 | 快速代码库搜索/分析 |
| Plan | 继承父级 | 只读 | Plan 模式下的研究 |
| General-purpose | 继承父级 | 全部 | 需要探索+行动的复杂多步任务 |

### 子代理关键特性

- **上下文隔离**：冗余输出（搜索结果、日志、文件内容）不进入主对话
- **工具限制**：可为每个子代理配置工具白名单/黑名单
- **成本路由**：任务可路由到更便宜/更快的模型（如 Haiku）
- **Forked Subagents（实验性）**：继承完整对话历史而非全新上下文，共享 prompt cache，比新建子代理更便宜。需 `CLAUDE_CODE_FORK_SUBAGENT=1` 启用
- **持久记忆**：`memory` 字段给子代理跨对话的持久目录（user / project / local 三种作用域）
- **自动压缩**：子代理在约 95% 容量时自动压缩上下文

### Agent Teams（实验性）

多个独立 Claude Code 实例协作的机制：
- **Team Lead** 协调工作，**Teammates** 独立工作
- 共享任务列表 + 邮箱通信系统
- 支持 tmux/iTerm2 分屏显示
- 建议 3-5 个 teammates，每人 5-6 个任务
- 限制：一次只能一个 team，不支持嵌套 team，token 成本线性增长

## 我的评价

### 值得关注的

1. **Dynamic Workflows 是方向性突破**。数百并行子代理的能力，让 AI 从"对话工具"走向"工程编排器"。这与当前 AI Coding 领域的 agent-native 趋势高度吻合——参见 [[agent-native-doc-skill]]。
2. **诚实性提升是隐性收益**。模型主动暴露不确定性比"看起来很厉害但暗藏错误"要安全得多。这对生产环境中的代码生成尤为关键。
3. **Effort Control 是好 UX**。不是所有问题都需要深度推理，给用户选择权比一刀切更合理。
4. **Fast Mode 降价**让高频调用场景的门槛进一步降低。

### 需要观察的

1. **Dynamic Workflows 还是研究预览**。数百子代理的协调质量、错误恢复、成本控制都是未知数。大规模并行 ≠ 大规模有效。
2. **定价结构未变**。Standard $5/$25 仍然是高端价格，对个人开发者和小团队的门槛依然很高。
3. **Mythos 级模型即将推出**。Anthropic 明确表示将在数周内发布超越 Opus 的 Mythos 级模型，这意味着 Opus 4.8 的"顶级"窗口可能很短。

### 与竞品对比

Opus 4.8 在基准上领先 GPT-5.5，但 OpenAI 的节奏也在加快。真正的差异化在于 Dynamic Workflows 这类 agent 编排能力——如果落地效果好，这会成为 Claude 在企业级 AI Coding 赛道的护城河。

## 开放问题

- Dynamic Workflows 在真实大型代码库中的表现如何？子代理间的冲突如何解决？
- Effort Control 的"低投入"模式是否会牺牲太多质量？
- Mythos 级模型的发布时间表和定价策略是什么？
- 并行子代理的成本模型如何？会不会出现"效率提升但账单爆炸"的情况？

## 扩展方向

- 深入研究 Dynamic Workflows 的技术架构和子代理通信机制
- 对比 Claude Code 的 agent 编排与 [[cli-building-for-agent-skills-research]] 中的 agent 设计模式
- 追踪 Mythos 级模型的发布动态
