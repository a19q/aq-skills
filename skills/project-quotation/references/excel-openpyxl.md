# openpyxl 操作手册（首选路径）

先确认可用：

```bash
python3 -c "import importlib.util; print(importlib.util.find_spec('openpyxl') is not None)"
```

不可用时先尝试安装，失败再走 `excel-xml-fallback.md`：

```bash
python3 -m pip install --quiet openpyxl || echo "fallback to XML"
```

## 1. 读取工作簿结构与数据验证允许值

动手前必做这一步——尤其是拿到 C 列允许值清单。

```python
import openpyxl

wb = openpyxl.load_workbook(PATH)
for ws in wb.worksheets:
    print("sheet:", ws.title, "max_row:", ws.max_row)
    print("header:", [c.value for c in ws[1]])
    for dv in ws.data_validations.dataValidation:
        print("  dv sqref:", dv.sqref, "formula1:", dv.formula1)
```

`formula1` 形如 `"邏輯,軟件接口對接,頁面,..."`，去掉首尾引号后按逗号切分即得允许值列表。

## 2. 术语映射

```python
KIND_KEYWORDS = {
    "UI开发":   ["頁面", "页面", "Page"],
    "组件开发": ["頁面", "页面", "Page"],
    "逻辑开发": ["邏輯", "逻辑", "Logic"],
    "接口对接": ["軟件接口對接", "软件接口对接"],
}
DAYS = {"UI开发": 0.5, "组件开发": 0.5, "逻辑开发": 1, "接口对接": 0.5}

def map_kind(kind, allowed):
    for kw in KIND_KEYWORDS[kind]:
        for a in allowed:
            if kw in a:
                return a
    raise SystemExit(f"未找到 {kind} 对应的模板允许值，请与用户确认映射：{allowed}")
```

匹配 `接口对接` 时注意排除 `硬件接口對接`，所以关键词用完整的 `軟件接口對接` 而不是 `接口`。

## 3. 找到真实的最后数据行

`ws.max_row` 会被空白样式行、合计公式行干扰，应以 A 列序号为准：

```python
last = 1
for r in range(2, ws.max_row + 1):
    if ws.cell(row=r, column=1).value is not None:
        last = r
next_row = last + 1
next_seq = (ws.cell(row=last, column=1).value or 1) + 1 if last > 1 else 1
```

## 4. 追加报价行（含标红）

```python
from copy import copy
from openpyxl.styles import Font

RED = "FFFF0000"

def append_row(ws, row_idx, seq, feature, kind_value, detail, days, highlight):
    tpl = ws.cell(row=row_idx - 1, column=1) if row_idx > 2 else None
    values = {1: seq, 2: feature, 3: kind_value, 4: detail, 5: days}
    for col, val in values.items():
        c = ws.cell(row=row_idx, column=col, value=val)
        if tpl is not None:
            c.font = copy(ws.cell(row=row_idx - 1, column=col).font)
            c.alignment = copy(ws.cell(row=row_idx - 1, column=col).alignment)
            c.border = copy(ws.cell(row=row_idx - 1, column=col).border)
    if highlight:
        d = ws.cell(row=row_idx, column=4)
        f = copy(d.font)
        d.font = Font(name=f.name or "宋体", size=f.size or 11, bold=f.bold, color=RED)
```

要点：

- 从上一行 `copy()` 字体/对齐/边框，保持样式一致
- 标红只改 D 列字体颜色，其余属性沿用
- **不要写 F 列**，不要触碰合计公式单元格

## 5. 复制 sheet 时同步数据验证

`wb.copy_worksheet` 不复制 `data_validations`，必须手工补：

```python
from openpyxl.worksheet.datavalidation import DataValidation

src = wb["Sheet1"]
dst = wb.copy_worksheet(src)
dst.title = "Sheet2"

for dv in src.data_validations.dataValidation:
    new_dv = DataValidation(
        type=dv.type,
        formula1=dv.formula1,
        allow_blank=dv.allow_blank,
        showDropDown=dv.showDropDown,
        showErrorMessage=dv.showErrorMessage,
    )
    new_dv.sqref = dv.sqref          # 保留原范围
    dst.add_data_validation(new_dv)
```

同时确认列宽也已复制（`copy_worksheet` 会带列宽，但跨工作簿复制不会）。

## 6. 删除被拆细替换的汇总行

用户要求把一条汇总项拆成多条时，先删旧行再追加新行，然后重排序号：

```python
ws.delete_rows(target_row, 1)
for i, r in enumerate(range(2, ws.max_row + 1), start=1):
    if ws.cell(row=r, column=4).value is None:
        continue
    ws.cell(row=r, column=1, value=i)
```

## 7. 写入后校验

```python
wb2 = openpyxl.load_workbook(PATH)
ws2 = wb2["Sheet1"]
total = 0
for r in range(2, ws2.max_row + 1):
    detail = ws2.cell(row=r, column=4).value
    if not detail:
        continue
    kind = ws2.cell(row=r, column=3).value
    days = ws2.cell(row=r, column=5).value
    color = ws2.cell(row=r, column=4).font.color
    total += days or 0
    print(r, ws2.cell(row=r, column=1).value, kind, days,
          "RED" if color and color.rgb == "FFFF0000" else "", detail)
print("总人天:", total)
```

校验清单：序号连续、类型在允许值内、人天符合固定规则、红字只在增补行的 D 列、总人天与预期一致。
