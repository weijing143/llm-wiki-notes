#!/usr/bin/env python3
"""归档层自检（只读）—— 本仓库的结构健康检查。

用法:
    python3 scripts/wiki-lint.py [root]            # root 默认为仓库根目录
    python3 scripts/wiki-lint.py --strict          # 软告警也判死（退出码 1）
    python3 scripts/wiki-lint.py --json            # 机器可读输出（供自动化消费）

检查十五类（括号内为严重级）：
  1. 断链          [[路径]] 指向不存在的页（硬）
  2. 孤儿页        无任何入链，index.md 的链接也算入链（软）
  3. 缺 frontmatter（硬）
  4. updated 与最后变更日期漂移（软；取 git 提交日期，无 git 时降级 mtime 并标注）
  5. index.md 重复的 H2 区块 / 重复条目（软）
  6. log.md 漏记   最新内容页日期 > 最新日志日期（软，需人工判读）
  7. 定级完整性    source/collection 必填 evidence_level；含 🟢🟡🔴 的表须自带图例（硬）
  8. type 完整性   每页必填 type，且值在允许集合内（硬）
  9. 子类型一致性  entity 必填 entity_type、concept 必填 concept_type 且与父目录一致；
                   source 必填 source_type（硬）
  10. 转述级警示   evidence_level 为 C/D 的页正文必须含 ⚠️（硬）
  11. 等级引用可溯 "X 级（出处：…）"等级字母合法、出处页存在；
                   半角格式 "X 级(出处:…)" 视为格式错误（硬）
  12. 逐条覆盖     collection 页核查表的主张行须带吻合度或等级引用（软，未全覆盖只告警）
  13. 缺链缺页候选 某页标题在他页出现 ≥2 次却未加 [[]] 链接；「引号词」全库出现 ≥3 次
                   却无对应页（软，半自动化的"缺失交叉引用 / 缺失页面"候选）
  14. 过时声明候选 内容页 updated 距今 > --stale-days（默认 90），或 > 30 天且含
                   "最新/目前/今年"等时效词（软，半自动化的"过时声明"候选）
  15. 结构计数     文件数 / 磁盘占用 / 各分类页数（信息，不参与判死）

退出码：0 全绿或仅软告警；1 存在硬告警（--strict 时软告警也算）；2 库根不存在。
schema 允许值从 WIKI.md 的 yaml 块解析（单源），解析失败回退内置默认值并告警。
纯标准库、只读、不改任何文件。
"""
import argparse
import collections
import datetime
import json
import os
import re
import subprocess
import sys

# Windows GBK 控制台打印 emoji 会 UnicodeEncodeError，强制 UTF-8 输出
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wiki_schema import (LINK_RE, fm_value, frontmatter, load_schema,
                         normalize, read)

EMOJI_RE = re.compile("🟢|🟡|🔴")
GRADE_REF_RE = re.compile(r"([A-Z])\s*级（出处：([^）]+)）")
GRADE_REF_HALF_RE = re.compile(r"([A-Z])\s*级\(出处\s*[:：]\s*([^)]+)\)")
NUM_ROW_RE = re.compile(r"^\|\s*#?\d+\s*\|")
SEP_ROW_RE = re.compile(r"^\|[\s:\-—|]+\|$")
BG_RE = re.compile(r"—\s*背景共识")

HARD, SOFT, INFO = "hard", "soft", "info"


def collect_pages(wiki_dir):
    pages = {}
    for dirpath, _dirs, files in os.walk(wiki_dir):
        for f in files:
            if f.endswith(".md"):
                rel = os.path.relpath(os.path.join(dirpath, f), wiki_dir)
                rel = rel.replace(os.sep, "/")[:-3]   # 统一正斜杠，键与 [[链接]] 一致
                pages[rel] = os.path.join(dirpath, f)
    return pages


def mtime_day(path):
    return datetime.date.fromtimestamp(os.path.getmtime(path))


def git_dates(root):
    """一次 git log 取全部文件的最后提交日期 {posix_rel_path: YYYY-MM-DD}。

    clone/checkout 会重置 mtime，只有 git 历史才是可靠的"最后变更"来源。
    无 git / 无提交时返回 {}，调用方降级 mtime。
    """
    dates = {}
    try:
        out = subprocess.run(
            ["git", "-C", root, "log", "--format=@%cs", "--name-only",
             "--", "wiki", "log.md"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=60)
        if out.returncode != 0:
            return {}
        current = None
        for line in out.stdout.splitlines():
            if line.startswith("@"):
                current = line[1:]
            elif line.strip() and current:
                p = line.strip().replace(os.sep, "/")
                dates.setdefault(p, current)   # 首次出现即最新提交
    except (OSError, subprocess.SubprocessError):
        pass
    return dates


def section(title):
    print("\n== " + title + " ==")


def main():
    ap = argparse.ArgumentParser(
        description="归档层自检（只读）。详见脚本 docstring。")
    ap.add_argument("root", nargs="?", help="库根目录，默认为仓库根")
    ap.add_argument("--strict", action="store_true",
                    help="软告警也判死（退出码 1），供 CI 使用")
    ap.add_argument("--json", action="store_true",
                    help="输出 JSON（供自动化消费），不打印人类可读段落")
    ap.add_argument("--stale-days", type=int, default=90,
                    help="过时声明候选的天数阈值（默认 90）")
    args = ap.parse_args()

    default_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root = os.path.abspath(os.path.expanduser(args.root)) if args.root else default_root
    wiki_dir = os.path.join(root, "wiki")
    log_path = os.path.join(root, "log.md")
    idx_path = os.path.join(wiki_dir, "index.md")

    if not os.path.isdir(wiki_dir):
        print("!! 找不到库根:", root)
        return 2

    schema, schema_origin = load_schema(root)
    page_types = set(schema["page_types"])
    entity_types = set(schema["entity_types"])
    concept_types = set(schema["concept_types"])
    entity_dir_type = schema["entity_dir_type"]
    concept_dir_type = schema["concept_dir_type"]

    pages = collect_pages(wiki_dir)
    index_txt = read(idx_path) if os.path.isfile(idx_path) else ""
    gdates = git_dates(root)
    date_source = "git 提交日期" if gdates else "文件 mtime（无 git 历史，降级）"

    def page_day(rel):
        key = "wiki/%s.md" % rel   # pages 键去掉了 .md，git 路径要带后缀
        if key in gdates:
            return datetime.date.fromisoformat(gdates[key])
        return mtime_day(pages[rel])

    # results: name -> {"severity", "violations": [str], "lines": [str]}
    results = collections.OrderedDict()

    def rec(name, severity, violations, lines=None):
        results[name] = {"severity": severity,
                         "violations": [str(v) for v in violations],
                         "lines": lines if lines is not None
                         else [str(v) for v in violations]}

    # 1 + 2. 断链 / 孤儿页
    inbound = collections.defaultdict(set)
    broken = []
    for rel, path in pages.items():
        for raw in LINK_RE.findall(read(path)):
            tgt = normalize(raw)
            if tgt in pages:
                inbound[tgt].add(rel)
            else:
                broken.append("%s -> %s" % (rel, raw.strip()))
    for raw in LINK_RE.findall(index_txt):
        tgt = normalize(raw)
        if tgt in pages:
            inbound[tgt].add("index")
    orphans = [p for p in sorted(pages) if p != "index" and not inbound[p]]
    rec("断链", HARD, broken, broken or ["0 条"])
    rec("孤儿页", SOFT, orphans, orphans or ["无"])

    # 3 + 4. frontmatter 完整性与 updated/变更日期漂移
    no_fm, drift = [], []
    for rel, path in sorted(pages.items()):
        fm = frontmatter(path)
        if fm is None:
            no_fm.append(rel)
            continue
        m = re.search(r"^updated:\s*[\"']?(\d{4}-\d{2}-\d{2})", fm, re.M)
        pd = page_day(rel)
        if m:
            fm_day = datetime.date.fromisoformat(m.group(1))
            delta = (pd - fm_day).days
            if delta != 0:
                drift.append("%-52s updated=%s 变更=%s (%+d 天)"
                             % (rel, fm_day.isoformat(), pd.isoformat(), delta))
        else:
            drift.append("%-52s (缺 updated) 变更=%s" % (rel, pd.isoformat()))
    rec("缺 frontmatter", HARD, no_fm, no_fm or ["无"])
    rec("updated 漂移", SOFT, drift,
        (["基准: " + date_source] + drift) if drift else ["基准: " + date_source, "无"])

    # 5. index 重复区块 / 重复条目
    heads = re.findall(r"^##\s+(.+)$", index_txt, re.M)
    dup_heads = [h for h, c in collections.Counter(heads).items() if c > 1]
    links = [normalize(x) for x in LINK_RE.findall(index_txt)]
    dup_links = [x for x, c in collections.Counter(links).items() if c > 1]
    dup_msgs = (["重复标题: " + ", ".join(dup_heads)] if dup_heads else []) \
        + (["重复条目: " + ", ".join(dup_links)] if dup_links else [])
    rec("index 重复区块", SOFT, dup_msgs, dup_msgs or ["无"])

    # 6. log.md 漏记
    log_lines, log_violations = [], []
    if os.path.isfile(log_path):
        log_txt = read(log_path)
        log_days = sorted(set(re.findall(r"^##\s*\[(\d{4}-\d{2}-\d{2})", log_txt, re.M)))
        content_days = sorted({page_day(p).isoformat() for p in pages if p != "index"})
        newest_log = log_days[-1] if log_days else "(无)"
        newest_content = content_days[-1] if content_days else "(无)"
        log_lines.append("最新日志 %s / 最新内容页 %s（%s）"
                         % (newest_log, newest_content, date_source))
        if log_days and content_days and newest_content > newest_log:
            log_violations.append("有内容页晚于最新日志（可能改了页没写 log，需人工判读）")
            log_lines.append("⚠️ " + log_violations[0])
    else:
        log_violations.append("无 log.md")
        log_lines.append("无 log.md")
    rec("log.md 漏记", SOFT, log_violations, log_lines)

    # 7. 定级完整性（evidence_level 必填 + 核查表须带图例）
    grade_missing, legend_missing = [], []
    types = {}
    for rel, path in sorted(pages.items()):
        fm = frontmatter(path) or ""
        ty = fm_value(fm, "type")
        if ty:
            types[rel] = ty
        if ty in ("source", "collection"):
            ev = fm_value(fm, "evidence_level")
            if ev not in ("A", "B", "C", "D", "N/A"):
                grade_missing.append("%s (%s, evidence_level=%r)" % (rel, ty, ev))
        txt = read(path)
        if EMOJI_RE.search(txt) and "图例" not in txt:
            legend_missing.append(rel)
    grade_msgs = (["缺 evidence_level（source/collection 必填）:"]
                  + ["  " + x for x in grade_missing] if grade_missing else []) \
        + (["含 🟢🟡🔴 但缺图例的表:"]
           + ["  " + x for x in legend_missing] if legend_missing else [])
    rec("定级完整性", HARD, grade_msgs, grade_msgs or ["无"])

    # 8. type 完整性（每页必填 + 允许值）
    type_missing, type_bad = [], []
    for rel, path in sorted(pages.items()):
        ty = fm_value(frontmatter(path), "type")
        if not ty:
            type_missing.append(rel)
        elif ty not in page_types:
            type_bad.append("%s (%s)" % (rel, ty))
    type_msgs = (["缺 type:"] + ["  " + x for x in type_missing] if type_missing else []) \
        + (["type 值非法:"] + ["  " + x for x in type_bad] if type_bad else [])
    rec("type 完整性", HARD, type_msgs, type_msgs or ["无"])

    # 9. 子类型一致性
    subtype_bad = []
    for rel, path in sorted(pages.items()):
        fm = frontmatter(path) or ""
        ty = types.get(rel)
        parts = rel.split("/")
        if ty == "entity":
            et = fm_value(fm, "entity_type")
            if not et:
                subtype_bad.append("%s: 缺 entity_type" % rel)
            elif et not in entity_types:
                subtype_bad.append("%s: entity_type=%s 非法" % (rel, et))
            else:
                exp = entity_dir_type.get(parts[1]) \
                    if parts[0] == "entities" and len(parts) >= 2 else None
                if exp and et != exp:
                    subtype_bad.append("%s: entity_type=%s 与目录 %s/ 不符（应为 %s）"
                                       % (rel, et, parts[1], exp))
        elif ty == "concept":
            ct = fm_value(fm, "concept_type")
            if not ct:
                subtype_bad.append("%s: 缺 concept_type" % rel)
            elif ct not in concept_types:
                subtype_bad.append("%s: concept_type=%s 非法" % (rel, ct))
            else:
                exp = concept_dir_type.get(parts[1]) \
                    if parts[0] == "concepts" and len(parts) >= 2 else None
                if exp and ct != exp:
                    subtype_bad.append("%s: concept_type=%s 与目录 %s/ 不符（应为 %s）"
                                       % (rel, ct, parts[1], exp))
        elif ty == "source" and not fm_value(fm, "source_type"):
            subtype_bad.append("%s: 缺 source_type" % rel)
    rec("子类型一致性", HARD, subtype_bad, subtype_bad or ["无"])

    # 10. 转述级警示（C/D 级页正文必须含 ⚠️）
    warn_missing = []
    for rel, path in sorted(pages.items()):
        ev = fm_value(frontmatter(path), "evidence_level")
        if ev in ("C", "D") and "⚠️" not in read(path):
            warn_missing.append(rel)
    rec("转述级警示", HARD, warn_missing, warn_missing or ["无"])

    # 11. 等级引用可溯（全角合法 + 半角报错）
    ref_bad = []
    for rel, path in sorted(pages.items()):
        txt = read(path)
        for letter, target in GRADE_REF_HALF_RE.findall(txt):
            ref_bad.append("%s: 半角格式「%s 级(出处:%s)」，应为全角（出处：…）"
                           % (rel, letter, target.strip()[:30]))
        for letter, target in GRADE_REF_RE.findall(txt):
            if letter not in "ABCD":
                ref_bad.append("%s: 非法等级字母 %s 级" % (rel, letter))
            t = normalize(target.strip().strip("[]"))
            if t not in pages:
                ref_bad.append("%s: 出处不存在 -> %s" % (rel, t))
    rec("等级引用可溯", HARD, ref_bad, ref_bad or ["无"])

    # 12. 逐条覆盖（软）
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
                if not (EMOJI_RE.search(line) or "级（出处" in line
                        or BG_RE.search(line)):
                    uncovered.append("L%d %s" % (ln, line.strip()[:36]))
        if uncovered:
            cover_bad.append("%s: %d/%d 主张行未标（%s）"
                             % (rel, len(uncovered), claims,
                                "；".join(uncovered[:3])))
    rec("逐条覆盖", SOFT, cover_bad, cover_bad or ["全覆盖"])

    # 13. 缺链缺页候选（软；只列候选，判读靠人工——manual 项"缺失页面"的半自动化）
    QUOTE_RE = re.compile("「([^」\n]{2,20})」")
    titles = {}
    for rel, path in pages.items():
        t = fm_value(frontmatter(path), "title")
        if t and len(t) >= 2:
            titles[rel] = t
    link_targets = {rel: {normalize(x) for x in LINK_RE.findall(read(path))}
                    for rel, path in pages.items()}
    mention_bad, quoted = [], collections.Counter()
    for rel, path in sorted(pages.items()):
        txt = read(path)
        for other, t in titles.items():
            if other == rel:
                continue
            n = txt.count(t)
            if n >= 2 and other not in link_targets[rel]:
                mention_bad.append("%s 提及「%s」%d 次但未链到 %s"
                                   % (rel, t, n, other))
        for q in QUOTE_RE.findall(txt):
            quoted[q] += 1
    known_titles = set(titles.values())
    miss_page = ["「%s」全库出现 %d 次但无对应页（建页候选）" % (q, c)
                 for q, c in quoted.most_common() if c >= 3 and q not in known_titles]
    rec("缺链缺页候选", SOFT, mention_bad + miss_page,
        (mention_bad + miss_page) or ["无"])

    # 14. 过时声明候选（软；manual 项"过时声明"的半自动化）
    TIME_WORD_RE = re.compile("最新|目前|当前|今年|截至目前|近来|recently", re.I)
    today = datetime.date.today()
    stale_bad = []
    for rel, path in sorted(pages.items()):
        ty = types.get(rel)
        if ty in (None, "index", "overview"):
            continue
        m = re.search(r"^updated:\s*[\"']?(\d{4}-\d{2}-\d{2})",
                      frontmatter(path) or "", re.M)
        if not m:
            continue
        age = (today - datetime.date.fromisoformat(m.group(1))).days
        if age > args.stale_days:
            stale_bad.append("%s: updated 距今 %d 天（阈值 %d）"
                             % (rel, age, args.stale_days))
        elif age > 30 and TIME_WORD_RE.search(read(path)):
            stale_bad.append("%s: updated 距今 %d 天且含时效词，需复核" % (rel, age))
    rec("过时声明候选", SOFT, stale_bad, stale_bad or ["无"])

    # 15. 结构计数（信息；排除 .git）
    files_all = []
    for d, subdirs, fs in os.walk(root):
        subdirs[:] = [x for x in subdirs if x != ".git"]
        files_all += [os.path.join(d, f) for f in fs]
    nfiles = len(files_all)
    nbytes = sum(os.path.getsize(p) for p in files_all)
    git_note = "（另有 .git 版本库，未计入）" \
        if os.path.isdir(os.path.join(root, ".git")) else ""
    by_dir = collections.Counter(p.split("/")[0] for p in pages)
    stat_lines = ["%s: %d 文件 / %.0f KB%s；wiki 页 %d 个"
                  % (root, nfiles, nbytes / 1024.0, git_note, len(pages))]
    stat_lines += ["  wiki/%-16s %d 页" % (k, v) for k, v in sorted(by_dir.items())]
    rec("结构计数", INFO, [], stat_lines)

    # 汇总
    hard_hits = [n for n, r in results.items()
                 if r["severity"] == HARD and r["violations"]]
    soft_hits = [n for n, r in results.items()
                 if r["severity"] == SOFT and r["violations"]]
    exit_code = 1 if hard_hits or (args.strict and soft_hits) else 0

    if args.json:
        print(json.dumps({
            "root": root,
            "schema_origin": schema_origin,
            "date_source": date_source,
            "strict": args.strict,
            "checks": {n: {"severity": r["severity"],
                           "violations": r["violations"]}
                       for n, r in results.items()},
            "summary": {"hard_failures": hard_hits, "soft_warnings": soft_hits,
                        "exit_code": exit_code},
        }, ensure_ascii=False, indent=2))
        return exit_code

    print("schema 来源: " + schema_origin)
    if schema_origin.startswith("WIKI.md 部分字段"):
        print("⚠️ schema 解析不完整，请检查 WIKI.md yaml 块格式")
    for name, r in results.items():
        tag = {"hard": "[硬]", "soft": "[软]", "info": "[信息]"}[r["severity"]]
        section("%s %s" % (name, tag))
        print("\n".join("  " + ln for ln in r["lines"]))
    print("\n== 汇总 ==")
    print("  硬告警: %s" % (", ".join(hard_hits) if hard_hits else "无"))
    print("  软告警: %s" % (", ".join(soft_hits) if soft_hits else "无"))
    print("  退出码: %d%s" % (exit_code, "（--strict 生效中）" if args.strict else ""))
    print("（只读检查，未改动任何文件）")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
