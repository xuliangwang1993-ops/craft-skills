---
name: piper
name_zh: 轻量离线配音（Piper）
description: 用 piper 开源工具CPU 即可实时运行的神经 TTS，命令行读文本出 wav。当任务需要 轻量离线配音 且希望用开源、可独立运行的底层工具（soundcraft / filmcraft 配音补位）时使用。
triggers: [piper, 轻量离线配音]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: tts
layer: base
backs: soundcraft / filmcraft 配音补位
version: 1
license: GPL-3.0（新版 piper1-gpl；旧版 MIT 已归档；各音色模型许可另见模型卡）
---

# piper · 轻量离线配音（Piper）

**它让我们能做什么：** 配音：低成本英文/多语配音。

CPU 即可实时运行的神经 TTS，命令行读文本出 wav。

## 定位

- 槽位：soundcraft / filmcraft 配音补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：GPL-3.0（新版 piper1-gpl；旧版 MIT 已归档；各音色模型许可另见模型卡）
- 无界面/命令行：是
- GPU：不需要
- 官方：https://github.com/OHF-Voice/piper1-gpl

## 安装

```sh
pip install piper-tts
```

## 核心用法

```
python -m piper.download_voices en_US-lessac-medium && echo 'Hello' | python -m piper -m en_US-lessac-medium -f out.wav
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
