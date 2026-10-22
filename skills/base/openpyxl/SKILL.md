---
name: openpyxl
name_zh: Excel 读写（openpyxl）
description: 用 openpyxl 开源工具纯 Python 读写 .xlsx：单元格、公式、样式、图表、筛选、条件格式。当任务需要 Excel 读写（openpyxl） 且希望用开源、可独立运行的底层工具（gridcraft 开源替代）时使用。
triggers: [openpyxl, Excel 读写]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: office-admin
layer: base
backs: gridcraft 开源替代
version: 1
license: MIT
---

# openpyxl · Excel 读写（openpyxl）

**它让我们能做什么：** 办公文档：表格生成、填数、出图表，接 python-docx / python-pptx 出报告。

纯 Python 读写 .xlsx：单元格、公式、样式、图表、筛选、条件格式。

## 定位

- 槽位：gridcraft 开源替代
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT

## 安装

```sh
pip install openpyxl
```

## 核心用法

```
from openpyxl import Workbook, load_workbook
from openpyxl.chart import BarChart, Reference
wb = Workbook(); ws = wb.active
ws.append(["月份", "营收"]); [ws.append([f"{m}月", m*100]) for m in range(1, 13)]
ws["D1"] = "=SUM(B2:B13)"
ch = BarChart(); ch.add_data(Reference(ws, min_col=2, min_row=1, max_row=13), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=1, min_row=2, max_row=13)); ws.add_chart(ch, "F2")
wb.save("out.xlsx")
v = load_workbook("out.xlsx", data_only=True)   # 注意：只能读到 Excel 上次保存时缓存的公式结果
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- openpyxl 不计算公式；需要数值时用 `soffice --headless --convert-to xlsx` 重算后再 `data_only=True` 读取核对。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
