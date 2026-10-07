# AGENTS.md — agent 操作入口

本仓库是 **LLM Wiki 模式**的知识笔记库：外部内容先原样存档到 `raw/`（不可变），经逐条溯源核查后沉淀为 `wiki/` 结构化知识页。维护者 = AI agent + 用户；用户负责喂料与提问，agent 负责写入与维护。

## 先读这个

**`WIKI.md` 是唯一规则源**（定级约定 / 入库规则 / lint 规则 / schema）。page type、entity/concept 子类型、目录映射的允许值都由脚本实时解析自 WIKI.md 的 yaml 块——不要凭本文件记忆这些值，以 WIKI.md 为准。

## 三条核心命令

```bash
python3 scripts/wiki-new.py <type> <slug> [选项]   # 建页：自动落目录、填 frontmatter、拒绝覆盖
python3 scripts/wiki-index.py                       # 重建 wiki/index.md（入库后必跑；禁手改）
python3 scripts/wiki-lint.py                        # 自检：16 项；退出码 0 全绿 / 1 硬告警 / 2 库根不存在
python3 scripts/wiki-lint.py --json                 # 机器可读输出（自动化判断用 --json，不要解析文本）
python3 -m unittest discover -s tests               # 改脚本后必跑的回归自测
```

## 入库（ingest）

- **仅用户明确指令触发**（`user_only`）；不主动提议入库、不追问
- 允许：外部链接 / 文件 / 论文 / 视频，用户显式点名的素材
- 禁止：日常对话、会话内容、查询问答结果——**query 只答，不写回 wiki**（唯一例外：用户点名"这个答案入库"，可沉淀为 `questions/` 页，`type: question`）
- 四件套 + 提交：`raw/` 快照（数字标抓取日期）→ wiki 页（新建或追加）→ 重跑 `wiki-index.py` 登记 → `log.md` 留痕 → lint 全绿后 `git commit`

## 写作约定（对应 lint 第 13 项，CI --strict 下软告警也判死）

- 页标题用带括号的完整名（如 `智谱（Zhipu）`），正文行文用简称
- `wiki/` 页正文禁用「」直角引号，一律用“”（「」是 lint 的缺页候选探测器）
- 他页实体 / 专题首次提及加 `[[]]` 链接

## 硬边界

- `raw/` 不可变：只写不改，它是溯源头（lint 第 16 项按 git 历史校验，CI `--strict` 下判死）
- `wiki/index.md` 由脚本生成：不手改，改了 CI 的 `--check` 会红
- 定级双轴不混写：来源等级 `A/B/C/D` × 吻合度 `🟢/🟡/🔴`；改判定先核实再改标签，核不实标 C/D，不猜不折中
- 数字 / 版本号必须本次实时抓取并标日期，不凭记忆代填
- lint 硬告警（断链 / 缺 frontmatter / 定级 / 类型 / 子类型 / 转述警示 / 引用可溯）未清零前不提交
