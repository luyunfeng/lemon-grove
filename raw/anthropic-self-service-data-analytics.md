# Anthropic 如何用 Claude 实现自助式数据分析

On this page

TL;DR 核心问题 技术栈 数据基础 可信源 Skills 验证 关键数据 关键教训 如何开始

Research & Learning · Anthropic Engineering

# Anthropic 如何用 Claude 实现自助式数据分析

来源：[Anthropic Blog](https://claude.com/blog/how-anthropic-enables-self-service-data-analytics-with-claude) · 2026-06-03 · 作者：Chen Chang, Clement Peng, Justin Leder, Johanne Jiao, Josh Cherry 

**TL;DR** — Anthropic 用 Claude Code 构建了一套 Agentic 数据分析系统，使 **95% 的业务分析查询实现自动化** ，准确率达到 ~95%。核心洞察：**"Data is not software"** — LLM 的创造力对编程有帮助，但对数据分析是伤害，因为数据分析往往只有一个正确答案、一个正确数据源。解决方案围绕四层栈展开：数据基础 → 可信源 → Skills → 验证，其中 **Semantic Layer（语义层）和 Skill 维护** 是决定性因素。 

## 核心问题：Data is not software

Anthropic 的 Data Science 团队发现，让 LLM 做数据分析与写代码有本质区别：

  * **编程** ：有多种正确实现方式，LLM 的创造力是优势
  * **数据分析** ：通常只有一个正确答案、一个正确的数据源，LLM 的"幻觉"会直接产生错误结论

⚠

核心瓶颈不是"让 Agent 访问更多信息"，而是"让 Agent 把用户问题映射到数据模型中的具体实体，并知道正确的使用方式"。

### 三大失败模式

Failure Mode 1

#### 概念 ↔ 实体歧义（Concept <> entity ambiguity）

数据模型中有数百个可用字段，Agent 无法确定用户说的"活跃用户"到底对应哪个字段、哪个表。

Failure Mode 2

#### 数据陈旧（Data staleness）

数据资产和 Agent 知识会过时，开始返回"看起来合理但 subtly wrong"的答案。准确率从上线时的 ~95% 在一个月内 drift 到 ~65%。

Failure Mode 3

#### 检索失败（Retrieval failure）

正确的信息确实在数据模型中，但 Agent 就是找不到。实验发现：给 Agent 原始检索访问数千条历史查询，准确率提升不到 1 个百分点。

## Agentic 数据分析技术栈

### 1\. 数据基础（Data Foundations）

  * **创建 canonical datasets** — 精心策划少量"单一事实来源"数据集，而非让 Agent 在数百张表中选择
  * **通过工具、CI 和强制要求执行标准** — 数据代码统一放在单一仓库，受 CI 检查约束
  * **将元数据视为一等产品** — 字段注释、表说明、业务定义必须完整且可检索

### 2\. 可信源（Sources of Truth）— 按信任度降序

1st

**Semantic Layer（语义层）** — 结构性要求 Agent 优先使用。包含指标定义、维度映射、聚合规则。实验发现：用 LLM 自动生成指标定义是 net-negative（净负面）。

2nd

**血缘与转换图谱（Lineage & transformation graph）** — 将"我不知道这个指标"转化为"我知道该从哪个受治理的模型聚合"。

3rd

**查询语料（Query corpus）** — 历史查询记录。但实验显示：给 Agent 原始检索访问数千条 prior queries，准确率提升不到 1 个百分点。瓶颈不是"访问历史工作"，而是"结构"。

4th

**业务上下文（Business context）** — 公司知识图谱：索引文档、路线图、决策日志、组织架构。

### 3\. Skills — 决定性因素

没有 Skills 时，准确率"在评估中不超过 21%"。添加 Skills 后，"聚合准确率持续高于 95%，某些领域经常达到 99%"。

Skill 设计要点

  * **Knowledge skill** ：作为顶层路由，缩小搜索空间
  * **Unbook skill** ：编码"资深分析师会遵循的流程"，含对抗性审查
  * **为 LLM 检索编写参考文档** ：不是给人读的，是给 LLM 检索用的
  * **将 Skill 维护视为一等公民** ：与转换模型同仓，~90% 的数据模型 PR 现在包含 Skill 变更
  * **跨所有界面保持一致体验**

Skill 文件骨架结构

  * 调用条件和越界决策
  * 查询执行优先级：托管连接 → CLI 回退 → 停止
  * **Semantic Layer（ REQUIRED 第一步）** ：强制工作流 + "预反驳借口"
  * 日期窗口和时区约定
  * Part 1: MUST KNOW — 红旗、升级规则、澄清步骤、业务上下文、实体消歧、数据完整性要求
  * Part 2: HOW TO DO — 技术执行、分析最佳实践、强制对抗性 SQL 审查、来源页脚格式
  * Part 3: DATA REFERENCES — 按领域导航知识库、故障排除指南、字段命名陷阱

### 4\. 验证（Validation）

#### 离线评估（Offline evals）

  * **Dashboard-based evals** \+ **Long tail evals**
  * **锚定 ground truth** 使其无法漂移
  * **像存储遥测一样存储结果** ，而不是像测试日志
  * **按领域控制发布门槛** （~90% 阈值）
  * **离线评估准确率应接近 100%** — 上线后才会降到 ~95%

#### 消融实验关键发现

🔬

给 Agent grep 访问"数千个文件"，准确率提升"不到 1 个百分点"。结论：**瓶颈不是访问历史工作，而是结构。**

#### 在线验证（Online validation）

方法| 效果| 成本  
---|---|---  
对抗性审查（Adversarial review） | 准确率 +6% | Token +32%，延迟 +72%  
来源页脚（Provenance footer） | 标注来源层级、新鲜度、负责人 | 低  
被动监控（Passive monitoring） | 监控语义层解析率和修正语言 | 低  
主动修正收集（Active correction harvesting） | 定时 Agent 扫描利益相关者频道，起草修复，开 PR | 中  
  
⚠

**未解决的问题** ："静默失败"（silent failures）— 答案错了，但看起来合理。用户可能永远不会发现。

## 关键数据一览

95%

业务查询自动化

通过 Claude 完成

~95%

聚合准确率

含 Skills 后

<21%

无 Skills 准确率

基线评估

~99%

特定领域峰值

成熟领域

## 关键教训

  1. **数据不是软件** — 不要照搬代码生成的思路做数据分析
  2. **Semantic Layer 是结构性必需** — 不是可选优化，是核心基础设施
  3. **Skill 维护 = 工程工作** — 必须像维护代码一样维护 Skill，与数据模型同仓、同 CI
  4. **消融实验揭示真相** — "给更多上下文"不一定有用，关键是结构
  5. **离线评估应接近 100%** — 上线后自然衰减到 ~95%，如果离线只有 95%，上线后会更低
  6. **对抗性审查有效但昂贵** — +6% 准确率，但 +32% token、+72% 延迟
  7. **静默失败是未解难题** — 最危险的错误是看起来对的错误

## 如何开始：五个对齐问题

在构建 Agentic 数据分析系统前，团队应先对齐这五个问题：

  1. "今天 vs 未来，正确答案有多重要？"
  2. "你预计业务复杂度会如何变化？"
  3. "目标受众的技术水平如何？"
  4. "你愿意为提升准确率付出多少成本？"
  5. "你对访问控制和内部数据隐私的舒适度如何？"
