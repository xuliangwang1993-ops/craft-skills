---
name: pyloudnorm
name_zh: 响度测量（pyloudnorm）
description: 用 pyloudnorm 开源工具按 ITU-R BS.1770-4 测量积分响度，Python 调用，适合做 QA 校验。当任务需要 响度测量 且希望用开源、可独立运行的底层工具（soundcraft 响度校验补位）时使用。
triggers: [pyloudnorm, 响度测量]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: audio
layer: base
backs: soundcraft 响度校验补位
version: 1
license: MIT
---

# pyloudnorm · 响度测量（pyloudnorm）

**它让我们能做什么：** 响度：出片后自动校验 LUFS。

按 ITU-R BS.1770-4 测量积分响度，Python 调用，适合做 QA 校验。

## 定位

- 槽位：soundcraft 响度校验补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT
- 无界面/命令行：是
- GPU：不需要
- 官方：https://github.com/csteinmetz1/pyloudnorm

## 安装

```sh
pip install pyloudnorm soundfile
```

## 核心用法

```
python -c "import soundfile as sf,pyloudnorm as pl; d,r=sf.read('a.wav'); print(pl.Meter(r).integrated_loudness(d))"
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
