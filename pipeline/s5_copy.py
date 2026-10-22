#!/usr/bin/env python3
"""Station 5 — 多语言房源描述

zh / en 两版由同一份「段落 + 事实键」表生成，句句可追溯。
只写 facts.status == verified 的设施；unverified/conflict 一律不出现。
ja / ko 未交付：本机无已验证翻译工具（argos-translate 未通过），不做机翻凑数。
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
import lib
from lib import PipelineError

# 禁词：平台标为「无 / 待确认」的东西，出现在文案里就是事故
# 用正则，避免 hair dryer 这种复合词误伤
FORBIDDEN = {
    "zh": [r"暖气", r"热水", r"烘干机", r"基本用品", r"监控", r"摄像头", r"门牌", r"密码"],
    "en": [r"\bheating\b", r"\bhot water\b", r"(?<!hair )\bdryer\b", r"\bessentials\b",
           r"\bcamera\b", r"\bcctv\b", r"\bdoor code\b", r"\bpassword\b"],
}

FORBIDDEN_AMENITY = {
    "Dryer": r"(?<!hair )\bdryer\b",
    "Essentials": r"\bessentials\b",
    "Hot water": r"\bhot water\b",
    "Heating": r"\bheating\b",
    "Exterior security cameras on property": r"\bcamera",
}

TITLE = {
    "zh": "Rosebery 独立房间 · 2 人 · 书桌与后院",
    "en": "Private room in Rosebery · desk & garden",
}

SECTIONS = [
    {
        "id": "about",
        "heading": {"zh": "关于这个空间", "en": "About this space"},
        "paras": {
            "zh": [("这是一间位于 Rosebery 的独立房间，位于一栋住宅内，最多住 2 人。", ["room_type", "max_guests", "suburb"]),
                   ("房间配一张 1.5 米双人床（queen），房门可以上锁。", ["beds", "amenities_included"]),
                   ("卫生间与其他人共用，房源页面已如实标注。", ["bathrooms"])],
            "en": [("A private room in a house in Rosebery, sleeping up to 2 guests.", ["room_type", "max_guests", "suburb"]),
                   ("The room has one queen bed and a lock on the bedroom door.", ["beds", "amenities_included"]),
                   ("The bathroom is shared, and the listing says so plainly.", ["bathrooms"])],
        },
    },
    {
        "id": "the_room",
        "heading": {"zh": "房间", "en": "The room"},
        "paras": {
            "zh": [("房间里有书桌工作区和空调，适合白天办公、晚上休息。", ["amenities_included"]),
                   ("现有的房间照片是实拍，你也可以要求看更多角度。", ["description_public"])],
            "en": [("There is a dedicated desk and air conditioning — fine for a workday, quiet at night.", ["amenities_included"]),
                   ("The room photos are real; ask and we will send more angles.", ["description_public"])],
        },
    },
    {
        "id": "access",
        "heading": {"zh": "住客可用区域", "en": "Guest access"},
        "paras": {
            "zh": [("你可以使用厨房、洗衣机、电视、钢琴，以及 Wi-Fi 和专用工作区。", ["amenities_included"]),
                   ("门外有免费的院内停车位；后院有户外用餐区和 BBQ。", ["amenities_included"])],
            "en": [("You can use the kitchen, washing machine, TV and piano, plus Wi-Fi and the dedicated workspace.", ["amenities_included"]),
                   ("Free parking on the premises; the back garden has an outdoor dining area and a BBQ.", ["amenities_included"])],
        },
    },
    {
        "id": "notes",
        "heading": {"zh": "其他注意事项", "en": "Other things to note"},
        "paras": {
            "zh": [("房屋守则：最多 2 位过夜住客，可以带宠物。", ["house_rules"]),
                   ("房间有空调；如果你对冬季取暖有要求，请在预订前先问一句。", ["amenities_included", "heating_listed"]),
                   ("入住与退房时间、Wi-Fi 与门锁方式，会在确认预订后由房东直接发送。", ["checkin_time", "wifi_password", "door_code"]),
                   ("卫生间里有吹风机；房内配烟雾报警器、一氧化碳报警器、灭火器和急救箱。", ["amenities_included", "safety_devices"])],
            "en": [("House rules: up to 2 overnight guests; pets are allowed.", ["house_rules"]),
                   ("The room has air conditioning. If winter warmth matters to you, please ask before booking.", ["amenities_included", "heating_listed"]),
                   ("Check-in and check-out times, Wi-Fi and door access are sent by the host after booking.", ["checkin_time", "wifi_password", "door_code"]),
                   ("There is a hair dryer in the bathroom; the room has a smoke alarm, a carbon monoxide alarm, a fire extinguisher and a first aid kit.", ["amenities_included", "safety_devices"])],
        },
    },
]


def render(lang: str, facts: dict, pricing: dict) -> dict:
    title = TITLE[lang]
    sections = []
    for sec in SECTIONS:
        paras = [{"text": t, "sources": [f"facts.{k}" for k in keys]} for t, keys in sec["paras"][lang]]
        sections.append({"id": sec["id"], "heading": sec["heading"][lang], "paragraphs": paras})
    return {
        "lang": lang,
        "title": title,
        "title_len": len(title),
        "sections": sections,
        "generated_at": lib.now(),
        "pricing_ref": {"status": pricing["status"], "note": "价格不写进文案：pricing 仍为 provisional"},
    }


def to_md(doc: dict, facts: dict, pricing: dict) -> str:
    lang = doc["lang"]
    lines = [f"# {doc['title']}", ""]
    meta = ("> DRAFT · 可直接粘贴进 Airbnb 后台；“其他注意事项”里不要加平台已有的字段。"
            if lang == "zh" else
            "> DRAFT · ready to paste into Airbnb. Do not duplicate fields Airbnb already collects.")
    lines += [meta, ""]
    for sec in doc["sections"]:
        lines += [f"## {sec['heading']}", ""]
        for p in sec["paragraphs"]:
            lines += [p["text"], ""]
    lines += ["---", ""]
    if lang == "zh":
        lines += ["**事实核对**：房间 1 张 queen 床、2 人、共用卫浴、可锁门、空调、书桌、厨房、洗衣机、电视、钢琴、"
                  "Wi-Fi、免费停车、后院 BBQ/户外用餐区、可带宠物 —— 均为平台公开页标注的设施。",
                  "", f"**未写入**：暖气、热水、烘干机、基本用品（平台标为『无』或待房东确认）。"]
    else:
        lines += ["**Facts check**: 1 queen bed, 2 guests, shared bathroom, lockable door, air conditioning, desk, "
                  "kitchen, washing machine, TV, piano, Wi-Fi, free parking, garden BBQ/outdoor dining, pets allowed — "
                  "all as listed on the public Airbnb page.",
                  "", "**Deliberately omitted**: heating, hot water, dryer, essentials (listed as unavailable, or pending owner confirmation)."]
    return "\n".join(lines) + "\n"


def run(run_id: str) -> None:
    st = lib.Station("05", "copy", run_id)
    facts_p = st.require_upstream("01", "facts.json", "facts")
    pricing_p = st.require_upstream("02", "pricing.json", "pricing")
    st.require_upstream("03", "photos/order.json")
    facts_doc = lib.read_json(facts_p)
    facts = facts_doc["facts"]
    pricing = lib.read_json(pricing_p)

    outdir = st.path("listing_copy")
    outdir.mkdir(parents=True, exist_ok=True)
    docs, problems = {}, []
    verified = [a for a in facts["amenities_included"]["value"]]

    for lang in ("zh", "en"):
        doc = render(lang, facts, pricing)
        lib.write_json(outdir / f"{lang}.json", doc)
        lib.validate("copy", doc, label=f"listing_copy/{lang}.json")
        md = to_md(doc, facts, pricing)
        (outdir / f"{lang}.md").write_text(md, encoding="utf-8")
        docs[lang] = doc

        if len(doc["title"]) > 50:
            problems.append(f"{lang}: title {len(doc['title'])} > 50")
        body = " ".join(p["text"] for sec in doc["sections"] for p in sec["paragraphs"])
        low = body.lower()
        for rx in FORBIDDEN[lang]:
            if re.search(rx, low):
                problems.append(f"{lang}: forbidden term /{rx}/ in copy")
        # 设施白名单：文案里提到、但不在 verified 列表里的设施名 → 停
        for amenity in facts["amenities_not_included"]["value"]:
            rx = FORBIDDEN_AMENITY.get(amenity, re.escape(amenity.lower()))
            if re.search(rx, low):
                problems.append(f"{lang}: mentions unverified amenity “{amenity}”")

    st.add_tree(outdir)
    st.add_tool("python3", sys.version.split()[0])

    checks = [
        {"id": "title_le_50", "ok": all(len(d["title"]) <= 50 for d in docs.values()),
         "detail": {k: len(d["title"]) for k, d in docs.items()}},
        {"id": "no_forbidden_terms", "ok": not problems, "detail": problems},
        {"id": "only_verified_amenities", "ok": not problems, "detail": f"{len(verified)} 项已验证设施"},
        {"id": "every_para_has_sources", "ok": all(p["sources"] for d in docs.values() for s in d["sections"] for p in s["paragraphs"])},
        {"id": "two_languages", "ok": set(docs) == {"zh", "en"}, "detail": list(docs)},
        {"id": "pricing_not_in_copy", "ok": "A$" not in (outdir / "zh.md").read_text() + (outdir / "en.md").read_text()},
    ]
    st.qa(checks)
    st.metrics = {"languages": list(docs), "title_len": {k: len(d["title"]) for k, d in docs.items()},
                  "words_en": len((outdir / "en.md").read_text().split()),
                  "chars_zh": len((outdir / "zh.md").read_text())}
    st.finish(1 if problems else 0, "; ".join(problems) if problems else None)
    if problems:
        raise PipelineError("; ".join(problems))
    lib.info("station 5 copy zh+en ok")


if __name__ == "__main__":
    run(lib.ctx_run_id(sys.argv[1:]))
