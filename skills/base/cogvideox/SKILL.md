---
name: cogvideox
name_zh: AI 视频生成（CogVideoX）
description: 用 cogvideox 开源工具智谱开源文生视频模型。⚠️ 5B 权重为自有许可，商用须登记。当任务需要 AI 视频生成 且希望用开源、可独立运行的底层工具（effectcraft / filmcraft 空镜补位）时使用。
triggers: [cogvideox, AI 视频生成]
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
license: ⚠️ 代码 Apache-2.0；2B 权重 Apache-2.0；5B 权重 CogVideoX License（商用须登记）
---

# cogvideox · AI 视频生成（CogVideoX）

**它让我们能做什么：** AI 视频：补空镜。

智谱开源文生视频模型。⚠️ 5B 权重为自有许可，商用须登记。

## 定位

- 槽位：effectcraft / filmcraft 空镜补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：⚠️ 代码 Apache-2.0；2B 权重 Apache-2.0；5B 权重 CogVideoX License（商用须登记）
- 无界面/命令行：是
- GPU：需要
- 官方：https://github.com/zai-org/CogVideo

## 安装

```sh
pip install diffusers transformers accelerate
```

## 核心用法

```
python -c "import torch;from diffusers import CogVideoXPipeline;from diffusers.utils import export_to_video;p=CogVideoXPipeline.from_pretrained('THUDM/CogVideoX-2b',torch_dtype=torch.float16).to('cuda');export_to_video(p('a bowl of noodle soup').frames[0],'out.mp4',fps=8)"
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
