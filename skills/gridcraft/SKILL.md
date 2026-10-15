---
name: gridcraft
name_zh: 表格数据处理
description: 用 GridCraft 引擎读写电子表格：读取/写入区域、逐格赋值、求值公式、插图表、建表、排序筛选，并校验 XLSX 缓存值与往返保真。当任务涉及 .xlsx/.csv/.tsv 的读取、计算、生成或格式转换时使用。
triggers: [Excel, xlsx, 表格, 公式, 数据整理, CSV, 做表]
inputs:
  - name: file
    description: 目标表格路径（.xlsx/.csv/.tsv/.json/.html）
    required: false
tools: []
mcp: [gridcraft]
permissions: [read_file, write_file]
category: office-admin
version: 1
license: Proprietary
source: https://getartcraft.com/apps/gridcraft
---

# GridCraft 表格班组

GridCraft 提供 21 个 MCP 工具，覆盖表格读写与计算。

## MCP 工具速查

| 工具 | 用途 |
|------|------|
| `new_workbook` / `open_workbook` / `save_workbook` | 新建/打开/保存 |
| `inspect_workbook` | 侦察：工作表、已用区域、表格、图表、命名区域 |
| `read_range` / `write_range` | 区域读写 |
| `get_cell` / `set_cell` | 单格读写 |
| `evaluate_formula` | **公式求值**（不必开 Excel） |
| `insert_chart` / `create_table` / `sort_range` / `filter` | 图表、表格、排序、筛选 |
| `format_range` | 区域格式 |
| `execute_command` / `list_commands` | 底层命令通道 |

CLI 侧还有 `check`（**缓存值计算 oracle + XLSX 往返保真校验**，有差异即退出码 1）。

## 标准作业流程

1. `inspect_workbook` 先摸清结构
2. 读数据 `read_range`；算公式 `evaluate_formula`
3. 写结果 `write_range` / `set_cell`
4. `save_workbook` 落盘
5. 关键数据用 CLI `check` 做保真校验

## 硬规则

- 不覆盖原始表格，另存新文件。
- 公式与硬编码值必须区分清楚：能用公式就别写死数字。
- 财务/合同金额类数据，输出后必须回读校验一次。
