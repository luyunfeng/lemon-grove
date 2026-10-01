# Lilian Weng Harness Engineering for Self-Improvement 阅读笔记

AI Coding Reading Note

# Harness Engineering for Self-Improvement：自我改进不只靠模型，更靠运行时系统

来源Lil'Log

作者Lilian Weng

时间2026-07-04

原文[lilianweng.github.io](https://lilianweng.github.io/posts/2026-07-04-harness/)

核心命题 Harness 模式 优化对象 论文地图 挑战 评测基准 我的理解

**核心观点：** 近中期的递归自我改进不太可能先表现为模型直接重写自己的权重，而更可能表现为模型改进围绕自己的 deployment system，也就是 harness：工作流、工具、权限、上下文、持久记忆、评测和可观测性。

文章把 harness 从“更复杂的 prompt”提升为“运行时软件系统”。它决定模型如何观察、行动、记忆、检查结果、调用子 agent、管理文件，以及如何从失败中形成下一轮改进。

## 一句话读懂 Harness

Harness 是围绕基础模型的一整套运行时系统：它编排模型如何思考和规划、如何调用工具和行动、如何感知并管理上下文、如何保存产物、如何评估结果。 

### 它不只是 Prompt

早期 agent 框架常被概括为 LLM + memory + tools + planning + action。Lilian 的文章强调，现代 harness 还包括 loop engineering、evaluation、permission control、persistent state management。

### 它更像操作系统

好的 harness 要把复杂逻辑封装在内部，对模型暴露简单、稳定、可泛化的接口。工具协议、配置、上下文格式和权限边界会逐步标准化。

## 三类基础设计模式

### 1\. Workflow Automation

让模型在明确循环中计划、执行、观察/测试、改进，再继续执行，直到目标完成。Karpathy 的 autoresearch 是典型例子。

planexecutetestimprove

### 2\. File System as Memory

长程任务不能把所有轨迹塞进上下文。实验日志、代码 diff、论文摘要、错误轨迹和过去 rollout 应保存在文件里，供模型按需读取。

artifactslogsstate

### 3\. Sub-agent and Backend Jobs

主 agent 可以并行探索多个假设、启动后台实验、委派隔离子任务，并需要一个小型进程管理器来启动、检查、取消和合并结果。

parallelinspectablemerge

这里最关键的是“可检查”。子 agent 输出如果只存在聊天上下文，很快就会隐藏或丢失；如果落在文件、日志、状态记录里，系统中断后仍可恢复。 

## 编码 Agent 的 Harness 已经趋于稳定

能力组| 典型接口| 为什么重要  
---|---|---  
文件系统| `glob`, `grep`, `ls`, read/edit/write/apply_patch| 让模型像工程师一样定位、阅读和修改代码。  
Shell 执行| `bash`, PowerShell| 运行测试、格式化、构建、诊断系统状态。  
开发 I/O| LSP, git status, git diff, git commit| 让改动可审计，可回滚，可纳入工程流程。  
外部上下文| MCP tools, skills, web search, browser tools| 把私有文档、运行系统和外部资料纳入任务。  
产物和后台任务| HTML/image artifacts, cron/backend jobs| 支持长程任务、报告、可视化和持续执行。  
Agent 委派| spawn/resume/wait/close/interrupt agent| 把独立探索并行化，同时保持父 agent 的整合责任。  
  
## Harness 优化对象的递进

**Instruction Prompts** 最早优化提示词和任务说明

**Structured Context** 整理上下文，而不是简单拼接历史

**Workflow** 优化 agent 循环、分支、评测和回退

**Harness Code** 直接修改运行时系统的代码与组件

**Optimizer Code** 优化“如何优化 harness”的机制

**Model Weights** 进一步和训练、持续学习结合

**RSI Loop** 系统改进产生更强后继系统

Lilian 的判断是：随着模型更强，优化对象会从 prompt 走向更复杂、更通用的程序对象。Harness 的本质是代码，因为代码能描述 prompts、tool calls、subagents、control flow、memory 和 evaluation 如何组合。 

## Context Engineering：从长提示词到可演化 Playbook

### ACE：结构化上下文日志

Agentic Context Engineering 把上下文看成 evolving playbook，而不是越来越长的 prompt。它包含三类角色：

  * **Generator** ：参考条目生成任务轨迹。
  * **Reflector** ：从成功/失败轨迹中提炼 insight。
  * **Curator** ：以 itemized bullets 更新结构化上下文。

### MCE：机制与内容分离

Meta Context Engineering 把“如何管理上下文”的机制和“上下文里有什么”的内容拆开，外层搜索 skill，内层优化 task context。

关键变化是：上下文函数可以落成一个文件目录，包含 `skill.md`、静态知识、动态 rollout 数据和工具化操作。

ACE 仍有手写规则，MCE 则把规则本身也纳入优化。这个方向很像把“记忆管理”从经验活变成可评测、可演化的软件对象。 

## Workflow Design：从专家手工流程到搜索问题

### 专家手工流程

**AI Scientist** 用 pipeline 组织 idea generation、code、experiment、analysis、manuscript、peer review。

**ScientistOne** 把 verifiability 放在中心，每个 citation、number、method、conclusion 都要追踪证据。

### 角色化数据生成

**Autodata** 让 challenger、weak solver、strong solver、verifier/judge 协同生成“强模型能解、弱模型不能解”的合适难度数据。

### 自动搜索流程

**ADAS** 让 meta-agent 设计新的 agentic workflows。

**AFlow** 把 workflow 表示成图，用 MCTS 在候选流程树里选择、扩展、评估、保留改进。

## 自我改进 Harness 的论文地图

方向| 代表系统| 核心机制| 读后抓手  
---|---|---|---  
递归优化器 | STOP | 不是优化答案，而是优化 improver 本身；强模型能发现遗传算法、分解、bandit、退火、beam/tree search 等策略。 | 递归结构不够，底座模型必须足够强；弱模型可能越改越差。  
能力拆分 | Harness Updating vs Harness Benefit | 区分“会写 harness edits”和“会利用更新后的 harness”。 | 小模型可能会提出类似强模型的改动，但是否真正受益取决于长程指令跟随、工具调用和 skill 使用能力。  
提议-验证-接受 | Self-Harness | weakness mining、bounded harness proposal、proposal validation。 | 只接受 held-in 修复且 held-out 无回归的候选；权限和安全层必须在循环外。  
可观测性驱动 | AHE | component observability、experience observability、decision observability。 | 每个 edit 都要绑定证据、根因、目标修复和下一轮可验证预测。  
进化搜索 | Promptbreeder, GEPA, AlphaEvolve, ShinkaEvolve | 在可评测搜索空间中保留高 fitness 解，并用反思、meta-prompt 或新颖性机制提高采样效率。 | 适合自动可评测任务；弱在评估慢、模糊、启发式强的领域。  
开放式 agent 演化 | Darwin Godel Machine, Hyperagents | 让 agent 修改自己的 harness-code repository，评测通过后加入候选池。 | 是固定模型下的 harness 演化，不等于模型权重自我改写。  
权重联合优化 | SIA, Continual Harness | 同时考虑 harness 更新和模型参数/策略更新。 | 方向有价值，但证据还早；训练稳定性、Goodhart、实验混杂仍是大问题。  
  
## Self-Harness 与 AHE 的关键区别

### Self-Harness：先找弱点，再做有界改动

  1. 对当前 harness 跑任务并收集 traces。
  2. 把失败聚类成 verifier-grounded failure patterns。
  3. 给 proposer 有界上下文：可编辑面、失败模式、要保留的通过行为、历史失败 edit。
  4. 用 held-in 和 held-out 回归测试决定是否接受。

### AHE：把每次改动变成可证伪主张

  1. 每个可编辑组件都在文件系统中有表示。
  2. 大量原始轨迹先变成 per-task root cause report，再汇总成 benchmark overview。
  3. 每个 edit 都要写 manifesto：证据名、根因、目标修复、预期收益、回归风险。
  4. runs、tracer、verifier、LLM config 只读，避免通过破坏评测来刷分。

## 文章列出的七个未来挑战

### 1\. 弱且模糊的评测器

研究品味、长期科学价值、真实业务价值都不容易用快速 verifier 衡量。

### 2\. 上下文与记忆生命周期

随着 agent 更独立，memory 会持续增长；context engineering 可能会成为智能本身的一部分。

### 3\. 负结果

研究激励偏向成功故事，而 self-improvement 系统必须能保存失败、承认失败、从失败中缩小搜索空间。

### 4\. 多样性塌缩

进化和 RL 循环会利用已知高 reward 模式，开放式研究需要保持探索。

### 5\. Reward Hacking

如果奖励来自单测、judge model 或 benchmark，agent 可能学会针对奖励源的作弊策略。

### 6\. 长期成功

编码 agent 短期完成任务不等于维护大型仓库的长期健康；维护性、所有权、迁移成本很难被短期 sandbox 奖励捕获。

### 7\. 人类角色

人不应从循环中消失，而应上移到更合适的抽象层，在关键决策点提供监督和方向。

文章对“AI Scientist 写论文”保持谨慎：论文生产不等于科学发现。系统可以写出像样的 manuscript，但仍可能有伪造引用、实现漂移或薄弱实验。 

## Trehan & Chopra 观察到的研究失败模式

失败模式| 含义| 对 Harness 的启发  
---|---|---  
训练数据默认偏置| 使用旧库、过时命令、默认格式或未被当前仓库/数据支撑的假设。| 必须做环境探查和证据绑定，不能凭常识模板推进。  
实现漂移| 当实现变复杂，模型会滑向更常见、更简单但偏离原方法的方案。| 需要 spec、trace、关键假设和中间验收。  
记忆退化| 长程项目会丢关键细节。| 必须把日志、决策、失败和产物持久化。  
过度乐观| 实验失败或信号噪声很大时仍宣布成功。| 需要负结果记录、统计审查和反证机制。  
领域智能不足| 缺少 tacit craft knowledge，不能判断复杂度、合理结果和重要 baseline。| 需要人类专家在高抽象层把关。  
科学品味弱| 实验能跑，但没有回答正确问题。| 不能只优化可执行性，还要优化问题选择和证据质量。  
  
## 附录里的评测基准

### PaperBench

复现 20 篇 ICML 2024 Spotlight/Oral 论文，拆成 8,316 个可评分 rubric。强模型仍未超过 ML PhD。

### CORE-Bench

基于 90 篇科学论文的 270 个计算可复现任务，覆盖计算机、社会科学、医学。

### ScienceAgentBench

从 44 篇同行评审论文提取 102 个数据驱动科学发现任务，覆盖数学、化学、生物、地理。

### RE-Bench

7 个真实 ML research-engineering 环境，对比 frontier agents 与人类专家。短预算下 agent 强，长预算下人类回报更好。

### MLE-bench

75 个 Kaggle 离线竞赛，测试数据准备、训练、实验和提交预测。

### KernelBench

250 个 PyTorch 任务，评估模型写出的 GPU kernel 是否正确且快于 baseline。

## 我的理解

这篇文章最重要的转向，是把“AI 自我改进”从神秘的模型自我重写，拉回到工程上可观察、可验证、可迭代的运行时系统。短期真正能落地的 RSI 不是模型自己改权重，而是模型在一个受控环境里改进 prompt、context、workflow、tools、memory、skills、permissions 和 evaluation。

对 AI coding 来说，harness 的价值很具体：它决定 agent 是否会先读代码再改、是否会记录失败、是否会把任务拆给子 agent、是否会跑测试、是否会尊重权限、是否会在上下文爆炸时转向文件系统。这些行为看似“流程”，实际直接决定任务质量。

我会用三个问题判断一个 harness 是否成熟：第一，它是否把失败变成可检索的证据；第二，它是否把每次改动变成可证伪的假设；第三，它是否把 verifier、权限和人类审查放在自我演化循环之外。缺任何一个，系统都容易从自我改进滑向自我确认。

记录时间：2026-07-28 | 笔记路径：doc-notes/ai-coding/2026-07/notes/lilian-weng-harness-engineering-self-improvement.html | 原文：Harness Engineering for Self-Improvement
