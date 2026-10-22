---
name: playwright
name_zh: 浏览器自动化（Playwright）
description: 用 playwright 开源工具完成「浏览器自动化」。当任务需要 浏览器自动化 且希望用开源、可独立运行的底层工具时使用。
triggers: [playwright, 浏览器自动化]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: web
layer: base
backs: 浏览器自动化
wave: 1
stage: 入库
version: 1
license: Apache-2.0
---

# playwright · 浏览器自动化（Playwright）

**它让我们能做什么：** 让 AI 像人一样打开网页、点击、填表、截图、导出 PDF，网页成为流水线的一个输入口。

## 定位

- 槽位：浏览器自动化（一格一个最强工具，本格只放 playwright）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
pip install playwright && playwright install chromium
```

## 核心用法

```
playwright screenshot --full-page https://example.com shot.png
playwright pdf https://example.com page.pdf
python - <<'P'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('https://example.com')
    print(pg.title()); pg.screenshot(path='a.png'); b.close()
P
```

## 输入/输出校验

- 先侦察输入，再处理。
- 退出码为 0；截图/PDF 文件存在且非空；`pdfinfo page.pdf` 能读出页数。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
