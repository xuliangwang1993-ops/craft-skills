---
name: 7zip
name_zh: 压缩归档（7-Zip）
description: 用 7zip 开源工具完成「压缩归档」。当任务需要 压缩归档 且希望用开源、可独立运行的底层工具时使用。
triggers: [7zip, 压缩归档]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: ops
layer: base
backs: 压缩归档
wave: 2
stage: 入库
version: 1
license: "LGPL-2.1（部分 BSD-3；unRAR 代码受 unRAR 许可限制，不得用于制作 RAR 压缩器）"
---

# 7zip · 压缩归档（7-Zip）

**它让我们能做什么：** 高压缩比打包/解包 7z/zip/tar 等，交付素材包。

## 定位

- 槽位：压缩归档（一格一个最强工具，本格只放 7zip）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：LGPL-2.1（部分 BSD-3；unRAR 代码受 unRAR 许可限制，不得用于制作 RAR 压缩器）
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
sudo apt install 7zip   # 提供 7zz；旧发行版 p7zip-full 提供 7z
```

## 核心用法

```
7zz a -t7z pack.7z out/ -mx=9
7zz x pack.7z -oextract/
7zz l -slt pack.7z
```

## 输入/输出（串联）

- 输入文件/目录 → 输出 7z/zip；`7zz l -slt` 列表可解析，接 rclone 分发。

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
