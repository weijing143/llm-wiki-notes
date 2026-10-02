---
title: Software Engineering vs Coding (AI时代)
type: concept
concept_type: theory
created: 2026-07-23
updated: 2026-10-01
tags: [software-engineering, coding, ai-era, methodology]
related:
  - [[entities/people/benoit-schillings]]
  - [[sources/articles/deepmind-software-engineering-not-about-code]]
  - [[concepts/methods/ai-code-review-shift]]
  - [[concepts/theories/programming-language-for-ai]]
---

# Software Engineering vs Coding (AI时代)

Benoit Schillings 提出的核心区分：写代码只是软件工程的一小部分。

## 核心理念

AI 时代代码生成免费，但软件工程的总成本不会清零：

- **代码** → 生成一段可运行的代码，只是第一步
- **软件工程** → 理解系统结构、理清模块依赖、判断改动范围、证明修改不会破坏已有功能

## 3500万行PHP测试

新工程师面对 3500 万行 PHP 代码库，在不破坏系统的情况下动一处逻辑——这才是软件工程。

> ⚠️ 上句中的「3500 万行」为 **C 级转述**（源自 [[sources/articles/deepmind-software-engineering-not-about-code]] 对演讲的翻译整理，未核实一手），引用该数字时须一并标注。

## 成本转移

| 过去 | 未来 |
|------|------|
| 写代码成本最高 | 代码接近免费 |
| 限制因素是机器 | 限制因素是人脑+系统复杂度 |
| 功能开发人员不够拒绝需求 | Agent 几分钟实现 → 运维面暴增 |

## 关键问题

每个代码改动都要回答：
1. 是不是我们需要的？
2. 能否在真实系统长期运行？
3. 如果错了，能不能看见并撤回？

## 来源

- [[sources/articles/deepmind-software-engineering-not-about-code]]
