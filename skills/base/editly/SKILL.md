---
name: editly
name_zh: 声明式成片（editly）
description: 用 editly 开源工具用 JSON5 描述片段、转场、标题，命令行一键出宣传短片。当任务需要 声明式成片 且希望用开源、可独立运行的底层工具（filmcraft 开源替代）时使用。
triggers: [editly, 声明式成片]
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

# editly · 声明式成片（editly）

**它让我们能做什么：** 一键成片：模板化宣传片批量生成。

用 JSON5 描述片段、转场、标题，命令行一键出宣传短片。

## 定位

- 槽位：filmcraft 开源替代
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT
- 无界面/命令行：是（需 xvfb 或 headless-gl）
- GPU：不需要
- 官方：https://github.com/mifi/editly

## 安装

```sh
npm install -g editly
```

## 核心用法

```
editly spec.json5 --out out.mp4    # spec 中写 width/height/clips/layers
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
