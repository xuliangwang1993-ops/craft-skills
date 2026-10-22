---
name: ocrmypdf
name_zh: 扫描件 OCR（OCRmyPDF）
description: 用 ocrmypdf 开源工具给扫描 PDF 加可搜索文字层，自动纠偏、去噪、输出 PDF/A。当任务需要 扫描件 OCR（OCRmyPDF） 且希望用开源、可独立运行的底层工具（pdfcraft OCR 开源替代）时使用。
triggers: [ocrmypdf, 扫描件 OCR]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: office-admin
layer: base
backs: pdfcraft OCR 开源替代
version: 1
license: MPL-2.0（依赖 Tesseract Apache-2.0、Ghostscript AGPL）
---

# ocrmypdf · 扫描件 OCR（OCRmyPDF）

**它让我们能做什么：** PDF：扫描件变可搜索、可复制的 PDF，供后续检索和审计。

给扫描 PDF 加可搜索文字层，自动纠偏、去噪、输出 PDF/A。

## 定位

- 槽位：pdfcraft OCR 开源替代
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MPL-2.0（依赖 Tesseract Apache-2.0、Ghostscript AGPL）

## 安装

```sh
sudo apt install ocrmypdf tesseract-ocr-chi-sim  # macOS: brew install ocrmypdf tesseract-lang
```

## 核心用法

```
ocrmypdf -l chi_sim+eng --deskew --rotate-pages in.pdf out.pdf
ocrmypdf --skip-text -l chi_sim in.pdf out.pdf          # 已有文字层的页跳过
ocrmypdf --output-type pdfa --optimize 2 in.pdf out.pdf
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- `pdftotext out.pdf - | head` 能提出文字；页数与原件一致。注意依赖 Ghostscript 为 AGPL。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
