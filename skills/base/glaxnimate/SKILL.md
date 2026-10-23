---
name: glaxnimate
name_zh: Lottie 动画（Glaxnimate）
description: 用 glaxnimate 开源工具矢量动画编辑器，支持 Lottie/SVG 动画，带命令行导出。当任务需要 Lottie 动画 且希望用开源、可独立运行的底层工具（effectcraft / vectorcraft 补位）时使用。
triggers: [glaxnimate, Lottie 动画]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: motion
layer: base
backs: effectcraft / vectorcraft 补位
version: 1
license: GPL-3.0
---

# glaxnimate · Lottie 动画（Glaxnimate）

**它让我们能做什么：** 动效：Lottie 贴纸/图标动画。

矢量动画编辑器，支持 Lottie/SVG 动画，带命令行导出。

## 定位

- 槽位：effectcraft / vectorcraft 补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：GPL-3.0
- 无界面/命令行：部分（glaxnimate 命令行可导出）
- GPU：不需要
- 官方：https://gitlab.com/mattbas/glaxnimate

## 安装

```sh
sudo apt install glaxnimate
```

## 核心用法

```
glaxnimate anim.rawr --export out.json   # 导出 Lottie；具体格式参数见 glaxnimate --help
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
