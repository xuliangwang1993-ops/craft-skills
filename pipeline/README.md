# pipeline — 一句话需求 → 可交付宣传短视频

八个站点串成一条链：**上一站的产出文件就是下一站的输入**，每站都写
`handoff.json`（输入/输出 sha256 + Schema + 工具版本 + 耗时 + 退出码）、`qa.json`（指标/阈值/实测）、
`scorecard.json`（商业价值 / 衔接 / 工艺 / 标杆）。任何一站不合规就**非 0 退出并停链**。

```
make run SENTENCE="给悉尼小锅米线（Slurp Slurp Noodle）做一支 30 秒宣传短视频，配中英字幕和三个社媒尺寸"
```

## 站点

| # | 站 | 主要工具 | 产出 |
|---|---|---|---|
| 0 | 需求解析 | jq | `brief.json` |
| 1 | 素材采集 | curl + opencv + ffprobe | `facts.json`、`media_manifest.json`、`licenses.json`、`shot_request.md` |
| 2 | 脚本/分镜 | python（+ PIL 排版） | `menu.json`、`script.json`、`storyboard.pdf` |
| 3 | 切镜/调色/清音/响度 | pyscenedetect、melt、ffmpeg、sox | `clips/*.mp4`、`timeline.mlt`、`rough_9x16.mp4`、`audio/mix.wav`、`grade.json` |
| 4 | 字幕 | 双语脚本 + PIL 字幕板 | `zh.srt`、`en.srt`、`overlays/<aspect>/*.png`、`review.json` |
| 5 | 合成 | ffmpeg（loudnorm 两遍法） | `promo_9x16/1x1/16x9.mp4`、`cover_*.jpg` |
| 6 | 后测 | ffmpeg ebur128、PIL 安全区、`qa/trace_check.py` | `decode.json`、`loudness.json`、`cer.json`、`safe_area/*.png`、`trace.json` |
| 7 | 客服 | 知识包 + workbench 卡片 | `customer/kb/*.md`、`kb_manifest.json`、`project_delivery.json` |

## 数据流硬规定

`qa/trace_check.py` 把成片倒着查一遍：

```
字幕行 → script.json 的镜头 → asset_id → fact source_id → facts.json 的 status
```

- 画面/字幕里出现的店名、电话、价格、地址、营业时间，必须能在 `facts.json`（status=verified）
  或 `menu.json`（status=verified 且 in_video）找到同值；
- 未核实/冲突项（中文店名、地址、营业时间、招牌菜、价格）**在第 2 站就被拦住**，不会进渲染；
- 交付 srt 与脚本逐行比对，任何漂移都算不一致。

## 环境变量

见 `.env.example`。没有密钥；workbench 导入的 key 只从环境变量读。

## 已知环境限制（会影响工具选择）

1. **两套 ffmpeg**：`/opt/ffmpeg/bin/ffmpeg`（Alpine 6.1.2，有 libx264/libass）与 `/usr/bin/ffmpeg`
   （iOS 版，只有 VideoToolbox，且被 kill 后会把整个 App 锁住，需重启）。流水线默认用前者。
2. **swscale 宽度必须是 16 的倍数**：1080 宽在本机静默产出 0 字节，1088 正常 ——
   melt 和 `scale` 都踩这个坑，所以内部一律 1088 再裁到 1080。
3. **无 torch**：whisper / funasr / demucs / argos-translate 全部装不上（musllinux-aarch64 无轮子）。
4. **4 GB 内存**：并发渲染会 OOM，全部串行。

## 目录

```
pipeline/
  run_all.py            统一入口（make run 调它）
  make_schemas.py       schemas/*.schema.json 的唯一来源
  verify_tools.py       跑 ⚠️ 工具并写 reports/tool_verification.json
  report.py             汇总评分卡与缺口清单
  stations/s0*.py       八个站点
  lib/common.py         handoff/qa/scorecard/Schema 校验
  lib/frames.py         PIL 逐帧运动+调色（比 ffmpeg zoompan 快 ~3 倍）
  lib/audio.py          原创配乐合成（numpy，固定 seed，CC0）
  lib/plates.py         占位画面（PIL 代码绘制，无 AI 生图）
qa/trace_check.py       事实溯源门禁
tests/fail_drill.py     人为制造失败，证明下游会停
```
