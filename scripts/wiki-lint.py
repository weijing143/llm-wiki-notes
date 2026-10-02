#!/usr/bin/env python3
"""归档层自检（只读）—— 本仓库的结构健康检查。

用法:
    python3 scripts/wiki-lint.py [root]      # root 默认为仓库根目录

检查十三类：
  1. 断链          [[路径]] 指向不存在的页
  2. 孤儿页        无任何入链（index.md 的链接也算入链）
  3. 缺 frontmatter
  4. updated 与文件 mtime 漂移
  5. index.md 重复的 H2 区块 / 重复条目
  6. log.md 漏记   （最新内容页日期 > 最新日志日期）
  7. 定级完整性    （source/collection 必填 evidence_level；含 🟢🟡🔴 的表须自带图例）
  8. type 完整性   （每页必填 type，且值在允许集合内）
  9. 子类型一致性  （entity 必填 entity_type、concept 必填 concept_type 且与父目录一致；source 必填 source_type）
  10. 转述级警示   （evidence_level 为 C/D 的页正文必须含 ⚠️）
  11. 等级引用可溯 （"X 级（出处：…）"的等级字母合法、出处页存在）
  12. 逐条覆盖     （collection 页核查表的主张行必须带吻合度或等级引用；未全覆盖只告警、不判死）
  13. 结构计数     （文件数 / 磁盘占用 / 各分类页数）
纯标准库、只读、不改任何文件。退出码恒为 0，除非库根不存在。
"""
import os
import re
import sys
import datetime
import collections

# Windows GBK 控制台打印 emoji 会 UnicodeEncodeError，强制 UTF-8 输出
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
    print(__doc__)
    sys.exit(0)

_DEFAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.abspath(os.path.expanduser(sys.argv[1])) if len(sys.argv) > 1 else _DEFAULT_ROOT
WIKI = os.path.join(ROOT, "wiki")
LOG = os.path.join(ROOT, "log.md")
IDX = os.path.join(WIKI, "index.md")

LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
EMOJI_RE = re.compile("🟢|🟡|🔴")
DATE_RE = re.compile(r"\[?(\d{4}-\d{2}-\d{2})")
GRADE_REF_RE = re.compile(r"([A-Z])\s*级（出处：([^）]+)）")
NUM_ROW_RE = re.compile(r"^\|\s*#?\d+\s*\|")
SEP_ROW_RE = re.compile(r"^\|[\s:\-—|]+\|$")
BG_RE = re.compile(r"—\s*背景共识")

PAGE_TYPES = {"index", "overview", "collection", "entity", "concept", "source",
              "analysis", "comparison", "question"}
ENTITY_TYPES = {"person", "organization", "product", "technology", "event"}
CONCEPT_TYPES = {"theory", "method", "framework", "metric", "principle"}
ENTITY_DIR_TYPE = {"people": "person", "organizations": "organization",
                   "products": "product", "technologies": "technology",
                   "events": "event"}
CONCEPT_DIR_TYPE = {"theories": "theory", "methods": "method",
                    "frameworks": "framework", "metrics": "metric",
                    "principles": "principle"}


def collect_pages():
    pages = {}
    for dirpath, _dirs, files in os.walk(WIKI):
        for f in files:
            if f.endswith(".md"):
                rel = os.path.relpath(os.path.join(dirpath, f), WIKI)
                rel = rel.replace(os.sep, "/")[:-3]   # 统一正斜杠，键与 [[链接]] 一致
                pages[rel] = os.path.join(dirpath, f)
    return pages


def read(path):
    return open(path, encoding="utf-8", errors="ignore").read()


def frontmatter(path):
    txt = read(path)
    if not txt.startswith("---"):
        return None
    end = txt.find("\n---", 3)
    return txt[3:end] if end != -1 else None


def fm_value(fm, name):
    m = re.search(r"^%s:\s*(.+)$" % name, fm or "", re.M)
    return m.group(1).strip() if m else None


def normalize(target):
    t = target.split("|")[0].strip()
    return t[len("wiki/"):] if t.startswith("wiki/") else t


def day(path):
    return datetime.date.fromtimestamp(os.path.getmtime(path))


def section(title):
    print("\n== " + title + " ==")


def main():
    if not os.path.isdir(WIKI):
        print("!! 找不到库根:", ROOT)
        return 1
    pages = collect_pages()
    index_txt = read(IDX) if os.path.isfile(IDX) else ""

    # 1 + 2. 断链 / 孤儿页
    inbound = collections.defaultdict(set)
    broken = []
    for rel, path in pages.items():
        for raw in LINK_RE.findall(read(path)):
            tgt = normalize(raw)
            if tgt in pages:
                inbound[tgt].add(rel)
            else:
                broken.append((rel, raw.strip()))
    for raw in LINK_RE.findall(index_txt):
        tgt = normalize(raw)
        if tgt in pages:
            inbound[tgt].add("index")
    orphans = [p for p in sorted(pages) if p != "index" and not inbound[p]]

    section("断链")
    print("  0 条" if not broken else "\n".join("  %s -> %s" % b for b in broken))

    section("孤儿页")
    print("  无" if not orphans else "\n".join("  " + o for o in orphans))

    # 3 + 4. frontmatter 完整性与 updated/mtime 漂移
    no_fm, drift = [], []
    for rel, path in sorted(pages.items()):
        fm = frontmatter(path)
        if fm is None:
            no_fm.append(rel)
            continue
        m = re.search(r"^updated:\s*(\d{4}-\d{2}-\d{2})", fm, re.M)
        mt = day(path)
        if m:
            fm_day = datetime.date.fromisoformat(m.group(1))
            delta = (mt - fm_day).days
            if delta != 0:
                drift.append((rel, fm_day.isoformat(), mt.isoformat(), delta))
        else:
            drift.append((rel, "(缺 updated)", mt.isoformat(), 0))

    section("缺 frontmatter")
    print("  无" if not no_fm else "\n".join("  " + x for x in no_fm))

    section("updated 与 mtime 漂移")
    print("  无" if not drift else "\n".join(
        "  %-52s updated=%s mtime=%s (%+d 天)" % d for d in drift))

    # 5. index 重复区块 / 重复条目
    heads = re.findall(r"^##\s+(.+)$", index_txt, re.M)
    dup_heads = [h for h, c in collections.Counter(heads).items() if c > 1]
    links = [normalize(x) for x in LINK_RE.findall(index_txt)]
    dup_links = [x for x, c in collections.Counter(links).items() if c > 1]
    section("index 重复区块")
    print("  无" if not (dup_heads or dup_links) else "\n".join(
        ["  重复标题: " + ", ".join(dup_heads)] * bool(dup_heads)
        + ["  重复条目: " + ", ".join(dup_links)] * bool(dup_links)))

    # 6. log.md 漏记
    section("log.md 漏记")
    if os.path.isfile(LOG):
        log_txt = read(LOG)
        log_days = sorted(set(re.findall(r"^##\s*\[(\d{4}-\d{2}-\d{2})", log_txt, re.M)))
        content_days = sorted({day(p).isoformat() for p in pages.values() if p != IDX})
        newest_log = log_days[-1] if log_days else "(无)"
        newest_content = content_days[-1] if content_days else "(无)"
        print("  最新日志 %s / 最新内容页 mtime %s" % (newest_log, newest_content))
        if log_days and content_days and newest_content > newest_log:
            print("  ⚠️ 有内容页晚于最新日志（可能是改了页没写 log，需人工判读）")
    else:
        print("  无 log.md")

    # 7. 定级完整性（evidence_level 必填 + 核查表须带图例）
    section("定级完整性")
    grade_missing, legend_missing = [], []
    for rel, path in sorted(pages.items()):
        fm = frontmatter(path) or ""
        txt = read(path)
        m = re.search(r"^type:\s*(\S+)", fm, re.M)
        ty = m.group(1) if m else ""
        if ty in ("source", "collection") and not re.search(r"^evidence_level:\s*(?:[ABCD]|N/A)\s*$", fm, re.M):
            grade_missing.append("%s (%s)" % (rel, ty or "无 type"))
        if EMOJI_RE.search(txt) and "图例" not in txt:
            legend_missing.append(rel)
    print("  缺 evidence_level（source/collection 必填）: "
          + ("无" if not grade_missing else "\n".join("    " + x for x in grade_missing)))
    print("  含 🟢🟡🔴 但缺图例的表: "
          + ("无" if not legend_missing else "\n".join("    " + x for x in legend_missing)))

    # 8. type 完整性（每页必填 + 允许值）
    section("type 完整性")
    type_missing, type_bad = [], []
    types = {}
    for rel, path in sorted(pages.items()):
        ty = fm_value(frontmatter(path), "type")
        if not ty:
            type_missing.append(rel)
        elif ty not in PAGE_TYPES:
            type_bad.append("%s (%s)" % (rel, ty))
        else:
            types[rel] = ty
    print("  缺 type: " + ("无" if not type_missing else "\n".join("    " + x for x in type_missing)))
    print("  type 值非法: " + ("无" if not type_bad else "\n".join("    " + x for x in type_bad)))

    # 9. 子类型一致性（entity/concept 必填子类型且与父目录一致；source 必填 source_type）
    section("子类型一致性")
    subtype_bad = []
    for rel, path in sorted(pages.items()):
        fm = frontmatter(path) or ""
        ty = types.get(rel)
        parts = rel.split("/")
        if ty == "entity":
            et = fm_value(fm, "entity_type")
            if not et:
                subtype_bad.append("%s: 缺 entity_type" % rel)
            else:
                if et not in ENTITY_TYPES:
                    subtype_bad.append("%s: entity_type=%s 非法" % (rel, et))
                exp = ENTITY_DIR_TYPE.get(parts[1]) if parts[0] == "entities" and len(parts) >= 2 else None
                if exp and et != exp:
                    subtype_bad.append("%s: entity_type=%s 与目录 %s/ 不符（应为 %s）" % (rel, et, parts[1], exp))
        elif ty == "concept":
            ct = fm_value(fm, "concept_type")
            if not ct:
                subtype_bad.append("%s: 缺 concept_type" % rel)
            else:
                if ct not in CONCEPT_TYPES:
                    subtype_bad.append("%s: concept_type=%s 非法" % (rel, ct))
                exp = CONCEPT_DIR_TYPE.get(parts[1]) if parts[0] == "concepts" and len(parts) >= 2 else None
                if exp and ct != exp:
                    subtype_bad.append("%s: concept_type=%s 与目录 %s/ 不符（应为 %s）" % (rel, ct, parts[1], exp))
        elif ty == "source" and not fm_value(fm, "source_type"):
            subtype_bad.append("%s: 缺 source_type" % rel)
    print("  无" if not subtype_bad else "\n".join("  " + x for x in subtype_bad))

    # 10. 转述级警示（C/D 级页正文必须含 ⚠️）
    section("转述级警示")
    warn_missing = []
    for rel, path in sorted(pages.items()):
        fm = frontmatter(path) or ""
        if re.search(r"^evidence_level:\s*[CD]\s*$", fm, re.M) and "⚠️" not in read(path):
            warn_missing.append(rel)
    print("  无" if not warn_missing else "\n".join("  " + x for x in warn_missing))

    # 11. 等级引用可溯（"X 级（出处：…）"等级合法 + 出处页存在）
    section("等级引用可溯")
    ref_bad = []
    for rel, path in sorted(pages.items()):
        for letter, target in GRADE_REF_RE.findall(read(path)):
            if letter not in "ABCD":
                ref_bad.append("%s: 非法等级字母 %s 级" % (rel, letter))
            t = normalize(target.strip().strip("[]"))
            if t not in pages:
                ref_bad.append("%s: 出处不存在 -> %s" % (rel, t))
    print("  无" if not ref_bad else "\n".join("  " + x for x in ref_bad))

    # 12. 逐条覆盖（collection 页核查表的主张行须带吻合度或等级引用；未全覆盖只告警）
    section("逐条覆盖")
    cover_bad = []
    for rel, path in sorted(pages.items()):
        if types.get(rel) != "collection":
            continue
        claims, uncovered = 0, []
        for ln, line in enumerate(read(path).splitlines(), 1):
            if not line.startswith("|") or SEP_ROW_RE.match(line):
                continue
            if NUM_ROW_RE.match(line) or EMOJI_RE.search(line):
                claims += 1
                if not (EMOJI_RE.search(line) or "级（出处" in line or BG_RE.search(line)):
                    uncovered.append("L%d %s" % (ln, line.strip()[:36]))
        if uncovered:
            cover_bad.append("%s: %d/%d 主张行未标（%s）"
                             % (rel, len(uncovered), claims, "；".join(uncovered[:3])))
    print("  全覆盖" if not cover_bad else "\n".join("  ⚠️ " + x for x in cover_bad))

    # 13. 结构计数（排除 .git，避免计数被版本库对象淹没）
    section("结构计数")
    files_all = []
    for d, s, fs in os.walk(ROOT):
        s[:] = [x for x in s if x != ".git"]
        files_all += [os.path.join(d, f) for f in fs]
    nfiles = len(files_all)
    nbytes = sum(os.path.getsize(p) for p in files_all)
    git_note = "（另有 .git 版本库，未计入）" if os.path.isdir(os.path.join(ROOT, ".git")) else ""
    print("  %s: %d 文件 / %.0f KB%s；wiki 页 %d 个"
          % (ROOT, nfiles, nbytes / 1024.0, git_note, len(pages)))
    by_dir = collections.Counter(p.split("/")[0] for p in pages)
    for k, v in sorted(by_dir.items()):
        print("    wiki/%-16s %d 页" % (k, v))
    print("\n（只读检查，未改动任何文件）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
