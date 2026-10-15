---
name: soundcraft
name_zh: 音频处理
description: 用 SoundCraft 引擎处理音频：新建/打开工程、导入音频、编排音轨、混音导出、格式与采样率转换、响度归一。当任务涉及音频剪辑、混音、格式转换、响度标准化时使用。
triggers: [音频, 混音, 音轨, 响度, 采样率, 转码, 播客]
inputs:
  - name: task
    description: 任务描述与交付要求
    required: true
tools: []
mcp: [soundcraft]
permissions: [read_file, write_file]
version: 1
license: Proprietary
category: arts-design-media
source: https://getartcraft.com/apps/soundcraft
---
# 音频处理班组（soundcraft）

由 Craft 引擎驱动，通过 MCP 无头调用。

## MCP 工具速查

| 工具 | 用途 |
|------|------|
| `new_session / open_session / save_session` | 工程生命周期 |
| `import_audio` | 导入音频 |
| `bounce_mix` | **混音导出** |
| `execute / batch / list_commands` | 底层命令通道 |
| `inspect_session` | 工程侦察 |

## 标准作业流程

1. `inspect_session` 或 `open_session` 摸清现状
2. `import_audio` 导入素材，用命令通道编排
3. `bounce_mix` 导出；需要转格式就用 CLI 的 `convert`

## 硬规则

- 交付前确认目标响度标准（播客 -16 LUFS / 音乐 -14 LUFS / 广播 -23 LUFS）
- 不覆盖原始音频，另存新文件
- 采样率与位深按交付平台定，不要盲目升采样

## 路径注意

这些引擎是 Windows 可执行文件，**不认 WSL 的 `/mnt/c/...` 路径**，必须传 Windows 格式（如 `C:\\Users\\you\\out.png`）。从 WSL 调用时用 `wslpath -w <路径>` 转换，或直接用 Windows 绝对路径。
