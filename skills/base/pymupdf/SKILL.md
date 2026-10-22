---
name: pymupdf
name_zh: PDF 读取/渲染/编辑（PyMuPDF）
description: 用 pymupdf 开源工具高速 PDF 解析库：提文字/坐标、渲染图片、增删页、真正的遮盖（redaction）、检测假遮盖。当任务需要 PDF 读取/渲染/编辑（PyMuPDF） 且希望用开源、可独立运行的底层工具（pdfcraft 开源替代）时使用。
triggers: [pymupdf, PDF 读取/渲染/编辑]
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
license: ⚠️ AGPL-3.0（或付费商业许可）
---

# pymupdf · PDF 读取/渲染/编辑（PyMuPDF）

**它让我们能做什么：** PDF：文本提取、页面渲染校验、真实遮盖与假遮盖审计。

高速 PDF 解析库：提文字/坐标、渲染图片、增删页、真正的遮盖（redaction）、检测假遮盖。

## 定位

- 槽位：pdfcraft 开源替代
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：⚠️ AGPL-3.0（或付费商业许可）

## 安装

```sh
pip install pymupdf
```

## 核心用法

```
import pymupdf                       # 旧写法 import fitz 亦可
doc = pymupdf.open("in.pdf")
print(doc.page_count, doc.metadata)
text = doc[0].get_text()
doc[0].get_pixmap(dpi=150).save("p1.png")
# 真实遮盖：先标注再 apply，底层文字才会被删除
page = doc[0]
for r in page.search_for("身份证号"): page.add_redact_annot(r, fill=(0,0,0))
page.apply_redactions()
doc.save("redacted.pdf", garbage=4, deflate=True)
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 遮盖后重新打开 `get_text()` 确认敏感字不在；渲染抽页目视。**AGPL：作为网络服务对外提供须开源全部代码，商用闭源请购商业许可或改用 pypdf（BSD）。**

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
