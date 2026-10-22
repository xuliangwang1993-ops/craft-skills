---
name: tectonic
name_zh: LaTeX 排版（Tectonic）
description: 用 tectonic 开源工具完成「数学公式/学术排版」。当任务需要 数学公式/学术排版 且希望用开源、可独立运行的底层工具时使用。
triggers: [tectonic, 数学公式/学术排版]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: doc
layer: base
backs: 数学公式/学术排版
wave: 1
stage: 入库
version: 1
license: MIT
---

# tectonic · LaTeX 排版（Tectonic）

**它让我们能做什么：** 单文件命令编译 LaTeX，按需自动下载宏包，公式和论文一次出版级 PDF。

## 定位

- 槽位：数学公式/学术排版（一格一个最强工具，本格只放 tectonic）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
cargo install tectonic  # 或 conda install -c conda-forge tectonic / 官方安装脚本
```

## 核心用法

```
tectonic paper.tex
pandoc in.md -o out.pdf --pdf-engine=tectonic
```

## 输入/输出校验

- 先侦察输入，再处理。
- 生成 PDF；`pdfinfo` 页数合理；日志无 undefined reference。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
