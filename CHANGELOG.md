# CHANGELOG

知识库**内容层面**的变更史：入库、核查修正、规则演进。

运维操作不在此列 —— 本仓库只承载知识内容与维护它的规则。

---

## 2026-10-02 · 模板化重构

- 清空全部样本内容（5 份 `raw/` 快照 + 13 个 wiki 页），保留方法论框架作为可复用空模板
- 补齐规则声称的目录空槽（`raw/` 的 `papers` / `transcripts` / `assets` / `data`，`wiki/` 的 `analyses` / `comparisons` / `questions` / `sources/papers`），以 `.gitkeep` 占位
- `WIKI.md` 升级 v3.1：`domain` 改为 `general`，移除「公开样本」表述，`log.md` 说明对齐空模板现状
- `wiki-lint.py` 修复 Windows GBK 控制台打印 🟢🟡🔴 时 `UnicodeEncodeError` 崩溃（stdout / stderr 强制 UTF-8）
- 样本期的入库与定级修正记录（2026-07 ~ 2026-10）不再随模板携带，可在 git 历史中查阅本文件的旧版本

## 2026-10-02 · 闭源

- 仓库可见性由 public 转为 private
