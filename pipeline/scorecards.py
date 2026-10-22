#!/usr/bin/env python3
"""四项评分卡：商业价值 35% / 衔接 25% / 标杆 15% / 工艺 25%。

分数不是拍脑袋：工艺分由 qa.json 的通过率与阈值决定；衔接分由 handoff 的 schema/sha 决定；
商业与标杆按下面的 RUBRIC 逐站写理由（含扣分项）。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
import lib

W = {"commercial": 0.35, "handoff": 0.25, "craft": 0.25, "benchmark": 0.15}

# station -> (商业价值, 理由) / (标杆, 理由)
RUBRIC = {
    "00_brief": ((4, "一句话就被拆成可执行的交付清单；但语言只留 zh/en，ja/ko 未定"), 4,
                 "jq 是 JSON 处理的基准工具；本机 1.7.1 实测通过"),
    "01_collect": ((3, "事实表完整可追溯（42 条），但竞品 0 个：定价与定位都缺参照"), 2,
                   "curl 合规但采集能力弱；crawl4ai 装不上，真正的行业做法是 crawl4ai/Playwright + 代理池"),
    "02_pricing": ((3, "给出可执行的价位与「直订省多少」算式，但全部是假设，不能对外报价"), 1,
                   "duckdb 不可用、无 PriceLabs/Beyond 类动态定价数据源；这是全链最弱的一格"),
    "03_photos": ((4, "6 张可直接用的占位成片，参数全记录；但缺 darktable、1 张透视无法扶正"), 2,
                  "darktable 是行业基准，本机没有；用 PIL/OpenCV 复刻了能复刻的部分"),
    "04_video": ((4, "双尺寸 40s 成片，响度 -13.8 LUFS、真峰 -5.2 dBTP，可直接发"), 4,
                 "ffmpeg 是事实标准；因本机 worker 锁死改到电脑端编码，链路仍可复现"),
    "05_copy": ((4, "中英两版可直接粘贴，句句带来源；但没有 ja/ko，也没做 A/B 文案"), 3,
                "无已验证翻译工具，人工撰写优于机翻；对标 DeepL+人工 仍差一档"),
    "06_guide": ((5, "双语 PDF，占位符齐全，打印即用；房东只需填本地字段"), 4,
                 "weasyprint 不是排版天花板（InDesign/LaTeX 更高），但自动化程度足够"),
    "07_site": ((4, "能收申请、不收款、移动端可用；但日历还没接房东真实 iCal"), 3,
                "原生静态站性能好，但功能对标 Lodgify/Hostaway 还差预订引擎与支付"),
    "08_qc": ((3, "把「哪里不能信」写成了机器可查的报告；但 Lighthouse 没跑成"), 2,
              "真实 Lighthouse 要 Chrome，本机跑不了；静态启发式只能算替身"),
    "09_support": ((5, "25 条 FAQ + 9 篇知识包，密码类问题 100% 拒答"), 3,
                   "规则检索不是 RAG；小助手接入后建议换向量检索"),
}


def station_score(d: Path) -> dict:
    qa = json.loads((d / "qa.json").read_text())
    ho = json.loads((d / "handoff.json").read_text())
    checks = qa["checks"]
    passed = sum(1 for c in checks if c.get("ok"))
    ratio = passed / max(1, len(checks))

    # 工艺：通过率映射到 0–5，再按硬阈值扣分
    craft = round(ratio * 5, 1)
    if not qa["passed"]:
        craft = min(craft, 3.5)

    # 衔接：schema 校验 + sha 记录 + 上游输入
    json_out = [o for o in ho["outputs"] if o["path"].endswith(".json")]
    schema_ok = any(o.get("schema") for o in json_out)
    inputs_ok = all(len(i["sha256"]) == 64 for i in ho["inputs"])
    handoff = 5.0
    if not schema_ok:
        handoff -= 1.0
    if not inputs_ok:
        handoff -= 1.0
    if ho.get("exit_code") not in (0, None):
        handoff -= 1.0

    name = ho["station"]
    rub = RUBRIC.get(name, ((3, "未写理由"), 3, "未写理由"))
    comm, comm_why = rub[0]
    bench, bench_why = rub[1], rub[2]
    total = round(comm * W["commercial"] + handoff * W["handoff"] + craft * W["craft"] + bench * W["benchmark"], 2)
    return {
        "station": name,
        "scores": {"commercial": comm, "handoff": round(handoff, 1), "craft": craft, "benchmark": bench},
        "total": total,
        "notes": [f"商业价值 {comm}/5：{comm_why}",
                  f"衔接 {handoff}/5：{passed}/{len(checks)} 项 QA 通过；schema={'是' if schema_ok else '缺'}；sha 校验={'是' if inputs_ok else '否'}",
                  f"工艺 {craft}/5：QA 通过率 {passed}/{len(checks)}",
                  f"标杆 {bench}/5：{bench_why}"],
    }


def main(run_id: str) -> None:
    run = lib.RUNS / run_id
    rows = []
    for d in sorted(p for p in run.iterdir() if p.is_dir() and p.name[:2].isdigit()):
        sc = station_score(d)
        lib.write_json(d / "scorecard.json", sc)
        rows.append(sc)

    overall = round(sum(r["total"] for r in rows) / len(rows), 2)
    by_axis = {k: round(sum(r["scores"][k] for r in rows) / len(rows), 2) for k in W}
    doc = {"run": run_id, "stations": rows, "overall": overall, "axis_average": by_axis,
           "weights": W}
    lib.write_json(run / "reports" / "scorecard.json", doc)

    md = [f"# 评分卡 · {run_id}", "",
          f"**总分 {overall}/5**　商业 {by_axis['commercial']} · 衔接 {by_axis['handoff']} · 工艺 {by_axis['craft']} · 标杆 {by_axis['benchmark']}", "",
          "| 站 | 商业(35%) | 衔接(25%) | 工艺(25%) | 标杆(15%) | 总分 |", "|---|---|---|---|---|---|"]
    for r in rows:
        s = r["scores"]
        md.append(f"| {r['station']} | {s['commercial']} | {s['handoff']} | {s['craft']} | {s['benchmark']} | **{r['total']}** |")
    md += ["", "## 扣分说明", ""]
    for r in rows:
        md.append(f"### {r['station']}")
        md += [f"- {n}" for n in r["notes"]]
        md.append("")
    (lib.ROOT / "reports").mkdir(exist_ok=True)
    (lib.ROOT / "reports" / "scorecard.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps({"overall": overall, "axes": by_axis}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(lib.ctx_run_id(sys.argv[1:]))
