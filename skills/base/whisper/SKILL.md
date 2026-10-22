---
name: whisper
name_zh: 语音识别与字幕（Whisper）
description: 用 whisper 开源工具OpenAI 开源多语种语音识别，直接输出 srt/vtt/txt 字幕。`faster-whisper`（CTranslate2，MIT）速度约 4 倍、显存更省。当任务需要 语音识别与字幕（Whisper） 且希望用开源、可独立运行的底层工具（filmcraft / soundcraft 字幕补位）时使用。
triggers: [whisper, 语音识别与字幕]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: audio
layer: base
backs: filmcraft / soundcraft 字幕补位
version: 1
license: MIT
---

# whisper · 语音识别与字幕（Whisper）

**它让我们能做什么：** 字幕：给任何视频/播客自动出带时间轴的字幕，接 FFmpeg 烧录或接 wordcraft 出文稿。

OpenAI 开源多语种语音识别，直接输出 srt/vtt/txt 字幕。`faster-whisper`（CTranslate2，MIT）速度约 4 倍、显存更省。

## 定位

- 槽位：filmcraft / soundcraft 字幕补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT

## 安装

```sh
pip install -U openai-whisper  # 需系统 ffmpeg；更快：pip install faster-whisper
```

## 核心用法

```
whisper in.mp4 --model large-v3 --language zh --output_format srt --output_dir out/
# faster-whisper（Python）
from faster_whisper import WhisperModel
m = WhisperModel("large-v3", device="cuda", compute_type="float16")  # CPU: device="cpu", compute_type="int8"
segments, info = m.transcribe("in.mp4", language="zh", vad_filter=True)
for s in segments: print(f"[{s.start:.2f}-{s.end:.2f}] {s.text}")
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 抽查 3 段时间轴与音频对齐；字幕最后时间戳 ≤ 媒体时长。中文专有名词准确率不够时改用 funasr。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
