---
name: liveportrait
name_zh: 数字人口型/表情驱动（LivePortrait）
description: 用 liveportrait 开源工具完成「数字人口型/表情驱动」。当任务需要 数字人口型/表情驱动 且希望用开源、可独立运行的底层工具时使用。
triggers: [liveportrait, 数字人口型/表情驱动]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: vision
layer: base
backs: 数字人口型/表情驱动
wave: 2
stage: 入库
version: 1
license: "⚠️ 代码 MIT，但依赖的 InsightFace 人脸模型仅限非商用（商用须替换检测模型或取得授权）"
---

# liveportrait · 数字人口型/表情驱动（LivePortrait）

**它让我们能做什么：** 一张照片 + 驱动视频，生成说话、表情跟随的人像视频。

## 定位

- 槽位：数字人口型/表情驱动（一格一个最强工具，本格只放 liveportrait）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：⚠️ 代码 MIT，但依赖的 InsightFace 人脸模型仅限非商用（商用须替换检测模型或取得授权）
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
git clone https://github.com/KwaiVGI/LivePortrait && cd LivePortrait && pip install -r requirements.txt
huggingface-cli download KwaiVGI/LivePortrait --local-dir pretrained_weights
```

## 核心用法

```
python inference.py -s face.jpg -d driving.mp4
# 输出在 animations/
```

## 输入/输出（串联）

- 输入人像 jpg + 驱动 mp4 → 输出 mp4，接 ffmpeg 合音轨 / real-esrgan 超分。**仅用于本人或已授权肖像。**

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
