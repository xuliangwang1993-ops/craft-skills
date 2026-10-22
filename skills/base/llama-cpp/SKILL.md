---
name: llama-cpp
name_zh: 本地大模型推理（llama.cpp）
description: 用 llama-cpp 开源工具完成「本地大模型推理」。当任务需要 本地大模型推理 且希望用开源、可独立运行的底层工具时使用。
triggers: [llama-cpp, 本地大模型推理]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: text
layer: base
backs: 本地大模型推理
wave: 2
stage: 入库
version: 1
license: "MIT（模型权重另见各自许可）"
---

# llama-cpp · 本地大模型推理（llama.cpp）

**它让我们能做什么：** 离线跑 GGUF 大模型，出机器不联网的摘要、改写、挑片段。

## 定位

- 槽位：本地大模型推理（一格一个最强工具，本格只放 llama-cpp）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT（模型权重另见各自许可）
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp && cmake -B build && cmake --build build -j
```

## 核心用法

```
./build/bin/llama-cli -m model.gguf -p "总结：..." -n 256 --seed 42
./build/bin/llama-server -m model.gguf --port 8081  # OpenAI 兼容接口
```

## 输入/输出（串联）

- 输入文本/提示 → 输出文本或 JSON（可用 --grammar / json schema 约束），接 jq / pandoc。

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
