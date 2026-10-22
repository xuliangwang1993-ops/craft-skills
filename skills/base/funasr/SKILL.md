---
name: funasr
name_zh: 中文语音识别（FunASR / Paraformer）
description: 用 funasr 开源工具阿里达摩院开源语音识别工具包，Paraformer 中文识别准确率高，带 VAD 断句、标点恢复、时间戳。当任务需要 中文语音识别（FunASR / Paraformer） 且希望用开源、可独立运行的底层工具（filmcraft / soundcraft 中文字幕补位）时使用。
triggers: [funasr, 中文语音识别]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: audio
layer: base
backs: filmcraft / soundcraft 中文字幕补位
version: 1
license: MIT（模型权重另见各自模型许可）
---

# funasr · 中文语音识别（FunASR / Paraformer）

**它让我们能做什么：** 字幕（中文优先）：中文口播、会议、播客出字幕比 Whisper 更准。

阿里达摩院开源语音识别工具包，Paraformer 中文识别准确率高，带 VAD 断句、标点恢复、时间戳。

## 定位

- 槽位：filmcraft / soundcraft 中文字幕补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT（模型权重另见各自模型许可）

## 安装

```sh
pip install -U funasr modelscope torch torchaudio
```

## 核心用法

```
from funasr import AutoModel
model = AutoModel(model="paraformer-zh", vad_model="fsmn-vad", punc_model="ct-punc")
res = model.generate(input="in.wav", batch_size_s=300)
print(res[0]["text"])          # 带标点全文；res[0] 中含 timestamp 字段可转 srt
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 对照原音抽查专有名词；输入先用 ffmpeg 转 16kHz 单声道 wav：`ffmpeg -i in.mp4 -ar 16000 -ac 1 in.wav`。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
