---
name: satori
name_zh: HTML/CSS 转 SVG（Satori）
description: 用 satori 开源工具Vercel 出品，把 JSX/HTML+CSS 转成 SVG，常配 resvg 出封面。当任务需要 HTML/CSS 转 SVG 且希望用开源、可独立运行的底层工具（designcraft / figcraft 补位）时使用。
triggers: [satori, HTML/CSS 转 SVG]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: layout
layer: base
backs: designcraft / figcraft 补位
version: 1
license: MPL-2.0
---

# satori · HTML/CSS 转 SVG（Satori）

**它让我们能做什么：** 封面：模板化封面/社媒图。

Vercel 出品，把 JSX/HTML+CSS 转成 SVG，常配 resvg 出封面。

## 定位

- 槽位：designcraft / figcraft 补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：MPL-2.0
- 无界面/命令行：是
- GPU：不需要
- 官方：https://github.com/vercel/satori

## 安装

```sh
npm install satori
```

## 核心用法

```
node -e "require('satori').default({type:'div',props:{children:'Hi',style:{fontSize:64}}},{width:1080,height:1920,fonts:[{name:'F',data:require('fs').readFileSync('font.ttf')}]}).then(s=>require('fs').writeFileSync('c.svg',s))"
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
