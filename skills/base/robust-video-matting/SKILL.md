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
git clone https://github.com/PeterL1n/RobustVideoMatting
# requirements_inference.txt 锁定 torch==1.9 / av==8.0.3，新版 Python 装不上；直接装新版依赖即可：
pip install torch torchvision av pims tqdm
# 权重直接下载（torch.hub 走 GitHub API，容易卡住）
curl -L -o RobustVideoMatting/rvm_mobilenetv3.pth https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3.pth
```

## 核心用法

```
import torch
from model import MattingNetwork        # 在 RobustVideoMatting 目录下运行
from inference import convert_video
device = "cuda" if torch.cuda.is_available() else "cpu"
model = MattingNetwork("mobilenetv3").eval().to(device)
model.load_state_dict(torch.load("rvm_mobilenetv3.pth", map_location=device))
# PyAV ≥10 下 output_type="video" 会报 to_avrational 错，统一输出 PNG 序列再用 ffmpeg 合成
convert_video(model, input_source="in.mp4", output_type="png_sequence",
              output_composition="com", output_alpha="pha",
              downsample_ratio=None, seq_chunk=12, device=device)
# ffmpeg -framerate <源帧率> -i pha/%04d.png -c:v libx264 -pix_fmt yuv420p pha.mp4
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 抽帧检查发丝和边缘；`ffprobe` 核对输出帧数与源一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
