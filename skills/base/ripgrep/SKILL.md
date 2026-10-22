---
name: ripgrep
name_zh: 代码与文本搜索（ripgrep）
description: 用 ripgrep 开源工具完成「全文/代码搜索」。当任务需要 全文/代码搜索 且希望用开源、可独立运行的底层工具时使用。
triggers: [ripgrep, 全文/代码搜索]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: dev
layer: base
backs: 全文/代码搜索
wave: 1
stage: 入库
version: 1
license: MIT OR Unlicense
---

# ripgrep · 代码与文本搜索（ripgrep）

**它让我们能做什么：** 在海量文件里毫秒级定位文字，结果 JSON 可接 jq，给 AI 改代码、查卷宗定位。

## 定位

- 槽位：全文/代码搜索（一格一个最强工具，本格只放 ripgrep）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT OR Unlicense
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
sudo apt install ripgrep
```

## 核心用法

```
rg -n '违约金' docs/
rg --json 'TODO' src/ | jq -c 'select(.type=="match") | .data.path.text'
rg -l -t py 'import cv2'
```

## 输入/输出校验

- 先侦察输入，再处理。
- 退出码 0=有匹配、1=无匹配、2=出错，脚本中区分处理。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
