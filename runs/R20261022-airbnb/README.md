# R20261022-airbnb · 交付索引

完整产物在本地；进 git 的只有文本、PDF、精修图与截图。**视频与站点大图不入库**（26 MB + 28 MB），
用 `make run` 可原样重放（同样的输入 → 同样的输出，随机种子固定）。

## 未入库的文件
| 文件 | 为什么 | 怎么拿回来 |
|---|---|---|
| `04_video/*.mp4` | 26 MB，二进制不可 diff | `make run`（本机 ffmpeg 不可用时走 `FFMPEG_HOST`） |
| `07_site/site/assets/img/*` | 由 `03_photos` 自动派生 | `python3 pipeline/s7_site.py` |
| `01_collect/raw/listing.html` | 平台页面原文，含第三方 key，不入库 | `python3 pipeline/s1_collect.py` 重抓（遵守 3s 间隔） |

每个文件的 sha256 都在对应站的 `handoff.json` 里，重建后可核对。

## 先看这几份
1. `reports/scorecard.md` — 十站评分
2. `reports/failtest.json` — 故意写坏两处，证明闸门有效
3. `03_photos/photos/order.json` — 排序与中英图注
4. `05_copy/listing_copy/zh.md` — 可直接粘贴的文案
5. `07_site/site/index.html` — 直订站
