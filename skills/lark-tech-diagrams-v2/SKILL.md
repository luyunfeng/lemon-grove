---
name: lark-tech-diagrams-v2
description: 默认的技术绘图风格，将逻辑画成与内置demo一致的架构、泳道、时序、ER等16类技术图。提供语义配色、图型布局、确定性SVG和质量检查；交付飞书时调用lark-whiteboard/lark-doc或官方CLI，不自带文档、上传或授权实现。
metadata:
  version: "2.3.0"
---

# 技术图：稳定复现 demo

用户只需给逻辑。参考图、色板、排版器、字体和输入契约都在包内，不需要旧聊天、个人记忆或历史文档。先读[风格契约](references/style-contract.md)；按[图型选择](references/diagram-types.md)选型，只读catalog中该图型的输入模板、SVG和PNG。

## 绘图

1. 按[输入契约](references/input-contract.md)把需求写成JSON。模板是虚构业务，替换实体、关系、条件、图例，保留所选图型语法。不能从模板补出用户没说的技术事实。
2. 用包内入口生成：`python3 <技能目录>/scripts/quick_draw.py render --spec <任务目录>/model.json --out <任务目录>/output`。输出SVG、本地PNG、布局和检查报告。脚本按包位置定位资源，不依赖当前目录；输出必须在包外的新目录。
3. 实际查看PNG，逐条核对需求与参考图的视觉规则。先修语义、遮挡和文字溢出，再调非阻塞间距；不改全局色板或缩字来掩盖问题。保存失败尝试。`passed`只表示机器检查通过，不等于视觉或飞书验收完成。

`quick_draw.py prepare --type <图型> --out <model.json>` 可复制底稿。依赖和无预览工具时的处理见[运行环境](references/runtime.md)。普通本地画图不需要飞书、Node、登录或网络。

## 交付与工具边界

用户要求飞书时，按[工具交接](references/tool-handoff.md)调用可用的lark-whiteboard；新建/定位文档交给lark-doc，认证交给lark-shared。交接的是已经画好的SVG，平台工具负责转换、上传、导出及回读。使用当前用户的身份/目标约定，不从示例继承账号、应用或目录。完成目标端预览与文字核对后再交付工具返回的完整链接；本地链接直接使用result.json返回的绝对路径，不猜测或保留示例占位链接。

工具缺失时保留已完成的SVG/PNG，明确缺少哪个交付能力；不得宣称已经上传，也不把未指定的他人账号当默认值。不要把既有SVG重新生成成另一种图来上传，这会丢失demo风格。

## 改进

普通请求只画当前图。用户要求优化Skill时，按[迭代验证](references/self-evolution.md)冻结候选、独立测试与看图、修复、回归和择优；评分与demo复现分开验证。包只保存可复用绘图资源，轮次记录、云端收据、个人配置留在任务工作区。
