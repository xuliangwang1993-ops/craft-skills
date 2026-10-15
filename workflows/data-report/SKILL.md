---
name: data-report
name_zh: 数据报告流水线
description: 把一份数据表做成正式报告：读取与校验数据 → 计算与出图表 → 撰写报告正文 → 搭配封面成图。当任务涉及数据分析报告、尽调材料、经营报表、财务分析交付时使用。
triggers: [数据报告, 分析报告, 尽调, 经营报表, 财务分析, 出报告]
inputs:
  - name: task
    description: 任务描述与交付要求
    required: true
tools: []
mcp: [gridcraft, wordcraft, designcraft]
permissions: [read_file, write_file]
version: 1
license: MIT
category: office-admin
kind: workflow
---
# 数据报告流水线

## 为什么要串起来

数据在表格里、论述在文档里、门面在版面里——**三件事分属三个引擎，手工做要来回倒腾三次**。

## 涉及引擎

- `gridcraft`
- `wordcraft`
- `designcraft`

## 流水线

1. **GridCraft `inspect_workbook` + `read_range`** —— 先看清工作表、区域、公式与图表结构
2. **GridCraft `evaluate_formula`** —— **不开 Excel 也能算公式**，用于交叉验证
3. **GridCraft `insert_chart` / `create_table`** —— 生成报告要用的图表
4. **GridCraft `save_workbook` + CLI `check`** —— 保存后跑 `check` 做**缓存值保真校验**（有差异退出码 1）
5. **WordCraft `new_document`（sample: report）** —— 用内置报告模板起稿
6. **WordCraft 写入正文与表格** —— `type_text` 灌正文，`insert.table` 或粘贴数据
7. **DesignCraft `set_story_text` + `place_image`** —— 做封面成图
8. **WordCraft `save_document` → pdf** —— 导出最终报告

## 坑点（踩过才写在这里）

- **公式与硬编码要分清**：能用公式就别写死数字，否则数据一改报告就错
- **出报告前必跑 `check`**：XLSX 的缓存值与实际计算可能不一致，肉眼看不出来
- **图表别截屏贴图**：用 `insert_chart` 生成真的图表对象，对方还能改
- **封面尺寸**：DesignCraft 建版前先确认交付介质（A4 打印 / 屏幕 16:9）

## 路径注意

引擎是 Windows 可执行文件，**不认 WSL 的 `/mnt/c/...` 路径**，必须传 Windows 格式（`C:\\Users\\you\\out.pdf`）。从 WSL 调用时用 `wslpath -w <路径>` 转换。
