---
name: meilisearch
name_zh: 全文检索引擎（Meilisearch）
description: 用 meilisearch 开源工具完成「全文检索引擎」。当任务需要 全文检索引擎 且希望用开源、可独立运行的底层工具时使用。
triggers: [meilisearch, 全文检索引擎]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: data
layer: base
backs: 全文检索引擎
wave: 2
stage: 入库
version: 1
license: "MIT（社区版；部分企业功能为商业许可）"
---

# meilisearch · 全文检索引擎（Meilisearch）

**它让我们能做什么：** 秒级模糊/拼写容错搜索，给知识库、素材库、站内搜索用。

## 定位

- 槽位：全文检索引擎（一格一个最强工具，本格只放 meilisearch）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT（社区版；部分企业功能为商业许可）
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
docker run -d -p 7700:7700 -e MEILI_MASTER_KEY=$MEILI_KEY -v $PWD/meili:/meili_data getmeili/meilisearch
```

## 核心用法

```
curl -X POST 'http://localhost:7700/indexes/docs/documents' -H "Authorization: Bearer $MEILI_KEY" -H 'Content-Type: application/json' --data-binary @docs.json
curl 'http://localhost:7700/indexes/docs/search?q=报销' -H "Authorization: Bearer $MEILI_KEY"
```

## 输入/输出（串联）

- 输入 JSON 文档数组（jq / crawl4ai 产出）→ 输出 JSON 命中结果，接 jq。与 qdrant 互补：一个关键词，一个语义。

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
