---
name: blender
name_zh: 3D 建模与渲染（Blender 无界面）
description: 用 blender 开源工具完成「3D 建模/渲染」。当任务需要 3D 建模/渲染 且希望用开源、可独立运行的底层工具时使用。
triggers: [blender, 3D 建模/渲染]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: 3d
layer: base
backs: 3D 建模/渲染
wave: 1
stage: 入库
version: 1
license: GPL-2.0+
---

# blender · 3D 建模与渲染（Blender 无界面）

**它让我们能做什么：** 无界面 Python 驱动建模、渲染出图和视频，3D 片头、产品图直接进 FFmpeg/MLT。

## 定位

- 槽位：3D 建模/渲染（一格一个最强工具，本格只放 blender）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：GPL-2.0+
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
sudo apt install blender  # 或官网下载（版本更新）
```

## 核心用法

```
blender -b scene.blend -o //render/frame_#### -F PNG -f 1
blender -b scene.blend -a              # 渲染整段动画
blender -b -P build.py -- --out out.glb # 脚本建模并导出
```

## 输入/输出校验

- 先侦察输入，再处理。
- 输出帧/文件存在；`ffprobe` 或图片尺寸核对与场景设置一致；日志无 Python Traceback。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
