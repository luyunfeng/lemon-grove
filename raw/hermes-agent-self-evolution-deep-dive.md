# Hermes Agent Self-Evolution：当 Agent 开始优化自己

## 摘要

Nous Research 的 `hermes-agent-self-evolution` 试图回答一个问题：**能不能让 Agent 自己优化自己的 Skill 和 Prompt？** 它用 DSPy + GEPA 构建了一条自动化进化流水线，把"调 prompt"从手工劳动变成了可重复的工程流程。

这不是科幻意义上的"AI 自我觉醒"，而是一次严肃的工程尝试：把 Agent 的行为层（而非模型权重层）当作可优化对象，用进化搜索替代手工调参。

## 一句话总结

Hermes Agent Self-Evolution 把 Prompt/Skill 优化从"玄学手艺"推进到了"可评测、可回滚、可提 PR 的工程流程"。

---

## 1. 先搞清楚：Hermes 是什么

### 1.1 Hermes 模型

Hermes 是 Nous Research 开发的开源模型系列：

- 基于 Llama 3.1 微调，有 8B、70B、405B 参数版本
- 训练数据以合成数据为主，强调指令遵循精确性
- 核心能力：长上下文保持、多轮对话、角色扮演、function-calling

> [!note]
> Hermes 是模型，不是 Agent。Hermes 4 已经演进到支持 reasoning 能力。

### 1.2 Hermes Agent

Hermes Agent 是基于 Hermes 模型构建的 Agent 框架：

- **自治性**：可以隔离派生子 agent 并行工作
- **多平台**：支持 15+ 消息平台集成
- **Skills 系统**：程序性记忆，可以创建、复用、改进技能
- **自学习闭环**：agent-curated memory + 自主 skill 创建

### 1.3 hermes-agent-self-evolution

这是我们要讨论的核心项目。它的定位是：

> 用 DSPy + GEPA 自动进化 Hermes Agent 的 skills、工具描述、系统提示和代码。

---

## 2. GEPA：核心算法

### 2.1 什么是 GEPA

GEPA（Genetic-Pareto）是 DSPy 框架中的 prompt 优化器，2025 年被 ICLR 2026 接收为 Oral 论文。

核心思想：**用自然语言反思替代强化学习的梯度下降。**

### 2.2 为什么 GEPA 比 RL 高效

| 维度 | 强化学习（如 GRPO） | GEPA |
| --- | --- | --- |
| 学习媒介 | 稀疏标量奖励的梯度 | 自然语言反馈 |
| 样本效率 | 需要数千次 rollout | 最高可少 35x |
| 可解释性 | 黑盒权重更新 | 可读的文本进化路径 |
| 性能 | 基准 | 比 GRPO 高 20% |

关键洞见：**语言的解释性本质，为 LLM 提供了比策略梯度更丰富的学习媒介。**

### 2.3 GEPA 的工作流程

1. **采样轨迹**：收集 Agent 的推理、工具调用、输出结果
2. **自然语言反思**：分析"为什么失败"，而非仅仅标记失败
3. **提出改进**：基于反思生成候选 prompt 变体
4. **Pareto 前沿选择**：从多个候选中选出最优组合
5. **迭代进化**：构建进化树，累积改进

---

## 3. Hermes Agent Self-Evolution 的工程实现

### 3.1 工作流程

```
当前 Skills/Prompts → 生成评测数据集 → GEPA 优化器处理执行轨迹
    → 生成候选变体 → 约束门控（测试/大小限制）→ 最优变体 → 提交 PR
```

### 3.2 Guardrails

这不是"让 AI 随便改自己"，而是有严格约束的进化：

- **测试套件**：所有变体必须通过完整测试
- **大小限制**：Skill ≤ 15KB，工具描述 ≤ 500 字符
- **语义保持**：不能改变核心功能
- **人工审批**：通过 PR 流程，不是自动上线

### 3.3 成本

- 不需要 GPU 训练
- 纯 API 调用
- 每次运行约 $2-10

---

## 4. 和 Harness Engineering 的关系

这是一个非常关键的视角。

### 4.1 自我进化是 Harness 的延伸

如果把 Harness Engineering 定义为"给模型套上外部控制系统"，那么自我进化就是在问：

> **Harness 本身能不能被优化？**

Superpowers 项目用 "TDD for Skills" 来测试和强化 Skill 本身，这是对反馈回路做反馈控制（元控制）。Hermes Agent Self-Evolution 走得更远：它不是测试 Skill 是否生效，而是自动生成更好的 Skill。

### 4.2 从"人设计 Harness"到"Agent 优化 Harness"

传统的 Harness Engineering 假设：人设计约束规则，Agent 在规则内执行。

Hermes 的尝试暗示另一条路：**约束规则本身也可以成为优化对象。**

但这里有一个根本问题：谁来定义"更好"？

- 如果用测试套件定义，那进化方向是"通过更多测试"
- 如果用人工评分定义，那进化方向是"人类偏好"
- 如果用 Agent 自己评估定义，那就回到自评偏差问题

Hermes 的方案是用执行轨迹 + 自然语言反思，这是一种"可解释的失败分析"，比纯奖励信号更丰富，但仍然需要外部锚点（测试、人工审批）。

---

## 5. 我的判断

### 5.1 它不是什么

- 不是"Agent 已经能自主进化了"
- 不是"模型权重层面的自我改进"
- 不是生产可用的成熟框架

### 5.2 它真正是什么

**一次严肃的工程探索**，把三个关键想法组合在一起：

1. **行为层优化**：不改权重，改 Skill/Prompt/工具描述
2. **进化搜索**：用 GEPA 替代手工调参
3. **工程闭环**：可评测、可回滚、可提 PR

### 5.3 局限

| 维度 | 现状 |
| --- | --- |
| 验证规模 | 官方实验只有 7 个 synthetic case |
| 评分方法 | 偏启发式（关键词重叠） |
| 覆盖范围 | Skill evolution 落地最多，代码层进化还在计划阶段 |
| Guardrails | 部分机制还没打磨好 |

### 5.4 真正的价值

不在于今天就能直接生产，而在于它指出了一条路线：

> **把 Agent 的行为层（而非权重层）当作可优化对象，用进化搜索 + 工程闭环替代手工调参。**

这条路线有三个关键前提：

1. **Agent 的行为主要由文本决定**（Skill、Prompt、工具描述）
2. **文本优化可以用 LLM 自己来完成**（GEPA 的核心假设）
3. **优化结果可以被外部验证**（测试、人工审批）

如果这三个前提成立，那么 Agent 自我进化就不是一个科幻概念，而是一个可执行的工程项目。

---

## 6. 一个更深的问题

如果 Harness Engineering 的核心洞见是"模型不可信，需要外部约束"，那么自我进化就是在问：

> **优化 Harness 的系统，本身可不可信？**

这里有一个潜在的递归问题：

- Harness 约束 Agent
- 进化系统优化 Harness
- 谁约束进化系统？

答案可能是：**人。**

但人的角色在变化：

- 从"约束 Agent"变成"约束优化 Harness 的系统"
- 从"in the loop"变成"on the loop"

这和 Harness Engineering 的最终结论是一致的：

> 工程师正在从回路内部的执行者，变成回路之上的设计者。

---

## 7. 适合关注的场景

- Skill-heavy Agent（技能调用复杂的 Agent）
- 工具规则频繁变化的场景
- 想做 Prompt 自动迭代但不想碰模型训练的团队
- 需要把"调 prompt"从玄学变成工程流程的项目

## 8. 延伸阅读

- [hermes-agent-self-evolution GitHub](https://github.com/NousResearch/hermes-agent-self-evolution)
- [Hermes Agent Documentation](https://hermes-agent.nousresearch.com/docs/)
- [GEPA Paper - arXiv:2507.19457](https://arxiv.org/abs/2507.19457)
- [DSPy GEPA Tutorial](https://dspy.ai/tutorials/gepa_ai_program/)

[[doc-notes/mocs/AI Coding MOC|AI Coding MOC]]
