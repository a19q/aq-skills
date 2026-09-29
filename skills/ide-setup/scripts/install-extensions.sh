#!/usr/bin/env bash
# 检查并安装 VSCode 插件（幂等：已安装的跳过）
#
# 用法：
#   ./install-extensions.sh <清单文件> [--cli code] [--dry-run]
#
# 示例：
#   ./install-extensions.sh ../assets/frontend-extensions.txt --dry-run
#   ./install-extensions.sh ../assets/fastapi-extensions.txt
#   ./install-extensions.sh ../assets/frontend-extensions.txt --cli windsurf
#
# 退出码：0=全部成功（或 dry-run）；1=参数/环境错误；2=部分插件安装失败

set -uo pipefail

LIST_FILE=""
CLI=""
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cli)     CLI="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) sed -n '2,14p' "$0"; exit 0 ;;
    *)         LIST_FILE="$1"; shift ;;
  esac
done

if [[ -z "$LIST_FILE" ]]; then
  echo "错误：未指定插件清单文件。用法：$0 <清单文件> [--cli code] [--dry-run]" >&2
  exit 1
fi

if [[ ! -f "$LIST_FILE" ]]; then
  echo "错误：清单文件不存在：$LIST_FILE" >&2
  exit 1
fi

# ── 自动探测编辑器 CLI ──
if [[ -z "$CLI" ]]; then
  for candidate in code cursor windsurf code-insiders trae; do
    if command -v "$candidate" >/dev/null 2>&1; then
      CLI="$candidate"
      break
    fi
  done
fi

if [[ -z "$CLI" ]] || ! command -v "$CLI" >/dev/null 2>&1; then
  cat >&2 <<'EOF'
错误：找不到可用的编辑器 CLI（尝试过 code / cursor / windsurf / code-insiders / trae）。

请先安装 shell 命令：
  VSCode 中按 Cmd+Shift+P → 输入 "Shell Command: Install 'code' command in PATH"
或用 --cli 显式指定，例如：--cli windsurf
EOF
  exit 1
fi

echo "使用编辑器 CLI：$CLI"
echo "插件清单：$LIST_FILE"
[[ $DRY_RUN -eq 1 ]] && echo "模式：dry-run（只检查，不安装）"
echo

# ── 读取已安装插件（小写，便于比对）──
INSTALLED=$("$CLI" --list-extensions 2>/dev/null | tr '[:upper:]' '[:lower:]')

installed_count=0
success_count=0
failed_count=0
declare -a TO_INSTALL=()
declare -a FAILED=()

# ── 第一遍：检查 ──
while IFS= read -r raw || [[ -n "$raw" ]]; do
  line="${raw%%#*}"                               # 去掉行内注释
  line="$(echo "$line" | tr -d '[:space:]')"      # 去掉所有空白
  [[ -z "$line" ]] && continue

  if echo "$INSTALLED" | grep -qix -- "$line"; then
    echo "  [已安装] $line"
    installed_count=$((installed_count + 1))
  else
    echo "  [待安装] $line"
    TO_INSTALL+=("$line")
  fi
done < "$LIST_FILE"

echo
echo "统计：已安装 $installed_count 个，待安装 ${#TO_INSTALL[@]} 个"

if [[ ${#TO_INSTALL[@]} -eq 0 ]]; then
  echo "✅ 所有插件均已安装，无需操作。"
  exit 0
fi

if [[ $DRY_RUN -eq 1 ]]; then
  echo
  echo "dry-run 结束。以下插件将被安装："
  printf '  - %s\n' "${TO_INSTALL[@]}"
  exit 0
fi

# ── 第二遍：安装 ──
echo
echo "开始安装..."
for ext in "${TO_INSTALL[@]}"; do
  echo "  → 安装 $ext"
  if "$CLI" --install-extension "$ext" --force >/dev/null 2>&1; then
    echo "    ✅ 成功"
    success_count=$((success_count + 1))
  else
    echo "    ❌ 失败"
    FAILED+=("$ext")
    failed_count=$((failed_count + 1))
  fi
done

echo
echo "────────────────────────────"
echo "已安装（跳过）：$installed_count"
echo "本次安装成功：  $success_count"
echo "安装失败：      $failed_count"

if [[ $failed_count -gt 0 ]]; then
  echo
  echo "失败清单："
  printf '  - %s\n' "${FAILED[@]}"
  echo
  echo "失败通常是因为插件市场源不可用，或该插件不在当前编辑器的市场中。"
  echo "可参考 references/extension-install.md 用 vsix 离线安装。"
  exit 2
fi

echo "✅ 全部完成。"
exit 0
