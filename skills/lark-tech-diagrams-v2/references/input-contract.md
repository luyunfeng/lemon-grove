# 逻辑描述到结构输入

用户描述逻辑，Agent填写JSON。先按diagram-types.md选型，再读取assets/benchmarks对应完整样例。替换所有假想事实、图例和条件；未知方向、基数和技术信息不得杜撰。

## 共同字段

必须有diagram_type、title、nodes、edges（时序可用messages替代edges），subtitle可选。节点有唯一id、label；边有唯一id、source、target、kind，以及需要表达的label。数据流和事件流必须具名，继承/实现等标准UML关系可不加文字。role为语义颜色角色，不改变实体类型。

色板支持blue、teal、purple、orange、amber、green、slate、rose。legend为[{role,label}]，label解释业务角色或类别，不能只写颜色名称。背景区域与节点使用不同编码时要说清含义。模板的图例也属于假想事实，必须一起改写。

## 按图型读取字段

| 类别 | diagram_type | 必读规范 |
|---|---|---|
| 系统结构 | c4_context / c4_container / c4_component / layered_architecture / deployment / network_topology | [system-types.md](system-types.md) |
| 行为交互 | flowchart / swimlane / sequence / state / activity | [behavior-types.md](behavior-types.md) |
| 数据与依赖 | er / class / dataflow / dependency / event_flow | [data-types.md](data-types.md) |

C4的system/container/component是抽象层级，不能把数据库容器写成另一个层级；用storage=true表示其存储外形。分层图groups带order；网络节点明确kind与区域，并保留给定的direction。活动图的fork/join表示并行，不可用两个普通先后步骤代替。ER关系从PK实体端指向FK实体端并提供两个字段与双端基数。类图aggregation为空心菱形、composition为实心菱形，菱形都在整体端。

脚本自动计算坐标、换行、端口和绕障，不要在JSON中手写像素位置。rank、stage属于可选布局提示，不改变关系或时间事实。超过单图可读密度时按语义拆分，并保持跨图接口命名一致。

## 输出与失败

`render.py` 写入 `diagram.svg`、`layout.json`、`validation.json`。发现几何/语义错误默认退出码2，保留工件供修复。`--allow-draft` 仅用于研究轮次保留失败证据，不能当成发布通过。

需要交付飞书时按tool-handoff.md调用现有工具完成转换、回读和目标端看图。

默认输出中等规模的单一视图。输入关系密集时先按责任/边界拆成总览和局部视图，并保持跨图接口名称与关系完整。没有对任意规模图作零交叉承诺，也不将局部SVG图形误称为全部原生绑定形状。
