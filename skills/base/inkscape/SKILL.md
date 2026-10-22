---
name: inkscape
name_zh: 矢量图命令行（Inkscape）
description: 用 inkscape 开源工具专业矢量编辑器，1.x 命令行可导出 PNG/PDF/EPS、文字转路径、执行 actions 批处理。当任务需要 矢量图命令行（Inkscape） 且希望用开源、可独立运行的底层工具（vectorcraft 开源替代）时使用。
triggers: [inkscape, 矢量图命令行]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: design
layer: base
backs: vectorcraft 开源替代
version: 1
license: GPL-2.0+
---

# inkscape · 矢量图命令行（Inkscape）

**它让我们能做什么：** 矢量：logo/图标批量导出各尺寸、SVG 转印刷 PDF。

专业矢量编辑器，1.x 命令行可导出 PNG/PDF/EPS、文字转路径、执行 actions 批处理。

## 定位

- 槽位：vectorcraft 开源替代
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：GPL-2.0+

## 安装

```sh
sudo apt install inkscape  # macOS: brew install --cask inkscape
```

## 核心用法

```
inkscape logo.svg --export-type=png --export-width=1024 --export-filename=logo.png
inkscape logo.svg --export-type=pdf --export-text-to-path --export-filename=logo.pdf
inkscape *.svg --export-type=png --export-dpi=300
inkscape in.svg --actions="select-all;object-to-path;export-filename:out.svg;export-do" 
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- `identify logo.png` 核对像素尺寸；`pdffonts logo.pdf` 为空说明文字已转路径。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
