---
title: Lil'Log 博客阅读路线
type: roadmap
tags: [learning-path, ai-safety, post-training, harness]
entities: []
---

# Lil'Log 博客阅读路线

> **目标**：围绕 AI coding 和 Agent 工程的需要，有选择地读 Lil'Log 博客（共 52 篇正式文章），建立「从模型能力到系统能力」的背景知识，能用 harness、评测、奖励设计、幻觉这些视角判断 Agent 工程方案。
>
> **读法**：不要从最早的一篇顺序读。先读 Prompt、Agent、Thinking、Harness、Reward Hacking、Hallucination 这几篇，再按缺口补 Transformer、Scaling、数据和强化学习基础。篇名直接搜索即可找到。

## 为什么值得读
- **它是一张研究重心迁移的地图**：主题从深度学习基础、视觉、生成模型和强化学习入门，到表示学习、元学习、数据效率、大模型系统，再到 LLM、Agent、对齐、推理时计算、规模规律和自我改进 harness。这条迁移本身反映了 AI 工程重心的变化：单点模型不够，系统边界、数据质量、评测和人类监督越来越重要。
- **写法本身可以借鉴**：每篇把问题背景、代表论文、方法谱系、关键图和局限放在同一个框架里，适合当「进入一个领域前的地图」。

## 阶段 1：Agent 与 LLM 工程（优先）
- [ ] **Prompt Engineering**：不改权重也能控制 LLM 行为，是走向上下文工程和 harness 的起点。
- [ ] **LLM Powered Autonomous Agents**：planning、memory、tool use 的基本框架。
- [ ] **Why We Think**：推理时计算（test-time compute）和思维链为什么能提升推理。
- [x] **Harness Engineering for Self-Improvement**：现代 Agent 运行时、评测、记忆和自我改进。要点已整理进 Skill 自进化和递归自我改进。

完成标志：能说清一个 Agent harness 由哪些部分组成，以及为什么近中期的自我改进先发生在 harness 层。

## 阶段 2：安全与可靠性
自动化程度越高的 Agent，越绕不开奖励作弊和弱评测器这类风险，这一阶段是阶段 1 的风险背景。
- [ ] **Reducing Toxicity in Language Models**：语言模型的安全风险从哪来、怎么测、怎么缓解。
- [ ] **Adversarial Attacks on LLMs**：prompt 注入与越狱的攻击面。
- [ ] **Extrinsic Hallucinations in LLMs**：事实性，以及「不知道时承认不知道」。
- [ ] **Reward Hacking in Reinforcement Learning**：奖励函数不完美时 Agent 如何钻漏洞，是自主 Agent 场景的核心障碍。

完成标志：能解释可验证奖励为什么也会被钻空子，以及为什么验证器要放在自我改进循环之外。

## 阶段 3：模型结构与规模（按缺口补）
- [ ] **Attention? Attention!**：先建立 attention 概念。
- [ ] **The Transformer Family** 与 **The Transformer Family Version 2.0**：架构演进。
- [ ] **How to Train Really Large Models on Many GPUs?**：训练系统、并行和显存管理。
- [ ] **Large Transformer Model Inference Optimization**：推理优化、蒸馏和部署效率。
- [ ] **Scaling Laws, Carefully**：计算、损失、模型规模、数据规模之间的经验规律。

## 阶段 4：生成模型与多模态（可选）
- [ ] **From GAN to WGAN**、**From Autoencoder to Beta-VAE**、**Flow-based Deep Generative Models**：三类经典生成范式。
- [ ] **What are Diffusion Models?**：现代扩散模型入门。
- [ ] **Diffusion Models for Video Generation**：从图像扩散走向视频的时序一致性和数据问题。
- [ ] **Generalized Visual Language Models**：视觉语言模型。

## 最值得优先读的 12 篇
| 顺序 | 篇名 | 为什么先读 |
|---|---|---|
| 1 | Harness Engineering for Self-Improvement（已读） | 直接对应现代 Agent 运行时、自我改进、可观测性和评测 |
| 2 | LLM Powered Autonomous Agents | Agent 基础框架 |
| 3 | Why We Think | 推理时计算与推理能力的系统综述 |
| 4 | Reward Hacking in Reinforcement Learning | 为什么更强的 Agent 必须重视评测和奖励设计 |
| 5 | Extrinsic Hallucinations in LLMs | 事实性、证据和「不知道」能力是产品化核心 |
| 6 | Prompt Engineering | 从 prompt 走向上下文和 harness 的起点 |
| 7 | Scaling Laws, Carefully | 能力提升背后的计算、数据、规模规律 |
| 8 | The Transformer Family | LLM 架构背景的核心入口 |
| 9 | Large Transformer Model Inference Optimization | 部署和性能工程的基础 |
| 10 | Thinking about High-Quality Human Data | 训练和对齐都离不开高质量人类数据 |
| 11 | What are Diffusion Models? | 生成模型主线里最重要的现代入口 |
| 12 | A (Long) Peek into Reinforcement Learning | 理解 RLHF、奖励作弊和 Agent 优化的基础 |

## 按主题补缺口（其余篇目）
- **强化学习与搜索**：The Multi-Armed Bandit Problem and Its Solutions；Policy Gradient Algorithms；Implementing Deep Reinforcement Learning Models with Tensorflow + OpenAI Gym；Meta Reinforcement Learning；Evolution Strategies；Curriculum for Reinforcement Learning；Exploration Strategies in Deep Reinforcement Learning。
- **数据效率与表示学习**：Self-Supervised Representation Learning；Contrastive Representation Learning；Learning with not Enough Data 三篇（Semi-Supervised Learning、Active Learning、Data Generation）。
- **语言与检索**：Learning Word Embedding；Generalized Language Models；How to Build an Open-Domain Question Answering System?；Controllable Neural Text Generation。
- **理论与可解释性**：Anatomize Deep Learning with Information Theory；How to Explain the Prediction of a Machine Learning Model?；Are Deep Neural Networks Dramatically Overfitted?；Some Math behind Neural Tangent Kernel。
- **元学习与自动化**：Meta-Learning: Learning to Learn Fast；Neural Architecture Search；Domain Randomization for Sim2Real Transfer。
- **视觉**：Object Detection 系列四篇（Gradient Vector, HOG, and SS；CNN, DPM and Overfeat；R-CNN Family；Fast Detection Models）。
- **入门**：An Overview of Deep Learning for Curious People；Predict Stock Prices Using RNN 两篇。

## 读 Harness 这篇时抓住的问题（供后续阅读对照）
- **三类基础模式**：工作流自动化（计划 → 执行 → 测试 → 改进）、文件系统当记忆、子 Agent 与后台任务。关键在「可检查」：输出落在文件、日志、状态记录里，中断后也能恢复。
- **优化对象阶梯**：指令提示 → 结构化上下文 → 工作流 → harness 代码 → 优化器代码 → 权重 → RSI 循环。
- **七个挑战**：弱评测器、记忆生命周期、负结果、多样性塌缩、奖励作弊、长期成功、人的角色。其中奖励作弊和幻觉正好对应阶段 2 的篇目。
