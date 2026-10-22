# pipeline · 一句话需求 → 十站交付

```
make run SENTENCE="给我家 Airbnb 做全套上架包"
```

## 契约

- 每站一个 `sN_*.py`，读上游产物、写 `NN_<站>/`，必产 `handoff.json` / `qa.json`。
- **输入必须来自上游站的 handoff**：`Station.require_upstream()` 会核对 sha256，
  文件被改过就停（`lib.py`）。
- 结构化产物都有 `schemas/*.schema.json`，下一站开工先校验；不合规立即非 0 退出。
- 事实只有四种状态：`verified / unverified / conflict / pending_owner`。
  只有 `verified` 能进文案、站点、知识包（`qa/trace_check.py` 会查）。
- 任何一站抛错，`run_all.py` 立即停，不写半成品交接。

## 站与工具

| 站 | 工具 | 降级路径 |
|---|---|---|
| 00 brief | jq | — |
| 01 collect | curl + 内联 JSON | crawl4ai 不可用 |
| 02 pricing | sqlite3 | duckdb 不可用 |
| 03 photos | PIL + OpenCV | darktable 不可用 |
| 04 video | ffmpeg + sox | 本机 ffmpeg 锁死 → `FFMPEG_HOST` |
| 05 copy | python 模板 + 事实键 | argos 不可用 |
| 06 guide | weasyprint | typst |
| 07 site | 原生 HTML/CSS/JS | — |
| 08 qc | minis-browser-use + ffprobe + ebur128 | playwright / lighthouse 不可用 |
| 09 kb | python 生成 + 规则自测 | — |

## 检查

```
make audit     # secret_scan + trace_check + failtest + scorecard
make verify    # 记录 ⚠️ 工具的真实状态
```

`qa/trace_check.py`：文案里每个 `facts.<key>` 必须存在；「平台标为无」的事实不得被肯定式写出；
评分/评价数/人数必须与 facts 同值；verified 设施在站点与知识库的丢失率必须为 0。
`qa/secret_scan.py`：密码、门锁码、电话、API key；HTML 会先剥标签再扫一遍（防 `<span>` 穿越）。
