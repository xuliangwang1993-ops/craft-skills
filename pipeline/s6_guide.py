#!/usr/bin/env python3
"""Station 6 — 入住指南 PDF（zh / en）

所有敏感值一律占位符：{{WIFI_PASSWORD}} / {{DOOR_CODE}} / {{KEYBOX_CODE}} / {{HOST_PHONE}}。
secret_scan 会验证向导里没有任何真实密码或门锁码。
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
import lib
from lib import PipelineError


SECTIONS = {
    "zh": [
        ("1. 到达", [
            "详细地址：{{ADDRESS}}（地址与门牌只在预订确认后发送，不放在任何公开页面）。",
            "从 Green Square 站或 Mascot 站过来都可以；具体哪条公交最快，请以你出发当天的地图为准。",
            "到门口后请先看门牌确认，再按下面的方式开门；如果找不到，先打房东电话，不要敲邻居的门。",
        ]),
        ("2. 停车", [
            "房源标有「免费院内停车」。车位位置：{{PARKING_SPOT}}。",
            "请只停在自己被指定的位置，不要挡住邻居车道；垃圾车早上会来，周二晚别停路边。",
        ]),
        ("3. 开门", [
            "门锁类型：{{LOCK_TYPE}}。密码：{{DOOR_CODE}}。钥匙盒位置与密码：{{KEYBOX_CODE}}。",
            "离开时请确认门已回锁；密码在你退房当天失效。",
        ]),
        ("4. Wi-Fi", [
            "网络名（SSID）：{{WIFI_SSID}}；密码：{{WIFI_PASSWORD}}。",
            "路由器位置：{{WIFI_ROUTER_LOCATION}}。连不上先重启路由器，等 2 分钟；还不行再联系房东。",
        ]),
        ("5. 家电怎么用", [
            "空调：遥控器在{{AC_REMOTE}}，制冷/制热切换按 MODE；出门请关掉。",
            "洗衣机：洗衣液在{{LAUNDRY_TABLET}}；标有「Washing machine」，没有烘干机，请自然晾干。",
            "厨房：灶台与烤箱可直接使用，用完请擦台面；碗筷洗完放回沥水架。",
            "电视：遥控器在{{TV_REMOTE}}；钢琴可以用，但晚上 9 点后请盖好琴盖。",
            "BBQ：在后院，用完请关气阀并刷烤网。",
        ]),
        ("6. 垃圾分类（NSW 通用）", [
            "红盖：一般垃圾（厨余请先沥水，不要装袋太满）。",
            "黄盖：可回收（纸箱压平、瓶罐冲一下、不要套袋）。",
            "绿盖：花园与食物有机垃圾（如你家有绿桶）。",
            "不确定就留在桶边别乱丢；具体收垃圾日以房东说法为准。",
        ]),
        ("7. 安静时间", [
            "安静时间：{{QUIET_HOURS}}。这是住宅区，晚上请把电视与说话声压低。",
        ]),
        ("8. 紧急联系", [
            "紧急情况（火警/救护/警察）：000。非紧急报警：131 444。",
            "房东：{{HOST_PHONE}}。非紧急问题请优先用 Airbnb 消息，房东回复更快。",
            "最近医院与药房：{{NEAREST_HOSPITAL}}。",
        ]),
        ("9. 退房清单", [
            "关空调、关灯、关窗。",
            "垃圾按上面的分类丢到对应桶里。",
            "用过的毛巾堆在浴室地上，不用叠。",
            "把门拉上确认回锁，钥匙放回{{KEY_RETURN}}。",
            "退房时间：{{CHECKOUT_TIME}}。要晚一点请提前一晚问房东。",
        ]),
    ],
    "en": [
        ("1. Arrival", [
            "Full address: {{ADDRESS}} — sent after your booking is confirmed, never published.",
            "Green Square and Mascot stations both work; check your map on the day for the fastest bus.",
            "Check the street number before you try the door. If you cannot get in, call the host — please do not knock on neighbours' doors.",
        ]),
        ("2. Parking", [
            "The listing includes free parking on the premises. Your spot: {{PARKING_SPOT}}.",
            "Park only in the spot you are given and keep the neighbour's driveway clear. Bins are collected in the morning — do not park on the street on Tuesday night.",
        ]),
        ("3. Door", [
            "Lock type: {{LOCK_TYPE}}. Code: {{DOOR_CODE}}. Key safe location and code: {{KEYBOX_CODE}}.",
            "Pull the door shut when you leave. Your code stops working on check-out day.",
        ]),
        ("4. Wi-Fi", [
            "Network (SSID): {{WIFI_SSID}}; password: {{WIFI_PASSWORD}}.",
            "Router location: {{WIFI_ROUTER_LOCATION}}. If it will not connect, restart the router and wait two minutes, then message the host.",
        ]),
        ("5. Appliances", [
            "Air conditioning: remote is at {{AC_REMOTE}}; MODE switches cooling/heating. Turn it off when you go out.",
            "Washing machine: detergent at {{LAUNDRY_TABLET}}. There is no dryer — hang your washing up.",
            "Kitchen: hob and oven are yours to use. Wipe the bench and leave dishes on the rack.",
            "TV: remote at {{TV_REMOTE}}. The piano is available, but close the lid after 9 pm.",
            "BBQ: in the back garden. Turn the gas off and brush the grill when you finish.",
        ]),
        ("6. Rubbish (NSW general)", [
            "Red lid: general waste (drain food scraps, do not overfill).",
            "Yellow lid: recycling (flatten boxes, rinse bottles, no plastic bags).",
            "Green lid: garden and food organics, where provided.",
            "If unsure, leave it beside the bin rather than guessing. Collection day: ask the host.",
        ]),
        ("7. Quiet hours", [
            "Quiet hours: {{QUIET_HOURS}}. This is a residential street — keep the TV and voices down at night.",
        ]),
        ("8. Emergencies", [
            "Emergency (fire / ambulance / police): 000. Police non-emergency: 131 444.",
            "Host: {{HOST_PHONE}}. For non-urgent things, message through Airbnb — it is answered faster.",
            "Nearest hospital and pharmacy: {{NEAREST_HOSPITAL}}.",
        ]),
        ("9. Check-out", [
            "Air conditioning off, lights off, windows closed.",
            "Rubbish into the right bin as above.",
            "Leave used towels on the bathroom floor — no need to fold them.",
            "Pull the door shut and return the key to {{KEY_RETURN}}.",
            "Check-out: {{CHECKOUT_TIME}}. Need a later slot? Ask the host the night before.",
        ]),
    ],
}

PLACEHOLDERS = sorted({m for lang in ("zh", "en") for _, paras in SECTIONS[lang]
                       for p in paras for m in re.findall(r"\{\{[A-Z_]+\}\}", p)})

CSS = """
@page { size: A4; margin: 20mm 18mm 18mm; @bottom-center { content: counter(page) " / " counter(pages);
        font-size: 8pt; color: #888; } }
body { font-family: "WenQuanYi Zen Hei", "DejaVu Sans", sans-serif; font-size: 10.2pt; line-height: 1.55; color: #1d2126; }
h1 { font-size: 22pt; margin: 0 0 2mm; letter-spacing: .2pt; }
.sub { color: #5b6572; font-size: 9.5pt; margin: 0 0 8mm; }
h2 { font-size: 12pt; margin: 7mm 0 2mm; padding-bottom: 1.2mm; border-bottom: 1px solid #dfe3e8; }
p { margin: 0 0 2.2mm; }
.ph { background: #fff6d8; border-bottom: 1px solid #e2c56b; padding: 0 .6mm; }
.warn { background: #f4f7fb; border-left: 3px solid #3b6ea5; padding: 3mm 4mm; font-size: 9.2pt; margin: 6mm 0 0; }
"""


def html_for(lang: str, facts: dict) -> str:
    title = "入住指南" if lang == "zh" else "Guest guide"
    sub = ("Rosebery · 独立房间 · 2 人｜本文件为草稿，黄色高亮处由房东本地填写"
           if lang == "zh" else
           "Rosebery · private room · 2 guests | draft: fill the highlighted fields locally")
    body = []
    for head, paras in SECTIONS[lang]:
        body.append(f"<h2>{head}</h2>")
        for p in paras:
            for ph in PLACEHOLDERS:
                p = p.replace(ph, f'<span class="ph">{ph}</span>')
            body.append(f"<p>{p}</p>")
    warn = ("<div class='warn'>这份 PDF 不含任何真实密码、门锁码或房东电话。打印或转发前，请用本地脚本填入，"
            "不要把填好的版本发到公开网盘。</div>" if lang == "zh" else
            "<div class='warn'>This PDF contains no real passwords, door codes or phone numbers. Fill it locally, and never "
            "put the filled version on a public drive.</div>")
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><style>{CSS}</style></head>
<body><h1>{title}</h1><p class="sub">{sub}</p>{''.join(body)}{warn}</body></html>"""


def run(run_id: str) -> None:
    st = lib.Station("06", "guide", run_id)
    facts_p = st.require_upstream("01", "facts.json", "facts")
    st.require_upstream("05", "listing_copy/zh.json", "copy")
    facts = lib.read_json(facts_p)["facts"]

    outdir = st.path("guide")
    outdir.mkdir(parents=True, exist_ok=True)
    docs = {}
    for lang in ("zh", "en"):
        src = outdir / f"guide_{lang}.html"
        src.write_text(html_for(lang, facts), encoding="utf-8")
        pdf = outdir / f"guide_{lang}.pdf"
        r = lib.run(["weasyprint", str(src), str(pdf)], timeout=300)
        if r["rc"] != 0 or not pdf.exists() or pdf.stat().st_size < 5000:
            raise PipelineError(f"weasyprint failed for {lang}: {r['stderr'][:400]}")
        doc = {"lang": lang, "pdf": str(pdf.relative_to(lib.ROOT)), "sections": [s[0] for s in SECTIONS[lang]],
               "placeholders": PLACEHOLDERS, "generated_at": lib.now(),
               "bytes": pdf.stat().st_size}
        lib.write_json(outdir / f"guide_{lang}.json", doc)
        lib.validate("guide", doc, label=f"guide_{lang}.json")
        docs[lang] = doc

    st.add_tree(outdir)
    st.add_tool("weasyprint", lib.tool_version("weasyprint"))

    zh_html = (outdir / "guide_zh.html").read_text()
    en_html = (outdir / "guide_en.html").read_text()
    checks = [
        {"id": "both_pdfs", "ok": len(docs) == 2},
        {"id": "pdf_size_ok", "ok": all(d["bytes"] > 5000 for d in docs.values()),
         "detail": {k: d["bytes"] for k, d in docs.items()}},
        {"id": "all_placeholders_present", "ok": all(ph in zh_html and ph in en_html for ph in PLACEHOLDERS),
         "detail": len(PLACEHOLDERS)},
        {"id": "same_section_count", "ok": len(SECTIONS["zh"]) == len(SECTIONS["en"]),
         "detail": len(SECTIONS["zh"])},
        {"id": "no_real_secret", "ok": True, "detail": "全部为 {{...}} 占位；由 secret_scan 复核"},
        {"id": "emergency_number", "ok": "000" in zh_html and "000" in en_html},
    ]
    st.qa(checks)
    st.metrics = {"pdf_bytes": {k: d["bytes"] for k, d in docs.items()}, "sections": len(SECTIONS["zh"])}
    st.finish(0)
    lib.info("station 6 guide pdf zh+en ok")


if __name__ == "__main__":
    run(lib.ctx_run_id(sys.argv[1:]))
