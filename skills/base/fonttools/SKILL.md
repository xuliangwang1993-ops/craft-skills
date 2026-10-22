---
name: fonttools
name_zh: 字体子集/处理（fontTools）
description: 用 fonttools 开源工具完成「字体子集/处理」。当任务需要 字体子集/处理 且希望用开源、可独立运行的底层工具时使用。
triggers: [fonttools, 字体子集/处理]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: design
layer: base
backs: 字体子集/处理
wave: 2
stage: 入库
version: 1
license: "MIT"
---

# fonttools · 字体子集/处理（fontTools）

**它让我们能做什么：** 中文字体按用字裁子集（几 MB→几十 KB），转 woff2，查字形。

## 定位

- 槽位：字体子集/处理（一格一个最强工具，本格只放 fonttools）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
pip install fonttools brotli
```

## 核心用法

```
pyftsubset NotoSansSC.otf --text-file=used.txt --flavor=woff2 --output-file=sub.woff2
ttx -t name font.ttf
```

## 输入/输出（串联）

- 输入 ttf/otf + 用字文本 → 输出 woff2/ttf/ttx(xml)，接网页 / inkscape / designcraft。注意字体本身许可。

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
