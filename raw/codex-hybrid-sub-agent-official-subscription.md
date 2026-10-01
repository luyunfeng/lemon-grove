# Codex 混动 Sub Agent：用官方订阅调度其他模型

AI CODING STUDY NOTE / 2026-08-03

# Codex 混动 Sub Agent：用官方订阅调度其他模型

这里讨论的是：主 Agent 继续使用 Codex 官方订阅里的高能力模型做理解、拆分和汇总，执行层按任务类型交给其他模型或其他官方 CLI。真正的难点不是“能不能换模型”，而是任务正文能否明文跨 Provider 送达、子线程是否还在 Codex 原生任务树里，以及这条兼容链路由谁承担维护。


CORE VIEWPOINT

原文的主线可以压缩成一句话：**如果你想保留 Codex V2 原生任务树并跨 Provider 调度，优先使用 CLIProxyAPI v7.2.115+ 的 Multi-Agent V2 optimizer；如果模型不在 V2 目录或无法保证消息路径都经过 optimizer，再把 GPT-5.6 Sol 切回 V1；如果只想低维护地复用官方订阅，External CLI 路径最省心。**

## 先理解“混动”的两层含义

### 原生混动

仍由 `spawn_agent` 创建子任务，保留 AgentPath、mailbox、`wait_agent`、resume 和统一状态树。父线程能像管理普通 Codex Sub Agent 一样等待、追问、汇总和恢复。

适合：希望继续使用 Codex 原生任务树、子任务生命周期和状态管理的场景。

### 进程混动

主 Codex 直接启动 Claude Code、Grok、Cursor、Codex CLI 等外部进程，把它们当成独立执行器，再从 stdout 或事件流回收结果。

适合：想用多份官方订阅、降低协议兼容成本、接受父线程自己处理超时和汇总的场景。

## 五条实现路径怎么选

路径 | 保留原生任务树 | 自由度 | 维护成本 | 适用判断  
---|---|---|---|---  
**CLIProxyAPI + V2 跨 Provider** | 完整保留 | 高 | 中 | 首选路径。前提是父任务发送路径经过 v7.2.115+ optimizer。  
**GPT-5.6 Sol + V1 跨 Provider** | 完整保留 | 高 | 中 | 目标模型不在 V2 目录，或 V2 optimizer 链路不可控时使用。  
**标准 External CLI** | 不保留 | 由各 CLI 自己负责 | 低 | 想低维护复用 Claude、Grok、Cursor、Codex 等官方订阅。  
**Fork Codex CLI** | 完整保留 | 最高 | 高 | 需要最高控制力，且愿意随官方版本持续重放 patch。  
**GPT-5.6 官方弱混动** | 完整保留 | Sol / Terra / Luna | 低至中 | 只想在 OpenAI 官方模型内部降档，不接第三方 Provider。  
  
## 原文最关键的技术问题：V2 消息加密

### 问题在哪里

Codex V2 collaboration tool 的 `spawn_agent`、`send_message`、`followup_task` 会给 message schema 加 `.with_encrypted()`。第三方模型即使路由正确，也可能拿到 `gAAAA...` 开头的密文，而不是任务正文。

### 为什么接收端代理救不了

密文一旦生成，接收端无法还原任务正文。能动手的位置只能在发送之前，所以父任务的发送路径必须经过 optimizer。只在子 Agent 或接收端套代理，不解决问题。

01

**父 Agent 决定派发**

主线程仍由 Codex 高能力模型负责理解、拆分和收口。

02

**工具 schema 生成**

V2 collaboration message 默认可能带 encrypted 字段。

03

**CLIProxyAPI optimizer**

v7.2.115+ 覆盖 spawn、send、followup 三条路径。

04

**跨 Provider 发送**

第三方模型收到的是明文任务，而不是密文占位。

05

**原生任务树保留**

父线程继续 wait、追问、汇总和管理子任务状态。
    
    
    codex:
      optimize-multi-agent-v2: true

**我的理解：** CLIProxyAPI 这里不是“解密器”，而是“阻止任务正文被加密后再交给第三方模型”。这决定了验收标准不能只看模型是否路由成功，还必须检查子线程 rollout 里是否真的出现完整任务文本。 

## V2 与 V1 的取舍

优先 V2

### V2 + optimizer

保留 GPT-5.6 Sol 原生 V2 的任务拆分、子任务契约、状态树和后续追踪能力。原文认为，只要 v7.2.115+ 的三条消息路径都覆盖，V2 不再需要默认退回 V1。

**风险：** CLIProxyAPI 进入完整信任边界，会看到 API Key、Prompt、工具参数和响应。建议绑定 `127.0.0.1`，独立访问密钥，远程部署时加 TLS、入口鉴权和日志脱敏。

保留后路

### Sol 切回 V1

当目标模型不在 V2 目录，或不能保证父任务和子任务都经过同一套 optimizer，V1 的普通 UserInput 反而更容易控制。它也是 Sol 调度 Luna 的前提。

**代价：**`model_catalog_json` 是权威静态目录，不是增量 overlay，会冻结新模型、context window、工具模式和 `comp_hash` 等元数据。升级 Codex 后要重新 dump 最新目录再修改。
    
    
    codex debug models > ~/.codex/models-current.json
    
    jq '
      (.models[]
        | select(.slug == "gpt-5.6-sol")
        | .multi_agent_version) = "v1"
    ' ~/.codex/models-current.json > ~/.codex/models-v1.json

## 执行层的三种桥接方式

### 原生 Responses

Provider 直接提供 `/responses` 时优先使用。例如原文提到 DeepSeek Flash 可以直接配置为 Responses transport。

注意：不要推断所有 DeepSeek 模型都支持 Responses，切换模型前要重新核对官方兼容表。

### 协议桥接

GLM、Kimi、DeepSeek Pro 等可通过 CC Switch、CLIProxyAPI、Sub2API 等把 Chat Completions 或 Anthropic Messages 转成 Responses。

核心契约：Codex 侧始终发送 Responses，网关负责上下游协议转换。

### External CLI

直接调度标准 Claude Code、Grok、Cursor、Codex CLI，或把 DeepSeek、GLM、Kimi 封装成 Claude Code wrapper。

优点是解耦；代价是没有 AgentPath、mailbox、wait_agent、resume 和统一状态树。

## 官方弱混动：Sol / Terra / Luna

组合 | 当前状态 | 做法  
---|---|---  
**GPT-5.6 Sol V2 - > GPT-5.6 Terra** | 可以 | 同为 V2，可设置默认子模型或显式 override。  
**GPT-5.6 Sol V2 - > GPT-5.6 Luna** | 仍不可以 | Luna 仍标记为 V1，V2 backend 会拒绝。  
**GPT-5.6 Sol V1 - > GPT-5.6 Luna** | 可以 | 先把 Sol catalog 改为 V1，再用 Luna 默认子模型或专用角色。  
      
    
    [agents]
    enabled = true
    default_subagent_model = "gpt-5.6-terra"
    default_subagent_reasoning_effort = "low"

**我的理解：** 如果只是想把低风险执行任务降档，Sol V2 -> Terra 是当前最省事的路线；如果是为了利用 Luna 降价后的成本优势，就要接受 Sol 切回 V1 带来的任务拆分和目录冻结成本。 

## 不要只验证“路由到了哪个模型”

原文强调，一次可靠的混动测试至少要覆盖四层。只看 `model_provider` 和 `model`，只能证明路由成功，不能证明任务正文真的被送达。

### 四层验收

  1. **版本：** 父线程 rollout 的 `multi_agent_version` 符合预期。
  2. **派发：**`spawn_agent.arguments.message` 是明文，或响应包含官方明文标记。
  3. **接收：** 子线程 rollout 中存在完整、准确的任务文本，而不是空 Payload 或密文占位。
  4. **产出：** 子线程返回指定 marker，或产生可复核的文件、命令和测试结果。

### 任务契约

无论走原生 Sub Agent 还是 External CLI，都要把目标、范围、权限、输出、停止条件写完整。尤其是 V2 自定义角色，优先使用 `fork_turns = "none"` 或有限历史，减少上下文污染和路由歧义。
    
    
    jq -r '
      select(.type == "turn_context") |
      [.payload.model,
       .payload.multi_agent_version,
       .payload.effort] | @tsv
    ' rollout.jsonl

## 我的落地判断框架

### 推荐路径

如果目标是“Codex 仍做主控，同时子任务可以跨 Provider”，先试 CLIProxyAPI v7.2.115+ 的 V2 optimizer。它最符合原生任务树、并行调度、后续追问和汇总的使用习惯。

如果团队还没有稳定网关或不想扩大信任边界，就先用 External CLI，把其他官方订阅封装成清晰的命名执行器。

### 不建议一上来做的事

不要为了跨 Provider 直接 Fork Codex CLI，除非你已经接受持续跟官方版本、重放 patch、回归 schema 和 App 加载路径的成本。Fork 是最高控制力路径，不是默认省事路径。

也不要只改 `default_subagent_model` 指向 Luna 后就认为成本优化完成；当前 Sol V2 -> Luna 会被 backend 拒绝。

## 关键资料索引

  * [CLIProxyAPI PR #4748：补齐 send_message / followup_task 的 V2 optimizer 处理](https://github.com/router-for-me/CLIProxyAPI/pull/4748)
  * [CLIProxyAPI v7.2.115 发布说明](https://github.com/router-for-me/CLIProxyAPI/releases/tag/v7.2.115)
  * [OpenAI Codex Issue #34833：跨 Provider Sub Agent 消息兼容问题](https://github.com/openai/codex/issues/34833)
  * [OpenAI Codex PR #35845：Support plaintext collaboration tool messages](https://github.com/openai/codex/pull/35845)
  * [OpenAI Codex Issue #31814：GPT-5.6 Sol 子 Agent 强制继承父模型](https://github.com/openai/codex/issues/31814)
  * [OpenAI Codex Issue #34301：Sol / Terra V2 无法派 GPT-5.6 Luna](https://github.com/openai/codex/issues/34301)
  * [patrick-fu/awesome-skills：External Agent 调度与实时监控](https://github.com/patrick-fu/awesome-skills)

记录日期：2026-08-03

笔记路径：doc-notes/ai-coding/2026-08/notes/codex-hybrid-sub-agent-official-subscription.html

说明：本笔记区分技术结论与个人理解；涉及模型目录、Codex App/CLI、CLIProxyAPI 行为的内容可能随版本变化，落地前应重新做四层验收。
