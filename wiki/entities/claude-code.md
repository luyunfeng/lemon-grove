---
title: Claude Code
type: entity
tags: [coding-agent, harness, guardrails, agent-loop, multi-agent]
entities: [claude-code, codex, claude-models]
---

# Claude Code

## 它是什么

Anthropic 的终端 Coding Agent。它像人类工程师一样遍历文件系统、读文件、grep、顺着引用找代码，不需要预先建索引，所以不存在索引过时的问题（Agentic Search 而非 RAG）。代价是它需要足够的起始上下文，才知道「往哪看」。

理解它的关键判断：**决定表现的往往不是模型，而是围绕模型搭的 harness**；而且 harness 要跟着模型一起迭代。

## 核心机制

### 1. harness 的扩展点和搭建顺序

五个扩展点按推荐的搭建顺序排列：CLAUDE.md → Hooks → Skills → Plugins → MCP，外加 LSP 和 Subagents 两项能力。顺序有讲究：先把最便宜、影响每次会话的层打好，再往外扩。

| 组件 | 何时加载 | 最适合 | 常见混淆 |
|---|---|---|---|
| CLAUDE.md | 每次会话 | 项目特定约定、代码库知识 | 把可复用的专业知识也塞进去 |
| Hooks | 事件触发 | 自动化一致行为、捕获会话中学到的东西 | 用 prompt 去做本该自动运行的事 |
| Skills | 按需，相关时才加载 | 跨会话、跨项目复用的专业知识 | 全部塞进 CLAUDE.md |
| Plugins | 配置后始终可用 | 把 skills + hooks + MCP 打包，在组织内分发 | 让好的设置停留在「口口相传」 |
| LSP | 配置后始终可用 | 符号级导航、自动发现错误 | 以为它是自动开启的 |
| MCP | 配置后始终可用 | 访问内部工具、数据和 API | 基础没打好就先建 MCP |
| Subagents | 调用时 | 分离探索与编辑、并行工作 | 在同一会话里又探索又编辑 |

- **CLAUDE.md 有作用域层级**：托管策略（全组织）→ 用户级 `~/.claude/CLAUDE.md` → 项目级 `./CLAUDE.md` → 本地 `./CLAUDE.local.md`。它是**建议性上下文**，不是强制配置；每个文件建议控制在 200 行以内，指令要具体到可验证（「用 2 空格缩进」，而不是「正确格式化代码」）。`.claude/rules/` 下的规则可以用 `paths` 限定只对某些文件生效。
- **Hook 不只是拦错事**：Stop hook 可以趁上下文新鲜，反思本次会话并提出 CLAUDE.md 的更新建议；Start hook 可以按团队动态加载上下文；lint、format 这类确定性规则交给 hook，比让模型「记住」可靠。PreToolUse hook 以退出码 2 直接阻断操作。
- **Skill 靠渐进式披露**：默认只有描述常驻上下文，正文在调用时才加载，所以长的查阅材料在用到之前几乎不花成本。frontmatter 可以控制调用方（`disable-model-invocation`、`user-invocable`）、限定工具、指定模型和 effort、用 `context: fork` 放进隔离子 Agent 运行、用 `paths` 按路径自动激活。
- **加载路径**：个人级 `~/.claude/skills/`、项目级 `.claude/skills/`、插件级（带命名空间，如 `/ecc:plan`）。

### 2. 并行与规模化：三层机制

| 机制 | 编排者 | 中间结果放哪 | 规模与限制 |
|---|---|---|---|
| Subagents | Claude 逐轮决定 | 回到主对话 | 每轮几个任务；内置 Explore（Haiku，只读）、Plan（只读）、General-purpose（全部工具） |
| Agent Teams（实验性） | Team Lead + Teammates，共享任务列表和邮箱 | 各自上下文 | 建议 3-5 个 teammates、每人 5-6 个任务；一次只能一个 team，不能嵌套，token 成本线性增长 |
| Dynamic Workflows（研究预览，v2.1.154+） | Claude 写的 JavaScript 脚本 | 脚本变量，不占主上下文 | 最多 16 个并发代理，单次最多 1,000 个代理；运行中不接受用户输入；只能在同一会话内恢复 |

补充细节：

- **子代理**：上下文隔离（搜索结果、日志不进主对话）、可配工具白名单、可路由到更便宜的模型；约 95% 容量时自动压缩；`memory` 字段提供 user / project / local 三种作用域的持久目录。**Forked Subagents**（实验性）继承完整对话并共享 prompt cache，比新建子代理便宜。
- **Dynamic Workflows**：prompt 里出现 "workflow" 就会自动写编排脚本；脚本本身没有文件系统和 Shell 权限，只做协调，读写由代理完成；按 `s` 可把脚本存到 `.claude/workflows/`（项目级）或 `~/.claude/workflows/`（个人级），之后当 `/<命令名>` 复用。内置的 `/deep-research` 就是这种形态。
- **Effort 档位**：Low / Default（High）/ Extra（xhigh）/ Max；`/effort ultracode` 把 xhigh 推理和自动工作流编排结合，由 Claude 判断何时启动工作流。

### 3. 循环工具链：/goal、/loop、Auto Mode

- **`/goal`（v2.1.139 引入）**：人写一个可验证的完成条件，Claude 反复「做 → 验 → 修」。每个 turn 结束后，把条件和完整对话交给独立的评估器模型（默认 Haiku），返回 yes/no 和理由；no 时理由带入下一轮，yes 时清除目标并停止。**评估器不调用工具**，只能判断对话里已经出现的内容，所以条件要写成「让 Claude 自己跑命令并把结果打印出来」的形式。`/goal` 查看状态，`/goal clear` 清除；非交互模式可以带 token 预算，如 `claude -p "/goal --tokens 250K ..."`。
- **`/loop`**：会话级定时调度器，如 `/loop 5m check the GitHub Actions workflow`，也可以不写间隔让 Claude 自选，或循环执行其他斜杠命令。只在 Claude Code 运行且空闲时触发，错过的不补跑；重复任务 7 天后过期；每会话最多 50 个任务；新对话会清除任务，`--resume` 可恢复未过期的。
- **组合**：`/goal` 定义「什么算完成」，`/loop` 负责持续推进或监控，例如 `/goal All GitHub Actions workflows pass` 配合 `/loop every 3m until: CI passes`。
- **Auto Mode**：用一个分类器（基于 Sonnet 4.6）对每个工具调用做风险评估，安全的自动放行、有风险的阻止，是无人值守循环的前提。开启方式：Shift+Tab 切换、环境变量 `CLAUDE_CODE_ENABLE_AUTO_MODE=1`、或 `--permission-mode auto`。
- `/plan` 是另一种控制方式：先定步骤、确认后按序执行，适合需求明确、需要人把控每一步的任务。

### 4. 背后的 harness 路线：生成与评估分离

Anthropic 走的是「生成与评估对抗分离」这条 harness 路线：它认为模型不只会漂移，还会对自己的输出过度自信、掩盖偏差，所以把规划、生成、评估拆成独立的推理过程（Planner-Generator-Evaluator），各自有独立上下文和预先给定的验收标准。评估者不只回 pass/fail，而是给出「哪里不满足、差在哪、怎么改」的结构化反馈，注入生成者的下一轮。`/goal` 就是这条路线的产品化简化版：一个 Worker 加一个轻量 Evaluator（Haiku）。同一路线的另一条原则是：harness 的每个组件都编码了一个关于模型局限的假设，模型进步后要回头删减——这正是下文「配置要定期审查」的依据。

## 怎么用

**大型代码库：让上下文可导航**

- CLAUDE.md 精简、分层：根文件只放指针和关键陷阱，子目录文件写本地约定。Claude 会自动向上遍历并加载沿途所有 CLAUDE.md，所以可以直接**在子目录启动**，范围收窄，根级上下文也不丢。
- 按子目录限定测试和 lint 命令，避免改一个服务就跑全量套件（既超时又浪费上下文）。编译型 monorepo 跨目录依赖深，这条更难做到。
- 用 `.ignore` 和提交到仓库的 `.claude/settings.json` 里的 `permissions.deny` 排除生成文件、构建产物和第三方代码。
- 目录结构不够自解释时，在根目录放一个轻量的代码库地图（顶层文件夹 + 一行描述），下一层细节交给子目录的 CLAUDE.md。
- 多语言大型代码库优先接 LSP：grep 常见函数名可能返回数千条匹配，LSP 只返回同一符号的引用，过滤发生在读取之前。
- 边界：几十万个文件夹、数百万文件，或非 git 版本控制的遗留系统，分层 CLAUDE.md 也会失效。

**一次标准的无人值守开发**

1. 进入 Auto Mode；
2. 用 `/goal` 写清完成条件，例如 `fix the race condition in conn_pool.go, run go test -race ./... with 0 failures`；
3. 需要监控时加 `/loop`；
4. 复杂任务再接 Skills 和 Subagents（只读子代理先摸清子系统，主 Agent 基于完整信息再改）；
5. CI 场景用 headless 模式（`claude -p`，可加 `--output-format json`）。

同时设好护栏：迭代上限、token 预算、N 轮无进展即停、错误率熔断。

**配置要定期审查**

为旧模型写的约束会限制新模型。例如「每次重构只改一个文件」对跨文件协调能力弱的模型有用，对能协调跨文件编辑的新模型就是枷锁；拦截写入以强制 `p4 edit` 的 hook，在原生支持 Perforce 后就冗余了。建议每 3-6 个月做一次有意义的审查，重大模型更新后表现停滞时也要审查。

**组织上要有 owner**

推广最快的部署都是先有一两个人或一个小团队把 plugins、MCP 准备好，开发者第一次用就在工作流里。新兴角色叫 Agent Manager；最小可行版本是一个 DRI，决定配置、权限策略、plugin 市场和 CLAUDE.md 规范。自下而上的采用有热情，但没人收口就会碎片化。受监管行业还要尽早回答：谁决定哪些 skills / plugins 可用、怎么避免重复造轮子、AI 生成的代码是否走同样的审查。

**不要迷信并行**：Dynamic Workflows 仍是研究预览，大规模并行不等于大规模有效，协调质量、冲突解决和成本都要自己验证；日常多数时候 2-3 个并行实例就够。运行大工作流前先看 `/model`，把不需要最强模型的阶段路由到小模型。
