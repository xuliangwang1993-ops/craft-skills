---
name: resvg
name_zh: SVG 渲染（resvg）
description: 用 resvg 开源工具快速、准确的 SVG 转 PNG 渲染器，适合从分镜 SVG 批量出帧。当任务需要 SVG 渲染 且希望用开源、可独立运行的底层工具（figcraft / vectorcraft 开源替代）时使用。
triggers: [resvg, SVG 渲染]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: image
layer: base
backs: figcraft / vectorcraft 开源替代
version: 1
license: Apache-2.0 / MIT
---

# resvg · SVG 渲染（resvg）

**它让我们能做什么：** 画面：分镜/字卡 SVG 批量栅格化。

快速、准确的 SVG 转 PNG 渲染器，适合从分镜 SVG 批量出帧。

## 定位

- 槽位：figcraft / vectorcraft 开源替代
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0 / MIT
- 无界面/命令行：是
- GPU：不需要
- 官方：https://github.com/linebender/resvg

## 安装

```sh
sudo apt install resvg   # 或 cargo install resvg
```

## 核心用法

```
resvg frame.svg frame.png -w 1080
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
