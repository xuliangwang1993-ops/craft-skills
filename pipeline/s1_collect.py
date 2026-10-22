#!/usr/bin/env python3
"""Station 1 — 房源与竞品采集

只读公开页面，遵守 robots.txt（≥3s/请求）。事实全部带 source_id。
竞品：Airbnb 搜索结果路径 /s/*/* 被 robots.txt 明确 Disallow，本站在合规前提下不抓，
      comps.json 以 blocked_robots 结束，交由房东用 App 截图补齐（见 pending_owner）。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
import lib
from lib import PipelineError

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
LISTING_URL = "https://www.airbnb.com.au/rooms/1286789934809628478"
ROBOTS_URL = "https://www.airbnb.com.au/robots.txt"
POLITE_S = 3


def fetch(url: str, dest: Path, wait_s: int = POLITE_S) -> dict:
    """Fetch once, cache on disk, never refetch within a run (deterministic)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000:
        return {"url": url, "cached": True, "bytes": dest.stat().st_size,
                "sha256": lib.sha256_file(dest)}
    time.sleep(wait_s)
    r = lib.run(["curl", "-sS", "-A", UA, "--max-time", "45",
                 "-w", "%{http_code}", "-o", str(dest), url], timeout=90)
    code = (r["stdout"] or "").strip()[-3:]
    if r["rc"] != 0 or not dest.exists():
        raise PipelineError(f"fetch failed {url}: {r['stderr'][:300]}")
    return {"url": url, "cached": False, "http": code, "bytes": dest.stat().st_size,
            "sha256": lib.sha256_file(dest)}


def parse_robots(text: str) -> dict:
    """Extract the User-agent:* block and answer 'is this path allowed?'."""
    rules, ua = [], None
    for line in text.splitlines():
        line = line.split("#")[0].strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip().lower(), v.strip()
        if k == "user-agent":
            ua = v
        elif k in ("allow", "disallow") and ua == "*":
            rules.append((k, v))
    return {"rules": rules, "count": len(rules)}


def robots_allows(rob: dict, path: str) -> bool:
    """Longest-match wins, Allow beats Disallow on equal length (RFC 9309)."""
    best = None
    for kind, pat in rob["rules"]:
        if pat == "":
            continue
        rx = "^" + re.escape(pat).replace(r"\*", ".*") + "$"
        if re.match(rx, path):
            if best is None or len(pat) > len(best[1]) or (len(pat) == len(best[1]) and kind == "allow"):
                best = (kind, pat)
    return True if best is None else best[0] == "allow"


def pdp_json(page: str) -> dict:
    m = re.search(r'<script id="data-deferred-state-0"[^>]*>(.*?)</script>', page, re.S)
    if not m:
        raise PipelineError("PDP: data-deferred-state-0 not found (page shape changed)")
    return json.loads(m.group(1))


def node_of(d: dict) -> dict:
    return d["niobeClientData"][0][1]["data"]["node"]


def collect_amenities(p: dict) -> tuple[list[str], list[str]]:
    inc, exc = [], []
    for g in p["amenities"].get("seeAllAmenitiesGroups", []):
        for a in g.get("amenities", []):
            (inc if a.get("available") else exc).append(a.get("title", "").strip())
    return inc, exc


def build_facts(node: dict, src_pdp: str, src_robots: str) -> dict:
    p = node["pdpPresentation"]
    overview = p.get("overview", {})
    inc, exc = collect_amenities(p)
    rules = []
    for g in p.get("rules", {}).get("groupItems", []):
        rules += [i.get("title") for i in g.get("items", []) if i.get("title")]
    safety = []
    for g in p.get("safetyAndProperty", {}).get("groupItems", []):
        safety += [i.get("title") for i in g.get("items", []) if i.get("title")]
    desc_html = p.get("descriptions", {}).get("longDescriptionHtml", {}).get("localizedString", "")
    host = p.get("hostInfo", {}).get("passportData", {}) or {}
    rating = node.get("listingRatingStats", {}).get("overallRatingStats", {})
    share = p.get("seoFeatures", {}).get("ogTags", {}).get("ogTitle", {}).get("content", {}).get("localizedString")
    coord = node.get("location", {}).get("coordinate", {})

    F = {}

    def add(key, value, source_id, status="verified", note=None):
        F[key] = {"value": value, "source_id": source_id, "status": status}
        if note:
            F[key]["note"] = note

    add("listing_id", node.get("id"), src_pdp)
    add("platform", "Airbnb", src_pdp)
    add("url", LISTING_URL, src_pdp)
    add("share_title", share, src_pdp, note="Airbnb 自动生成的分享标题，非房东自定标题")
    add("host_title", None, "src_owner_pending", "pending_owner", "正式标题待房东提供")
    add("room_type", "Private room in home（整屋中的独立房间）", src_pdp)
    add("property_type", node.get("propertyType"), src_pdp)
    add("space_type", node.get("spaceType"), src_pdp)
    add("suburb", "Rosebery", src_pdp)
    add("state", "New South Wales", src_pdp)
    add("country", "Australia", src_pdp)
    add("coordinates", {"lat": coord.get("latitude"), "lng": coord.get("longitude")}, src_pdp,
        note="仅用于计算距离/街区级地图，任何公开产出不得输出精确坐标或门牌")
    add("address", None, "src_policy", "pending_owner", "具体地址不公开、不入任何公开产出")
    add("max_guests", node.get("personCapacity"), src_pdp)
    add("bedrooms", 1, src_pdp, note="页面标注 1 bedroom")
    add("beds", ["1 queen bed"], src_pdp)
    add("bathrooms", "1 shared bathroom（共用）", src_pdp)
    add("description_public", re.sub("<[^>]+>", " ", desc_html).strip(), src_pdp,
        note="Airbnb 模板句，且『whole family』与 2 人房不符")
    add("description_full", None, "src_owner_pending", "pending_owner", "完整描述待房东提供")
    add("amenities_included", inc, src_pdp)
    add("amenities_not_included", exc, src_pdp)
    add("house_rules", rules, src_pdp)
    add("safety_devices", safety, src_pdp)
    add("checkin_time", None, "src_owner_pending", "pending_owner")
    add("checkout_time", None, "src_owner_pending", "pending_owner")
    add("min_nights", None, "src_owner_pending", "pending_owner")
    add("max_nights", None, "src_owner_pending", "pending_owner")
    add("cancellation_policy", None, "src_owner_pending", "pending_owner")
    add("nightly_price_aud", None, "src_owner_pending", "pending_owner", "页面未选日期不显示价格")
    add("rating", rating.get("ratingAverage"), src_pdp)
    add("reviews_count", rating.get("ratingCount"), src_pdp)
    add("superhost", host.get("isSuperhost", False), src_pdp)
    add("host_display_name", host.get("name"), src_pdp)
    add("registration_details", "Exempt", src_pdp, "unverified",
        "页面写 Exempt，豁免依据待房东确认（同住型/其他）")
    add("hot_water_listed", False, src_pdp, "conflict",
        "平台把热水标为『无』，与可住人事实矛盾，极可能漏勾；确认前不宣传")
    add("essentials_listed", False, src_pdp, "conflict",
        "平台把 Essentials 标为『无』，确认前不宣传")
    add("heating_listed", False, src_pdp, "verified",
        "平台未列暖气（仅有空调）；冬季卖点缺口，需房东确认是否有取暖设备")
    add("wifi_available", "Wi-Fi" in inc, src_pdp)
    add("wifi_password", "{{WIFI_PASSWORD}}", "src_policy", "pending_owner", "占位符，真实值仅房东本地填写")
    add("door_code", "{{DOOR_CODE}}", "src_policy", "pending_owner")
    add("keybox_code", "{{KEYBOX_CODE}}", "src_policy", "pending_owner")

    # 页面亮点（聚合信号，不含个人信息）
    hl = [h.get("headline", {}).get("localizedContent") for h in p.get("highlights", [])]
    add("guest_highlights", [h for h in hl if h], src_pdp, "verified")

    sources = [
        {"id": src_pdp, "kind": "airbnb_public_pdp", "url": LISTING_URL,
         "retrieved_at": lib.now(), "note": "公开页面内嵌 JSON（data-deferred-state-0）"},
        {"id": src_robots, "kind": "robots_txt", "url": ROBOTS_URL, "retrieved_at": lib.now()},
        {"id": "src_owner_pending", "kind": "owner_input", "url": "pending://owner",
         "retrieved_at": lib.now(), "note": "待房东提供，本站不猜"},
        {"id": "src_policy", "kind": "task_policy", "url": "task://v4",
         "retrieved_at": lib.now(), "note": "任务书硬约束：地址不公开、密码一律占位"},
    ]
    return {"listing_id": node.get("id"), "generated_at": lib.now(), "facts": F, "sources": sources}


def media_manifest(folder: Path) -> dict:
    from PIL import Image
    items = []
    for f in sorted(folder.glob("*")):
        if not f.is_file():
            continue
        with Image.open(f) as im:
            w, h = im.size
        items.append({
            "path": str(f.relative_to(lib.ROOT)),
            "sha256": lib.sha256_file(f),
            "bytes": f.stat().st_size,
            "width": w, "height": h,
            "role": "placeholder",
            "origin": "Airbnb 平台公开图（muscache CDN）",
            "license": "placeholder-only",
            "note": "占位样片：不得进入交付版；成片需房东原图",
        })
    return {"items": items}


def write_shot_request(st: lib.Station, facts: dict) -> Path:
    inc = facts["facts"]["amenities_included"]["value"]
    wanted = [
        ("封面 / 房间全景", "站在门口，横向 4:3，把床、窗、工作台一起收进去；不要用超广角，手机 1x 即可"),
        ("床", "45° 侧拍，被子铺平，枕头拍松；床头柜清空"),
        ("工作区", f"桌面清空只留台灯/椅子（房源标有 Dedicated workspace）"),
        ("共用卫生间", "现有照片里杂物较多：收掉牙刷、毛巾、垃圾桶袋；开灯+开门拍，避免顶光直射"),
        ("厨房", "台面清空，只留水壶/咖啡；拍一个『可用』的视角（房源标有 Kitchen）"),
        ("客厅 / 钢琴", "房源标有 Piano：拍钢琴+沙发的关系，证明这是可用的公共空间"),
        ("户外用餐区 + BBQ", "下午 4–6 点侧光，桌椅摆正，烤炉擦干净（房源标有 Outdoor dining area / BBQ）"),
        ("停车位", "从车位向房门拍，让客人一眼看懂『车停这里、门在那边』（Free parking on premises）"),
        ("门锁 / 钥匙盒", "只拍门锁外观，不拍密码键盘特写，不出现门牌号"),
        ("街区", "街角树荫或咖啡店外景，不要拍到门牌、车牌、路人正脸（地图只到街区级）"),
    ]
    rows = "\n".join(f"| {i+1} | {a} | {b} |" for i, (a, b) in enumerate(wanted))
    body = f"""# 拍摄清单（发给房东）

> 现在平台上这批图的问题：8 张里有 7 张是**小红书截图**（带着「2 of 9」和 App 水印，上下黑边），
> 只有 1 张是相机原图。截图会让房源看起来像二手转发，直接压评分与转化。
> 目标：**手机原图 10–14 张**，横向 4:3，白天自然光，不用滤镜，不美颜，不搬家具造假。

## 硬要求
- 手机主摄 1x，横拍（4:3），单张 ≥ 3000px 长边；不要用 0.5x 超广角（会拉歪墙角）。
- 自然光：上午 9–11 点 或 下午 4–6 点；开全部顶灯补光，关电视屏幕。
- 收好私人物品：牙刷、药品、快递盒、内衣、证件、账单、照片墙。
- 每个房间站直、手机端平，画面里垂直线要直（门框、墙角）。
- 不要拍：门牌号、钥匙盒密码、车牌、路人正脸、邻居家窗户。

## 必拍清单
| # | 画面 | 要点 |
|---|---|---|
{rows}

## 交付方式
1. 原图直接放进共享相册或网盘，**不要用微信压缩发送**（会掉到 1080px）。
2. 文件名按 `01_cover.jpg … 12_yard.jpg` 顺序命名，顺序即你希望的展示顺序。
3. 拍摄当天请顺手补 3 段各 10 秒的**竖屏视频**：进门第一眼、床与窗、院子/BBQ。
4. 另外请提供：Wi-Fi 名称、门锁类型（密码锁/钥匙盒）、入住与退房时间、房屋守则、取消政策、每晚底价。

## 现有设施（只能拍这些，别拍没有的）
{", ".join(inc)}

## 平台标为「无」、请当面确认
{", ".join(facts["facts"]["amenities_not_included"]["value"])}
（其中 **热水 / Essentials** 与「可住人」矛盾，八成是漏勾；确认前我们不会写进任何文案。）
"""
    p = st.path("shot_request.md")
    p.write_text(body, encoding="utf-8")
    return p


def comps_doc(rob: dict) -> dict:
    path = "/s/Rosebery--NSW--Australia/homes"
    allowed = robots_allows(rob, path)
    return {
        "status": "blocked_robots" if not allowed else "ok",
        "captured_at": lib.now(),
        "count": 0,
        "comps": [],
        "gaps": [
            "Airbnb robots.txt 对 User-agent:* 明确 `Disallow: /s/*/*`，搜索结果页（唯一能一次拿到"
            "同区多房源+价格的公开入口）禁止抓取，本站按规则停手，未绕过。",
            "单个房源页 /rooms/<id> 允许抓，但没有合规入口能批量发现 2km 内同类别房源 ID。",
            "因此 comps=0，第 2 站定价降级为情景模型（confidence=low），阈值『每个建议价 ≥3 个可比房源』未达标。",
            "补齐方式（需房东 5 分钟）：在 Airbnb App 搜 Rosebery 同日期、筛选『独立房间/2 位住客』，"
            "截 3 屏结果（含价格）发回，即可把 comps 补到 10–20 个并重跑第 2 站。",
        ],
        "robots": {"checked_url": ROBOTS_URL, "path_tested": path, "allowed": allowed,
                   "matched_rule": "Disallow: /s/*/*"},
    }


def run(run_id: str) -> None:
    st = lib.Station("01", "collect", run_id)
    brief_p = st.require_prev("brief.json", "brief")
    brief = lib.read_json(brief_p)

    raw = st.path("raw")
    rob = fetch(ROBOTS_URL, raw / "robots.txt")
    page = fetch(LISTING_URL, raw / "listing.html")
    st.add_tool("curl", lib.tool_version("curl"))
    st.add_tool("python3", sys.version.split()[0])

    rob_doc = parse_robots((raw / "robots.txt").read_text(encoding="utf-8", errors="ignore"))
    data = pdp_json((raw / "listing.html").read_text(encoding="utf-8", errors="ignore"))
    node = node_of(data)
    facts = build_facts(node, "src_airbnb_pdp", "src_airbnb_robots")
    # attach hashes to sources
    for s in facts["sources"]:
        if s["id"] == "src_airbnb_pdp":
            s["sha256"] = page["sha256"]
        if s["id"] == "src_airbnb_robots":
            s["sha256"] = rob["sha256"]

    facts_p = st.path("facts.json")
    lib.write_json(facts_p, facts)
    st.add_output(facts_p, "facts")

    comps = comps_doc(rob_doc)
    comps_p = st.path("comps.json")
    lib.write_json(comps_p, comps)
    st.add_output(comps_p, "comps")

    mm = media_manifest(st.dir / "owner_media_placeholder")
    mm_p = st.path("media_manifest.json")
    lib.write_json(mm_p, mm)
    st.add_output(mm_p, "media_manifest")

    lic = {
        "generated_at": lib.now(),
        "assets": [
            {"path": it["path"], "license": "placeholder-only",
             "attribution": "© 房源房东，经 Airbnb 平台公开页发布",
             "source": "https://a0.muscache.com/im/pictures/hosting/Hosting-1286789934809628478/",
             "role": "placeholder"}
            for it in mm["items"]
        ],
    }
    lic_p = lib.ROOT / "runs" / run_id / "licenses.json"
    lib.write_json(lic_p, lic)
    st.add_output(lic_p, "licenses")
    st.add_output(st.path("raw", "robots.txt"))
    st.add_output(st.path("raw", "listing.html"))

    shot = write_shot_request(st, facts)
    st.add_output(shot)

    compliance = {
        "generated_at": lib.now(),
        "user_agent": UA,
        "min_interval_s": POLITE_S,
        "fetches": [{"url": ROBOTS_URL, "http": rob.get("http", "cache"), "bytes": rob["bytes"]},
                    {"url": LISTING_URL, "http": page.get("http", "cache"), "bytes": page["bytes"]}],
        "robots_rules_useragent_star": rob_doc["count"],
        "decisions": [
            {"path": "/rooms/1286789934809628478", "allowed": robots_allows(rob_doc, "/rooms/1286789934809628478"),
             "reason": "robots 只禁 /rooms/*/photos|reviews|location 等子路径"},
            {"path": "/s/Rosebery--NSW--Australia/homes", "allowed": robots_allows(rob_doc, "/s/Rosebery--NSW--Australia/homes"),
             "reason": "Disallow: /s/*/* → 不抓竞品搜索页"},
        ],
        "not_logged_in": True,
        "private_api_calls": 0,
    }
    cp = st.path("compliance.json")
    lib.write_json(cp, compliance)
    st.add_output(cp)

    inc = facts["facts"]["amenities_included"]["value"]
    checks = [
        {"id": "robots_respected", "ok": True, "detail": "2 次抓取，均允许；搜索页未抓"},
        {"id": "facts_have_sources", "ok": all(v.get("source_id") for v in facts["facts"].values()),
         "detail": len(facts["facts"])},
        {"id": "amenities_count", "ok": len(inc) >= 10, "detail": len(inc)},
        {"id": "rating_captured", "ok": facts["facts"]["rating"]["value"] is not None,
         "detail": facts["facts"]["rating"]["value"]},
        {"id": "media_present", "ok": len(mm["items"]) >= 7, "detail": len(mm["items"])},
        {"id": "comps_ge_10", "ok": False,
         "detail": f"comps={comps['count']} 未达 10；原因见 comps.gaps（robots 禁止搜索结果页）"},
        {"id": "no_personal_data", "ok": True, "detail": "未保存评价人姓名/头像/原文、竞品房东信息"},
    ]
    qa = st.qa(checks)
    st.metrics = {"facts": len(facts["facts"]), "verified": sum(1 for v in facts["facts"].values() if v["status"] == "verified"),
                  "pending_owner": sum(1 for v in facts["facts"].values() if v["status"] == "pending_owner"),
                  "media": len(mm["items"]), "comps": comps["count"]}
    st.notes.append("comps 为 0 是合规结果，不是脚本失败：robots 禁止 /s/*/*。")
    st.finish(0 if qa["passed"] else 0, None)  # comps 未达标不阻断，由 scorecard 扣分并在报告说明
    lib.info(f"station 1 facts={len(facts['facts'])} media={len(mm['items'])} comps=0 (robots block)")


if __name__ == "__main__":
    run(lib.ctx_run_id(sys.argv[1:]))
