# 后端接口设计 - 面向 CLI 客户端的最佳实践

> 当后端服务的消费者是 CLI 而非 Web 前端时，接口设计的侧重点不同。CLI 是无状态、一次性执行的客户端，接口要让它能快速拿到结果、能处理流式进度、能精确判断错误并给出下一步动作。

## 核心区别

Web 前端：用户在浏览器里，交互是异步的，可以轮询、可以等。
CLI：用户在终端里盯着，要么快速返回，要么给流式反馈，不能让人干等。

## 1. 响应格式

给 CLI 的接口不需要考虑前端渲染需要的嵌套/聚合，保持扁平、直接：

```json
// Web 前端（聚合多个资源方便渲染）
{ "user": { "name": "...", "avatar": "...", "recentOrders": [...] } }

// CLI（单一职责、扁平结构）
{ "id": "abc", "name": "...", "status": "running", "created_at": "..." }
```

- 列表接口返回数组时，考虑支持 **ndjson**（每行一个 JSON），方便 CLI 逐行处理/pipe
- 提供 `?fields=id,name,status` 让 CLI 只拿需要的字段，减少输出噪音

## 2. 长时间操作：异步模式

两种推荐模式：

### 轮询模式

```
POST /deployments
→ 202 Accepted
→ { "operation_id": "op-123", "poll_url": "/operations/op-123" }

GET /operations/op-123
→ { "status": "running", "progress": 65, "message": "Building image..." }
→ { "status": "completed", "result": { ... } }
```

### SSE/Streaming 模式（CLI 更友好）

```
POST /deployments?stream=true
→ 200 (chunked transfer / SSE)
→ data: {"phase": "build", "progress": 30}
→ data: {"phase": "push", "progress": 70}
→ data: {"phase": "done", "result": {...}}
```

CLI 拿到流可以直接逐行输出 spinner/progress，不需要自己轮询。

## 3. 错误响应

CLI 的错误必须精确、可操作（不像 Web 前端可以模糊提示"操作失败，请重试"）：

```json
{
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Deployment quota exceeded: 5/5 used",
    "hint": "Run `mytool quota upgrade` or delete unused deployments",
    "details": { "current": 5, "limit": 5 }
  }
}
```

- `code`：机器可判断，CLI 用来决定退出码或自动重试
- `hint`：直接告诉用户下一步该执行什么命令
- 参数校验错误要精确到字段名，CLI 好映射回哪个 flag 出了问题

## 4. 认证方式

| 方式 | 适用场景 |
|------|----------|
| API Key / Token（Header） | 最常见，CLI 存本地配置文件 |
| Device Flow OAuth | 需要用户授权的场景（`mytool login` 打开浏览器） |
| mTLS / Service Account | CI/CD 自动化场景 |

不要用 Cookie/Session，CLI 不是浏览器。Token 刷新逻辑要简单——长期 token 或服务端支持 refresh token 自动续期。

## 5. 分页：Cursor-based

CLI 场景推荐 cursor-based 分页而非传统 offset 分页。

### Offset 分页的问题

```
GET /items?page=3&page_size=20
```

- 翻页期间有新数据插入会导致重复或遗漏
- 数据量大时 `OFFSET 10000` 性能差

### Cursor-based 分页

```
GET /items?limit=20&cursor=eyJpZCI6MTAwfQ==
```

cursor 是不透明标记（通常是最后一条记录的 ID 或时间戳的编码），表示"从这个位置之后再给我 N 条"。

```json
{
  "items": [...],
  "next_cursor": "eyJpZCI6MTIwfQ=="
}
```

服务端实现：

```sql
SELECT * FROM items WHERE id > 100 ORDER BY id LIMIT 20
```

**为什么 CLI 更适合 cursor：**
- 增量拉取 — `--follow` 或轮询时天然表示"上次读到哪了"
- 稳定性 — 不受中间数据插入/删除影响
- 性能 — 不管翻到多深，查询性能恒定（走索引）
- 无状态 — cursor 本身携带位置信息，CLI 存一下就行

缺点是不能"跳到第 N 页"，但 CLI 场景基本不需要随机跳页。

## 6. 幂等性

CLI 用户会习惯性重试失败的命令（按上箭头回车），所以：

- 写操作支持 `Idempotency-Key` header
- 或设计成声明式（PUT 语义）：`PUT /config` 传完整状态，重复调用结果一致

## 7. 版本控制

```
# Header 方式（推荐）
Accept: application/vnd.myapi.v2+json

# 或 URL 前缀
/v1/deployments
```

CLI 发布后用户不一定会升级，后端要考虑多版本共存时间比 Web 前端更长。

## 对比总结

| 维度 | 给 Web 前端 | 给 CLI |
|------|------------|--------|
| 响应结构 | 可以聚合嵌套，配合页面渲染 | 扁平、单一职责，方便 pipe |
| 长操作 | WebSocket/轮询 | SSE stream 或 poll + 202 |
| 错误信息 | 用户友好的提示文案 | 机器可判断的 code + 可执行的 hint |
| 认证 | Cookie/OAuth redirect | Bearer token / Device Flow |
| 分页 | offset/page | cursor-based |
| 超时容忍 | 3-5s 用户就烦了 | 可以更长，但要有流式进度 |
| 幂等要求 | 一般 | 更高（用户会重试命令） |
| 版本兼容 | 可以强制升级前端 | 要兼容更久（用户不升级 CLI） |
