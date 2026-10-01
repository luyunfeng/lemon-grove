# Lilian Weng Lil'Log 全站学习地图

AI / ML Reading Map

# Lilian Weng Lil'Log 全站炼化：从深度学习入门到 Agent 自我改进

来源Lil'Log Homepage / Archive / RSS

作者Lilian Weng

范围52 篇正式文章，2017-2026

原站[lilianweng.github.io](https://lilianweng.github.io/)

总览 时间线 主题地图 学习路径 全量目录 我的理解

**核心判断：** Lil'Log 的价值不只是“科普文章多”，而是持续记录了深度学习研究重心的迁移：2017-2018 从基础模型、视觉、GAN/VAE/RL 入门开始；2019-2022 进入 representation、meta-learning、data efficiency、large model systems；2023-2026 明显转向 LLM、agent、alignment、thinking、scaling law 和 harness self-improvement。

如果把全站当作学习路线，它不是线性的“从第一篇读到最后一篇”，而是几条交织的主线：模型结构、学习范式、数据与训练、生成模型、强化学习、语言模型与 agent、安全与可靠性。

## 十年演进：博客主题如何变化

**2017** 10 篇

深度学习入门、RNN 股票预测、解释性、GAN、词向量、目标检测。

**2018** 9 篇

Bandit/RL、Policy Gradient、Attention、VAE/Flow、Meta-learning、目标检测。

**2019** 6 篇

语言模型、泛化、sim2real、Meta-RL、进化策略、自监督。

**2020** 5 篇

Transformer、课程 RL、探索、NAS、开放域问答。

**2021** 6 篇

可控文本、毒性、对比学习、扩散、大模型训练、半监督。

**2022** 4 篇

主动学习、数据生成、视觉语言模型、NTK。

**2023** 5 篇

推理优化、Transformer v2、Prompt、Autonomous Agents、LLM 攻击。

**2024** 4 篇

高质量人类数据、视频扩散、幻觉、reward hacking。

**2025** 1 篇

test-time compute 与 thinking。

**2026** 2 篇

Scaling laws 与 harness engineering/self-improvement。

全站一共 52 篇正式文章；RSS 另含 FAQ，本笔记已排除 FAQ。

## 主题地图：52 篇文章应该怎么归类

### LLM、Agent 与对齐

2021-2026 的主线，从可控生成、毒性、Prompt Engineering，到 autonomous agents、幻觉、reward hacking、thinking、harness self-improvement。

PromptAgentAlignmentHarness

### Transformer 与大模型系统

从 Attention 到 Transformer family，再到 inference optimization、multi-GPU training、scaling laws，构成“模型结构 + 系统工程 + 规模规律”。

TransformerInferenceScaling

### 数据效率与表示学习

半监督、主动学习、数据生成、自监督、对比学习、高质量人类数据，回答“没有足够标注时怎么学习”和“什么数据真正有价值”。

DataSSLContrastive

### 强化学习与搜索

Bandit、RL overview、Policy Gradient、课程学习、探索、Meta-RL、进化策略，为后续 reward hacking 与 agent optimization 提供基础。

RLExplorationEvolution

### 生成模型

GAN/WGAN、VAE、Flow、Diffusion、Video Diffusion，覆盖显式密度、隐变量、对抗训练、score/diffusion 到时序一致性。

GANVAEFlowDiffusion

### 视觉与多模态

目标检测四部曲、VLM、video generation，体现从传统视觉管线到视觉语言、多模态生成的迁移。

Object DetectionVLMVideo

## 建议学习路径

**路径 A**  
AI Agent / LLM 工程

  1. [Prompt Engineering](https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/)：理解如何不用改权重控制 LLM 行为。
  2. [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/)：建立 planning、memory、tool use 的基本框架。
  3. [Why We Think](https://lilianweng.github.io/posts/2025-05-01-thinking/)：理解 test-time compute 为什么提升推理。
  4. [Harness Engineering for Self-Improvement](https://lilianweng.github.io/posts/2026-07-04-harness/)：进入现代 agent runtime、evaluation、memory、self-improvement。

**路径 B**  
LLM 安全与可靠性

  1. [Reducing Toxicity in Language Models](https://lilianweng.github.io/posts/2021-03-21-lm-toxicity/)：先理解语言模型安全风险。
  2. [Adversarial Attacks on LLMs](https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/)：看 prompt/jailbreak 攻击面。
  3. [Extrinsic Hallucinations in LLMs](https://lilianweng.github.io/posts/2024-07-07-hallucination/)：看事实性和不知道时承认不知道。
  4. [Reward Hacking in Reinforcement Learning](https://lilianweng.github.io/posts/2024-11-28-reward-hacking/)：理解 autonomous use cases 的核心阻塞。

**路径 C**  
模型结构与规模

  1. [Attention? Attention!](https://lilianweng.github.io/posts/2018-06-24-attention/)：先建立 attention 概念。
  2. [The Transformer Family](https://lilianweng.github.io/posts/2020-04-07-the-transformer-family/) 与 [Version 2.0](https://lilianweng.github.io/posts/2023-01-27-the-transformer-family-v2/)：看架构演进。
  3. [How to Train Really Large Models on Many GPUs?](https://lilianweng.github.io/posts/2021-09-25-train-large/)：补训练系统。
  4. [Large Transformer Model Inference Optimization](https://lilianweng.github.io/posts/2023-01-10-inference-optimization/)：补推理系统。
  5. [Scaling Laws, Carefully](https://lilianweng.github.io/posts/2026-06-24-scaling-laws/)：理解规模、数据、计算之间的规律。

**路径 D**  
生成模型与多模态

  1. [From GAN to WGAN](https://lilianweng.github.io/posts/2017-08-20-gan/)、[From Autoencoder to Beta-VAE](https://lilianweng.github.io/posts/2018-08-12-vae/)、[Flow-based Deep Generative Models](https://lilianweng.github.io/posts/2018-10-13-flow-models/)：三类经典生成范式。
  2. [What are Diffusion Models?](https://lilianweng.github.io/posts/2021-07-11-diffusion-models/)：进入现代 diffusion。
  3. [Diffusion Models for Video Generation](https://lilianweng.github.io/posts/2024-04-12-diffusion-video/)：理解视频生成的时序一致性与数据问题。
  4. [Generalized Visual Language Models](https://lilianweng.github.io/posts/2022-06-09-vlm/)：补视觉语言模型。

## 最值得优先读的 12 篇

优先级| 文章| 为什么先读  
---|---|---  
1| [Harness Engineering for Self-Improvement](https://lilianweng.github.io/posts/2026-07-04-harness/)| 直接对应现代 agent runtime、自我改进、可观测性和评测。  
2| [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/)| Agent 基础框架：planning、memory、tool use。  
3| [Why We Think](https://lilianweng.github.io/posts/2025-05-01-thinking/)| test-time compute 与 reasoning 的系统综述。  
4| [Reward Hacking in Reinforcement Learning](https://lilianweng.github.io/posts/2024-11-28-reward-hacking/)| 解释为什么更强 agent 必须重视评测和奖励设计。  
5| [Extrinsic Hallucinations in LLMs](https://lilianweng.github.io/posts/2024-07-07-hallucination/)| 事实性、证据和“不知道”能力是 LLM 产品化核心。  
6| [Prompt Engineering](https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/)| 从 prompt 走向 context/harness 的起点。  
7| [Scaling Laws, Carefully](https://lilianweng.github.io/posts/2026-06-24-scaling-laws/)| 理解大模型能力提升背后的计算、数据、规模规律。  
8| [The Transformer Family](https://lilianweng.github.io/posts/2020-04-07-the-transformer-family/)| LLM 架构背景的核心入口。  
9| [Large Transformer Model Inference Optimization](https://lilianweng.github.io/posts/2023-01-10-inference-optimization/)| LLM 部署和性能工程的基础。  
10| [Thinking about High-Quality Human Data](https://lilianweng.github.io/posts/2024-02-05-human-data-quality/)| 训练和对齐都离不开高质量人类数据。  
11| [What are Diffusion Models?](https://lilianweng.github.io/posts/2021-07-11-diffusion-models/)| 生成模型主线中最重要的现代入口。  
12| [A (Long) Peek into Reinforcement Learning](https://lilianweng.github.io/posts/2018-02-19-rl-overview/)| 理解 RLHF、reward hacking、agent optimization 的基础。  
  
## 全量目录：52 篇正式文章

日期| 标题| 主题归类| 一句话定位  
---|---|---|---  
2026-07-04| [Harness Engineering for Self-Improvement](https://lilianweng.github.io/posts/2026-07-04-harness/)| LLM / Agent| 把自我改进落到 harness、workflow、memory、evaluation 和 observability。  
2026-06-24| [Scaling Laws, Carefully](https://lilianweng.github.io/posts/2026-06-24-scaling-laws/)| Scaling / Systems| 系统理解 compute、loss、model size、data size 的经验规律。  
2025-05-01| [Why We Think](https://lilianweng.github.io/posts/2025-05-01-thinking/)| Reasoning| 综述 test-time compute、CoT 和 thinking time 为什么有效。  
2024-11-28| [Reward Hacking in Reinforcement Learning](https://lilianweng.github.io/posts/2024-11-28-reward-hacking/)| Alignment / RL| 奖励函数不完美时，agent 如何学会钻漏洞。  
2024-07-07| [Extrinsic Hallucinations in LLMs](https://lilianweng.github.io/posts/2024-07-07-hallucination/)| Reliability| 聚焦不由上下文或世界知识支撑的事实性幻觉。  
2024-04-12| [Diffusion Models for Video Generation](https://lilianweng.github.io/posts/2024-04-12-diffusion-video/)| Generative / Video| 从图像 diffusion 走向视频生成的时序一致性问题。  
2024-02-05| [Thinking about High-Quality Human Data](https://lilianweng.github.io/posts/2024-02-05-human-data-quality/)| Data| 高质量人类标注和 RLHF 数据质量的工程本质。  
2023-10-25| [Adversarial Attacks on LLMs](https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/)| Safety| LLM jailbreak / adversarial attack 的攻击面和防御背景。  
2023-06-23| [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/)| Agent| Autonomous agent 的 planning、memory、tool use 总览。  
2023-03-15| [Prompt Engineering](https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/)| LLM| 不更新权重而控制 LLM 行为的经验科学。  
2023-01-27| [The Transformer Family Version 2.0](https://lilianweng.github.io/posts/2023-01-27-the-transformer-family-v2/)| Architecture| Transformer 架构改进的新版系统整理。  
2023-01-10| [Large Transformer Model Inference Optimization](https://lilianweng.github.io/posts/2023-01-10-inference-optimization/)| Systems| 大模型推理优化、蒸馏和部署效率。  
2022-09-08| [Some Math behind Neural Tangent Kernel](https://lilianweng.github.io/posts/2022-09-08-ntk/)| Theory| 从数学角度理解过参数化网络和 NTK。  
2022-06-09| [Generalized Visual Language Models](https://lilianweng.github.io/posts/2022-06-09-vlm/)| Multimodal| 图像到文本、多模态理解和视觉语言模型。  
2022-04-15| [Learning with not Enough Data Part 3: Data Generation](https://lilianweng.github.io/posts/2022-04-15-data-gen/)| Data Efficiency| 数据生成作为小数据学习策略。  
2022-02-20| [Learning with not Enough Data Part 2: Active Learning](https://lilianweng.github.io/posts/2022-02-20-active-learning/)| Data Efficiency| 主动学习如何选择最值得标注的样本。  
2021-12-05| [Learning with not Enough Data Part 1: Semi-Supervised Learning](https://lilianweng.github.io/posts/2021-12-05-semi-supervised/)| Data Efficiency| 半监督学习处理标注不足问题。  
2021-09-24| [How to Train Really Large Models on Many GPUs?](https://lilianweng.github.io/posts/2021-09-25-train-large/)| Systems| 大模型多 GPU 训练、并行和显存管理。  
2021-07-11| [What are Diffusion Models?](https://lilianweng.github.io/posts/2021-07-11-diffusion-models/)| Generative| Diffusion / score-based generative modeling 入门。  
2021-05-31| [Contrastive Representation Learning](https://lilianweng.github.io/posts/2021-05-31-contrastive/)| Representation| 相似样本靠近、不相似样本远离的表示学习范式。  
2021-03-21| [Reducing Toxicity in Language Models](https://lilianweng.github.io/posts/2021-03-21-lm-toxicity/)| Safety| 语言模型毒性来源、测量和缓解。  
2021-01-02| [Controllable Neural Text Generation](https://lilianweng.github.io/posts/2021-01-02-controllable-text-generation/)| NLP| 如何控制神经语言模型生成指定属性文本。  
2020-10-29| [How to Build an Open-Domain Question Answering System?](https://lilianweng.github.io/posts/2020-10-29-odqa/)| NLP / Retrieval| 开放域问答系统的检索、阅读和事实回答。  
2020-08-06| [Neural Architecture Search](https://lilianweng.github.io/posts/2020-08-06-nas/)| AutoML| 自动搜索神经网络结构。  
2020-06-07| [Exploration Strategies in Deep Reinforcement Learning](https://lilianweng.github.io/posts/2020-06-07-exploration-drl/)| RL| 深度强化学习里的探索策略。  
2020-04-07| [The Transformer Family](https://lilianweng.github.io/posts/2020-04-07-the-transformer-family/)| Architecture| Transformer 及其长上下文、效率改进。  
2020-01-29| [Curriculum for Reinforcement Learning](https://lilianweng.github.io/posts/2020-01-29-curriculum-rl/)| RL| 如何用课程让 RL 逐步学习复杂任务。  
2019-11-10| [Self-Supervised Representation Learning](https://lilianweng.github.io/posts/2019-11-10-self-supervised/)| Representation| 用自监督任务从无标注数据学习表示。  
2019-09-05| [Evolution Strategies](https://lilianweng.github.io/posts/2019-09-05-evolution-strategies/)| Optimization| 梯度下降之外的进化式优化。  
2019-06-23| [Meta Reinforcement Learning](https://lilianweng.github.io/posts/2019-06-23-meta-rl/)| RL / Meta-learning| 让 agent 学会快速适应新 RL 任务。  
2019-05-05| [Domain Randomization for Sim2Real Transfer](https://lilianweng.github.io/posts/2019-05-05-domain-randomization/)| Robotics| 通过随机化缩小仿真到现实的迁移差距。  
2019-03-14| [Are Deep Neural Networks Dramatically Overfitted?](https://lilianweng.github.io/posts/2019-03-14-overfit/)| Theory| 深网为什么过参数化却仍能泛化。  
2019-01-31| [Generalized Language Models](https://lilianweng.github.io/posts/2019-01-31-lm/)| NLP| 从词向量到上下文化语言模型。  
2018-12-27| [Object Detection Part 4: Fast Detection Models](https://lilianweng.github.io/posts/2018-12-27-object-recognition-part-4/)| Vision| SSD、RetinaNet、YOLO 等快速检测模型。  
2018-11-30| [Meta-Learning: Learning to Learn Fast](https://lilianweng.github.io/posts/2018-11-30-meta-learning/)| Meta-learning| 少样本快速学习的核心方法。  
2018-10-13| [Flow-based Deep Generative Models](https://lilianweng.github.io/posts/2018-10-13-flow-models/)| Generative| 显式概率密度建模的 flow family。  
2018-08-12| [From Autoencoder to Beta-VAE](https://lilianweng.github.io/posts/2018-08-12-vae/)| Generative| 从 autoencoder 到 VAE、disentanglement。  
2018-06-24| [Attention? Attention!](https://lilianweng.github.io/posts/2018-06-24-attention/)| Architecture| Attention 机制及其在 Transformer 前后的演进。  
2018-05-05| [Implementing Deep Reinforcement Learning Models with Tensorflow + OpenAI Gym](https://lilianweng.github.io/posts/2018-05-05-drl-implementation/)| RL| 经典深度 RL 模型的 TensorFlow/Gym 实现。  
2018-04-08| [Policy Gradient Algorithms](https://lilianweng.github.io/posts/2018-04-08-policy-gradient/)| RL| Policy gradient 及其现代变体。  
2018-02-19| [A (Long) Peek into Reinforcement Learning](https://lilianweng.github.io/posts/2018-02-19-rl-overview/)| RL| 强化学习基础概念和经典算法总览。  
2018-01-23| [The Multi-Armed Bandit Problem and Its Solutions](https://lilianweng.github.io/posts/2018-01-23-multi-armed-bandit/)| Bandit| exploration vs exploitation 的最小问题模型。  
2017-12-31| [Object Detection for Dummies Part 3: R-CNN Family](https://lilianweng.github.io/posts/2017-12-31-object-recognition-part-3/)| Vision| R-CNN、Fast/Faster R-CNN、Mask R-CNN。  
2017-12-15| [Object Detection for Dummies Part 2: CNN, DPM and Overfeat](https://lilianweng.github.io/posts/2017-12-15-object-recognition-part-2/)| Vision| CNN、DPM、Overfeat 等视觉检测前史。  
2017-10-29| [Object Detection for Dummies Part 1: Gradient Vector, HOG, and SS](https://lilianweng.github.io/posts/2017-10-29-object-recognition-part-1/)| Vision| 梯度向量、HOG、Selective Search。  
2017-10-15| [Learning Word Embedding](https://lilianweng.github.io/posts/2017-10-15-word-embedding/)| NLP| 词向量学习的基础方法。  
2017-09-28| [Anatomize Deep Learning with Information Theory](https://lilianweng.github.io/posts/2017-09-28-information-bottleneck/)| Theory| 信息瓶颈视角下的深度学习。  
2017-08-20| [From GAN to WGAN](https://lilianweng.github.io/posts/2017-08-20-gan/)| Generative| GAN 训练难点与 Wasserstein GAN。  
2017-08-01| [How to Explain the Prediction of a Machine Learning Model?](https://lilianweng.github.io/posts/2017-08-01-interpretation/)| Interpretability| 模型解释性方法总览。  
2017-07-22| [Predict Stock Prices Using RNN: Part 2](https://lilianweng.github.io/posts/2017-07-22-stock-rnn-part-2/)| Tutorial| RNN 股票预测的多股票扩展。  
2017-07-08| [Predict Stock Prices Using RNN: Part 1](https://lilianweng.github.io/posts/2017-07-08-stock-rnn-part-1/)| Tutorial| TensorFlow RNN 股票预测入门。  
2017-06-21| [An Overview of Deep Learning for Curious People](https://lilianweng.github.io/posts/2017-06-21-overview/)| Foundation| 面向好奇读者的深度学习总览。  
  
## 我的理解：这套博客最值得学什么

第一，Lilian Weng 的写作方式本身是一种研究笔记范式：不是只讲直觉，也不是只堆公式，而是把问题背景、代表论文、方法谱系、关键图和局限放在同一个框架里。这很适合做“进入一个领域前的地图”。

第二，全站最强的连续主线是“从模型能力到系统能力”。早期文章解释模型结构和学习算法，中期文章解释数据、训练、推理和表示，近期文章解释 LLM/agent 的运行时、评测和风险。这个迁移本身反映了 AI 工程重心的迁移：单点模型不够，系统边界、数据质量、评测和人类监督越来越重要。

第三，如果目标是服务当前 AI coding/agent 工作，不建议从 2017 顺序读起。更高效的读法是先读 Prompt、Agent、Thinking、Harness、Reward Hacking、Hallucination，再按缺口补 Transformer、Scaling、Data 和 RL 基础。

记录时间：2026-07-28 | 笔记路径：doc-notes/ai-coding/2026-07/notes/lilian-weng-lillog-learning-map.html | 数据来源：Lil'Log homepage, archive, RSS index
