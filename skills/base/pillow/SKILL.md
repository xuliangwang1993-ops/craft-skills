---
name: pillow
name_zh: Python 图像处理（Pillow）
description: 用 pillow 开源工具Python 标准图像库：裁剪、缩放、叠字、合成。当任务需要 Python 图像处理 且希望用开源、可独立运行的底层工具（photocraft 批处理补位）时使用。
triggers: [pillow, Python 图像处理]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: image
layer: base
backs: photocraft 批处理补位
version: 1
license: MIT-CMU（HPND）
---

# pillow · Python 图像处理（Pillow）

**它让我们能做什么：** 画面：脚本内图片处理。

Python 标准图像库：裁剪、缩放、叠字、合成。

## 定位

- 槽位：photocraft 批处理补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT-CMU（HPND）
- 无界面/命令行：是
- GPU：不需要
- 官方：https://github.com/python-pillow/Pillow

## 安装

```sh
pip install pillow
```

## 核心用法

```
python -c "from PIL import Image; Image.open('in.jpg').resize((1080,1920)).save('out.jpg')"
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
