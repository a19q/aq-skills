---
name: ide-setup
description: 在 VSCode/兼容编辑器（Cursor、Windsurf）当前工作区初始化项目级编辑器配置——① 创建 AI agent 配置目录（如 .claude、.codex，已有专门说明按说明、否则参考官网默认）；② 生成 .vscode/settings.json（支持 FastAPI 与前端两套模板）；③ 按清单检查并安装缺失插件（已装跳过）。严格遵守作用域：只做用户明确要求的那一类，其余不碰；目标已存在且用户未说明覆盖/追加时一律终止并询问。用户提到「初始化编辑器/项目配置」「配置 .vscode / settings.json」「初始化 claude/codex 配置」「安装 fastapi/前端项目插件」时使用。
license: Apache-2.0
allowed-tools: Bash, Read, Write, Glob
disable-model-invocation: true
---

# 项目编辑器配置初始化

在**当前工作区**（用户项目根目录）生成项目级编辑器配置。三类产物彼此独立，按用户要求**只做对应类**：

| 用户要的                     | 产物                                          | 参考                                                               |
| ---------------------------- | --------------------------------------------- | ------------------------------------------------------------------ |
| 初始化某个 **AI agent** 配置 | 项目根 agent 目录（`.claude/`、`.codex/` …）  | [references/agents.md](references/agents.md)                       |
| 初始化 **.vscode 设置**      | `.vscode/settings.json`（FastAPI / 前端模板） | [references/vscode-settings.md](references/vscode-settings.md)     |
| 安装 **项目插件**            | 按清单检查并装缺失插件（不改任何配置文件）    | [references/extension-install.md](references/extension-install.md) |

> 本技能数据来源于工作区 `ide setting/` 目录，已整理为 `assets/`（模板/清单）+ `references/`（说明）+ `scripts/`（幂等脚本）。
> `ide setting/settings/user-settings.md` 是**用户级**设置，不属于本技能内容，**忽略**。

## ⚠️ 铁律（最高优先级）

1. **作用域严格**：只做用户明确要求的那一类/那一个对象，不主动扩展。
   - 「初始化 claude 配置」→ 只建 `.claude/`，不碰 `.vscode`、不装插件。
   - 「安装前端插件」→ 只装前端清单插件，不写 settings、不建 agent 目录。
   - 「初始化 fastapi 编辑器设置」→ 只写 `.vscode/settings.json`。
2. **已存在即终止，除非明确授权覆盖/追加**：
   - agent 目录（`.claude/` 等）**已存在 → 立即终止**，不覆盖不追加，告知用户并询问。
   - `.vscode/settings.json` **已存在且用户没说覆盖/合并 → 终止**，询问要 `append`（合并保留旧值）还是 `overwrite`（覆盖，会备份）。
   - 不存在则按用户意图**新建**（`.vscode` 目录不存在就一并创建）。
3. **每个写操作前**用一句话说明要创建/修改的路径；涉及覆盖已有文件必须先得到确认。

## 执行流程

先定位**用户项目根目录**（当前工作区，非本技能目录）。以下各步按需执行——用户只要求哪类就只走哪步。

### 1. AI agent 配置（如 claude / codex）

详见 [references/agents.md](references/agents.md)。

- 确定目标目录：claude → `.claude/`；codex → `.codex/`。
- 检查目录是否已存在：**存在 → 终止并询问**；不存在 → 新建。
- 取配置模板落盘：
  - `ide setting/agent setting/<agent>/` 有专门说明 → 以它为准（claude 用
    `assets/agent-configs/claude/settings.local.json` → 落为 `.claude/settings.local.json`）。
  - 没有专门说明（codex 目录为空）→ 参考官网默认，用
    `assets/agent-configs/codex/config.toml` → 落为 `.codex/config.toml`。
- claude 场景提示：`settings.local.json` 是个人文件，建议加进 `.gitignore`。

```bash
# 示例：初始化 claude（目录存在则终止）
test -d .claude && echo "终止：.claude 已存在" || mkdir -p .claude
```

### 2. `.vscode/settings.json` 设置

详见 [references/vscode-settings.md](references/vscode-settings.md)。

- 识别项目类型：FastAPI → `assets/fastapi-settings.json`；前端 → `assets/frontend-settings.json`。
- 落盘用 `scripts/merge-settings.py`（支持 JSONC，保护已有值，已内置 create/append/overwrite 三态）：

```bash
# 目标不存在 → 新建；已存在 → 脚本以码 3 终止（安全保护）
python3 <技能目录>/scripts/merge-settings.py <技能目录>/assets/fastapi-settings.json .vscode/settings.json --mode create
# 用户明确要合并：
... --mode append     # 保留用户已有键，只补新增键
# 用户明确要覆盖：
... --mode overwrite  # 覆盖，自动备份 .bak
```

- 落盘前提醒并按实际项目调整**项目专属值**（venv 路径、`.env.dev`、`fastapi-runner` 目录、
  前端 `prettier.prettierPath`、Vetur/Volar 选择）。模板里已用注释标出。
- `.vscode` 目录不存在时脚本会自动创建。

### 3. 安装项目插件

详见 [references/extension-install.md](references/extension-install.md)。

- 识别项目类型选清单：FastAPI → `assets/fastapi-extensions.txt`；前端 → `assets/frontend-extensions.txt`。
- 用脚本「先检查、未装才装」（幂等，大小写不敏感）：

```bash
# 先 dry-run 看缺哪些
<技能目录>/scripts/install-extensions.sh <技能目录>/assets/frontend-extensions.txt --dry-run
# 确认后安装
<技能目录>/scripts/install-extensions.sh <技能目录>/assets/frontend-extensions.txt
# CLI 探测不到时指定编辑器：--cli code | cursor | windsurf
```

- 安装失败（市场源不通 / 插件不在当前编辑器市场）→ 按 reference 里的 vsix 离线方式兜底。
- 只装对应清单的插件，不写任何配置文件。

## 完成后汇报

按实际执行的类别汇报：创建的 agent 目录/文件、`.vscode/settings.json`（新建/合并/覆盖，含备份路径）、
插件「已装跳过 N 个 / 新装 M 个 / 失败 K 个」及失败清单。未被要求的类别明确说明「未改动」。
