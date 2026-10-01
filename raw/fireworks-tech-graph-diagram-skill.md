# fireworks-tech-graph 技术图 Skill 阅读笔记

AI Coding Reading Note

# `fireworks-tech-graph`：把“手动画技术图”变成“说清楚系统结构”

来源微信公众号

作者开源先锋

时间2026-07-20 抓取

原文[mp.weixin.qq.com](https://mp.weixin.qq.com/s/WMDOVnl6AzGKcxMGCrtctA)

**核心观点：**`fireworks-tech-graph` 是一个可在 Codex 和 Claude Code 中使用的 Agent Skill。它用自然语言生成技术图，输出经过几何校验的 SVG、高清 PNG、语义化 GIF 动效，以及支持缩放平移的离线 HTML。

它瞄准的是 AI 应用文档里的高频痛点：RAG、Multi-Agent、Tool Call、Mem0、Agentic Search 等结构变化快，手动开 Draw.io 拖框拉线成本太高。

## 文章精华

### 1\. 目标不是“替你装饰图”

文章强调它不是简单换皮，而是把架构图生成拆成语义识别、布局选择、几何校验、格式导出几步。

用户描述“画一张 Mem0 架构图”，它会识别成 Memory Architecture Diagram，并套用泳道、圆柱体、语义箭头等图形语言。

### 2\. 面向 AI/Agent 场景

内置 RAG、Agentic Search、Mem0、Multi-Agent、Tool Call flow 等模式知识。

文章举例说，LLM、Agent、向量库等对象会有稳定的形状规范，减少每次画图时重新设计图例的成本。

### 3\. 输出不只是一张图

支持 SVG 和 PNG 双输出，PNG 默认 1920px 宽，适合直接放文章或方案文档。

也可以生成 GIF 动效，把数据流转顺序一条条画出来，适合解释流程而不是只展示静态结构。

### 4\. 可用在 Codex / Claude Code

安装后可以在 Claude Code 里直接用自然语言描述需求，工具会识别触发词、判断图类型和风格，再生成 SVG/PNG。

文章称项目已有 8.8k star，且仍在持续迭代。

## 从描述到产物的链路

**Natural Language** 说清楚系统、角色、组件、数据流

**Diagram Intent** 识别架构图、UML、Tool Call、RAG 等类型

**Style System** 选择扁平、蓝图、Notion、玻璃态、Claude/OpenAI 风格

**Geometry Check** 布局、箭头、泳道、图形语义保持一致

**Artifacts** 导出 SVG、PNG、GIF、交互 HTML

## 能力清单

能力 | 文章中的描述 | 实际价值  
---|---|---  
12 种视觉风格 | 白底扁平、暗黑终端、工程蓝图、Notion 极简、玻璃态、Claude/OpenAI 官方风等。 | 让图适配不同场景：博客、README、汇报、方案文档，不必每次手调样式。  
AI/Agent 领域知识 | 内置 RAG、Agentic Search、Mem0、Multi-Agent、Tool Call flow 等模式。 | 减少“什么对象该画成什么形状”的决策成本，稳定图形语言。  
14 种 UML 图 | 类图、组件图、部署图、状态机图、时序图、用例图等。 | 覆盖传统软件设计文档，不局限于 AI 架构图。  
语义化箭头 | 实线代表主数据流，虚线代表异步事件，另一种虚线代表内存写入。 | 让读者通过线型和颜色理解关系，减少额外解释。  
工程化输出 | SVG、PNG、GIF、离线 HTML；PNG 默认 1920px；渲染器支持 cairosvg、rsvg-convert、puppeteer。 | 从“生成草图”推进到“能进文档的交付物”。  
  
## 安装与使用

### 安装 Skill
    
    
    npx skills add yizhiyanhua-ai/fireworks-tech-graph

文章特别提醒：这里使用 GitHub 仓库路径，不是 npm 包名。

### 更新到最新版
    
    
    npx skills add yizhiyanhua-ai/fireworks-tech-graph --force -g -y

重新执行并带 `--force`。

### PNG 渲染器
    
    
    pip install cairosvg

文章推荐使用 `cairosvg`。

### GIF 动效依赖
    
    
    brew install ffmpeg
    npm install --prefix ~/.claude/skills/fireworks-tech-graph puppeteer-core@25.3.0

需要动图时再装 FFmpeg 和 Puppeteer。

## 示例 Prompt

### Tool Call

画一个 Tool Call 工具调用流程图：LLM -> 工具选择 -> 执行 -> 结果解析 -> 回传 LLM。

### UML 用例图

画一个在线教育平台的 UML 用例图。角色：学生、教师、管理员。用例：选课、观看视频、提交作业、批改作业、管理用户、查看学情报告。

### 微服务蓝图

画一个微服务架构蓝图，工程蓝图风格。展示移动端/Web -> API 网关 -> 用户、订单、支付、通知服务 -> PostgreSQL + Redis + RabbitMQ，并包含 Prometheus + Grafana 监控层。

## 关键原句

把“画技术图”这个体力活，变成“说清楚系统结构”这个脑力活。 

## 我的理解

这类 Skill 的价值不只是省掉 Draw.io 的拖拽时间，而是让“图”进入 AI 编程工作流：需求、设计、代码实现、文档解释可以共享同一段结构化描述，并持续再生成。

但我会把它定位成“技术文档图的生产工具”，而不是完整建模工具。对于汇报、README、架构说明、方案评审，它很合适；对于需要严格语义约束、长期维护的系统模型，仍然要把源描述、生成结果和人工评审一起纳入版本管理。

实际使用时，最重要的不是写“帮我画个好看的图”，而是把组件、边界、方向、同步/异步、存储、外部系统、失败路径讲清楚。描述越像设计文档，生成图越有用。

## 适合我的工作流

  1. 先写一段系统结构说明，不急着画图。
  2. 明确图类型：架构图、时序图、用例图、部署图、数据流图。
  3. 指定风格和用途：README、方案评审、技术分享、交互 HTML。
  4. 要求同时输出 SVG + PNG，重要流程再补 GIF。
  5. 把源 prompt 和生成图一起放进文档仓库，方便后续更新。

记录日期：2026-07-20  
笔记路径：doc-notes/ai-coding/2026-07/notes/fireworks-tech-graph-diagram-skill.html  
原文包含 13 张正文图片；本笔记保留文字核心信息和可执行命令，未下载归档原图。
