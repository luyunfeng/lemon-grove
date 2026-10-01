# Superpowers Skill 设计模式深度研究

> [!summary]
> 从 Jesse Vincent 的 Superpowers 项目出发，系统分析 AI 编程 Agent 的 Skill 文件设计模式：Skill 的结构、分类、发现机制、TDD 验证方法、抗合理化设计，以及跨系统（Claude Code Skills、CLAUDE.md、Codex AGENTS.md、Cursor Rules）的通用设计原则。核心结论：好 Skill = 特异性 + 可验证性 + 可发现性 + 抗合理化 + 测试驱动。

## 一、Superpowers 项目全景

### 1.1 项目定位

**Superpowers**（github.com/obra/superpowers）是 Jesse Vincent 创建的 AI 编程 Agent 完整软件开发方法论系统，构建于一组可组合的 Skills 之上。207k+ stars，最具影响力的 AI 编程 Agent 技能框架。

相关仓库：
- `obra/superpowers`：主插件
- `obra/superpowers-skills`：社区可编辑技能（已归档）
- `obra/superpowers-lab`：实验性技能
- `GadaaLabs/claude-code-on-steroids`：从 14 个技能扩展到 24 个

### 1.2 四大核心原则

| 原则 | 含义 |
|------|------|
| Test-Driven Development | 测试先行，永远如此 |
| Systematic over Ad-hoc | 流程优先于猜测 |
| Complexity Reduction | 简洁是首要目标 |
| Evidence over Claims | 验证先于声明成功 |

关键理念：Agent 启动时不立即写代码，而是"退后一步，询问你真正想做什么"。通过对话提取规格说明后，以可消化的块呈现设计供审查。

### 1.3 七步基础工作流

```
1. Brainstorming（头脑风暴）
   ↓ 代码编写前激活
2. Using Git Worktrees（Git Worktree）
   ↓ 设计批准后激活
3. Writing Plans（编写计划）
   ↓ 批准的设计，拆分为 2-5 分钟小任务
4. Subagent-Driven Development（子 Agent 驱动开发）
   ↓ 每任务一个新子 Agent，两阶段审查
5. Test-Driven Development（测试驱动开发）
   ↓ 实现期间激活，RED-GREEN-REFACTOR
6. Requesting Code Review（代码审查）
   ↓ 任务间激活
7. Finishing a Development Branch（完成开发分支）
   ↓ 任务完成后激活
```

## 二、核心技能拆解

### 2.1 头脑风暴技能（Brainstorming）

苏格拉底方法将粗略想法精炼为完整设计：

**Phase 1: Understanding** — 一次只问一个问题，尽可能用多选题，收集目的、约束、成功标准

**Phase 2: Exploration** — 提出 2-3 种方案，每种给出核心架构、权衡、复杂度评估

**Phase 3: Design Presentation** — 以 200-300 字段落呈现，覆盖架构、组件、数据流、错误处理、测试，每段后问"这看起来对吗？"

**Phase 4: Worktree Setup** — 设计批准后切换到 Git Worktree 技能

**Phase 5: Planning Handoff** — 询问"准备好创建实现计划了吗？"，切换到 Writing Plans 技能

核心原则："需要时可以回退——灵活性 > 刚性推进"

### 2.2 编写计划技能（Writing Plans）

**核心假设**：执行者是一个"热情但品味差、判断力差、没有项目上下文、厌恶测试的初级工程师"。

**任务粒度**：每步 2-5 分钟：
- "编写失败的测试" — 一个步骤
- "运行确认失败" — 一个步骤
- "实现最小代码使测试通过" — 一个步骤
- "运行测试确认通过" — 一个步骤
- "提交" — 一个步骤

**计划文档结构**：

```markdown
# [Feature Name] Implementation Plan

**Goal:** 一句话描述构建什么
**Architecture:** 2-3 句话描述方法
**Tech Stack:** 关键技术/库

---

## Task 1: [Component Name]

**Files:**
- Create: `exact/path/to/new/file`
- Modify: `path/to/file.py:123-145`
- Test: `exact/test/file/path`

**Step 1: Write the failing test**
[完整测试代码]

**Step 2: Run test to verify it fails**
[精确命令 + 预期输出]

**Step 3: Write minimal implementation**
[完整最小实现代码]

**Step 4: Run test to verify it passes**
[精确命令 + 预期: PASS]

**Step 5: Commit**
[精确 git add + commit 命令]
```

### 2.3 子 Agent 驱动开发

**核心原则**："每任务一个新子 Agent + 任务间代码审查 = 高质量、快速迭代"

7 步流程：加载计划 → 执行任务 → 审查工作 → 应用反馈 → 标记完成 → 最终审查 → 完成开发

**两阶段审查机制**：
- 第一阶段：规格合规性 — 实现是否符合计划要求？
- 第二阶段：代码质量 — 代码本身的质量如何？

### 2.4 TDD 技能

**铁律**："没有失败测试先行，就没有生产代码"

如果先写了代码再写测试，必须**完全删除**重新开始。不能保留作"参考"，不能"适配"已有代码。"删除就是删除"。

**RED-GREEN-REFACTOR 循环**：

| 阶段 | 动作 | 关键要求 |
|------|------|----------|
| RED | 编写失败测试 | 一个行为，清晰命名 |
| Verify RED | 观察失败 | 必须——永不跳过 |
| GREEN | 最小代码通过 | 不加功能，不重构 |
| Verify GREEN | 观察通过 | 必须——确认所有测试通过 |
| REFACTOR | 清理 | 只在 GREEN 后，不加行为 |

**合理化反驳表**（Superpowers 最独特的设计之一）：

| 借口 | 现实 |
|------|------|
| "太简单不需要测试" | 简单代码也会出错；测试只需 30 秒 |
| "我稍后写测试" | 后写的测试立即通过，证明不了什么 |
| "后写测试效果一样" | 后写测试回答"这做了什么？"，先写测试回答"这应该做什么？" |
| "已经手动测试了" | 临时的 ≠ 系统的；无记录，无法重跑 |
| "删除 X 小时的工作是浪费" | 沉没成本谬误；保留未验证代码是技术债 |
| "保留作参考，先写测试" | 你会适配它——那就是后写测试；删除就是删除 |

### 2.5 系统化调试技能

**铁律**："没有根因调查，就没有修复"

四阶段框架：
1. **根因调查** — 仔细阅读错误信息，一致复现，检查最近变更，追踪数据流
2. **模式分析** — 找到工作的例子，与参考对比，识别差异
3. **假设与测试** — 形成单一假设，最小化测试，验证后继续
4. **实现** — 创建失败测试用例，实现单一修复，验证修复

关键洞察："95% 的'没有根因'案例是不完整的调查"

**3 次失败规则**：如果 3+ 次修复失败，质疑架构。

## 三、Skill 文件设计模式

### 3.1 SKILL.md 标准结构

```yaml
---
name: Skill Name
description: 一句话描述技能做什么和何时使用
when_to_use: when [具体触发条件、症状、场景]
version: x.y.z
languages: all | specific-languages
---
```

正文结构（按顺序）：
1. **Overview** — 核心原则，1-2 句话
2. **When to Use** — 症状和用例列表；何时不使用
3. **Core Pattern** — 前后代码对比（技术/模式型）
4. **Quick Reference** — 表格或要点，便于扫描
5. **Implementation** — 简单模式内联代码；重度参考用路径引用
6. **Common Mistakes** — 什么会出错 + 修复方法
7. **Real-World Impact** — 可选，具体结果

### 3.2 技能类型分类

| 类型 | 描述 | 示例 |
|------|------|------|
| **Technique（技术）** | 有步骤的具体方法 | condition-based-waiting, root-cause-tracing |
| **Pattern（模式）** | 思考问题的方式 | flatten-with-flags, preserving-productive-tensions |
| **Reference（参考）** | API 文档、语法指南 | office-docs, pptxgenjs |
| **Discipline（纪律）** | 强制执行的规则/要求 | TDD, verification-before-completion |

### 3.3 目录结构模式

**自包含技能**：
```
defense-in-depth/
  SKILL.md    # 所有内容内联
```

**带可复用工具的技能**：
```
condition-based-waiting/
  SKILL.md    # 概述 + 模式
  example.ts  # 可适配的工作辅助代码
```

**带重度参考的技能**：
```
pptx/
  SKILL.md       # 概述 + 工作流
  pptxgenjs.md   # 600 行 API 参考
  ooxml.md       # 500 行 XML 结构
  scripts/       # 可执行工具
```

### 3.4 Claude 搜索优化（CSO）— 技能发现设计

这是 Superpowers 最精妙的设计之一——确保未来的 Agent 实例能**找到**你的技能。

**1. 丰富的 when_to_use**

Claude 读取 `when_to_use` 来决定加载哪个技能：

```yaml
# 差: when_to_use: For async testing（太抽象，不以"when"开头）
# 好: when_to_use: when tests have race conditions, timing dependencies, or pass/fail inconsistently
```

**2. 关键词覆盖** — 使用 Claude 会搜索的词汇：错误信息、症状、同义词、工具名

**3. 描述性命名** — 动词优先：`creating-skills` 而非 `skill-creation`

**4. Token 效率**

| 技能类型 | 目标字数 |
|----------|----------|
| 入门工作流 | <150 词 |
| 频繁加载技能 | <200 词总计 |
| 其他技能 | <500 词 |

**5. 内容重复** — 在 description、when_to_use、overview、章节标题中多次提及关键概念

**6. 交叉引用** — 使用路径格式，不用 `@` 前缀（避免强制加载消耗上下文）

## 四、TDD for Skills — 技能测试驱动开发

这是 Superpowers 最具创新性的设计模式：**编写技能就是将 TDD 应用于流程文档**。

### 4.1 TDD 映射

| TDD 概念 | 技能创建等价物 |
|----------|---------------|
| 测试用例 | 使用子 Agent 的压力场景 |
| 生产代码 | 技能文档（SKILL.md） |
| 测试失败（RED） | Agent 没有技能时违反规则（基线） |
| 测试通过（GREEN） | Agent 有技能时遵守规则 |
| 重构 | 关闭漏洞同时保持合规 |

### 4.2 铁律

**"没有失败测试先行，就没有技能"**

适用于新技能和现有技能的编辑。如果在测试前写了技能——删除它重新开始。没有例外。

### 4.3 RED 阶段：基线测试

运行**没有**技能的压力场景——观察 Agent 失败并记录确切失败。

**压力类型**：

| 压力 | 示例 |
|------|------|
| 时间 | 紧急情况、截止日期、部署窗口关闭 |
| 沉没成本 | 数小时的工作，删除是"浪费" |
| 权威 | 资深者说跳过，经理覆盖 |
| 经济 | 工作、晋升、公司存亡 |
| 疲劳 | 一天结束时，已经累了 |
| 社交 | 看起来教条，显得不灵活 |
| 务实 | "务实 vs 教条" |

最佳测试组合 3+ 种压力。

### 4.4 GREEN 阶段：编写最小技能

编写解决特定基线失败的技能。不要为假设情况添加额外内容。

### 4.5 REFACTOR 阶段：关闭漏洞

**抗合理化设计**（最独特的部分）：

1. **显式否定每条漏洞** — 不只陈述规则，禁止特定变通方法
2. **处理"精神 vs 字面"论证** — 添加基础原则："违反字面规则就是违反精神规则"
3. **构建合理化表** — 从基线测试中捕获每个借口
4. **创建红旗列表** — 让 Agent 自检何时在合理化
5. **更新 CSO** — 在 when_to_use 中添加即将违规的症状

**防弹技能的标志**：
1. Agent 在最大压力下选择正确选项
2. Agent 引用技能章节作为理由
3. Agent 承认诱惑但仍遵循规则
4. 元测试揭示"技能很清楚，我应该遵循它"

### 4.6 不同技能类型的测试方法

| 技能类型 | 测试方法 | 成功标准 |
|----------|----------|----------|
| 纪律执行型 | 学术问题 + 压力场景 + 多重压力组合 | Agent 在最大压力下遵循规则 |
| 技术方法型 | 应用场景 + 变体场景 + 缺失信息测试 | Agent 成功应用技术到新场景 |
| 模式型 | 识别场景 + 应用场景 + 反例 | Agent 正确识别何时/如何应用 |
| 参考型 | 检索场景 + 应用场景 + 间隙测试 | Agent 找到并正确应用参考信息 |

## 五、跨系统设计模式

### 5.1 Claude Code CLAUDE.md 系统

**本质**：CLAUDE.md 文件是**建议性上下文**，而非强制配置。

**文件作用域层级**：

| 作用域 | 位置 | 共享范围 |
|--------|------|----------|
| 托管策略 | `/etc/claude-code/CLAUDE.md` | 所有组织用户 |
| 用户指令 | `~/.claude/CLAUDE.md` | 仅自己（所有项目） |
| 项目指令 | `./CLAUDE.md` 或 `./.claude/CLAUDE.md` | 团队（通过源码控制） |
| 本地指令 | `./CLAUDE.local.md` | 仅自己（当前项目） |

**编写最佳实践**：
- 目标每文件 200 行以下
- 写足够具体可验证的指令（好："使用 2 空格缩进" / 坏："正确格式化代码"）
- 消除矛盾规则

**路径特定规则**（`.claude/rules/`）：
```yaml
---
paths:
  - "src/api/**/*.ts"
---
# API Development Rules
- All API endpoints must include input validation
```

### 5.2 Claude Code Skills 系统

**与 CLAUDE.md 的关键区别**："技能的主体只在被使用时加载，因此长参考材料在需要之前几乎不消耗任何成本。"

**SKILL.md 文件格式**：

```yaml
---
name: Display Name
description: 技能做什么和何时使用
when_to_use: 附加触发上下文
argument-hint: [issue-number]
arguments: [named positional args]
disable-model-invocation: true/false
user-invocable: true/false
allowed-tools: [tool list]
model: model-override
effort: low/medium/high/xhigh/max
context: fork  # 在隔离子 Agent 中运行
agent: general-purpose  # 子 Agent 类型
hooks: {}  # 生命周期钩子
paths: ["glob patterns"]  # 自动激活条件
---
```

**调用控制矩阵**：

| 配置 | 用户可调用 | Claude 可调用 | 上下文加载 |
|------|-----------|-------------|-----------|
| 默认 | 是 | 是 | 描述始终在上下文，完整内容调用时加载 |
| `disable-model-invocation: true` | 是 | 否 | 描述不在上下文，用户调用时加载 |
| `user-invocable: false` | 否 | 是 | 描述始终在上下文，调用时加载 |

### 5.3 Claude Code Hooks 系统

在 Claude Code 生命周期特定点自动执行的用户定义命令：

| 事件 | 时机 | 关键能力 |
|------|------|----------|
| SessionStart | 会话开始 | 添加上下文，设置环境变量 |
| PreToolUse | 工具执行前 | 允许/拒绝/修改输入 |
| PostToolUse | 工具成功后 | 添加反馈，替换输出 |
| Stop | Claude 完成响应 | 可阻止停止 |
| SubagentStart | 子 Agent 生成 | 注入额外上下文 |

### 5.4 OpenAI Codex AGENTS.md 系统

Codex CLI 使用 `AGENTS.md` 作为项目级指令文件。

**关键设计特点**：
- **极其具体**：不是"格式化代码"，而是"When using format! and you can inline variables into {}, always do that"
- **包含精确命令**：`just test -p codex-tui` 而非"运行测试"
- **明确禁止**：用"Never"和"Always"标记硬性规则
- **上下文感知**：区分不同场景

### 5.5 Claude Code on Steroids 扩展

GadaaLabs 的扩展项目从 14 个技能扩展到 24 个，增加了关键基础设施：

**Oracle 技能**（模型分层设计的典范）：
```
Phase 1: Task Classification（30 秒）→ 复杂度评分(1-10)
Phase 2: Skill Chain Selection → debug/feature/refactor/architecture/research-chain
Phase 3: Pattern Search（复杂度≥4 时必需）→ 搜索 ReasoningBank
Phase 4: Model Tier Assignment → 1-3:Haiku, 4-6:Sonnet, 7-9:Sonnet→Opus, 10:Opus
Phase 5: SPARC Gate（复杂度≥8 时必需）
```

**6 条工作流链**：
```
DEBUG: chronicle → hunter → forge → sentinel → oracle → chronicle(store)
FEATURE: oracle → chronicle → [domain] → architect → blueprint → horizon → vector + legion → phantom → sentinel → tribunal → oracle → chronicle(store)
ARCH: oracle → chronicle → architect → blueprint → tribunal → oracle → chronicle(store)
REFACTOR: oracle → forge → blueprint → horizon → sentinel → oracle → chronicle(store)
```

## 六、设计原则深度分析

### 6.1 特异性 vs 灵活性

**原则**：指令应该具体到可以验证，但灵活到可以适应。

| 维度 | 过于具体 | 平衡点 | 过于灵活 |
|------|----------|--------|----------|
| 指令 | "使用 2 空格缩进" | "使用 2 空格缩进" | "正确格式化代码" |
| 流程 | "必须运行 `npm test`" | "提交前运行 `npm test`" | "测试你的更改" |

Superpowers 的解决方案：
- **纪律型技能**：刚性规则，不允许变通
- **模式型技能**：灵活原则，适应上下文
- **技能本身告诉你它是哪种类型**

### 6.2 上下文效率设计

**核心矛盾**：更多指令 = 更好行为，但更多指令 = 更多 token 消耗。

| 策略 | 实现方式 | 适用场景 |
|------|----------|----------|
| 按需加载 | 技能只在被使用时加载主体 | 长参考材料 |
| 路径作用域 | 只在操作匹配文件时加载规则 | 项目特定约定 |
| 分层架构 | CLAUDE.md(全局) + Skills(按需) + Hooks(强制) | 不同强制级别 |
| 模型分层 | 简单任务用便宜模型，复杂任务用强模型 | 成本优化 |
| 压缩保留 | compaction 后重新注入关键指令 | 长会话 |

### 6.3 三层强制模型

```
Level 1: CLAUDE.md / Rules — 建议性上下文
  → 依赖编写质量决定遵循程度
  → 适合：编码风格、项目约定

Level 2: Skills — 结构化流程指导
  → 通过合理化反驳表和红旗列表增强遵循
  → 适合：TDD、调试流程、代码审查

Level 3: Hooks — 硬性强制
  → 通过 exit code 2 阻止操作
  → 适合：安全策略、必须运行的检查
```

### 6.4 边缘情况处理

1. **合理化反驳表** — 预先列出所有可能的借口和反驳
2. **红旗列表** — 让 Agent 自检何时在合理化
3. **基础原则声明** — "违反字面就是违反精神"切断整类论证
4. **3 次失败规则** — 调试时 3 次修复失败则质疑架构
5. **显式否定** — 不只说"做 X"，还说"不要以 Y 方式规避 X"

### 6.5 架构张力保留原则

**Preserving Productive Tensions**：某些张力携带有价值的信息，而非需要解决的问题。

张力是生产性的当：
- 两种方法服务于不同的合法优先级
- 更优选择取决于部署上下文
- 不同用户会合理地选择不同选项

保留模式：配置化、并行实现、文档化权衡。

## 七、实用技能编写指南

### 7.1 从零编写技能的完整流程

**Step 1: 确定是否需要技能**

创建技能当：
- 该技术对你来说不是直觉明显的
- 你会跨项目再次引用它
- 该模式广泛适用（非项目特定）
- 其他人会受益

不要创建当：
- 一次性解决方案
- 其他地方已有良好文档的标准实践
- 项目特定约定（那些放在 CLAUDE.md）

**Step 2: RED — 运行基线测试**

运行场景 WITHOUT 技能，记录 Agent 的确切行为和合理化借口（逐字记录）。

**Step 3: GREEN — 编写最小技能**

只解决特定基线失败，不为假设情况添加额外内容。

**Step 4: Verify GREEN — 用技能重新测试**

运行相同场景 WITH 技能。Agent 应该现在合规。

**Step 5: REFACTOR — 关闭漏洞**

识别新的合理化 → 添加显式反驳 → 构建合理化表 → 创建红旗列表 → 更新 when_to_use → 重新测试

**Step 6: 质量检查**

- [ ] 流程图仅在决策非显然时使用
- [ ] 快速参考表存在
- [ ] 常见错误章节存在
- [ ] 没有叙述性讲故事
- [ ] 字数在目标范围内

**Step 7: 部署**

提交到 git，考虑通过 PR 贡献回社区。

### 7.2 技能编写反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|----------|
| 叙述性示例 | "在 2025-10-03 的会话中，我们发现..." — 太具体 | 提取通用模式 |
| 多语言稀释 | 5 种语言的平庸示例 | 一个优秀示例即可 |
| 流程图中的代码 | 用流程图节点表示代码 — 无法复制 | 代码用 Markdown 代码块 |
| 通用标签 | helper1, step3 — 无语义 | 使用有意义的标签 |
| 未测试的技能 | "技能显然很清楚" | 始终测试 |
| 批量创建 | 不测试就连续创建多个技能 | 每个技能独立测试验证 |

### 7.3 不同类型技能的编写模板

**纪律执行型**（如 TDD、调试流程）：

```yaml
---
name: Skill Name
description: "[动词] [对象] — [核心约束]"
when_to_use: when [触发条件], before [动作], when tempted to [常见违规]
version: x.y.z
---

# Skill Name

## Overview
核心原则（1-2 句）。声明："违反字面规则就是违反精神规则。"

## The Iron Law
绝对规则陈述。

## Process
分阶段流程，每阶段有验证步骤。

## Common Rationalizations
| 借口 | 现实 |
|------|------|

## Red Flags — STOP
- 警告信号列表

## Verification Checklist
- [ ] 每个验证项
```

**技术方法型**（如 condition-based-waiting）：

```yaml
---
name: Skill Name
description: "[方法] for [问题域]"
when_to_use: when [具体症状/场景]
version: x.y.z
languages: [specific | all]
---

# Skill Name

## Overview
核心方法（1-2 句）。

## Core Pattern
Before/After 代码对比。

## Quick Reference
| 场景 | 方法 |
|------|------|

## Implementation
完整代码示例（一个优秀示例）。

## Common Mistakes
- 错误 → 修复
```

**参考型**（如 API 文档）：

```yaml
---
name: Skill Name
description: "Reference for [技术/工具]"
when_to_use: when working with [技术/工具], when looking up [特定信息]
version: x.y.z
---

# Skill Name

## Overview
工具/技术简介。

## Quick Reference
核心操作表格。

## Detailed Reference
@link-to-separate-file（如果超过 100 行）
```

### 7.4 技能命名指南

| 原则 | 好 | 差 |
|------|---|---|
| 动词优先 | `creating-skills` | `skill-creation` |
| 核心洞察命名 | `condition-based-waiting` | `async-test-helpers` |
| 动名词表示过程 | `testing-skills` | `skill-tests` |
| 描述你做什么 | `root-cause-tracing` | `debugging-techniques` |

### 7.5 代码示例编写原则

**"一个优秀示例胜过多个平庸示例"**

好示例：完整且可运行、良好注释解释**为什么**、来自真实场景、可直接适配

不要：用 5+ 种语言实现、创建填空模板、编写人为示例

## 八、好技能 vs 差技能

| 维度 | 好技能 | 差技能 |
|------|--------|--------|
| **特异性** | "使用 2 空格缩进" | "正确格式化代码" |
| **可验证性** | "运行 `npm test` 确认通过" | "确保代码工作" |
| **可发现性** | 丰富的 when_to_use + 关键词覆盖 | 模糊的描述 |
| **Token 效率** | <500 词，重度参考分离到外部文件 | 冗长叙述，所有内容内联 |
| **抗合理化** | 显式反驳表 + 红旗列表 | 只陈述规则 |
| **测试验证** | 经过子 Agent 压力测试 | "显然清楚" |
| **结构化** | Markdown 标题 + 表格 + 要点 | 大段散文 |
| **可组合性** | 通过路径引用其他技能 | 重复其他技能的内容 |

## 九、设计原则总结

1. **特异性优于通用性** — 指令应该具体到可以验证
2. **简洁性优于完整性** — 每 token 都有成本
3. **模块化作用域优于单体文件** — 按需加载，路径作用域
4. **结构化 Markdown 优于散文** — 标题、表格、要点
5. **测试驱动优于直觉驱动** — 没有失败测试就没有技能
6. **显式反驳优于隐含期望** — 列出合理化借口和反驳
7. **组合优于重复** — 交叉引用其他技能
8. **分层强制优于全有全无** — CLAUDE.md(建议) + Skills(指导) + Hooks(强制)
9. **上下文效率优于信息完备** — 主体按需加载，描述始终可用
10. **证据优于声明** — 验证先于声明成功

## 十、我的判断

### 最有价值的洞察

1. **TDD for Skills** 是整个体系中最具原创性的贡献。把"写技能"本身当作可以用 TDD 验证的工程活动，而不是"写文档"，这是一个范式转换。合理化反驳表和红旗列表不是装饰，而是让技能从"建议"变成"可执行约束"的关键机制。

2. **抗合理化设计**比规则本身更重要。Superpowers 的核心洞察是：Agent 违规不是因为不知道规则，而是因为会"合理化"绕过规则。所以技能设计的关键不是写更多规则，而是堵住每一条合理化路径。

3. **CSO（Claude 搜索优化）**揭示了 Skill 设计中一个容易被忽视的维度：技能不仅要写得好，还要**能被找到**。when_to_use 的关键词覆盖、描述性命名、内容重复，都是为了解决"技能存在但 Agent 不知道"的问题。

### 需要警惕的地方

1. **Superpowers 的 TDD 铁律可能过重**。对于个人项目或小团队，"没有失败测试就没有技能"的门槛可能导致技能库长期为空。更务实的做法是：对纪律型技能严格执行 TDD，对参考型和模式型技能降低门槛。

2. **合理化反驳表的有效性依赖于对 Agent 行为的准确预测**。如果 Agent 找到了表中没有的新借口，反驳表就失效了。这意味着技能需要持续迭代，而不是写一次就完。

3. **模型分层（Oracle/Vector）增加了系统复杂度**。在模型能力快速迭代的当下，硬编码的分层策略可能很快过时。更灵活的做法是把模型选择也做成可配置的。

### 对当前 Vault 的启发

1. Vault 中的笔记可以借鉴 Skill 的结构化设计：每篇笔记增加"何时使用"和"常见误区"章节
2. 笔记之间的关联可以借鉴 CSO 的思路：在 frontmatter 中增加更丰富的关键词，让 Agent 更容易发现相关笔记
3. "我的判断"章节可以借鉴合理化反驳表：不只说"我认为 X"，还说"有人可能认为 Y，但 Y 的问题在于 Z"

## 参考来源

- Superpowers 主插件：github.com/obra/superpowers
- Superpowers Skills 库：github.com/obra/superpowers-skills
- Superpowers Lab：github.com/obra/superpowers-lab
- Writing Skills SKILL.md：obra/superpowers-skills/skills/meta/writing-skills/SKILL.md
- Testing Skills SKILL.md：obra/superpowers-skills/skills/meta/testing-skills-with-subagents/SKILL.md
- TDD SKILL.md：obra/superpowers-skills/skills/testing/test-driven-development/SKILL.md
- Systematic Debugging：obra/superpowers-skills/skills/debugging/systematic-debugging/SKILL.md
- Brainstorming：obra/superpowers-skills/skills/collaboration/brainstorming/SKILL.md
- Writing Plans：obra/superpowers-skills/skills/collaboration/writing-plans/SKILL.md
- Subagent-Driven Dev：obra/superpowers-skills/skills/collaboration/subagent-driven-development/SKILL.md
- Preserving Tensions：obra/superpowers-skills/skills/architecture/preserving-productive-tensions/SKILL.md
- Claude Code Memory：code.claude.com/docs/en/memory
- Claude Code Skills：code.claude.com/docs/en/skills
- Claude Code Hooks：code.claude.com/docs/en/hooks
- Codex AGENTS.md：github.com/openai/codex/main/AGENTS.md
- Claude Code on Steroids：github.com/GadaaLabs/claude-code-on-steroids

[[doc-notes/mocs/AI Coding MOC|AI Coding MOC]]
