# Wiki Activity Log

本文件记录本库的操作（入库 / 查询 / 自检），格式 `## [YYYY-MM-DD] 操作 | 标题`。

> **本样本保留留痕机制、不发布条目内容**：此处只有格式与空白记录区。
> 入库四件套（`WIKI.md` → `ingest`）与 `scripts/wiki-lint.py` 第 6 项（`log.md 漏记`）都依赖本文件存在。

---

<!-- 记录自此处起追加 -->

## [2026-10-07] 入库 | 智谱×AWS：GLM-5.3 接入 Bedrock 与调用量分成

- 线索：B 站 AI 日报第 540 期（BV1a9pF61EBc，2026-10-06），用户点名入库
- 快照：`raw/notes/ai-daily-540-2026-10-07.md`（视频）、`raw/notes/zhipu-aws-bedrock-verify-2026-10-07.md`（溯源检索，4 条命中）
- 新建页：`collections/zhipu-aws-bedrock-2026`（页级 C）、`sources/articles/ai-daily-540`、`thepaper-bedrock-glm53`、`cnstock-bedrock-glm53`（均 C）、`entities/organizations/zhipu`、`aws`
- 核查要点：视频标题“智谱宣布与亚马逊合作”判 🟡（官宣主体为 AWS/Bedrock，接入对象为 GLM-5.3）；OpenRouter 份额数据判 🟡（转述统计未核原始）；页级按木桶原则取 C
- 收尾：`wiki/index.md` 由 `scripts/wiki-index.py` 重建；`wiki-lint.py --strict` 全绿（15 项，退出码 0）
