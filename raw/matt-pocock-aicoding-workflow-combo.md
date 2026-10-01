# Matt Pocock AICoding 组合拳阅读笔记

AI Coding Reading Note

# Matt Pocock Skills：一套“小而美”的 AI Coding 组合拳

来源微信公众号

作者why技术

时间2026-07-20 抓取

原文[mp.weixin.qq.com](https://mp.weixin.qq.com/s/k6lgYu1hKtnAbNNEvuIiCg)

**核心观点：** 文章用一个完整案例说明 `mattpocock/skills` 如何把一个模糊想法推进成可执行软件：先用 `/grill-with-docs` 拷问需求并沉淀上下文，再用 `/to-spec` 生成规格，用 `/to-tickets` 拆任务，最后用 `/implement` 执行 TDD + code review。

文章还特别扩展了 `/wayfinder`：它不只适合技术问题，也适合任何“目标明确但路径模糊”的探索型任务。

## 背景信息

### 项目热度

文章称 `mattpocock/skills` 在 GitHub 上有约 176k star，是经过市场验证的明星项目。

### 下载增长

作者引用 Matt Pocock 视频中的数据：7 月 16 日约 750 万下载，7 月 18 日写文时约 960 万下载。

### 上下文体量

安装完成后，整套 skills 在 context 中只占约 660 tokens。作者认为这是它“小而美”的关键特征。

## 安装与初始化

### 安装仓库
    
    
    npx skills add mattpocock/skills

文章提醒：安装时会看到一个 `other` 分组，里面是作者正在试验、未来可能删除的技能，可以先不用重点关注。

### 项目内初始化
    
    
    /setup-matt-pocock-skills

这一步需要在具体项目里执行，用来设置问题跟踪方式、技能触发关键词、开发相关文件等。

## 组合拳全链路

**Idea** 一个模糊想法或产品需求

**/grill-with-docs** 一问一答澄清需求、术语、冲突和决策

**CONTEXT + ADR** 沉淀术语、业务背景、架构决策

**/to-spec** 把已澄清需求转成结构化规格文档

**/to-tickets** 拆成可执行任务和依赖关系

**/implement** 逐个实现任务，内部使用 TDD + code review

## 每个 Skill 的功能定位

Skill | 文章中的角色 | 产物 | 关键价值  
---|---|---|---  
`/grill-with-docs` | 通过“拷问”式多轮对话，把需求聊清楚。 | `CONTEXT.md`、术语解释、ADR。 | 把无法从代码推导出来的业务背景、历史决策和约束沉淀下来。  
`/to-spec` | 把已讨论明确的需求整理成结构化 Spec。 | `.scratch/.../spec.md` | 把对话转成可执行的软件开发规范，减少后续实现时的猜测。  
`/to-tickets` | 把 spec 拆成详细任务。 | 多个 issue / ticket，附任务依赖和可并行项。 | 把大需求切成 Agent 可逐个完成的小单元。  
`/implement` | 进入编码实现阶段。 | 实际代码改动、测试、评审结果。 | 它是组合技能，内部使用 `/tdd` 和 `/code-review`，不需要再手动追加评审。  
`/wayfinder` | 处理“目标存在但路线不清晰”的探索问题。 | `map.md`、子任务、待定项、阶段性路线图。 | 先找到正确路线，再进入验证、规格或执行。  
  
## `/grill-with-docs` 案例：音乐节海报网站

### 初始需求

用户想做一个网站，输入音乐节名称、时间和乐队列表，生成一张“看过的乐队演出”海报。示例是 2026 年 5 月草莓音乐节，包含棱镜、马赛克、夏日入侵企画、痛仰等乐队。

### 追问方式

这个 skill 的重要准则是一次只问一个问题。每个问题都会附带推荐答案和推荐理由，让用户可以快速决策。

### 发现冲突

当用户选择“零后端”又选择“AI 生成主视觉”时，skill 会指出外部图像 API 与零后端之间的冲突，并要求用户做决策。

### 沉淀结果

经过约 20 个问题后，需求被澄清，项目文件中出现了术语解释和 ADR，后续可以进入 `/to-spec`。

## `/to-spec` 生成的规范结构

### Problem Statement

描述要解决什么问题，以及为什么需要这个功能。

### Solution

描述整体解决方案和功能流程。

### User Stories

用“谁、要做什么、为什么做”的方式明确需求。

### Implementation Decisions

记录架构设计、技术选型、数据模型和关键约束。

### Testing Decisions

明确测试范围、测试策略和核心测试边界。

### Out of Scope

明确当前版本不做什么，防止 Agent 自行扩展需求。

## `/wayfinder` 的单独价值

### 区别于 `/grill-with-docs`

文章的理解是：`/wayfinder` 是寻找正确路线，属于探索和规划；`/grill-with-docs` 是审问已有方案，确保方案和项目知识一致，属于验证和沉淀。

### 非技术案例

作者用“10km 当前 45 分钟，3 个月后想跑进 40 分钟”作为例子。`/wayfinder` 会先询问跑量、经验、每周训练时间等基础信息，再生成路线图和子任务。

### 动态地图

`map.md` 中会有 `not yet specified`，并围绕这些待明确点生成子任务。随着问题被回答，地图会持续更新。

### 结果形态

在跑步案例中，经过 31 个问题后，最终输出了 12 周训练计划、恢复计划、营养安排、配速区间和进度观察方式。

## 文章里的关键建议

  * 进入编码前可以先 `/clear` 清空上下文，把上下文窗口留给实现阶段。
  * `/implement` 可以逐个实现 tickets，也可以拿到一组 tickets 后逐个推进。
  * 如果有改动需求，可以再次从 `/grill-with-docs` 开始，把新冲突和新决策沉淀下来。
  * 遇到目标明确但路径不清时，可以先用 `/wayfinder`，不必局限在技术任务。

## 我的理解

这套流程最有价值的地方，不是它有很多命令，而是每个命令都对应一个清晰的工程阶段：探索、澄清、规格、拆票、实现、评审。它把“让 AI 写代码”前面的需求治理和决策治理补上了。

`/grill-with-docs` 解决的是“用户脑子里的隐性需求”；`/to-spec` 解决的是“对话不可执行”；`/to-tickets` 解决的是“大任务不可控”；`/implement` 解决的是“实现过程需要纪律”；`/wayfinder` 则解决的是“连路线都还没清晰”。

我会把它理解成轻量版的 AI Coding 操作系统：不是用复杂框架强行接管开发，而是用一组小 skill 把关键阶段串起来。真正落地时，最需要关注的是产物是否进入项目：`CONTEXT.md`、ADR、spec、tickets、测试结果、code review 结论，这些才是可复用的工程记忆。

## 可迁移工作流

  1. 模糊需求先走 `/wayfinder`：判断路线是否清晰，列出待定点。
  2. 已有想法走 `/grill-with-docs`：一次一个问题，把术语、冲突、边界、业务规则问清楚。
  3. 需求稳定后走 `/to-spec`：生成可执行规范，尤其写清 out of scope。
  4. 规范稳定后走 `/to-tickets`：拆任务，标依赖，识别可并行项。
  5. 实现前 `/clear`，再用 `/implement`：让上下文窗口服务于编码和测试。
  6. 新增需求不要直接补代码：重新从澄清开始，把新决策沉淀到项目知识中。

## 标签

Matt Pocock Skills AI Coding Workflow /grill-with-docs /to-spec /to-tickets /implement /wayfinder

记录日期：2026-07-20  
笔记路径：doc-notes/ai-coding/2026-07/notes/matt-pocock-aicoding-workflow-combo.html  
原文包含 57 张正文图片；本笔记保留文字主线、截图对应的案例脉络和可执行命令，未下载归档原图。
