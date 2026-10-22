---
name: postgresql
name_zh: 关系数据库（PostgreSQL / psql）
description: 用 postgresql 开源工具完成「关系数据库」。当任务需要 关系数据库 且希望用开源、可独立运行的底层工具时使用。
triggers: [postgresql, 关系数据库]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: data
layer: base
backs: 关系数据库
wave: 1
stage: 入库
version: 1
license: PostgreSQL License（类 MIT）
---

# postgresql · 关系数据库（PostgreSQL / psql）

**它让我们能做什么：** 业务数据的权威存储，订单、客户、案件都落这里，供 DuckDB 分析、openpyxl 出表。

## 定位

- 槽位：关系数据库（一格一个最强工具，本格只放 postgresql）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：PostgreSQL License（类 MIT）
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
sudo apt install postgresql-client  # 服务端: postgresql 或 docker run postgres
```

## 核心用法

```
psql "$DATABASE_URL" -c '\dt'
psql "$DATABASE_URL" -c "\copy (SELECT * FROM orders) TO 'orders.csv' CSV HEADER"
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f migrate.sql
```

## 输入/输出校验

- 先侦察输入，再处理。
- `-v ON_ERROR_STOP=1` 下退出码为 0；导出 CSV 行数与 `SELECT count(*)` 一致。写操作先在事务里试跑。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
