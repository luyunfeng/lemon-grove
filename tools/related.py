#!/usr/bin/env python3
"""按标签和实体找相关页面（只读）。

用法（在仓库根目录执行，或从任意目录调用本脚本）:
  python3 tools/related.py wiki/concepts/verification.md   # 与该页标签或实体有交集的页面
  python3 tools/related.py --tag agent-skill               # 打了某个标签的页面
  python3 tools/related.py --entity codex                  # 涉及某个实体的页面
可以同时给多个 --tag / --entity。结果按共享的标签和实体数量从多到少排序。
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"


def head(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    fm = m.group(1) if m else ""

    def field(k):
        mm = re.search(rf"^{k}:\s*\[(.*?)\]", fm, re.M)
        return {v.strip() for v in mm.group(1).split(",") if v.strip()} if mm else set()

    t = re.search(r"^title:\s*(.+)$", fm, re.M)
    return (t.group(1).strip() if t else path.stem), field("tags"), field("entities")


def main():
    ap = argparse.ArgumentParser(description="按标签和实体找相关页面")
    ap.add_argument("page", nargs="?", help="页面路径，如 wiki/concepts/verification.md")
    ap.add_argument("--tag", action="append", default=[], help="标签，可重复")
    ap.add_argument("--entity", action="append", default=[], help="实体 slug，可重复")
    a = ap.parse_args()
    if not (a.page or a.tag or a.entity):
        ap.error("请给一个页面路径，或 --tag / --entity")

    pages = {p: head(p) for p in sorted(WIKI.glob("*/*.md")) + [WIKI / "overview.md"] if p.exists()}
    want_tags, want_ents, self_path = set(a.tag), set(a.entity), None
    if a.page:
        pp = Path(a.page)
        self_path = (pp if pp.is_absolute() else Path.cwd() / pp).resolve()
        if not self_path.exists():
            self_path = (ROOT / a.page).resolve()
        if self_path not in pages:
            sys.exit(f"找不到页面：{a.page}")
        _, t, e = pages[self_path]
        want_tags |= t
        want_ents |= e
        if self_path.parent.name == "entities":
            want_ents.add(self_path.stem)

    rows = []
    for p, (title, tags, ents) in pages.items():
        if p == self_path:
            continue
        st, se = tags & want_tags, ents & want_ents
        if p.parent.name == "entities" and p.stem in want_ents:
            se = se | {p.stem}
        if st or se:
            rows.append((len(st) + len(se), p, title, st, se))
    rows.sort(key=lambda r: (-r[0], str(r[1])))
    print(f"查询：tags={sorted(want_tags)} entities={sorted(want_ents)}，命中 {len(rows)} 页")
    for n, p, title, st, se in rows:
        why = "，".join(x for x in [("标签 " + " ".join(sorted(st))) if st else "", ("实体 " + " ".join(sorted(se))) if se else ""] if x)
        print(f"{n}  {p.relative_to(ROOT).as_posix():45s} {title}  （{why}）")


if __name__ == "__main__":
    main()
