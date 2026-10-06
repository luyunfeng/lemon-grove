# 安装与运行 V1.1.0

V1 是早期风格参考。新任务推荐 [V2.3.0](../lark-tech-diagrams-v2/INSTALL.md)，其中包含 16 类确定性排版器、字体和离线复现检查。V1 主要由 Agent 按参考风格创作 SVG，再由助手检查；不提供 V2 的参考图逐字节复现保证。

## 依赖与安装

在仓库根目录执行下面的命令，将目录链接到 Codex 技能目录。已有同名安装时先处理备份，避免覆盖当前修改。

```sh
diagram_skill_root="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$diagram_skill_root"
ln -s "$PWD/skills/lark-architecture-diagrams" "$diagram_skill_root/lark-architecture-diagrams"
```

也可以复制整个目录到 Agent 的技能目录，或直接读取 `SKILL.md`。需要 Python 3、Node.js、npx；检查助手调用固定版本 `@larksuite/whiteboard-cli@0.2.13`。npx 使用调用方的 npm registry 配置，需要可访问的镜像或已安装的工具；必要时可仅对当前命令设置 `npm_config_registry=https://registry.npmjs.org`，不需要复制作者的配置或缓存。飞书操作还需要当前用户自行配置的官方 CLI、身份和权限。

## 本地示例检查

```sh
diagram_task_dir="$(mktemp -d)"
python3 skills/lark-architecture-diagrams/scripts/diagram.py check \
  --spec skills/lark-architecture-diagrams/assets/er/example.json \
  --svg skills/lark-architecture-diagrams/assets/er/example.svg \
  --out "$diagram_task_dir/checks"
```

助手校验节点、关系、文字覆盖及工具转换后的原生文字。实际查看输出 PNG；本地通过不代表远端已经验证。新图按照 [结构约定](references/structure.md)和图型参考构建，不能把示例直接当成用户系统。

## 飞书交付与版本边界

V1 保留旧版空画板发布助手，参数中的 profile、应用 ID 和画板 token 均须由调用方显式提供；仓库不保存作者的实际账号、目录、文档或授权状态。使用现有飞书 Skill 获取目标资源和处理认证后，再按 `SKILL.md` 中的命令操作。

本版助手只填写空画板，不支持覆盖用户已有内容。目标端仍需回读并看图。V1 的历史发布封装不属于 V2，V2 统一交接现有工具；不要在两版间混用输入字段或发布命令。
