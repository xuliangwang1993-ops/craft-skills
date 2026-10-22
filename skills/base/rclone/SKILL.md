---
name: rclone
name_zh: 文件同步/云存储（rclone）
description: 用 rclone 开源工具完成「文件同步/云存储」。当任务需要 文件同步/云存储 且希望用开源、可独立运行的底层工具时使用。
triggers: [rclone, 文件同步/云存储]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: ops
layer: base
backs: 文件同步/云存储
wave: 2
stage: 入库
version: 1
license: "MIT"
---

# rclone · 文件同步/云存储（rclone）

**它让我们能做什么：** 一条命令对接 70+ 云盘/对象存储，同步、备份、分发成品。

## 定位

- 槽位：文件同步/云存储（一格一个最强工具，本格只放 rclone）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
sudo apt install rclone
```

## 核心用法

```
rclone config
rclone copy out/ remote:bucket/out --progress
rclone sync src/ remote:backup --dry-run
```

## 输入/输出（串联）

- 输入本地目录/远端路径 → 输出远端文件，`rclone lsjson` 出 JSON 接 jq。sync 会删目标多余文件，先 --dry-run。

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
