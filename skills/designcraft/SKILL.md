---
name: designcraft
name_zh: 版面设计
description: 用 DesignCraft 引擎做版面与视觉设计：新建文档、写入图文、放置图片、渲染页面、导出 PNG，支持脚本化批处理。当任务涉及海报、封面、宣传页、图文排版或设计稿导出时使用。
triggers: [海报, 封面, 排版, banner, 设计稿, 宣传页, 图文]
inputs:
  - name: brief
    description: 设计需求描述（尺寸、风格、必备元素）
    required: true
tools: []
mcp: [designcraft]
permissions: [read_file, write_file]
category: arts-design-media
version: 1
license: Proprietary
source: https://getartcraft.com/apps/designcraft
---

# DesignCraft 版面班组

DesignCraft 提供 25 个 MCP 工具，用于版面创作与导出。

## MCP 工具速查

| 工具 | 用途 |
|------|------|
| `new_document` / `open_document` / `save_document` | 文档生命周期 |
| `set_story_text` / `get_story` | 文本块读写 |
| `place_image` | 放图 |
| `render_page` / `export_png` | 渲染与导出 |
| `execute` / `batch` | 命令执行 |
| `inspect_document` | 结构侦察 |
| `list_commands` | 查全部可用命令 |
| `select_tool` / `pointer` / `click` / `drag` / `key` / `type_text` | 桌面 GUI 控制（需应用在跑） |

## 标准作业流程

1. 先明确尺寸、风格、必备元素，再动手
2. `new_document` 建版
3. `set_story_text` + `place_image` 铺内容
4. `render_page` 目视检查，不满意就改
5. `export_png` 交付

## 硬规则

- 交付前至少渲染一次确认版面没有溢出、错位、压字。
- 用户给的品牌色/字体必须沿用，不得自行替换。
- 涉及商标、肖像、版权素材，先确认用户有使用权。
