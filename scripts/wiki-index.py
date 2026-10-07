#!/usr/bin/env python3
"""index.md 生成器 —— 扫描 wiki/ 全部页面 frontmatter，按分类重建目录。

index.md 由本脚本生成，禁止手改：入库四件套的"登记"动作 = 重跑本脚本。
CI 用 --check 校验漂移（有人手改或入库后没重新生成都会报出来）。

生成物只依赖页面内容，不写入运行日：updated 取页内最新 updated，页脚不带日期；
否则 --check 在“非重建当天”必然误报（内容没变也会红）。

用法:
    python3 scripts/wiki-index.py            # 重建 wiki/index.md
    python3 scripts/wiki-index.py --check    # 只校验：与页面现状不一致则退出码 1
    python3 scripts/wiki-index.py --diff     # 打印差异，不写文件
    python3 scripts/wiki-index.py --root X   # 指定库根（默认仓库根）

分类结构（Overview / Collections / Entities / Concepts / Sources / 其他）由
WIKI.md 的目录映射驱动：新增子目录类型后无需改本脚本。
"""
import argparse
import collections
import datetime
import difflib
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wiki_schema import fm_value, frontmatter, load_schema

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTRO = ("全部 wiki 页面的目录（当前 {n} 页）。入库触发方式与定级规则见库根 `WIKI.md`。\n\n"
         "> 本文件由 `scripts/wiki-index.py` 生成，请勿手改；入库后重新生成，CI 以 `--check` 校验。")


def collect(schema, wiki_dir):
    """返回页面元信息列表 [{rel, title, type, updated, parts}]，跳过 index 自身。"""
    metas = []
    for dirpath, _dirs, files in os.walk(wiki_dir):
        for f in sorted(files):
            if not f.endswith(".md"):
                continue
            path = os.path.join(dirpath, f)
            rel = os.path.relpath(path, wiki_dir).replace(os.sep, "/")[:-3]
            if rel == "index":
                continue
            fm = frontmatter(path)
            if fm is None:
                print("⚠️ 缺 frontmatter，未收入目录: " + rel, file=sys.stderr)
                continue
            metas.append({
                "rel": rel,
                "title": fm_value(fm, "title") or rel,
                "type": fm_value(fm, "type") or "?",
                "updated": fm_value(fm, "updated") or "?",
                "parts": rel.split("/"),
            })
    metas.sort(key=lambda p: p["rel"])
    return metas


def entry(p):
    return "- [[%s|%s]]（updated: %s）" % (p["rel"], p["title"], p["updated"])


def build(schema, metas, created):
    latest = max([p["updated"] for p in metas if p["updated"] != "?"] or [created])
    ent_dirs = list(schema["entity_dir_type"].items())      # [(dir, type)]
    con_dirs = list(schema["concept_dir_type"].items())

    def by_type(ty):
        return [p for p in metas if p["type"] == ty]

    def by_dir(prefix):
        return [p for p in metas if p["parts"][0] == prefix]

    out = ["---", "title: LLM Wiki Index", "type: index",
           "created: " + created, "updated: " + latest, "---", "",
           "# LLM Wiki Index", "", INTRO.format(n=len(metas)), ""]

    def emit_group(title, pages, sub=None):
        """sub: None 平铺；'entities' / 'concepts' / 'sources' 按第二级目录分小节。"""
        out.append("## " + title)
        out.append("")
        if sub is None:
            out.extend([entry(p) for p in pages] or ["（暂无）"])
            out.append("")
            return
        subdirs = {"entities": ent_dirs, "concepts": con_dirs}.get(sub)
        if subdirs is None:   # sources：按出现的目录名动态分组
            names = sorted({p["parts"][1] for p in pages if len(p["parts"]) >= 3})
        else:
            names = [d for d, _t in subdirs]
            names += sorted({p["parts"][1] for p in pages
                             if len(p["parts"]) >= 3 and p["parts"][1] not in names})
        for name in names:
            sub_pages = [p for p in pages
                         if len(p["parts"]) >= 3 and p["parts"][1] == name]
            out.append("### " + name.capitalize())
            out.append("")
            out.extend([entry(p) for p in sub_pages] or ["（暂无）"])
            out.append("")
        top = [p for p in pages if len(p["parts"]) < 3]
        if top:
            out.append("### 未分组")
            out.append("")
            out.extend(entry(p) for p in top)
            out.append("")

    emit_group("Overview", by_type("overview"))
    emit_group("Collections", by_dir("collections"))
    emit_group("Entities", by_dir("entities"), "entities")
    emit_group("Concepts", by_dir("concepts"), "concepts")
    emit_group("Sources", by_dir("sources"), "sources")

    others = [p for p in metas if p["parts"][0]
              in ("analyses", "comparisons", "questions")]
    emit_group("其他（analyses / comparisons / questions）", others)

    # 未启用分类：schema 目录映射中当前 0 页的目录
    used = {(p["parts"][0], p["parts"][1]) for p in metas if len(p["parts"]) >= 2}
    idle = ["entities/" + d for d, _t in ent_dirs if ("entities", d) not in used]
    idle += ["concepts/" + d for d, _t in con_dirs if ("concepts", d) not in used]
    idle += [d for d in ("analyses", "comparisons", "questions", "collections")
             if not by_dir(d)]
    out.append("## 未启用分类")
    out.append("")
    out.append("、".join("`%s`" % x for x in idle) + "（暂无页面，按需创建）"
               if idle else "（全部分类均有页面）")
    out.append("")
    out.append("---")
    out.append("*由 scripts/wiki-index.py 生成；内容以各页 frontmatter 为准，入库后重跑本脚本更新*")
    out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="index.md 生成器（详见 docstring）。")
    ap.add_argument("--check", action="store_true",
                    help="只校验不写文件；与页面现状不一致退出码 1")
    ap.add_argument("--diff", action="store_true", help="打印差异，不写文件")
    ap.add_argument("--root", default=ROOT)
    args = ap.parse_args()

    root = os.path.abspath(os.path.expanduser(args.root))
    wiki_dir = os.path.join(root, "wiki")
    idx_path = os.path.join(wiki_dir, "index.md")
    if not os.path.isdir(wiki_dir):
        print("!! 找不到库根: " + root)
        return 2

    schema, origin = load_schema(root)
    metas = collect(schema, wiki_dir)
    today = datetime.date.today().isoformat()

    old = open(idx_path, encoding="utf-8").read() if os.path.isfile(idx_path) else ""
    created = fm_value(frontmatter(idx_path), "created") \
        if os.path.isfile(idx_path) else None
    new = build(schema, metas, created or today)

    if args.diff:
        sys.stdout.writelines(difflib.unified_diff(
            old.splitlines(True), new.splitlines(True),
            fromfile="index.md(现)", tofile="index.md(新)"))
        return 0
    if new == old:
        print("index.md 已是最新（%d 页）" % len(metas))
        return 0
    if args.check:
        print("!! index.md 与页面现状不一致，请运行 python3 scripts/wiki-index.py 重建")
        return 1
    with open(idx_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    print("已重建 wiki/index.md（%d 页；schema 来源: %s）" % (len(metas), origin))
    return 0


if __name__ == "__main__":
    sys.exit(main())
