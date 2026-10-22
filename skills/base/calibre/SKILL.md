---
name: calibre
name_zh: 电子书转换（Calibre）
description: 用 calibre 开源工具完成「电子书」。当任务需要 电子书 且希望用开源、可独立运行的底层工具时使用。
triggers: [calibre, 电子书]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: document
layer: base
backs: 电子书
wave: 2
stage: 入库
version: 1
license: "GPL-3.0"
---

# calibre · 电子书转换（Calibre）

**它让我们能做什么：** epub/mobi/azw3/pdf/docx 互转，改元数据。

## 定位

- 槽位：电子书（一格一个最强工具，本格只放 calibre）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：GPL-3.0
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
sudo apt install calibre
```

## 核心用法

```
ebook-convert in.epub out.pdf
ebook-convert in.docx out.epub --title "书名"
ebook-meta out.epub --authors "作者"
```

## 输入/输出（串联）

- 输入 epub/docx/html/md → 输出 epub/azw3/pdf，接 qpdf / pandoc。

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
