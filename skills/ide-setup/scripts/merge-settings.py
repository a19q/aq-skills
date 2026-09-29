#!/usr/bin/env python3
"""合并/写入 .vscode/settings.json（支持 JSONC，保护已有配置）。

用法:
    python3 merge-settings.py <模板文件> <目标settings.json> --mode {create,append,overwrite} [--dry-run]

模式语义（对应技能的安全规则）:
    create     目标文件不存在时才写入；已存在 → 报错退出（码 3），交由用户决定
    append     合并：目标已有的键**保持不变**，只补充模板中新增的键
    overwrite  用模板完全覆盖目标（会先备份为 settings.json.bak）

退出码: 0=成功 1=参数/IO错误 2=JSON解析失败 3=目标已存在（create 模式）
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path


def strip_jsonc(text: str) -> str:
    """移除 JSONC 的注释和尾逗号，使其可被 json.loads 解析。

    注意：字符串字面量内的 // 和 /* 不会被误删。
    """
    out = []
    i = 0
    n = len(text)
    in_string = False
    escaped = False

    while i < n:
        ch = text[i]

        if in_string:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue

        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue

        # 行注释
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue

        # 块注释
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue

        out.append(ch)
        i += 1

    result = "".join(out)
    # 移除尾逗号: {"a":1,}  或  [1,2,]
    result = re.sub(r",(\s*[}\]])", r"\1", result)
    return result


def load_jsonc(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")

    # 容错：模板可能被 markdown 代码围栏包裹
    fence = re.match(r"^\s*```(?:json[c5]?)?\s*\n(.*?)\n\s*```\s*$", raw, re.S)
    if fence:
        raw = fence.group(1)

    try:
        return json.loads(strip_jsonc(raw))
    except json.JSONDecodeError as exc:
        print(f"错误：解析 JSON 失败 {path}\n  {exc}", file=sys.stderr)
        sys.exit(2)


def deep_merge_keep_existing(base: dict, incoming: dict) -> tuple[dict, list, list]:
    """合并，冲突时保留 base（已有）的值。返回 (结果, 新增键, 跳过键)。"""
    result = dict(base)
    added, skipped = [], []

    for key, new_val in incoming.items():
        if key not in result:
            result[key] = new_val
            added.append(key)
        elif isinstance(result[key], dict) and isinstance(new_val, dict):
            merged, sub_added, sub_skipped = deep_merge_keep_existing(result[key], new_val)
            result[key] = merged
            added.extend(f"{key}.{k}" for k in sub_added)
            skipped.extend(f"{key}.{k}" for k in sub_skipped)
        else:
            skipped.append(key)

    return result, added, skipped


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("template", type=Path, help="模板文件（assets/*-settings.json）")
    ap.add_argument("target", type=Path, help="目标 .vscode/settings.json")
    ap.add_argument("--mode", required=True, choices=["create", "append", "overwrite"])
    ap.add_argument("--dry-run", action="store_true", help="只预览，不写盘")
    args = ap.parse_args()

    if not args.template.is_file():
        print(f"错误：模板文件不存在：{args.template}", file=sys.stderr)
        return 1

    template = load_jsonc(args.template)
    exists = args.target.is_file()

    # ── create：已存在则终止 ──
    if args.mode == "create" and exists:
        print(
            f"⛔ 终止：{args.target} 已存在。\n"
            f"   按技能安全规则，不擅自修改已有配置。\n"
            f"   如需合并请用 --mode append，如需覆盖请用 --mode overwrite。",
            file=sys.stderr,
        )
        return 3

    if args.mode == "append" and not exists:
        print(f"提示：{args.target} 不存在，append 将退化为新建。")

    existing = load_jsonc(args.target) if exists else {}

    # ── 计算最终内容 ──
    if args.mode == "overwrite":
        final, added, skipped = template, list(template), []
    else:
        final, added, skipped = deep_merge_keep_existing(existing, template)

    # ── 报告 ──
    print(f"模板  : {args.template}")
    print(f"目标  : {args.target} ({'已存在' if exists else '新建'})")
    print(f"模式  : {args.mode}")
    print(f"新增键: {len(added)}")
    for k in added:
        print(f"   + {k}")
    if skipped:
        print(f"保留原值（未覆盖）: {len(skipped)}")
        for k in skipped:
            print(f"   = {k}")

    if args.dry_run:
        print("\n[dry-run] 未写入任何文件。")
        return 0

    if args.mode != "overwrite" and not added:
        print("\n无新增键，文件保持不变。")
        return 0

    # ── 写盘 ──
    if exists:
        backup = args.target.with_suffix(args.target.suffix + ".bak")
        shutil.copy2(args.target, backup)
        print(f"\n已备份原文件 → {backup}")

    args.target.parent.mkdir(parents=True, exist_ok=True)
    args.target.write_text(
        json.dumps(final, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"✅ 已写入 {args.target}")
    print("注意：JSON 输出不保留注释；模板中的说明请回看 assets/ 原文件。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
