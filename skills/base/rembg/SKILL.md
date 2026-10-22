---
name: rembg
name_zh: 图片去背景（rembg）
description: 用 rembg 开源工具完成「图片抠图/去背景」。当任务需要 图片抠图/去背景 且希望用开源、可独立运行的底层工具时使用。
triggers: [rembg, 图片抠图/去背景]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: image
layer: base
backs: 图片抠图/去背景
wave: 1
stage: 入库
version: 1
license: MIT
---

# rembg · 图片去背景（rembg）

**它让我们能做什么：** 一条命令把商品/人像图去背景成透明 PNG，直接进 designcraft/libvips 合成。

## 定位

- 槽位：图片抠图/去背景（一格一个最强工具，本格只放 rembg）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
pip install "rembg[cli]"
```

## 核心用法

```
rembg i in.jpg out.png
rembg p input_dir/ output_dir/
rembg i -m birefnet-general in.jpg out.png
```

## 输入/输出校验

- 先侦察输入，再处理。
- 输出为带 alpha 的 PNG（`vipsheader` 看 bands=4）；抽样检查边缘。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
