---
name: himalaya
name_zh: 命令行邮件（Himalaya）
description: 用 himalaya 开源工具完成「邮件收发」。当任务需要 邮件收发 且希望用开源、可独立运行的底层工具时使用。
triggers: [himalaya, 邮件收发]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: comm
layer: base
backs: 邮件收发
wave: 1
stage: 入库
version: 1
license: MIT
---

# himalaya · 命令行邮件（Himalaya）

**它让我们能做什么：** 命令行读写邮件，附件进流水线、成品自动回发，JSON 输出可接 jq。

## 定位

- 槽位：邮件收发（一格一个最强工具，本格只放 himalaya）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
cargo install himalaya  # 或下载 GitHub Releases 二进制
```

## 核心用法

```
himalaya envelope list -o json | jq '.[0]'
himalaya message read 42
himalaya attachment download 42
```

## 输入/输出校验

- 先侦察输入，再处理。
- 发送前必须人工确认收件人与正文；读取类操作先行。命令随版本变化，以 `himalaya --help` 为准。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
