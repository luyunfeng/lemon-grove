# Loop Engineering 深度解析：从 Prompt Engineering 到 Loop Engineering

目录

什么是 Loop Engineering 四代演进 六要素架构 Agent Loop 详解 Claude Code 的 Loop /goal 命令 /loop 命令 对比：各工具 Loop 如何在 Claude Code 触发 Loop 风险与注意事项

Research & Learning · AI Coding Paradigm

# Loop Engineering 深度解析

从 "Prompt Engineering" 到 "Loop Engineering" —— AI 编程领域正在经历一场范式转变。 你不再手动给 agent 写提示，而是设计让系统自动给 agent 写提示的循环。 

## 什么是 Loop Engineering

> "You shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents." — Peter Steinberger, OpenClaw 创始人, 2026-06-07

**Loop Engineering（循环工程）** 是 2026 年在 AI 编程领域兴起的一个核心概念。 它的核心思想是：**用设计自动调用 agent 的系统，来替代你作为手动提示 agent 的人** 。 

Anthropic Claude Code 负责人 Boris Cherny 也表达了类似观点： _"我不再手动提示 Claude 了。我运行着自动提示 Claude 的循环。我的工作是写循环。"_

**核心转变** ：从"写一个好 prompt" → "设计一个能持续生成好 prompt 的系统" 

### 四代演进

2023 · Gen 1

AutoGPT

证明了需求，但陷入无限循环和高额 API 账单

2023 · Gen 2

ReAct, Reflexion

学术框架，形式化"推理+行动"的交错结构

2024 · Gen 3

OODA Loop, Dual Loop

架构模式出现，内外双循环、多代理编排

2025-2026 · Gen 4

/loop, /goal

产品化工具让 Loop Engineering 成为主流实践

### 六要素架构

Loop Engineering 的架构包含六个核心组件：

模块| 功能| 说明  
---|---|---  
Automations | 定时触发器 | 用于自动发现/分类任务，如 cron 调度  
Worktrees | 并行 agent 隔离 | 每个 agent 独立工作目录，避免文件冲突  
Skills | 项目知识固化 | 用 SKILL.md 持久化跨会话的知识  
Plugins | 外部工具集成 | 通过 MCP 连接 JIRA、Postgres、Sentry 等  
Sub-agents | 角色分离 | 分离"实现者（maker）"与"检查者（checker）"  
Memory | 外部持久化 | 对话记录之外的 durable state  
  
## Agent Loop 详解

**Agent Loop（代理循环）** 是 AI agent 的底层工作机制，指的是让 AI agent 能够 **自主决策 → 执行行动 → 观察结果 → 重复** 直到任务完成的架构模式。 

感知  
Perceive

→

推理  
Reason

→

行动  
Act

→

观察  
Observe

→

感知  
...

ReAct 模式：Reasoning + Acting 的循环交错 

这是 **ReAct（Reasoning + Acting）** 模式的工程实现。一个 turn（回合）的完整过程：

  1. Claude 生成包含工具调用的输出
  2. SDK 执行这些工具
  3. 结果自动反馈给 Claude
  4. Claude 基于新信息继续推理

外层循环（Loop Engineering）

Loop Engineering 在 Agent Loop 之上构建了一个**外层循环** ： 你不再是给 agent 写提示的人，而是设计**自动给 agent 写提示的系统** 。 

触发条件  
cron / event

→

生成提示  
prompt builder

→

Agent Loop  
inner loop

→

验证结果  
evaluator

→

记录状态  
memory

## Claude Code 的 Loop 机制

Claude Code 提供了业界最完整的 Loop Engineering 工具链，核心是两个命令：

### /goal —— 目标驱动循环

`/goal` 是 Claude Code v2.1.139 引入的**原生目标驱动循环** 。 它让 Claude 持续工作，直到满足你设定的完成条件。 

核心机制：Worker + Evaluator 双模型分离

每次 turn 结束后：

  1. 条件 + 完整对话记录提交给**评估器模型** （默认 Haiku）
  2. 评估器返回 yes/no + 理由
  3. **"no"** → Claude 继续工作，评估器的理由作为指导包含在下一次输入中
  4. **"yes"** → 清除目标，停止循环

    
    
    # 基础用法
    /goal all tests in test/auth pass, and the lint step is clean
    
    # 带 turn 限制
    /goal find and fix the flaky auth tests or stop after 20 turns
    
    # 可验证的完成条件（评估器只能"看到"对话中出现的内容）
    /goal run npm test -- --coverage and the printed coverage line shows >= 80%
    
    # 查看状态
    /goal
    
    # 清除目标
    /goal clear

**关键限制** ：评估器**不调用工具** ——只能判断 Claude 已在对话中展示的内容。 所以条件必须是"对话中可见"的，而不是外部系统的状态。 

### /loop —— 定时循环

`/loop` 是一个**会话级调度器** ，让提示按设定间隔自动触发。
    
    
    # 每 5 分钟检查 CI 状态
    /loop 5m check the GitHub Actions workflow and notify me when it completes
    
    # 每 30 分钟检查 PR
    /loop 30m check PR #456 for new comments or requested changes
    
    # 动态间隔（Claude 自选）
    /loop check the build
    
    # 循环执行其他 slash 命令
    /loop 20m /review-pr 1234

/loop 关键限制

• 任务只在 Claude Code 运行且空闲时触发

• 错过的触发不会补执行

• 新对话清除任务；`--resume` 恢复未过期的

• 重复任务 7 天后过期

• 每会话最多 50 个任务

### /goal vs /loop 对比

维度| /goal| /loop  
---|---|---  
核心功能| 设定持久性目标，定义"完成"状态| 创建循环执行机制，持续运行  
触发方式| 上一 turn 完成后立即开始下一 turn| 时间间隔到达后触发  
停止方式| 模型确认条件满足即停止| 手动停止或 Claude 决定工作完成  
使用场景| 需要明确终态的任务| 需要反复执行的任务  
组合用法| /goal 定义完成标准 + /loop 持续执行直至达标  
  
## 对比：各 AI 编程工具的 Loop 机制

工具| Loop 特点| 自主模式| 形态  
---|---|---|---  
**Claude Code** | `/goal` 目标驱动 + `/loop` 定时循环；双模型分离评估 | Auto Mode（分类器风险评估） | 终端 CLI  
**OpenAI Codex** | `/goal` 命令（Ralph Loop）；显式无状态；自动压缩 | `full-auto` approval mode | 终端 CLI  
**Cursor** | Composer 模型；最多 8 个并行 agent；git worktree 隔离 | Agent Mode 自主执行 | VS Code fork  
**Cline** | Plan/Act 模式切换；Auto Approve 分级权限；MCP 集成 | YOLO Mode（全自动，无安全检查） | VS Code 扩展 / CLI  
**Aider** | Git-native 终端结对编程；每编辑自动提交；多模型支持 | 自动编辑 + 自动提交 | 终端 CLI  
  
**关键差异** ：OpenAI 让模型自主决定"完成"，Anthropic 坚持独立评估器默认介入。 Claude Code 的 `/goal` 使用 Haiku 作为独立评估器，更安全、更可控。 

## 标准开发流程：如何在 Claude Code 触发 Loop

开发一个需求时，标准流程如下：

### Step 1: 进入 Auto Mode（可选但推荐）
    
    
    # 方式 1：交互式切换
    按 Shift+Tab 循环切换到 auto 模式
    
    # 方式 2：环境变量
    CLAUDE_CODE_ENABLE_AUTO_MODE=1 claude
    
    # 方式 3：命令行
    claude --permission-mode auto

Auto Mode 使用基于 Sonnet 4.6 的分类器，对每个工具调用进行风险评估。 安全操作自动通过，风险操作被阻止。这是 Loop Engineering 的关键使能器。 

### Step 2: 使用 /goal 定义完成标准
    
    
    # 示例 1：实现一个功能
    /goal implement user authentication with JWT, all tests in test/auth/ pass
    
    # 示例 2：重构代码
    /goal extract the database logic from handlers.go into a new db/ package,
            and verify with go test ./...
    
    # 示例 3：修复 bug
    /goal fix the race condition in conn_pool.go, run go test -race ./... with 0 failures

### Step 3: 组合 /goal + /loop 监控进度
    
    
    # 定义完成标准
    /goal All GitHub Actions workflows pass
    
    # 持续检查直至达标
    /loop every 3m until: CI passes

### Step 4: 使用 Skills 和 Subagents 构建复杂 Loop
    
    
    # 创建 Skill（.claude/skills/review-pr.md）
    # 创建 Subagent（.claude/agents/code-reviewer.md）
    
    # 在 Loop 中调用
    /loop 1h /skill:review-pr --agent code-reviewer

### Step 5: Headless/CI 模式
    
    
    # 非交互式运行 /goal
    claude -p "/goal CHANGELOG.md has an entry for every PR merged this week"
    
    # 带 token 限制
    claude -p "/goal --tokens 250K do deep research and build the full prototype" \
           --output-format json
    
    # 使用 Agent View 监控多个会话
    claude agents

## 风险与注意事项

**1\. 验证仍靠人** ：无人值守的循环也在无人值守地犯错。循环可以自动运行，但"完成"的验证仍需人负责。 

**2\. 理解债务加速** ：循环产出你未亲自编写的代码越快，理解差距越大。 

**3\. 认知投降（Cognitive Surrender）** ：不加判断地接受循环返回的一切。 

**硬护栏设置建议** ：

  * 设置迭代上限（`max_turns`）
  * 设置 token 预算（`max_budget_usd`）
  * 设置无进展检测（N 轮无变化则停止）
  * 设置熔断机制（错误率超过阈值则停止）

关键概念速查

**Agent Loop** ：AI agent 的底层"感知-推理-行动-观察"循环（所有工具都有）

**Loop Engineering** ：在 Agent Loop 之上设计外层自动化系统（2026 年新范式）

**Claude Code /goal** ：目标驱动的循环命令，带独立评估器（Haiku）

**Claude Code /loop** ：定时触发的循环命令

**Claude Code Auto Mode** ：安全的全自动权限模式，分类器风险评估
