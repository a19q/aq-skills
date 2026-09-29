# 插件安装参考

## 插件清单

| 项目类型 | 清单文件 | 说明 |
| --- | --- | --- |
| FastAPI（Python） | `assets/fastapi-extensions.txt` | Python 工具链 + FastAPI 辅助 + 通用 |
| 前端 | `assets/frontend-extensions.txt` | Vue/React/TS + ESLint/Prettier + 样式 + 通用 |

清单格式：每行一个 `publisher.extension`，`#` 后为注释。

---

## 标准安装流程（走脚本）

脚本 `scripts/install-extensions.sh` 已内置「**先检查、未装才装**」的幂等逻辑。

```bash
# 1) 先 dry-run 看差异，不装任何东西
./scripts/install-extensions.sh assets/frontend-extensions.txt --dry-run

# 2) 确认后实际安装
./scripts/install-extensions.sh assets/frontend-extensions.txt

# 3) 指定编辑器 CLI（不指定则自动探测）
./scripts/install-extensions.sh assets/fastapi-extensions.txt --cli windsurf
```

脚本行为：

- 自动探测 CLI，顺序：`code` → `cursor` → `windsurf` → `code-insiders` → `trae`。
- 用 `<cli> --list-extensions` 读已装列表，**大小写不敏感**比对（市场返回的 ID 大小写不统一）。
- 已装 → 打印 `[已安装]` 并跳过；未装 → `--install-extension <id> --force`。
- 结尾输出统计：已安装/成功/失败，并列出失败清单。
- 退出码：`0` 全部成功或 dry-run；`1` 参数/环境错误；`2` 有插件安装失败。

### CLI 不可用时

```
错误：找不到可用的编辑器 CLI
```

让用户在 VSCode 中执行：`Cmd+Shift+P` → `Shell Command: Install 'code' command in PATH`；
或用 `--cli` 显式指定编辑器命令。

---

## 手动检查/安装（不用脚本时）

```bash
# 查看已安装
code --list-extensions

# 检查单个是否已装
code --list-extensions | grep -ix "esbenp.prettier-vscode"

# 安装
code --install-extension esbenp.prettier-vscode --force
```

---

## 离线 / vsix 安装（市场源不可用时的兜底）

脚本报安装失败，通常是插件市场源不通，或该插件不在当前编辑器（Windsurf/Cursor 用 Open VSX）的市场里。
此时手动下载 vsix：

```bash
# 1) 从微软市场下载插件包（替换 <publisher> / <extension>）
curl -L "https://marketplace.visualstudio.com/_apis/public/gallery/publishers/Smekalin/vsextensions/vue-attr-sort/latest/vspackage" \
  -o /tmp/vue-attr-sort.vsix

# 2) 下载下来是 gzip 流，需解压还原为标准 vsix
gzip -dc /tmp/vue-attr-sort.vsix > /tmp/vue-attr-sort_decompressed.vsix

# 3) 安装到编辑器（code / cursor / windsurf 均可）
windsurf --install-extension /tmp/vue-attr-sort_decompressed.vsix
```

插件安装目录：`~/.vscode/extensions`（Windsurf 为 `~/.windsurf/extensions`）。

---

## 切换插件市场源

某些编辑器默认用 Open VSX，插件不全。可改 `product.json` 的 `extensionsGallery`：

```jsonc
// 微软官方 VS Code Marketplace 源
"extensionsGallery": {
  "serviceUrl": "https://marketplace.visualstudio.com/_apis/public/gallery",
  "cacheUrl": "https://vscode.blob.core.windows.net/gallery/index",
  "itemUrl": "https://marketplace.visualstudio.com/items",
  "controlUrl": "",
  "recommendationsUrl": ""
}

// Open VSX 开源社区源
"extensionsGallery": {
  "serviceUrl": "https://open-vsx.org/vscode/gallery",
  "itemUrl": "https://open-vsx.org/vscode/item"
}
```

> 改市场源属于**编辑器级**改动，不是项目级配置。仅在用户明确要求时才动，改完需重启编辑器。
