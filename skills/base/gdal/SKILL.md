---
name: gdal
name_zh: 地图与地理数据（GDAL/OGR）
description: 用 gdal 开源工具完成「GIS/地理数据」。当任务需要 GIS/地理数据 且希望用开源、可独立运行的底层工具时使用。
triggers: [gdal, GIS/地理数据]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: gis
layer: base
backs: GIS/地理数据
wave: 1
stage: 入库
version: 1
license: MIT
---

# gdal · 地图与地理数据（GDAL/OGR）

**它让我们能做什么：** 任意地理格式互转、投影变换、裁切，输出 GeoJSON/GeoTIFF 给地图和报告使用。

## 定位

- 槽位：GIS/地理数据（一格一个最强工具，本格只放 gdal）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MIT
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
sudo apt install gdal-bin
```

## 核心用法

```
gdalinfo dem.tif
ogr2ogr -f GeoJSON out.geojson in.shp -t_srs EPSG:4326
gdalwarp -t_srs EPSG:3857 -cutline area.geojson -crop_to_cutline in.tif out.tif
```

## 输入/输出校验

- 先侦察输入，再处理。
- `gdalinfo`/`ogrinfo -so` 读回输出，核对坐标系与要素数。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
