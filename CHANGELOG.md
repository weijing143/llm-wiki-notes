# CHANGELOG

知识库**内容层面**的变更史：入库、核查修正、规则演进。

运维操作不在此列 —— 本仓库只承载知识内容与维护它的规则。

---

## 2026-10-02 · 页级定级规则 + 逐条覆盖检查（WIKI.md v3.3）

- 定级约定补**木桶原则**：collection 页级 `evidence_level` 取表内最低来源等级；全部主张无外部来源才允许 N/A
- `wiki-lint.py` 第 13 项「逐条覆盖」：collection 页核查表的主张行（编号行或含 🟢🟡🔴 的行）必须带吻合度或等级引用，未全覆盖输出 ⚠️ 告警转人工
- `WIKI.md` v3.2 → v3.3：载体分工表述修正（collection 先于 entity/concept），lint 清单扩至 13 项

## 2026-10-02 · 校验体系补全（WIKI.md v3.2）

- `wiki-lint.py` 由 8 项扩至 **12 项**：新增 type 完整性（每页必填 type 且值合法）、子类型一致性（entity/concept 必填子类型且与父目录一致，source 必填 source_type）、转述级警示（C/D 级页正文必须含 ⚠️）、等级引用可溯（`X 级（出处：…）`字母合法 + 出处存在）
- **修复跨平台 bug**：Windows 下 `os.path.relpath` 产生反斜杠键，与 `[[]]` 正斜杠链接永不匹配，导致断链/孤儿页全部误报（回归测试暴露，历史版本在 Windows 上从未真正全绿）
- 修复 Windows GBK 控制台打印 🟢🟡🔴 崩溃（stdout / stderr 强制 UTF-8）
- `WIKI.md` 新增 Page Types 权威定义（type 允许值 + 各类型必填字段），Entity/Concept 增加 dir_mapping
- 验证：历史 13 页（0d3bd5c）回归零误报；6 个违规 fixture 全部精准触发

## 2026-10-02 · 模板化重构

- 清空全部样本内容（5 份 `raw/` 快照 + 13 个 wiki 页），保留方法论框架作为可复用空模板
- 补齐规则声称的目录空槽（`raw/` 的 `papers` / `transcripts` / `assets` / `data`，`wiki/` 的 `analyses` / `comparisons` / `questions` / `sources/papers`），以 `.gitkeep` 占位
- `WIKI.md` 升级 v3.1：`domain` 改为 `general`，移除「公开样本」表述，`log.md` 说明对齐空模板现状
- `wiki-lint.py` 修复 Windows GBK 控制台打印 🟢🟡🔴 时 `UnicodeEncodeError` 崩溃（stdout / stderr 强制 UTF-8）
- 样本期的入库与定级修正记录（2026-07 ~ 2026-10）不再随模板携带，可在 git 历史中查阅本文件的旧版本

## 2026-10-02 · 闭源

- 仓库可见性由 public 转为 private
