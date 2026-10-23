---
name: framepack
name_zh: 长视频图生视频（FramePack）
description: 用 framepack 开源工具基于 HunyuanVideo 的下一帧预测，低显存生成长时视频。当任务需要 长视频图生视频 且希望用开源、可独立运行的底层工具（effectcraft 补位）时使用。
triggers: [framepack, 长视频图生视频]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: ai-video
layer: base
backs: effectcraft 补位
version: 1
license: Apache-2.0（底座模型 HunyuanVideo 许可另计 ⚠️）
---

# framepack · 长视频图生视频（FramePack）

**它让我们能做什么：** AI 视频：图片动起来。

基于 HunyuanVideo 的下一帧预测，低显存生成长时视频。

## 定位

- 槽位：effectcraft 补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0（底座模型 HunyuanVideo 许可另计 ⚠️）
- 无界面/命令行：部分（自带 Gradio，需改脚本批量）
- GPU：需要（约 6GB+）
- 官方：https://github.com/lllyasviel/FramePack

## 安装

```sh
git clone https://github.com/lllyasviel/FramePack && cd FramePack && pip install -r requirements.txt
```

## 核心用法

```
python demo_gradio.py --server 127.0.0.1
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
