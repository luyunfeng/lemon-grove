# 系统结构六图型：输入与实现契约

本组只实现本地渲染与语义检查，不承担视觉评分、飞书发布或回读。样例是独立示意模型，参考图仅为色系灵感，不决定图型布局。

## 所有图共有的结构字段

- `diagram_type`、`title`，可选 `subtitle`。
- `nodes[]`：唯一 `id`、`label`、`kind`、`role`；`lines` 可选。`rank` 可作为 C4 布局列提示；环形协作建议显式提供 rank，rank 不是抽象层级。
- `edges[]`：唯一 `id`、`source`、`target`、非空 `label`、可选 `kind`。不删边、不复用无语义的公共总线。
- `groups[]`：唯一 `id`、`label`、`kind`、`role`。成员以 `node.group` 指向所属边界。
- 可选 `legend: [{role, label}]`。图例只描述当前图中真实使用的角色。

输入深拷贝后才进行显示处理，渲染不改变调用者传入的 spec/style。布局中保留节点 `semantic_kind` / `group`、分组 `semantic_kind`，边保留 `direction` / `protocol` / `ports` / `channel_id`，便于主线程核验。

## 不因缺少描述性元信息而阻断冷启动

严格检查抽象层、真实归属、端点和方向冲突；**不要求用户先补技术栈、职责段落或运行环境才能画图**。

- `technology` 未给定时省略。不从组件名字推断 Python、Java、Kubernetes、数据库实现等技术事实。
- `responsibility` 可以简短沿用用户明确表达的职责含义；仅有名称且无法确认时，画为“职责：未知（未提供）”。渲染器不通过猜测扩写业务行为。
- 层的职责描述缺失时显示“职责未知”；安全区域的 `trust` 缺失时显示“信任策略未知”。普通网络分组不意味着安全隔离。
- 部署 `artifact` / `runtime` 缺失时分别显示制品或运行时未知。实例类型、实例属于哪个区域仍须明确。
- 组件边界的 `parent_system` 缺失时显示“所属系统未知”。组件所属的容器边界 `group` 必须有效；未知系统名称不会变成虚构的系统归属。
- 协议缺失时省略，保留原来的通信描述；缺少 `port` 不猜端口。协议与端口给定时一定显示，即使原始 label 没有重复它们。
- 网络方向缺失不猜测，采用下文 `unspecified` 语义。

这些未知标识不属于硬错误，也不表示已完成架构事实核验。若结构字段本身有冲突或缺失，才报告相应结构错误。

## C4 三种抽象层

| 图型 | 内部节点 kind | 边界 kind | 外部协作者 |
|---|---|---|---|
| `c4_context` | 恰好一个 `system` | `system-boundary` | `person`、`external` |
| `c4_container` | `container` | `system-boundary` | `person`、`external` |
| `c4_component` | `component` | `container-boundary` | `person`、`external`、外部 `container` |

三类都只有一个关注边界：上下文关注完整系统；容器图展开一个系统；组件图展开一个容器，并允许展示父系统名称。外部协作者不填写 group，不能被画入关注边界。不允许上下文里混放容器/组件，也不允许组件图将外部容器放进其内部边界。

类型文字分别为 `[Software System]`、`[Container]`、`[Component]`，不是仅改图标题。`storage: true` 是容器的存储形态提示，用圆柱表示，但其抽象层仍是 container，不能将 `kind` 改成 database 来混淆 C4 语义。

C4 边是调用/使用关系，source → target 必须由输入给定。渲染不从布局位置倒推关系。非网络图如显式填写 direction，仅接受 directed；方向冲突应由调用者澄清，不静默转换。

## 分层架构

`groups[].kind='layer'`，每层用唯一整数 `order` 决定从上到下的职责顺序。`responsibility` 描述层职责，未提供时标未知；每个模块必须拥有有效 group。

层以横向边界面板呈现，模块排列在所属层内。箭头指向被依赖方，不是泳道里的动作时间顺序。向上的依赖必须提供 `allow_upward: true` 和 `rationale`，以区分用户明确给定的回调/依赖倒置关系与误连线。本模块不强制相邻层调用，但不添加不存在的跨层边。

## 部署

兼容现有部署基准字段：节点 `kind='instance'`（省略时按部署实例解释）、`artifact`、`runtime`、`group`，分组代表运行区域或运行节点集合；可选 `network_label` 提供外层网络边界名称。

实例卡展示部署制品与运行时，外层网络边界包含各运行区面板。它描述“哪个实例运行在哪”，区别于网络拓扑描述的路由设备、安全区域和通信协议。既有基准 group 无 kind 时按 `deployment-region` 解释。

## 网络拓扑

- 节点 `kind` 必须为 `router`、`switch`、`firewall`、`client`、`host`、`service`、`store` 或 `external`。
- `router` 显示“路由设备”；`service` 显示“网络服务”；`store` 显示“数据存储”并使用圆柱。不会把所有节点都称为部署实例。
- `security-zone` **是 groups 的 kind，不是可通信节点**。边只能连接真实节点。安全区域用面板和 `trust` 表达准入范围。只给拓扑归属时用 `network-segment`，不能填trust或暗示访问策略；每个节点归入一个已声明分组。
- 边的 `protocol` 可为协议名，`port` 可选；给定值显示在边上，未给定协议不补写。
- 顶层 `communication_direction` 是默认值，边级 `direction` 优先。允许：

| direction | 绘制 | 含义 |
|---|---|---|
| `directed` | source → target | 通信发起方向已给定，不声称响应不返回 |
| `bidirectional` | 两端箭头 | 双向通信明确给定 |
| `undirected` | 无箭头 | 明确建模为无向连通 |
| `unspecified` 或都未提供 | 无箭头 + 方向未给定说明 | 信息不足，不推断双向或单向 |

图底部显式说明实际采用的方向语义。传输层响应、路由可达性与应用发起方向不混作同一事实。

## 自适应布局

网络连通树且分组保持连通时自动层次分叉；其他拓扑采用通用分组布局，不改变方向。管理员终端用client，普通主机可用host。

长链C4内部节点按rank自动折为多行，外部协作者保持在整个焦点边界之外；折行不增删节点或关系。模板位于assets/benchmarks，实际目标预览位于assets/previews。
