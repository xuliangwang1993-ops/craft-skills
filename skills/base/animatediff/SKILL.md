---
name: animatediff
name_zh: 动画化扩散（AnimateDiff）
description: 用 animatediff 开源工具给 Stable Diffusion 加运动模块生成短动画，常在 ComfyUI 内使用。当任务需要 动画化扩散 且希望用开源、可独立运行的底层工具（effectcraft 补位）时使用。
triggers: [animatediff, 动画化扩散]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: ai-video
layer: base
backs: effectcraft 补位
version: 1
license: Apache-2.0（SD 底模许可另计）
---

# animatediff · 动画化扩散（AnimateDiff）

**它让我们能做什么：** AI 视频：风格化短动画。

给 Stable Diffusion 加运动模块生成短动画，常在 ComfyUI 内使用。

## 定位

- 槽位：effectcraft 补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0（SD 底模许可另计）
- 无界面/命令行：是
- GPU：需要
- 官方：https://github.com/guoyww/AnimateDiff

## 安装

```sh
git clone https://github.com/guoyww/AnimateDiff && cd AnimateDiff && pip install -r requirements.txt
```

## 核心用法

```
python -m scripts.animate --config configs/prompts/1_animate/1_1_animate_RealisticVision.yaml
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
