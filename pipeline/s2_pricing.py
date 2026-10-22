#!/usr/bin/env python3
"""Station 2 — 定价分析

工具：duckdb（⚠️）在本机不可用（无 musllinux/aarch64 wheel；官方 CLI 依赖 glibc __res_init），
      本次降级为 Python 内置 sqlite3，SQL 逻辑一致，验证记录写入 reports/tool_verification.json。
输入：comps.json（本轮 0 条，robots 拦截）+ facts.json + 明确标注的假设
输出：pricing.json（含每个数字的证据强度）+ pricing_report.pdf
"""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
import lib
from lib import PipelineError

# ---- 全部假设集中在这里，逐条进 evidence，strength=assumption -----------------
ASSUMPTIONS = [
    ("A1", "悉尼内南（Rosebery/Mascot/Zetland）2 人独立房间、共用卫浴的公开挂牌价多在 A$55–95/晚", 68),
    ("A2", "基准入住率 55%（无历史订单，按同城独立房间常态取值）", 0.55),
    ("A3", "Airbnb 房东服务费 15.5% + GST ≈ 17.05% 有效费率", 0.1705),
    ("A4", "每次入住清洁/布草成本 A$25（房东自做则为时间成本）", 25),
    ("A5", "直订收款手续费按 1.75% + A$0.30/笔 计（Stripe 标准价，未验证商户费率）", 0.0175),
    ("A6", "旺季 = 12/20–1/5、Mardi Gras 周末、NSW 学校假期；其余为平日/周末", 0),
]


def build_db(db_path: Path, comps: dict) -> None:
    con = sqlite3.connect(db_path)
    con.execute("DROP TABLE IF EXISTS comps")
    con.execute("""CREATE TABLE comps(
        comp_id TEXT PRIMARY KEY, suburb TEXT, room_type TEXT, guests INT,
        rating REAL, price_aud REAL, price_date TEXT)""")
    con.executemany(
        "INSERT INTO comps VALUES (?,?,?,?,?,?,?)",
        [(c["comp_id"], c["suburb"], c["room_type"], c["guests"], c["rating"], c["price_aud"], c["price_date"])
         for c in comps["comps"]],
    )
    con.execute("DROP TABLE IF EXISTS scenarios")
    con.execute("CREATE TABLE scenarios(rate REAL, occupancy REAL)")
    con.executemany("INSERT INTO scenarios VALUES (?,?)",
                    [(r, o) for r in (55, 65, 75, 85, 95) for o in (0.40, 0.55, 0.70)])
    con.commit()
    con.close()


def sql_report(db_path: Path) -> dict:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row

    def q(sql, args=()):
        return [dict(r) for r in con.execute(sql, args).fetchall()]

    out = {}
    out["comp_summary"] = q("""SELECT COUNT(*) n, ROUND(AVG(price_aud),1) avg_price,
                                      MIN(price_aud) lo, MAX(price_aud) hi,
                                      ROUND(AVG(rating),2) avg_rating FROM comps""")[0]
    out["comp_by_suburb"] = q("""SELECT suburb, COUNT(*) n, ROUND(AVG(price_aud),1) avg_price
                                 FROM comps GROUP BY suburb ORDER BY n DESC""")
    fee = {a[0]: a[2] for a in ASSUMPTIONS}["A3"]
    out["scenarios"] = q(f"""
        SELECT rate, ROUND(occupancy*100) occ_pct,
               ROUND(rate*365*occupancy, 0) gross_year,
               ROUND(rate*365*occupancy*(1-{fee}), 0) net_platform_year,
               ROUND(rate*365*occupancy*(1-0.0175), 0) net_direct_year,
               ROUND(rate*365*occupancy*{fee}, 0) fee_year
        FROM scenarios ORDER BY rate, occupancy""")
    con.close()
    return out


def main(run_id: str) -> None:
    st = lib.Station("02", "pricing", run_id)
    comps_p = st.require_prev("comps.json", "comps")
    facts_p = st.require_prev("facts.json", "facts")
    comps = lib.read_json(comps_p)
    facts = lib.read_json(facts_p)["facts"]

    db = st.path("pricing.sqlite")
    build_db(db, comps)
    rep = sql_report(db)
    st.add_tool("sqlite3(python)", sqlite3.sqlite_version)
    st.add_tool("duckdb", "unavailable: no musllinux/aarch64 wheel; CLI needs glibc __res_init")
    st.add_tool("weasyprint", lib.tool_version("weasyprint"))

    n_comps = rep["comp_summary"]["n"]
    status = "ok" if n_comps >= 10 else "insufficient_market_data"
    rating = facts["rating"]["value"] or 0
    no_heat = facts["heating_listed"]["value"] is False

    # 基准价：以 A1 中位 A$68 起，按评分/共用卫浴/无暖气三处扣减，全部写进 evidence
    base = 68.0
    adj = []
    if rating < 4.7:
        base -= 3; adj.append(("评分 4.6 < 4.7，扣 A$3", -3))
    if "shared" in str(facts["bathrooms"]["value"]):
        base -= 4; adj.append(("共用卫浴，扣 A$4", -4))
    if no_heat:
        base -= 3; adj.append(("平台未列暖气（冬季风险），扣 A$3", -3))
    base = round(base, 0)

    rec = {
        "weekday": {"low": base - 8, "high": base + 7, "point": base, "currency": "AUD",
                    "basis": ["A1", "A2"] + (["facts.rating"] if rating < 4.7 else [])},
        "weekend": {"low": round(base * 1.15), "high": round(base * 1.32), "point": round(base * 1.2),
                    "currency": "AUD", "basis": ["A2", "A6"]},
        "peak": {"low": round(base * 1.55), "high": round(base * 1.95), "point": round(base * 1.7),
                 "currency": "AUD", "basis": ["A2", "A6"]},
        "min_nights": {"standard": 2, "peak": 3, "gap_fill": 1,
                       "note": "空档 48 小时内可放 1 晚，其余 2 晚起"},
        "weekend_definition": "周五、周六夜",
    }

    evidence = [{"claim": txt, "source_id": f"assumption:{code}", "strength": "assumption"}
                for code, txt, _ in ASSUMPTIONS]
    evidence += [{"claim": f"评分 {rating} / {facts['reviews_count']['value']} 条评价",
                  "source_id": facts["rating"]["source_id"], "strength": "verified"},
                 {"claim": f"设施含：{', '.join(facts['amenities_included']['value'][:6])}…",
                  "source_id": facts["amenities_included"]["source_id"], "strength": "verified"}]
    for text, delta in adj:
        evidence.append({"claim": f"价格调整 {text}", "source_id": "assumption:A1", "strength": "assumption"})

    fee_year = rep["scenarios"][7]["fee_year"] if len(rep["scenarios"]) > 7 else 0
    pricing = {
        "status": status,
        "currency": "AUD",
        "generated_at": lib.now(),
        "recommendations": rec,
        "confidence": "low",
        "provisional": True,
        "comps_used": n_comps,
        "scenarios": rep["scenarios"],
        "fee_math": {
            "platform_fee_rate": 0.1705,
            "example": "A$68 × 2 晚 = A$136/单；平台抽 17.05% ≈ A$23.2；直订同等价格多留 A$23.2/单，10 单 ≈ A$232",
            "ten_bookings_2nights_saving": round(base * 2 * 0.1705 * 10, 0),
        },
        "evidence": evidence,
        "gaps": [
            "comps=0：Airbnb 搜索结果页被 robots.txt 禁止，未绕过 → 阈值『每价 ≥3 个可比房源』不达标。",
            "无房东历史订单导出（入住率、实际成交价、退改率均未知），A2 入住率为假设。",
            "旺季日期表 A6 为通用日历，未用悉尼 2027 年具体活动/假期校核。",
            "结论标 provisional=true：只可用于内部试算，对外报价前必须补 comps 重跑。",
        ],
    }
    pj = st.path("pricing.json")
    lib.write_json(pj, pricing)
    st.add_output(pj, "pricing")

    pdf = render_pdf(st, pricing, facts, rep, base)
    st.add_output(pdf)

    checks = [
        {"id": "comps_ge_10", "ok": n_comps >= 10, "detail": f"实际 {n_comps}"},
        {"id": "every_price_has_3_comps", "ok": False, "detail": "0 个可比房源，全部建议价仅有假设支撑"},
        {"id": "ranges_sane", "ok": rec["weekday"]["low"] < rec["weekday"]["high"] <= rec["peak"]["high"],
         "detail": f"weekday {rec['weekday']['low']}-{rec['weekday']['high']}, peak {rec['peak']['low']}-{rec['peak']['high']}"},
        {"id": "evidence_tagged", "ok": all(e["strength"] in ("verified", "assumption") for e in evidence)},
        {"id": "degraded_declared", "ok": status != "ok" and pricing["provisional"] is True},
    ]
    st.qa(checks)
    st.metrics = {"comps": n_comps, "base": base, "status": status}
    st.finish(0)
    lib.info(f"station 2 pricing status={status} base=A${base:.0f} (comps={n_comps})")


def render_pdf(st, pricing, facts, rep, base) -> Path:
    rows = "".join(
        f"<tr><td>{s['rate']}</td><td>{s['occ_pct']}%</td><td>${s['gross_year']:,.0f}</td>"
        f"<td>${s['net_platform_year']:,.0f}</td><td>${s['net_direct_year']:,.0f}</td>"
        f"<td>${s['fee_year']:,.0f}</td></tr>"
        for s in rep["scenarios"])
    rec = pricing["recommendations"]
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
    @page {{ size: A4; margin: 18mm; }}
    body {{ font-family: "DejaVu Sans", "WenQuanYi Zen Hei", sans-serif; font-size: 10pt; color:#222; }}
    h1 {{ font-size: 19pt; margin: 0 0 4mm; }} h2 {{ font-size: 12pt; margin: 7mm 0 2mm; }}
    .tag {{ display:inline-block; background:#fff3cd; border:1px solid #e0c068; padding:1mm 2mm; font-size:8pt; }}
    table {{ width:100%; border-collapse:collapse; font-size:8.5pt; }}
    th,td {{ border:1px solid #ccc; padding:1.4mm 2mm; text-align:right; }}
    th:first-child, td:first-child {{ text-align:left; }}
    .k {{ color:#666; }} .box {{ background:#f6f7f9; padding:3mm; border-left:3px solid #444; }}
    </style></head><body>
    <h1>定价分析 · Rosebery 独立房间</h1>
    <div class="tag">DRAFT · 临时结论 · 可比房源 {pricing['comps_used']} 个 · 置信度低</div>
    <p class="k">对象：Airbnb {facts['listing_id']['value']}｜2 人｜1 卧室｜1 共用卫浴｜评分
    {facts['rating']['value']}（{facts['reviews_count']['value']} 条）｜{pricing['currency']}</p>

    <h2>1. 建议价（provisional）</h2>
    <table><tr><th>时段</th><th>低</th><th>建议</th><th>高</th><th>依据</th></tr>
    <tr><td>平日（周日–周四）</td><td>A${rec['weekday']['low']:.0f}</td><td><b>A${rec['weekday']['point']:.0f}</b></td>
        <td>A${rec['weekday']['high']:.0f}</td><td>假设 A1/A2</td></tr>
    <tr><td>周末（周五、周六）</td><td>A${rec['weekend']['low']:.0f}</td><td><b>A${rec['weekend']['point']:.0f}</b></td>
        <td>A${rec['weekend']['high']:.0f}</td><td>假设 A2/A6</td></tr>
    <tr><td>旺季（12/20–1/5、Mardi Gras、学校假期）</td><td>A${rec['peak']['low']:.0f}</td>
        <td><b>A${rec['peak']['point']:.0f}</b></td><td>A${rec['peak']['high']:.0f}</td><td>假设 A2/A6</td></tr>
    </table>
    <p>最少晚数：平日 {rec['min_nights']['standard']} 晚；旺季 {rec['min_nights']['peak']} 晚；48 小时内空档可放
    {rec['min_nights']['gap_fill']} 晚。基准价 A${base:.0f} = 假设中位 A$68 − 共用卫浴 4 − 评分 3 − 无暖气 3。</p>

    <h2>2. 情景模型（年化）</h2>
    <table><tr><th>房价</th><th>入住率</th><th>毛收入</th><th>平台净收入</th><th>直订净收入</th><th>平台费</th></tr>{rows}</table>
    <p class="k">平台费按 15.5% + GST ≈ 17.05%；直订按 1.75% + A$0.30/笔 计。清洁成本未计入（A$25/次，随入住次数上升）。</p>

    <h2>3. 这份报告哪里不能信</h2>
    <div class="box">
    <p><b>0 个可比房源。</b>Airbnb robots.txt 对 <code>/s/*/*</code> 明确 Disallow，搜索结果页是唯一能一次拿到同区
    多房源+价格的公开入口，本站按规则停手。所以上面所有价格只有「假设」支撑，没有一条来自真实竞品。</p>
    <p><b>没有历史订单。</b>入住率、实际成交价、退改率全部未知，55% 是拍出来的。</p>
    <p><b>结论只用于内部试算。</b>补 3 屏 App 搜索截图（同日期、独立房间、2 位住客）即可重跑本站，把置信度从 low 提到 medium。</p>
    </div>

    <h2>4. 假设清单</h2>
    <table><tr><th>编号</th><th>假设</th></tr>
    {''.join(f'<tr><td>{c}</td><td style="text-align:left">{t}</td></tr>' for c,t,_ in ASSUMPTIONS)}
    </table>
    </body></html>"""
    src = st.path("pricing_report.html")
    src.write_text(html, encoding="utf-8")
    pdf = st.path("pricing_report.pdf")
    r = lib.run(["weasyprint", str(src), str(pdf)], timeout=300)
    if r["rc"] != 0 or not pdf.exists():
        raise PipelineError(f"weasyprint failed: {r['stderr'][:400]}")
    return pdf


if __name__ == "__main__":
    main(lib.ctx_run_id(sys.argv[1:]))
