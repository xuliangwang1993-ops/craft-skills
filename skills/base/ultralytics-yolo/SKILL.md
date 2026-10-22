---
name: ultralytics-yolo
name_zh: 目标检测/跟踪（Ultralytics YOLO）
description: 用 ultralytics-yolo 开源工具完成「目标检测/跟踪」。当任务需要 目标检测/跟踪 且希望用开源、可独立运行的底层工具时使用。
triggers: [ultralytics-yolo, 目标检测/跟踪]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: vision
layer: base
backs: 目标检测/跟踪
wave: 2
stage: 入库
version: 1
license: "⚠️ AGPL-3.0（闭源商用需 Ultralytics 企业许可）"
---

# ultralytics-yolo · 目标检测/跟踪（Ultralytics YOLO）

**它让我们能做什么：** 检测、分割、跟踪画面里的人和物，给自动剪辑、打码、遮罩提供框和掩码。

## 定位

- 槽位：目标检测/跟踪（一格一个最强工具，本格只放 ultralytics-yolo）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：⚠️ AGPL-3.0（闭源商用需 Ultralytics 企业许可）
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
pip install ultralytics
```

## 核心用法

```
yolo predict model=yolo11n.pt source=in.mp4 save=True save_txt=True
yolo track model=yolo11n-seg.pt source=in.mp4
```

## 输入/输出（串联）

- 输入图片/视频 → 输出标注 mp4 + 每帧 txt 框（YOLO 格式，可转 json），掩码可喂 iopaint / ffmpeg 打码。

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
