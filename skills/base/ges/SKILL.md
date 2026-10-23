---
name: ges
name_zh: 时间线编辑服务（GStreamer Editing Services）
description: 用 ges 开源工具GStreamer 的非线性编辑层，ges-launch-1.0 命令行拼时间线、转场、导出。当任务需要 时间线编辑服务 且希望用开源、可独立运行的底层工具（filmcraft 开源替代）时使用。
triggers: [ges, 时间线编辑服务]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: video
layer: base
backs: filmcraft 开源替代
version: 1
license: LGPL-2.1+
---

# ges · 时间线编辑服务（GStreamer Editing Services）

**它让我们能做什么：** 剪辑：GStreamer 生态的命令行时间线。

GStreamer 的非线性编辑层，ges-launch-1.0 命令行拼时间线、转场、导出。

## 定位

- 槽位：filmcraft 开源替代
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：LGPL-2.1+
- 无界面/命令行：是
- GPU：不需要
- 官方：https://gstreamer.freedesktop.org/documentation/gst-editing-services/

## 安装

```sh
sudo apt install ges1.0-tools gstreamer1.0-plugins-good gstreamer1.0-libav
```

## 核心用法

```
ges-launch-1.0 +clip a.mp4 inpoint=0 duration=5 +clip b.mp4 duration=5 -o out.mp4
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
