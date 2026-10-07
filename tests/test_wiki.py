#!/usr/bin/env python3
"""wiki-lint.py / wiki-new.py 的回归自测（纯标准库 unittest）。

策略：在临时目录构造迷你 wiki fixture，用子进程跑脚本、解析 --json 输出断言。
覆盖：退出码分级、断链、缺 type、引号 evidence_level、锚点链接、schema 单源
（WIKI.md 自定义 type 生效）、C/D 警示、子类型与目录一致性、--strict、脚手架建页。

运行:
    python3 -m unittest discover -s tests -v
"""
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINT = os.path.join(REPO, "scripts", "wiki-lint.py")
NEW = os.path.join(REPO, "scripts", "wiki-new.py")
INDEX = os.path.join(REPO, "scripts", "wiki-index.py")
TODAY = datetime.date.today().isoformat()

WIKI_MD = """---
version: 9.9-test
---

# Wiki Configuration

```yaml
page_types:
  allowed: [index, overview, collection, entity, concept, source, note]
```

```yaml
entities:
  types: [person, organization]
  dir_mapping:
    people: person
    organizations: organization
```

```yaml
concepts:
  categories: [theory, method]
  dir_mapping:
    theories: theory
    methods: method
```
"""

INDEX_MD = """---
title: Index
type: index
created: %s
updated: %s
---

# Index
""" % (TODAY, TODAY)

LOG_MD = "# Log\n\n## [%s] lint | fixture\n" % TODAY


def page(ty, extra_fm="", body="正文。"):
    return ("---\ntitle: T\ntype: %s\ncreated: %s\nupdated: %s\n%s---\n\n# T\n\n%s\n"
            % (ty, TODAY, TODAY, extra_fm, body))


class Fixture(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="wiki-test-")
        self.addCleanup(shutil.rmtree, self.root, True)
        os.makedirs(os.path.join(self.root, "wiki"))
        self.w("WIKI.md", WIKI_MD)
        self.w("log.md", LOG_MD)
        self.w("wiki/index.md", INDEX_MD)

    def w(self, rel, text):
        path = os.path.join(self.root, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)

    def lint(self, *extra):
        out = subprocess.run(
            [sys.executable, LINT, self.root, "--json"] + list(extra),
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(out.stderr, "", "lint 不应向 stderr 输出")
        return out.returncode, json.loads(out.stdout)

    def new(self, *cli):
        return subprocess.run(
            [sys.executable, NEW] + list(cli) + ["--root", self.root,
                                                 "--date", TODAY],
            capture_output=True, text=True, encoding="utf-8", errors="replace")


class TestGoodFixture(Fixture):
    def test_minimal_wiki_passes(self):
        code, d = self.lint()
        self.assertEqual(code, 0, json.dumps(d["summary"], ensure_ascii=False))
        self.assertEqual(d["summary"]["hard_failures"], [])

    def test_schema_single_source(self):
        """WIKI.md 自定义的 page type `note` 应被 lint 接受（单源生效）。"""
        self.assertEqual(d_schema(self.lint()[1]), "WIKI.md v9.9-test（单源）")
        self.w("wiki/collections/c1.md", page("note"))
        code, d = self.lint()
        self.assertEqual(code, 0)
        self.assertEqual(d["checks"]["type 完整性"]["violations"], [])

    def test_linked_entity_passes(self):
        self.w("wiki/entities/people/p1.md",
               page("entity", "entity_type: person\n"))
        self.w("wiki/index.md", INDEX_MD + "\n[[entities/people/p1]]\n")
        code, d = self.lint()
        self.assertEqual(code, 0, json.dumps(d["checks"], ensure_ascii=False))

    def test_quoted_evidence_level_accepted(self):
        self.w("wiki/collections/c1.md",
               page("collection", 'evidence_level: "A"\n'))
        code, d = self.lint()
        self.assertEqual(d["checks"]["定级完整性"]["violations"], [])

    def test_anchor_link_not_broken(self):
        self.w("wiki/entities/people/p1.md",
               page("entity", "entity_type: person\n"))
        self.w("wiki/index.md",
               INDEX_MD + "\n[[entities/people/p1#小节]]\n[[entities/people/p1.md]]\n")
        code, d = self.lint()
        self.assertEqual(d["checks"]["断链"]["violations"], [])


def d_schema(d):
    return d["schema_origin"]


class TestHardFailures(Fixture):
    def test_broken_link_fails(self):
        self.w("wiki/collections/c1.md",
               page("collection", "evidence_level: A\n", "见 [[nowhere/page]]。"))
        code, d = self.lint()
        self.assertEqual(code, 1)
        self.assertIn("断链", d["summary"]["hard_failures"])

    def test_missing_type_fails(self):
        self.w("wiki/collections/c1.md",
               page("collection").replace("type: collection\n", ""))
        code, d = self.lint()
        self.assertEqual(code, 1)
        self.assertIn("type 完整性", d["summary"]["hard_failures"])

    def test_missing_evidence_level_fails(self):
        self.w("wiki/collections/c1.md", page("collection"))
        code, d = self.lint()
        self.assertEqual(code, 1)
        self.assertIn("定级完整性", d["summary"]["hard_failures"])

    def test_c_level_without_warning_fails(self):
        self.w("wiki/sources/articles/s1.md",
               page("source", "evidence_level: C\nsource_type: 公众号\n"))
        code, d = self.lint()
        self.assertEqual(code, 1)
        self.assertIn("转述级警示", d["summary"]["hard_failures"])

    def test_subtype_dir_mismatch_fails(self):
        self.w("wiki/entities/organizations/p1.md",
               page("entity", "entity_type: person\n"))
        code, d = self.lint()
        self.assertEqual(code, 1)
        self.assertIn("子类型一致性", d["summary"]["hard_failures"])

    def test_halfwidth_grade_ref_fails(self):
        self.w("wiki/entities/people/p1.md",
               page("entity", "entity_type: person\n",
                    "数据为 A 级(出处:collections/c1)。"))
        code, d = self.lint()
        self.assertEqual(code, 1)
        self.assertIn("等级引用可溯", d["summary"]["hard_failures"])

    def test_missing_root_exit_2(self):
        out = subprocess.run(
            [sys.executable, LINT, os.path.join(self.root, "nope"), "--json"],
            capture_output=True, text=True)
        self.assertEqual(out.returncode, 2)


class TestStrict(Fixture):
    def test_orphan_soft_by_default_hard_under_strict(self):
        self.w("wiki/entities/people/p1.md",
               page("entity", "entity_type: person\n"))   # 无入链 → 孤儿（软）
        code, _ = self.lint()
        self.assertEqual(code, 0)
        code, d = self.lint("--strict")
        self.assertEqual(code, 1)
        self.assertIn("孤儿页", d["summary"]["soft_warnings"])


class TestGitDateBasis(Fixture):
    @unittest.skipUnless(shutil.which("git"), "需要 git")
    def test_git_commit_date_beats_mtime(self):
        """提交日期 2026-01-15（mtime 是今天）：updated 对齐提交日期则不应漂移。

        回归：pages 键无 .md 后缀而 git 路径有，拼接错误会静默降级 mtime。"""
        past = "2026-01-15"
        self.w("wiki/entities/people/p1.md",
               page("entity", "entity_type: person\n").replace(TODAY, past))
        self.w("wiki/index.md",
               (INDEX_MD + "\n[[entities/people/p1]]\n").replace(TODAY, past))
        self.w("log.md", "# Log\n\n## [%s] lint | fixture\n" % past)
        env = dict(os.environ, GIT_AUTHOR_DATE=past + "T10:00:00+00:00",
                   GIT_COMMITTER_DATE=past + "T10:00:00+00:00")
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                        "add", "-A"], cwd=self.root, check=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-qm", "c"], cwd=self.root, check=True, env=env)
        code, d = self.lint()
        self.assertEqual(d["date_source"], "git 提交日期")
        self.assertEqual(d["checks"]["updated 漂移"]["violations"], [])
        self.assertEqual(code, 0, json.dumps(d["summary"], ensure_ascii=False))


class TestIndexGenerator(Fixture):
    def run_index(self, *a):
        return subprocess.run([sys.executable, INDEX, "--root", self.root] + list(a),
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace")

    def test_generate_then_check_roundtrip(self):
        self.w("wiki/entities/people/p1.md",
               page("entity", "entity_type: person\n").replace(
                   "title: T", "title: Alice"))
        out = self.run_index()
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        with open(os.path.join(self.root, "wiki", "index.md"),
                  encoding="utf-8") as f:
            idx = f.read()
        self.assertIn("[[entities/people/p1|Alice]]", idx)
        self.assertIn("请勿手改", idx)
        self.assertEqual(self.run_index("--check").returncode, 0)
        # 改了页没重新生成 → --check 必须报出来
        self.w("wiki/entities/people/p1.md",
               page("entity", "entity_type: person\n").replace(
                   "title: T", "title: Bob"))
        self.assertEqual(self.run_index("--check").returncode, 1)

    def test_empty_wiki_generates(self):
        self.assertEqual(self.run_index().returncode, 0)
        self.assertEqual(self.run_index("--check").returncode, 0)


class TestSemiAutoChecks(Fixture):
    def test_stale_page_flagged_soft(self):
        self.w("wiki/entities/people/p1.md",
               page("entity", "entity_type: person\n").replace(TODAY, "2020-01-01"))
        code, d = self.lint()
        self.assertEqual(code, 0)   # 软告警不判死
        v = d["checks"]["过时声明候选"]["violations"]
        self.assertTrue(any("p1" in x for x in v))

    def test_time_word_flagged(self):
        old = (datetime.date.today() - datetime.timedelta(days=60)).isoformat()
        self.w("wiki/entities/people/p1.md",
               page("entity", "entity_type: person\n",
                    "这是最新的进展。").replace(TODAY, old))
        code, d = self.lint()
        v = d["checks"]["过时声明候选"]["violations"]
        self.assertTrue(any("时效词" in x for x in v))

    def test_mention_without_link_flagged(self):
        self.w("wiki/entities/people/p1.md",
               page("entity", "entity_type: person\n").replace(
                   "title: T", "title: Alpha"))
        self.w("wiki/entities/people/p2.md",
               page("entity", "entity_type: person\n",
                    "Alpha 提出过 X。Alpha 又提出 Y。"))
        code, d = self.lint()
        v = d["checks"]["缺链缺页候选"]["violations"]
        self.assertTrue(any("Alpha" in x and "未链到" in x for x in v))

    def test_missing_page_candidate_flagged(self):
        body = "「Transformer」是核心。「Transformer」改变了范式。「Transformer」仍在演化。"
        self.w("wiki/entities/people/p1.md",
               page("entity", "entity_type: person\n", body))
        code, d = self.lint()
        v = d["checks"]["缺链缺页候选"]["violations"]
        self.assertTrue(any("Transformer" in x and "建页候选" in x for x in v))


class TestWikiNew(Fixture):
    def test_scaffold_entity_then_lint_no_hard_failures(self):
        out = self.new("entity", "p1", "--entity-type", "person")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        path = os.path.join(self.root, "wiki", "entities", "people", "p1.md")
        self.assertTrue(os.path.isfile(path))
        code, d = self.lint()
        self.assertEqual(d["summary"]["hard_failures"], [])

    def test_scaffold_refuses_overwrite(self):
        self.assertEqual(self.new("collection", "c1").returncode, 0)
        self.assertEqual(self.new("collection", "c1").returncode, 2)

    def test_scaffold_bad_entity_type_rejected(self):
        out = self.new("entity", "p1", "--entity-type", "alien")
        self.assertEqual(out.returncode, 2)

    def test_scaffold_concept_dir_mapping(self):
        out = self.new("concept", "m1", "--concept-type", "method")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertTrue(os.path.isfile(
            os.path.join(self.root, "wiki", "concepts", "methods", "m1.md")))


class TestIndexDeterminism(Fixture):
    """回归：生成物曾写入运行日，--check 在非重建当天系统性误报。"""

    def load_module(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("wiki_index", INDEX)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_output_only_depends_on_page_content(self):
        self.w("wiki/entities/people/p1.md",
               page("entity", "entity_type: person\n").replace(
                   "title: T", "title: Alice"))
        out = subprocess.run([sys.executable, INDEX, "--root", self.root],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        mod = self.load_module()
        schema, _ = mod.load_schema(self.root)
        metas = mod.collect(schema, os.path.join(self.root, "wiki"))
        idx = os.path.join(self.root, "wiki", "index.md")
        created = mod.fm_value(mod.frontmatter(idx), "created")
        # build 不接受“今天”：输出只能由页面内容决定，换一天运行结果不变
        built = mod.build(schema, metas, created)
        with open(idx, encoding="utf-8") as f:
            self.assertEqual(built, f.read())
        self.assertNotIn("生成于", built)          # 运行日不再进入生成物
        self.assertIn("updated: " + TODAY, built)   # updated 取页内最新


class TestLegendScope(Fixture):
    """图例检查只作用于表格块：正文引用 🟢🟡🔴 不是“缺图例的表”。"""

    def test_table_without_legend_fails(self):
        body = "| # | 主张 | 吻合度 |\n|---|---|---|\n| 1 | x | 🟢 |\n"
        self.w("wiki/collections/c1.md",
               page("collection", "evidence_level: A\n", body))
        code, d = self.lint()
        self.assertEqual(code, 1)
        self.assertIn("定级完整性", d["summary"]["hard_failures"])
        self.assertTrue(any("缺图例" in x
                            for x in d["checks"]["定级完整性"]["violations"]))

    def test_legend_line_before_table_passes(self):
        body = ("> 图例：🟢 吻合 · 🟡 偏差 · 🔴 放大\n\n"
                "| # | 主张 | 吻合度 |\n|---|---|---|\n| 1 | x | 🟢 |\n")
        self.w("wiki/collections/c1.md",
               page("collection", "evidence_level: A\n", body))
        code, d = self.lint()
        self.assertEqual(d["checks"]["定级完整性"]["violations"], [])

    def test_prose_emoji_without_table_not_flagged(self):
        self.w("wiki/entities/people/p1.md",
               page("entity", "entity_type: person\n",
                    "本条判定 🟢 与来源吻合，另一条 🟡。"))
        code, d = self.lint()
        self.assertEqual(code, 0, json.dumps(d["checks"], ensure_ascii=False))
        self.assertEqual(d["checks"]["定级完整性"]["violations"], [])


class TestRelatedLinks(Fixture):
    """related: 是正文 [[…]] 之外的交叉引用，须同样可解析（原为校验盲区）。"""

    def test_dangling_related_fails(self):
        self.w("wiki/entities/people/p1.md",
               page("entity", "entity_type: person\nrelated: [entities/people/nope]\n"))
        code, d = self.lint()
        self.assertEqual(code, 1)
        self.assertIn("断链", d["summary"]["hard_failures"])
        self.assertTrue(any("related:" in x
                            for x in d["checks"]["断链"]["violations"]))

    def test_existing_related_passes(self):
        self.w("wiki/entities/people/p1.md", page("entity", "entity_type: person\n"))
        self.w("wiki/entities/people/p2.md",
               page("entity", "entity_type: person\nrelated: [entities/people/p1.md]\n"))
        code, d = self.lint()
        self.assertEqual(d["checks"]["断链"]["violations"], [])


class TestOrphanScope(Fixture):
    """index.md 由脚本生成、必然收录全部页，其链接不能算孤儿检查的入链。"""

    def test_index_only_link_is_not_orphan(self):
        self.w("wiki/entities/people/p1.md", page("entity", "entity_type: person\n"))
        self.w("wiki/index.md", INDEX_MD + "\n[[entities/people/p1]]\n")
        code, d = self.lint("--strict")
        self.assertEqual(code, 0, json.dumps(d["summary"], ensure_ascii=False))
        self.assertEqual(d["checks"]["孤儿页"]["violations"], [])
        out = subprocess.run([sys.executable, LINT, self.root],
                             capture_output=True, text=True, encoding="utf-8")
        self.assertIn("仅被 index 收录", out.stdout)

    def test_page_without_any_inbound_is_still_orphan(self):
        self.w("wiki/entities/people/p1.md", page("entity", "entity_type: person\n"))
        code, d = self.lint("--strict")
        self.assertEqual(code, 1)
        self.assertIn("孤儿页", d["summary"]["soft_warnings"])


@unittest.skipUnless(shutil.which("git"), "需要 git")
class TestRawImmutable(Fixture):
    """raw/ 不可变此前只靠约定：改 raw 快照 lint 照样全绿。"""

    def git(self, *argv):
        return subprocess.run(
            ["git", "-c", "user.email=t@t", "-c", "user.name=t"] + list(argv),
            cwd=self.root, check=True, capture_output=True, text=True)

    def test_modified_raw_flagged(self):
        self.w("raw/notes/n-2026-01-01.md", "只写不改\n")
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-qm", "init")
        self.w("raw/notes/n-2026-01-01.md", "只写不改\n被改了\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "edit raw")
        code, d = self.lint()
        self.assertEqual(code, 0)   # 软告警：本地默认不判死
        self.assertTrue(any("raw/notes/n-2026-01-01.md" in x
                            for x in d["checks"]["raw 不可变"]["violations"]))
        code, d = self.lint("--strict")
        self.assertEqual(code, 1)   # CI 跑 --strict，照样拦下
        self.assertIn("raw 不可变", d["summary"]["soft_warnings"])

    def test_append_only_raw_passes(self):
        self.w("raw/notes/n-2026-01-01.md", "一号\n")
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-qm", "init")
        self.w("raw/notes/m-2026-01-02.md", "二号\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "add raw")
        code, d = self.lint()
        self.assertEqual(d["checks"]["raw 不可变"]["violations"], [])


if __name__ == "__main__":
    unittest.main()
