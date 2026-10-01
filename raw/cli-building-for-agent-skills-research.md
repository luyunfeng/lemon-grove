# CLI 建设调研：如何为 Agent/Skill 打造 CLI 接口

> [!abstract]
> 调研业界 CLI 建设模式，重点关注：现有系统如何打造 CLI 给 AI Agent/Skill 使用，哪种暴露形式最有效，以及"输出一大段文本描述用法"这种方式的优劣和替代方案。

---

## 一、业界主流 CLI 架构模式

### 1.1 层级子命令模式（Subcommand Pattern）

几乎所有主流工具的标准范式：

```
tool resource verb [flags] [args]
```

| 工具 | 示例 | 框架 |
|------|------|------|
| AWS CLI | `aws ec2 describe-instances` | Python (botocore) |
| GitHub CLI | `gh pr create --title "fix"` | Go (Cobra) |
| kubectl | `kubectl get pods -o json` | Go (Cobra) |
| Terraform | `terraform plan -out=tfplan` | Go (Cobra) |
| Vercel CLI | `vercel deploy --prod` | Node.js |

设计要点：
- **名词 + 动词**：资源在前，操作在后
- **全局一致 flag**：`--output`、`--format`、`--verbose` 跨子命令统一
- **可组合**：每个命令做一件事，管道串联

### 1.2 插件式架构（Plugin Architecture）

以 Terraform 为代表：
- 核心 CLI 只负责编排（HCL 解析、状态管理、依赖图）
- Provider 是独立 gRPC 二进制，按需下载
- 第三方可扩展，无需修改核心

kubectl 也支持：任何 `kubectl-xxx` 命名的可执行文件自动成为 `kubectl xxx` 子命令。

### 1.3 常用框架对比

| 语言 | 框架 | 特点 | 代表项目 |
|------|------|------|----------|
| Go | Cobra | 层级子命令、自动补全、help 生成 | kubectl, docker, gh, hugo |
| Python | Click | 装饰器风格、类型安全 | pip, black |
| Node.js | Commander.js | 轻量、500M 周下载 | 大量 npm CLI |
| Node.js | Oclif | Salesforce 出品、插件体系、脚手架 | Salesforce CLI, Heroku CLI |
| Rust | Clap | derive 宏、强类型、编译期校验 | ripgrep, fd |

---

## 二、Agent-Friendly CLI：新的设计范式

### 2.1 核心矛盾

传统 CLI 为人设计（彩色表格、缩写 flag、交互式提示），AI Agent 需要的是完全不同的东西：

> "Human DX optimizes for discoverability. Agent DX optimizes for predictability."
> — Justin Poehnelt, *You Need to Rewrite Your CLI for AI Agents*

Agent 的核心需求：
- **可发现**：不读文档就知道有什么命令
- **可解析**：结构化输出，不需要正则 hack
- **可预测**：同样输入永远同样格式的输出
- **有界**：输出量可控，不撑爆 context window

### 2.2 CLI Spec 六原则（2026）

[CLI Spec](https://clispec.dev/) 定义的面向多受众（人、脚本、Agent）的 CLI 设计规范：

1. **结构化输出（Structured Output）**：管道时自动 JSON，终端时人类友好
2. **Schema 自省（Schema Introspection）**：`schema` 命令暴露机器可读的命令/参数/输出字段/错误类型
3. **Stderr/Stdout 分离**：数据走 stdout，诊断/进度/错误走 stderr
4. **默认非交互（Non-Interactive by Default）**：所有交互输入都有 flag 替代
5. **幂等操作（Idempotent Operations）**：重复执行产生相同结果
6. **有界输出（Bounded Output）**：支持 `--limit`、`--offset`、`--fields`

> "Agents should never need to parse `--help` text to discover what a tool can do."

### 2.3 AXI：Agent eXperience Interface 十原则

[AXI](https://axi.md/) 是更激进的 Agent 优先设计框架，分四类十原则：

**效率（Efficiency）**
1. Token 高效输出 — 用 TOON（Token-Optimized Object Notation）替代 JSON，节省 ~40% token
2. 最小默认 schema — 列表每项只返回 3-4 个字段
3. 内容截断 — 大字段截断并给出 size hint

**健壮性（Robustness）**
4. 预计算聚合 — 返回派生字段（总数、CI 摘要），消除额外请求
5. 明确的空状态 — 输出 "0 results" 而非沉默
6. 结构化错误 + exit code — 幂等 mutation，错误输出到 stdout，永不交互式提示

**可发现性（Discoverability）**
7. 环境上下文（Ambient Context）— 自注入 session hook，Agent 行动前就能看到相关状态
8. 内容优先 — 无参数运行时显示实时数据，而非 help 文本
9. 上下文披露 — 输出后附带下一步可用命令的具体模板
10. 一致的 help — 每个子命令提供简洁 `--help`

**验证数据**：490 次浏览器自动化 + 425 次 GitHub API 测试中，AXI 达到 100% 成功率，$0.074/task（MCP $0.100，原始 CLI $0.088）。

### 2.4 AI Agent 实际用得好的 6 个 CLI

来源：[DeployHQ 调研](https://www.deployhq.com/blog/6-developer-clis-ai-coding-agents-use-well)

| CLI | 领域 | Agent 友好特征 |
|-----|------|---------------|
| gh | 源码管理 | `--json` flag、一致的 verb-noun 结构 |
| Linear CLI | 项目管理 | 结构化输出、非交互 |
| Vercel CLI | 前端部署 | 可预测的命令模式 |
| DeployHQ (dhq) | 部署 | 清晰错误信息 |
| flyctl | 边缘基础设施 | JSON 输出、非交互默认 |
| Terraform | IaC | 计划/应用分离、JSON plan |

共同特征：
- `--json` flag（**最重要的单一特征**）
- 一致的 verb-noun 命令结构
- 非交互默认或 `--yes` flag
- 清晰的结构化错误信息

---

## 三、给 Skill 暴露 CLI 的几种形式

### 形式 A：大文本描述（当前常见方式）

把 CLI 用法写成一段文本，塞进 system prompt 或 skill 描述：

```markdown
This tool supports:
- `deploy --env prod --service api` - Deploy a service
- `logs --service api --tail 100` - View logs
- `status --env prod` - Check environment status
```

**优点**：
- 简单直接，零额外开发
- LLM 训练数据中大量类似格式，理解无障碍
- 快速验证阶段够用

**缺点**：
- 占用 context window，命令多时不可扩展
- 容易与实际代码不同步
- Agent 每次调用都要"重新阅读"整个说明
- 无法按需加载，全量或无

**适用场景**：命令 < 20 个、相对稳定、快速验证阶段

### 形式 B：Schema 自省（推荐方向）

CLI 自身暴露机器可读的 schema：

```bash
mytool schema          # 所有命令的 JSON schema
mytool schema deploy   # 单个命令的详细 schema
```

```json
{
  "commands": {
    "deploy": {
      "description": "Deploy a service to target environment",
      "args": {"service": {"type": "string", "required": true}},
      "flags": {"--env": {"type": "enum", "values": ["prod","staging"]}},
      "output": {"type": "object", "fields": {"status": "string", "url": "string"}}
    }
  }
}
```

**优点**：
- 始终与实际代码同步（schema 从代码生成）
- Agent 可按需加载单个命令的 schema，不浪费 context
- 实测 first-try 准确率从 ~60% 提升到 ~90%（[Building AI-Friendly CLIs](https://www.hahwul.com/posts/2026/building-ai-friendly-clis/)）
- 解析错误从 41% 降到接近 0

**缺点**：
- 需要额外开发 schema 层
- 需要维护 schema 与实现的一致性（最好自动生成）

**实现参考**：
- Google Workspace CLI 的 `gws schema drive.files.list`
- Cobra 框架可自动生成 JSON schema

### 形式 C：MCP（Model Context Protocol）封装

把 CLI 包装成 MCP server，暴露为 tool：

```json
{
  "name": "deploy_service",
  "description": "Deploy a service to target environment",
  "input_schema": {
    "type": "object",
    "properties": {
      "service": {"type": "string"},
      "env": {"type": "string", "enum": ["prod", "staging"]}
    }
  }
}
```

**优点**：
- 结构化输入输出，Agent 原生支持
- 内置认证、审计日志
- 跨系统协调时优势明显

**缺点**：
- 多一层抽象
- Schema 加载消耗 token（upfront cost）
- 本地快速迭代时 overhead 不值得

### 形式 D：渐进式披露（Progressive Disclosure）

Claude Code Skills 采用的模式，也是最值得学习的：

```
启动时 → 只加载 name + description（一行）
匹配时 → 加载完整 SKILL.md 指令
需要时 → 加载关联脚本和资源
```

**映射到 CLI 暴露**：
- 顶层：只暴露命令分类和一句话描述（占极少 context）
- 按需：Agent 决定使用某个命令时，再通过 `--help` 或 `schema <cmd>` 获取详情
- 深入：执行时才加载完整参数和示例

这是**大文本描述的升级版**——不是一次性塞入所有信息，而是分层按需加载。

### 形式对比总结

| 维度 | 大文本 | Schema 自省 | MCP | 渐进式 |
|------|--------|------------|-----|--------|
| 开发成本 | 极低 | 中 | 高 | 中 |
| Context 效率 | 差 | 好 | 中 | 最好 |
| 同步性 | 手动维护 | 自动 | 自动 | 半自动 |
| Agent 准确率 | ~60% | ~90% | ~90% | ~85-90% |
| 适用规模 | < 20 命令 | 不限 | 不限 | 不限 |
| 适用阶段 | 验证期 | 成熟期 | 跨系统 | 通用 |

---

## 四、Inner Loop vs Outer Loop 框架

来源：[CircleCI - MCP vs CLI](https://circleci.com/blog/mcp-vs-cli/)

| 场景 | 推荐方式 | 原因 |
|------|----------|------|
| 本地开发、快速迭代（Inner Loop） | 直接 CLI | 零开销，LLM 对标准工具已有训练数据，token 效率高 33% |
| 跨系统协调、需要认证（Outer Loop） | MCP 封装 | 结构化响应，集中认证，审计日志 |
| 已有 CLI，想快速接入 AI | 大文本 + JSON 输出 | 最小改动 |
| 新建系统 | Schema 自省 + 渐进式 | 面向未来 |

关键数据：CLI 在多步调试任务中 token 效率高 33%，任务完成分 77 vs 60（对比 MCP）。

---

## 五、AI-Native CLI 的演进光谱

来源：[CLI Index](https://cliindex.easya.work/blog/ai-native-cli-tools)

```
Agent-Hostile → Agent-Compatible → Agent-Friendly → Agent-Native
   (交互式)      (Unix 哲学)        (加了 --json)    (为 Agent 设计)
   
   vim            grep, git          gh, terraform    Claude Code, aider
```

五个 AI-Native 特征：
1. **结构化输出为默认** — JSON 是主输出，人类可读是次要的
2. **自然语言输入** — 接受意图描述，不只是 flag
3. **自描述接口** — 运行时暴露 schema
4. **确定性操作** — 固定排序、稳定格式
5. **结构化错误** — 返回可操作信息（什么失败了、为什么、怎么修）

---

## 六、实操建议

### 6.1 已有系统快速接入（最小可行方案）

1. **加 `--output json` flag**：所有命令支持 JSON 输出
2. **加 `--no-color` / 检测 isatty()**：管道时自动去 ANSI
3. **加 `--yes` / `--force`**：所有确认操作有非交互替代
4. **写精简命令清单**：作为 skill 描述（控制在合理长度）
5. **有意义的 exit code**：不同错误不同 code
6. **错误输出为 JSON**：`{"error": "msg", "code": "NOT_FOUND", "suggestion": "..."}`

### 6.2 中期建设

1. **实现 `schema` 子命令**：从代码自动生成，暴露命令/参数/输出类型
2. **支持 `--fields` 选择**：Agent 只取需要的字段，节省 context
3. **支持 `--limit` 分页**：有界输出
4. **Input hardening**：校验路径遍历、特殊字符、双编码（Agent 幻觉模式与人不同）
5. **`--dry-run`**：本地校验请求，不实际执行

### 6.3 长期方向

1. **渐进式 schema 披露**：顶层索引 + 按需详情
2. **MCP wrapper 自动生成**：从 schema 自动生成 MCP server
3. **TOON 格式**：Token-Optimized Object Notation，比 JSON 省 40% token
4. **Ambient context**：自注入 session hook，Agent 行动前就有上下文
5. **Contextual disclosure**：输出后附带下一步命令模板

### 6.4 关于"输出一大段文本"的判断

你观察到的"输出一个很大的文本描述 CLI 用法"这种形式，本质上是形式 A。它的天花板：

- 命令超过 ~20 个时，context window 压力大
- Agent 每次都要"重新阅读"全部说明
- 无法与代码自动同步

**更好的做法**：分层披露
- 顶层只暴露命令分类 + 一句话描述（类似 Claude Skills 的 name + description）
- Agent 需要时再通过 `schema <cmd>` 或 `<cmd> --help` 获取详情
- 这样既保持了文本描述的简单性，又解决了规模问题

---

## 七、关键参考资料

| 资料 | 核心价值 |
|------|----------|
| [CLI Spec](https://clispec.dev/) | 六原则规范，面向人/脚本/Agent 的统一设计 |
| [AXI - Agent eXperience Interface](https://axi.md/) | 十原则，有 benchmark 数据 |
| [You Need to Rewrite Your CLI for AI Agents](https://justin.poehnelt.com/posts/rewrite-your-cli-for-ai-agents/) | Schema 自省、Input Hardening、Safety Rails |
| [Building AI-Friendly CLIs](https://www.hahwul.com/posts/2026/building-ai-friendly-clis/) | JSON-First I/O 实测数据（60%→90%） |
| [MCP vs CLI](https://circleci.com/blog/mcp-vs-cli/) | Inner/Outer Loop 框架 |
| [6 CLIs AI Agents Use Well](https://www.deployhq.com/blog/6-developer-clis-ai-coding-agents-use-well) | 实际案例分析 |
| [AI-Native CLI Tools](https://cliindex.easya.work/blog/ai-native-cli-tools) | 演进光谱 |
| [Claude Code Skills Framework](https://www.digitalapplied.com/blog/claude-agent-skills-framework-guide) | 渐进式披露的实现参考 |

---

## 八、与之前笔记的关联

- 本笔记是 [[cli-as-agent-interface]] 的深化调研版本
- 之前的判断"CLI 是 Agent 最佳工具接口"得到了业界数据验证
- 新增内容：具体的暴露形式对比、AXI 框架、实操路径、benchmark 数据
