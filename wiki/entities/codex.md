---
title: Codex
type: entity
tags: [coding-agent, agent-skill, multi-agent, guardrails]
entities: [codex, claude-code]
---

# Codex

## 它是什么

OpenAI 的终端 Coding Agent（Codex CLI，另有 App）。项目级指令写在 `AGENTS.md`，本地配置放在 `.codex/`，强调本地工作区协作。和 Claude Code 相比，它的 Hook 体系在机制上更完整，Skill 发现目录有明确的官方边界，子 Agent 可以跨模型调度；短板在生态：围绕它的原生框架和实战经验积累明显少于 Claude Code。

## 核心机制

### 1. Skill 发现目录

官方承诺会扫描的位置有四处，并且支持 symlink：

| 级别 | 位置 |
|---|---|
| 仓库级 | `.agents/skills` |
| 用户级 | `$HOME/.agents/skills` |
| 管理员级 | `/etc/codex/skills` |
| 系统级 | 随 Codex 打包的 system skills |

`~/.codex/skills` 不在官方列出的用户可写目录里。某些环境里它也能用，应理解为实现细节或内置目录，而不是稳定接口。

### 2. Hook 体系

Codex 有 10 个 Hook 事件（Claude Code 是 8 个）：

| 事件 | 时机 | Claude Code 有没有 |
|---|---|---|
| `SessionStart` | 会话开始 | 有 |
| `UserPromptSubmit` | 用户提交 prompt | Codex 独有 |
| `PreToolUse` | 工具调用前 | 有 |
| `PermissionRequest` | 权限请求决策 | Codex 独有 |
| `PostToolUse` | 工具调用后 | 有 |
| `PreCompact` / `PostCompact` | 上下文压缩前后 | 有 |
| `SubagentStart` / `SubagentStop` | 子代理启动 / 停止 | Codex 独有 |
| `Stop` | Agent 停止 | 有 |

架构特点：Rust 原生实现；用结构化的 Request → Outcome，而不是退出码；Plugin 声明式注册；用户级 / 项目级 / 会话级三层配置；支持只允许受管 Hook 的模式（`allow_managed_hooks_only`）。代价是开发门槛比 Claude Code 的 shell 脚本高。

「Codex 没有 Hook」是一个常见的错误说法。更准确的是：很多跨工具框架还没有适配 Codex 的 Hook。会话间记忆传递、压缩前保存状态、持续学习、密钥检测（可以放在独有的 `UserPromptSubmit` 上）这些模式，理论上都能迁移过来，需要的是适配层而不是重新设计。

### 3. AGENTS.md 的写法

- 极其具体：不是「格式化代码」，而是写到某个具体语法场景该怎么做；
- 给精确命令：写 `just test -p <crate>` 这样的命令，而不是「运行测试」；
- 硬规则用 Never / Always 标出来；
- 按场景区分，而不是一刀切。

### 4. 循环与自主模式

Codex 也有 `/goal`（Ralph Loop），配合 `full-auto` 审批模式，显式无状态、自动压缩。和 Claude Code 的关键差异是：**由模型自己判断何时「完成」**，而 Claude Code 默认让独立评估器介入。

这背后是 OpenAI 的 harness 路线：「多层级联控制」。它把核心问题看成「模型会漂移」，在不同时间尺度上串起多层「观测 → 比较 → 修正」的反馈回路，传感器以确定性信号为主（测试通过与否、linter 报错、CI 和运行态），控制器是编码在仓库里的规则和标准；主观质量靠质量文档、人工评分和长期趋势跟踪来补。与之对照的是 Claude Code 背后「生成与评估对抗分离」的路线。两者并不互斥：确定性控制器管可形式化的约束，独立评估 Agent 管需要语义判断的质量。

### 5. 混合模型子 Agent

思路是：主 Agent 用官方订阅里的高能力模型做理解、拆分和汇总，执行层按任务类型交给其他模型或其他 CLI。

**两种混法**

- **原生混动**：仍由 `spawn_agent` 创建子任务，保留 AgentPath、mailbox、`wait_agent`、resume 和统一状态树，父线程可以等待、追问、汇总、恢复。
- **进程混动**：主 Codex 直接启动 Claude Code、Cursor、Codex CLI 等外部进程当执行器，从 stdout 或事件流回收结果。维护成本低，但没有统一状态树，超时和汇总要父线程自己处理。

**五条实现路径**

| 路径 | 保留原生任务树 | 维护成本 | 什么时候用 |
|---|---|---|---|
| 协议网关 + V2 跨 Provider | 是 | 中 | 首选；前提是父任务的发送路径经过网关的 optimizer（CLIProxyAPI v7.2.115+） |
| 主模型切回 V1 + 跨 Provider | 是 | 中 | 目标模型不在 V2 目录，或保证不了消息都经过 optimizer |
| 标准 External CLI | 否 | 低 | 只想低维护地复用多份官方订阅 |
| Fork Codex CLI | 是 | 高 | 要最高控制力，并愿意随官方版本持续重放 patch |
| 官方模型内部降档 | 是 | 低至中 | 不接第三方，只在官方模型之间降档（如 GPT-5.6 Sol → Terra） |

**真正的难点：任务正文能不能明文送到**

V2 collaboration 工具（`spawn_agent`、`send_message`、`followup_task`）的消息 schema 会被加密。第三方模型即使路由正确，也可能只拿到一串密文。密文一旦生成，接收端无法还原，所以只能在**发送之前**处理：父任务的三条发送路径都要经过 optimizer。它不是「解密器」，作用是阻止任务正文在交给第三方之前被加密。

切回 V1 也有代价：`model_catalog_json` 是权威的静态目录，不是增量覆盖，会冻结新模型、上下文窗口、工具模式等元数据；升级 Codex 后要重新导出最新目录再改。

**V2 与 V1 两种形态**

| 形态 | 特点 | 什么时候用 | 代价 |
|---|---|---|---|
| V2 + optimizer | 保留主模型原生 V2 的任务拆分、子任务契约、状态树和后续追踪；三条消息路径（spawn / send / followup）都经过 CLIProxyAPI v7.2.115+ 的 optimizer 后，不必默认退回 V1 | 首选 | 网关进入完整信任边界 |
| 主模型切回 V1 | 子任务走普通 UserInput，更容易控制 | 目标模型不在 V2 目录，或保证不了父子任务都经过同一套 optimizer；也是 V1 档位模型当子 Agent 的前提 | 需要改静态模型目录（见下），升级后要重做 |

开启 optimizer 的网关配置：

```yaml
codex:
  optimize-multi-agent-v2: true
```

切回 V1 的做法是先导出当前模型目录，再把主模型的 `multi_agent_version` 改成 `v1`（`codex debug models` 导出 JSON，用 jq 改对应 slug 的字段后作为 `model_catalog_json` 使用）。

**官方模型档位（GPT-5.6 Sol / Terra / Luna）**

| 组合 | 能否派发 | 做法 |
|---|---|---|
| Sol（V2）→ Terra | 可以 | 同为 V2，设默认子模型或显式 override |
| Sol（V2）→ Luna | 不可以 | Luna 标记为 V1，V2 后端会拒绝 |
| Sol（V1）→ Luna | 可以 | 先把 Sol 的目录改成 V1，再用 Luna 做默认子模型或专用角色 |

只想把低风险执行任务降档时，Sol V2 → Terra 最省事：

```toml
[agents]
enabled = true
default_subagent_model = "gpt-5.6-terra"
default_subagent_reasoning_effort = "low"
```

想用 Luna 的成本优势，就要接受 Sol 切回 V1 带来的任务拆分变化和目录冻结成本。

执行层接入第三方模型有三种方式：Provider 原生提供 Responses 接口时直接用；否则用协议网关（如 CC Switch、CLIProxyAPI、Sub2API）把 Chat Completions 或 Anthropic Messages 转成 Responses（Codex 侧始终只发 Responses；某家模型支持 Responses 不代表同厂所有模型都支持，切换前要核对兼容表）；或者走 External CLI（直接调度标准 Claude Code、Cursor、Codex CLI 等，或把第三方模型封装成 Claude Code wrapper）。

## 怎么用

- **装自定义 Skill**：团队共享时统一装在 `$HOME/.agents/skills`。分享安装方式时，明确区分「官方承诺的目录」和「当前环境碰巧能用的路径」，免得升级后踩坑。
- **写 AGENTS.md**：按上面四条写，能交给 Hook 做确定性检查的就不写成「请记住」。
- **混合子 Agent 的验收，至少查四层**：
  1. 版本：父线程记录里的 `multi_agent_version` 符合预期；
  2. 派发：`spawn_agent` 的 message 参数是明文；
  3. 接收：子线程记录里出现完整、准确的任务文本，而不是空内容或密文；
  4. 产出：子线程返回约定的标记，或产生可复核的文件、命令和测试结果。
  只看 `model_provider` 和 `model` 字段，只能证明路由成功。
- **任务契约写全**：目标、范围、权限、输出、停止条件都要写；V2 自定义角色优先用 `fork_turns = "none"` 或只带有限历史，减少上下文污染。
- **安全边界**：协议网关会看到 API Key、Prompt、工具参数和响应，进入完整信任边界。只绑定本机回环地址、用独立的访问密钥；远程部署要加 TLS、入口鉴权和日志脱敏。
- **不要一上来 Fork Codex CLI**：那是最高控制力的路径，不是省事的路径。也不要以为把 `default_subagent_model` 改成更便宜的模型就完成了降本：主模型在 V2 时，派给仍标记为 V1 的模型会被后端拒绝。
- **学习顺序**：先在一个工具上把工作流做扎实，再迁移到 Codex。skill 文档、规则思想和验证流程属于共享层；hook 事件、命令格式和工具权限属于适配层。
- 模型目录、网关行为、CLI 版本都变得很快，落地前重新做一遍四层验收。
