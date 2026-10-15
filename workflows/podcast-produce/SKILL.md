---
name: podcast-produce
name_zh: 播客制作流水线
description: 做一期播客：音频导入与剪辑 → 降噪与响度归一 → 混音导出 → 同步产出节目文稿与时间轴。当任务涉及播客、访谈录音、有声内容制作时使用。
triggers: [播客, 访谈, 有声书, 降噪, 响度, 节目文稿]
inputs:
  - name: task
    description: 任务描述与交付要求
    required: true
tools: []
mcp: [soundcraft, wordcraft]
permissions: [read_file, write_file]
version: 1
license: MIT
category: arts-design-media
kind: workflow
---
# 播客制作流水线

## 为什么要串起来

播客不只是音频，**还要节目文稿、章节时间轴、Shownotes**——分开做要重复听好几遍。

## 涉及引擎

- `soundcraft`
- `wordcraft`

## 流水线

1. **SoundCraft `new_session` / `import_audio`** —— 建工程导素材
2. **SoundCraft 剪辑** —— 用 `execute` / `batch` 剪掉口误与空白
3. **SoundCraft 处理** —— 降噪、`normalize` 响度（播客标准 **-16 LUFS**）
4. **SoundCraft `bounce_mix`** —— 混音导出成 MP3/WAV
5. **WordCraft `new_document`** —— 起节目文稿
6. **WordCraft 写入文稿** —— 正文 + 章节时间轴 + Shownotes + 嘉宾信息
7. **WordCraft `save_document` → md/pdf** —— 导出发布用文稿

## 坑点（踩过才写在这里）

- **-16 LUFS 是播客标准**：不归一的话，听众切到下一期会被音量差吓一跳
- **章节标记**：发布平台的章节功能能大幅提升完播率，别忘打标记
- **备份原始录音**：所有编辑在副本上做，原轨永不动

## 路径注意

引擎是 Windows 可执行文件，**不认 WSL 的 `/mnt/c/...` 路径**，必须传 Windows 格式（`C:\\Users\\you\\out.pdf`）。从 WSL 调用时用 `wslpath -w <路径>` 转换。
