---
name: real-esrgan
name_zh: 超分辨率放大（Real-ESRGAN）
description: 用 real-esrgan 开源工具腾讯 ARC 开源的真实场景超分模型，图片/视频帧 2x–4x 放大并去噪。当任务需要 超分辨率放大（Real-ESRGAN） 且希望用开源、可独立运行的底层工具（photocraft / filmcraft 画质增强补位）时使用。
triggers: [real-esrgan, 超分辨率放大]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: vision
layer: base
backs: photocraft / filmcraft 画质增强补位
version: 1
license: BSD-3-Clause
---

# real-esrgan · 超分辨率放大（Real-ESRGAN）

**它让我们能做什么：** 超分放大：老照片、低清素材、视频帧放大修复。

腾讯 ARC 开源的真实场景超分模型，图片/视频帧 2x–4x 放大并去噪。

## 定位

- 槽位：photocraft / filmcraft 画质增强补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：BSD-3-Clause

## 安装

```sh
# 推荐：ncnn 便携版（pip install realesrgan basicsr 在新版 Python/torchvision 上构建失败，不推荐）
curl -LO https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip
unzip realesrgan-ncnn-vulkan-20220424-ubuntu.zip && chmod +x realesrgan-ncnn-vulkan   # 自带 models/
# 无显卡机器：sudo apt install mesa-vulkan-drivers，再 export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json（CPU 软件渲染，慢但可用）
```

## 核心用法

```
# 便携版（ncnn，支持 AMD/Intel/NVIDIA）
realesrgan-ncnn-vulkan -i in.jpg -o out.png -n realesrgan-x4plus -s 4
realesrgan-ncnn-vulkan -i frames/ -o up/ -n realesr-animevideov3 -s 2   # 动漫/视频帧
# 视频：ffmpeg 拆帧 → 放大 → 合帧
mkdir -p frames up    # 目录必须先建好
FPS=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 in.mp4)   # 用源帧率，写死 30 会变速
ffmpeg -i in.mp4 frames/%06d.png
realesrgan-ncnn-vulkan -i frames/ -o up/ -n realesr-animevideov3 -s 2
ffmpeg -framerate "$FPS" -i up/%06d.png -i in.mp4 -map 0:v -map 1:a? -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 核对输出分辨率 = 输入 × 倍数；放大后对比局部细节，人像可加 GFPGAN 修脸。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
