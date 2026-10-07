---
title: 智谱×AWS：GLM-5.3接入Bedrock与调用量分成
type: collection
created: 2026-10-07
updated: 2026-10-07
evidence_level: C
related: [entities/organizations/zhipu, entities/organizations/aws]
---

# 智谱×AWS：GLM-5.3接入Bedrock与调用量分成

> ⚠️ 本页 evidence_level 为 C：全部来源均为媒体转述（B 站日报视频 + 财经媒体报道），未定位到 AWS 或智谱官方公告原文。数字以各来源报道口径为准，抓取日期 2026-10-07；若日后定位到官方公告（A 级），本页页级可随之上调。

## 核心结论

2026-10-06，AWS 旗下大模型托管平台 Amazon Bedrock 官宣接入智谱 GLM-5.3，并按模型调用量与智谱收入分成——这是智谱 9 月披露的“海外云平台分成”战略的首个落地案例，标志国产大模型出海从“卖 API”转向“与云厂商按账单分成”。入库线索（B 站日报视频）标题“智谱宣布与亚马逊达成合作”与来源口径存在偏差：官宣主体是 AWS / Bedrock，接入对象是具体模型 GLM-5.3，故判 🟡 而非 🟢（核查表第 3 条）。

相关实体：[[entities/organizations/zhipu]]、[[entities/organizations/aws]]

## 核查表

> 图例：来源等级 A 官方一手 · B 自报 · C 转述 · D 待确认 ｜ 吻合度 🟢 与来源吻合 · 🟡 措辞口径偏差或演绎 · 🔴 口径放大或不符 ｜ — 背景共识（只标注不计数）

| # | 主张 | 吻合度 | 来源等级 | 出处 |
|---|------|--------|----------|------|
| 1 | 2026-10-06 Amazon Bedrock 官宣接入智谱 GLM-5.3，企业客户可经托管 API 调用，支持跨区域推理与 Prompt Cache | 🟢 | C | [[sources/articles/cnstock-bedrock-glm53]] |
| 2 | AWS 将基于模型调用量与智谱进行收入分成，区别于一次性授权（智谱向记者确认） | 🟢 | C | [[sources/articles/cnstock-bedrock-glm53]] |
| 3 | 日报视频标题“智谱宣布与亚马逊达成合作，部署GLM模型按调用量分成”——官宣主体实为 AWS / Bedrock，接入对象为 GLM-5.3 而非笼统“GLM 模型” | 🟡 | C | [[sources/articles/ai-daily-540]] |
| 4 | 智谱 2026-09-16 分析师电话会披露：已与多家海内外头部云服务商签署收入分成协议，相关收入 2026 年 10 月起确认 | 🟢 | C | [[sources/articles/thepaper-bedrock-glm53]] |
| 5 | 智谱全业务口径 ARR 达 18 亿美元；年末 ARR 目标由 24 亿上调至 30 亿美元（2026-09-16 披露） | 🟢 | C | [[sources/articles/thepaper-bedrock-glm53]] |
| 6 | 国内：阿里云百炼已签署类似分成协议；华为云已上架 GLM-5.3 并就同类分成合作达成意向 | 🟢 | C | [[sources/articles/cnstock-bedrock-glm53]] |
| 7 | 2026-09-30 Baseten 宣布企业用户可在 OpenAI Codex 中调用 Kimi K3 与 GLM-5.3，费用计入企业已有 OpenAI 采购承诺额度 | 🟢 | C | [[sources/articles/thepaper-bedrock-glm53]] |
| 8 | 2026-10-06 智谱（02513.HK）收盘 715.5 港元，涨 7.59%，成交 25.05 亿港元 | 🟢 | C | [[sources/articles/thepaper-bedrock-glm53]] |
| 9 | 高盛将智谱评级由“中性”上调至“买入”，2026 年底 ARR 预测由 27 亿上调至 32 亿美元 | 🟢 | C | [[sources/articles/cnstock-bedrock-glm53]] |
| 10 | OpenRouter 统计：中国模型全球调用份额 2026 年 6 月初整体超美国，7 月下旬近 28 天约 63.5%（转述统计，未核原始数据） | 🟡 | C | [[sources/articles/thepaper-bedrock-glm53]] |
| — | — 背景共识：Anthropic 2025 年约 46 亿美元收入中约 47% 经 Amazon / Google 云市场完成（市场消息，未定位一手，仅作模式参照） | — | — | [[sources/articles/cnstock-bedrock-glm53]] |

## 反方视角

- **自部署分流**：GLM-5.3 为开放权重模型，企业既可经 Bedrock 按调用付费，也可下载权重自行部署；模型越开放，云 API 收入被分流的风险越大（第一财经转引的市场观点）。
- **条款不透明**：双方均未披露分成比例与保底条款，收入兑现速度与规模存在不确定性（经济观察报的谨慎观点）。
- **海外合规门槛**：海外企业对数据安全、模型责任与供应链稳定性的要求，可能影响大规模生产部署。
- **成本端压力未消**：分成模式免去自建海外推理集群的资本开支，但模型持续迭代仍需高额研发投入，智谱短期盈利压力仍在。

## 后续跟踪点

- 定位 AWS / 智谱官方公告原文（A 级来源；本页升级的关键）
- 智谱 2026 Q4 财报：云平台分成收入的实际确认规模，对照年末 ARR 30 亿美元目标
- 华为云分成协议是否正式签署；除 AWS 外其他海外云厂商的落地名单
- Bedrock 上 GLM-5.3 的定价与实际调用量（对比企业自部署成本）

## 归档记录

- 2026-10-07 创建（[[index]]）：线索来自 B 站 AI 日报第 540 期（BV1a9pF61EBc），原始快照 `raw/notes/ai-daily-540-2026-10-07.md`，溯源检索快照 `raw/notes/zhipu-aws-bedrock-verify-2026-10-07.md`。
