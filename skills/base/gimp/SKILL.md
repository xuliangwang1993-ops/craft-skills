---
name: gimp
name_zh: GIMP 批处理
description: 用 gimp 开源工具GIMP 无界面批处理模式（Script-Fu / Python-Fu）。需要再包一层脚本才能稳定调用。当任务需要 GIMP 批处理 且希望用开源、可独立运行的底层工具（photocraft 补位）时使用。
triggers: [gimp, GIMP 批处理]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: image
layer: base
backs: photocraft 补位
version: 1
license: GPL-3.0
---

# gimp · GIMP 批处理

**它让我们能做什么：** 画面：复杂修图脚本化。

GIMP 无界面批处理模式（Script-Fu / Python-Fu）。需要再包一层脚本才能稳定调用。

## 定位

- 槽位：photocraft 补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：GPL-3.0
- 无界面/命令行：是（gimp -i -b）
- GPU：不需要
- 官方：https://www.gimp.org

## 安装

```sh
sudo apt install gimp
```

## 核心用法

```
gimp -i -b '(let* ((i (car (gimp-file-load RUN-NONINTERACTIVE "in.png" "in.png")))) (gimp-image-flatten i) (gimp-file-save RUN-NONINTERACTIVE i (car (gimp-image-get-active-drawable i)) "out.jpg" "out.jpg"))' -b '(gimp-quit 0)'   # GIMP 2.10 语法
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
