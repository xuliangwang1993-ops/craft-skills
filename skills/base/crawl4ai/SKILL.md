---
name: crawl4ai
name_zh: 网页抓取与正文提取（Crawl4AI）
description: 用 crawl4ai 开源工具完成「网页抓取/正文提取」。当任务需要 网页抓取/正文提取 且希望用开源、可独立运行的底层工具时使用。
triggers: [crawl4ai, 网页抓取/正文提取]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: web
layer: base
backs: 网页抓取/正文提取
wave: 1
stage: 入库
version: 1
license: Apache-2.0
---

# crawl4ai · 网页抓取与正文提取（Crawl4AI）

**它让我们能做什么：** 把任意网页变成干净的 Markdown/JSON，直接喂给大模型或 Pandoc。

## 定位

- 槽位：网页抓取/正文提取（一格一个最强工具，本格只放 crawl4ai）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
pip install -U crawl4ai && crawl4ai-setup
```

## 核心用法

```
crwl https://example.com -o markdown > page.md
python - <<'P'
import asyncio
from crawl4ai import AsyncWebCrawler
async def m():
    async with AsyncWebCrawler() as c:
        r=await c.arun(url='https://example.com'); print(r.markdown[:500])
asyncio.run(m())
P
```

## 输入/输出校验

- 先侦察输入，再处理。
- 输出 Markdown 非空、含页面标题；抽样人工比对正文无导航垃圾。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
