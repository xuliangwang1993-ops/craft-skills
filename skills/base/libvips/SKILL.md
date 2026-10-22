---
name: libvips
name_zh: 高速批量图片处理（libvips）
description: 用 libvips 开源工具流式、低内存的图像处理库，大图和批量缩略/转码比 ImageMagick 快数倍。当任务需要 高速批量图片处理（libvips） 且希望用开源、可独立运行的底层工具（photocraft 批处理开源替代）时使用。
triggers: [libvips, 高速批量图片处理]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: photo
layer: base
backs: photocraft 批处理开源替代
version: 1
license: LGPL-2.1+
---

# libvips · 高速批量图片处理（libvips）

**它让我们能做什么：** 批量图片：上万张图缩略、转 WebP/AVIF、裁剪，速度和内存最优。

流式、低内存的图像处理库，大图和批量缩略/转码比 ImageMagick 快数倍。

## 定位

- 槽位：photocraft 批处理开源替代
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：LGPL-2.1+

## 安装

```sh
sudo apt install libvips-tools  # macOS: brew install vips；Python: pip install pyvips
```

## 核心用法

```
vipsthumbnail in.jpg -s 800x800 -o thumb_%s.jpg[Q=85]
vips copy in.tif out.webp[Q=80]
vips crop in.jpg out.jpg 100 100 640 480
vipsheader -a in.jpg
# Python
import pyvips
pyvips.Image.thumbnail("in.jpg", 1200).write_to_file("out.webp[Q=80]")
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- `vipsheader out.webp` 核对尺寸；批量后核对输出数 = 输入数。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
