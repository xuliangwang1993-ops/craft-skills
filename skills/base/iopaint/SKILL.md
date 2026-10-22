---
name: iopaint
name_zh: 图片修复/消除路人（LaMa · IOPaint）
description: 用 iopaint 开源工具完成「图片修复/消除路人」。当任务需要 图片修复/消除路人 且希望用开源、可独立运行的底层工具时使用。
triggers: [iopaint, 图片修复/消除路人]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: image
layer: base
backs: 图片修复/消除路人
wave: 2
stage: 入库
version: 1
license: "Apache-2.0（LaMa 模型 Apache-2.0）"
---

# iopaint · 图片修复/消除路人（LaMa · IOPaint）

**它让我们能做什么：** 按遮罩擦除路人、水印、杂物并自然补全背景。

## 定位

- 槽位：图片修复/消除路人（一格一个最强工具，本格只放 iopaint）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0（LaMa 模型 Apache-2.0）
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
pip install iopaint
```

## 核心用法

```
iopaint run --model=lama --device=cpu --image=imgs/ --mask=masks/ --output=out/
# 或起服务：iopaint start --model=lama --port=8080
```

## 输入/输出（串联）

- 输入 png/jpg + 同名黑白遮罩 png（可由 rembg/YOLO 分割生成）→ 输出修复后 png，接 libvips/ImageMagick。

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
