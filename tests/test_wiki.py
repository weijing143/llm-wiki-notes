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


if __name__ == "__main__":
    unittest.main()
