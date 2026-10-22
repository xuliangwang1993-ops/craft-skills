---
name: duckdb
name_zh: 嵌入式分析（DuckDB）
description: 用 duckdb 开源工具完成「数据分析/SQL on 文件」。当任务需要 数据分析/SQL on 文件 且希望用开源、可独立运行的底层工具时使用。
triggers: [duckdb, 数据分析/SQL on 文件]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: data
layer: base
backs: 数据分析/SQL on 文件
wave: 1
stage: 入库
version: 1
license: MIT
---

# duckdb · 嵌入式分析（DuckDB）

**它让我们能做什么：** 直接对 CSV/Parquet/Excel/Postgres 跑 SQL，秒出统计结果，交给 gridcraft/openpyxl 出报表。

## 定位

- 槽位：数据分析/SQL on 文件（一格一个最强工具，本格只放 duckdb）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
pip install duckdb  # 或下载 duckdb CLI
```

## 核心用法

```
duckdb -c "SELECT region, sum(amount) FROM 'sales.csv' GROUP BY 1 ORDER BY 2 DESC"
duckdb -c "COPY (SELECT * FROM 'a.csv') TO 'a.parquet' (FORMAT parquet)"
```

## 输入/输出校验

- 先侦察输入，再处理。
- 结果行数/合计与源数据抽样对账；输出 parquet 可被 `duckdb -c "DESCRIBE 'a.parquet'"` 读回。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
