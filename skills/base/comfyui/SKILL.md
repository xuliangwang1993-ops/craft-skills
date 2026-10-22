---
name: comfyui
name_zh: 本地图像生成（ComfyUI，需 GPU）
description: 用 comfyui 开源工具完成「AI 图像生成」。当任务需要 AI 图像生成 且希望用开源、可独立运行的底层工具时使用。
triggers: [comfyui, AI 图像生成]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: image
layer: base
backs: AI 图像生成
wave: 1
stage: 入库
version: 1
license: GPL-3.0（模型权重另见各自许可）
---

# comfyui · 本地图像生成（ComfyUI，需 GPU）

**它让我们能做什么：** 节点化工作流本地生成/重绘图像，工作流 JSON 固定即输出稳定。⚠️ 需要 NVIDIA GPU（≥8GB 显存）。

## 定位

- 槽位：AI 图像生成（一格一个最强工具，本格只放 comfyui）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：GPL-3.0（模型权重另见各自许可）
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
git clone https://github.com/comfyanonymous/ComfyUI && cd ComfyUI && pip install -r requirements.txt && python main.py --listen
```

## 核心用法

```
# 在 UI 中导出 API 格式工作流 workflow_api.json，然后提交：
curl -s -X POST http://127.0.0.1:8188/prompt -H 'Content-Type: application/json' -d "{\"prompt\": $(cat workflow_api.json)}"
curl -s http://127.0.0.1:8188/history | jq 'keys'
```

## 输入/输出校验

- 先侦察输入，再处理。
- `/history` 出现该 prompt_id 且 output 目录有图；固定 seed 复跑结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
