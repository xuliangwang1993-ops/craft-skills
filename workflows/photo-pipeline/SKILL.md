---
name: photo-pipeline
name_zh: 批量调色出图
description: 把一堆原始照片整理成一组成品：图库导入与智能筛选 → 批量套预设调色 → 裁剪构图 → 分层或批量导出。当任务涉及婚礼照/活动照/产品图的批量处理或图库整理时使用。
triggers: [批量调色, 婚礼照, 活动照, 产品图, 图库整理, 批量出图]
inputs:
  - name: task
    description: 任务描述与交付要求
    required: true
tools: []
mcp: [lightcraft, photocraft]
permissions: [read_file, write_file]
version: 1
license: MIT
category: arts-design-media
kind: workflow
---
# 批量调色出图

## 为什么要串起来

LightCraft 管「批量决策」（330 个工具，能按条件筛图、套预设、批量显影），
PhotoCraft 管「精细加工」（图层、合成、按图层导出）。**前者做广度，后者做深度。**

## 涉及引擎

- `lightcraft`
- `photocraft`

## 流水线

1. **LightCraft `import`** —— 导入当天所有素材
2. **LightCraft `query_photos`** —— **按条件筛图**：曝光、时间、评分、颜色特征——先把废片剔掉
3. **LightCraft `select_photos` + `apply_preset`** —— 选中的批量套预设
4. **LightCraft `render_photo`（先渲 1-2 张）** —— **必须**先验收，风格不对就改预设，别全量跑
5. **LightCraft `export`** —— 确认风格后批量出图
6. **PhotoCraft `doc_open` → 合成/修图** —— 需要精修的少数几张拖进 PhotoCraft
7. **PhotoCraft `doc_export_layers`** —— 要交付分层 PSD 时按图层导出

## 坑点（踩过才写在这里）

- **批量前必须小样验收**：套错预设跑 500 张，返工比重做还慢
- **调色不破坏原片**：LightCraft 只写显影参数，原图永不动
- **交付格式按用途定**：网络用压缩 JPEG，打印用 TIFF/高质 JPEG
- **文件命名**：导出前先理清命名规则，否则成品几百张没法对号入座

## 路径注意

引擎是 Windows 可执行文件，**不认 WSL 的 `/mnt/c/...` 路径**，必须传 Windows 格式（`C:\\Users\\you\\out.pdf`）。从 WSL 调用时用 `wslpath -w <路径>` 转换。
