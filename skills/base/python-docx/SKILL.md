---
name: python-docx
name_zh: Word 读写（python-docx）
description: 用 python-docx 开源工具Python 读写 .docx：段落、样式、表格、图片、页眉页脚、分节。当任务需要 Word 读写（python-docx） 且希望用开源、可独立运行的底层工具（wordcraft 开源替代）时使用。
triggers: [python-docx, Word 读写]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: office-admin
layer: base
backs: wordcraft 开源替代
version: 1
license: MIT
---

# python-docx · Word 读写（python-docx）

**它让我们能做什么：** 办公文档：合同、报告、批量生成文书。

Python 读写 .docx：段落、样式、表格、图片、页眉页脚、分节。

## 定位

- 槽位：wordcraft 开源替代
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT

## 安装

```sh
pip install python-docx
```

## 核心用法

```
from docx import Document
from docx.shared import Pt, Inches
doc = Document()
doc.add_heading("报告标题", level=1)
p = doc.add_paragraph("正文 "); p.add_run("加粗").bold = True
t = doc.add_table(rows=1, cols=2, style="Table Grid"); t.rows[0].cells[0].text = "项目"
doc.add_picture("chart.png", width=Inches(5))
doc.save("out.docx")
for para in Document("in.docx").paragraphs: print(para.style.name, para.text)
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 重新打开核对段落数/表格数；`soffice --headless --convert-to pdf` 目视排版。不支持修订痕迹的完整读写，需要时用 wordcraft。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
