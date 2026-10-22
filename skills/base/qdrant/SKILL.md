---
name: qdrant
name_zh: 向量检索（Qdrant）
description: 用 qdrant 开源工具完成「向量数据库/语义检索」。当任务需要 向量数据库/语义检索 且希望用开源、可独立运行的底层工具时使用。
triggers: [qdrant, 向量数据库/语义检索]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: data
layer: base
backs: 向量数据库/语义检索
wave: 1
stage: 入库
version: 1
license: Apache-2.0
---

# qdrant · 向量检索（Qdrant）

**它让我们能做什么：** 文档、案例、素材做成向量，语义检索找最相关片段，给大模型做知识库。

## 定位

- 槽位：向量数据库/语义检索（一格一个最强工具，本格只放 qdrant）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
docker run -d -p 6333:6333 -v $PWD/qdrant:/qdrant/storage qdrant/qdrant  # 客户端: pip install qdrant-client
```

## 核心用法

```
python - <<'P'
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
c=QdrantClient('localhost',port=6333)
c.recreate_collection('docs',vectors_config=VectorParams(size=4,distance=Distance.COSINE))
c.upsert('docs',[PointStruct(id=1,vector=[.1,.2,.3,.4],payload={'t':'a'})])
print(c.query_points('docs',query=[.1,.2,.3,.4],limit=1))
P
```

## 输入/输出校验

- 先侦察输入，再处理。
- `curl localhost:6333/collections/docs` 点数与写入一致；查询返回预期 payload。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
