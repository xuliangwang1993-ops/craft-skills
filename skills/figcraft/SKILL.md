---
name: figcraft
name_zh: 界面设计
description: 用 FigCraft 引擎做界面设计与原型：建稿、绘制图形与路径、自动布局、组件、导出 PNG/SVG。当任务涉及 UI 稿、界面原型、组件库、设计规范交付时使用。
triggers: [UI 稿, 界面设计, 原型, 组件, 自动布局, Figma, figcraft]
inputs:
  - name: task
    description: 设计需求（页面、组件、尺寸、目标平台）
    required: true
tools: []
mcp: [figcraft]
permissions: [read_file, write_file]
version: 1
license: MIT
category: arts-design-media
source: https://github.com/storytold/figcraft
---

# 界面设计班组（figcraft）

Figma 类工具的净室重写版，纯 Rust。**400+ 命令**，UI / CLI / JSON 控制通道 / MCP 全部调同一套命令注册表。

## CLI 常用命令

```sh
figcraft-cli render landing.figcraft -o landing.png --scale 2   # 渲染出图
figcraft-cli export landing.figcraft -o out/ --format svg       # 导出 SVG
figcraft-cli run build-card.json --out card.figcraft            # 跑命令脚本建稿
figcraft-cli commands --filter autoLayout                       # 查命令与参数
figcraft-cli mcp                                                # 起 MCP 服务（无头）
figcraft-cli mcp --attach 47800                                 # 或挂到运行中的 App
```

桌面版另有回环控制通道：`figcraft --control <port>`（查 UI 状态、指针/键盘驱动、截图）。

## MCP 工具

`command_list` / `command_run` / `command_batch` 是通用通道；
`inspect_document` / `render_preview` / `screenshot` 用于侦察与验收；
`type_text` / `select_tool` / `pointer_gesture` 等用于驱动画布。

## 标准作业流程

1. 先确认画板尺寸与目标平台（移动 375 / 桌面 1440 / 自定义）
2. `command_list` 查可用命令，`command_run` 建稿
3. 用自动布局命令排布，别手算坐标
4. `render_preview` 目视校验
5. `export` 出 PNG（预览）/ SVG（切图）

## 硬规则

- 组件要真的做成组件，别复制粘贴一堆散元素
- 交付前渲染一遍确认没有重叠、错位、溢出
- 尺寸单位与栅格先定死，改起来代价极大
- 用户给的品牌色/字体必须沿用

## 路径注意

Windows 可执行文件**不认 WSL 的 `/mnt/c/...`**，必须传 `C:\...` 格式。
