---
title: AI时代代码审查转向系统行为
type: concept
concept_type: method
created: 2026-07-23
updated: 2026-07-23
tags: [code-review, ai-code, system-testing, engineering-practice]
related:
  - [[entities/people/benoit-schillings]]
  - [[sources/articles/deepmind-software-engineering-not-about-code]]
  - [[concepts/theories/software-engineering-vs-coding]]
---

# AI时代代码审查转向系统行为

Benoit Schillings 预测：一年后开发者会让模型直接生成代码，不再逐行阅读。

## 传统审查 → 未来审查

| 传统代码审查 | 未来系统行为审查 |
|-------------|-----------------|
| 逐行阅读代码 | 查看接口契约变化 |
| 找语法/logic bug | 检查权限是否扩大 |
| 风格检查 | 性能基线是否倒退 |
| 人工走读 | 新依赖供应链风险 |

## 自动化手段

- 单元测试 + 集成测试
- 静态扫描
- 运行时指标监控
- 回滚记录

## 类比

今天有多少程序员会在构建后阅读编译器输出的汇编？同理，未来也不会有人逐行读 AI 生成的代码。

## 来源

- [[sources/articles/deepmind-software-engineering-not-about-code]]
