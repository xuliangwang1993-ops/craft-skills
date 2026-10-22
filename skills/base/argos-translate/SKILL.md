---
name: argos-translate
name_zh: 离线翻译（Argos Translate）
description: 用 argos-translate 开源工具完成「机器翻译（离线）」。当任务需要 机器翻译（离线） 且希望用开源、可独立运行的底层工具时使用。
triggers: [argos-translate, 机器翻译（离线）]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: text
layer: base
backs: 机器翻译（离线）
wave: 1
stage: 入库
version: 1
license: MIT
---

# argos-translate · 离线翻译（Argos Translate）

**它让我们能做什么：** 离线多语种翻译，字幕、文档翻译不出机器，接 Whisper 字幕和 python-docx。

## 定位

- 槽位：机器翻译（离线）（一格一个最强工具，本格只放 argos-translate）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
pip install argostranslate
```

## 核心用法

```
argospm update && argospm install translate-en_zh
argos-translate --from en --to zh "Hello world"
```

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空；抽样人工核对术语。质量低于商用大模型，正式文书须人工复核。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
