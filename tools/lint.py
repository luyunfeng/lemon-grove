#!/usr/bin/env python3
"""LLM Wiki 机械体检脚本（只读，不修改任何文件）。

用法: python3 tools/lint.py [知识库根目录]      # 默认是本脚本所在仓库的根目录
检查: 目录白名单、头部四项（title/type/tags/entities）、标签词表（读 AGENTS.md 3.2）、
      entities 对应实体页、正文站内链接（只有 index.md 允许）、index 一致性、
      作者 / 来源 / 日期 / 人名痕迹、外链、敏感信息、raw 结构与头部元数据。
退出码: 有 ERROR 返回 1，否则 0。
"""
import re
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ["title", "type", "tags", "entities"]
TYPES = {"concept", "entity", "roadmap", "synthesis", "overview"}
SUBDIRS = {"concepts", "entities", "roadmaps", "syntheses"}
SPECIAL = {"index.md", "log.md"}
RAW_SUBDIRS = {"assets"}
TAGS_BEGIN, TAGS_END = "<!-- tags:begin -->", "<!-- tags:end -->"
TAG_ROW_RE = re.compile(r"^\|\s*`([a-z0-9][a-z0-9-]*)`\s*\|")
# 页面不写作者、来源、时间线（AGENTS.md 3.1）。命中只报 WARN，由人判断。
TRACE_RE = re.compile(r"作者|出处|来源|笔记里|某笔记|这篇笔记|多个来源|认识演进|延伸阅读|参考资料|"
                      r"(?<!\d)20\d\d[-./年]\d{1,2}|(?<![\d.])\d{1,2} ?月(?:份|的)?(?:笔记|文章|发布)")
NAME_RE = re.compile(r"Karpathy|Lilian Weng|Weng|Pocock|Affaan|姚顺宇", re.I)
# 仓库名与安装命令不算人名归属
NAME_ALLOW_RE = re.compile(r"mattpocock/skills|mattpocock-skills|setup-matt-pocock-skills", re.I)
# 敏感信息：内网地址、内部域名、内部 IM 链接、常见密钥格式。命中报 ERROR。
SENSITIVE_RE = re.compile(
    r"(?<![\d.])(?:10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}(?![\d.])|"
    r"byted\.org|bytedance\.net|larkoffice|feishu\.cn|larksuite|feishu://|"
    r"(?:AKIA|AKLT)[A-Za-z0-9]{12,}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|xox[bp]-|-----BEGIN [A-Z ]*PRIVATE KEY")
RAW_META_RE = re.compile(r"^> ?- ?(来源|作者|发布日期|收录日期|原文链接)\s*[:：]", re.M)
DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")
# Scan personal environment hints in all Markdown files, including root docs/skills.
PERSONAL_ENV_RE = re.compile(
    r"/(?:data\d+/)?home/[^/\s`]+/|/Users/[^/\s`]+/|"
    r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|"
    r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)")
INTERNAL_SOURCE_RE = re.compile(r"内部(?:链接|域名|文档链接|来源名称)已移除|(?:来源|原文).*Feishu Wiki|飞书(?:文档增量|妙记)", re.I)
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
WIKILINK_RE = re.compile(r"\[\[[^\]]+\]\]")
CODE_RE = re.compile(r"```.*?```|`[^`\n]*`", re.S)
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def parse_frontmatter(text):
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    raw, body = text[4:end], text[end + 4:]
    fm, key = {}, None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).split(" #")[0].strip()
            if val.startswith("[") and val.endswith("]"):
                fm[key] = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
            elif val == "":
                fm[key] = []
            else:
                fm[key] = val.strip("'\"")
        elif key and line.strip().startswith("- "):
            if not isinstance(fm.get(key), list):
                fm[key] = []
            fm[key].append(line.strip()[2:].split(" #")[0].strip().strip("'\""))
    return fm, body


def load_vocab(root):
    agents = root / "AGENTS.md"
    if not agents.exists():
        return None
    text = agents.read_text(encoding="utf-8")
    if TAGS_BEGIN not in text or TAGS_END not in text:
        return None
    block = text.split(TAGS_BEGIN, 1)[1].split(TAGS_END, 1)[0]
    return {m.group(1) for line in block.splitlines() if (m := TAG_ROW_RE.match(line.strip()))}


def links_in(text):
    text = COMMENT_RE.sub("", CODE_RE.sub("", text))
    return [t for t in LINK_RE.findall(text)]


def is_external(target):
    return bool(re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I))


def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_ROOT
    wiki, raw = root / "wiki", root / "raw"
    if not wiki.is_dir():
        print(f"ERROR: 找不到 {wiki}")
        return 1
    errors, warns = [], []
    vocab = load_vocab(root)
    if not vocab:
        errors.append("AGENTS.md 里找不到标签词表（<!-- tags:begin --> … <!-- tags:end -->）")
        vocab = set()
    for p in sorted(root.rglob("*.md")):
        relpath = p.relative_to(root)
        if any(part.startswith(".") for part in relpath.parts):
            continue
        for number, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if SENSITIVE_RE.search(line) or PERSONAL_ENV_RE.search(line):
                # Report location only; a found credential must not be echoed.
                errors.append(f"{relpath.as_posix()}:{number}: 疑似敏感信息或个人环境线索（内容已隐藏）")
            if relpath.parts[0] == "raw" and INTERNAL_SOURCE_RE.search(line):
                warns.append(f"{relpath.as_posix()}:{number}: 疑似内部来源痕迹（内容已隐藏）")
    entity_slugs = {p.stem for p in (wiki / "entities").glob("*.md")} if (wiki / "entities").is_dir() else set()
    pages = sorted(wiki.rglob("*.md"))
    articles = [p for p in pages if p.relative_to(wiki).as_posix() not in SPECIAL]

    for d in sorted(x for x in wiki.iterdir() if x.is_dir()):
        if d.name not in SUBDIRS:
            errors.append(f"wiki/{d.name}/: 不在目录白名单 {sorted(SUBDIRS)} 内")

    for p in pages:
        rel = p.relative_to(root).as_posix()
        wrel = p.relative_to(wiki)
        name = wrel.as_posix()
        text = p.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        if len(wrel.parts) > 2:
            errors.append(f"{rel}: wiki 只允许一级子目录")
        if name not in SPECIAL:
            if fm is None:
                errors.append(f"{rel}: 缺少 frontmatter")
                fm = {}
            keys = list(fm.keys())
            missing = [k for k in REQUIRED if k not in fm]
            extra = [k for k in keys if k not in REQUIRED]
            if missing:
                errors.append(f"{rel}: 头部缺 {missing}（只允许 title / type / tags / entities 四项）")
            if extra:
                errors.append(f"{rel}: 头部多出 {extra}（只允许 title / type / tags / entities 四项）")
            if fm.get("type") and fm["type"] not in TYPES:
                errors.append(f"{rel}: 未知 type={fm['type']}")
            for k in ("tags", "entities"):
                if k in fm and not isinstance(fm[k], list):
                    errors.append(f"{rel}: {k} 必须是列表，如 {k}: [a, b]")
            tags = fm.get("tags") if isinstance(fm.get("tags"), list) else []
            if "tags" in fm and not tags:
                errors.append(f"{rel}: tags 不能为空")
            for t in tags:
                if t not in vocab:
                    errors.append(f"{rel}: 标签 {t!r} 不在 AGENTS.md 词表里（先加进词表再用）")
            ents = fm.get("entities") if isinstance(fm.get("entities"), list) else []
            for e in ents:
                if e not in entity_slugs:
                    errors.append(f"{rel}: entities 里的 {e!r} 没有对应的 wiki/entities/{e}.md")
            if wrel.parts[0] == "entities" and p.stem not in ents:
                warns.append(f"{rel}: 实体页的 entities 应包含自己（{p.stem}）")
        content = body if fm is not None else text
        plain = COMMENT_RE.sub("", content)
        # 站内链接：只有 index.md 允许
        for target in links_in(content):
            if is_external(target) or target.startswith("#"):
                continue
            if name != "index.md":
                errors.append(f"{rel}: 正文有站内链接 -> {target}（只有 index.md 允许放链接）")
                continue
            dest = (p.parent / target.split("#")[0]).resolve()
            if raw == dest or raw in dest.parents:
                errors.append(f"{rel}: 链接指向 raw -> {target}")
            elif not dest.exists():
                errors.append(f"{rel}: 死链 -> {target}")
        if WIKILINK_RE.search(CODE_RE.sub("", plain)):
            errors.append(f"{rel}: 有 [[wikilink]]（不允许）")
        if name != "log.md":
            for line in plain.splitlines():
                m = TRACE_RE.search(line) or NAME_RE.search(NAME_ALLOW_RE.sub("", line))
                if m:
                    warns.append(f"{rel}: 疑似作者 / 来源 / 日期痕迹「{m.group(0)}」: {line.strip()[:60]}")
            if re.search(r"\]\(https?://", plain):
                warns.append(f"{rel}: 含外链（页面不放外链）")

    # index 一致性：每页都要登记
    index = wiki / "index.md"
    indexed = set()
    if index.exists():
        for t in links_in(index.read_text(encoding="utf-8")):
            if not is_external(t):
                indexed.add((wiki / t.split("#")[0]).resolve())
    else:
        errors.append("wiki/index.md 不存在")
    for p in articles:
        if p.resolve() not in indexed:
            errors.append(f"{p.relative_to(root).as_posix()}: 未登记到 wiki/index.md")

    # raw：一级目录不分类，只允许 assets/；头部不写元数据，文件名不带日期
    raw_files = []
    if raw.is_dir():
        for d in sorted(x for x in raw.iterdir() if x.is_dir()):
            if d.name not in RAW_SUBDIRS:
                errors.append(f"raw/{d.name}/: raw 下除 assets/ 外不能有子目录（原始资料一律放 raw/ 一级目录）")
        for d in sorted(x for x in (raw / "assets").rglob("*") if x.is_dir()) if (raw / "assets").is_dir() else []:
            errors.append(f"{d.relative_to(root).as_posix()}/: raw/assets 下不再分子目录")
        raw_files = [r for r in sorted(raw.rglob("*")) if r.is_file() and r.name != ".gitkeep"]
        for r in raw_files:
            rr = r.relative_to(root).as_posix()
            if DATE_PREFIX_RE.match(r.name):
                warns.append(f"{rr}: raw 文件名不应带日期前缀")
            if r.suffix == ".md":
                txt = r.read_text(encoding="utf-8")
                if RAW_META_RE.search("\n".join(txt.splitlines()[:15])):
                    warns.append(f"{rr}: raw 头部不应写作者 / 来源 / 日期等元数据")

    print(f"LLM Wiki lint @ {root}")
    print(f"页面 {len(articles)} 个（不含 index/log），实体 {len(entity_slugs)} 个，标签词表 {len(vocab)} 个，raw {len(raw_files)} 个")
    for e in errors:
        print(f"ERROR  {e}")
    for w in warns:
        print(f"WARN   {w}")
    print(f"结果: {len(errors)} ERROR, {len(warns)} WARN")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
