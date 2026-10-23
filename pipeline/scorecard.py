#!/usr/bin/env python3
"""汇总 runs/<run_id>/*/scorecard.json → reports/scorecard.md。用法：python pipeline/scorecard.py runs/<run_id>"""
import json, pathlib, sys
W = {"commercial": .35, "handoff": .25, "craft": .25, "benchmark": .15}
rd = pathlib.Path(sys.argv[1]); out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else rd / "reports/scorecard.md")
rows, tot = [], {k: [] for k in W}
for p in sorted(rd.glob("*/scorecard.json")):
    s = json.loads(p.read_text()); w = sum(s[k] * W[k] for k in W)
    for k in W: tot[k].append(s[k])
    qa = json.loads((p.parent / "qa.json").read_text())["pass"]
    rows.append(f"| {s['station']} | {s['commercial']} | {s['handoff']} | {s['craft']} | {s['benchmark']} | **{w:.2f}** | {'✓' if qa else '✗'} |")
    rows.append(f"| ↳ 扣分理由 | {s['reasons']['commercial']} | {s['reasons'].get('handoff','Schema 校验通过、sha256 交接')} | {s['reasons']['craft']} | {s['reasons']['benchmark']} | | |")
avg = {k: sum(v) / len(v) for k, v in tot.items()}; T = sum(avg[k] * W[k] for k in W)
md = ["# 评分卡（0–5 分；总分 = 商业 35% + 衔接 25% + 工艺 25% + 标杆 15%）", "", f"run_id: `{rd.name}`", "",
      "| 站 | ①商业 | ②衔接 | ③工艺 | ④标杆 | 加权 | qa |", "|---|---|---|---|---|---|---|", *rows,
      f"| **平均** | {avg['commercial']:.2f} | {avg['handoff']:.2f} | {avg['craft']:.2f} | {avg['benchmark']:.2f} | **{T:.2f} / 5（{T/5*100:.0f} 分）** | |"]
out.parent.mkdir(exist_ok=True, parents=True); out.write_text("\n".join(md) + "\n"); print("\n".join(md[-1:])); print(out)
