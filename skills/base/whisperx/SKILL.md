---
name: whisperx
name_zh: 逐字时间对齐（WhisperX）
description: 用 whisperx 开源工具完成「逐字时间对齐」。当任务需要 逐字时间对齐 且希望用开源、可独立运行的底层工具时使用。
triggers: [whisperx, 逐字时间对齐]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: audio
layer: base
backs: 逐字时间对齐
wave: 2
stage: 入库
version: 1
license: "BSD-2-Clause（说话人分离用 pyannote，需 HF token 并同意模型条款）"
---

# whisperx · 逐字时间对齐（WhisperX）

**它让我们能做什么：** 词级时间戳 + 说话人分离，做卡字幕、逐字高亮、多人访谈分角色。

## 定位

- 槽位：逐字时间对齐（一格一个最强工具，本格只放 whisperx）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：BSD-2-Clause（说话人分离用 pyannote，需 HF token 并同意模型条款）
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
pip install whisperx
```

## 核心用法

```
whisperx in.wav --model large-v3 --language zh --output_format srt --output_dir out/
# 说话人分离：加 --diarize --hf_token $HF_TOKEN
```

## 输入/输出（串联）

- 输入 wav/mp4 → 输出 srt/vtt/json（词级），接 ffmpeg 烧字幕 / argos-translate 翻译。

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
