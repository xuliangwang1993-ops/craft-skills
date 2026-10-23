---
name: f5-tts
name_zh: 零样本声音克隆（F5-TTS）
description: 用 f5-tts 开源工具流匹配 TTS，零样本克隆。⚠️ 官方预训练权重 CC-BY-NC，不可商用。当任务需要 零样本声音克隆 且希望用开源、可独立运行的底层工具（soundcraft 配音补位）时使用。
triggers: [f5-tts, 零样本声音克隆]
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
license: ⚠️ 代码 MIT；官方权重 CC-BY-NC-4.0（不可商用）
---

# f5-tts · 零样本声音克隆（F5-TTS）

**它让我们能做什么：** 配音：仅限内部试样（权重不可商用）。

流匹配 TTS，零样本克隆。⚠️ 官方预训练权重 CC-BY-NC，不可商用。

## 定位

- 槽位：soundcraft 配音补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：⚠️ 代码 MIT；官方权重 CC-BY-NC-4.0（不可商用）
- 无界面/命令行：是
- GPU：需要
- 官方：https://github.com/SWivid/F5-TTS

## 安装

```sh
pip install f5-tts
```

## 核心用法

```
f5-tts_infer-cli --ref_audio ref.wav --ref_text '参考文本' --gen_text '要合成的文本'
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
