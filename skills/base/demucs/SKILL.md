---
name: demucs
name_zh: 人声/伴奏分离（Demucs）
description: 用 demucs 开源工具Meta 开源音源分离模型（Hybrid Transformer），把歌曲拆成人声、鼓、贝斯、其他。当任务需要 人声/伴奏分离（Demucs） 且希望用开源、可独立运行的底层工具（soundcraft 开源补位）时使用。
triggers: [demucs, 人声/伴奏分离]
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
license: MIT
---

# demucs · 人声/伴奏分离（Demucs）

**它让我们能做什么：** 人声伴奏分离：提伴奏、去 BGM 留人声、做卡拉 OK 与二创。

Meta 开源音源分离模型（Hybrid Transformer），把歌曲拆成人声、鼓、贝斯、其他。

## 定位

- 槽位：soundcraft 开源补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT

## 安装

```sh
pip install -U demucs
```

## 核心用法

```
demucs --two-stems=vocals song.mp3 -o separated/        # 输出 separated/htdemucs/song/vocals.wav + no_vocals.wav
demucs -n htdemucs_ft song.mp3 -o separated/              # 四轨、更高质量（更慢）
demucs --mp3 --two-stems=vocals song.mp3                  # 直接出 mp3
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 核对输出文件时长与原曲一致；试听 vocals 是否有明显伴奏残留。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
