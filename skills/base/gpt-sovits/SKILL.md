---
name: gpt-sovits
name_zh: 中文声音克隆（GPT-SoVITS）
description: 用 gpt-sovits 开源工具少样本声音克隆 TTS，中文效果好，带 API 服务。当任务需要 中文声音克隆 且希望用开源、可独立运行的底层工具（soundcraft 配音补位）时使用。
triggers: [gpt-sovits, 中文声音克隆]
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
license: MIT（使用他人声音须授权）
---

# gpt-sovits · 中文声音克隆（GPT-SoVITS）

**它让我们能做什么：** 配音：授权音色克隆。

少样本声音克隆 TTS，中文效果好，带 API 服务。

## 定位

- 槽位：soundcraft 配音补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT（使用他人声音须授权）
- 无界面/命令行：是（api_v2.py）
- GPU：需要
- 官方：https://github.com/RVC-Boss/GPT-SoVITS

## 安装

```sh
git clone https://github.com/RVC-Boss/GPT-SoVITS && cd GPT-SoVITS && bash install.sh
```

## 核心用法

```
python api_v2.py -a 127.0.0.1 -p 9880   # 再 GET /tts?text=...&text_lang=zh&ref_audio_path=ref.wav&prompt_lang=zh
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
