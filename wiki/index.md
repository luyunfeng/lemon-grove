# 知识地图（Index）

> 按领域分组，每页一行：链接 + 一句话。一页讲一个知识点或一个工具；页面之间不互相链接，关联靠每页头部的 `tags` 和 `entities` 来找（命令见 AGENTS.md 3.3）。本页是全库唯一放链接的地方。查询时先读这里。

## 概览
- [知识库概览](overview.md) — 在学什么、掌握程度、待解问题
- [操作日志](log.md) — 写操作记录

## Agent 工程方法
- [Agentic Engineering（智能体工程）](concepts/agentic-engineering.md) — Agent 成为主要执行者后，工程重心转向定义意图、设计验证、承担判断
- [Context Engineering（上下文工程）](concepts/context-engineering.md) — 把上下文当稀缺资源：渐进式披露、工具执行隔离、分层入口文件
- [Harness Engineering（驾驭工程）](concepts/harness-engineering.md) — 用反馈闭环包住会漂移的概率模型；harness 随模型进步要删减
- [Verification（验证）](concepts/verification.md) — 生成容易验证难：maker/checker 分离、可验证的完成条件、证据的边界
- [Loop Engineering（循环工程）](concepts/loop-engineering.md) — 设计自动驱动 Agent 的外层循环：触发、提示、运行、验证、记录
- [目标驱动与计划驱动（Goal vs Plan）](concepts/goal-vs-plan.md) — 事前定步骤与事后验目标两种控制方式，各自适用的场景
- [Spec 驱动开发与执行前校准（Vibe / Plan / Spec）](concepts/spec-driven-development.md) — 执行前校准的光谱 Vibe → Plan → Spec，以及从澄清到规格到任务的流水线
- [子 Agent 编排（Sub-agents / Multi-Agent）](concepts/sub-agent-orchestration.md) — 用子 Agent 隔离上下文、分离实现与检查；模型编排、脚本编排、跨模型混合
- [约束的强制分层（Rule Enforcement Layers）](concepts/rule-enforcement-layers.md) — 约束分建议、流程、硬拦截三层；能确定性检查的不靠模型记住
- [Compound Engineering（复利工程）](concepts/compound-engineering.md) — 把每次工作沉淀成可复用资产，让下一次同类工作更容易
- [提示词中的置信度](concepts/confidence-in-prompts.md) — 让模型输出置信度，用来自我校准、决策路由和聚焦人工验证
- [Agent 工具接口（CLI 优先，MCP 作薄适配层）](concepts/agent-tool-interface.md) — CLI 是 Agent 最好用的工具接口，MCP 作薄适配层；后端也要为 CLI 设计
- [Agent 原生文档（Agent-Native-Doc）](concepts/agent-native-doc.md) — 写给 Agent 读的仓库文档：只写代码推不出来的领域知识

## Agent Skills
- [Agent Skill](concepts/agent-skill.md) — 按需加载的专家能力包：何时值得做、怎么加载、装在哪里
- [Agent Skill 设计](concepts/agent-skill-design.md) — 写判断不写教程、能被找到、抵抗合理化、用 TDD 测 Skill
- [Skill 自进化](concepts/skill-self-evolution.md) — 不动权重，优化 Skill 与 Prompt；验证即奖励，改动有界、门控严格
- [递归自我改进](concepts/recursive-self-improvement.md) — AI 参与构建更强的 AI；近中期更可能是改进 harness 而非权重

## 模型训练与评测
- [可验证奖励](concepts/verifiable-rewards.md) — 后训练从人类偏好转向可验证奖励，Coding 因此率先突破
- [模型评测](concepts/model-evaluation.md) — Arena、传统基准、自有评测三层，以及怎么读懂一次模型发布

## 个人知识管理
- [LLM Wiki 模式](concepts/llm-wiki-pattern.md) — LLM 把资料持续编译成互链的 wiki：raw / wiki / schema 三层，ingest / query / lint
- [Open Knowledge Format（OKF）](concepts/open-knowledge-format.md) — 把 LLM wiki 规范成可移植、可互操作的开放格式
- [本知识库的设计与用法](concepts/knowledge-base-design.md) — 本库的结构、写法、硬规则和日常用法

## 工具与项目
- [Claude Code](entities/claude-code.md) — 终端 Coding Agent：harness 扩展点、大型代码库做法、/goal 与 /loop、子 Agent
- [Codex](entities/codex.md) — 终端 Coding Agent：Skill 发现目录、Hook 体系、混合模型子 Agent
- [Claude 模型家族（以 Opus 4.8 / Fable 5 为例）](entities/claude-models.md) — 以一代 Claude 模型为例：诚实性、Effort Control、动态工作流等能力点
- [ECC（Everything Claude Code）](entities/ecc.md) — Agent 行为层框架：Command → Agent → Skill → Hook → Instinct，学法是做减法
- [Superpowers](entities/superpowers.md) — 纪律型 Skill 框架：七步工作流、三层强制、TDD for Skills
- [mattpocock/skills](entities/mattpocock-skills.md) — 小而可组合的 Skill 工具箱：wayfinder → grill → to-spec → to-tickets → implement

## 学习路线
- [Agent 工作流实践路线：用减法搭最小闭环](roadmaps/agent-workflow-practice.md) — 用减法搭一个能反复跑通的 plan → change → verify → review → handoff 闭环
- [Lil'Log 博客阅读路线](roadmaps/lillog-reading-path.md) — 按主题分阶段读 Lil'Log，补齐从模型能力到系统能力的背景

## 综合 / 问答
<!-- 仅在用户明确要求沉淀结论时写入（需确认 + MR） -->
