---
name: manim
name_zh: 代码动画（Manim）
description: 用 manim 开源工具用 Python 代码生成精确的图形、文字、数据动画。当任务需要 代码动画 且希望用开源、可独立运行的底层工具（effectcraft 动效补位）时使用。
triggers: [manim, 代码动画]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: motion
layer: base
backs: effectcraft 动效补位
version: 1
license: MIT
---

# manim · 代码动画（Manim）

**它让我们能做什么：** 动效：信息图、数字滚动、文字动画。

用 Python 代码生成精确的图形、文字、数据动画。

## 定位

- 槽位：effectcraft 动效补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT
- 无界面/命令行：是
- GPU：不需要
- 官方：https://github.com/ManimCommunity/manim

## 安装

```sh
pip install manim  # 需先 apt install libcairo2-dev libpango1.0-dev ffmpeg
```

## 核心用法

```
manim -qh scene.py MyScene    # 输出 media/videos/scene/1080p60/MyScene.mp4
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
