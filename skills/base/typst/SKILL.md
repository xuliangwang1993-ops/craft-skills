---
name: typst
name_zh: 现代排版（Typst）
description: 用 typst 开源工具标记语言排版引擎，命令行出 PDF/PNG/SVG，适合字卡、海报、价目单。当任务需要 现代排版 且希望用开源、可独立运行的底层工具（designcraft / wordcraft 补位）时使用。
triggers: [typst, 现代排版]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: layout
layer: base
backs: designcraft / wordcraft 补位
version: 1
license: Apache-2.0
---

# typst · 现代排版（Typst）

**它让我们能做什么：** 版式：字卡、海报、菜单排版。

标记语言排版引擎，命令行出 PDF/PNG/SVG，适合字卡、海报、价目单。

## 定位

- 槽位：designcraft / wordcraft 补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0
- 无界面/命令行：是
- GPU：不需要
- 官方：https://github.com/typst/typst

## 安装

```sh
cargo install --locked typst-cli   # 或下载 release 二进制
```

## 核心用法

```
typst compile card.typ card.png --ppi 144
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
