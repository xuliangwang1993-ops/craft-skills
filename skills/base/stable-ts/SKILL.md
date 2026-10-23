---
name: stable-ts
name_zh: 稳定字幕时间戳（stable-ts）
description: 用 stable-ts 开源工具让 Whisper 时间戳更稳，并可把已有文案对齐到音频。仓库已归档，仍可用。当任务需要 稳定字幕时间戳 且希望用开源、可独立运行的底层工具（filmcraft 字幕补位）时使用。
triggers: [stable-ts, 稳定字幕时间戳]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: asr
layer: base
backs: filmcraft 字幕补位
version: 1
license: MIT（已归档）
---

# stable-ts · 稳定字幕时间戳（stable-ts）

**它让我们能做什么：** 字幕：已有文案对齐到配音。

让 Whisper 时间戳更稳，并可把已有文案对齐到音频。仓库已归档，仍可用。

## 定位

- 槽位：filmcraft 字幕补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT（已归档）
- 无界面/命令行：是
- GPU：可选
- 官方：https://github.com/jianfch/stable-ts

## 安装

```sh
pip install stable-ts
```

## 核心用法

```
stable-ts in.wav --model medium --language zh -o out.srt
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
