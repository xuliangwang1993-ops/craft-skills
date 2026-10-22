---
name: robust-video-matting
name_zh: 无绿幕人像抠像（RVM）
description: 用 robust-video-matting 开源工具字节开源实时人像视频抠图，不需绿幕，输出 alpha 通道或合成视频。当任务需要 无绿幕人像抠像（RVM） 且希望用开源、可独立运行的底层工具（effectcraft / filmcraft 抠像补位）时使用。
triggers: [robust-video-matting, 无绿幕人像抠像]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: video
layer: base
backs: effectcraft / filmcraft 抠像补位
version: 1
license: GPL-3.0
---

# robust-video-matting · 无绿幕人像抠像（RVM）

**它让我们能做什么：** 抠像：不用绿幕直接把人物从视频里抠出来换背景。

字节开源实时人像视频抠图，不需绿幕，输出 alpha 通道或合成视频。

## 定位

- 槽位：effectcraft / filmcraft 抠像补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：GPL-3.0

## 安装

```sh
git clone https://github.com/PeterL1n/RobustVideoMatting && pip install -r RobustVideoMatting/requirements_inference.txt
```

## 核心用法

```
import torch
from inference import convert_video     # 在 RobustVideoMatting 目录下运行
model = torch.hub.load("PeterL1n/RobustVideoMatting", "mobilenetv3").eval().cuda()
convert_video(model, input_source="in.mp4", output_type="video",
              output_composition="com.mp4", output_alpha="pha.mp4",
              downsample_ratio=None, seq_chunk=12)
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 抽帧检查发丝和边缘；`ffprobe` 核对输出帧数与源一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
