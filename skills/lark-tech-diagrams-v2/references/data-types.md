# 数据与依赖图型接入说明

## 通用字段

`diagram_type, title, subtitle?, nodes, edges`。节点需要唯一 `id`、`label`、`role`；边需要唯一 `id`、`source`、`target`、可选 `label`、`kind`，数据流与事件流必须具名。`lines` 为补充说明。

| 图型 | 节点字段 | 关系字段与方向 |
|---|---|---|
| er | `fields: [{name, type, key}]`；`key` 包含 PK/FK；`rank` 可作布局提示 | `kind: relationship`；`source_field` 指向主键，`target_field` 指向外键；`cardinality: {source, target}` 支持 `1 / 0..1 / 1..* / 0..*`；绘制乌鸦脚，无流程箭头 |
| class | `fields: []`、`methods: []` 分隔属性与方法；接口名可用 `«interface»` | `inheritance`、`realization`：子类/实现类 → 父类/接口，空心三角位于目标；`composition`：整体 → 部分，实心菱形位于源端；`aggregation`：整体 → 共享部分，空心菱形位于源端；`association`：可导航关联；`dependency`：使用方 → 契约，虚线开箭头；可附两端基数 |
| dataflow | `kind: external / process / store` | 连线必须有数据名，至少一端为 process；process 必须有输入与输出；`flow / feedback` 是数据流，不应把时间顺序或无数据的控制指令当数据流 |
| dependency | `rank` 分列，`group` 对应 `groups: [{id,label,role}]`；分组保持独立边界，布局可将同依赖深度的分组置于同列不同面板；`lines_hint` 补充模块职责 | `import / dependency / implements`；箭头从依赖方指向被依赖方，虚线开箭头；不表达运行时请求次序 |

ER 类型核对检查单字段 PK → FK 类型一致，不推导数据库完整约束；`aggregation` 表示整体到共享部分，使用源端空心菱形；`composition` 使用实心菱形。标准UML继承、实现、聚合、组合可以省略关系文字；未知字段类型不做武断的类型冲突判断。DFD 处理节点的输入输出存在性不能证明转换逻辑正确，仍需业务审查。依赖图允许真实循环，是否违反架构边界需要业务规则判定。

## event_flow 输入契约

节点 `kind`：

| kind | 语义 | 默认颜色 | 附加字段 |
|---|---|---|---|
| publisher | 发布事件的应用 | blue | `lines` 描述发布条件 |
| topic | 事件主题 | purple | 必须有 `event_type`、`delivery_mode: fanout` |
| subscriber | 独立逻辑订阅的消费者 | teal | `lines` 展示订阅名称及处理职责 |
| dead_letter | 失败事件的死信主题 | rose | `lines` 说明保留原事件、错误与订阅信息 |

基本角色层次为0/1/2/3；实际前向拓扑决定下游层级，确认边不参与推高列级。死信主题可以有独立订阅者，后续订阅者自动排到死信主题下游。`type_label` 自动显示节点角色。节点显式 `role` 可覆盖默认配色；边使用固定语义配色。

| 边 kind | 方向 | 必需附加字段 | 表现 |
|---|---|---|---|
| publish | publisher → topic | `event_type` 等于目标主题类型 | blue，实线开箭头 |
| deliver | topic或dead_letter → subscriber | `event_type` 等于源主题类型，`subscription` 非空 | teal，实线开箭头 |
| ack | subscriber → 对应的topic或dead_letter | `acknowledges` 是反向对应的 deliver 边 ID | slate，虚线开箭头 |
| dead_letter | subscriber → dead_letter | `failed_delivery` 是该消费者收到的 deliver 边 ID；`event_type` 保留原投递事件类型 | rose，实线开箭头 |

同一主题的每条 deliver 对应不同的 `subscription`，表示扇出后独立投递、处理与确认。共享一个订阅的竞争消费者实例不是独立扇出，本契约拒绝重复订阅名称。若需要表达消费组内实例竞争，应先聚合为一个逻辑订阅者，或扩展专门的消费组视图。

消费确认表示该投递的处理完成，不是新领域事件、RPC 返回值，也不表示另一个订阅成功。成功确认与失败耗尽后转入死信是不同条件分支，不承诺二者会同时发生；图表达消息拓扑，不表达时序。当前 ack 专指消费确认，不表示 broker 对发布的确认。死信箭头表达逻辑失败转移，不断言搬运由应用还是 broker 执行。样例不声称 exactly-once。topic、ack或死信本身均不证明持久化保证；只有用户明确给出时才在补充说明里标注持久化。

不强制每个图必须包含 ack 或死信；但出现这两类边时必须关联对应的原始投递。未知节点种类、未知边种类、事件类型改变、跨订阅确认、直接从发布者投递到订阅者均会报错。

保留 `spec.legend=[{role,label}]` 自定义图例；未提供时显示发布、主题、独立订阅、虚线消费确认、死信五类说明。

## 复杂关系与布局

死信主题不是必然终点。若有独立订阅，dead_letter节点必须声明event_type和delivery_mode=fanout，deliver边照常带subscription，ack关联其deliver。死信投递仍保留failed_delivery与原事件类型。不能为了通过校验删除人工处理器或将死信订阅伪装成发布。

依赖图按分组之间的依赖距离组织，应用与基础设施可在同列独立面板中。普通依赖/导入为灰色虚线，实现为橙色虚线，图例明示区别。事件流长链按拓扑阶段折行，确认不推动阶段。类图名称栏与属性/操作栏有明确分隔线，浅色填充不能代替分栏。
