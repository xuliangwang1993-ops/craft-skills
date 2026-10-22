---
name: practical-rife
name_zh: 慢动作补帧（Practical-RIFE）
description: 用 practical-rife 开源工具完成「慢动作补帧」。当任务需要 慢动作补帧 且希望用开源、可独立运行的底层工具时使用。
triggers: [practical-rife, 慢动作补帧]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: video
layer: base
backs: 慢动作补帧
wave: 2
stage: 入库
version: 1
license: "MIT"
---

# practical-rife · 慢动作补帧（Practical-RIFE）

**它让我们能做什么：** 视频补帧到 2x/4x，做丝滑慢动作、低帧率素材提帧。

## 定位

- 槽位：慢动作补帧（一格一个最强工具，本格只放 practical-rife）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
git clone https://github.com/hzwer/Practical-RIFE && cd Practical-RIFE && pip install -r requirements.txt
# 按 README 下载模型权重放入 train_log/
```

## 核心用法

```
python inference_video.py --multi=2 --video=in.mp4
# 输出 in_2X_xxfps.mp4
```

## 输入/输出（串联）

- 输入 mp4（ffmpeg 可预裁剪）→ 输出高帧率 mp4，接 ffmpeg 变速/ mlt 时间线。建议 GPU。

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
