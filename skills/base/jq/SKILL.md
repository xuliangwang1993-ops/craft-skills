---
name: jq
name_zh: JSON 处理（jq）
description: 用 jq 开源工具完成「JSON 处理」。当任务需要 JSON 处理 且希望用开源、可独立运行的底层工具时使用。
triggers: [jq, JSON 处理]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: dev
layer: base
backs: JSON 处理
wave: 1
stage: 入库
version: 1
license: MIT
---

# jq · JSON 处理（jq）

**它让我们能做什么：** 所有工具 JSON 输出之间的转接头：筛选、改形、拼装，保证输出接输入。

## 定位

- 槽位：JSON 处理（一格一个最强工具，本格只放 jq）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
sudo apt install jq
```

## 核心用法

```
jq '.results[] | {title,url}' res.json
ffprobe -v error -show_format -of json a.mp4 | jq -r .format.duration
jq -s 'add' a.json b.json > merged.json
```

## 输入/输出校验

- 先侦察输入，再处理。
- `jq -e` 在结果为 null/false 时返回非零，用于断言。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
