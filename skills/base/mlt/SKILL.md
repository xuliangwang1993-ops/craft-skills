---
name: mlt
name_zh: 多轨时间线剪辑（melt）
description: 用 mlt 开源工具Kdenlive/Shotcut 背后的多轨时间线引擎，`melt` 命令行可直接拼接、转场、叠轨、渲染 MLT XML 工程。当任务需要 多轨时间线剪辑（melt） 且希望用开源、可独立运行的底层工具（filmcraft 开源替代）时使用。
triggers: [mlt, 多轨时间线剪辑]
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
license: LGPL-2.1（部分模块 GPL）
---

# mlt · 多轨时间线剪辑（melt）

**它让我们能做什么：** 和 FFmpeg 组成视频剪辑主干：多轨时间线、转场、关键帧、叠字，覆盖并超过剪映约八成剪辑功能。

Kdenlive/Shotcut 背后的多轨时间线引擎，`melt` 命令行可直接拼接、转场、叠轨、渲染 MLT XML 工程。

## 定位

- 槽位：filmcraft 开源替代
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：LGPL-2.1（部分模块 GPL）

## 安装

```sh
sudo apt install melt  # macOS: brew install mlt
```

## 核心用法

```
melt a.mp4 in=0 out=249 b.mp4 -consumer avformat:out.mp4 vcodec=libx264 acodec=aac   # 顺序拼接
melt a.mp4 out=149 b.mp4 -mix 25 -mixer luma -consumer avformat:xfade.mp4               # 25 帧溶解转场
melt project.mlt -consumer avformat:final.mp4 vcodec=libx264 crf=20                     # 渲染 Kdenlive/Shotcut 工程
melt a.mp4 -track b.mp4 -transition composite a_track=0 b_track=1 -consumer avformat:pip.mp4
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 渲染后用 `ffprobe` 核对总时长 ≈ 各片段之和减去转场重叠；抽帧检查转场位置。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
