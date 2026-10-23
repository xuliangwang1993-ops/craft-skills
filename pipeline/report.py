#!/usr/bin/env python3
"""Aggregates every station scorecard into reports/scorecard.md + reports/gaps.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.common import read_json, write_json  # noqa: E402

DIMS = [("business", "商业价值", 0.35), ("handoff", "衔接", 0.25),
        ("craft", "工艺", 0.25), ("benchmark", "标杆", 0.15)]
NAMES = {
    "00_brief": "0 需求解析", "01_collect": "1 素材采集", "02_script": "2 脚本/分镜",
    "03_edit": "3 切镜/调色/音频", "04_subs": "4 字幕", "05_compose": "5 合成",
    "06_qa": "6 后测", "07_customer": "7 客服",
}


def main(run_id: str) -> int:
    run_dir = ROOT / "runs" / run_id
    rows, notes, missing = [], [], []
    for folder in NAMES:
        p = run_dir / folder / "scorecard.json"
        if not p.exists():
            missing.append(folder)
            continue
        card = read_json(p)
        qa = read_json(run_dir / folder / "qa.json") if (run_dir / folder / "qa.json").exists() else {}
        rows.append({"folder": folder, "name": NAMES[folder], "card": card, "qa": qa})
        notes.append((NAMES[folder], card.get("notes", [])))

    if not rows:
        print("no scorecards found", file=sys.stderr)
        return 1

    dim_avg = {}
    for key, _, _ in DIMS:
        vals = [r["card"]["scores"][key] for r in rows]
        dim_avg[key] = round(sum(vals) / len(vals), 2)
    overall = round(sum(dim_avg[k] * w for k, _, w in DIMS), 2)

    lines = [f"# 评分卡汇总 · run `{run_id}`", "",
             "权重：商业价值 35% · 衔接 25% · 工艺 25% · 标杆 15%", "",
             "| 站 | 商业价值 | 衔接 | 工艺 | 标杆 | 总分 | 阻断项 |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        s = r["card"]["scores"]
        failed = r["qa"].get("blocking_failures", [])
        lines.append(f"| {r['name']} | {s['business']} | {s['handoff']} | {s['craft']} | "
                     f"{s['benchmark']} | **{r['card']['total']}** | "
                     f"{', '.join(failed) if failed else '—'} |")
    lines += ["", f"**维度均值**：商业价值 {dim_avg['business']} · 衔接 {dim_avg['handoff']} · "
                  f"工艺 {dim_avg['craft']} · 标杆 {dim_avg['benchmark']}", "",
              f"**总分：{overall} / 5**", "", "## 各站扣分理由", ""]
    for name, ns in notes:
        lines.append(f"### {name}")
        lines += [f"- {n}" for n in ns] or ["- （未写）"]
        lines.append("")
    if missing:
        lines += ["## 缺失站点", "", "未产出 scorecard：" + ", ".join(missing), ""]

    (ROOT / "reports/scorecard.md").write_text("\n".join(lines), encoding="utf-8")

    gaps = {
        "run_id": run_id,
        "product_gaps": [
            {"gap": "TTS 配音", "why": "cosyvoice 被任务书禁用，其余开源 TTS 未入库", "impact": "本片无口播，只有配乐与字幕"},
            {"gap": "自动配乐/素材库", "why": "模板与素材生态是立项缺口（见 docs/扩库立项.md 4.6）", "impact": "配乐由代码合成，风格单一"},
            {"gap": "ASR/MT 实测", "why": "torch / ctranslate2 无 musllinux-aarch64 wheel", "impact": "字幕走人工撰写路径，无自动转写能力"},
            {"gap": "darktable 调色", "why": "Alpine 无该包", "impact": "用 ffmpeg 曲线替代，参数可复现但少了 RAW 级控制"},
            {"gap": "自动卡点（librosa）", "why": "同上装不上", "impact": "节奏按固定 90 BPM 手工排，不跟画面卡点"},
            {"gap": "workbench 真机联调", "why": "无 Supabase 凭据，且不允许改线上库", "impact": "卡片只在本地产出 JSON + SQL 迁移"},
        ],
        "environment_gaps": [
            {"gap": "MLT 画幅限制", "detail": "melt 对 1080 宽/1080x1080 输出 0 字节，须用 16 的倍数（1088）再裁切"},
            {"gap": "iOS ffmpeg 缺 libx264/libass", "detail": "只能 VideoToolbox 编码 + PNG 叠字幕；CPU 版 ffmpeg 作降级"},
            {"gap": "内存 4GB / 磁盘紧张", "detail": "并发渲染会 OOM，必须串行"},
        ],
        "missing_scorecards": missing,
        "overall": overall,
        "dimension_average": dim_avg,
    }
    write_json(ROOT / "reports/gaps.json", gaps)
    print(f"scorecard.md written, overall={overall}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ""))
