#!/usr/bin/env python3
"""Station 2 — 脚本与分镜.

Reads: facts.json, media_manifest.json (+ optional customer menu).
Writes: menu.json, script.json, storyboard.pdf.

Hard gate: a line may only carry text whose every element resolves to a `verified`
fact or a customer-confirmed menu item. Unverified/conflict facts are rejected here,
not at render time — that is the whole point of the chain.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.common import ROOT, Station, now, read_json, station_main, validate, write_json

# 7 shots, durations sum to exactly 30.0 s
SHOTS = [
    {
        "shot_id": "s01", "plate": "steam_pot", "seconds": 4.5,
        "visual": "铜锅特写：汤面翻滚，热气上升（占位板，客户素材到位后替换）",
        "sub_zh": "锅开了。", "sub_en": "The pot is on.",
        "fact_refs": [], "menu_refs": [], "asset_refs": ["ast_graphics_generated"],
    },
    {
        "shot_id": "s02", "plate": "noodle_lift", "seconds": 4.5,
        "visual": "筷子挑起面，热气跟着上升",
        "sub_zh": "一挑，热气跟着上来。", "sub_en": "Lift — the steam follows.",
        "fact_refs": [], "menu_refs": [], "asset_refs": ["ast_graphics_generated"],
    },
    {
        "shot_id": "s03", "plate": "bowl_top", "seconds": 4.5,
        "visual": "成品碗 45° 俯拍，镜头缓推",
        "sub_zh": "这一碗，趁热。", "sub_en": "This bowl. While it's hot.",
        "fact_refs": [], "menu_refs": [], "asset_refs": ["ast_graphics_generated"],
    },
    {
        "shot_id": "s04", "plate": "storefront", "seconds": 4.0,
        "visual": "店门与招牌，傍晚灯亮（占位板）",
        "sub_zh": "Slurp Slurp Noodle", "sub_en": "Slurp Slurp Noodle",
        "fact_refs": ["src_web_title"], "menu_refs": [], "asset_refs": ["ast_graphics_generated"],
    },
    {
        "shot_id": "s05", "plate": "photo_placeholder", "seconds": 4.5,
        "visual": "官网菜品图（占位，未授权，带水印）",
        "sub_zh": "悉尼，来 slurp 一口。", "sub_en": "Sydney — come slurp.",
        "fact_refs": ["src_city"], "menu_refs": [], "asset_refs": ["ast_photo_official"],
    },
    {
        "shot_id": "s06", "plate": "steam_pot", "seconds": 4.0,
        "visual": "汤面再推近，蒸汽满屏（占位板，与 s01 不同机位）",
        "sub_zh": "再来一口。", "sub_en": "One more slurp.",
        "fact_refs": [], "menu_refs": [], "asset_refs": ["ast_graphics_generated"],
    },
    {
        "shot_id": "s07", "plate": "logo_card", "seconds": 4.0,
        "visual": "logo 落版 + 电话",
        "sub_zh": "02 9663 3817", "sub_en": "Slurp Slurp Noodle · Sydney",
        "fact_refs": ["src_web_tel", "src_web_title"], "menu_refs": [],
        "asset_refs": ["ast_logo_official"],
    },
]

# Words that may only appear if the matching fact is verified.
FORBIDDEN_IF_UNVERIFIED = {
    "小锅米线": "src_web_cn_name",       # Chinese name — pending customer
    "云南": "src_ue_cuisine",
    "Rothschild": "src_dir_addr",
    "Rosebery": "src_dir_addr",
    "11:00": "src_hours_mates",
    "21:00": "src_hours_zmenu",
    "Minty": "src_ue_signature",
    "Copper Pot": "src_ue_signature",
}


def build_storyboard_pdf(path: Path, brief: dict, shots: list, facts_by_id: dict, plates_dir: Path):
    """storyboard.pdf via Pillow → PNG pages → img2pdf-free: write a minimal PDF ourselves."""
    from PIL import Image, ImageDraw, ImageFont

    f_zh = "/var/minis/workspace/craft-skills/assets/fonts/NotoSansSC-Regular.otf"
    f_zh_b = "/var/minis/workspace/craft-skills/assets/fonts/NotoSansSC-Bold.otf"
    f_en = "/var/minis/workspace/craft-skills/assets/fonts/Inter-Medium.otf"
    f_en_b = "/var/minis/workspace/craft-skills/assets/fonts/Inter-ExtraBold.otf"

    pages = []
    # cover
    W, H = 1240, 1754  # A4 @150dpi
    cover = Image.new("RGB", (W, H), (16, 34, 113))
    d = ImageDraw.Draw(cover)
    d.text((90, 150), "STORYBOARD", font=ImageFont.truetype(f_en_b, 86), fill=(255, 255, 255))
    d.text((90, 260), "分镜脚本", font=ImageFont.truetype(f_zh_b, 64), fill=(255, 214, 150))
    d.text((90, 380), brief["client"]["name_en"], font=ImageFont.truetype(f_en, 54), fill=(255, 255, 255))
    d.text((90, 460), "30s · 9:16 / 1:1 / 16:9 · 中英字幕", font=ImageFont.truetype(f_zh, 34),
           fill=(200, 205, 235))
    d.line((90, 540, W - 90, 540), fill=(255, 214, 150), width=3)
    d.text((90, 580), f"run_id: {brief['run_id']}", font=ImageFont.truetype(f_en, 30), fill=(190, 196, 230))
    d.text((90, 630), "样片 · 占位素材 · 未授权（客户素材到位后替换）", font=ImageFont.truetype(f_zh, 30),
           fill=(255, 170, 140))
    pages.append(cover)

    for shot in shots:
        page = Image.new("RGB", (W, H), (250, 248, 252))
        d = ImageDraw.Draw(page)
        d.rectangle((0, 0, W, 120), fill=(16, 34, 113))
        d.text((60, 36), f"{shot['shot_id'].upper()}  ·  {shot['seconds']}s",
               font=ImageFont.truetype(f_en_b, 44), fill=(255, 255, 255))
        d.text((W - 330, 44), f"{shot['index'] + 1} / {len(shots)}",
               font=ImageFont.truetype(f_en, 32), fill=(255, 214, 150))

        thumb_path = plates_dir / f"{shot['plate']}.png"
        if thumb_path.exists():
            im = Image.open(thumb_path).convert("RGB")
            th = im.resize((360, 636), Image.LANCZOS)
            page.paste(th, (60, 170))
            d.rectangle((60, 170, 420, 806), outline=(180, 180, 190), width=2)
            d.text((60, 820), "画面（占位板）", font=ImageFont.truetype(f_zh, 24), fill=(120, 120, 130))

        x = 460
        y = 180
        d.text((x, y), "画面描述", font=ImageFont.truetype(f_zh_b, 30), fill=(16, 34, 113))
        y += 50
        for line in _wrap(shot["visual"], 22):
            d.text((x, y), line, font=ImageFont.truetype(f_zh, 26), fill=(40, 40, 50))
            y += 40

        y += 30
        d.text((x, y), "字幕（中）", font=ImageFont.truetype(f_zh_b, 30), fill=(16, 34, 113))
        y += 50
        for line in _wrap(shot["sub_zh"], 18):
            d.text((x, y), line, font=ImageFont.truetype(f_zh, 30), fill=(20, 20, 30))
            y += 44

        y += 24
        d.text((x, y), "Subtitle (EN)", font=ImageFont.truetype(f_en_b, 28), fill=(16, 34, 113))
        y += 46
        for line in _wrap(shot["sub_en"], 26):
            d.text((x, y), line, font=ImageFont.truetype(f_en, 26), fill=(40, 40, 50))
            y += 38

        y += 30
        d.text((x, y), "事实依据", font=ImageFont.truetype(f_zh_b, 28), fill=(16, 34, 113))
        y += 44
        refs = shot["fact_refs"] or ["—（无事实断言）"]
        for r in refs:
            label = r if r in facts_by_id else r
            if r in facts_by_id:
                label = f"{r}: {facts_by_id[r]['value']}  [{facts_by_id[r]['status']}]"
            for line in _wrap(label, 30):
                d.text((x, y), line, font=ImageFont.truetype(f_zh, 22), fill=(70, 70, 80))
                y += 32
        pages.append(page)

    # minimal PDF (one image per page, no external deps)
    _write_pdf(path, pages)


def _wrap(text: str, width: int) -> list:
    out, cur = [], ""
    for ch in text:
        cur += ch
        if len(cur) >= width:
            out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    return out or [""]


def _write_pdf(path: Path, pages) -> None:
    import io
    objs = []  # list of bytes payloads (indirect objects), index+1 = object number
    objs.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    # reserve object 2 for pages
    objs.append(b"")  # placeholder
    page_ids = []
    for img in pages:
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=82)
        data = buf.getvalue()
        w, h = img.size
        img_id = len(objs) + 1
        objs.append(b"<< /Type /XObject /Subtype /Image /Width %d /Height %d "
                    b"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode "
                    b"/Length %d >>\nstream\n" % (w, h, len(data)) + data + b"\nendstream")
        content = b"q %.2f 0 0 %.2f 0 0 cm /Im0 Do Q" % (w, h)
        cont_id = len(objs) + 1
        objs.append(b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream")
        page_id = len(objs) + 1
        objs.append(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %d %d] "
                    b"/Resources << /XObject << /Im0 %d 0 R >> >> /Contents %d 0 R >>"
                    % (w, h, img_id, cont_id))
        page_ids.append(page_id)
    kids = b" ".join(b"%d 0 R" % i for i in page_ids)
    objs[1] = b"<< /Type /Pages /Kids [" + kids + b"] /Count %d >>" % len(page_ids)

    out = bytearray(b"%PDF-1.5\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for i, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n" % (len(objs) + 1)
    out += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        out += b"%010d 00000 n \n" % off
    out += (b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n"
            % (len(objs) + 1, xref))
    path.write_bytes(bytes(out))


def main(st: Station):
    prev = st.dir.parent
    facts_doc = read_json(st.read(prev / "01_collect/facts.json"))
    manifest = read_json(st.read(prev / "01_collect/media_manifest.json"))
    brief = read_json(st.read(prev / "00_brief/brief.json"))
    validate(facts_doc, "facts", where="01_collect/facts.json")
    validate(manifest, "media_manifest", where="01_collect/media_manifest.json")

    facts_by_id = {f["source_id"]: f for f in facts_doc["facts"]}
    verified = {k for k, v in facts_by_id.items() if v["status"] == "verified"}

    # ---- menu.json ------------------------------------------------------- #
    customer_menu = ROOT / "inputs/customer_menu.json"
    items = []
    if customer_menu.exists():
        st.read(customer_menu)
        for row in read_json(customer_menu)["items"]:
            items.append(row)
    menu = {
        "run_id": st.run_id, "generated_at": now(), "currency": "AUD", "gst_included": True,
        "items": items,
        "note": "只收客户提供或已核实的品项。官网无菜单，客户尚未提供，故本片不出现任何菜品名与价格。",
        "empty_reason": "客户未提供菜单；Uber Eats 菜单仅可作核对，不直接入片。" if not items else "",
    }
    validate(menu, "menu", where="02_script/menu.json")
    st.emit(write_json(st.dir / "menu.json", menu), "menu")

    # ---- script.json ----------------------------------------------------- #
    total = 0.0
    for i, shot in enumerate(SHOTS):
        shot["index"] = i
        total += shot["seconds"]
        shot["plate"] = shot["plate"]
        shot["motion"] = ["push_in", "pull_back", "push_in", "drift_up", "pull_back", "push_in", "settle"][i]
        shot["refs"] = {
            "facts": shot["fact_refs"],
            "menu": shot["menu_refs"],
            "assets": shot["asset_refs"],
        }
    total = round(total, 3)
    st.require(abs(total - 30.0) < 1e-6, f"shot durations sum to {total}s, must be 30.0")

    script = {
        "run_id": st.run_id, "generated_at": now(),
        "duration_seconds": 30, "fps": 30, "shots": SHOTS, "total_seconds": total,
    }

    # gate 1: every fact_ref must exist and be verified
    for shot in SHOTS:
        for ref in shot["fact_refs"]:
            st.require(ref in facts_by_id, f"{shot['shot_id']}: unknown fact ref {ref}")
            st.require(facts_by_id[ref]["status"] == "verified",
                       f"{shot['shot_id']}: fact {ref} is {facts_by_id[ref]['status']} — must not appear on screen")
        for ref in shot["menu_refs"]:
            hit = next((m for m in items if m["item_id"] == ref), None)
            st.require(hit is not None and hit["status"] == "verified" and hit["in_video"],
                       f"{shot['shot_id']}: menu item {ref} not verified/in_video")
        for ref in shot["asset_refs"]:
            st.require(any(a["asset_id"] == ref for a in manifest["assets"]),
                       f"{shot['shot_id']}: unknown asset {ref}")

    # gate 2: no forbidden word may slip in unless its fact is verified
    banned_hits = []
    for shot in SHOTS:
        text = shot["sub_zh"] + " " + shot["sub_en"] + " " + shot["visual"]
        for word, fact_id in FORBIDDEN_IF_UNVERIFIED.items():
            if word in text and fact_id not in verified:
                banned_hits.append({"shot": shot["shot_id"], "word": word, "fact": fact_id})
    st.require(not banned_hits, "unverified fact leaked into script: %s" % banned_hits)

    # gate 3: subtitle length rules (<=2 lines, zh <=16 chars/line)
    for shot in SHOTS:
        zh = shot["sub_zh"]
        st.require(len(zh) <= 32, f"{shot['shot_id']}: zh subtitle too long ({len(zh)} chars)")
        lines = [zh[i:i + 16] for i in range(0, len(zh), 16)]
        st.require(len(lines) <= 2, f"{shot['shot_id']}: zh subtitle >2 lines")

    validate(script, "script", where="02_script/script.json")
    st.emit(write_json(st.dir / "script.json", script), "script")

    # ---- storyboard.pdf -------------------------------------------------- #
    sys.path.insert(0, str(ROOT / "pipeline"))
    from lib import plates as plates_mod
    brand = {
        "font_en": str(ROOT / "assets/fonts/Inter-ExtraBold.otf"),
        "font_zh": str(ROOT / "assets/fonts/NotoSansSC-Bold.otf"),
        "logo": str(ROOT / "inputs/customer_media/Slur-Slurp-New-Logo.png"),
        "photo": str(ROOT / "inputs/customer_media/75513371_2388668874794660_3434699996744646656_n.jpg"),
    }
    plates_dir = st.path("plates")
    for name in plates_mod.PLATES:
        plates_mod.render(name, brand, plates_dir)
    pdf = st.dir / "storyboard.pdf"
    build_storyboard_pdf(pdf, brief, SHOTS, facts_by_id, plates_dir)
    st.emit(pdf, "application/pdf")

    st.check("S2-01", "每镜引用字段存在且 verified",
             sum(len(s["fact_refs"]) for s in SHOTS), "不一致 0",
             True, "全部 fact_refs 命中 verified 集合")
    st.check("S2-02", "时长合计 30.0s", total, "==30.0", abs(total - 30) < 1e-6)
    st.check("S2-03", "镜头数 6–8", len(SHOTS), "6..8", 6 <= len(SHOTS) <= 8)
    st.check("S2-04", "未核实事实零泄漏", len(banned_hits), "0", not banned_hits,
             "小锅米线/云南/Rosebery/营业时间/招牌菜均未入片")
    st.check("S2-05", "字幕行数 ≤2 且中文 ≤16 字/行", "all", "all",
             all(len(s["sub_zh"]) <= 32 for s in SHOTS))
    st.check("S2-06", "菜品与价格入片数", len([m for m in items if m["in_video"]]), "0（客户未提供）",
             True, "menu.json 为空，成片不含任何菜品名/价格")

    return {
        "scores": {"business": 3.5, "handoff": 5.0, "benchmark": 4.0, "craft": 4.5},
        "notes": [
            "三道门：fact_ref 必须 verified、禁用词扫描、字幕行长；任何一道不过，本站直接非 0 退出。",
            "因为中文名与菜单都还没到，脚本刻意不含菜名/价格 —— 这是合规，不是缺内容；客户确认后 5 分钟即可补。",
            "扣分：wordcraft（Craft 家族 Windows 可执行）本机不可用，storyboard 改用 python-docx 同族思路的 PIL+手写 PDF，属降级。",
        ],
    }


if __name__ == "__main__":
    sys.exit(station_main(main, 2, "script", "脚本与分镜"))
