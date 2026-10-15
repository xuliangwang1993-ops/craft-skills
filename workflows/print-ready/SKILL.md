---
name: print-ready
name_zh: 印刷交付流水线
description: 把设计稿做成可送印的文件：矢量稿绘制与检查 → 色彩空间与出血确认 → 导出印刷级 PDF 并做完整性校验。当任务涉及名片、海报、包装、画册的送印文件准备时使用。
triggers: [印刷, 送印, 出血, CMYK, 名片, 海报, 包装]
inputs:
  - name: task
    description: 任务描述与交付要求
    required: true
tools: []
mcp: [vectorcraft, pdfcraft]
permissions: [read_file, write_file]
version: 1
license: MIT
category: arts-design-media
kind: workflow
---
# 印刷交付流水线

## 为什么要串起来

屏幕上好看的稿子，**送印前有一堆硬性检查**（出血、色彩空间、字体嵌入、分辨率），漏一个就废版。

## 涉及引擎

- `vectorcraft`
- `pdfcraft`

## 流水线

1. **VectorCraft `open_file` / 新建** —— 开稿或建新稿
2. **VectorCraft `draw_path` / `draw_shape` / `set_paint`** —— 绘制与上色
3. **VectorCraft `render_preview`** —— 目视检查
4. **确认关键参数** —— 色彩空间（印刷 **必须 CMYK**）、出血（通常 3mm）、安全边距
5. **VectorCraft `export` → PDF/SVG** —— 导出印刷级文件
6. **PdfCraft `info`** —— 检查页面尺寸、字体嵌入、是否有异常
7. **PdfCraft `audit`** —— 顺便查一下有没有意外残留的隐藏内容

## 坑点（踩过才写在这里）

- **CMYK vs RGB**：送印用 RGB 会被印刷厂退回或色彩严重偏差
- **出血要留**：3mm 出血是行业默认，不留的话裁切会切到内容
- **字体要嵌入或转曲**：否则印刷厂的机器没这个字体，排版全乱
- **分辨率**：位图元素在印刷稿里至少 300 DPI

## 路径注意

引擎是 Windows 可执行文件，**不认 WSL 的 `/mnt/c/...` 路径**，必须传 Windows 格式（`C:\\Users\\you\\out.pdf`）。从 WSL 调用时用 `wslpath -w <路径>` 转换。
