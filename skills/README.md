# 技能目录

这里保存知识库配套的可复用技能源码，每个技能一个子目录。知识页放在 `wiki/`，技能的执行规则与使用说明放在这里。

## 已收录

| 技能 | 用途 | 入口 |
|---|---|---|
| `llm-wiki` | 定位知识库并读取根目录规则，支持后续查询、收录与体检 | [技能入口](llm-wiki/SKILL.md) |
| `speak-human` | 保留原意，把中文草稿整理成有逻辑的 Markdown 要点 | [使用说明](speak-human/README.md) · [技能入口](speak-human/SKILL.md) |

## 安装与更新

将所需的**完整技能目录**复制或链接到宿主使用的技能目录，保持 `SKILL.md` 与 `references/` 等资源的相对位置。具体目录以当前宿主配置为准。

在使用个人 `skills` 目录的 Codex 环境中，可从本仓库根目录执行以下 Bash 命令。示例安装 `speak-human`；安装 `llm-wiki` 时替换第一行的技能名。

```bash
skill_name=speak-human
skill_source="$(pwd)/skills/$skill_name"
skill_parent="${CODEX_HOME:-$HOME/.codex}/skills"
skill_target="$skill_parent/$skill_name"

if [ ! -f "$skill_source/SKILL.md" ]; then
  printf '%s\n' '请在知识库根目录执行，并检查技能名称。'
elif [ -e "$skill_target" ] || [ -L "$skill_target" ]; then
  printf '%s\n' '目标已存在，请先核对内容并备份，避免覆盖本地修改。'
else
  mkdir -p "$skill_parent" && ln -s "$skill_source" "$skill_target"
fi
```

按宿主提供的方式重新加载技能后，使用技能名调用。软链接依赖仓库位置保持稳定；仓库移动后需要重新建立链接。复制安装的技能需要在源码更新后同步副本。

后续修改以仓库源码为准，遵循根目录 `AGENTS.md` 的确认与 PR 流程。技能变更合入并同步到本地后，软链接会读取更新后的内容；同一宿主只保留一份同名技能入口，避免加载到不同版本。

## 新增技能

1. 创建 `skills/<skill-name>/`，名称用小写英文 kebab-case。
2. 提供 `SKILL.md` 与 `README.md`。前者写触发条件、行为和必要约束；后者写用途、安装、调用示例、验证与维护方式。
3. 只有实际需要时才增加 `references/`、`agents/`、`scripts/` 等目录；使用相对引用，避免依赖原始会话或某台机器。
4. 在上方清单登记，检查示例是否保留原意、引用是否可访问，以及包内是否包含敏感信息，再按知识库流程提交 PR。

需要生成、联网或写入外部系统的技能，应在自己的说明中写清实际依赖与操作范围；目录本身不授予额外权限。
