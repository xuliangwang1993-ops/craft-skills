---
name: exiftool
name_zh: 文件元数据（ExifTool）
description: 用 exiftool 开源工具完成「文件元数据」。当任务需要 文件元数据 且希望用开源、可独立运行的底层工具时使用。
triggers: [exiftool, 文件元数据]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: media
layer: base
backs: 文件元数据
wave: 2
stage: 入库
version: 1
license: "Artistic License / GPL-1.0+（Perl 同款双许可）"
---

# exiftool · 文件元数据（ExifTool）

**它让我们能做什么：** 读写照片/视频/PDF 元数据，查拍摄时间、清 GPS 隐私、批量改版权。

## 定位

- 槽位：文件元数据（一格一个最强工具，本格只放 exiftool）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Artistic License / GPL-1.0+（Perl 同款双许可）
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
sudo apt install libimage-exiftool-perl
```

## 核心用法

```
exiftool -json photo.jpg > meta.json
exiftool -gps:all= -o clean/ photos/
exiftool '-FileName<CreateDate' -d %Y%m%d_%H%M%S%%-c.%%e dir/
```

## 输入/输出（串联）

- 输入任意媒体文件 → 输出 JSON 元数据（接 jq/duckdb）或改写后新文件。

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
