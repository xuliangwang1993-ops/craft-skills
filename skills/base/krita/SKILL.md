---
name: krita
name_zh: Krita 命令行导出
description: 用 krita 开源工具Krita 支持 --export 把 .kra 等工程无界面导出为图片。当任务需要 Krita 命令行导出 且希望用开源、可独立运行的底层工具（photocraft / designcraft 补位）时使用。
triggers: [krita, Krita 命令行导出]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: image
layer: base
backs: photocraft / designcraft 补位
version: 1
license: GPL-3.0
---

# krita · Krita 命令行导出

**它让我们能做什么：** 画面：手绘工程批量导出。

Krita 支持 --export 把 .kra 等工程无界面导出为图片。

## 定位

- 槽位：photocraft / designcraft 补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：GPL-3.0
- 无界面/命令行：是（--export）
- GPU：不需要
- 官方：https://krita.org

## 安装

```sh
sudo apt install krita
```

## 核心用法

```
krita in.kra --export --export-filename out.png
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
