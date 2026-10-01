# CLAUDE.md

本仓库是一个 LLM Wiki 模式的个人学习知识库。**唯一的规则来源是 [AGENTS.md](AGENTS.md)**，请先完整阅读并严格遵守：

@AGENTS.md

要点速记（与 AGENTS.md 冲突时，以 AGENTS.md 为准）：
- **写入先确认**：炼化、收录这类写入请求，第一步列出要写的内容、文件路径、分支名和 PR 标题，等用户明确同意后才动手。
- **查询只读**：不改文件、不回写、不记 log、不做 git 写操作；值得沉淀的内容只提建议。
- **只走 PR**：从 `origin/main` 开 `wiki/<YYYYMMDD>-<slug>` 分支，然后 commit、`git push -u origin HEAD`、`gh pr create --base main`；不 push main，不合并 PR。
- `raw/` 一级目录不分类，正文只增不改；wiki 页面不写作者、来源和日期，正文不放站内链接，关联靠头部的 tags（词表见 AGENTS.md）和 entities；按知识点更新已有页面；写完跑 `python3 tools/lint.py`，必须 0 ERROR。
