# 安装与验证 V2.3.0

以下命令在本仓库根目录执行。先克隆仓库并进入目录；不需要复制旧聊天或实验目录。

```sh
git clone https://github.com/luyunfeng/lemon-grove.git
cd lemon-grove
```

## 安装 Python 依赖

核心绘图需要 Python 3.11+ 和 Pillow；完整本地 PNG 预览还需要 CairoSVG、Cairo 和兼容 Fontconfig 的字体后端。当前完整验证使用 Python 3.12 和 Linux。系统运行库由环境包管理器安装，具体条件见 [运行环境](references/runtime.md)。

将虚拟环境放在仓库之外：

```sh
diagram_venv="${XDG_CACHE_HOME:-$HOME/.cache}/technical-diagrams-venv"
python3 -m venv "$diagram_venv"
"$diagram_venv/bin/python" -m pip install -r skills/lark-tech-diagrams-v2/requirements.txt
```

如果系统不提供 `venv`/`ensurepip`，先通过系统包管理器补齐对应 Python 的虚拟环境支持。只输出 SVG 时不加载 CairoSVG，但仍须安装 Pillow；不能将无 PNG 的状态当作已经完成视觉审查。

## 让 Agent 找到 Skill

Codex 示例使用软链，目标目录已有同名安装时先备份并处理旧安装：

```sh
diagram_skill_root="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$diagram_skill_root"
ln -s "$PWD/skills/lark-tech-diagrams-v2" "$diagram_skill_root/lark-tech-diagrams-v2"
```

也可以复制整个 `lark-tech-diagrams-v2/` 到所用 Agent 的技能目录，或直接让 Agent 读取仓库中的 `SKILL.md`。复制时保留 `assets/fonts/`、字体许可、模板和脚本。运行脚本使用已安装依赖的 Python 解释器。

## 检查参考图复现

```sh
diagram_task_dir="$(mktemp -d)"
"$diagram_venv/bin/python" skills/lark-tech-diagrams-v2/scripts/check_examples.py \
  --out "$diagram_task_dir/reference-check"
```

检查应返回 `passed: true`，16 类 `svg_matches_demo` 都为 `true`，几何/语义错误为 0。产物和报告保存在临时任务目录；此项只验证同输入复现，不能替代陌生业务和目标端的实际看图。

## 画一张图

```sh
"$diagram_venv/bin/python" skills/lark-tech-diagrams-v2/scripts/quick_draw.py prepare \
  --type swimlane --out "$diagram_task_dir/model.json"
# 编辑 model.json：将示例对象、关系、条件和图例替换为本次需求。
"$diagram_venv/bin/python" skills/lark-tech-diagrams-v2/scripts/quick_draw.py render \
  --spec "$diagram_task_dir/model.json" --out "$diagram_task_dir/output"
```

输出 SVG、PNG、布局、检查报告及带真实文件路径的 `result.json`。仅需要 SVG 时给 `render` 添加 `--svg-only`。实际查看 PNG 并核对原始逻辑后再交付。

## 交付飞书

另行配置当前用户可用的官方 CLI 和 `lark-doc`、`lark-whiteboard`、`lark-shared` 等能力。身份、应用、权限和目标文档由调用方配置，不从示例继承；用户要求飞书时才调用这些能力。

按 [工具交接](references/tool-handoff.md) 将既有 SVG 交给工具，再查看服务端 PNG 和原生文字回读。绘图脚本不创建文档、不授权、不上传，也不修改现有画板。
