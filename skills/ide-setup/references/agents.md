# AI Agent 项目级配置参考

初始化某个 AI agent 的编辑器配置 = 在项目根目录创建该 agent 的项目级配置文件夹。
**只创建 agent 自己的配置目录；目录已存在则终止，不覆盖、不追加**（用户明确要求覆盖/合并除外）。

配置来源规则：

- 若 `ide setting/agent setting/<agent>/` 下有专门说明 → **以它为准**（当前 `claude` 有）。
- 若没有专门说明（当前 `codex` 目录为空）→ **参考该 agent 官网**，按下文默认配置创建。

> 配置文件正文请从 `assets/agent-configs/` 取模板文件原样落盘，本文档只说明放哪、什么语义。

---

## Claude Code → `.claude/`

项目级配置放在项目根目录 `.claude/` 下。

| 文件 | 作用 | 是否入库 |
| --- | --- | --- |
| `.claude/settings.json` | 团队共享配置（权限、hooks、env 等），随仓库提交 | 是 |
| `.claude/settings.local.json` | 个人本地配置（私有权限等），**不提交** | 否（应加 .gitignore） |
| `CLAUDE.md` | 项目说明/约定（代码架构、命令、风格） | 视团队而定 |

**优先级**（高→低）：managed → CLI 命令行 → `.claude/settings.local.json`（本地）→ `.claude/settings.json`（共享）→ 用户级 `~/.claude/settings.json`。

### 本技能的处理

- `ide setting/agent setting/claude/settings.local.json.md` 有专门说明 → **以它为准**，用
  `assets/agent-configs/claude/settings.local.json` 落盘为 `.claude/settings.local.json`。
- 该模板内容为允许 `npm run *` 的权限白名单；初始化后提示用户按需把 `.claude/settings.local.json`
  加入 `.gitignore`（个人文件）。
- 若用户还需要团队共享配置，可另建 `.claude/settings.json`（参考官网：
  https://code.claude.com/docs/en/settings ）。

初始化后建议追加：

```bash
# .gitignore
.claude/settings.local.json
```

---

## Codex → `.codex/`

Codex 的**项目级**配置放在仓库根目录 `.codex/config.toml`（用户级在 `~/.codex/config.toml`）。
`AGENTS.md` 是另一回事——它是项目说明文件（类似 CLAUDE.md），不是配置文件。

**优先级**（高→低）：CLI flags → 项目 `.codex/config.toml`（就近生效，仅限受信任项目）
→ profile → 用户级 `~/.codex/config.toml` → 系统级 → 内置默认。

> 安全说明：项目级 `.codex/` 层只在用户**信任该项目**时才加载；标记为不信任时 Codex 会跳过
> 项目内 config/hooks/rules。

### 本技能的处理

`ide setting/agent setting/codex/` 为空（无专门说明）→ **参考官网**，用
`assets/agent-configs/codex/config.toml` 落盘为 `.codex/config.toml`。

默认配置（最小可用，来源：官方配置文档）：

```toml
model = "gpt-5.6"
approval_policy = "on-request"   # on-request | untrusted | never
sandbox_mode = "workspace-write" # read-only | workspace-write | danger-full-access
```

- `model`：默认模型。
- `approval_policy`：执行命令前何时请求批准。
- `sandbox_mode`：命令执行时的文件/网络访问范围。

官网参考：https://learn.chatgpt.com/docs/config-file/config-basic

---

## 新增其他 Agent

遇到未列出的 agent（cursor rules、windsurf 等）：

1. 先看 `ide setting/agent setting/<agent>/` 是否有专门说明；有则以它为准。
2. 没有则查该 agent 官网的**项目级**配置路径与最小配置，在项目根创建对应目录/文件。
3. 同样遵守：目录已存在 → 终止并询问，不擅自覆盖。
