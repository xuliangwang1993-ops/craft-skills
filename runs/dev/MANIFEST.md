# runs/dev — 这一版跑的是什么

`run_id = dev`（示例跑批；正式跑批用 `make run SENTENCE="…"` 会自动用 UTC 时间戳做 run_id）。

| 项 | 值 |
|---|---|
| 需求句 | 给悉尼小锅米线（Slurp Slurp Noodle）做一支 30 秒宣传短视频，配中英字幕和三个社媒尺寸 |
| 时间 | 2026-10-22 17:0x → 2026-10-23 03:xx（Sydney），纯 CPU |
| 机器 | iPhone iSH / Alpine 3.21 / aarch64 / musl / 4 GB RAM |
| 站数 | 8 站全过（`run_manifest.json`） |

## 提交进仓库的内容

- 全部结构化产出：`brief.json`、`facts.json`、`media_manifest.json`、`licenses.json`、`menu.json`、
  `script.json`、`grade.json`、`review.json`、`trace.json`、`decode.json`、`loudness.json`、`cer.json`、
  `kb_manifest.json`、`project_delivery.json`
- 每站的 `handoff.json` / `qa.json` / `scorecard.json`
- 可交付物：三个成片（9:16 / 1:1 / 16:9）、三张封面、`zh.srt` / `en.srt`
- `storyboard.pdf`、`shot_request.md`、`safe_area/*.png`（安全区标注图）

## 故意没有提交的（体积）

| 路径 | 大小 | 为什么不提交 |
|---|---|---|
| `03_edit/clips/*.mp4` | ~23 MB | 中间镜头，可用 `make run` 重算（同一 seed + 同一 grade 表，逐字节一致） |
| `03_edit/rough_9x16.mp4` | ~37 MB | MLT 时间线渲染结果，同上 |
| `03_edit/audio/bed_raw.wav`、`bed.wav`、`mix.wav` | ~17 MB | numpy 合成，seed 固定，可重算 |

重算命令：

```sh
RUN_ID=dev make run SENTENCE="给悉尼小锅米线（Slurp Slurp Noodle）做一支 30 秒宣传短视频，配中英字幕和三个社媒尺寸"
```

（第 3 站带渲染缓存：`clips/<shot>.key` 记录 grade+motion+时长，key 不变就不重渲。）

## 一句实话

`05_compose/*.mp4` 里三个成片是**样片**：画面为代码绘制的占位板 + 官网未授权图，
带「样片 · 占位素材 · 未授权」水印。客户素材与书面授权到位后重跑，水印会自动去掉。
