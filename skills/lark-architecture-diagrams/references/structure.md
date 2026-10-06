# 结构约定

把自然语言转换成最小结构，不要求用户会写 JSON。

```json
{"title":"请求处理架构","nodes":[{"id":"client","title":"客户端","detail":["提交请求"]},{"id":"api","title":"API 服务","detail":["校验与处理"]}],"edges":[{"id":"e01","source":"client","target":"api","kind":"request"}]}
```

可加 basis（事实依据）、notes（边界）、source_refs（证据定位）。资料只取画图所需内容，产物不包含密钥或内部地址。节点 ID 唯一，端点必须存在。`source/target` 标识关系两端；其含义由图型与kind决定，ER不因此需要流程箭头。

推荐按图型增加最少的语义字段：

- `diagram_type`、`color_dimension` 或 `visual_map`：解释视觉编码。
- 泳道：节点的 `lane` / 责任方，边的 `condition`，泳道顺序与流程方向。
- ER：节点 `fields`（name/key/references/nullable），关系 `source_cardinality/target_cardinality/foreign_key`；父端连接主键或明确的实体级端口，避免连在错误字段行。
- 交互：边的 `label/message_order/kind/branch`，参与者、生命线与alt/loop片段。已受理后的最终交付通常是新的通知，不冒充首次同步请求的return。

边的 `label` 会参与原生文本核对，确保消息名和关系名没有随SVG降级而失去编辑能力。基数端点、责任归属和时序仍需人工图型验收。

SVG 对应标记：

```xml
<g data-node-id="client">
  <rect x="40" y="80" width="180" height="100" fill="#F6FAFF" stroke="#337FF0"/>
  <text x="60" y="120" font-size="24">客户端</text>
  <text x="60" y="150" font-size="18">提交请求</text>
</g>
<polyline data-edge-id="e01" data-source="client" data-target="api" points="220,130 300,130" fill="none" stroke="#337FF0" marker-end="url(#arrow)"/>
```

`check` 比较节点ID、端点和节点文字，拒绝脚本、外链、嵌入图片及常见不兼容效果。它不推断关系是否正确，不保证飞书连接器端口绑定，仍需目测与回读。
