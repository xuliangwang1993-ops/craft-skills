---
name: rubberband
name_zh: 变速不变调（Rubber Band）
description: 用 rubberband 开源工具高质量时间伸缩与变调，用于把音乐/配音卡到精确时长。当任务需要 变速不变调 且希望用开源、可独立运行的底层工具（soundcraft 开源补位）时使用。
triggers: [rubberband, 变速不变调]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: audio
layer: base
backs: soundcraft 开源补位
version: 1
license: GPL-2.0（另有商业许可）
---

# rubberband · 变速不变调（Rubber Band）

**它让我们能做什么：** 音频：配音/音乐对齐时长。

高质量时间伸缩与变调，用于把音乐/配音卡到精确时长。

## 定位

- 槽位：soundcraft 开源补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：GPL-2.0（另有商业许可）
- 无界面/命令行：是
- GPU：不需要
- 官方：https://github.com/breakfastquay/rubberband

## 安装

```sh
sudo apt install rubberband-cli
```

## 核心用法

```
rubberband -D 30 in.wav out.wav     # 拉伸到 30 秒；-p 2 升 2 个半音
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
