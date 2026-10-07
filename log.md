# Wiki Activity Log

本文件记录本库的操作（入库 / 查询 / 自检），格式 `## [YYYY-MM-DD] 操作 | 标题`。

> 入库四件套（`WIKI.md` → `ingest`）与 `scripts/wiki-lint.py` 第 6 项（`log.md 漏记`）都依赖本文件存在。

---

<!-- 记录自此处起追加 -->

## [2026-10-07] 入库 | 智谱×AWS：GLM-5.3 接入 Bedrock 与调用量分成

- 线索：B 站 AI 日报第 540 期（BV1a9pF61EBc，2026-10-06），用户点名入库
- 快照：`raw/notes/ai-daily-540-2026-10-07.md`（视频）、`raw/notes/zhipu-aws-bedrock-verify-2026-10-07.md`（溯源检索，4 条命中）
- 新建页：`collections/zhipu-aws-bedrock-2026`（页级 C）、`sources/articles/ai-daily-540`、`thepaper-bedrock-glm53`、`cnstock-bedrock-glm53`（均 C）、`entities/organizations/zhipu`、`aws`
- 核查要点：视频标题“智谱宣布与亚马逊合作”判 🟡（官宣主体为 AWS/Bedrock，接入对象为 GLM-5.3）；OpenRouter 份额数据判 🟡（转述统计未核原始）；页级按木桶原则取 C
- 收尾：`wiki/index.md` 由 `scripts/wiki-index.py` 重建；`wiki-lint.py --strict` 全绿（15 项，退出码 0）

## [2026-10-07] 核查 | 外部代码审计后的工具链修补与内容勘误

- 审计范围：脚本/lint 逻辑、index 生成、CI 门禁、raw 不可变约定、证据链抽查（实抓引用原文）
- 代码修补：`wiki-index.py` 生成物去掉运行日（`--check` 不再每日误报）；`wiki-lint.py` 第 7 项图例检查限定表格块、第 1 项并入 `related:` 死链、第 2 项孤儿页只数正文入链、新增第 16 项 `raw 不可变`（软；无 git 跳过）
- 内容勘误：`collections/zhipu-aws-bedrock-2026` 第 5 条出处由 thepaper 更正为 cnstock（澎湃原文无“ARR 18 亿美元”口径），吻合度 🟢→🟡，thepaper 来源页留勘误注记
- 文档同步：`WIKI.md` v3.7（16 项 / index 确定性 / N/A 适用面）、README 检查项与用例表（24 → 34 例）、`log.md` 清理样本期遗留说明
- 收尾：`wiki-index.py` 重建、`wiki-lint.py --strict` 全绿（16 项，退出码 0）、自测 34 例全过
