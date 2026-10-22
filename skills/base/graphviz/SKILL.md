---
name: graphviz
name_zh: 图表与流程图（Graphviz）
description: 用 graphviz 开源工具完成「流程图/关系图」。当任务需要 流程图/关系图 且希望用开源、可独立运行的底层工具时使用。
triggers: [graphviz, 流程图/关系图]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: diagram
layer: base
backs: 流程图/关系图
wave: 1
stage: 入库
version: 1
license: EPL-1.0
---

# graphviz · 图表与流程图（Graphviz）

**它让我们能做什么：** 文本描述直接生成流程图、组织图、依赖图，SVG 可进 Inkscape、PDF 可进 qpdf 合并。

## 定位

- 槽位：流程图/关系图（一格一个最强工具，本格只放 graphviz）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：EPL-1.0
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
sudo apt install graphviz
```

## 核心用法

```
dot -Tsvg flow.dot -o flow.svg
dot -Tpdf flow.dot -o flow.pdf
echo 'digraph{A->B->C}' | dot -Tpng -o abc.png
```

## 输入/输出校验

- 先侦察输入，再处理。
- 退出码 0 且无 warning；SVG 可被 Inkscape 打开导出。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
