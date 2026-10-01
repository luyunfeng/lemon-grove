# Hermes Agent Self-Evolution 观察记录

> [!summary]
> 
>
> Nous Research 的 `hermes-agent-self-evolution` 不是在训练更强模型，而是在尝试让 agent 自己迭代 `SKILL.md`、工具描述和 system prompt，后面甚至想推进到代码层的进化。

## 这件事在做什么

- 先把当前 agent 的技能和提示词当作 baseline。
- 自动生成评测任务，或从历史 session 中挖真实案例。
- 用 DSPy + GEPA 做进化式搜索，根据执行结果和失败轨迹改写提示词与 skill 文本。
- 再做约束校验，比如结构完整性、尺寸限制、测试和基准回归。
- 最后选出更优版本，通过 PR 流程提交，而不是直接自动上线。

## 值得关注的点

- 它优化的是 agent 的行为层，不是模型权重层，所以不需要 GPU 训练，主要靠 API 调用就能跑。
- 它想把 prompt / skill 的优化做成可重复的工程流程，而不是纯手工调参。

## 我的判断

这更像一个早期的 Phase 1 原型，还不是成熟的自进化框架。

### 目前的现实进展

- 真正落地的主要还是 skill evolution。
- tool description、system prompt、code evolution 还更多停留在计划阶段。
- 报告里最主要的验证结果，是用 `arxiv` skill 做的一次小规模实验。

### 这次实验的局限

- 样本很小，只有 7 个 synthetic case。
- 3 个用于训练，2 个用于 held-out。
- 评分方法偏启发式，主要依赖关键词重叠。
- 报告里写的亮点是 `+39.5%`，但更直接看平均值，实际上是 `0.391 -> 0.472`，大约 `+20.7%`。

### 工程成熟度

- 代码里的不少 guardrail 还没完全打磨好。
- 完整闭环还不够完整。
- 距离生产可用还有明显距离。

## 更准确的定位

它不是“agent 已经会自主进化了”，而是 Nous 在认真探索一条合理路线：

- 把 agent 的技能、工具说明和 prompt 当作可优化对象。
- 用 evolutionary search 做低成本持续改进。
- 把结果放进可评测、可回滚、可提 PR 的工程流程里。

## 适合关注的场景

- skill-heavy agent
- 工具调用规则复杂的 agent
- 想做 prompt / system instruction 自动迭代，但又不想碰模型训练的人

## 一句话总结

这项目的价值不在于今天就能直接生产，而在于它把"agent 自我改进"从概念炒作，往"可评测、可回滚、可提 PR 的工程流程"推进了一步。

[[doc-notes/mocs/AI Coding MOC|AI Coding MOC]]
