---
title: Programming Language for AI (下一代编程语言)
type: concept
concept_type: theory
created: 2026-07-23
updated: 2026-07-23
tags: [programming-language, ai, formal-methods, lean]
related:
  - [[entities/people/benoit-schillings]]
  - [[sources/articles/deepmind-software-engineering-not-about-code]]
---

# Programming Language for AI (下一代编程语言)

Benoit Schillings 提出的前瞻性设想：是不是到了为模型设计新编程语言的时候？

## 核心论点

- Python 等语言为**人类**发明——易读易表达，安全与可靠性非最优先
- 既然写代码痛苦消失，可以让模型承担更高生成成本
- 使用强类型或 Lean 等形式化方法，把"证明自己正确"的压力交给模型
- 这种语言**不一定需要对人类友好**

## 现状与展望

| 现状 | 展望 |
|------|------|
| Python 对人友好 | 新语言对模型友好 |
| 人类手写为主 | 模型生成+形式化验证 |
| 手动管理复杂度 | 编译器+AI管理复杂度 |
| 安全靠人工审查 | 安全靠形式化证明 |

## 短期局限

- 线上代码仍需人类排障
- 需与已有工具链交接
- 短期内难进入大多数团队

## 深层含义

今天的编程语言和代码形态，也许只是人类亲手写代码时代的产物。

## 来源

- [[sources/articles/deepmind-software-engineering-not-about-code]]
