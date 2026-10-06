# 研究依据与取舍

研究日期：2026-10-02。以下是设计参考，不是已验证的检测准确率。本技能的指令与评分表独立编写，没有整份复制上游技能。

| 资料 | 采用的思路 | 保留的边界 |
|---|---|---|
| [blader/humanizer](https://github.com/blader/humanizer/blob/main/SKILL.md) | 从结构与信息价值检查模板表达，改后复核信息 | 不把列表或加粗一概当问题；不加入原文没有的个人反应 |
| [syw2039/humanizer-zh](https://github.com/syw2039/humanizer-zh/blob/main/SKILL.md) | 中文表达、文体匹配、限定条件和事实保护 | 模糊但有实质含义的主张不能随意删除 |
| [0xtresser/cn-humanizer](https://github.com/0xtresser/cn-humanizer/blob/main/SKILL.md) | 中文抽象黑话、翻译腔、模板连接的候选现象 | 不采用“单词是铁证”、固定句长统计阈值和为了人味补写事实的做法 |
| [中文技术文档写作风格指南](https://github.com/ruanyf/document-style-guide/blob/master/docs/paragraph.md) | 一个表达单元承载一个主题，支撑内容贴近中心句 | 不把视觉行数当硬限制；本技能按用户偏好默认分点 |
| [HC3 官方仓库](https://github.com/Hello-SimpleAI/chatgpt-comparison-detection) 与 [论文](https://arxiv.org/abs/2301.07597) | 区分中文真人和模型表达的观察语料；提供人类与 ChatGPT 的同题回答 | 历史问答数据不能直接代表当前模型；人类答案不自动等于优质答案 |
| [HC3-Chinese 数据集](https://huggingface.co/datasets/Hello-SimpleAI/HC3-Chinese) | 检查实际中文表达，而不是只翻译英文禁词表 | 原始同题回答不保证语义一致，不能当作改写金标准 |

## 本技能的设计判断

- “AI 味”是编辑者对可见文风问题的简称，不是来源鉴定。用具体缺陷来评，不用某个词推断作者身份。
- 分点符合此用户的阅读偏好。要控制的是没有关系的拆句、重复标题和机械凑数。
- 自然度容易与删减冲突，因此先验证语义，再比较逻辑和文风。
- 结构重排也会改变意思：条件的作用范围、步骤顺序、方案的适用边界必须一起移动。
- 评分使用有锚点的主观量表。未经人类盲评，不能宣称“完美”或给出检测准确率。

上游网页会变化；本文件记录的是研究时的取舍。HC3 的中文语料用于定性观察，本包不附语料原文或历史评测记录。重新验证当前版本时，使用 README 中的检查方法，并记录实际输入、输出与问题；引用或再分发语料时按对应子集的许可处理。
