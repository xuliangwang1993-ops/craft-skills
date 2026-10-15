---
name: lightcraft
name_zh: 照片调色
description: 用 LightCraft 引擎（330 个工具）管理照片库并调色：导入、查询筛选、调整显影参数、套用预设、裁剪、渲染导出。当任务涉及照片批量调色、图库整理、预设套用或批量出图时使用。
triggers: [调色, 照片库, 显影, 预设, 批量出图, Lightroom]
inputs:
  - name: task
    description: 任务描述与交付要求
    required: true
tools: []
mcp: [lightcraft]
permissions: [read_file, write_file]
version: 1
license: Proprietary
category: arts-design-media
source: https://getartcraft.com/apps/lightcraft
---
# 照片调色班组（lightcraft）

由 Craft 引擎驱动，通过 MCP 无头调用。

## MCP 工具速查

| 工具 | 用途 |
|------|------|
| `import / query_photos / select_photos` | **导入与智能筛选** |
| `get_develop / set_develop / apply_preset` | 显影参数与预设 |
| `crop` | 裁剪 |
| `render_photo / export` | 渲染与导出 |
| `cmd_library_* 系列` | 图库管理（源、筛选、文件夹、标签） |

## 标准作业流程

1. `import` 导入 → `query_photos` 按条件筛选出目标集
2. `select_photos` 选定 → `apply_preset` 或逐个 `set_develop`
3. `crop` 调整构图
4. 先 `render_photo` 一张试效果，满意再批量 `export`

## 硬规则

- 批量套预设前必须先在 1-2 张上验收，确认风格对路再全量
- 调色不改变原始文件，只写显影参数
- 交付格式按用途定（打印要 TIFF/高质 JPEG，网络用压缩 JPEG）

## 路径注意

这些引擎是 Windows 可执行文件，**不认 WSL 的 `/mnt/c/...` 路径**，必须传 Windows 格式（如 `C:\\Users\\you\\out.png`）。从 WSL 调用时用 `wslpath -w <路径>` 转换，或直接用 Windows 绝对路径。
