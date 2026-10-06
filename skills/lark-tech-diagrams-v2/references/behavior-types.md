# 行为交互图型输入契约

## 公共输入与入口

- `diagram_type`：`flowchart`、`swimlane`、`sequence`、`state`、`activity`。
- `title`、`subtitle`：标题与可选说明。
- `nodes`：唯一 `id`、`label`、`role`；可选 `kind`、`lines`。
- `edges`：唯一 `id`、`source`、`target`、`kind`；`label` 可省略或为空，可选 `role`。不删边、不改业务标签；仅决策出口要求可识别的守卫，不把 label 要求泛化到全部 UML 关系。

## flowchart

`kind=decision` 使用菱形，至少两条具名分支；普通步骤使用动作卡片。分支深度决定列排布，反馈边走独立端口。`outcome=success|failure|reused` 保留旧版兼容语义，显式 `role` 优先。

## swimlane

`lanes=[{id,label,role?}]` 声明责任主体，每个节点通过 `lane` 归属。lane.role决定责任区域底色，节点role表达动作类别、判断或结果；节点未指定role时沿用责任色。空责任 lane 仍保留其面板。图的阶段由边拓扑计算，不能依赖节点列表顺序冒充时序。

方向优先级为 `spec.orientation` → `style.swimlane_orientation` → `horizontal`。仅支持 `horizontal|vertical`，不存在强制纵向默认。

- `horizontal`：责任横带，流程从左向右；相邻阶段间距按完整边标签测量，不截断长中文。
- `vertical`：责任列，流程从上向下；顶部责任标题，节点在所属 `lane-<id>` 面板内；同一责任列、同一拓扑层的多个动作并排。
- 业务交接自然适合横向时使用横向；责任人需要并列且步骤较多时可显式选择纵向。
- 当前不支持phases字段；拓扑层不能强行解释为业务阶段。

## sequence

参与者的数组顺序决定横向位置，消息顺序决定时间向下推进；保留竖向虚线生命线。

- `edges` 为推荐消息数组，兼容 `messages`；两者同时存在时 `messages` 优先。
- `kind=sync`：实线实心箭头；`async`：实线开放箭头；`return`：虚线开放箭头。
- `activations=[{participant,start,end}]`：消息 ID 界定激活段。
- `branches=[{kind:"alt",operands:[{guard,start,end},...]}]`：至少两个非空 guard 的互斥操作数，范围必须存在、有序、不重叠。
- 支持多个互不重叠 alt 框；嵌套或相互重叠框明确拒绝，避免画成同级框而改变含义。
- 自调用保留折返路径，按完整标签宽度分配空间；末位参与者自调用也不能越界。

## state

保留状态机的初始实心圆与终态靶心、状态卡片，以及 `事件 [守卫] / 动作` 转移标签。

- 初始节点 `kind=initial`，终态 `kind=final`。
- 兼容独立 `pseudonodes`；普通状态沿用 `waiting|active|success|failure`。
- 重试与反馈是状态转移，不用活动并行条代替。多返回路径时保留完整事件文本与独立路线。

## activity

活动控制流要求明确的开始和结束，不能仅给普通流程图换标题。

- `kind`：`initial|final|action|decision|merge|fork|join`，兼容独立 `pseudonodes`。
- 初始节点：恰好一个，无入边、恰好一个出边；终态：至少一个，有入边、无出边。
- 普通 action：一入一出；多个出口必须显式使用 decision 或 fork，多个入口必须显式使用 merge 或 join。
- decision：一入、至少两条具名守卫出口，菱形；merge：多入一出，菱形，只合并互斥路径。
- fork：一入多出；join：多入一出。同步条跨越相应并行分支，入边从上侧、出边从下侧连接。
- 所有节点必须可从初始节点到达，并存在到终态的路径。检查不等价于任意复杂活动网络的死锁证明，也不自动推导分支条件互斥性。
- `fork/join` 标签可为空；如给 label，渲染器在条右侧保留原文。条内部不容纳卡片文字。

状态机初始转换不能携带事件触发器或guard；可以空标签或写 / 初始化动作。创建状态机的外部事件放说明，若需要等待事件则用普通等待状态表示。该规则依据 [OMG UML说明](https://issues.omg.org/issues/UMLR-803)。
