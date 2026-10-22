---
name: searxng
name_zh: 元搜索（SearXNG，自托管）
description: 用 searxng 开源工具完成「网页搜索」。当任务需要 网页搜索 且希望用开源、可独立运行的底层工具时使用。
triggers: [searxng, 网页搜索]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: web
layer: base
backs: 网页搜索
wave: 1
stage: 入库
version: 1
license: AGPL-3.0
---

# searxng · 元搜索（SearXNG，自托管）

**它让我们能做什么：** 自托管、无 API 费的聚合搜索，输出 JSON 结果列表，接 Crawl4AI 抓全文。

## 定位

- 槽位：网页搜索（一格一个最强工具，本格只放 searxng）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：AGPL-3.0
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
docker run -d -p 8888:8080 --name searxng searxng/searxng
```

## 核心用法

```
# 需在 settings.yml 的 search.formats 中启用 json
curl -s 'http://localhost:8888/search?q=ffmpeg+loudnorm&format=json' | jq '.results[:5][] | {title,url}'
```

## 输入/输出校验

- 先侦察输入，再处理。
- 返回 JSON 且 `.results | length > 0`；URL 可被 Crawl4AI 抓取。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
