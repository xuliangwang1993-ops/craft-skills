---
name: deepfilternet
name_zh: 语音降噪（DeepFilterNet）
description: 用 deepfilternet 开源工具完成「语音降噪」。当任务需要 语音降噪 且希望用开源、可独立运行的底层工具时使用。
triggers: [deepfilternet, 语音降噪]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: audio
layer: base
backs: 语音降噪
wave: 2
stage: 入库
version: 1
license: "MIT OR Apache-2.0"
---

# deepfilternet · 语音降噪（DeepFilterNet）

**它让我们能做什么：** 实时级语音降噪，嘈杂录音/会议/口播一键变干净，接 Whisper 字幕前做预处理。

## 定位

- 槽位：语音降噪（一格一个最强工具，本格只放 deepfilternet）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT OR Apache-2.0
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
pip install deepfilternet
```

## 核心用法

```
deepFilter noisy.wav -o out/
# 先转 48k 单声道：ffmpeg -i in.mp4 -ac 1 -ar 48000 noisy.wav
```

## 输入/输出（串联）

- 输入 wav（48 kHz 单声道最佳，ffmpeg 预转）→ 输出降噪 wav，直接喂 whisper / funasr / sox。

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
