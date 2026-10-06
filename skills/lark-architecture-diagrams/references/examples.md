# 图型示例

用户已确认以下视觉基线。v1.1.0 优先采用最新记忆读写泳道图呈现较丰富的职责交接、条件分支与回路；基础泳道、ER 和交互样例继续适用。按新任务重新组织业务对象，不复制参考图的固定坐标或事实结论。

| 图型 | SVG | 结构 | 关注点 |
|---|---|---|---|
| 泳道：优先参考 | [记忆读写样例](../assets/swimlane/memory-flow.svg) | [结构](../assets/swimlane/memory-flow.json) | 职责色、阶段栏、条件分支、被动资源、本轮与跨轮次回路 |
| 泳道：基础交接 | [基础样例](../assets/swimlane/example.svg) | [结构](../assets/swimlane/example.json) | 跨道交接与简单返工 |
| ER | [示例](../assets/er/example.svg) | [结构](../assets/er/example.json) | 领域色、PK→FK、两端基数与可选性 |
| 交互 | [示例](../assets/interaction/example.svg) | [结构](../assets/interaction/example.json) | 参与方色、生命线、请求/响应/异步通知 |

泳道布局细节见 [定稿画法](swimlane.md)。架构图沿用同一色板与视觉层级，按领域或职责组织容器与依赖。偏好与定稿状态见 [preference.json](../assets/preference.json)。

这些样例均完成了本地结构/几何检查与飞书回读目检。最新泳道图有14个语义节点、16条关系；全部66段SVG文字在远端保持完整，职责归属、选择性写入与跨会话复用已经核验。这些数量仅记录样例，不限制后续图。
