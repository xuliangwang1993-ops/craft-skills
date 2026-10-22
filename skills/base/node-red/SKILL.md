---
name: node-red
name_zh: 流程编排（Node-RED）
description: 用 Node-RED 开源工具完成「工作流编排」。当任务需要 工作流编排 且希望用开源、可独立运行、可商用的底层工具时使用。
triggers: [node-red, 工作流编排, 自动化]
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
license: "Apache-2.0（OpenJS Foundation）"
---

# node-red · 流程编排（Node-RED）

**它让我们能做什么：** 把各工具 CLI/HTTP 串成定时/触发式流水线，浏览器里拖拽连线，流程存成 JSON 可进仓库版本管理。

## 定位

- 槽位：工作流编排（一格一个最强工具，本格只放 node-red）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0（OpenJS Foundation）
- 阶段：入库（文档已写，尚未落地验证）
- 2026-10-22 替换上任工具（许可证问题），见 docs/扩库立项.md

## 安装

```sh
docker run -d -p 1880:1880 -v $PWD/node-red:/data --name nodered nodered/node-red
# 或 npm install -g --unsafe-perm node-red
```

## 核心用法

```
node-red -u ./data flows.json          # 启动并加载流程
curl -X POST http://127.0.0.1:1880/flows -H "Content-Type: application/json" -d @flows.json   # 部署流程（Admin API）
# exec 节点调用 ffmpeg/whisper 等 CLI；http in 节点暴露触发接口
```

## 输入/输出（串联）

- 输入 flows.json + 触发（HTTP/定时/文件）→ 调用各工具 CLI/HTTP，输出由节点决定（JSON 为主）。发外部消息的节点须人工确认。

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
