# Claude Code 在大型代码库中的最佳实践

> [!abstract]
> 来源：[Claude Code at scale 系列](https://claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start)
>
> 最成功的 Claude Code 企业级部署在配置、工具链和组织结构上都呈现出一组可识别的模式。本文是 Claude Code 规模化系列的第一篇。

---

## 一、核心洞察：Agentic Search vs RAG

Claude Code 导航代码库的方式与人类工程师一样：遍历文件系统、读取文件、使用 grep 精确查找、跨代码库跟踪引用。它在开发者本地机器上运行，不需要构建、维护或上传代码库索引到服务器。

| 维度 | RAG 方案 | Agentic Search（Claude Code） |
|------|----------|------------------------------|
| 索引维护 | 需要嵌入管道，可能滞后数小时/天/周 | 无索引，直接操作实时代码库 |
| 过时风险 | 高（返回已删除/重命名的函数） | 零（始终操作最新代码） |
| 启动成本 | 需要预构建索引 | 零（开箱即用） |
| 前提条件 | 低 | 需要足够的起始上下文知道"往哪看" |

**关键结论**：Agentic Search 避免了 RAG 的失效模式，但效果取决于代码库的设置质量——通过 CLAUDE.md 文件和 skills 分层提供上下文。

---

## 二、Harness（工具链生态）比模型更重要

一个常见误解：Claude Code 的能力仅由所用模型决定。实际上，围绕模型构建的生态系统（harness）比模型本身更能决定表现。

Harness 由五个扩展点构成，按构建顺序排列：

### 2.1 CLAUDE.md 文件（第一层）

- **作用**：Claude 每次会话自动读取的上下文文件
- **结构**：根文件提供全局视角，子目录文件提供本地约定
- **原则**：只放广泛适用的内容，防止性能拖累

### 2.2 Hooks（第二层）

- **常见误解**：只用于阻止 Claude 做错事
- **更有价值的用法**：
  - **Stop hook**：会话结束时反思发生了什么，趁上下文新鲜时提出 CLAUDE.md 更新建议
  - **Start hook**：动态加载团队特定的上下文，让每个开发者无需手动配置就能获得适合自己模块的设置
  - **自动化检查**：linting、formatting 等确定性规则比让 Claude"记住"指令更可靠

### 2.3 Skills（第三层）

- **核心机制**：渐进式披露（progressive disclosure）
- **解决的问题**：大型代码库有数十种任务类型，不是所有专业知识都需要在每个会话中出现
- **路径绑定**：可以限定到特定路径，只在相关代码区域自动加载
- **示例**：安全审查 skill 只在评估漏洞时加载，文档处理 skill 只在代码变更需要更新文档时加载

### 2.4 Plugins（第四层）

- **解决的问题**：好的设置容易变成"部落知识"
- **机制**：将 skills、hooks、MCP 配置打包成可安装包
- **分发**：通过托管市场（managed marketplaces）在组织内分发更新
- **案例**：某大型零售组织构建了连接内部分析平台的 skill，作为 plugin 在全面推广前分发给业务分析师

### 2.5 MCP Servers（第五层）

- **作用**：连接 Claude 无法直接访问的内部工具、数据源和 API
- **高级用法**：暴露结构化搜索作为 Claude 可直接调用的工具
- **常见连接对象**：内部文档、工单系统、分析平台

### 2.6 两个额外能力

| 能力 | 说明 | 价值 |
|------|------|------|
| **LSP 集成** | 通过语言服务器协议提供符号级导航 | 在大型代码库中区分同名函数，C/C++ 规模化导航的"最高价值投资" |
| **Subagents** | 隔离的 Claude 实例，独立完成任务后只返回结果 | 将探索与编辑分离：只读 subagent 映射子系统，主 agent 基于完整信息编辑 |

### 2.7 组件对比表

| 组件 | 是什么 | 何时加载 | 最适合 | 常见混淆 |
|------|--------|----------|--------|----------|
| CLAUDE.md | 自动读取的上下文文件 | 每次会话 | 项目特定约定、代码库知识 | 把可复用的专业知识也塞进去 |
| Hooks | 关键时点运行的脚本 | 事件触发 | 自动化一致行为、捕获会话学习 | 用 prompt 做应该自动运行的事 |
| Skills | 特定任务类型的打包指令 | 按需，相关时加载 | 跨会话/项目的可复用专业知识 | 全部加载到 CLAUDE.md |
| Plugins | 打包的 skills + hooks + MCP | 配置后始终可用 | 在组织内分发工作配置 | 让好的设置停留在部落知识 |
| LSP | 通过语言服务器实时代码智能 | 配置后始终可用 | 符号级导航和自动错误检测 | 以为是自动的 |
| MCP Servers | 连接外部工具和数据 | 配置后始终可用 | 给 Claude 访问无法直接触及的内部工具 | 基础没打好就建 MCP |
| Subagents | 特定任务的独立 Claude 实例 | 调用时 | 分离探索与编辑、并行工作 | 在同一会话里跑探索和编辑 |

---

## 三、成功部署的三大配置模式

### 3.1 让代码库在规模上可导航

Claude 在大型代码库中的帮助能力受限于其找到正确上下文的能力。过多上下文拖慢性能，过少则让它盲目导航。

**具体做法**：

- **CLAUDE.md 文件保持精简和分层**
  - 根文件：只放指针和关键陷阱
  - 子目录文件：本地约定
  - Claude 自动向上遍历目录树，加载沿途所有 CLAUDE.md

- **在子目录而非仓库根初始化**
  - 让 Claude 范围限定到与任务相关的代码部分
  - 根级上下文不会丢失（自动向上遍历）

- **按子目录限定测试和 lint 命令**
  - 避免改动一个服务时运行全量套件（超时 + 浪费上下文）
  - 适用于每个目录有自己测试/构建命令的服务导向代码库
  - 编译型 monorepo 有深层跨目录依赖时更难实现

- **使用 `.ignore` 文件排除生成文件、构建产物和第三方代码**
  - 在 `.claude/settings.json` 中提交 `permissions.deny` 规则
  - 版本控制确保团队内一致
  - 生成文件本身是开发对象的场景可本地覆盖

- **构建代码库地图（当目录结构不够自解释时）**
  - 根目录轻量 markdown 文件：顶层文件夹 + 一行描述
  - 分层：根文件只描述最高层结构，子目录 CLAUDE.md 提供下一层细节
  - 简单场景可用 @-mention 指定文件/目录

- **运行 LSP 服务器**
  - grep 常见函数名返回数千匹配，Claude 浪费上下文打开文件筛选
  - LSP 只返回指向同一符号的引用，过滤在 Claude 读取前完成
  - 需要安装对应语言的 code intelligence plugin 和语言服务器二进制

> **注意**：在数十万文件夹、数百万文件，或非 git 版本控制的遗留系统中，分层 CLAUDE.md 也会失效。系列后续文章会讨论。

### 3.2 随模型演进主动维护 CLAUDE.md

模型演进时，为当前模型写的指令可能对未来模型起反作用。

**示例**：
- 早期模型需要"每次重构只改一个文件"的规则来保持正轨
- 新模型能很好处理跨文件协调编辑，这条规则反而限制了它

**维护节奏**：
- 每 3-6 个月做一次有意义的配置审查
- 重大模型发布后性能停滞时也应审查
- 补偿特定模型限制的 skills/hooks 在限制消除后变成开销

**案例**：拦截文件写入以强制 `p4 edit` 的 hook，在 Claude Code 添加原生 Perforce 支持后变得冗余。

### 3.3 为 Claude Code 管理分配明确 owner

技术配置 alone 不能驱动采用。组织层面的投资同样关键。

**最快推广的部署特征**：
- 广泛开放前有小团队做基础设施投入
- 有时仅一两个人就接好了工具链，让 Claude 在开发者首次接触时就融入工作流
- 案例 A：几个工程师在 day one 就准备好了 plugins 和 MCPs
- 案例 B：整个团队专注于管理 AI 编码工具，在推广开始前基础设施就位

**Owner 定位**：
- 通常位于 Developer Experience / Developer Productivity 部门
- **新兴角色**：Agent Manager——混合 PM/工程师职能，专门管理 Claude Code 生态
- **最小可行版本**：一个 DRI（直接负责人），拥有配置、权限策略、plugin 市场、CLAUDE.md 规范的决策权

**治理问题（在受监管行业尤其早出现）**：
- 谁控制哪些 skills/plugins 可用？
- 如何防止数千工程师独立重复造轮子？
- 如何确保 AI 生成代码经过与人类代码相同的审查流程？

**建议**：
- 从预定义的技能集、强制代码审查流程、有限初始访问开始
- 建立跨职能工作组：工程 + 信息安全 + 治理代表共同定义需求、制定推广路线图

---

## 四、反思与关联

### 4.1 与之前笔记的关联

- **[[cli-building-for-agent-skills-research|CLI 建设调研]]** 中提到的"渐进式披露"和"Schema 自省"在这里得到了 Claude Code 官方实现（Skills 的 progressive disclosure、CLAUDE.md 的分层加载）
- **[[cli-as-agent-interface]]** 中"CLI 是 Agent 最佳工具接口"的判断，与本文 Agentic Search 优于 RAG 的论点一致
- **[[harness-engineering-reliability|Harness Engineering]]** 的核心理念——"把可靠性问题变成系统设计问题"——与本文"Harness 比模型更重要"完全呼应

### 4.2 关键收获

1. **Agentic Search 是大型代码库的正确范式**：RAG 的索引滞后问题在活跃工程团队中不可接受
2. **配置是复利资产**：CLAUDE.md、Skills、Hooks 的初始投入会在每次会话中持续产生回报
3. **组织设计决定技术上限**：没有明确 owner 的 bottoms-up 采用会停滞在部落知识阶段
4. **模型迭代要求配置迭代**：每 3-6 个月审查一次配置，避免旧约束限制新能力
5. **LSP 是多语言大型代码库的"最高价值投资"**：符号级导航解决 grep 的上下文浪费问题

### 4.3 待探索问题

- [ ] 如何设计 CLAUDE.md 的分层结构？根文件、子目录文件的具体内容边界在哪？
- [ ] Skills 的 progressive disclosure 机制与之前调研的 CLI Schema 自省有何异同？
- [ ] Subagent 模式与 Inner/Outer Loop 框架的对应关系？
- [ ] 在非传统环境（游戏引擎大二进制资产、非 git 版本控制）中的额外配置工作具体是什么？

---

## 五、原文摘录

> "The most successful Claude Code deployments share a set of recognizable patterns across configurations, tooling, and org structure."

> "Human DX optimizes for discoverability. Agent DX optimizes for predictability."

> "Teams that invest in codebase setup see better results."

> "The harness is built from five extension points—CLAUDE.md files, hooks, skills, plugins, and MCP servers—each serving a different function. The order in which teams build them matters."

> "Bottoms-up adoption generates enthusiasm but can fragment without someone to centralize what works."
