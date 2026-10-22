---
name: sox
name_zh: 音频处理（SoX）
description: 用 sox 开源工具命令行音频瑞士军刀：格式/采样率转换、裁剪、拼接、淡入淡出、增益、降噪、统计。当任务需要 音频处理（SoX） 且希望用开源、可独立运行的底层工具（soundcraft 开源替代）时使用。
triggers: [sox, 音频处理]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: audio
layer: base
backs: soundcraft 开源替代
version: 1
license: GPL-2.0（libsox 为 LGPL）
---

# sox · 音频处理（SoX）

**它让我们能做什么：** 音频：批量转换、剪裁、混音、降噪和响度检查，接 soundcraft 流程。

命令行音频瑞士军刀：格式/采样率转换、裁剪、拼接、淡入淡出、增益、降噪、统计。

## 定位

- 槽位：soundcraft 开源替代
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：GPL-2.0（libsox 为 LGPL）

## 安装

```sh
sudo apt install sox libsox-fmt-all  # macOS: brew install sox
```

## 核心用法

```
soxi in.wav                                       # 侦察
sox in.wav -r 48000 -b 24 out.wav                 # 改采样率/位深
sox in.wav out.wav trim 0 30 fade t 0.5 30 1      # 截 30s，0.5s 淡入，1s 淡出
sox -m voice.wav bgm.wav mix.wav                  # 混音
sox noise.wav -n noiseprof n.prof && sox in.wav clean.wav noisered n.prof 0.21
sox in.wav -n stats                               # 峰值/RMS
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- `soxi` 核对采样率、声道、时长；`sox out.wav -n stats` 确认峰值未削波（Pk lev dB < 0）。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
