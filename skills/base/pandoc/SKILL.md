---
name: pandoc
name_zh: 文档格式互转（Pandoc）
description: 用 pandoc 开源工具通用文档转换器：Markdown、docx、HTML、LaTeX、EPUB、pptx 等互转，支持参考样式模板与引用。当任务需要 文档格式互转（Pandoc） 且希望用开源、可独立运行的底层工具（wordcraft / deckcraft 格式转换补位）时使用。
triggers: [pandoc, 文档格式互转]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: office-admin
layer: base
backs: wordcraft / deckcraft 格式转换补位
version: 1
license: GPL-2.0+
---

# pandoc · 文档格式互转（Pandoc）

**它让我们能做什么：** 办公文档：Markdown 写作一键出 Word/PDF/PPT，串起 AI 输出与办公格式。

通用文档转换器：Markdown、docx、HTML、LaTeX、EPUB、pptx 等互转，支持参考样式模板与引用。

## 定位

- 槽位：wordcraft / deckcraft 格式转换补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：GPL-2.0+

## 安装

```sh
sudo apt install pandoc  # macOS: brew install pandoc；PDF 另需 texlive-xetex
```

## 核心用法

```
pandoc in.md -o out.docx --reference-doc=template.docx
pandoc in.docx -t gfm -o out.md --extract-media=media
pandoc in.md -o out.pdf --pdf-engine=xelatex -V CJKmainfont="Noto Serif CJK SC"
pandoc slides.md -o slides.pptx
pandoc paper.md --citeproc --bibliography=refs.bib -o paper.docx
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 打开输出核对标题层级、图片和表格；中文 PDF 必须指定 CJK 字体否则缺字。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
