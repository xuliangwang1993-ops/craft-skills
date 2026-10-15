---
name: legal-bundle
name_zh: 法律卷宗流水线
description: 把 Word 诉状/合同做成正式卷宗：起草改稿 → 导出带批注与修订痕迹的 PDF → 合并多份文书成卷 → 审计虚假遮盖。当任务涉及诉讼文书、合同定稿、卷宗整理或文件安全审查时使用。
triggers: [诉状, 卷宗, 合同定稿, 批注, 修订痕迹, 遮盖审计, 法律文书]
inputs:
  - name: task
    description: 任务描述与交付要求
    required: true
tools: []
mcp: [wordcraft, pdfcraft]
permissions: [read_file, write_file]
version: 1
license: MIT
category: legal
kind: workflow
---
# 法律卷宗流水线

## 为什么要串起来

单用 WordCraft 只能出稿，单用 PdfCraft 只能处理已有 PDF。
**串起来才能完成法律实务的完整闭环**：改稿 → 保留修订留痕 → 归档成册 → 检查有没有「假遮盖」。

## 涉及引擎

- `wordcraft`
- `pdfcraft`

## 流水线

1. **WordCraft `open_document` + `inspect_document`** —— 先摸清页数、段落、批注、修订状态，别凭猜改稿
2. **WordCraft 改稿** —— 用 `select_text` + `type_text` 精改；`execute` 跑 `format.*`、`para.*` 样式命令
3. **WordCraft `save_document`** —— 先存一份 `*-final.docx` 定稿
4. **`wordcraft-cli convert 定稿.docx 卷宗稿.pdf --markup`** —— **关键**：`--markup` 把批注与修订痕迹一并烧进 PDF，缺了它批注全丢
5. **PdfCraft `doc_list` + `doc_combine`** —— 多份文书合并成卷（起诉状 + 证据清单 + 附件）
6. **PdfCraft `audit`** —— **查虚假遮盖**：PDF 里常见的「黑框遮盖」其实文字还在底层，一复制就露馅
7. **PdfCraft `page_render` 抽页目视** —— 归档前肉眼过一遍排版

## 坑点（踩过才写在这里）

- **`--markup` 不能忘**：不带的转换会把批注和修订全部丢掉，等于白改
- **遮盖审计是刚需**：澳洲法院对「faux redaction」（假遮盖）零容忍，交卷前必须 `audit`
- **不覆盖原件**：所有产出另存，法律文书的版本链不能断
- **修订操作者要标明**：WordCraft 的 `--author` 参数决定修订和批注署谁的名
- **页眉页脚与页码**：合并后页码会重排，合并前先规划好分卷

## 路径注意

引擎是 Windows 可执行文件，**不认 WSL 的 `/mnt/c/...` 路径**，必须传 Windows 格式（`C:\\Users\\you\\out.pdf`）。从 WSL 调用时用 `wslpath -w <路径>` 转换。
