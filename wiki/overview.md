---
title: LLM Wiki Notes Overview
type: overview
created: 2026-07-23
updated: 2026-10-02
sources: []
---

# LLM Wiki Notes Overview

## Introduction

本样本沉淀**经核查的外部内容**，不收录日常对话与查询结果（入库规则见库根 `WIKI.md`）。建库于 2026-07-23；截至 **2026-10-01**：13 个 wiki 页（4 个专题 · 3 实体 · 3 概念 · 1 来源摘要 · index / overview）、5 份 `raw/` 快照。所有主张均带来源等级（A/B/C/D）与吻合度标记；本页为**首次合成**（此前长期为模板占位）。

## Key Themes（跨专题主题）

1. **巨头从"卖模型 / 卖工具"转向"占入口"**
   Anthropic 同时做免费教育（[[collections/ai-education-2026]]）与自建湿实验室做药（[[collections/ai-pharma-2026]]）；OpenAI 走平台 / agentic coding 路线（同上、[[collections/openai-alien-mind-2026]]）。教育、制药、开发者工具都是"抢占默认选项"的前沿。

2. **"语言模型化"范式在向非文本领域扩张**
   代码（软件工程）→ 蛋白质 / 药物设计 → 基因组（DNA 当语言生成）→ 教育方法论。同一套范式在不同领域复现：[[concepts/theories/programming-language-for-ai]]、[[collections/ai-genome-design-2026]]、[[collections/ai-pharma-2026]]。

3. **能力加速与安全治理的张力**
   OpenAI 首席科学家自陈"没有实验室（含 OpenAI 自己）准备好"，承认最看重的 CoT 监控可靠性在下降，呼吁把自愿承诺升级为外部强制底线（[[collections/openai-alien-mind-2026]]）；AI 设计病原体的生物安全议题是同一张力在生物域的表现（[[collections/ai-genome-design-2026]]）。

4. **自媒体内容的信息质量有可预测的分布**
   三张核查表的经验：**"事件 / 事实"类主张多与来源吻合**；**"金额规模、身份头衔、时间跨度"处最易出现口径放大或转述偏差**——如 AI 制药页 #9 把"四领域分摊的 10 亿"说成"一年全投生命科学"（口径放大）、#13 未定位到出处、#6 头衔细节偏差；教育页 #3 的"员工培训"属演绎。

5. **成本转移是本样本最一致的经济学观察**
   写代码变免费 → 为代码负责变贵（[[concepts/theories/software-engineering-vs-coding]]）；药物研发周期被宣称从 10 年压到 1 年（[[collections/ai-pharma-2026]]）；当下真正先兑现的是算力与工具（"卖铲子的先收钱"）。

## Major Entities

| 实体 | 位置 | 要点 |
|---|---|---|
| Anthropic | [[entities/organizations/anthropic]] | 跨教育 / 制药两专题；2026 起生态扩张最活跃 |
| Google DeepMind | [[entities/organizations/google-deepmind]] | 旗下 Isomorphic Labs 独立做药；研究总裁见 [[entities/people/benoit-schillings]] |
| OpenAI | [[collections/openai-alien-mind-2026]] · [[collections/ai-pharma-2026]] | 安全立场（Preparedness Framework）+ 平台路线 |
| NVIDIA / AMD | [[collections/ai-pharma-2026]] | 算力侧；礼来联合实验室、Absci / ReefIQ |
| Moderna + 默沙东 | [[collections/ai-pharma-2026]] | 个性化 mRNA 癌症疫苗（intismeran 三期双终点达标） |
| Arc Institute | [[collections/ai-genome-design-2026]] | Evo 基因组模型；首个 AI 设计噬菌体 |

## Core Concepts

- **证据定级体系**（本样本自身方法论）：来源等级 A/B/C/D + 吻合度标记 + `—` 背景共识，两轴不得混写——规则见库根 `WIKI.md`
- **软件工程 ≠ 写代码**：成本从"写"转移到"判断 / 验证 / 担责"（[[concepts/theories/software-engineering-vs-coding]]）
- **审查对象转移**：逐行读码 → 接口契约 / 权限 / 性能基线 / 供应链风险（[[concepts/methods/ai-code-review-shift]]）
- **为模型而非人类设计的语言**：强类型 / 形式化验证优先（[[concepts/theories/programming-language-for-ai]]）
- **对齐的两个层次**：goal alignment（目标）vs value alignment（价值）；RSI（递归自我改进）；CoT monitoring（[[collections/openai-alien-mind-2026]]）
- **4D AI Fluency**：Delegation / Description / Discernment / Diligence（[[collections/ai-education-2026]]）

## 收藏专题速查

| 专题 | 时点 | 一句话 |
|---|---|---|
| [[collections/ai-pharma-2026]] | 2026-08 | 六玩家布局 + 13 条主张核查；结论"方向成立但需打折" |
| [[collections/ai-genome-design-2026]] | 2026-08 | 首个 AI 设计噬菌体（Science 论文）+ 事件时间线 |
| [[collections/ai-education-2026]] | 2026-08 | Claude Academy 免费课程体系 + 4D 框架 |
| [[collections/openai-alien-mind-2026]] | 2026-09 | 《An Alien Mind》原文要点 + 6 条分级核查 |

## Open Questions

- Anthropic 湿实验室的首个管线项目是什么？（[[collections/ai-pharma-2026]]）
- Isomorphic 的闭源路线（IsoDDE）能否持续领先于开源 AlphaFold 系？（同上）
- Evo 基因组模型是否开源？AI 设计病原体的监管如何落地？（[[collections/ai-genome-design-2026]]）
- 4D 框架会不会被企业培训采纳为事实标准？Claude Academy 会否推出付费认证？（[[collections/ai-education-2026]]）
- CoT 监控可靠性下降有无替代手段（confessions / activation monitoring）？（[[collections/openai-alien-mind-2026]]）
- "自愿减速"会真的普遍化，还是停留在呼吁？（同上）

## Knowledge Gaps

- **缺一手学术来源**：`sources/` 仅 1 页且是 **C 级公众号转述**（[[sources/articles/deepmind-software-engineering-not-about-code]]，"3500 万行 PHP"等数字未核实一手）→ 需补演讲原件（官方录像 / slides）或论文原文
- **实体覆盖薄且偏组织**：3 个实体页（1 人 / 2 组织）；无产品、技术、事件类实体页；跨专题人物（John Jumper、Jakub Pachocki）尚无实体页
- **缺对比与分析类页面**：`analyses` / `comparisons` 为空——跨厂商横向对比（如 Anthropic vs OpenAI 安全立场）尚未成页
- **定级体系缺校准样本**：B 级（自报）与 D 级（待确认）在全库极少出现，等级区分度未经充分检验
- **视角偏美国厂商**：六大玩家与主要来源均为美国公司，缺中国 / 亚洲 AI 产业的一手材料

---
*本页为跨页合成（人工 + lint 触发），数据截至 2026-10-01*
