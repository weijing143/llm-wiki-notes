---
project: llm-wiki-notes
domain: general
created: 2026-07-23
version: 3.4
updated: 2026-10-07
---

# Wiki Configuration

> 本仓库是 **LLM Wiki 模式**的可复用空模板：只含框架（规则 + 目录骨架 + 自检脚本），尚未入库任何内容。外部内容先原样存档到 `raw/`（不可变），再经核查沉淀为 `wiki/` 结构化知识页。

## Project Info

- **Name**: LLM Wiki Notes ｜ **Domain**: general
- **Description**: 外部内容经核查后沉淀的结构化知识页（LLM Wiki 模式）
- **Created**: 2026-07-23 ｜ **配置版本**: 3.4

## 三层结构

| 层 | 路径 | 规则 |
|---|---|---|
| 源文档 | `raw/`（notes · articles · transcripts · papers · assets · data） | 不可变、只写不改；数字标抓取日期，作溯源头 |
| 知识库 | `wiki/`（index · overview · collections · entities · concepts · sources） | 由人工 + agent 协作维护；交叉引用用 `[[页面路径]]` |
| 配置 / 日志 | `WIKI.md`（本文件）· `log.md` | 规则与约定（定级 / 入库 / lint）；`log.md` 记录操作留痕（当前为空模板，暂无条目） |

**分类目录按需创建**：现有 `entities/people`、`entities/organizations`、`concepts/theories`、`concepts/methods`、`sources/articles`、`collections`，以及备用空槽 `analyses`、`comparisons`、`questions`、`sources/papers`（均 .gitkeep 占位）；`entities/products|technologies|places`、`concepts/frameworks` 未建目录，需要时 `mkdir` 即可。

**`raw/` 落点规则**：`articles/` 网页原文 ｜ `notes/` **实际主力**——视频快照、API 快照、检索笔记均落此处 ｜ `papers/` 论文 PDF ｜ `assets/` 图片 / 附件 ｜ `transcripts/` 会议 / 访谈转写 ｜ `data/` 独立数据集文件。后四者目前为空槽（.gitkeep 占位），保留备用、不做迁移。

## Page Types

每页 frontmatter **必填 `type:`**，允许值：

> **schema 单源**：`scripts/wiki-lint.py` 与 `scripts/wiki-new.py` 直接解析本文件的 ```yaml 块获取允许值与目录映射——改 schema 只改本文件，脚本无需同步。解析失败时脚本回退内置默认值并打印告警。

```yaml
page_types:
  allowed: [index, overview, collection, entity, concept, source, analysis, comparison, question]
  required_fields:
    index: []                                # 总目录
    overview: []                             # 跨专题合成页；不标等级
    collection: [evidence_level]             # 专题页；页级等级 + 表内逐条标
    entity: [entity_type]                    # 实体页；entity_type ∈ 实体类型菜单，且与父目录一致
    concept: [concept_type]                  # 概念页；concept_type ∈ 概念分类菜单，且与父目录一致
    source: [evidence_level, source_type]    # 来源页；evidence_level 为等级源头；source_type 自由文本
  notes:
    - evidence_level 取值：A/B/C/D 或 N/A（N/A 仅限全部主张均无外部来源的内部记录页）
    - C / D 级页正文必须含 ⚠️ 显式警示（lint 第 10 项）
    - entity / concept 页引用等级须写作 `A 级（出处：collections/<专题>）`（lint 第 11 项校验字母合法 + 出处存在）
```

## Entity Types

```yaml
entities:
  types: [person, organization, product, technology, event]   # 允许值菜单；entity_type 字段取值范围
  dir_mapping:                                                # lint 第 9 项：entity_type 与父目录必须一致
    people: person
    organizations: organization
    products: product
    technologies: technology
    events: event
  suggested_attributes:                                       # 文档性指引；lint 暂不强制校验
    person: [role, affiliation, expertise]
    organization: [industry, size, location]
    product: [category, company, status]
    technology: [category, maturity, adopters]
    event: [date, type, significance]
```

## Concept Categories

```yaml
concepts:
  categories: [theory, method, framework, metric, principle]  # concept_type 字段取值范围
  dir_mapping:                                                # lint 第 9 项：concept_type 与父目录必须一致
    theories: theory
    methods: method
    frameworks: framework
    metrics: metric
    principles: principle
```

## 定级约定（Evidence Grading）

**两套标记 = 两个轴，不得混写在同一格。**

| 标记 | 轴 | 含义 |
|---|---|---|
| `A/B/C/D` | **来源等级** | A 官方一手 · B 自报（主体自行披露）· C 转述（含公众号转述演讲）· D 待确认（无法定位或互相冲突） |
| `🟢/🟡/🔴` | **吻合度** | 🟢 与来源吻合 · 🟡 方向真实但措辞口径有偏差、或属演绎·转述 · 🔴 口径放大或与来源不符 |
| `—` | 补充标记 | 背景共识：非被核查主张的背景陈述，只标注不计数 |

**载体分工**：`source` 页 frontmatter 必填 `evidence_level`（等级源头）→ `collection` 页填页级等级并在表内逐条标 → `entity` / `concept` 继承（引用时写成 `A 级（出处：collections/<专题>）`）→ `overview` / `index` 不标。

**页级等级推导（木桶原则）**：`collection` 页只有唯一的页级 `evidence_level`，当表内逐条来源等级不一致时，**页级取最低的来源等级**（宁严勿宽；读者看到页级即得到整页可信度的下界保证）。全部主张均无外部来源时才允许填 N/A。

**硬要求**：

- 每张核查表**自带图例**（读者不必回查本文件）
- 表内每条主张**逐条标注**吻合度 / 来源等级；漏标由 lint 第 12 项告警
- 数字 / 日期可溯源到具体来源页；**转述级须在正文顶部显式警示**（⚠️）
- 改判定**先核实再改标签**（直抓一手 URL 对原文），核不实按 C/D 标，不猜不折中
- 摘要与核查表不一致时**以表为准**，并在原处留「勘误」注记，不静默替换
- 跨页**同形态主张判定必须一致**
- `source` 页等级空白会波及全部下游页 → 优先修
- 自动校验：`scripts/wiki-lint.py` 第 7 / 10 / 11 / 12 项，运行 `python3 scripts/wiki-lint.py`

## 入库规则（Ingest）

```yaml
ingest:
  trigger: user_only              # 仅用户明确指令；不主动提议、不追问
  allow_sources: [外部来源（链接 / 文件 / 论文 / 视频）, 用户显式点名的素材]
  deny_sources:  [日常对话, 会话内容, 查询问答结果]      # query 只答，不写回 wiki
  artifacts:                      # 四件套 + 提交
    - raw/<分类>/<主题>-<日期>.md         # 原始快照；数字标抓取日期
    - wiki/collections/<主题>-<年>.md     # 或向现有页追加
    - wiki/index.md                      # 登记
    - log.md                             # 操作留痕
    - git commit                          # 收尾提交
  page_decision: 同主题续条 → 追加现有页；同域不同主题 → 新建独立页
  collection_page_sections: [核心结论, 核查表（带图例）, 反方视角, 后续跟踪点, 归档记录]
  anti_orphan: 新建页在 frontmatter `related:` 直接挂兄弟页，不等实体 / 概念页
  data_integrity: stars / 版本号 / 数字必须本次实时抓取并标日期，不凭记忆代填
```

## Lint Rules

```yaml
lint:
  trigger: manual + CI            # 本地手动执行；push / PR 时 GitHub Actions 跑 --strict
  cadence: 按需 / 结构变动后        # 例：批量归档后、重建后
  automated:                      # 共 13 项，见脚本 docstring
    [断链, 孤儿页, 缺 frontmatter, updated 与变更日期漂移, index 重复区块,
     log.md 漏记, 定级完整性, type 完整性, 子类型一致性, 转述级警示, 等级引用可溯,
     逐条覆盖, 结构计数]
  severity:                       # v3.4 起分级，决定退出码
    hard: [断链, 缺 frontmatter, 定级完整性, type 完整性, 子类型一致性,
           转述级警示, 等级引用可溯]        # 存在即退出码 1
    soft: [孤儿页, updated 漂移, index 重复区块, log.md 漏记, 逐条覆盖]
                                        # 默认不影响退出码；--strict 下也判死
    info: [结构计数]                      # 不参与判死
  exit_codes: {0: 全绿或仅软告警, 1: 硬告警（--strict 含软告警）, 2: 库根不存在}
  date_basis: git 提交日期（clone/checkout 会重置 mtime）；无 git 历史时降级 mtime 并在输出中标注
  flags: [--strict, --json]       # --json 供自动化消费（含各项 violations 与退出码）
  schema_source: 允许值 / 目录映射解析自本文件 yaml 块（单源）
  self_test: python3 -m unittest discover -s tests -v   # 脚本回归自测
  manual: [跨页矛盾, 过时声明, 缺失页面, 数据缺口]
  on_fix: 修完复跑脚本确认全绿
```

## 建页脚手架（wiki-new）

```yaml
scaffold:
  script: scripts/wiki-new.py
  templates: templates/           # collection / entity / concept / source / generic
  usage:
    - python3 scripts/wiki-new.py collection <slug> --title 标题
    - python3 scripts/wiki-new.py entity <slug> --entity-type person
    - python3 scripts/wiki-new.py concept <slug> --concept-type theory
    - python3 scripts/wiki-new.py source <slug> --evidence-level C
  behavior:
    - 按 schema 目录映射落到正确目录，自动填 created / updated / type / 子类型
    - 目标已存在拒绝覆盖；entity_type / concept_type 不在菜单内直接报错
    - 只建文件，index.md 登记与 log.md 留痕仍按入库四件套执行
```

## Output Preferences

```yaml
output:
  default_format: markdown
  include_citations: true
```

---
*配置版本 3.4 ｜ 空模板版*
