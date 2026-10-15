---
name: vectorcraft
name_zh: 矢量图形
description: 用 VectorCraft 引擎绘制矢量图形：画路径与形状、设置填充描边、编排图层、导出。当任务涉及 logo、图标、插画、矢量海报或 SVG/EPS 类交付物时使用。
triggers: [矢量图, logo, 图标, 插画, SVG, EPS, 路径]
inputs:
  - name: task
    description: 任务描述与交付要求
    required: true
tools: []
mcp: [vectorcraft]
permissions: [read_file, write_file]
version: 1
license: Proprietary
category: arts-design-media
source: https://getartcraft.com/apps/vectorcraft
---
# 矢量图形班组（vectorcraft）

由 Craft 引擎驱动，通过 MCP 无头调用。

## MCP 工具速查

| 工具 | 用途 |
|------|------|
| `open_file / save_file / export` | 文件生命周期与导出 |
| `draw_path / draw_shape / set_paint` | 路径、形状与上色 |
| `inspect_document / doc_inspect` | 结构侦察 |
| `render_preview / screenshot` | 渲染预览 |
| `run_command / command_batch / list_commands` | 底层命令通道 |

## 标准作业流程

1. 先确认尺寸、色彩空间、最终用途（印刷 / 屏幕）
2. `open_file` 或新建；用 `inspect_document` 看现有结构
3. `draw_path` / `draw_shape` + `set_paint` 绘制
4. `render_preview` 目视校验，最后 `export`

## 硬规则

- 印刷用途必须用 CMYK 或确认色彩配置，别默认 RGB 交差
- 路径要闭合、要合并的节点要合并，别留半成品
- logo 类交付物需同时给可缩放矢量与预览图

## 路径注意

这些引擎是 Windows 可执行文件，**不认 WSL 的 `/mnt/c/...` 路径**，必须传 Windows 格式（如 `C:\\Users\\you\\out.png`）。从 WSL 调用时用 `wslpath -w <路径>` 转换，或直接用 Windows 绝对路径。
