---
name: wan
name_zh: 文生视频（Wan 2.x）
description: 用 wan 开源工具完成「文生视频」。当任务需要 文生视频 且希望用开源、可独立运行的底层工具时使用。
triggers: [wan, 文生视频]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: video
layer: base
backs: 文生视频
wave: 2
stage: 入库
version: 1
license: "Apache-2.0（⚠️ 需大显存 GPU）"
---

# wan · 文生视频（Wan 2.x）

**它让我们能做什么：** 文字或图片生成短视频镜头，补空镜、做概念片。

## 定位

- 槽位：文生视频（一格一个最强工具，本格只放 wan）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0（⚠️ 需大显存 GPU）
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
git clone https://github.com/Wan-Video/Wan2.2 && cd Wan2.2 && pip install -r requirements.txt
huggingface-cli download Wan-AI/Wan2.2-TI2V-5B --local-dir ./Wan2.2-TI2V-5B
```

## 核心用法

```
python generate.py --task ti2v-5B --size 1280*704 --ckpt_dir ./Wan2.2-TI2V-5B --prompt "海边日落，航拍" --base_seed 42
```

## 输入/输出（串联）

- 输入文本（可加首帧图）→ 输出 mp4，接 practical-rife 补帧 / mlt 成片。固定 --base_seed 保证可复现。

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
