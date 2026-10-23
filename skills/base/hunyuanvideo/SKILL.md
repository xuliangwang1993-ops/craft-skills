---
name: hunyuanvideo
name_zh: AI 视频生成（HunyuanVideo）
description: 用 hunyuanvideo 开源工具腾讯混元开源文生视频大模型。⚠️ 自有许可，欧盟、英国、韩国不可用。当任务需要 AI 视频生成 且希望用开源、可独立运行的底层工具（effectcraft / filmcraft 空镜补位）时使用。
triggers: [hunyuanvideo, AI 视频生成]
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
license: ⚠️ Tencent Hunyuan Community License（排除欧盟/英国/韩国；超大规模用户需另授权）
---

# hunyuanvideo · AI 视频生成（HunyuanVideo）

**它让我们能做什么：** AI 视频：高质量空镜（注意地区限制）。

腾讯混元开源文生视频大模型。⚠️ 自有许可，欧盟、英国、韩国不可用。

## 定位

- 槽位：effectcraft / filmcraft 空镜补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：⚠️ Tencent Hunyuan Community License（排除欧盟/英国/韩国；超大规模用户需另授权）
- 无界面/命令行：是
- GPU：需要（大显存）
- 官方：https://github.com/Tencent-Hunyuan/HunyuanVideo

## 安装

```sh
git clone https://github.com/Tencent-Hunyuan/HunyuanVideo && cd HunyuanVideo && pip install -r requirements.txt
```

## 核心用法

```
python sample_video.py --video-size 720 1280 --video-length 129 --prompt '...' --save-path ./results
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 输出用 `ffprobe` / `identify` 核对时长、尺寸、编码；音频用 pyloudnorm 或 `ffmpeg -af ebur128` 核对响度。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
- 第 2 批入库，**未实测**：示例语法按官方文档整理，首次使用先跑通再进流水线。
