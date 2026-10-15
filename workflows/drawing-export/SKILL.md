---
name: drawing-export
name_zh: 图纸归档流水线
description: 把 CAD 图纸批量转成可分发格式并归档：图纸侦察 → 图元与文字检索 → 批量转 PDF/SVG → 合集校验。当任务涉及工程图交付、图纸归档、批量转换或图纸内容检索时使用。
triggers: [CAD, 图纸, DXF, DWG, 工程图归档, 图纸转换]
inputs:
  - name: task
    description: 任务描述与交付要求
    required: true
tools: []
mcp: [cadcraft, pdfcraft]
permissions: [read_file, write_file]
version: 1
license: MIT
category: arts-design-media
kind: workflow
---
# 图纸归档流水线

## 为什么要串起来

CAD 图纸对方多半打不开（要专业软件），**转成 PDF 才能发给非专业人士**；而批量转换前必须知道图里有什么。

## 涉及引擎

- `cadcraft`
- `pdfcraft`

## 流水线

1. **CADCraft `inspect_drawing`** —— 摸清图层、范围、单位
2. **CADCraft `query_entities` + `find_text`** —— 定位关键图元、检索标注文字（要找某个编号的构件就靠这个）
3. **CADCraft `render` → PDF/PNG/SVG** —— 单张出图
4. **CADCraft `script`** —— **批量转换**多张图纸
5. **PdfCraft `doc_combine`** —— 合并成图纸册
6. **PdfCraft `info` / `page_render`** —— 校验页数与出图质量

## 坑点（踩过才写在这里）

- **单位与比例**：mm 和 inch 搞错会让图纸完全没法用，转换前必须确认
- **改图先备份**：CAD 图元关联复杂，误改难复原
- **PDF 给甲方，SVG/DXF 给后续编辑**：两者用途不同，别只出一种
- **图层可见性**：出图前确认该隐藏的图层已隐藏，否则会漏不该给的内容

## 路径注意

引擎是 Windows 可执行文件，**不认 WSL 的 `/mnt/c/...` 路径**，必须传 Windows 格式（`C:\\Users\\you\\out.pdf`）。从 WSL 调用时用 `wslpath -w <路径>` 转换。
