---
name: fish-speech
name_zh: 声音克隆（Fish-Speech）
description: 用 fish-speech 开源工具多语种 TTS 与克隆。⚠️ 模型权重 CC-BY-NC-SA，不可商用。当任务需要 声音克隆 且希望用开源、可独立运行的底层工具（soundcraft 配音补位）时使用。
triggers: [fish-speech, 声音克隆]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: tts
layer: base
backs: soundcraft 配音补位
version: 1
license: ⚠️ 代码见仓库 LICENSE；权重 CC-BY-NC-SA-4.0（不可商用）
---

# fish-speech · 声音克隆（Fish-Speech）

**它让我们能做什么：** 配音：仅限内部试样（权重不可商用）。

多语种 TTS 与克隆。⚠️ 模型权重 CC-BY-NC-SA，不可商用。

## 定位

- 槽位：soundcraft 配音补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：⚠️ 代码见仓库 LICENSE；权重 CC-BY-NC-SA-4.0（不可商用）
- 无界面/命令行：是（API 服务）
- GPU：需要
- 官方：https://github.com/fishaudio/fish-speech

## 安装

```sh
git clone https://github.com/fishaudio/fish-speech && cd fish-speech && pip install -e .
```

## 核心用法

```
python tools/api_server.py --listen 0.0.0.0:8080   # 具体参数以仓库 docs 为准
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
