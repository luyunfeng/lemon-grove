# LLM Wiki 学习知识库

按 LLM Wiki 模式组织的个人学习知识库：
**raw（原始资料底稿，正文只增不改） → wiki（AI 维护的 Markdown 知识页，关联靠标签和实体） ← AGENTS.md（唯一规则来源）**。
纯 Markdown + git，不用数据库，也不用向量索引。

## 目录

```
AGENTS.md          唯一规则来源：目录约定、frontmatter、查询/写入/体检流程、写入确认、PR 流程
CLAUDE.md          Claude Code 入口（@AGENTS.md）
raw/               原始资料底稿（一级目录，不分类；图片放 raw/assets/；文件名不带日期，头部不写作者和来源）
wiki/              知识页：index.md 知识地图、log.md 写入日志、overview.md 概览
  concepts/ entities/ roadmaps/ syntheses/   一页一个知识点或工具；头部的 tags / entities 用来找关联，正文不放站内链接
apps/lemon-grove/  柠檬林站点的完整源码、依赖锁文件、测试与 GitHub 内容发布版本
templates/         页面模板
tools/lint.py      只读体检脚本
tools/related.py   按页面、标签或实体列出相关页面
skills/llm-wiki/   全局 skill：按线索找到（或克隆）本仓库，再定位到 AGENTS.md
skills/lark-architecture-diagrams/  V1.1.0 技术绘图旧版参考
skills/lark-tech-diagrams-v2/       V2.3.0 技术绘图，默认推荐
```

## 用法（在 Codex 或 Claude Code 里直接说）

- 查询（只读）：「查知识库：RAG 我记了什么？」「我的知识库里有没有讲过 X」
- 写入：「炼化一下：<内容或 URL>」「把这篇收录进知识库」。AI 会先列出计划，**你确认后**才会写入，然后开分支、提交并创建 PR（不会直接改 main，也不会自动合并）。
- 体检：「知识库体检 / lint 一下」。先给报告，修复同样需要你确认，并走 PR。

skill `llm-wiki` 装好后在任何目录下都能触发。新机器安装见 `skills/llm-wiki/INSTALL.md`。

手工检查：

```bash
python3 tools/lint.py                    # 头部四项 / 标签词表 / 实体 / 站内链接 / index 一致性 / 来源与日期痕迹
python3 tools/related.py --tag verification   # 按标签找相关页面（也可以 --entity 或传一个页面路径）
grep "^## \[" wiki/log.md | tail -5      # 最近 5 次写入
```

## 技术绘图 Skills

两版技术绘图源码保存在 `skills/`，版本选择、安装与验证入口见 [Skills 说明](skills/README.md)。新任务推荐 V2.3.0：内置 16 类技术图、语义配色、确定性排版、字体和参考图；飞书文档与画板交付调用现有工具。V1.1.0 保留为早期风格参考。

## 柠檬林站点源码

站点完整源码保存在 `apps/lemon-grove/`，包括页面、服务端读取逻辑、依赖锁文件、测试和构建配置。运行与内容同步说明见 `apps/lemon-grove/README.md`。

恢复与本地开发（Node.js >=22.13.0）：

```bash
cd apps/lemon-grove
npm ci
npm run dev
```

验证和构建使用 `npm test`、`npx tsc --noEmit`、`npm run build`。后续代码变更通过 PR 维护此目录，发布时使用同一份已验证的源码；`.openai/hosting.json` 保留现有 Site 身份。

知识内容继续从 GitHub 的 `main` 分支同步。默认展示 `app/knowledge-publication.json` 中记录的 GitHub 发布版本；新内容合入后需要再次同步发布。可选的实时读取配置见站点 README。仓库不保存运行凭据、依赖安装目录或构建产物。
