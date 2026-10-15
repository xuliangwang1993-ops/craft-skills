---
name: deck-builder
name_zh: 路演稿流水线
description: 把数据做成一套演示稿：数据整理与图表 → 建稿分页 → 铺内容与配图 → 渲染校验 → 导出交付。当任务涉及路演、汇报、销售演示、项目提案的演示文稿制作时使用。
triggers: [路演, 汇报幻灯, 演示稿, 提案, pitch deck, PPT]
inputs:
  - name: task
    description: 任务描述与交付要求
    required: true
tools: []
mcp: [gridcraft, deckcraft, designcraft]
permissions: [read_file, write_file]
version: 1
license: MIT
category: office-admin
kind: workflow
---
# 路演稿流水线

## 为什么要串起来

数据在表格、封面在版面、正文在幻灯——**手工三头倒腾，最容易出的错是数据过期**（图改了数没改）。

## 涉及引擎

- `gridcraft`
- `deckcraft`
- `designcraft`

## 流水线

1. **GridCraft `read_range` + `evaluate_formula`** —— 拿到要展示的数字，先算准
2. **GridCraft `insert_chart` → 导出图表** —— 生成图表素材
3. **DeckCraft `new_presentation`** —— 建稿
4. **DeckCraft `add_slide` × N** —— 按叙事顺序分页
5. **DeckCraft `add_text_box` / `insert_picture` / `insert_chart`** —— 铺内容
6. **DesignCraft → 封面** —— 需要设计感强的封面时用 DesignCraft 出图再 `insert_picture` 贴回
7. **DeckCraft `render_slide`（逐页）** —— **每页都渲染验收**，确认没溢出、没压字
8. **DeckCraft `export`** —— 导出 pptx / pdf

## 坑点（踩过才写在这里）

- **每页都要 `render_slide`**：幻灯片最容易出文字溢框和元素越界，静态看不出
- **数据要标来源与日期**：路演稿的数字没有出处，对方会追问
- **图表用对象不用截图**：截图在对方修改时就成了死图
- **页数控制**：投资类路演通常 10-12 页，超过就砍

## 路径注意

引擎是 Windows 可执行文件，**不认 WSL 的 `/mnt/c/...` 路径**，必须传 Windows 格式（`C:\\Users\\you\\out.pdf`）。从 WSL 调用时用 `wslpath -w <路径>` 转换。
