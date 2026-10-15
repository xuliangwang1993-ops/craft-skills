---
name: deckcraft
name_zh: 演示文稿
description: 用 DeckCraft 引擎制作演示文稿：新建/打开幻灯片、增删页、加形状与文本框、插入图片/表格/图表、渲染导出。当任务涉及 PPT/演示稿/路演材料/汇报幻灯片的制作或修改时使用。
triggers: [PPT, 演示文稿, 幻灯片, 路演, 汇报材料, slides, deck]
inputs:
  - name: task
    description: 任务描述与交付要求
    required: true
tools: []
mcp: [deckcraft]
permissions: [read_file, write_file]
version: 1
license: Proprietary
category: office-admin
source: https://getartcraft.com/apps/deckcraft
---
# 演示文稿班组（deckcraft）

由 Craft 引擎驱动，通过 MCP 无头调用。

## MCP 工具速查

| 工具 | 用途 |
|------|------|
| `new_presentation / open_presentation / save_presentation` | 演示文稿生命周期 |
| `add_slide / go_to_slide / inspect_slide` | 页面增删与检查 |
| `add_shape / add_text_box / set_text` | 形状与文字 |
| `insert_picture / insert_table / insert_chart` | 图表素材插入 |
| `render_slide / export` | 整页渲染与导出 |
| `run_command / batch / list_commands` | 底层命令通道 |

## 标准作业流程

1. 先问清页数、主题、受众，再动手
2. `new_presentation` 建稿（或用 `open_presentation` 接现有稿）
3. 逐页 `add_slide` + `add_text_box`/`add_shape` 铺内容
4. 数据类内容用 `insert_chart`，别贴图片
5. `render_slide` 目视检查每一页，`export` 交付

## 硬规则

- 交付前渲染至少一遍，确认没有文字溢出、元素越界
- 用户给的主色/字体必须沿用，不得自行替换
- 涉及商标、肖像、版权素材，先确认用户有使用权

## 路径注意

这些引擎是 Windows 可执行文件，**不认 WSL 的 `/mnt/c/...` 路径**，必须传 Windows 格式（如 `C:\\Users\\you\\out.png`）。从 WSL 调用时用 `wslpath -w <路径>` 转换，或直接用 Windows 绝对路径。
