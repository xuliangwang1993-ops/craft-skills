---
name: ffmpeg
name_zh: 音视频转码与处理（共享底层）
description: 用 ffmpeg 开源工具音视频解码、转码、剪切、拼接、滤镜、抽帧、混流的事实标准。当任务需要 音视频转码与处理（共享底层） 且希望用开源、可独立运行的底层工具（共享底层 · 支撑 filmcraft / soundcraft / effectcraft）时使用。
triggers: [ffmpeg, 音视频转码与处理]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: video
layer: base
backs: 共享底层 · 支撑 filmcraft / soundcraft / effectcraft
version: 1
license: LGPL-2.1+（启用 --enable-gpl 编译时为 GPL）
---

# ffmpeg · 音视频转码与处理（共享底层）

**它让我们能做什么：** 共享底层：和 MLT 一起构成视频剪辑主干，覆盖并超过剪映约八成功能；所有音视频工具的输入输出都经它转换。

音视频解码、转码、剪切、拼接、滤镜、抽帧、混流的事实标准。

## 定位

- 槽位：共享底层 · 支撑 filmcraft / soundcraft / effectcraft
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：LGPL-2.1+（启用 --enable-gpl 编译时为 GPL）

## 安装

```sh
sudo apt install ffmpeg  # macOS: brew install ffmpeg
```

## 核心用法

```
ffprobe -v error -show_format -show_streams -of json in.mp4      # 侦察
ffmpeg -ss 00:00:10 -i in.mp4 -t 30 -c copy cut.mp4                # 无重编码剪切（按关键帧）
ffmpeg -i in.mp4 -c:v libx264 -crf 20 -preset medium -c:a aac -b:a 192k out.mp4
ffmpeg -f concat -safe 0 -i list.txt -c copy joined.mp4            # list.txt 每行: file 'a.mp4'
ffmpeg -i in.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" vertical.mp4
ffmpeg -i in.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:v copy norm.mp4
ffmpeg -i in.mp4 -vf subtitles=subs.srt -c:a copy burned.mp4
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- `ffprobe` 核对输出时长、分辨率、编码与音轨数；`ffmpeg -v error -i out.mp4 -f null -` 无报错即可解码完整。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
