# 技术绘图 Skills

本仓库保存两版可复用的技术绘图源码。新任务推荐 **lark-tech-diagrams-v2 2.3.0**；V1 保留早期风格和输入约定，便于参考已有工作。

| Skill | 版本 | 用途 | 安装与运行 |
|---|---|---|---|
| [lark-tech-diagrams-v2](lark-tech-diagrams-v2/SKILL.md) | 2.3.0 | 16 类技术图，确定性 SVG、语义配色、图型布局、包内字体和离线检查 | [安装说明](lark-tech-diagrams-v2/INSTALL.md) |
| [lark-architecture-diagrams](lark-architecture-diagrams/SKILL.md) | 1.1.0 | 早期架构、泳道、ER、交互图风格参考；保留旧版检查与空画板发布助手 | [安装说明](lark-architecture-diagrams/INSTALL.md) |

普通绘图建议只启用 V2；需要旧版时明确点名，避免两份风格同时匹配。安装入口是各目录的 `SKILL.md`，全部代码、模板和必要资源随目录保存，不需要历史聊天。

## V2 的能力与边界

V2 覆盖 C4 上下文、C4 容器、C4 组件、分层架构、部署、网络拓扑、流程、泳道、时序、状态机、活动、ER、UML 类、数据流、模块依赖和事件流。

绘图包负责逻辑建模、颜色语义、排版、字体测量、连线与离线质量检查。创建文档、授权、画板更新、上传、导出和原生节点回读由现有飞书 Skill 或官方 CLI 承担。目标工具接收已经生成的 SVG，避免重新生成另一种图后改变风格。

`assets/fonts/` 中的两份 Noto Sans CJK 字体共约 40 MB，附带 SIL OFL 许可和文件哈希。保留字体是为了稳定文字测量和换行；运行时、账号、缓存、云端收据和逐轮实验报告不随 Skill 提交。

## 使用与验证

给 Agent 的典型请求：

> 使用 lark-tech-diagrams-v2，把下面的逻辑画成技术图：……

> 使用 lark-tech-diagrams-v2，把下面的逻辑画到指定飞书文档：……

先按安装说明运行 `check_examples.py`，验证 16 类参考输入与 SVG 一致；陌生业务仍需检查节点、关系、方向、基数、分支及实际 PNG。示例是虚构业务，不能直接当作用户系统事实。输出目录放在仓库和 Skill 之外。

V2 当前验证环境为 Linux、Python 3.12、Pillow 12.3.0、CairoSVG 2.9.0 和兼容 Fontconfig 的 Cairo。其他操作系统需独立验证；目标端转换和原生文字可编辑性也需由工具回读核验。连接器拖动绑定不在已验证范围内。

## 维护

修改 V2 时，先冻结输入与风格，再运行参考复现、长标签/复杂拓扑回归和独立新任务评审。规则与流程见 [迭代验证](lark-tech-diagrams-v2/references/self-evolution.md)。需要修改参考 SVG 时记录原因并实际看图，不只更新哈希。

V1 的发布助手作为历史实现保留，不作为 V2 的依赖。仓库副本已去掉作者的应用和目录配置；两版都应使用当前调用方自己的账号与目标。
