---
name: photocraft
name_zh: 位图与图层
description: 用 PhotoCraft 引擎处理位图与图层文件：打开/新建文档、置入素材、图层导出、数据集合成、批量渲染。当任务涉及 PSD/图层文件、图片合成、批处理导出或格式转换时使用。
triggers: [PSD, 图层, 图片合成, 批处理导出, 抠图, 位图]
inputs:
  - name: task
    description: 任务描述与交付要求
    required: true
tools: []
mcp: [photocraft]
permissions: [read_file, write_file]
version: 1
license: Proprietary
category: arts-design-media
source: https://getartcraft.com/apps/photocraft
---
# 位图与图层班组（photocraft）

由 Craft 引擎驱动，通过 MCP 无头调用。

## MCP 工具速查

| 工具 | 用途 |
|------|------|
| `doc_new / doc_open / doc_save / doc_export` | 文档生命周期 |
| `doc_place / doc_select` | 素材置入与选择 |
| `doc_export_layers` | **按图层批量导出** |
| `doc_import_data_sets / doc_export_data_sets` | 数据集合成（批量套版） |
| `render_preview / ui_screenshot` | 渲染预览 |
| `jobs_list / jobs_cancel` | 后台任务管理 |

## 标准作业流程

1. `doc_open` + `doc_inspect` 先看清图层结构
2. 合成/修改用命令通道（`command_run` / `command_batch`）
3. 要拆图层就 `doc_export_layers`；要批量套版走 data sets
4. `render_preview` 确认后 `doc_save` / `doc_export`

## 硬规则

- 不覆盖原始 PSD，一律另存
- 大批量导出前先跑一张确认参数，再全量
- 图层命名混乱时先整理命名再导出，否则产物无法对号入座

## 路径注意

这些引擎是 Windows 可执行文件，**不认 WSL 的 `/mnt/c/...` 路径**，必须传 Windows 格式（如 `C:\\Users\\you\\out.png`）。从 WSL 调用时用 `wslpath -w <路径>` 转换，或直接用 Windows 绝对路径。
