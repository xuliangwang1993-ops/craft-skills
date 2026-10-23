---
name: revideo
name_zh: 可无界面渲染的代码动效（Revideo）
description: 用 revideo 开源工具Motion Canvas 的分支，增加 headless 渲染 API，适合服务端批量出片。当任务需要 可无界面渲染的代码动效 且希望用开源、可独立运行的底层工具（effectcraft / filmcraft 开源替代）时使用。
triggers: [revideo, 可无界面渲染的代码动效]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: motion
layer: base
backs: effectcraft / filmcraft 开源替代
version: 1
license: MIT
---

# revideo · 可无界面渲染的代码动效（Revideo）

**它让我们能做什么：** 动效：模板化动效视频服务端批量渲染。

Motion Canvas 的分支，增加 headless 渲染 API，适合服务端批量出片。

## 定位

- 槽位：effectcraft / filmcraft 开源替代
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT
- 无界面/命令行：是
- GPU：不需要
- 官方：https://github.com/midrender/revideo

## 安装

```sh
npm init @revideo@latest
```

## 核心用法

```
npx revideo render   # 或在 Node 中调用 @revideo/renderer 的 renderVideo()
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
