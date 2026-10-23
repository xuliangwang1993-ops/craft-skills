---
name: cc0-music-sources
name_zh: 免版权音乐来源（CC0 / 可商用）
description: 用 cc0-music-sources 清单为宣传短片挑选可确认免版权的背景音乐与音效，逐首核对许可并留证。当任务需要 免版权音乐 且希望用开源、可独立运行的底层素材来源（soundcraft 素材补位）时使用。
triggers: [cc0-music-sources, 免版权音乐, 背景音乐]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: audio
layer: base
backs: soundcraft 素材补位
version: 1
license: 各曲目许可不同，逐首核对
---

# cc0-music-sources · 免版权音乐来源（CC0 / 可商用）

**它让我们能做什么：** 素材：给宣传片配上可确认可商用的音乐/音效，补「模板与素材生态」缺口。

## 定位

- 槽位：soundcraft 素材补位
- 许可：**按曲目逐首核对**，优先 CC0，其次 CC-BY（需署名），**拒绝任何 NC（非商用）**

| 来源 | 许可情况 | 网址 |
|------|----------|------|
| Free Music Archive | 每首不同；筛 CC0 / CC-BY，避开 NC | https://freemusicarchive.org |
| Freesound | 每个文件不同（CC0 / CC-BY / ⚠️ CC-BY-NC）；筛 CC0 | https://freesound.org |
| ccMixter | 多为 CC-BY / ⚠️ CC-BY-NC，逐首看 | https://ccmixter.org |
| Pixabay Music | ⚠️ 非 CC0，是 Pixabay Content License：可免费商用，不可单独转售音乐 | https://pixabay.com/service/license-summary/ |
| YouTube 音频库 | ⚠️ 主要授权 YouTube 内使用，用于抖音/小红书等前逐首确认 | https://studio.youtube.com |

## 核心用法

```
# 1. 在来源站按许可筛选（Freesound: 搜索页 License = Creative Commons 0）
# 2. 下载后记录到 licenses.json：media_id / path / origin / license / 曲目页 URL / 下载日期 / 许可截图路径
# 3. 校验时长与响度
ffprobe -v error -show_entries format=duration -of csv=p=0 bgm.mp3
ffmpeg -i bgm.mp3 -af ebur128 -f null - 2>&1 | tail -12
```

## 输入/输出校验

- 每首曲目必须有曲目页 URL + 许可截图，否则 `deliverable_ok: false`。
- CC-BY 曲目把署名写进片尾或发布文案。

## 硬规则

- **确认不了许可就不用**，退回环境声。
- 不用含 NC / ND（需改编时）条款的曲目做商用交付。
- 许可证据与成片一起归档。
