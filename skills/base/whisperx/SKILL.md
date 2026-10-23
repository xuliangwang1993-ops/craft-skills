---
name: whisperx
name_zh: 逐字时间戳字幕（WhisperX）
description: 用 whisperx 开源工具Whisper + 强制对齐，输出逐字时间戳与说话人区分，适合卡点字幕。当任务需要 逐字时间戳字幕 且希望用开源、可独立运行的底层工具（filmcraft / soundcraft 字幕补位）时使用。
triggers: [whisperx, 逐字时间戳字幕]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: asr
layer: base
backs: filmcraft / soundcraft 字幕补位
version: 1
license: BSD-2-Clause
---

# whisperx · 逐字时间戳字幕（WhisperX）

**它让我们能做什么：** 字幕：逐字精确时间轴。

Whisper + 强制对齐，输出逐字时间戳与说话人区分，适合卡点字幕。

## 定位

- 槽位：filmcraft / soundcraft 字幕补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：BSD-2-Clause
- 无界面/命令行：是
- GPU：建议（CPU 可跑但慢）
- 官方：https://github.com/m-bain/whisperX

## 安装

```sh
pip install whisperx
```

## 核心用法

```
whisperx in.wav --model large-v3 --language zh --output_format srt --compute_type int8
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
