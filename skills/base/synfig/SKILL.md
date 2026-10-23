---
name: synfig
name_zh: 2D 矢量动画（Synfig）
description: 用 synfig 开源工具2D 矢量/骨骼动画，synfig 命令行渲染 .sif 工程。当任务需要 2D 矢量动画 且希望用开源、可独立运行的底层工具（effectcraft 动效开源替代）时使用。
triggers: [synfig, 2D 矢量动画]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: motion
layer: base
backs: effectcraft 动效开源替代
version: 1
license: GPL-3.0
---

# synfig · 2D 矢量动画（Synfig）

**它让我们能做什么：** 动效：矢量角色/logo 动画。

2D 矢量/骨骼动画，synfig 命令行渲染 .sif 工程。

## 定位

- 槽位：effectcraft 动效开源替代
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：GPL-3.0
- 无界面/命令行：是
- GPU：不需要
- 官方：https://github.com/synfig/synfig

## 安装

```sh
sudo apt install synfig
```

## 核心用法

```
synfig scene.sifz -t ffmpeg -o out.mp4 -w 1080 -h 1920
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
