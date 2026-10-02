# 柠檬林 · Lemon Grove

柠檬林（Lemon Grove）从 GitHub 仓库 `luyunfeng/lemon-grove` 的 `main` 分支读取个人知识库。网站提供分类、全文搜索、标签筛选和 Markdown 阅读，保留卡带存档界面。

## 内容更新

知识库的内容维护和 PR 合入继续在 GitHub 完成。默认使用已连接的 GitHub 授权读取远端 `main`，固定 commit SHA 后把知识页同步为 `app/knowledge-publication.json`，随站点发布。打开网页即可阅读，无需另配站点读取凭据。这个文件是远端知识页的发布副本，不是独立编辑的内容源。

- 展示 `wiki/concepts/*.md`、`wiki/entities/*.md`、`wiki/roadmaps/*.md`、`wiki/syntheses/*.md` 与 `wiki/overview.md`。
- 从页面 frontmatter 读取 `title`、`type`、`tags`、`entities`；从 `wiki/index.md` 读取领域、简介和排列顺序。
- 不读取或展示 `raw/`、`wiki/log.md`、规则文件、未合入分支、符号链接或 submodule。
- Markdown 支持标题、列表、引用、表格和代码块，原始 HTML 不执行。
- 发布副本记录 GitHub 提交版本和同步时间，所有知识页都来自同一个提交。
- GitHub 后续合入的内容需要再次同步发布；页面的“重新加载”读取当前站点版本，不会替用户完成 GitHub 同步。打开的页面每 5 分钟检查已发布内容更新。
- 可选实时读取模式下，服务端缓存有效期为 5 分钟；同一凭据的并发请求会合并，版本未变化时不会重复下载正文。
- 临时故障保留可用内容并标记状态。实时读取不可用时，可继续阅读已经发布的 GitHub 版本。

## 可选的实时读取

如需网页自行检查 GitHub 的新提交，可在 Sites 的服务端 Secret 中设置 `GITHUB_TOKEN`。使用 fine-grained GitHub token，仅选择 `luyunfeng/lemon-grove`，授予 **Contents: Read-only**。此配置不是阅读已有内容的前提，凭据不得放入页面或提交到 Git。

本地开发可在忽略的 `.dev.vars` 中配置同名变量。网页与 `/api/knowledge` 仅在 Cloudflare Worker 服务端读取凭据，响应中不包含凭据。站点访问范围继续由 Sites 管理。

未设置凭据时，页面直接展示从 GitHub 同步的真实知识页，并注明当前是发布版本。已设置凭据时，网站会尝试读取最新 `main`；成功后新知识页无需重新部署即可出现。

GitHub 接口说明：[仓库内容](https://docs.github.com/en/rest/repos/contents)、[Git trees](https://docs.github.com/en/rest/git/trees)。

## 开发与验证

Node.js 版本要求：`>=22.13.0`。

```bash
npm install
npm run dev
```

```bash
npx tsc --noEmit
npm test
npm run build
```

运行开发预览后，可额外验证实际页面和接口：

```bash
SAVEPOINT_TEST_URL=http://localhost:3000 node --test tests/rendered-html.test.mjs
```

测试中的合成 Markdown 仅用于验证，不进入站点内容。GitHub 读取、缓存与权限边界测试位于 `app/knowledge-source.test.ts`，网页交互测试位于 `app/page.test.tsx`。

## 主要文件

- `app/knowledge-source.ts`：GitHub 只读适配、知识页解析、版本一致性与缓存。
- `app/knowledge-publication.json`：从固定 GitHub 提交生成的发布内容，不能手工改写正文。
- `app/api/knowledge/route.ts`：同源读取接口，使用 `private, no-store` 响应。
- `app/page.tsx`：动态服务端首屏，加载真实连接状态与内容。
- `app/archive-browser.tsx`：分类、搜索、阅读、刷新与错误恢复。
- `.openai/hosting.json`：站点的 Site 身份；不保存运行时凭据。

网站使用 vinext 和 Cloudflare Workers。现有 D1、R2 配置继续为 `null`；GitHub 是内容来源。
