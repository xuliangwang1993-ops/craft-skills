---
name: effectcraft
name_zh: 动效合成
description: 用 EffectCraft 引擎做动效与合成：读写合成与图层、查询与设置属性、加关键帧与特效、渲染帧。当任务涉及动效、合成、特效、关键帧动画或逐帧渲染时使用。
triggers: [动效, 合成, 特效, 关键帧, 动画, After Effects]
inputs:
  - name: task
    description: 任务描述与交付要求
    required: true
tools: []
mcp: [effectcraft]
permissions: [read_file, write_file]
version: 1
license: Proprietary
category: arts-design-media
source: https://getartcraft.com/apps/effectcraft
---
# 动效合成班组（effectcraft）

由 Craft 引擎驱动，通过 MCP 无头调用。

## MCP 工具速查

| 工具 | 用途 |
|------|------|
| `open_project / save_project / get_project` | 工程生命周期 |
| `get_comp / get_layer / get_property / set_property` | **合成与图层属性读写** |
| `add_keyframe` | **关键帧动画** |
| `add_effect / list_effects` | 特效挂载 |
| `render_frame` | 逐帧渲染 |
| `run_script / execute_command / batch` | 脚本与批量执行 |
| `undo / redo / history` | 撤销与历史 |

## 标准作业流程

1. `get_project` → `get_comp` → `get_layer` 逐层摸清结构
2. `get_property` 读现值，`set_property` 改值
3. 动画用 `add_keyframe`，特效用 `add_effect`
4. `render_frame` 抽帧验收，最后 `save_project`

## 硬规则

- 动效参数改动前先 `history` 或记下原值，便于回滚
- 关键帧要连成合理缓动，别留线性跳变
- 渲染帧数多时先渲关键帧验收，再全量

## 路径注意

这些引擎是 Windows 可执行文件，**不认 WSL 的 `/mnt/c/...` 路径**，必须传 Windows 格式（如 `C:\\Users\\you\\out.png`）。从 WSL 调用时用 `wslpath -w <路径>` 转换，或直接用 Windows 绝对路径。
