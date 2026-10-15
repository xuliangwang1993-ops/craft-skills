---
name: wordcraft
name_zh: Word 文档处理
description: 用 WordCraft 引擎读写与排版 Word 文档：新建/打开 docx，改写正文、套用样式、处理表格、审阅修订与批注、邮件合并、Zotero 引用，并导出 docx/pdf/odt/rtf/html/md/tex/txt/png。当任务涉及 .docx/.doc/.odt/.rtf 文档的生成、修改、格式转换或渲染预览时使用。
triggers: [Word 文档, docx, 合同, 报告, 公函, 起诉状, 修订痕迹, 批注, 格式转换]
inputs:
  - name: file
    description: 目标文档路径（.docx/.doc/.odt/.rtf/.md/.tex/.html/.txt）
    required: false
tools: []
mcp: [wordcraft]
permissions: [read_file, write_file, network]
category: office-admin
version: 1
license: Proprietary
source: https://getartcraft.com/apps/wordcraft
---

# WordCraft 文档班组

WordCraft 是一个可无头运行的 Word 处理器（617 条命令，MCP 接口 16 个工具）。

## MCP 工具速查

| 工具 | 用途 |
|------|------|
| `new_document` | 新建：`blank` / `sample` / `letter` / `resume` / `report` |
| `open_document` | 打开 docx/doc/odt/rtf/md/tex/html/txt/json |
| `type_text` | 在光标处输入（`\n` 换行，段落用 `text.newParagraph`） |
| `execute` | 执行单条命令，如 `{command:"format.bold"}` |
| `batch` | 顺序执行多条命令，遇错即停（可 `keepGoing`） |
| `select_text` | 选中第 n 次出现的文本 |
| `get_text` | 取正文纯文本 |
| `inspect_document` | 结构化 JSON：段落/样式/格式 run/列表/表格/节/选区/页数 |
| `render_page` | 渲染某页为 PNG 用于目视校验 |
| `save_document` | 保存，格式由扩展名决定（docx/pdf/odt/rtf/html/md/tex/txt/png） |
| `list_commands` | 查全部 617 条命令（含参数），用 `query` 过滤 |

## 标准作业流程

1. `open_document` 或 `new_document`
2. `inspect_document` 先看清结构，不要凭猜测改
3. 改动用 `execute` / `batch`；改文字用 `select_text` + `type_text`
4. `get_text` 或 `render_page` 验证结果
5. `save_document` 落盘

## 硬规则

- 改稿先备份原文件（另存 `*.bak.docx`），不得原地覆盖未备份的用户文档。
- 涉及「修订痕迹 / tracked changes」时用 `--author` 标明操作者，不得把修订和最终稿混为一谈。
- 邮件合并、批量套模板属于外发动作，**必须经用户确认后才执行**。
- 转换带批注的文档时，用 `convert --markup` 才能把批注与修订一并烧进 PDF。
