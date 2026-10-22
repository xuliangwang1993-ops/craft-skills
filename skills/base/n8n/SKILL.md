---
name: n8n
name_zh: 工作流编排（n8n）
description: 用 n8n 开源工具完成「工作流编排」。当任务需要 工作流编排 且希望用开源、可独立运行的底层工具时使用。
triggers: [n8n, 工作流编排]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: automation
layer: base
backs: 工作流编排
wave: 2
stage: 入库
version: 1
license: "⚠️ Sustainable Use License（源码可见，非 OSI 开源；不得作为托管服务转售）"
---

# n8n · 工作流编排（n8n）

**它让我们能做什么：** 把各工具串成定时/触发式流水线，拖拽或 JSON 定义。

## 定位

- 槽位：工作流编排（一格一个最强工具，本格只放 n8n）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：⚠️ Sustainable Use License（源码可见，非 OSI 开源；不得作为托管服务转售）
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
docker run -d -p 5678:5678 -v $PWD/n8n:/home/node/.n8n docker.n8n.io/n8nio/n8n
```

## 核心用法

```
n8n import:workflow --input=flow.json
n8n execute --id <workflowId>
```

## 输入/输出（串联）

- 输入 workflow JSON → 调用各工具 CLI/HTTP，输出由节点决定（JSON 为主）。发外部消息的节点须人工确认。

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
