# LLM Wiki Notes

用 **LLM Wiki 模式**沉淀知识笔记的框架 —— 外部内容先原样存档，再经多源核查沉淀为结构化知识页。

核心不是收藏链接，而是**把「自媒体主张」与「一手来源」逐条对齐**：每条主张都带来源等级和吻合度，口径被放大的地方显式标出来。

框架含规则（`WIKI.md`）、目录骨架、页面模板（`templates/`）、脚手架与自检脚本（`scripts/`）与留痕机制（`log.md`），已入库首个真实专题（智谱×AWS：GLM-5.3 接入 Bedrock，2026-10-07）；清空 `wiki/`、`raw/` 内容页即可复用为空模板。

## 工作流

1. **原样存档**（`raw/`）—— 视频 / 文章 / 论文的元数据、出处与关键数据快照，标注抓取日期，只写不改
2. **拆主张**（`wiki/`）—— 把观点类内容拆成可验证的单条主张
3. **逐条溯源** —— 直抓官方一手来源（新闻稿 / 论文 / 官方博客）核对，不用二手转述代替
4. **双轴定级** —— 来源等级 `A/B/C/D` × 吻合度 `🟢/🟡/🔴`，两轴不混写
5. **交叉引用** —— 实体页 / 概念页 / 综合页互链，断链与孤儿页由 lint 校验

| 标记 | 轴 | 含义 |
|---|---|---|
| `A/B/C/D` | 来源等级 | A 官方一手 · B 自报 · C 转述 · D 待确认 |
| `🟢/🟡/🔴` | 吻合度 | 吻合 · 措辞口径偏差或演绎 · 口径放大 |
| `—` | 补充 | 背景共识，只标注不计数 |

## 目录

```
README.md
AGENTS.md                      # agent 操作入口：先读 WIKI.md + 三条核心命令 + 硬边界
WIKI.md                        # 库规范：定级约定 / 入库规则 / lint 规则（schema 单源）
LICENSE                        # wiki/ 内容 CC BY 4.0（scripts/ 代码为 MIT，见 scripts/LICENSE）
CHANGELOG.md                   # 内容变更史
log.md                         # 操作留痕（入库 / 核查 / 规则演进）
scripts/wiki-lint.py           # 结构自检：15 项检查，退出码分级，--strict / --json / --stale-days
scripts/wiki-new.py            # 建页脚手架：按 schema 落目录、自动填 frontmatter
scripts/wiki-index.py          # index.md 生成器：扫描 frontmatter 重建目录（--check 供 CI）
scripts/wiki_schema.py         # 从 WIKI.md 解析 schema 的共用模块（单源）
templates/                     # 页面模板：collection / entity / concept / source / generic
tests/test_wiki.py             # 脚本回归自测（unittest + 临时 fixture）
.github/workflows/lint.yml     # CI：push / PR 跑 lint --strict + 自测
raw/                           # 源文档层（只写不改，作溯源头）
  articles/                     网页原文的出处卡片
  notes/                        视频 / API / 检索快照
  papers/                       论文 PDF（空槽备用）
  transcripts/                  会议 / 访谈转写（空槽备用）
  assets/                       图片 / 附件（空槽备用）
  data/                         独立数据集文件（空槽备用）
wiki/                          # 知识库层
  index.md                      全部页面目录（wiki-index.py 生成，禁手改）
  collections/                  专题页：核查表所在
  entities/                     实体页：人 / 组织
  concepts/                     概念页：理论 / 方法
  sources/                      来源摘要页，承载 evidence_level
  analyses/ · comparisons/ · questions/ · sources/papers/   # 空槽备用
```

## 建页

```bash
python3 scripts/wiki-new.py entity <slug> --entity-type person      # 实体页
python3 scripts/wiki-new.py collection <slug> --title 专题名         # 专题核查页
python3 scripts/wiki-new.py source <slug> --evidence-level C        # 来源页
```

按 `WIKI.md` 的目录映射落到正确位置，自动填好 `created` / `updated` / `type` / 子类型，拒绝覆盖已有页。建页后按入库四件套收尾：`raw/` 快照 → `wiki-index.py` 登记 → `log.md` 留痕 → lint 复跑。

## 自检

```bash
python3 scripts/wiki-index.py           # 重建 index.md（--check 只校验，供 CI）
python3 scripts/wiki-lint.py            # 15 项检查，硬告警时退出码 1
python3 scripts/wiki-lint.py --strict   # 软告警也判死（CI 用）
python3 scripts/wiki-lint.py --json     # 机器可读输出（自动化用）
python3 -m unittest discover -s tests   # 脚本自身的回归自测
```

十五类检查：断链、孤儿页、缺 frontmatter、`updated` 与最后变更日期漂移（以 git 提交日期为基准，无 git 历史降级 mtime）、index 重复区块、`log.md` 漏记、定级完整性（含"带 🟢🟡🔴 的表必须自带图例"）、type 完整性、子类型一致性、转述级警示、等级引用可溯（半角格式会报错）、逐条覆盖、缺链缺页候选（提及未加链 /「引号词」无对应页）、过时声明候选（updated 超阈值或含时效词，`--stale-days` 调阈值）、结构计数。

检查分三级：**硬**（断链 / 缺 frontmatter / 定级 / 类型 / 子类型 / 警示 / 引用可溯，存在即退出码 1）、**软**（孤儿 / 漂移 / 重复 / 漏记 / 覆盖 / 两类候选清单，默认只告警）、**信息**（结构计数）。允许值与目录映射从 `WIKI.md` 的 yaml 块解析（单源），改 schema 不用改脚本。纯标准库、只读。

## 已知边界

- 每页是**特定时间点的快照**，数字为核查时点值，不做回溯更新（页内均标 `created` / `updated`）
- 核查深度取决于投入，**未核实的会标 C/D 而不是省略**
- `raw/` 中第三方内容（视频、文章、论文）的版权归原作者所有，此处仅作研究存档与出处标注

## 许可

`wiki/` 知识页内容采用 [CC BY 4.0](LICENSE)；`scripts/` 与 `tests/` 代码采用 [MIT](scripts/LICENSE)。第三方内容版权归原作者。

## 测试用例（`tests/test_wiki.py`，共 24 例）

策略：在临时目录构造迷你 wiki fixture，子进程跑脚本、解析 `--json` 输出断言，不碰真实内容。运行 `python3 -m unittest discover -s tests`，CI 每次 push 也会执行。

| 测试类 | 用例数 | 覆盖点 |
|---|:---:|---|
| `TestGoodFixture` | 5 | 最小 wiki 全绿（退出码 0）；schema 单源（WIKI.md 自定义 type `note` 被接受）；带链实体页通过；引号包裹的 `evidence_level: "A"` 合法；`[[页#锚点]]` / `[[页.md]]` 不算断链 |
| `TestHardFailures` | 7 | 断链 → 退出码 1；缺 `type` → 1；缺 `evidence_level` → 1；C 级页无 ⚠️ 警示 → 1；`entity_type` 与目录不符 → 1；半角 `级(出处:…)` 报错 → 1；库根不存在 → 2 |
| `TestStrict` | 1 | 孤儿页默认软告警（退出码 0），`--strict` 下判死（退出码 1） |
| `TestGitDateBasis` | 1 | git 提交日期优先于 mtime（回归：pages 键缺 `.md` 后缀曾致静默降级，由 CI 首次暴露） |
| `TestIndexGenerator` | 2 | 生成 → `--check` 通过 → 改页未重建 → `--check` 报错；空 wiki 也能生成 |
| `TestSemiAutoChecks` | 4 | `updated` 超阈值进过时清单；>30 天含时效词进清单；标题被提及 ≥2 次未加链；「引号词」≥3 次无页 → 建页候选 |
| `TestWikiNew` | 4 | 脚手架建实体页后 lint 零硬告警；拒绝覆盖已有页（退出码 2）；非法 `entity_type` 拒绝；concept 按目录映射落位 |
