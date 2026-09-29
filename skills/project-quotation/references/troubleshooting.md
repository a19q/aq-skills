# 常见故障排查

## 类型列显示为非法值 / 下拉打不开

**原因**：写入了简体术语（`UI开发`、`逻辑开发`、`接口对接`），但模板数据验证允许值是繁体或英文。

**处理**：先读取目标 sheet 的 `data_validations` 取允许值清单，按语义映射后重写 C 列。模板没有对应项时停下来问用户，不要硬塞。

## 某个 sheet 的下拉不见了

**原因**：用 `wb.copy_worksheet` 新建 sheet，`data_validations` 未被复制。

**处理**：逐条从源 sheet 读 `DataValidation`，在新 sheet 上 `add_data_validation`，保留原 `sqref`。见 `excel-openpyxl.md` 第 5 节。

## 合计人天没变

**可能原因**：

1. 合计单元格被覆盖成静态数字 —— 恢复为 `=SUM(E:E)`
2. E 列被写成字符串 `"0.5"` 而不是数字 —— 写入 `float`，不要写 `str`
3. 用 openpyxl 以 `data_only=True` 读取后再保存 —— 公式会被抹成缓存值，**读取时不要用 `data_only=True` 再回写**

## 红字没生效

**可能原因**：

1. 只设了 `color` 却新建了空 `Font()`，丢掉了字号字体 —— 从原 font `copy()` 后只改 `color`
2. XML 方案里用了错误的 `xf` 索引 —— 按 `excel-xml-fallback.md` 第 4 步实测索引
3. 颜色写成 `FF0000`（6 位）—— openpyxl 用 8 位 ARGB：`FFFF0000`

## 序号不连续

追加、删除、重排之后统一重排一遍序号，只对 D 列非空的行编号。

## Excel 报「文件已损坏」

XML 方案重写 zip 时漏掉了原有条目，或 `count` / `uniqueCount` / `dimension` 未同步。做法：一次性读入全部条目到 dict，改完后整体写回。

**建议**：动手前先备份 `cp 目标.xlsx 目标.bak.xlsx`。

## 权限不足 / 文件被占用

- 文件在 Excel 或 WPS 中打开着 → 提示用户关闭后重试
- 下载目录无写权限 → 保存到当前工作目录，并在回复中说明

## 明细重复报价

用户要求把汇总项拆细时，**先删除原汇总行再追加**。改完后按 D 列文本查一遍重复：

```python
seen = {}
for r in range(2, ws.max_row + 1):
    d = ws.cell(row=r, column=4).value
    if d:
        seen.setdefault(d, []).append(r)
print({k: v for k, v in seen.items() if len(v) > 1})
```

## 用户只给了项目名就要报价

这属于需求不足。只创建文件、sheet 和表头，不写明细，并提醒用户补充可拆分的功能说明。见 SKILL.md「前置闸门」。
