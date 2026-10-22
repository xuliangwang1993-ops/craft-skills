---
name: musetalk
name_zh: 数字人口型驱动（MuseTalk）
description: 用 MuseTalk 开源工具完成「数字人口型/表情驱动」。当任务需要 数字人口型/表情驱动 且希望用开源、可独立运行、可商用的底层工具时使用。
triggers: [musetalk, 数字人, 口型驱动, lip-sync]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: video
layer: base
backs: 数字人口型/表情驱动
wave: 2
stage: 入库
version: 1
license: "MIT（代码与 MuseTalk 权重，官方声明可商用）；依赖权重：whisper-tiny Apache-2.0、sd-vae-ft-mse MIT、DWPose Apache-2.0、face-parsing BiSeNet MIT、ResNet18 BSD、S3FD（face-alignment）BSD-3；⚠️ 官方测试数据仅限研究，勿用；SyncNet 仅训练用，推理不下载"
---

# musetalk · 数字人口型驱动（MuseTalk）

**它让我们能做什么：** 给一段人像视频/照片 + 一段音频，输出口型对上音频的数字人视频（30fps+ 实时级，需 GPU）。

## 定位

- 槽位：数字人口型/表情驱动（一格一个最强工具，本格只放 musetalk）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT（代码与 MuseTalk 权重，官方声明可商用）；依赖权重：whisper-tiny Apache-2.0、sd-vae-ft-mse MIT、DWPose Apache-2.0、face-parsing BiSeNet MIT、ResNet18 BSD、S3FD（face-alignment）BSD-3；⚠️ 官方测试数据仅限研究，勿用；SyncNet 仅训练用，推理不下载
- 阶段：入库（文档已写，尚未落地验证）
- 2026-10-22 替换上任工具（许可证问题），见 docs/扩库立项.md

## 安装

```sh
git clone https://github.com/TMElyralab/MuseTalk && cd MuseTalk && pip install -r requirements.txt
# 按 README 装 mmcv/mmpose，再 bash download_weights.sh（可删掉 SyncNet 那段）
```

## 核心用法

```
python -m scripts.inference --inference_config configs/inference/test.yaml \
  --result_dir out --unet_model_path models/musetalkV15/unet.pth \
  --unet_config models/musetalkV15/musetalk.json --version v15
```

## 输入/输出（串联）

- 输入人像视频/图片 + WAV（可来自 gpt-sovits/cosyvoice）→ 输出 MP4，接 ffmpeg 合成字幕、real-esrgan 超分。

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
