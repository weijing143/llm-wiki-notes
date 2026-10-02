#!/usr/bin/env python3
"""归档层自检（只读）—— 本仓库的结构健康检查。

用法:
    python3 scripts/wiki-lint.py [root]      # root 默认为仓库根目录

检查八类：
  1. 断链          [[路径]] 指向不存在的页
  2. 孤儿页        无任何入链（index.md 的链接也算入链）
  3. 缺 frontmatter
  4. updated 与文件 mtime 漂移
  5. index.md 重复的 H2 区块 / 重复条目
  6. log.md 漏记   （最新内容页日期 > 最新日志日期）
  7. 定级完整性    （source/collection 必填 evidence_level；含 🟢🟡🔴 的表须自带图例）
  8. 结构计数      （文件数 / 磁盘占用 / 各分类页数）
纯标准库、只读、不改任何文件。退出码恒为 0，除非库根不存在。
"""
import os
import re
import sys
import datetime
import collections

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


def collect_pages():
    pages = {}
    for dirpath, _dirs, files in os.walk(WIKI):
        for f in files:
            if f.endswith(".md"):
                rel = os.path.relpath(os.path.join(dirpath, f), WIKI)
                pages[rel[:-3]] = os.path.join(dirpath, f)
    return pages


def read(path):
    return open(path, encoding="utf-8", errors="ignore").read()


def frontmatter(path):
    txt = read(path)
    if not txt.startswith("---"):
        return None
    end = txt.find("\n---", 3)
    return txt[3:end] if end != -1 else None


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

    # 8. 结构计数（排除 .git —— 2026-10-01 库入 git 后必须剪掉，否则计数被版本库对象淹没）
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
