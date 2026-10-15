---
name: filmcraft
name_zh: 视频剪辑
description: 用 FilmCraft 引擎处理视频项目：导入素材、编排时间线、渲染帧与预览。当任务涉及视频剪辑、序列编排、素材整理或视频预览渲染时使用。
triggers: [视频剪辑, 时间线, 序列, 渲染帧, 导入素材]
inputs:
  - name: task
    description: 任务描述与交付要求
    required: true
tools: []
mcp: [filmcraft]
permissions: [read_file, write_file]
version: 1
license: Proprietary
category: arts-design-media
source: https://getartcraft.com/apps/filmcraft
---
# 视频剪辑班组（filmcraft）

由 Craft 引擎驱动，通过 MCP 无头调用。

## MCP 工具速查

| 工具 | 用途 |
|------|------|
| `project_inspect / sequence_inspect` | 项目与序列侦察 |
| `media_import` | 素材导入 |
| `render_frame / render_preview` | 单帧渲染与预览 |
| `command_run / command_batch / list_commands` | 底层命令通道 |
| `ui_* 系列` | 桌面 GUI 控制（需应用在跑） |

## 标准作业流程

1. `project_inspect` 摸清项目结构，`sequence_inspect` 看时间线
2. `media_import` 导入素材
3. 用命令通道编排；`render_frame` 抽帧验效果
4. `render_preview` 出预览交付

## 硬规则

- 长视频渲染耗时，先出低分辨率预览确认再全量
- 不覆盖原始工程文件
- 素材版权与肖像先确认使用权

## 路径注意

这些引擎是 Windows 可执行文件，**不认 WSL 的 `/mnt/c/...` 路径**，必须传 Windows 格式（如 `C:\\Users\\you\\out.png`）。从 WSL 调用时用 `wslpath -w <路径>` 转换，或直接用 Windows 绝对路径。
