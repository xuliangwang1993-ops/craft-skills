---
name: wan2
name_zh: AI 视频生成（Wan2.2）
description: 用 wan2 开源工具阿里通义万相开源文生视频/图生视频模型。当任务需要 AI 视频生成 且希望用开源、可独立运行的底层工具（effectcraft / filmcraft 空镜补位）时使用。
triggers: [wan2, AI 视频生成]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: ai-video
layer: base
backs: effectcraft / filmcraft 空镜补位
version: 1
license: Apache-2.0
---

# wan2 · AI 视频生成（Wan2.2）

**它让我们能做什么：** AI 视频：补空镜（不得替代客户真实素材）。

阿里通义万相开源文生视频/图生视频模型。

## 定位

- 槽位：effectcraft / filmcraft 空镜补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0
- 无界面/命令行：是
- GPU：需要（大显存，见仓库说明）
- 官方：https://github.com/Wan-Video/Wan2.2

## 安装

```sh
git clone https://github.com/Wan-Video/Wan2.2 && cd Wan2.2 && pip install -r requirements.txt
```

## 核心用法

```
python generate.py --task ti2v-5B --size 1280*704 --ckpt_dir ./Wan2.2-TI2V-5B --prompt '...'
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
