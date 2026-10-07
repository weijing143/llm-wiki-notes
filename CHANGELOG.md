# CHANGELOG

知识库**内容层面**的变更史：入库、核查修正、规则演进。

运维操作不在此列 —— 本仓库只承载知识内容与维护它的规则。

---

## 2026-10-07 · 外部审计后的工具链修补 + 内容勘误（WIKI.md v3.7）

外部代码审计暴露的问题逐条修复（每条都有回归用例）：

- **修 index 每日误报**：`wiki-index.py` 生成物不再写入运行日（`updated` 取页内最新，页脚去日期），`--check` 对任意运行日稳定——此前任何“非重建当天”的 push 都会红
- **图例检查收紧**：lint 第 7 项只按表格块判定（表前 6 行内或表内须含“图例”并报出行号）；正文引用 🟢🟡🔴 不再误判为“缺图例的表”
- **`related:` 纳入断链**：frontmatter 交叉引用死链此前是校验盲区，现并入第 1 项（硬）
- **孤儿页语义修正**：index.md 由脚本生成、必然收录全部页，把它当入链会让本项永不触发；改为只数正文入链，仅被 index 收录的另列候选（不判死）
- **新增第 16 项 `raw 不可变`**：git 历史中 `raw/` 只允许新增（当前树中仍存在的文件被改 / 删 / 重命名即告警；样本期已删除的历史清理不追究），无 git 时跳过；严重级为软，CI 的 `--strict` 下同样判死
- **内容勘误**：专题页第 5 条“ARR 18 亿美元”出处由澎湃更正为上证报，吻合度 🟢→🟡（实抓原文复核：澎湃无此口径，仓库 raw 快照原本即记在上证报名下）；thepaper 来源页撤下该数字并按“不静默替换”留勘误注记
- **测试**：24 → 34 例（index 确定性、图例作用域、related 死链、孤儿语义、raw 不可变），并修掉一处未关闭文件句柄
- 文档同步：README 检查项 / 用例表、`WIKI.md` v3.7、`wiki_schema.py` 注释、`log.md` 清理样本期遗留说明

---

## 2026-10-07 · 命名约定 + question 页工作流（WIKI.md v3.6）

首次真实入库（智谱×AWS 专题，commit 0e6090c2）暴露问题的复盘固化：

- **命名与引用约定**（新章节）：页标题用带括号完整名（`智谱（Zhipu）`），正文用简称；`wiki/` 正文禁用「」（留给 lint 第 13 项当缺页候选探测器）；他页实体首次提及加 `[[]]` 链
- **question 页工作流**：query 默认只答不写回的例外——用户点名"这个答案入库"时可沉淀为 `questions/` 页（type: question）
- **跟踪点回看机制**：后续跟踪点写成含时效词的表述（如"目前未定位官方公告"），>30 天后 lint 第 14 项自动带入复核清单
- 首次入库内容：collections/zhipu-aws-bedrock-2026（C）+ sources×3 + entities×2 + raw 快照×2

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
