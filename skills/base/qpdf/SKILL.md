---
name: qpdf
name_zh: PDF 结构操作（qpdf）
description: 用 qpdf 开源工具无损的 PDF 结构变换：合并、拆分、选页、旋转、加解密、线性化、修复。当任务需要 PDF 结构操作（qpdf） 且希望用开源、可独立运行的底层工具（pdfcraft 开源替代）时使用。
triggers: [qpdf, PDF 结构操作]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: office-admin
layer: base
backs: pdfcraft 开源替代
version: 1
license: Apache-2.0
---

# qpdf · PDF 结构操作（qpdf）

**它让我们能做什么：** PDF：合并拆分、页序调整、加解密，接 ocrmypdf / pymupdf。

无损的 PDF 结构变换：合并、拆分、选页、旋转、加解密、线性化、修复。

## 定位

- 槽位：pdfcraft 开源替代
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0

## 安装

```sh
sudo apt install qpdf  # macOS: brew install qpdf
```

## 核心用法

```
qpdf --check in.pdf
qpdf --empty --pages a.pdf b.pdf 1-3 -- merged.pdf
qpdf in.pdf --pages . 1-5 -- first5.pdf
qpdf --split-pages=1 in.pdf page-%d.pdf
qpdf in.pdf out.pdf --rotate=+90:2-4
qpdf --decrypt --password=口令 in.pdf plain.pdf          # 仅限用户提供口令
qpdf --linearize in.pdf web.pdf
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- `qpdf --check out.pdf` 无错误；`qpdf --show-npages out.pdf` 核对页数。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
