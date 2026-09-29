# XML 兜底方案（openpyxl 不可用时）

`xlsx` 本身是 zip 包，可直接编辑其中的 XML。以下命令可直接复用，实际使用时只替换文件名、行范围、目标条目。

处理已有报价文件时的原则：保留原工作表结构与样式、优先复用已有共享字符串、仅在需要时新增红字样式并后续复用、追加行后同步 `dimension` 范围、保持序号连续。

## 1. 查看压缩包结构

```bash
unzip -l '目标文件.xlsx'
```

关注 `xl/worksheets/sheet1.xml`、`xl/sharedStrings.xml`、`xl/styles.xml`。多 sheet 时先看 `xl/workbook.xml` 确认 sheet 名与文件序号的对应关系。

## 2. 读取共享字符串与工作表行

```bash
python3 - <<'PY'
import zipfile, xml.etree.ElementTree as ET
ns={'a':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile('目标文件.xlsx') as z:
    sst=[]
    root=ET.fromstring(z.read('xl/sharedStrings.xml'))
    for si in root.findall('a:si', ns):
        sst.append(''.join(t.text or '' for t in si.iterfind('.//a:t', ns)))
    ws=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    for row in ws.findall('.//a:sheetData/a:row', ns):
        vals=[]
        for c in row.findall('a:c', ns):
            t=c.attrib.get('t')
            if t=='s':
                v=sst[int(c.findtext('a:v', namespaces=ns))]
            else:
                v=c.findtext('a:v', default='', namespaces=ns)
            vals.append((c.attrib['r'], c.attrib.get('s'), v))
        print('row', row.attrib['r'], vals)
PY
```

## 3. 读取类型列数据验证允许值

```bash
python3 - <<'PY'
import zipfile, xml.etree.ElementTree as ET
ns={'a':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile('目标文件.xlsx') as z:
    ws=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    for dv in ws.iter(f'{{{ns["a"]}}}dataValidation'):
        print(dv.attrib.get('sqref'), dv.findtext('a:formula1', namespaces=ns))
PY
```

## 4. 查看样式索引并确认红字样式

```bash
python3 - <<'PY'
import zipfile, xml.etree.ElementTree as ET
ns={'a':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile('目标文件.xlsx') as z:
    styles=ET.fromstring(z.read('xl/styles.xml'))
    fonts=styles.find('a:fonts', ns)
    for i,f in enumerate(fonts.findall('a:font', ns)):
        color=f.find('a:color', ns)
        print('font', i, color.attrib if color is not None else None)
    cellxfs=styles.find('a:cellXfs', ns)
    print('cellXfs count', cellxfs.attrib.get('count'))
    for i,xf in enumerate(cellxfs.findall('a:xf', ns)):
        align=xf.find('a:alignment', ns)
        print('xf', i, xf.attrib, align.attrib if align is not None else None)
PY
```

若已存在 `color rgb="FFFF0000"` 的 font 及引用它的 `xf`，**复用该 xf 索引**作为标红样式，不要重复新增。

## 5. 追加报价行

只需修改 `path`、`new_rows`、以及标红行用的样式索引。

```bash
python3 - <<'PY'
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

path = Path('目标文件.xlsx')
ns = {'a': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
ET.register_namespace('', ns['a'])

# (序号, 功能, 类型-必须是模板允许值, 报价明细, 人天, 是否标红)
new_rows = [
    ('10', 'FR-02', '頁面', '标记工具栏UI开发', '0.5', False),
    ('11', 'FR-02', '邏輯', '标记清除功能交互逻辑开发', '1', True),
]

STYLE_NORMAL = '3'   # D 列常规样式索引（按第 4 步实测替换）
STYLE_RED = '3'      # D 列红字样式索引（按第 4 步实测替换）

with zipfile.ZipFile(path, 'r') as zin:
    files = {name: zin.read(name) for name in zin.namelist()}

sst_root = ET.fromstring(files['xl/sharedStrings.xml'])
strings = []
string_to_idx = {}
for i, si in enumerate(sst_root.findall('a:si', ns)):
    text = ''.join(t.text or '' for t in si.iterfind('.//a:t', ns))
    strings.append(text)
    string_to_idx.setdefault(text, i)

def get_sst_idx(text):
    if text in string_to_idx:
        return string_to_idx[text]
    si = ET.Element(f'{{{ns["a"]}}}si')
    t = ET.SubElement(si, f'{{{ns["a"]}}}t')
    t.text = text
    sst_root.append(si)
    idx = len(strings)
    strings.append(text)
    string_to_idx[text] = idx
    return idx

for _, func, typ, detail, _, _ in new_rows:
    get_sst_idx(func); get_sst_idx(typ); get_sst_idx(detail)

sst_root.set('uniqueCount', str(len(strings)))
sst_root.set('count', str(len(strings)))
files['xl/sharedStrings.xml'] = ET.tostring(sst_root, encoding='utf-8', xml_declaration=True)

ws_root = ET.fromstring(files['xl/worksheets/sheet1.xml'])
sheet_data = ws_root.find('a:sheetData', ns)
rows = sheet_data.findall('a:row', ns)
start_row_num = max(int(r.attrib['r']) for r in rows) + 1

for offset, (seq, func, typ, detail, days, red) in enumerate(new_rows):
    rnum = start_row_num + offset
    row = ET.Element(f'{{{ns["a"]}}}row', {'r': str(rnum), 'spans': '1:7'})

    def add_num(ref, value, style='1'):
        c = ET.SubElement(row, f'{{{ns["a"]}}}c', {'r': ref, 's': style})
        ET.SubElement(c, f'{{{ns["a"]}}}v').text = value

    def add_s(ref, text, style):
        c = ET.SubElement(row, f'{{{ns["a"]}}}c', {'r': ref, 's': style, 't': 's'})
        ET.SubElement(c, f'{{{ns["a"]}}}v').text = str(get_sst_idx(text))

    add_num(f'A{rnum}', seq)
    add_s(f'B{rnum}', func, '1')
    add_s(f'C{rnum}', typ, '2')
    add_s(f'D{rnum}', detail, STYLE_RED if red else STYLE_NORMAL)
    add_num(f'E{rnum}', days)
    sheet_data.append(row)

last_row = start_row_num + len(new_rows) - 1
for dim in ws_root.findall('a:dimension', ns):
    dim.set('ref', f'A1:G{last_row}')

files['xl/worksheets/sheet1.xml'] = ET.tostring(ws_root, encoding='utf-8', xml_declaration=True)

with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zout:
    for name, data in files.items():
        zout.writestr(name, data)
print('appended rows', start_row_num, '-', last_row)
PY
```

## 6. 新增红字样式（仅当第 4 步确认不存在时）

在 `xl/styles.xml` 的 `<fonts>` 末尾追加一个红色 font，再在 `<cellXfs>` 末尾追加引用它的 `xf`（复制原 D 列 xf 的属性，只改 `fontId`），同时把 `fonts` 和 `cellXfs` 的 `count` 加一。新 `xf` 的下标即为 `STYLE_RED`。

## 7. 校验最后追加的行

```bash
python3 - <<'PY'
import zipfile, xml.etree.ElementTree as ET
START = 10   # 起始行号
ns={'a':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile('目标文件.xlsx') as z:
    sst=[]
    root=ET.fromstring(z.read('xl/sharedStrings.xml'))
    for si in root.findall('a:si', ns):
        sst.append(''.join(t.text or '' for t in si.iterfind('.//a:t', ns)))
    ws=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    for row in ws.findall('.//a:sheetData/a:row', ns):
        r=int(row.attrib['r'])
        if r < START:
            continue
        vals=[]
        for c in row.findall('a:c', ns):
            t=c.attrib.get('t')
            if t=='s':
                v=sst[int(c.findtext('a:v', namespaces=ns))]
            else:
                v=c.findtext('a:v', default='', namespaces=ns)
            vals.append((c.attrib['r'], c.attrib.get('s'), v))
        print('row', r, vals)
PY
```

## 注意事项

- 重写 zip 时必须写回**全部**原有条目，漏掉任何一个都会让 Excel 报「文件已损坏」
- 修改共享字符串后同步更新 `count` 与 `uniqueCount`
- `spans` 属性要覆盖实际写入的列范围
- 合计单元格是公式，追加行后不要动它；Excel 打开时会重算
