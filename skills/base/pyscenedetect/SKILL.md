---
name: pyscenedetect
name_zh: 镜头切分（PySceneDetect）
description: 用 pyscenedetect 开源工具完成「镜头/场景检测」。当任务需要 镜头/场景检测 且希望用开源、可独立运行的底层工具时使用。
triggers: [pyscenedetect, 镜头/场景检测]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: video
layer: base
backs: 镜头/场景检测
wave: 1
stage: 入库
version: 1
license: BSD-3-Clause
---

# pyscenedetect · 镜头切分（PySceneDetect）

**它让我们能做什么：** 自动找出每个镜头切点，是「一键成片」的第一步，输出时间码给 MLT/FFmpeg 剪辑。

## 定位

- 槽位：镜头/场景检测（一格一个最强工具，本格只放 pyscenedetect）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：BSD-3-Clause
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
pip install "scenedetect[opencv]"
```

## 核心用法

```
scenedetect -i in.mp4 detect-adaptive list-scenes
scenedetect -i in.mp4 detect-content split-video
scenedetect -i in.mp4 detect-adaptive save-images
```

## 输入/输出校验

- 先侦察输入，再处理。
- 生成 scenes CSV；镜头数合理；切分片段总时长与原片一致（ffprobe 核对）。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
