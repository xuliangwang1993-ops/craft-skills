---
name: darktable-cli
name_zh: 照片批量调色（darktable）
description: 用 darktable-cli 开源工具专业 RAW 冲印软件；`darktable-cli` 无界面按 XMP 调色参数批量导出。当任务需要 照片批量调色（darktable） 且希望用开源、可独立运行的底层工具（lightcraft 开源替代）时使用。
triggers: [darktable-cli, 照片批量调色]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: photo
layer: base
backs: lightcraft 开源替代
version: 1
license: GPL-3.0
---

# darktable-cli · 照片批量调色（darktable）

**它让我们能做什么：** 调色：在 GUI 里调好一张生成 .xmp，再批量套到整组照片导出。

专业 RAW 冲印软件；`darktable-cli` 无界面按 XMP 调色参数批量导出。

## 定位

- 槽位：lightcraft 开源替代
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：GPL-3.0

## 安装

```sh
sudo apt install darktable  # macOS: brew install --cask darktable
```

## 核心用法

```
darktable-cli in.CR3 out.jpg --width 2048 --height 2048 --hq true
darktable-cli in.CR3 style.xmp out.jpg                      # 套用 XMP 参数
darktable-cli raws/ out/ --style "我的风格" --out-ext jpg     # 整目录套风格
darktable-cli in.NEF out.tif --core --conf plugins/imageio/format/tiff/bpp=16
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 核对输出张数 = 输入张数；`exiftool` 或 `identify` 检查尺寸；抽查肤色。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
