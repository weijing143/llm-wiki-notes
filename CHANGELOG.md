# CHANGELOG

知识库**内容层面**的变更史：入库、核查修正、规则演进。

运维操作不在此列 —— 本仓库只承载知识内容与维护它的规则。

---

## 2026-10-07 · index 自动化 + manual 检查半自动化（WIKI.md v3.5）

- 新增 `scripts/wiki-index.py`：扫描全部页面 frontmatter 按分类重建 `wiki/index.md`（保留 created、分类结构跟随 schema 目录映射）；**index.md 转为脚本生成、禁止手改**，入库四件套的"登记"改为重跑该脚本；`--check` 接入 CI（手改或入库后未重建即红）
- `wiki-lint.py` 13 → **15 项**，manual 检查的半自动化（只列候选、判读仍靠人工）：
  - 第 13 项「缺链缺页候选」：某页标题在他页出现 ≥2 次却未加 `[[]]` 链接；「引号词」全库出现 ≥3 次却无对应页
  - 第 14 项「过时声明候选」：内容页 `updated` 距今 > 90 天（`--stale-days` 可调），或 > 30 天且含"最新/目前/今年"等时效词
- 共享工具函数（frontmatter / fm_value / normalize / LINK_RE）下沉至 `scripts/wiki_schema.py`，lint 与 wiki-index 复用
- manual 检查项收敛为两项（跨页矛盾、数据缺口），WIKI.md 记录 semi_auto 映射
- 自测 18 → 24 用例；本仓库 `wiki/index.md` 已切换为生成版

## 2026-10-07 · agent 发现入口

- 新增 `AGENTS.md`：指向 WIKI.md 为唯一规则源 + 三条核心命令 + 入库规则摘要 + 硬边界；agent clone 后可自助上岗，无需用户口头交代规则

## 2026-10-07 · 工具链硬化（WIKI.md v3.4）

- `wiki-lint.py` **退出码分级**：7 项硬告警（断链 / 缺 frontmatter / 定级完整性 / type / 子类型 / 转述警示 / 引用可溯）存在即退出码 1；5 项软告警默认只警告，`--strict` 下判死；新增 `--json` 机器可读输出
- **日期基准修复**：`updated` 漂移与 `log.md` 漏记两项改用 **git 提交日期**（clone/checkout 会重置 mtime，旧版在新克隆仓库系统性误报）；无 git 历史时降级 mtime 并在输出中标注
- **schema 单源化**：新增 `scripts/wiki_schema.py`，lint / wiki-new 直接解析 `WIKI.md` 的 yaml 块获取允许值与目录映射，改 schema 不再双份维护；解析失败回退内置默认值并告警
- 解析健壮性：frontmatter 值容忍引号包裹（`evidence_level: "A"`）；`[[链接]]` 支持锚点 `#` 与 `.md` 后缀；半角 `X 级(出处:…)` 显式报格式错误
- 新增 `scripts/wiki-new.py` **建页脚手架** + `templates/` 五份模板：按 schema 落目录、自动填 frontmatter、拒绝覆盖，从建页源头消除 lint 第 3 / 8 / 9 项错误
- 新增 `tests/test_wiki.py`：17 个用例（好/坏 fixture + 脚手架）回归自测；新增 `.github/workflows/lint.yml`：push / PR 跑 `--strict` + 自测（fetch-depth 0 保证 git 日期基准）
- 许可证拆分：`wiki/` 内容 CC BY 4.0 不变，`scripts/` 与 `tests/` 代码改标 MIT（`scripts/LICENSE`）

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
