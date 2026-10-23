---
name: audiowaveform
name_zh: 波形图生成（audiowaveform）
description: 用 audiowaveform 开源工具BBC 出品，从音频生成波形 PNG 或 JSON 数据，用于剪辑卡点可视化或片内波形动效。当任务需要 波形图生成 且希望用开源、可独立运行的底层工具（soundcraft / effectcraft 补位）时使用。
triggers: [audiowaveform, 波形图生成]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: audio
layer: base
backs: soundcraft / effectcraft 补位
version: 1
license: GPL-3.0
---

# audiowaveform · 波形图生成（audiowaveform）

**它让我们能做什么：** 音频可视化：波形图/波形数据。

BBC 出品，从音频生成波形 PNG 或 JSON 数据，用于剪辑卡点可视化或片内波形动效。

## 定位

- 槽位：soundcraft / effectcraft 补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：GPL-3.0
- 无界面/命令行：是
- GPU：不需要
- 官方：https://github.com/bbc/audiowaveform

## 安装

```sh
sudo add-apt-repository ppa:chris-needham/ppa && sudo apt install audiowaveform
```

## 核心用法

```
audiowaveform -i in.wav -o wave.png -w 1080 -h 200
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
