---
name: yt-dlp
name_zh: 媒体下载（yt-dlp）
description: 用 yt-dlp 开源工具完成「在线音视频下载」。当任务需要 在线音视频下载 且希望用开源、可独立运行的底层工具时使用。
triggers: [yt-dlp, 在线音视频下载]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: video
layer: base
backs: 在线音视频下载
wave: 1
stage: 入库
version: 1
license: Unlicense
---

# yt-dlp · 媒体下载（yt-dlp）

**它让我们能做什么：** 从上千个站点下载音视频与字幕，直接成为 FFmpeg/Whisper/MLT 的输入。

## 定位

- 槽位：在线音视频下载（一格一个最强工具，本格只放 yt-dlp）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Unlicense
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
pip install -U yt-dlp  # 依赖 ffmpeg
```

## 核心用法

```
yt-dlp -F URL                         # 列格式
yt-dlp -f 'bv*+ba/b' --merge-output-format mp4 -o '%(title)s.%(ext)s' URL
yt-dlp -x --audio-format wav URL
yt-dlp --write-subs --sub-langs zh.* --skip-download URL
```

## 输入/输出校验

- 先侦察输入，再处理。
- `ffprobe` 校验文件完整；只下载有权使用的内容，遵守站点条款与版权。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
