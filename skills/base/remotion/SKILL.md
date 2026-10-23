---
name: remotion
name_zh: React 视频（Remotion）
description: 用 remotion 开源工具用 React 组件写视频，CLI 渲染。⚠️ 非 OSI 开源：3 人以上公司商用须买许可。当任务需要 React 视频 且希望用开源、可独立运行的底层工具（effectcraft / filmcraft 补位）时使用。
triggers: [remotion, React 视频]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: motion
layer: base
backs: effectcraft / filmcraft 补位
version: 1
license: ⚠️ Remotion License（源码可见；个人/≤3 人公司免费，其余需付费）
---

# remotion · React 视频（Remotion）

**它让我们能做什么：** 动效：React 模板化视频（注意商用许可）。

用 React 组件写视频，CLI 渲染。⚠️ 非 OSI 开源：3 人以上公司商用须买许可。

## 定位

- 槽位：effectcraft / filmcraft 补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：⚠️ Remotion License（源码可见；个人/≤3 人公司免费，其余需付费）
- 无界面/命令行：是
- GPU：不需要
- 官方：https://github.com/remotion-dev/remotion

## 安装

```sh
npx create-video@latest
```

## 核心用法

```
npx remotion render src/index.ts MyComp out.mp4
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
