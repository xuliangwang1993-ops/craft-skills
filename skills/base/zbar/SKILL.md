---
name: zbar
name_zh: 二维码/条码识别（ZBar）
description: 用 zbar 开源工具完成「二维码/条码」。当任务需要 二维码/条码 且希望用开源、可独立运行的底层工具时使用。
triggers: [zbar, 二维码/条码]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: image
layer: base
backs: 二维码/条码
wave: 1
stage: 入库
version: 1
license: LGPL-2.1
---

# zbar · 二维码/条码识别（ZBar）

**它让我们能做什么：** 从图片和视频帧读出二维码/条码内容，票据、包装、物料单自动录入。

## 定位

- 槽位：二维码/条码（一格一个最强工具，本格只放 zbar）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：LGPL-2.1
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
sudo apt install zbar-tools  # 生成二维码另配 qrencode
```

## 核心用法

```
zbarimg --raw code.png
zbarimg -q --xml scan.jpg
qrencode -o qr.png 'https://example.com'   # 生成（qrencode, LGPL）
```

## 输入/输出校验

- 先侦察输入，再处理。
- `zbarimg` 退出码 0 表示识别到码，4 表示未识别；生成后用 zbarimg 回读核对。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
