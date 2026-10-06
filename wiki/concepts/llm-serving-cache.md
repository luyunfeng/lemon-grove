---
title: LLM Serving 四层缓存
type: concept
tags: [inference]
entities: []
---

LLM serving 用四层缓存复用已处理的 token，避免 agent 循环里每轮重复支付 prefill 成本。

## 要点

每次请求都要对完整 prompt 做 prefill：为每个 token 在每一层计算 attention 状态。这一步同时决定输入费用和首 token 延迟。Agent 循环中大部分 prompt 是上一轮已处理过的文本，缓存的目标就是不为这些 token 重复付费。

- **KV cache**：为单个活跃请求保存每层每个 token 的 key/value 张量，请求结束即释放，作用域是一次请求。
- **Prefix caching**：服务端跨请求保留这些张量。vLLM 按 16-token 块存储，块的哈希链式包含前一块的哈希，前面全部命中该块才可能命中；调度器在第一个 miss 处停下，只 prefill 后缀。
- **Prompt caching**：同一复用跑在 provider 硬件上，按价目表计费：写入收 1.25 倍基础输入价，读取收 0.1 倍。
- **Semantic caching**：把请求 prompt 嵌入向量，对已存 prompt 做相似度检索，超过阈值就直接返回存的答案，完全跳过模型。它连输出 token 都省了，但每次请求（包括 miss）都要付一次 embedding 往返。

## 怎么用

不必自建 serving stack。transformers 库把 KV cache 做成可保留的对象：对语料 prefill 一次，保留返回的张量，跨查询复用，约十行代码。用 provider API 就开启它的 prompt cache；自托管 vLLM 则直接受益于 prefix cache。

## 边界与误区

- 前三种按精确 token 匹配，不改变模型输出，只省输入侧的重复计算；输出费用与生成质量都不受影响。
- 语义缓存按相似度匹配，embedding 误配就可能返回错误答案：它额外省输出 token，却引入答非所问的正确性风险，只适合高重复、可容忍过期的低风险问答。
- prompt 前缀的一致性决定命中率：哈希链式匹配意味着从第一个变更处开始整条链失效，稳定的 system prompt 和工具定义要放在最前面。
