# `.vscode/settings.json` 项目设置参考

`.vscode/settings.json` 是**项目级 / 工作区级**编辑器设置（随仓库提交，团队共享）。
与之区分：

- **用户级**设置（`~/Library/Application Support/Code/User/settings.json`）是个人全局配置，
  对应 `ide setting/settings/user-settings.md`——**本技能不处理用户级**，除非用户明确要求。
- 本技能只写项目根的 `.vscode/settings.json`。

| 项目类型 | 模板文件 |
| --- | --- |
| FastAPI（Python） | `assets/fastapi-settings.json` |
| 前端 | `assets/frontend-settings.json` |

模板是 JSONC（允许注释），VSCode 原生支持。落盘前注意模板里标注的**项目专属值**：

- FastAPI：`fastapi-runner.workingDirectory`、`fastapi-runner.defaultFile`、`.env.dev`、
  `.venv/bin/python` 等需按实际目录/启动方式调整。
- 前端：`prettier.prettierPath` 是 monorepo 专属路径，普通项目应删除；
  Vetur 段仅 Vue 2 需要，Vue 3 用 Volar（`vue.volar`）应删除 Vetur 段。

---

## 安全规则（关键）

对已有的 `.vscode/settings.json`，**默认不覆盖、不追加**。只有用户明确给出模式才动：

| 目标状态 | 用户说法 | 动作 |
| --- | --- | --- |
| `.vscode` / `settings.json` 不存在 | 初始化 fastapi/前端设置 | **新建**目录与文件，写入模板 |
| 已存在，用户**没说**覆盖/合并 | 初始化设置 | **终止**，告知文件已存在，询问要 append 还是 overwrite |
| 已存在，用户说「**合并/追加/补上**」 | append | 合并，**保留用户已有键的值**，只补模板里新增的键 |
| 已存在，用户说「**覆盖/用模板替换**」 | overwrite | 整体覆盖（先备份 `.bak`） |

落盘用脚本 `scripts/merge-settings.py`，已实现上述三态且保护已有值：

```bash
# create：目标不存在才写；已存在则报错退出（码 3）
python3 scripts/merge-settings.py assets/fastapi-settings.json .vscode/settings.json --mode create

# append：合并，冲突键保留用户原值；先 dry-run 预览
python3 scripts/merge-settings.py assets/frontend-settings.json .vscode/settings.json --mode append --dry-run
python3 scripts/merge-settings.py assets/frontend-settings.json .vscode/settings.json --mode append

# overwrite：整体覆盖（自动备份 settings.json.bak）
python3 scripts/merge-settings.py assets/fastapi-settings.json .vscode/settings.json --mode overwrite
```

退出码：`0` 成功；`1` 参数/IO 错误；`2` JSON 解析失败；`3` 目标已存在（create 模式命中保护）。

说明：

- 脚本能解析 JSONC（注释、尾逗号），也能解析被 markdown 围栏包裹的片段。
- 合并输出为标准 JSON，**不保留注释**；需要注释语义时回看 `assets/` 原模板。
- append 会自动备份原文件为 `settings.json.bak` 后再写。

---

## 作用域纪律

- 初始化「fastapi 编辑器设置」→ **只动 `.vscode/settings.json`**，不装插件、不建 agent 目录，
  除非用户一并要求。
- `.vscode` 里的其他文件（`extensions.json`、`launch.json`、`tasks.json`）不在模板范围，不主动创建。
