---
name: motion-canvas
name_zh: TypeScript 动效（Motion Canvas）
description: 用 motion-canvas 开源工具用 TypeScript 生成器函数写时间轴动画，浏览器预览，渲染出图序列/视频。当任务需要 TypeScript 动效 且希望用开源、可独立运行的底层工具（effectcraft 动效补位）时使用。
triggers: [motion-canvas, TypeScript 动效]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: motion
layer: base
backs: effectcraft 动效补位
version: 1
license: MIT
---

# motion-canvas · TypeScript 动效（Motion Canvas）

**它让我们能做什么：** 动效：精细关键帧动画。

用 TypeScript 生成器函数写时间轴动画，浏览器预览，渲染出图序列/视频。

## 定位

- 槽位：effectcraft 动效补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT
- 无界面/命令行：部分（渲染需浏览器，可用 Playwright 驱动）
- GPU：不需要
- 官方：https://github.com/motion-canvas/motion-canvas

## 安装

```sh
npm init @motion-canvas@latest
```

## 核心用法

```
npm start   # 编辑器内点 Render；无界面批量渲染建议用 revideo
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
