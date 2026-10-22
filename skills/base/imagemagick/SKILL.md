---
name: imagemagick
name_zh: 通用图片处理（ImageMagick）
description: 用 imagemagick 开源工具覆盖 200+ 格式的图像命令行：缩放、裁剪、合成、加字、水印、拼图、格式转换。当任务需要 通用图片处理（ImageMagick） 且希望用开源、可独立运行的底层工具（photocraft 批处理开源替代）时使用。
triggers: [imagemagick, 通用图片处理]
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
license: ImageMagick License（Apache-2.0 风格）
---

# imagemagick · 通用图片处理（ImageMagick）

**它让我们能做什么：** 批量图片：加水印、拼图、加字、格式转换等需要合成的批处理。

覆盖 200+ 格式的图像命令行：缩放、裁剪、合成、加字、水印、拼图、格式转换。

## 定位

- 槽位：photocraft 批处理开源替代
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：ImageMagick License（Apache-2.0 风格）

## 安装

```sh
sudo apt install imagemagick  # macOS: brew install imagemagick
```

## 核心用法

```
magick in.jpg -resize 1200x1200\> -quality 85 out.jpg      # IM7；IM6 用 convert
magick in.jpg -gravity southeast logo.png -geometry +20+20 -composite wm.jpg
magick mogrify -path out/ -resize 50% -format webp *.jpg
magick montage *.jpg -tile 4x -geometry 300x300+4+4 sheet.jpg
magick identify -format "%f %wx%h\n" *.jpg
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- `magick identify` 核对尺寸格式；不处理不可信 SVG/PS 输入（安全策略见 policy.xml）。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
