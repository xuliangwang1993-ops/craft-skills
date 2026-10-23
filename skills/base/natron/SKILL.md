---
name: natron
name_zh: 节点式合成（Natron）
description: 用 natron 开源工具类 Nuke 的节点合成软件，NatronRenderer 可无界面渲染工程。基本停更，仅作合成补位。当任务需要 节点式合成 且希望用开源、可独立运行的底层工具（effectcraft 合成补位）时使用。
triggers: [natron, 节点式合成]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: compositing
layer: base
backs: effectcraft 合成补位
version: 1
license: GPL-2.0
---

# natron · 节点式合成（Natron）

**它让我们能做什么：** 合成：节点式抠像、跟踪、合成工程批量渲染。

类 Nuke 的节点合成软件，NatronRenderer 可无界面渲染工程。基本停更，仅作合成补位。

## 定位

- 槽位：effectcraft 合成补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：GPL-2.0
- 无界面/命令行：是（NatronRenderer）
- GPU：不需要
- 官方：https://github.com/NatronGitHub/Natron

## 安装

```sh
下载官方 Linux 包：https://github.com/NatronGitHub/Natron/releases
```

## 核心用法

```
NatronRenderer -w Write1 1-750 project.ntp
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
