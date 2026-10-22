---
name: librosa
name_zh: 音乐节拍分析（librosa）
description: 用 librosa 开源工具完成「节拍/音乐分析（卡点）」。当任务需要 节拍/音乐分析（卡点） 且希望用开源、可独立运行的底层工具时使用。
triggers: [librosa, 节拍/音乐分析（卡点）]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: audio
layer: base
backs: 节拍/音乐分析（卡点）
wave: 1
stage: 入库
version: 1
license: ISC
---

# librosa · 音乐节拍分析（librosa）

**它让我们能做什么：** 找出音乐节拍和重拍时间点，给剪辑自动卡点，时间点 JSON 交 MLT 排时间线。

## 定位

- 槽位：节拍/音乐分析（卡点）（一格一个最强工具，本格只放 librosa）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：ISC
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
pip install librosa soundfile
```

## 核心用法

```
python - <<'P'
import librosa, json
y,sr=librosa.load('bgm.wav')
tempo,beats=librosa.beat.beat_track(y=y,sr=sr)
json.dump({'tempo':float(tempo[0] if hasattr(tempo,'__len__') else tempo),'beats':librosa.frames_to_time(beats,sr=sr).tolist()},open('beats.json','w'))
P
```

## 输入/输出校验

- 先侦察输入，再处理。
- beats.json 时间点单调递增且在音频时长内；BPM 与人工听感一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
