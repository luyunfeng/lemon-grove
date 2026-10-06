# 调研来源与采用的原则

本技能独立实现，不直接移植第三方代码。以下公开资料用于了解布局、校验和图型组织方法；并不证明本技能已通过验收。

- [excalidraw](https://raw.githubusercontent.com/iruochen/excalidraw-diagram-skill/main/SKILL.md)：语义输入与几何输出分离；同输入重复生成应稳定。；字号、内边距、节点间距和路由净距统一为参数。 许可信息：MIT。
- [mermaid](https://raw.githubusercontent.com/anyforge/anymermaid/main/skills/anymermaid-skill/SKILL.md)：图型路由表与渲染环境清单独立维护。；语法成功和视觉通过分别记录。 许可信息：Apache-2.0。
- [drawio-ir](https://raw.githubusercontent.com/Agents365-ai/drawio-skill/main/skills/drawio-skill/SKILL.md)：一份语义模型投影为多个受众视图。；视觉评审与几何证据交叉校验。 许可信息：MIT。
- [drawio-lint](https://raw.githubusercontent.com/Sunwood-ai-labs/draw-io-skill/main/SKILL.md)：覆盖率属于验证结果；不能把零解析边当作零缺陷。；建立能稳定重现视觉缺陷的小型样例。 许可信息：MIT。
- [lark](https://raw.githubusercontent.com/larksuite/cli/main/skills/lark-whiteboard/SKILL.md)：先选择图型和布局，再选择经过验证的传输格式。；转换后的预览应成为飞书交付验收对象。 许可信息：MIT。

白板适配以实际转换与服务端回读为准；本地SVG、可编辑节点、动态端口绑定是不同验证对象。
