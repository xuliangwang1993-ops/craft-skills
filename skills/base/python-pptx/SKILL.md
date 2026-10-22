---
name: python-pptx
name_zh: PPT 生成（python-pptx）
description: 用 python-pptx 开源工具Python 生成/修改 .pptx：版式、文本、图片、表格、原生图表。当任务需要 PPT 生成（python-pptx） 且希望用开源、可独立运行的底层工具（deckcraft 开源替代）时使用。
triggers: [python-pptx, PPT 生成]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: office-admin
layer: base
backs: deckcraft 开源替代
version: 1
license: MIT
---

# python-pptx · PPT 生成（python-pptx）

**它让我们能做什么：** 办公文档：数据直接生成路演稿和汇报 PPT。

Python 生成/修改 .pptx：版式、文本、图片、表格、原生图表。

## 定位

- 槽位：deckcraft 开源替代
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT

## 安装

```sh
pip install python-pptx
```

## 核心用法

```
from pptx import Presentation
from pptx.util import Inches
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
prs = Presentation()
s = prs.slides.add_slide(prs.slide_layouts[1])
s.shapes.title.text = "季度汇报"; s.placeholders[1].text = "要点一\n要点二"
s2 = prs.slides.add_slide(prs.slide_layouts[5])
cd = CategoryChartData(); cd.categories = ["Q1","Q2","Q3"]; cd.add_series("营收", (10, 14, 19))
s2.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(1), Inches(1.5), Inches(8), Inches(5), cd)
s2.shapes.add_picture("logo.png", Inches(8.5), Inches(0.2), height=Inches(0.8))
prs.save("out.pptx")
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- `soffice --headless --convert-to pdf out.pptx` 后渲染检查文字溢出；核对页数。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
