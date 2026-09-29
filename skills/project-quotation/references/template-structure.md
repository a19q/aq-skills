# 报价模板结构

本文件记录 `人天报价模板PMX.xlsx` 的真实结构，用于快速比对或在没有模板文件时重建。

## 列布局

| 列 | 含义 | 宽度 |
| --- | --- | --- |
| A | 序号 | 6.48076923076923 |
| B | 功能 | 32.8557692307692 |
| C | 类型（挂数据验证下拉） | 25.7980769230769 |
| D | 报价明细 | 62.1826923076923 |
| E | 人天 | 12.5 |
| F | （不使用） | 8.88461538461539 |
| G | Total | 9.92307692307692 |

## 表头（第 1 行）

`A1=序号`、`B1=功能`、`C1=类型`、`D1=报价明细`、`E1=人天`、`G1=Total`。

字体统一为 `宋体 11 号 FF000000`，对齐为水平居中 + 垂直居中。

## 合计公式

`G2 = "=SUM(E:E)"`，字体与对齐同表头。**不要重写这个单元格**，追加行后 Excel 会自动重算。

## 类型列数据验证允许值

```
邏輯, 軟件接口對接, 頁面, 定義一個實體（含CURD）, 定義一個實體的DBUP, 接口, 硬件接口對接, 硬件集成, Discount
```

作用范围通常为 `C2:C1048576`，`allow_blank=True`。

## 完整重建脚本

等价于 `scripts/build_template.py`，此处保留内联版本便于直接粘贴执行。

```python
import os
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.datavalidation import DataValidation

OUT = os.path.join(os.path.expanduser("~"), "Downloads", "人天报价模板PMX.xlsx")

wb = Workbook()
ws = wb.active
ws.title = "Sheet1"

col_widths = {
    "A": 6.48076923076923,
    "B": 32.8557692307692,
    "C": 25.7980769230769,
    "D": 62.1826923076923,
    "E": 12.5,
    "F": 8.88461538461539,
    "G": 9.92307692307692,
}
for col_letter, width in col_widths.items():
    ws.column_dimensions[col_letter].width = width

font = Font(name="宋体", size=11, color="FF000000")
align = Alignment(horizontal="center", vertical="center")

headers = {
    "A1": "序号",
    "B1": "功能",
    "C1": "类型",
    "D1": "报价明细",
    "E1": "人天",
    "G1": "Total",
}
for cell_ref, value in headers.items():
    c = ws[cell_ref]
    c.value = value
    c.font = font
    c.alignment = align

c = ws["G2"]
c.value = "=SUM(E:E)"
c.font = font
c.alignment = align

dv = DataValidation(
    type="list",
    formula1='"邏輯,軟件接口對接,頁面,定義一個實體（含CURD）,定義一個實體的DBUP,接口,硬件接口對接,硬件集成,Discount"',
    allow_blank=True,
)
dv.sqref = "C2:C1048576"
ws.add_data_validation(dv)

wb.save(OUT)
print("saved:", OUT)
```

## 行高

模板中所有行高均为 `None`（默认），**不要显式设置行高**。
