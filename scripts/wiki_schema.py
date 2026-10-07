#!/usr/bin/env python3
"""从 WIKI.md 解析 schema（唯一事实源），供 wiki-lint.py 与 wiki-new.py 共用。

WIKI.md 的 ```yaml 代码块只用到两个 YAML 子集结构：

    key: [a, b, c]     # 行内列表
    key:               # 缩进映射
      sub: val

本模块只解析这两个子集，不依赖 PyYAML。
解析失败或缺字段时回退到内置默认值，并由调用方打印告警。

用法:
    from wiki_schema import load_schema
    schema, origin = load_schema(root)   # origin 为人类可读的来源说明
"""
import os
import re

# 内置默认值：与 WIKI.md v3.7 的 yaml 块保持一致；仅作解析失败的兜底
DEFAULTS = {
    "page_types": ["index", "overview", "collection", "entity", "concept",
                   "source", "analysis", "comparison", "question"],
    "entity_types": ["person", "organization", "product", "technology", "event"],
    "concept_types": ["theory", "method", "framework", "metric", "principle"],
    "entity_dir_type": {"people": "person", "organizations": "organization",
                        "products": "product", "technologies": "technology",
                        "events": "event"},
    "concept_dir_type": {"theories": "theory", "methods": "method",
                         "frameworks": "framework", "metrics": "metric",
                         "principles": "principle"},
}

_YAML_BLOCK_RE = re.compile(r"```yaml\s*\n(.*?)```", re.S)
_INLINE_LIST_RE = re.compile(r"^(\w[\w-]*)\s*:\s*\[([^\]]*)\]\s*(?:#.*)?$")
_MAP_ENTRY_RE = re.compile(r"^(\w[\w-]*)\s*:\s*([^\s\[][^\s]*)\s*$")
_KEY_ONLY_RE = re.compile(r"^(\w[\w-]*)\s*:\s*(?:#.*)?$")
_VERSION_RE = re.compile(r"^version:\s*(\S+)", re.M)

LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def read(path):
    return open(path, encoding="utf-8", errors="ignore").read()


def frontmatter(path):
    """取页面 frontmatter 原始文本；无则 None。"""
    txt = read(path)
    if not txt.startswith("---"):
        return None
    end = txt.find("\n---", 3)
    return txt[3:end] if end != -1 else None


def fm_value(fm, name):
    """取 frontmatter 标量值；容忍引号包裹（evidence_level: "A" 也算合法）。"""
    m = re.search(r"^%s:\s*(.+)$" % re.escape(name), fm or "", re.M)
    if not m:
        return None
    return m.group(1).strip().strip('"').strip("'")


def normalize(target):
    """[[链接]] 归一化：去别名 |、去锚点 #、去 wiki/ 前缀与 .md 后缀。"""
    t = target.split("|")[0].split("#")[0].strip()
    if t.startswith("wiki/"):
        t = t[len("wiki/"):]
    if t.endswith(".md"):
        t = t[:-3]
    return t


def _parse_list(raw):
    return [x.strip() for x in raw.split(",") if x.strip()]


def _parse_blocks(text):
    """把全部 ```yaml 块解析成 {top_key: {sub_key: list_or_map}} 的浅结构。"""
    data = {}
    for block in _YAML_BLOCK_RE.findall(text):
        top = sub = None
        for line in block.splitlines():
            if not line.strip() or line.strip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip())
            s = line.strip()
            if indent == 0:
                m = _KEY_ONLY_RE.match(s)
                top = m.group(1) if m else None
                sub = None
                if top:
                    data.setdefault(top, {})
                continue
            if top is None or indent > 4:
                continue
            if indent == 2:
                m = _INLINE_LIST_RE.match(s)
                if m:
                    data[top][m.group(1)] = _parse_list(m.group(2))
                    sub = None
                    continue
                m = _KEY_ONLY_RE.match(s)
                sub = m.group(1) if m else None
                if sub:
                    data[top].setdefault(sub, {})
                continue
            # indent == 4：映射条目（值为列表的行留给 list 分支，这里只收标量）
            if sub:
                m = _MAP_ENTRY_RE.match(s)
                if m and isinstance(data[top].get(sub), dict):
                    data[top][sub][m.group(1)] = m.group(2)
    return data


def load_schema(root):
    """返回 (schema, origin)。schema 键与 DEFAULTS 相同；origin 说明来源。"""
    schema = {k: (dict(v) if isinstance(v, dict) else list(v))
              for k, v in DEFAULTS.items()}
    path = os.path.join(root, "WIKI.md")
    if not os.path.isfile(path):
        return schema, "内置默认值（未找到 WIKI.md）"
    try:
        text = open(path, encoding="utf-8", errors="ignore").read()
        data = _parse_blocks(text)
    except OSError:
        return schema, "内置默认值（WIKI.md 读取失败）"

    version = None
    m = _VERSION_RE.search(text.split("\n---", 1)[0])
    if m:
        version = m.group(1)

    got = {}
    pt = data.get("page_types", {})
    if isinstance(pt.get("allowed"), list) and pt["allowed"]:
        schema["page_types"] = pt["allowed"]
        got["page_types"] = True
    ent = data.get("entities", {})
    if isinstance(ent.get("types"), list) and ent["types"]:
        schema["entity_types"] = ent["types"]
        got["entity_types"] = True
    if isinstance(ent.get("dir_mapping"), dict) and ent["dir_mapping"]:
        schema["entity_dir_type"] = ent["dir_mapping"]
        got["entity_dir_type"] = True
    con = data.get("concepts", {})
    if isinstance(con.get("categories"), list) and con["categories"]:
        schema["concept_types"] = con["categories"]
        got["concept_types"] = True
    if isinstance(con.get("dir_mapping"), dict) and con["dir_mapping"]:
        schema["concept_dir_type"] = con["dir_mapping"]
        got["concept_dir_type"] = True

    if len(got) == 5:
        origin = "WIKI.md%s（单源）" % (" v" + version if version else "")
    else:
        missing = sorted(set(DEFAULTS) - set(got))
        origin = "WIKI.md 部分字段解析失败，缺失项回退内置默认值: %s" % ", ".join(missing)
    return schema, origin
