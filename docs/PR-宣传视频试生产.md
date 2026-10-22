# trial: 宣传视频试生产（一句话 → 三尺寸成片）

一句话需求跑通八站流水线：**给悉尼小锅米线（Slurp Slurp Noodle）做一支 30 秒宣传短视频，配中英字幕和三个社媒尺寸**。

> **不合并。** 这是一次试生产验收，用真实客户数据检验工具链的衔接、准确、完整与工艺。

## 跑出来的东西

| 产出 | 位置 |
|---|---|
| 三个成片（1080×1920 / 1080×1080 / 1920×1080，30.000s，-14.1 LUFS） | `runs/dev/05_compose/promo_*.mp4` |
| 三张封面 + 中英外挂字幕 | `runs/dev/05_compose/cover_*.jpg`、`zh.srt`、`en.srt` |
| 分镜脚本 PDF（8 页） | `runs/dev/02_script/storyboard.pdf` |
| 拍摄清单（发给店家） | `runs/dev/01_collect/shot_request.md` |
| 客服知识包（5 篇 / 22 条 FAQ） | `customer/kb/` |
| 评分卡 / 缺口 / 工具验证 / 失败演练 | `reports/` |
| 试生产报告 | `docs/宣传视频试生产报告.md` |

## 流水线

```
make run SENTENCE="给悉尼小锅米线（Slurp Slurp Noodle）做一支 30 秒宣传短视频，配中英字幕和三个社媒尺寸"
```

0 需求解析（jq）→ 1 素材采集（curl/opencv/ffprobe）→ 2 脚本分镜 → 3 切镜调色音频（melt/pyscenedetect/ffmpeg/sox）
→ 4 字幕 → 5 合成（loudnorm 两遍法）→ 6 后测（ebur128/安全区/trace）→ 7 客服知识包

每站写 `handoff.json`（输入输出 sha256 + Schema + 工具版本 + 耗时 + 退出码）、`qa.json`、`scorecard.json`；
下一站开工先校验上一站 Schema，不合规立即非 0 退出。

## 事实门禁

`qa/trace_check.py` 从成片倒查：

```
字幕行 → script.json 镜头 → asset_id → fact source_id → facts.json status
```

未核实/冲突的事实（中文店名、地址、营业时间、招牌菜、价格）**在第 2 站就被拦住**，永远进不了渲染。
交付 srt 与脚本逐行比对，漂移即报错。

## 失败演练（证明链会停）

`make fail-drill`：

- 字幕价格被改成 `A$12.50` → `unverified_price`，退出码 1
- 官网图 `permission=borrowed` + 空 license → 第 2 站 Schema 校验失败，退出码 1，下游全部不运行

证据：`reports/fail_drill.json`。

## 工具验证（本次运行实测）

✅ jq 1.7.1、pyscenedetect 0.7.2、ffmpeg 6.1.2、sox 14.4.2、opencv 4.10、melt 7.28、imagemagick 7.1.1
❌ argos-translate / librosa / crawl4ai / whisper / funasr / demucs / darktable（musllinux-aarch64 无轮子或 Alpine 无包）
⚠️ libvips 8.15.3 本机缺 jpeg/png 模块

明细：`reports/tool_verification.json`（含安装命令、示例命令、退出码、耗时、错误原文）。

## 已知限制（会影响报价）

1. 内部画幅一律 1088 再裁 1080：本机 swscale/melt 对非 16 倍数的宽度静默产出 0 字节
2. iOS ffmpeg 只有 VideoToolbox 且会自锁；流水线默认用 Alpine 版 libx264
3. 4 GB 内存，渲染串行；本机一支 30s × 三尺寸约 75 分钟
4. 无 TTS / 无 ASR / 无机器翻译：本片无口播，字幕走双语脚本 + 逐行核对

## 不改的东西

- 没有改动 `skills/`、`workflows/`、`docs/扩库立项.md` 里的任何既有文件
- 没有碰 x-connect.ai、Wix、Cloudflare；没有动任何 Render 服务
- 没有密钥；`.env.example` 只有占位符
