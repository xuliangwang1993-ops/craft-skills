---
name: libass
name_zh: ASS 特效字幕渲染（libass）
description: 用 libass 开源工具ASS/SSA 字幕渲染库，通过 ffmpeg subtitles/ass 滤镜烧录描边、卡拉 OK、定位字幕。当任务需要 ASS 特效字幕渲染 且希望用开源、可独立运行的底层工具（filmcraft 字幕烧录补位）时使用。
triggers: [libass, ASS 特效字幕渲染]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: subtitle
layer: base
backs: filmcraft 字幕烧录补位
version: 1
license: ISC
---

# libass · ASS 特效字幕渲染（libass）

**它让我们能做什么：** 字幕：中英双语样式字幕烧录。

ASS/SSA 字幕渲染库，通过 ffmpeg subtitles/ass 滤镜烧录描边、卡拉 OK、定位字幕。

## 定位

- 槽位：filmcraft 字幕烧录补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：ISC
- 无界面/命令行：是（经 ffmpeg）
- GPU：不需要
- 官方：https://github.com/libass/libass

## 安装

```sh
sudo apt install libass9 ffmpeg
```

## 核心用法

```
ffmpeg -i in.mp4 -vf "ass=subs.ass" -c:a copy out.mp4
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
