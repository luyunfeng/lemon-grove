# 飞书接入

调用方使用自己的 profile、应用和目标目录。本文不提供默认账号、App ID、父目录或资源 token；这些属于当前用户的运行配置，应由现有飞书工具读取或由调用方显式提供。用户文档操作通常使用 user 身份，按实际任务和授权选择。

先用 `lark-cli --profile ... auth status --json --verify` 核对应用和用户态。参数可能随版本变化，读 CLI 内置 skill 和 help。官方项目：[Lark CLI](https://github.com/larksuite/cli)。转换能力以 whiteboard-cli 实测为准。

历史验证环境：lark-cli 1.0.74，whiteboard-cli 0.2.13。新建画板需要 `board:whiteboard:node:create`，回读与导出需要 `board:whiteboard:node:read`。历史验证不代表使用者已有这些权限；按实时登录状态和工具返回的具体缺失 scope 处理。

空画板的真实响应可能是 `{"ok":true,"data":{"msg":"whiteboard is empty"}}`，非空返回 `data.nodes`。未知响应不能当空画板。

转换成功和几何检查通过不代表业务文字可编辑：回读的 `image` 可能包含整个模块。必须将结构中的标题和详情与 `text_shape` / 形状节点的 `text.text` 核对。带变换的图标 path 用独立 g 隔离，避免父模块整体降级。图标与独立箭头成为图片节点可以接受。

```sh
lark-cli --profile <profile> docs +create --content @document.xml --as user --parent-token <parent-token>
```

XML 中每版含标题、说明与 `<whiteboard type="blank"></whiteboard>`。从成功信封 `data.document.new_blocks` 取 block_id/block_token。把文档链接、编号、token 保存在任务的 boards.json，不进模板。结果不明时先查是否已创建，避免重复文档。

SVG 写入转换成多个节点；raw 回读核对文字、形状和连接器类型，image 导出服务端PNG后目测。只验本地不能说已验证远端。

发布助手只填充已有空画板；不改变归属、不改分享权限、不发消息。收据保留稳定幂等 key，重复调用不重复写入。后续迭代先查远端手改情况，默认新增版本；明确要求覆盖才走 lark-whiteboard 编辑流程。

多个可编辑节点不等于连接器端口已绑定；实测拖动跟随后才能这样承诺。本地 structure 是重绘依据，但不能用旧版覆盖用户新改动。
