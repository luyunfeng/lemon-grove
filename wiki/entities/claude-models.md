---
title: Claude 模型家族（以 Opus 4.8 / Fable 5 为例）
type: entity
tags: [llm-models, evaluation]
entities: [claude-models]
---

# Claude 模型家族（以 Opus 4.8 / Fable 5 为例）

## 它是什么

Anthropic 的大模型家族，按能力和价格分档：Haiku（快、便宜）、Sonnet（日常主力）、Opus（最强、最贵），以及新一代 Claude 5 系列。本页把 Opus 4.8 和 Fable 5 这一代当作**读懂一次模型发布**的案例：发布里哪些是能力，哪些是产品功能，哪些数字能比、哪些不能比，哪些只是新闻层面的定位。

## 核心机制

### 1. 分档与路由

- **Haiku**：重复性任务、多 Agent 里的 worker、格式化、摘要；Claude Code 内置的 Explore 子代理和 `/goal` 的评估器默认用它。
- **Sonnet**：约九成的日常编码。
- **Opus**：架构决策、安全关键代码、跨文件重构，以及便宜模型第一次失败后的升级。
- 价格上 Haiku 与 Opus 差约 5 倍，Sonnet 与 Opus 只差约 1.67 倍，所以「Haiku 打杂 + Opus 攻坚」的组合往往比「Sonnet + Opus」更省。

### 2. Opus 4.8：一次发布里的几类信息

**行为变化（最值得看，基准里看不出来）**

- 更愿意标注不确定性、更少无根据的断言：让代码缺陷被忽视的概率比前代降低约 4 倍。对代码生成和审查来说，「不装懂」比「看起来很强」更安全。
- 失对齐行为率（欺骗、配合滥用等）明显低于前代。

**产品能力（属于 harness，不属于模型本身）**

- **Effort Control** 四档：Low（快、省额度）、Default（High，质量与体验的平衡点）、Extra（xhigh，适合难题和长时间异步工作流）、Max（投入更多 token 求最好结果）。
- **Dynamic Workflows**（Claude Code 研究预览）：由模型写 JavaScript 编排脚本，在后台调度数十到数百个子代理，中间结果留在脚本变量里，不占主上下文。
- **Messages API** 允许在 messages 数组中途插入 system 条目：代理运行时可以更新权限、token 预算或环境信息，而不破坏 prompt cache，也不必借 user turn 传递。

**价格**

| 模式 | 输入（每百万 token） | 输出（每百万 token） |
|---|---|---|
| Standard | $5 | $25 |
| Fast（约 2.5 倍速度） | $10 | $50 |

Standard 与前代持平；fast mode 比前代便宜 3 倍。

**基准（要带着口径读）**

- 亮点：Online-Mind2Web（浏览器代理）84%；法律代理基准首次突破 10% 的全通过标准；Databricks Genie 代理场景的 token 成本比前代低 61%。
- 口径陷阱：Terminal-Bench 2.1 用的是 Terminus-2 公共框架，而对比对象 GPT-5.5 的 83.4% 用的是 Codex CLI 框架；OSWorld-Verified 更新了评测方法，连前代 Opus 4.7 的分数都被改成 82.3%。**不同 harness、不同评测版本的分数不能直接横比。**

### 3. Fable 5：新一代的公开版本

- Claude 5 系列首个公开的通用模型，出自内部代号 Mythos 的模型系列，是经过安全对齐与能力裁剪的「de-fanged」版本；更原始的 Mythos 5 保留在内部或受限渠道。
- 渠道：Claude API、Claude Platform on AWS、Amazon Bedrock、Google Vertex AI、Microsoft Foundry。付费订阅用户只有很短的免费试用窗口，之后要额外付费。
- 这类发布速览只有渠道和定位，**没有基准数据**；「Opus 4.8 与 Fable 5 高低搭配」属于新闻层面的定位，要靠自己的评测验证。

## 怎么用

读一次模型发布，按这个顺序过：

1. **先分清三类信息**：模型行为（诚实性、工具调用、指令遵循）、产品功能（Effort、工作流、API 变化）、价格。产品功能往往换个模型也能用，不要算到模型头上。
2. **基准看口径**：用的什么 harness、评测是否改过版本、对比对象是否同口径。头部模型之间差一两个百分点更像噪声。
3. **写清评测对象**：发布版能力 ≠ 内部最强能力（Fable 5 就是裁剪后的公开版），记录结论时写到具体型号和档位。
4. **按任务分配模型**：强模型做复杂设计、跨文件重构、安全判断；便宜模型或低 Effort 档做格式化、机械替换、摘要。跑大规模并行前先确认每个阶段用的是哪个模型。
5. **落到自己的任务上**：用公开榜单缩小候选，再在自己的任务集上做带盲评的小规模对照。
