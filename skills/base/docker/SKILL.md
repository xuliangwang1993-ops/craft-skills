---
name: docker
name_zh: 容器运行（Docker）
description: 用 docker 开源工具完成「容器/环境隔离」。当任务需要 容器/环境隔离 且希望用开源、可独立运行的底层工具时使用。
triggers: [docker, 容器/环境隔离]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: ops
layer: base
backs: 容器/环境隔离
wave: 1
stage: 入库
version: 1
license: Apache-2.0（Docker Engine / Moby）
---

# docker · 容器运行（Docker）

**它让我们能做什么：** 把 GPU 模型、服务（SearXNG、Qdrant、ComfyUI）装进隔离容器，环境可复现、输出稳定。

## 定位

- 槽位：容器/环境隔离（一格一个最强工具，本格只放 docker）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0（Docker Engine / Moby）
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
curl -fsSL https://get.docker.com | sh
```

## 核心用法

```
docker run --rm -v "$PWD":/w -w /w jrottenberg/ffmpeg -i in.mp4 out.webm
docker compose up -d
docker ps --format '{{.Names}} {{.Status}}'
```

## 输入/输出校验

- 先侦察输入，再处理。
- 容器退出码 0；服务类用健康检查或 curl 端口确认；固定镜像 tag 保证可复现。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
