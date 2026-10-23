---
name: coqui-tts
name_zh: 多语种 TTS（Coqui TTS / XTTS）
description: 用 coqui-tts 开源工具Coqui TTS 工具包，含 XTTS-v2 多语种克隆。⚠️ XTTS 权重为 CPML，不可商用。当任务需要 多语种 TTS 且希望用开源、可独立运行的底层工具（soundcraft 配音补位）时使用。
triggers: [coqui-tts, 多语种 TTS]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: tts
layer: base
backs: soundcraft 配音补位
version: 1
license: ⚠️ 代码 MPL-2.0；XTTS-v2 权重 CPML（不可商用）
---

# coqui-tts · 多语种 TTS（Coqui TTS / XTTS）

**它让我们能做什么：** 配音：仅限内部试样（XTTS 权重不可商用）。

Coqui TTS 工具包，含 XTTS-v2 多语种克隆。⚠️ XTTS 权重为 CPML，不可商用。

## 定位

- 槽位：soundcraft 配音补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：⚠️ 代码 MPL-2.0；XTTS-v2 权重 CPML（不可商用）
- 无界面/命令行：是
- GPU：需要（XTTS）
- 官方：https://github.com/coqui-ai/TTS

## 安装

```sh
pip install coqui-tts   # 原 coqui-ai/TTS 已停更，社区维护版 idiap/coqui-ai-TTS
```

## 核心用法

```
tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 --text '你好' --language_idx zh-cn --speaker_wav ref.wav --out_path out.wav
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
