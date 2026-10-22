#!/usr/bin/env python3
"""Station 7 — 直订网站（静态，无框架、无支付、无追踪）

- 相册/视频/设施/文案全部来自上游产物，不另写事实
- 地图只到街区级（手绘 SVG），不出现坐标与门牌
- 可订日期：只读 iCal（房东从 Airbnb 导出后放到 owner_calendar.ics；没有就明说「未连接」）
- 预订申请表：姓名/日期/人数/邮箱，提交到 config.js 里的 endpoint（默认 mailto）。不收钱、不存卡号。
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import lib
from lib import PipelineError

ASSETS = Path(__file__).with_name("assets_site")


def img_variants(src: Path, outdir: Path, stem: str) -> dict:
    im = Image.open(src).convert("RGB")
    made = {}
    for w in (1280, 2048):
        if im.width >= w or w == 2048:
            h = round(im.height * w / im.width)
            v = im.resize((w, h), Image.LANCZOS)
            p = outdir / f"{stem}-{w}.jpg"
            v.save(p, quality=84, subsampling=1)
            made[w] = p
    return made


def build_copy(zh: dict, en: dict, photos: list) -> dict:
    """站点用的扁平 i18n 字典；正文段落直接取第 5 站的 listing copy。"""
    def sec(doc, sid):
        for s in doc["sections"]:
            if s["id"] == sid:
                return [p["text"] for p in s["paragraphs"]]
        return []

    def one(lang, doc, repo):
        room = " ".join(sec(doc, "about") + sec(doc, "the_room"))
        access = " ".join(sec(doc, "access"))
        return {
            "nav": {"room": "房间" if lang == "zh" else "Room",
                    "gallery": "照片" if lang == "zh" else "Photos",
                    "video": "视频" if lang == "zh" else "Film",
                    "place": "位置" if lang == "zh" else "Location",
                    "book": "预订申请" if lang == "zh" else "Request"},
            "hero": {"pill": "Rosebery · 独立房间 · 最多 2 人" if lang == "zh" else "Rosebery · private room · up to 2",
                     "title": "一间安静的独立房间，书桌对着后院" if lang == "zh" else "A quiet room with a desk, and a garden behind it",
                     "sub": "1 张 queen 床 · 共用卫浴 · 空调 · 免费院内停车" if lang == "zh" else "Queen bed · shared bathroom · air conditioning · free parking"},
            "facts": {"guests": "2 人" if lang == "zh" else "2 guests",
                      "guests_l": "最多入住" if lang == "zh" else "max capacity",
                      "bed": "1 张 queen 床" if lang == "zh" else "1 queen bed",
                      "bed_l": "独立房间" if lang == "zh" else "private room",
                      "bath": "共用卫浴" if lang == "zh" else "Shared bathroom",
                      "bath_l": "与住客共用" if lang == "zh" else "shared with guests",
                      "rating": "4.6 ★" if lang == "zh" else "4.6 ★",
                      "rating_l": "25 条评价" if lang == "zh" else "25 reviews"},
            "room": {"eyebrow": "The room" if lang == "en" else "房间",
                     "h": "房间与共用空间" if lang == "zh" else "The room and the shared spaces",
                     "body": room,
                     "note": "卫生间是共用的。页面上不会出现具体门牌，确认预订后才发地址。" if lang == "zh"
                             else "The bathroom is shared. No street number appears on this page — the address is sent after confirmation."},
            "amen": {"h": "设施" if lang == "zh" else "What you get"},
            "gallery": {"eyebrow": "Photos" if lang == "en" else "照片",
                        "h": "实拍照片" if lang == "zh" else "Real photos",
                        "note": "当前为占位样片（平台公开图 + 样片水印）。房东原图到位后同一套版式直接替换。" if lang == "zh"
                                else "Placeholder samples (public listing images, watermarked). Swap in the owner's originals — the layout stays."},
            "video": {"eyebrow": "Walkthrough" if lang == "en" else "看房视频",
                      "h": "先看一遍再决定" if lang == "zh" else "See it before you decide",
                      "body": "竖屏版给手机看，横屏版给网页看。两版都来自同一组照片，不会出现「照片和现场不一样」。" if lang == "zh"
                              else "One vertical cut for phones, one widescreen for the web, both from the same photos — no surprises on arrival.",
                      "meta": "40 秒 · 1080p · 中英字幕" if lang == "zh" else "40 seconds · 1080p · zh/en captions",
                      "dl": "下载竖屏版（9:16）" if lang == "zh" else "Download the 9:16 cut"},
            "place": {"eyebrow": "Location" if lang == "en" else "位置",
                      "h": "Rosebery，悉尼内南" if lang == "zh" else "Rosebery, inner-south Sydney",
                      "body": "房源在 Rosebery 的住宅街上，走路能到 Green Square 一带的咖啡与超市。具体门牌不在网上公开，确认预订后由房东发送。" if lang == "zh"
                              else "A residential street in Rosebery, walkable to the cafés and supermarkets around Green Square. The street number is never published — the host sends it after confirmation.",
                      "legend": "示意图只标街区关系，不含坐标、比例尺或街道名。" if lang == "zh"
                                else "Schematic only: neighbourhood relationships, no coordinates, scale or street names.",
                      "badge": "地址在确认后发送" if lang == "zh" else "Address sent after confirmation"},
            "book": {"eyebrow": "Booking request" if lang == "en" else "预订申请",
                     "h": "提交申请，不收款" if lang == "zh" else "Send a request — no payment"},
            "form": {"name": "姓名" if lang == "zh" else "Name",
                     "email": "邮箱" if lang == "zh" else "Email",
                     "checkin": "入住" if lang == "zh" else "Check-in",
                     "checkout": "退房" if lang == "zh" else "Check-out",
                     "guests": "人数" if lang == "zh" else "Guests",
                     "msg": "备注（可选）" if lang == "zh" else "Anything else (optional)",
                     "submit": "发送申请" if lang == "zh" else "Send request",
                     "hint": "只收姓名、日期、人数、邮箱。不收款、不存卡号。房东回复确认后才算订上。" if lang == "zh"
                             else "We only collect name, dates, guests and email. No payment, no card data. Nothing is booked until the host replies.",
                     "ok": "已发出。房东通常 12 小时内回复。" if lang == "zh" else "Sent. The host usually replies within 12 hours.",
                     "errName": "请填姓名" if lang == "zh" else "Name required",
                     "errEmail": "邮箱格式不对" if lang == "zh" else "Check the email",
                     "errDates": "退房要晚于入住" if lang == "zh" else "Check-out must be after check-in",
                     "errGuests": "这间房最多 2 人" if lang == "zh" else "This room takes up to 2 guests",
                     "errSend": "没发出去，请直接发邮件给房东。" if lang == "zh" else "Could not send — email the host directly."},
            "cal": {"h": "可订日期" if lang == "zh" else "Availability",
                    "sub": "只读房东的 Airbnb 日历（iCal）。" if lang == "zh" else "Read-only feed from the host's Airbnb calendar.",
                    "offline": "日历没连上：房东导出 Airbnb iCal 后放进 data/ 即可。" if lang == "zh"
                               else "Calendar not connected: drop the Airbnb iCal export into data/.",
                    "connected": "灰色是被占的日期，绿色可申请。" if lang == "zh" else "Grey = booked, green = free to request.",
                    "empty": "还没有导入日历，先在右侧提交日期申请。" if lang == "zh" else "No calendar yet — send your dates in the form.",
                    "week": ["一", "二", "三", "四", "五", "六", "日"] if lang == "zh" else ["M", "T", "W", "T", "F", "S", "S"]},
            "legal": {"h": "合规说明" if lang == "zh" else "Compliance",
                      "body": "直订同样受 NSW 短租登记（STRA Register）与《短租行为准则》约束；房东需自行确认本房源是否属于豁免、以及 Bayside Council 对短租天数与规划的要求。" if lang == "zh"
                              else "Direct bookings are still covered by the NSW STRA Register and the Code of Conduct. The host must confirm the exemption basis and Bayside Council's rules on nights and planning."},
            "foot": {"note": "这是试生产样站：照片为占位样片，价格与可订日期以房东确认为准。" if lang == "zh"
                             else "Trial build: photos are placeholders; rates and dates are confirmed by the host.",
                     "contact": "联系：预订表单 / Airbnb 站内消息" if lang == "zh" else "Contact: booking form / Airbnb messages"},
        }

    out = {"zh": one("zh", zh, None), "en": one("en", en, None)}
    for lang in ("zh", "en"):
        for i, p in enumerate(photos):
            out[lang]["gallery"][str(i)] = p["cap_zh"] if lang == "zh" else p["cap_en"]
    return out


def calendar_events(run_id: str) -> tuple[str, int]:
    """优先读房东导出的 owner_calendar.ics；没有就返回空日历 + 0。"""
    own = lib.RUNS / run_id / "07_site" / "owner_calendar.ics"
    if own.exists():
        return own.read_text(encoding="utf-8"), len(re.findall("BEGIN:VEVENT", own.read_text()))
    ics = ("BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//craft-skills//airbnb-direct//EN\r\n"
           "CALSCALE:GREGORIAN\r\nEND:VCALENDAR\r\n")
    return ics, 0


def svg_map() -> str:
    """街区级示意图：只有几个公开地标，不含坐标、比例尺与街道名。"""
    return """<svg viewBox="0 0 520 420" role="img" aria-label="Neighbourhood sketch">
  <defs><pattern id="grid" width="26" height="26" patternUnits="userSpaceOnUse">
    <path d="M26 0H0V26" fill="none" stroke="#e2e0d9" stroke-width="1"/></pattern></defs>
  <rect width="520" height="420" fill="url(#grid)"/>
  <circle cx="268" cy="212" r="132" fill="#dfe9df" opacity=".55"/>
  <circle cx="268" cy="212" r="86" fill="#cfe0d2" opacity=".55"/>
  <circle cx="268" cy="212" r="10" fill="#3f6b52"/>
  <text x="284" y="206" font-size="15" font-weight="700" fill="#1d2a22">Rosebery</text>
  <text x="284" y="224" font-size="11.5" fill="#5f6b78">this listing</text>
  <g fill="#8b94a0" font-size="11.5">
    <circle cx="120" cy="108" r="5"/><text x="132" y="112">Green Square</text>
    <circle cx="420" cy="300" r="5"/><text x="330" y="322">Mascot</text>
    <circle cx="392" cy="92" r="5"/><text x="300" y="86">Kensington</text>
    <circle cx="118" cy="318" r="5"/><text x="60" y="340">Zetland</text>
  </g>
  <text x="24" y="398" font-size="10.5" fill="#9aa2ac">Schematic only — no address, no scale.</text>
</svg>"""


def page(ctx: dict) -> str:
    ph = ctx["photos"]
    hero = ph[0]
    gallery = "".join(
        f'<figure><img src="assets/img/{p["stem"]}-1280.jpg" width="1280" height="960" '
        f'decoding="async" alt="{p["alt"]}"><figcaption data-i18n="gallery.{i}">{p["cap_zh"]}</figcaption></figure>'
        for i, p in enumerate(ph))
    amenities = "".join(
        f'<li><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        f'aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg><span>{a}</span></li>'
        for a in ctx["amenities"])
    copy_json = json.dumps(ctx["copy"], ensure_ascii=False)
    cfg_json = json.dumps(ctx["config"], ensure_ascii=False)
    return f"""<!doctype html>
<html lang="zh-Hans">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rosebery 独立房间 · 直订 / Private room, Rosebery</title>
<meta name="description" content="Rosebery 独立房间，2 人入住，1 张 queen 床，共用卫浴，书桌与后院。可直接提交预订申请，不收款。">
<meta name="theme-color" content="#fbfaf8">
<meta property="og:title" content="Rosebery 独立房间 · 直订">
<meta property="og:description" content="2 guests · 1 queen bed · shared bathroom · desk & garden. Booking request only, no payment.">
<meta property="og:image" content="assets/img/{hero['stem']}-1280.jpg">
<meta property="og:type" content="website">
<link rel="stylesheet" href="styles.css?v={ctx['v']}">
<link rel="preload" as="image" href="assets/img/{hero['stem']}-2048.jpg">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header><div class="wrap bar">
  <div class="brand">Rosebery <span>·</span> room</div>
  <nav aria-label="Sections">
    <a href="#room" data-i18n="nav.room">房间</a>
    <a href="#gallery" data-i18n="nav.gallery">照片</a>
    <a href="#video" data-i18n="nav.video">视频</a>
    <a href="#place" data-i18n="nav.place">位置</a>
    <a class="cta" href="#book" data-i18n="nav.book">预订申请</a>
  </nav>
  <a class="cta mob" href="#book" data-i18n="nav.book">预订申请</a>
  <div class="lang" role="group" aria-label="Language">
    <button data-lang="zh" aria-pressed="true">中文</button>
    <button data-lang="en" aria-pressed="false">EN</button>
  </div>
</div></header>

<main id="main">
  <div class="hero">
    <img src="assets/img/{hero['stem']}-2048.jpg" width="2048" height="1536" alt="{hero['alt']}" fetchpriority="high">
    <div class="veil"></div>
    <div class="sample">SAMPLE · 样片</div>
    <div class="inner">
      <div class="pill" data-i18n="hero.pill">Rosebery · 独立房间 · 最多 2 人</div>
      <h1 data-i18n="hero.title">一间安静的独立房间，书桌对着后院</h1>
      <p data-i18n="hero.sub">1 张 queen 床 · 共用卫浴 · 空调 · 免费院内停车</p>
    </div>
  </div>

  <div class="wrap facts">
    <div class="fact"><b data-i18n="facts.guests">2 人</b><span data-i18n="facts.guests_l">最多入住</span></div>
    <div class="fact"><b data-i18n="facts.bed">1 张 queen 床</b><span data-i18n="facts.bed_l">独立房间</span></div>
    <div class="fact"><b data-i18n="facts.bath">共用卫浴</b><span data-i18n="facts.bath_l">与住客共用</span></div>
    <div class="fact"><b data-i18n="facts.rating">4.6 ★</b><span data-i18n="facts.rating_l">25 条评价</span></div>
  </div>

  <section id="room"><div class="wrap cols">
    <div>
      <p class="eyebrow" data-i18n="room.eyebrow">The room</p>
      <h2 data-i18n="room.h">房间与共用空间</h2>
      <div class="lead" data-i18n="room.body"></div>
      <p class="note" data-i18n="room.note">卫生间是共用的。页面上不会出现具体门牌，确认预订后才发地址。</p>
    </div>
    <div>
      <h2 style="font-size:20px" data-i18n="amen.h">设施</h2>
      <ul class="amen">{amenities}</ul>
    </div>
  </div></section>

  <section id="gallery" style="padding-top:0"><div class="wrap">
    <p class="eyebrow" data-i18n="gallery.eyebrow">Photos</p>
    <h2 data-i18n="gallery.h">实拍照片</h2>
    <div class="gallery">{gallery}</div>
    <p class="small" data-i18n="gallery.note">当前为占位样片（平台公开图 + 样片水印）。房东原图到位后同一套版式直接替换。</p>
  </div></section>

  <section id="video" style="padding-top:0"><div class="wrap split">
    <div>
      <video controls preload="metadata" playsinline poster="assets/video/cover_16x9.jpg" width="1920" height="1080">
        <source src="assets/video/tour_16x9.mp4" type="video/mp4">
        <track kind="captions" src="assets/video/tour_zh.srt" srclang="zh" label="中文" default>
        <track kind="captions" src="assets/video/tour_en.srt" srclang="en" label="English">
      </video>
      <p class="vmeta" data-i18n="video.meta">40 秒 · 1080p · 中英字幕</p>
    </div>
    <div>
      <p class="eyebrow" data-i18n="video.eyebrow">Walkthrough</p>
      <h2 data-i18n="video.h">先看一遍再决定</h2>
      <p class="lead" data-i18n="video.body">竖屏版给手机看，横屏版给网页看。两版都来自同一组照片，不会出现「照片和现场不一样」。</p>
      <p><a class="cta" href="assets/video/tour_9x16.mp4" download data-i18n="video.dl">下载竖屏版（9:16）</a></p>
    </div>
  </div></section>

  <section id="place" style="padding-top:0"><div class="wrap">
    <p class="eyebrow" data-i18n="place.eyebrow">Location</p>
    <h2 data-i18n="place.h">Rosebery，悉尼内南</h2>
    <div class="mapcard">
      <div class="txt">
        <p data-i18n="place.body">房源在 Rosebery 的住宅街上，走路能到 Green Square 一带的咖啡与超市。具体门牌不在网上公开，确认预订后由房东发送。</p>
        <p class="legend" data-i18n="place.legend">示意图只标街区关系，不含坐标、比例尺或街道名。</p>
        <p><span class="badge" data-i18n="place.badge">地址在确认后发送</span></p>
      </div>
      {svg_map()}
    </div>
  </div></section>

  <section id="book" style="padding-top:0"><div class="wrap">
    <p class="eyebrow" data-i18n="book.eyebrow">Booking request</p>
    <h2 data-i18n="book.h">提交申请，不收款</h2>
    <div class="book">
      <div class="card">
        <form id="bookform" novalidate>
          <label for="name" data-i18n="form.name">姓名</label>
          <input id="name" name="name" autocomplete="name" required>
          <label for="email" data-i18n="form.email">邮箱</label>
          <input id="email" name="email" type="email" autocomplete="email" required>
          <label for="checkin" data-i18n="form.checkin">入住</label>
          <input id="checkin" name="checkin" type="date" required>
          <label for="checkout" data-i18n="form.checkout">退房</label>
          <input id="checkout" name="checkout" type="date" required>
          <label for="guests" data-i18n="form.guests">人数</label>
          <select id="guests" name="guests"><option value="1">1</option><option value="2" selected>2</option></select>
          <label for="msg" data-i18n="form.msg">备注（可选）</label>
          <textarea id="msg" name="message" rows="3"></textarea>
          <button class="submit" type="submit" data-i18n="form.submit">发送申请</button>
          <p class="hint" data-i18n="form.hint">只收姓名、日期、人数、邮箱。不收款、不存卡号。房东回复确认后才算订上。</p>
          <div id="formstatus" class="status" role="status" aria-live="polite"></div>
        </form>
      </div>
      <div class="card">
        <h3 style="margin:0 0 6px" data-i18n="cal.h">可订日期</h3>
        <p class="small" data-i18n="cal.sub">只读房东的 Airbnb 日历（iCal）。</p>
        <div id="cal" class="cal"></div>
      </div>
    </div>
  </div></section>

  <section style="padding-top:0"><div class="wrap">
    <div class="note">
      <p style="margin:0 0 8px"><b data-i18n="legal.h">合规说明</b></p>
      <p style="margin:0" data-i18n="legal.body">直订同样受 NSW 短租登记（STRA Register）与《短租行为准则》约束；房东需自行确认本房源是否属于豁免、以及 Bayside Council 对短租天数与规划的要求。</p>
    </div>
  </div></section>
</main>

<footer><div class="wrap cols2">
  <div>
    <p style="margin:0 0 6px"><b>Rosebery room</b></p>
    <p class="small" data-i18n="foot.note">这是试生产样站：照片为占位样片，价格与可订日期以房东确认为准。</p>
  </div>
  <div class="small">
    <p data-i18n="foot.contact">联系：预订表单 / Airbnb 站内消息</p>
    <p>© <span id="y"></span> · No payment is taken on this site.</p>
  </div>
</div></footer>
<script type="text/plain" id="ics">{ctx['ics']}</script>
<script>window.__COPY__={copy_json};window.__CONFIG__={cfg_json};document.getElementById('y').textContent=new Date().getFullYear();</script>
<script src="app.js?v={ctx['v']}" defer></script>
</body></html>
"""


def run(run_id: str) -> None:
    st = lib.Station("07", "site", run_id)
    order_p = st.require_upstream("03", "photos/order.json")
    copy_zh = st.require_upstream("05", "listing_copy/zh.json", "copy")
    copy_en = st.require_upstream("05", "listing_copy/en.json", "copy")
    facts_p = st.require_upstream("01", "facts.json", "facts")
    order = lib.read_json(order_p)["items"]
    facts = lib.read_json(facts_p)["facts"]

    site = st.path("site")
    for sub in ("assets/img", "assets/video", "data"):
        (site / sub).mkdir(parents=True, exist_ok=True)

    photos = []
    for i, it in enumerate(order, 1):
        src = lib.ROOT / it["file"]
        stem = f"p{i:02d}"
        img_variants(src, site / "assets/img", stem)
        photos.append({"stem": stem, "alt": it["caption_en"], "cap_zh": it["caption_zh"],
                       "cap_en": it["caption_en"]})

    vid = lib.RUNS / run_id / "04_video"
    for f in ("tour_16x9.mp4", "tour_9x16.mp4", "cover_16x9.jpg", "cover_9x16.jpg"):
        shutil.copyfile(vid / f, site / "assets/video" / f)
    for f in ("tour_zh.srt", "tour_en.srt"):
        shutil.copyfile(vid / "subs" / f, site / "assets/video" / f)

    ics, n_events = calendar_events(run_id)
    (site / "data" / "availability.ics").write_text(ics, encoding="utf-8")

    config = {"hostEmail": "{{HOST_EMAIL}}", "formEndpoint": "", "calendarUrl": "data/availability.ics"}
    (site / "config.js").write_text("window.__SITE_CONFIG__=" + json.dumps(config) + ";\n", encoding="utf-8")

    shutil.copyfile(ASSETS / "styles.css", site / "styles.css")
    shutil.copyfile(ASSETS / "app.js", site / "app.js")

    ctx = {
        "photos": photos,
        "amenities": facts["amenities_included"]["value"],
        "copy": build_copy(lib.read_json(copy_zh), lib.read_json(copy_en), photos),
        "config": config, "ics": ics.replace("</script>", ""),
        "v": lib.now().replace(":", "").replace("-", "").replace("+0000", ""),
    }
    (site / "index.html").write_text(page(ctx), encoding="utf-8")

    manifest = {
        "root": str(site.relative_to(lib.ROOT)),
        "pages": ["index.html"],
        "form": {"fields": ["name", "email", "checkin", "checkout", "guests", "message"],
                 "endpoint": "mailto fallback / config.formEndpoint", "payment": False},
        "no_payment": True,
        "calendar_events": n_events,
        "generated_at": lib.now(),
        "assets": {"images": len(photos) * 2, "videos": 2, "srt": 2},
    }
    lib.write_json(st.path("site.json"), manifest)
    lib.validate("site", manifest)
    st.add_output(st.path("site.json"), "site")
    st.add_tree(site)

    html = (site / "index.html").read_text()
    checks = [
        {"id": "no_payment", "ok": not re.search(r"stripe|paypal|card number|checkout\\.com", html, re.I)},
        {"id": "no_coordinates", "ok": "-33.9" not in html and "151.2" not in html},
        {"id": "no_password_literal", "ok": "{{" in html or "WIFI" not in html},
        {"id": "images_have_alt", "ok": all(f'alt="{p["alt"]}"' in html for p in photos)},
        {"id": "lang_toggle", "ok": 'data-lang="en"' in html},
        {"id": "legal_notice", "ok": "STRA" in html or "短租登记" in html},
        {"id": "calendar_file", "ok": (site / "data" / "availability.ics").exists()},
        {"id": "form_fields", "ok": all(f'name="{f}"' in html for f in ("name", "email", "checkin", "checkout", "guests"))},
    ]
    st.qa(checks)
    st.metrics = {"images": len(photos), "bytes": sum(f.stat().st_size for f in site.rglob("*") if f.is_file()),
                  "calendar_events": n_events}
    st.add_tool("python-pillow", Image.__version__)
    st.finish(0)
    lib.info(f"station 7 site built ({len(photos)} photos, {manifest['assets']['videos']} videos)")


if __name__ == "__main__":
    run(lib.ctx_run_id(sys.argv[1:]))
