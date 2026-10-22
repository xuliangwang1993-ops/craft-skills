---
name: rf-detr
name_zh: 目标检测/分割（RF-DETR）
description: 用 RF-DETR 开源工具完成「目标检测/跟踪」。当任务需要 目标检测/跟踪 且希望用开源、可独立运行、可商用的底层工具时使用。
triggers: [rf-detr, 目标检测, 实例分割]
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
license: "Apache-2.0（代码与 Nano/Small/Medium/Base/Large 及 Seg 权重；⚠️ 只用 Apache 档，禁装 rfdetr[plus]：Atto/Femto/Pico/XL/2XL 为 PML 1.0）"
---

# rf-detr · 目标检测/分割（RF-DETR）

**它让我们能做什么：** 在图片/视频帧里框出人、物、商品并给出类别和置信度，可微调到自家数据集；跟踪可接 supervision ByteTrack（MIT）。

## 定位

- 槽位：目标检测/跟踪（一格一个最强工具，本格只放 rf-detr）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0（代码与 Nano/Small/Medium/Base/Large 及 Seg 权重；⚠️ 只用 Apache 档，禁装 rfdetr[plus]：Atto/Femto/Pico/XL/2XL 为 PML 1.0）
- 阶段：入库（文档已写，尚未落地验证）
- 2026-10-22 替换上任工具（许可证问题），见 docs/扩库立项.md

## 安装

```sh
pip install rfdetr supervision   # 不要装 rfdetr[plus]
```

## 核心用法

```
from rfdetr import RFDETRMedium
import supervision as sv
m = RFDETRMedium()
dets = m.predict("in.jpg", threshold=0.5)   # sv.Detections
sv.ByteTrack().update_with_detections(dets)  # 视频逐帧跟踪
```

## 输入/输出（串联）

- 输入图片/视频帧 → 输出 sv.Detections（xyxy、class_id、confidence），可导出 JSON/COCO，接 opencv/ffmpeg 裁切、iopaint 去除、mediapipe 细化。

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
