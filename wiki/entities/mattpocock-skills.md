---
title: mattpocock/skills 组合
type: entity
tags: [agent-framework, agent-skill, spec, workflow]
entities: [mattpocock-skills, superpowers]
---

# mattpocock/skills 组合

## 它是什么

一组「小而美」的 AI Coding Skills（仓库名 `mattpocock/skills`）。整套装好后在上下文里只占约 660 tokens。它不用一个大框架接管开发，而是用几把小工具把「让 AI 写代码」之前的需求治理和决策治理补上：每个命令对应一个清楚的工程阶段——探索、澄清、规格、拆票、实现、评审。

里面既有用户主动调用的**编排型** skill，也有模型自行调用的**纪律型** skill（如 `/tdd`、`/code-review`）。

## 核心机制

### 1. 主链路

`/wayfinder`（路线不清时）→ `/grill-with-docs` → `/to-spec` → `/to-tickets` → `/implement`

| Skill | 解决什么问题 | 产物 |
|---|---|---|
| `/wayfinder` | 连路线都还不清楚 | 带 `wayfinder:map` 标签的主 Issue（或 `map.md`）、子问题、阶段性路线 |
| `/grill-with-docs` | 需求藏在用户脑子里 | `CONTEXT.md`（术语、业务背景）、ADR（架构决策记录） |
| `/to-spec` | 对话不可执行 | 结构化规格文档 |
| `/to-tickets` | 大任务不可控 | 多个 issue / ticket，标出依赖和可并行项 |
| `/implement` | 实现需要纪律 | 代码改动、测试、评审结论；内部调用 `/tdd` 和 `/code-review`，不必再手动加评审 |

### 2. `/grill-with-docs`：拷问式澄清

- 一次只问一个问题，每个问题附**推荐答案和推荐理由**，让人能快速拍板。
- 主动发现冲突：例如用户既要「零后端」又要「AI 生成主视觉」，它会指出外部图像 API 与零后端矛盾，要求做决策。
- 结论沉淀进项目：术语解释、业务背景和 ADR 写进文件，这些是**从代码推不出来**的知识。一个中等需求大约问 20 个问题。

### 3. `/to-spec` 的规格结构

Problem Statement（问题和为什么要做）→ Solution（整体方案和流程）→ User Stories（谁、做什么、为什么）→ Implementation Decisions（架构、选型、数据模型、关键约束）→ Testing Decisions（测试范围、策略、边界）→ Out of Scope（这一版不做什么，防止 Agent 自行扩展需求）。

### 4. `/wayfinder`：面向不确定性的上游规划

适用于「目标大致明确、路径仍然模糊」的任务，例如重构权限系统、数据迁移、复杂产品架构调整——知道目标，但还写不出可靠的规格。直接进入实现或规格，很容易把还没决定的问题包装成开发任务。

流程：

1. **Destination**：定义这轮探索结束时要拿到的交付物或决策；
2. **Map**：建主 Issue，包含目标、备忘（notes）、已决策、未决策（not yet specified）、超出范围；
3. **Frontier**：从未阻塞、未领取的问题里挑一个推进，每次只推进一个；
4. **Resolve**：按问题类型解决；
5. **Update**：关闭子 Issue，把结论和新冒出的问题回写地图。

四类待解问题：

| 类型 | 什么时候用 | 例子 |
|---|---|---|
| `grilling` | 需要人回答业务、产品或偏好问题 | 自定义角色的能力边界到哪一层？ |
| `prototype` | 先做低成本原型，用看得见的东西辅助判断 | 先画权限配置界面，再定角色 / 策略模型 |
| `research` | 要读外部文档、API，可交给研究子 Agent | 权限审计日志的存储和合规要求 |
| `task` | 必须先完成一个现实操作才能继续决策 | 申请测试账号、导出旧权限数据 |

它「负责规划和消除不确定性，不负责实现最终交付物」。地图不是一次性计划，而是一张动态收敛的不确定性清单。它也不限于技术问题：「10 公里从 45 分钟跑进 40 分钟」这种目标，问完约 31 个问题后能产出 12 周训练、恢复、营养、配速区间和进度观察方式。

和 `/grill-with-docs` 的分工：`/wayfinder` 找路线（探索与规划），`/grill-with-docs` 审方案（验证并沉淀项目知识）。

## 怎么用

安装与初始化：

```
npx skills add mattpocock/skills                           # 整套
npx skills add mattpocock/skills --skill=wayfinder         # 只装一个
/setup-matt-pocock-skills                                  # 在具体项目里执行，设置问题跟踪方式、触发词、开发相关文件
```

安装时会看到一个 `other` 分组，是仍在试验、可能删除的技能，可以先不管。

可迁移的工作流：

1. 模糊需求先走 `/wayfinder`：写一句 Destination，列出所有不敢拍板、会影响方案的问题，按四类分型。
2. 已有想法走 `/grill-with-docs`：一次一个问题，把术语、冲突、边界、业务规则问清楚。
3. 需求稳定后 `/to-spec`，尤其写清 Out of Scope。
4. 规格稳定后 `/to-tickets`：拆任务、标依赖、找可并行项。
5. 实现前先 `/clear` 清空上下文，把窗口留给编码和测试，再逐个 `/implement`。
6. 新增需求不要直接补代码：重新从 `/grill-with-docs` 开始，把新冲突和新决策沉淀下来。

落地时最该盯的是**产物有没有进项目**：`CONTEXT.md`、ADR、spec、tickets、测试结果、评审结论，这些才是可复用的工程记忆。每解决一个 `/wayfinder` 问题，都回写「结论 + 证据 + 对后续计划的影响」。

和 Superpowers 的区别：Superpowers 像一套完整、强约束的方法，适合希望 Agent 默认走完整工程流程的人；这套更像可自由组合的工具箱，适合想自己掌握流程控制、按任务挑工具的人。
