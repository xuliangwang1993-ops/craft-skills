---
name: video-package
name_zh: 视频成片流水线
description: 把素材做成一支成片：剪辑编排 → 混音与响度归一 → 动效片头与特效 → 出预览与成片。当任务涉及短视频、宣传片、课程视频、成片交付时使用。
triggers: [剪辑, 成片, 宣传片, 短视频, 混音, 片头]
inputs:
  - name: task
    description: 任务描述与交付要求
    required: true
tools: []
mcp: [filmcraft, soundcraft, effectcraft]
permissions: [read_file, write_file]
version: 1
license: MIT
category: arts-design-media
kind: workflow
---
# 视频成片流水线

## 为什么要串起来

画面、声音、动效是三条独立产线，**手工合流最费时**，而且响度不统一是差评重灾区。

## 涉及引擎

- `filmcraft`
- `soundcraft`
- `effectcraft`

## 流水线

1. **FilmCraft `project_inspect` + `media_import`** —— 摸清工程并导入素材
2. **FilmCraft 编排时间线** —— 用 `command_run` / `command_batch` 剪接
3. **FilmCraft `render_frame` 抽帧** —— 抽关键帧验收画面
4. **SoundCraft `import_audio` + 编排** —— 配乐与音效编排
5. **SoundCraft `bounce_mix`** —— **混音导出**，注意目标响度标准
6. **EffectCraft `open_project` + `add_effect` + `add_keyframe`** —— 做片头动效
7. **EffectCraft `render_frame`** —— 逐帧渲染片头
8. **FilmCraft 合成 → `render_preview` → 出成片** —— 先低分辨率预览，确认后全量

## 坑点（踩过才写在这里）

- **响度标准**：播客 -16 LUFS / 流媒体 -14 LUFS / 广播 -23 LUFS，**不统一会被平台压**
- **先渲预览再全量**：视频渲染是按小时计的，参数错了血亏
- **声画同步校验**：混音后要回 FilmCraft 对齐，别默认时间轴一致
- **片头别太长**：短视频片头超 3 秒就掉完播率

## 路径注意

引擎是 Windows 可执行文件，**不认 WSL 的 `/mnt/c/...` 路径**，必须传 Windows 格式（`C:\\Users\\you\\out.pdf`）。从 WSL 调用时用 `wslpath -w <路径>` 转换。
