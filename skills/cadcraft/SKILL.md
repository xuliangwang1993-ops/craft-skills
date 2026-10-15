---
name: cadcraft
name_zh: 工程图纸
description: 用 CADCraft 引擎处理 CAD 图纸：读取与检查 DXF/DWG、查询图元、查找文字、执行命令与脚本、渲染导出为 SVG/PNG/PDF。当任务涉及工程图、建筑图、图纸转换或图元分析时使用。
triggers: [CAD, DXF, DWG, 工程图, 图纸, 建筑图]
inputs:
  - name: task
    description: 任务描述与交付要求
    required: true
tools: []
mcp: [cadcraft]
permissions: [read_file, write_file]
version: 1
license: Proprietary
category: arts-design-media
source: https://getartcraft.com/apps/cadcraft
---
# 工程图纸班组（cadcraft）

由 Craft 引擎驱动，通过 MCP 无头调用。

## MCP 工具速查

| 工具 | 用途 |
|------|------|
| `new_drawing / open / save` | 图纸生命周期 |
| `inspect_drawing / query_entities` | **结构侦察与图元查询** |
| `find_text` | **图纸内文字检索** |
| `render` | 渲染出图（SVG/PNG/PDF） |
| `execute / script / command_line / list_commands` | 命令与脚本通道 |

## 标准作业流程

1. `inspect_drawing` 摸清图层与范围，`query_entities` 定位目标图元
2. 需要找标注文字用 `find_text`
3. 改动用 `execute` 或 `script`
4. `render` 出图给对方看（PDF 给甲方，SVG 给后续编辑）

## 硬规则

- 不覆盖原始图纸，另存新文件
- 改图前先备份，CAD 图元关联复杂，误改难复原
- 单位与比例必须确认（mm / inch），别默认

## 路径注意

这些引擎是 Windows 可执行文件，**不认 WSL 的 `/mnt/c/...` 路径**，必须传 Windows 格式（如 `C:\\Users\\you\\out.png`）。从 WSL 调用时用 `wslpath -w <路径>` 转换，或直接用 Windows 绝对路径。
