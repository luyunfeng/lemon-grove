# Matt Pocock /wayfinder Skill 阅读笔记

AI Coding Reading Note

# Matt Pocock Skills 又更新了：`/wayfinder` 是面向“不确定性”的上游规划工具

来源微信公众号

作者数字边界 EdgeX

时间2026-07-20 抓取

原文[mp.weixin.qq.com](https://mp.weixin.qq.com/s/_u7U-aXg0KXXzyFNtLcvIw)

**核心观点：**`/wayfinder` 不是用来直接实现功能的 skill，而是用来在“目标大致明确、路径仍然模糊”的阶段创建共享地图，逐步消除产品、架构、迁移、边界等不确定性。

它的位置在 `/to-spec` 和 `/to-tickets` 之前：先把未知问题找出来、拆开、逐个解决，再进入规格化和任务拆分。

## 文章精华

### 1\. 安装方式

如果要安装 Matt Pocock 的 skill 集，可以使用：

`npx skills@latest add mattpocock/skills`

也可以只安装 `wayfinder`：

`npx skills add mattpocock/skills --skill=wayfinder`

### 2\. 适用问题

适合重构权限系统、数据迁移、复杂产品架构调整这类“知道目标，但无法直接写可靠规格”的任务。

如果直接进入实现或规格，很容易把还没决定的问题包装成开发任务。

### 3\. 工作载体

`/wayfinder` 会创建带 `wayfinder:map` 标签的主 Issue，作为探索索引。

主地图包含目标、笔记、已决策、未决策、超出范围等部分。

### 4\. 解决方式

真正的问题会作为主地图的子 Issue 被逐个处理。每解决一个问题，就把结论回写到主地图，并可能生成新的问题。

地图不是一次性计划，而是动态收敛的不确定性清单。

## `/wayfinder` 的流程图

**Destination** 定义最终要得到的交付物或决策

**Map** 创建主 Issue，记录范围、笔记、已知和未知

**Frontier** 从未阻塞、未领取的问题中挑一个推进

**Resolve** 用问答、原型、研究或实际任务解决问题

**Update** 关闭子 Issue，把结论和新问题回写主地图

## 四类待解决问题

类型 | 什么时候用 | 例子  
---|---|---  
`grilling` | 需要用户参与回答，补齐业务、产品或偏好信息。 | 自定义角色的能力边界到底到哪一层？  
`prototype` | 需要先做低成本原型，用可见产物辅助判断。 | 先画权限配置界面，再决定角色/策略模型。  
`research` | 需要阅读外部文档、API、知识库，可交给研究子 Agent。 | 调研权限审计日志的存储和合规要求。  
`task` | 必须先完成一个现实操作才能继续决策。 | 申请测试账号、导出旧权限数据、开通测试环境。  
  
## Superpowers 与 Matt Pocock Skills 的区别

### Superpowers

  * 更像一套完整、强约束的软件开发方法。
  * 强调 brainstorming、工作树、计划、子 Agent、TDD、评审等纪律链条。
  * 适合希望 Agent 默认遵循完整工程流程的人。

### Matt Pocock Skills

  * 更像一组可自由组合的工程工具箱。
  * 既有用户主动调用的编排型 skill，也有模型自行调用的纪律型 skill。
  * 适合希望自己掌握流程控制、按任务选择工具的人。

## 关键原句

负责规划和消除不确定性，不负责实现最终交付物。 

## 我的理解

`/wayfinder` 的价值不是“多做一步计划”，而是把复杂任务里最容易被忽略的东西显性化：哪些问题还没决策、哪些问题需要人回答、哪些问题需要原型验证、哪些问题只是执行前置条件。

它更适合放在需求早期或重构早期：当你感觉可以写代码，但每写一步都可能撞上隐藏决策时，就应该先建地图。等地图收敛之后，再把结论喂给 `/to-spec`、`/to-tickets` 或本地计划/TDD流程，效果会更稳。

## 可迁移到日常工作的用法

  1. 先写一句 Destination：这轮探索结束后，我要拿到什么可交付结果。
  2. 列出 Not yet specified：所有当前不敢拍板、会影响方案的问题。
  3. 按 grilling / prototype / research / task 给问题分型。
  4. 每次只解决一个 Frontier 问题，避免把研究发散成泛泛调研。
  5. 每解决一个问题，都回写“结论 + 证据 + 对后续计划的影响”。

记录日期：2026-07-20  
笔记路径：doc-notes/ai-coding/2026-07/notes/matt-pocock-wayfinder-skills.html
