---
name: pdfcraft
name_zh: PDF 文档处理
description: 用 PdfCraft 引擎处理 PDF：提取文本、渲染页面、旋转/删除/移动/插入页、合并拆分、批量 OCR 与优化，并审计虚假遮盖（faux redaction）。当任务涉及 .pdf 的读取、编辑、拆分合并、OCR、压缩或安全审计时使用。
triggers: [PDF, 拆分PDF, 合并PDF, OCR, 提取文字, 遮盖审计, 扫描件]
inputs:
  - name: file
    description: 目标 PDF 路径
    required: true
tools: []
mcp: [pdfcraft]
permissions: [read_file, write_file, network]
category: office-admin
version: 1
license: Proprietary
source: https://getartcraft.com/apps/pdfcraft
---

# PdfCraft 文档班组

PdfCraft 提供 **163 个 MCP 工具**，覆盖 PDF 全生命周期操作。

## 核心工具族

| 工具族 | 代表工具 | 用途 |
|--------|----------|------|
| 文档级 | `doc_open` / `doc_info` / `doc_save` / `doc_combine` / `doc_batch` | 打开、读信息、保存、合并、批处理 |
| 页面级 | `page_render` / `page_rotate` / `page_delete` / `page_move` / `page_extract` / `page_insert_blank` / `page_insert_file` | 页面编排 |
| 内容级 | `text_extract` / `text_find` / `object_list` / `object_move` | 文字与对象抽取 |
| 增强 | `page_enhance_camera` | 手机拍歪/反光的扫描件扶正增强 |

CLI 侧还提供 `audit`（**查找虚假遮盖**）、`check`（文档健康检查）、`batch`（批量 convert/ocr/optimize）。

## 标准作业流程

1. `doc_open` + `doc_info` 先侦察（页数、大小、加密状态）
2. 按需调用页面级 / 内容级工具
3. `page_render` 抽页渲染做目视校验
4. `doc_save` 另存，不覆盖原件

## 硬规则

- **不得覆盖原始 PDF**，一律另存新文件。
- 处理加密文档前先向用户索取口令，不得暴力破解。
- 涉及**删除页、遮盖内容、拆分**等不可逆操作，先说明影响范围并取得确认。
- 扫描件 OCR 前先 `page_enhance_camera` 提升识别率。
