---
name: moviepy
name_zh: Python 视频剪辑（MoviePy）
description: 用 moviepy 开源工具用 Python 脚本剪辑、拼接、叠字、合成视频，适合批量出多尺寸宣传片。当任务需要 Python 视频剪辑 且希望用开源、可独立运行的底层工具（filmcraft 开源替代）时使用。
triggers: [moviepy, Python 视频剪辑]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: video
layer: base
backs: filmcraft 开源替代
version: 1
license: MIT
---

# moviepy · Python 视频剪辑（MoviePy）

**它让我们能做什么：** 剪辑：脚本化批量剪片、裁尺寸、叠标题。

用 Python 脚本剪辑、拼接、叠字、合成视频，适合批量出多尺寸宣传片。

## 定位

- 槽位：filmcraft 开源替代
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT
- 无界面/命令行：是
- GPU：不需要
- 官方：https://github.com/Zulko/moviepy

## 安装

```sh
pip install moviepy
```

## 核心用法

```
python -c "from moviepy import VideoFileClip; VideoFileClip('in.mp4').subclipped(0,30).resized(height=1920).write_videofile('out.mp4')"   # MoviePy 2.x API
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
