#!/usr/bin/env python3
"""新页脚手架 —— 按 schema 在正确目录建页，自动填好 frontmatter。

从源头消灭 lint 第 3 / 8 / 9 项要抓的错误（缺 frontmatter、缺 type、子类型
与目录不符），比事后检查便宜。只建文件，不改 index.md / log.md（见收尾提示）。

用法:
    python3 scripts/wiki-new.py collection <slug> [--title 标题]
    python3 scripts/wiki-new.py entity <slug> --entity-type person
    python3 scripts/wiki-new.py concept <slug> --concept-type theory
    python3 scripts/wiki-new.py source <slug> [--source-dir articles] [--evidence-level C]
    python3 scripts/wiki-new.py analysis|comparison|question <slug>

选项:
    --title           页标题（默认用 slug）
    --entity-type     person / organization / product / technology / event
    --concept-type    theory / method / framework / metric / principle
    --source-dir      sources 下的子目录（默认 articles）
    --source-type     source 页 source_type 自由文本（默认 待填）
    --evidence-level  A / B / C / D / N/A（collection 与 source 必填，默认 C）
    --related         逗号分隔的兄弟页路径（写入 related:）
    --date            覆盖 created/updated 日期（默认今天）
    --root            库根目录（默认仓库根）
"""
import argparse
import datetime
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wiki_schema import load_schema

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def fail(msg):
    print("!! " + msg)
    return 2


def main():
    ap = argparse.ArgumentParser(
        description="新页脚手架：按 schema 建页并填好 frontmatter。")
    ap.add_argument("type",
                    choices=["collection", "entity", "concept", "source",
                             "analysis", "comparison", "question"])
    ap.add_argument("slug", help="文件名（小写字母/数字/连字符，不含 .md）")
    ap.add_argument("--title")
    ap.add_argument("--entity-type")
    ap.add_argument("--concept-type")
    ap.add_argument("--source-dir", default="articles")
    ap.add_argument("--source-type", default="待填")
    ap.add_argument("--evidence-level", default="C",
                    choices=["A", "B", "C", "D", "N/A"])
    ap.add_argument("--related", default="")
    ap.add_argument("--date")
    ap.add_argument("--root", default=ROOT)
    args = ap.parse_args()

    root = os.path.abspath(os.path.expanduser(args.root))
    if not os.path.isdir(os.path.join(root, "wiki")):
        return fail("找不到库根: " + root)
    if not SLUG_RE.match(args.slug):
        return fail("slug 只能含小写字母 / 数字 / 连字符: " + args.slug)

    schema, origin = load_schema(root)
    today = args.date or datetime.date.today().isoformat()

    # 目标目录与模板
    repl = {
        "{{TITLE}}": args.title or args.slug,
        "{{DATE}}": today,
        "{{ENTITY_TYPE}}": args.entity_type or "",
        "{{CONCEPT_TYPE}}": args.concept_type or "",
        "{{SOURCE_TYPE}}": args.source_type,
        "{{EVIDENCE_LEVEL}}": args.evidence_level,
        "{{PAGE_TYPE}}": args.type,
        "{{RELATED}}": "[%s]" % ", ".join(
            x.strip() for x in args.related.split(",") if x.strip()),
    }

    if args.type == "collection":
        subdir, tpl = "collections", "collection"
    elif args.type == "entity":
        et = args.entity_type
        if et not in schema["entity_types"]:
            return fail("--entity-type 必填且须在 %s 内（schema 来源: %s）"
                        % (schema["entity_types"], origin))
        dir_for = {v: k for k, v in schema["entity_dir_type"].items()}
        if et not in dir_for:
            return fail("entity_type=%s 无目录映射，请先在 WIKI.md 的 "
                        "entities.dir_mapping 中登记" % et)
        subdir, tpl = "entities/" + dir_for[et], "entity"
    elif args.type == "concept":
        ct = args.concept_type
        if ct not in schema["concept_types"]:
            return fail("--concept-type 必填且须在 %s 内（schema 来源: %s）"
                        % (schema["concept_types"], origin))
        dir_for = {v: k for k, v in schema["concept_dir_type"].items()}
        if ct not in dir_for:
            return fail("concept_type=%s 无目录映射，请先在 WIKI.md 的 "
                        "concepts.dir_mapping 中登记" % ct)
        subdir, tpl = "concepts/" + dir_for[ct], "concept"
    elif args.type == "source":
        subdir, tpl = "sources/" + args.source_dir, "source"
    else:
        subdir = {"analysis": "analyses", "comparison": "comparisons",
                  "question": "questions"}[args.type]
        tpl = "generic"

    # 模板是工具的一部分，随脚本走（不从目标库根找，目标库可能不是本仓库）
    tpl_path = os.path.join(ROOT, "templates", tpl + ".md")
    if not os.path.isfile(tpl_path):
        tpl_path = os.path.join(ROOT, "templates", "generic.md")
    if not os.path.isfile(tpl_path):
        return fail("找不到模板: " + tpl_path)

    target_dir = os.path.join(root, "wiki", *subdir.split("/"))
    target = os.path.join(target_dir, args.slug + ".md")
    if os.path.exists(target):
        return fail("目标已存在，拒绝覆盖: " + target)

    body = open(tpl_path, encoding="utf-8").read()
    for k, v in repl.items():
        body = body.replace(k, v)
    if "{{" in body:
        leftover = sorted(set(re.findall(r"\{\{\w+\}\}", body)))
        return fail("模板存在未替换占位符 %s（缺对应参数）" % leftover)

    os.makedirs(target_dir, exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)

    rel = os.path.relpath(target, root).replace(os.sep, "/")
    print("已创建: " + rel)
    print("schema 来源: " + origin)
    print("\n收尾四件套（入库规则）：")
    print("  1. raw/<分类>/<主题>-<日期>.md   原始快照（数字标抓取日期）")
    print("  2. wiki/index.md                登记本页")
    print("  3. log.md                       追加操作留痕")
    print("  4. python3 scripts/wiki-lint.py 复跑确认全绿后 git commit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
