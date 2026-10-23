---
name: ltx-video
name_zh: AI 视频生成（LTX-Video）
description: 用 ltx-video 开源工具Lightricks 开源实时级文/图生视频模型。当任务需要 AI 视频生成 且希望用开源、可独立运行的底层工具（effectcraft / filmcraft 空镜补位）时使用。
triggers: [ltx-video, AI 视频生成]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: ai-video
layer: base
backs: effectcraft / filmcraft 空镜补位
version: 1
license: Apache-2.0（各版本权重另见模型卡许可）
---

# ltx-video · AI 视频生成（LTX-Video）

**它让我们能做什么：** AI 视频：快速出空镜。

Lightricks 开源实时级文/图生视频模型。

## 定位

- 槽位：effectcraft / filmcraft 空镜补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0（各版本权重另见模型卡许可）
- 无界面/命令行：是
- GPU：需要
- 官方：https://github.com/Lightricks/LTX-Video

## 安装

```sh
git clone https://github.com/Lightricks/LTX-Video && cd LTX-Video && pip install -e .[inference]
```

## 核心用法

```
python inference.py --prompt '...' --height 704 --width 1216 --num_frames 121 --pipeline_config configs/ltxv-2b-0.9.8-distilled.yaml   # 配置名以仓库为准
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
