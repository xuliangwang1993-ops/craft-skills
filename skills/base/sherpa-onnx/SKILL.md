---
name: sherpa-onnx
name_zh: 离线语音识别与合成（sherpa-onnx）
description: 用 sherpa-onnx 开源工具新一代 Kaldi 的 ONNX 推理框架，离线 ASR/TTS/VAD，支持中文，CPU 可跑。当任务需要 离线语音识别与合成 且希望用开源、可独立运行的底层工具（soundcraft / filmcraft 字幕与配音补位）时使用。
triggers: [sherpa-onnx, 离线语音识别与合成]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: tts
layer: base
backs: soundcraft / filmcraft 字幕与配音补位
version: 1
license: Apache-2.0（模型另见各自许可）
---

# sherpa-onnx · 离线语音识别与合成（sherpa-onnx）

**它让我们能做什么：** 配音/字幕：可商用的离线中文语音。

新一代 Kaldi 的 ONNX 推理框架，离线 ASR/TTS/VAD，支持中文，CPU 可跑。

## 定位

- 槽位：soundcraft / filmcraft 字幕与配音补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0（模型另见各自许可）
- 无界面/命令行：是
- GPU：不需要
- 官方：https://github.com/k2-fsa/sherpa-onnx

## 安装

```sh
pip install sherpa-onnx
```

## 核心用法

```
sherpa-onnx-offline-tts --vits-model=model.onnx --vits-tokens=tokens.txt --output-filename=out.wav '你好'
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
