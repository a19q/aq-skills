---
name: pr-review
description: 使用 glab 在 GitLab 上审查 Merge Request。覆盖三个子任务：①审计代码——仅 review 当前分支 PR 相对 base 分支的最终 diff（忽略提交过程与 commit 历史），查逻辑错误、语法警告或报错、敏感数据、风格规范、冗余写法；②PR 合法性检查——里程碑、approve rule ≥1 人、body 含 Close issue、pmx link 规则、Assignee；③提交 review comment——把用户确认的问题以 inline comment 提交到 PR，只说明问题不给建议、必须引用到代码。用户提到「审计代码」「review PR/MR」「代码审查」「PR 合法性检查」「提交 review comment」时使用。
license: Apache-2.0
allowed-tools: Bash, Read, Grep, Glob
---

# GitLab PR（MR）审查

使用 `glab` CLI 审查 MR。三个子任务可独立执行；用户未指明时默认：先做 ①审计 + ②合法性检查，汇报结果等用户确认；用户要求时才执行 ③提交 comment。

先探测环境（与 pr-creation 相同）：

```bash
git remote -v
which glab
glab auth status   # 应显示 Logged in to <HOST> as <USERNAME>
```

`glab` 未登录或不可用时停止并告知用户先 `glab auth login`。

## ① 审计代码

- **范围红线**：只 review 当前分支 MR 相对 base 分支的**最终 diff**（汇总后的整体变更），不对整个项目泛泛而谈
- **忽略提交过程**：不逐 commit 审查、不参考 commit 历史与提交信息、不关心代码在分支上的演变经过；即使某个 commit 单独看有问题、但最终 diff 中已不存在，也不算问题
- 查 MR 与 diff 的命令见 [references/glab-api.md](references/glab-api.md)
- 审计维度（逐条过 diff）：
  1. 逻辑错误
  2. 语法代码警告或报错
  3. 代码敏感数据安全问题（硬编码密钥/凭据/日志泄露，特征正则同 code-security 技能模式①）
  4. 不符合项目代码风格规范
  5. 冗余写法
- 输出问题清单：每条含位置（`文件路径:行号` + 代码片段）、问题类型、严重程度（高/中/低）
- **先汇报给用户确认，不直接提交 comment**；用户确认后才进入 ③

## ② PR 合法性检查（checklist）

| 检查项 | 要求 |
| --- | --- |
| 里程碑 | MR 已绑定 milestone |
| approve rule | 至少 1 人审批（approvals_required ≥ 1） |
| body | 含 `Close #<issue>` |
| pmx link | 目标分支**不是** main：检查 **base 分支对应的 PR** 描述含「pmx link」和「pmx」两个全匹配字符串（不区分大小写）；目标是 main：检查**当前 PR** |
| assignee | 已设置 |

输出通过/缺失清单；缺失项可衔接 pr-creation 技能补设（assignee、milestone、审批规则均为 API 可改）。

## ③ 提交 review comment

- **只提交用户确认过的问题**
- comment 只说明问题，**不给修改建议**（不要出现「建议改成…」）
- 必须引用到相关代码：以 inline discussion 挂在具体文件与行号上，**不要只发纯文本总 comment**
- inline discussion 与 diff_refs 获取命令见 [references/glab-api.md](references/glab-api.md)

## 执行约定

- 多行 comment 内容一律写入临时文件再用 `$(cat <file>)` 传值；临时文件默认放 `~/Downloads`，用完可清理
- 每条外部动作（发 comment、改 MR 字段）执行前给用户一句简短说明
- 完成后汇报：审查的 MR 号、问题数（按严重程度）、合法性检查结果、已提交 comment 数
