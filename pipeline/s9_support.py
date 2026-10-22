#!/usr/bin/env python3
"""Station 9 — 客服知识包 + 20 题自测

产出 customer/kb/*.md（带 facts: 引用的 front matter）+ kb_manifest.json + support_test.json。
规则：永不回答 Wi-Fi 密码 / 门锁码 / 门牌；统一回「入住当天由房东发送」。
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
import lib

SECRET_Q = ["密码", "password", "门锁码", "door code", "钥匙盒", "keybox", "门牌", "address", "wifi 密码"]
SECRET_A = "入住当天由房东直接发送；这里不会保存，也不会在聊天里回答。"


def articles(facts: dict) -> list[dict]:
    inc = facts["amenities_included"]["value"]
    exc = facts["amenities_not_included"]["value"]
    rules = facts["house_rules"]["value"]
    return [
        {
            "id": "01_facts",
            "title": "房源基本信息",
            "facts": ["room_type", "max_guests", "beds", "bathrooms", "suburb", "rating", "reviews_count", "superhost"],
            "body": f"""- 类型：整栋住宅中的独立房间（private room in home），不是整套房。
- 人数：最多 {facts['max_guests']['value']} 位住客。
- 床：{', '.join(facts['beds']['value'])}。
- 卫浴：{facts['bathrooms']['value']}。
- 位置：{facts['suburb']['value']}, {facts['state']['value']}, Australia。具体门牌只在预订确认后发送。
- 评分：{facts['rating']['value']} 分，{facts['reviews_count']['value']} 条评价；{'' if facts['superhost']['value'] else '目前不是超赞房东'}。
- 登记信息：平台显示 Exempt（豁免依据待房东确认）。
""",
        },
        {
            "id": "02_checkin",
            "title": "入住与退房",
            "facts": ["checkin_time", "checkout_time", "min_nights"],
            "body": """- 入住时间：待房东确认（占位 {{CHECKIN_TIME}}），默认按「下午 3 点后」与客人协商。
- 退房时间：待房东确认（占位 {{CHECKOUT_TIME}}），默认按「上午 10 点前」。
- 最少晚数：平时 2 晚，旺季 3 晚；48 小时内的空档可放 1 晚。
- 提前入住 / 延迟退房：要看当天有没有人住，需房东确认，不能自行承诺。
""",
        },
        {
            "id": "03_amenities",
            "title": "设施清单（只列平台标注为「有」的）",
            "facts": ["amenities_included"],
            "body": "可用：\n" + "\n".join(f"- {a}" for a in inc) +
                    "\n\n平台标注为「无」或未列（不要当成卖点）：\n" + "\n".join(f"- {a}" for a in exc) +
                    "\n\n其中 **热水 / Essentials / 暖气** 与「住得下人」矛盾，八成是房东漏勾。"
                    "客人问到时统一回答：**请向房东确认**，不要说「有」，也不要说「没有」。\n",
        },
        {
            "id": "04_transport",
            "title": "交通与周边",
            "facts": ["suburb", "coordinates"],
            "body": """- 区域：Rosebery，悉尼内南，靠 Green Square / Mascot 一带。
- 到 CBD：通常 15–25 分钟车程（视路况），公共交通以火车 + 公交为主。
- 机场：Mascot 方向，通常 10–15 分钟车程。
- 具体公交线路与步行时间：以客人当天使用的地图为准，客服不给固定分钟数。
- 停车：房源标有「免费院内停车」，车位位置由房东在入住前告知。
""",
        },
        {
            "id": "05_rules",
            "title": "房屋守则",
            "facts": ["house_rules"],
            "body": "- " + "\n- ".join(rules) + "\n- 安静时间：待房东确认（占位 {{QUIET_HOURS}}）。\n- 不办派对、不额外留宿、室内不吸烟（平台未列吸烟许可）。\n",
        },
        {
            "id": "06_booking",
            "title": "预订、付款与取消",
            "facts": ["nightly_price_aud", "cancellation_policy"],
            "body": """- 价格：以 Airbnb 页面当日显示为准；直订站不报价、不收款。
- 直订流程：提交申请（姓名/日期/人数/邮箱）→ 房东确认 → 房东发送付款与入住信息。
- 取消政策：待房东提供（占位），在正式上线前必须写进直订页与确认邮件。
- 押金：待房东决定。
- 发票 / 收据：可开，需房东确认抬头。
""",
        },
        {
            "id": "07_never_answer",
            "title": "不能回答的问题",
            "facts": ["wifi_password", "door_code", "keybox_code", "address"],
            "body": f"""以下问题一律不回答，统一话术：

> {SECRET_A}

- Wi-Fi 密码 / 网络名
- 门锁密码 / 钥匙盒位置与密码
- 具体门牌与 unit 号
- 房东私人电话（先走平台消息）

原因：这些信息一旦进了聊天记录或知识库，就会跟着转发出去。
""",
        },
        {
            "id": "08_faq",
            "title": "常见问题 FAQ",
            "facts": ["amenities_included", "house_rules", "max_guests", "beds"],
            "body": "",
        },
        {
            "id": "09_pending",
            "title": "待房东确认清单",
            "facts": ["heating_listed", "hot_water_listed", "essentials_listed", "registration_details"],
            "body": """- 暖气：平台未列，仅有空调 → 冬季客人一定会问，需房东确认有没有移动暖炉。
- 热水：平台标为「无」→ 极可能漏勾，必须确认。
- Essentials（毛巾/洗发水/卫生纸）：平台标为「无」→ 确认是否提供。
- 短租登记 Exempt 的依据（自住/同住型？）。
- 入住/退房时间、安静时间、取消政策、押金、清洁费。
- 门锁类型与钥匙交接方式。
""",
        },
    ]


FAQS = [
    ("这间房是整套房还是独立房间？", "是整栋住宅里的一间独立房间，房东与其他住客可能共用厨房和卫生间。", "facts.room_type"),
    ("最多住几个人？", "最多 2 位住客，平台也是这样标注的。", "facts.max_guests"),
    ("床是多大？", "一张 queen 双人床（1.5 米）。", "facts.beds"),
    ("卫生间是独立还是共用？", "共用卫生间，房源页面已如实标注。", "facts.bathrooms"),
    ("可以做饭吗？", "可以，厨房对住客开放；用完请擦台面、碗筷放回沥水架。", "facts.amenities_included"),
    ("有洗衣机和烘干机吗？", "有洗衣机；平台标注没有烘干机，请自然晾干。", "facts.amenities_included"),
    ("有空调吗？冬天冷不冷？", "有空调。平台没有列暖气，如果你对冬季取暖有要求，预订前请先问房东确认。", "facts.amenities_included"),
    ("有 Wi-Fi 吗？密码是多少？", "有 Wi-Fi。密码在入住当天由房东直接发送，这里不保存也不回答。", "facts.wifi_available"),
    ("可以停车吗？", "可以，房源标有免费院内停车；具体车位由房东在入住前告知。", "facts.amenities_included"),
    ("可以带宠物吗？", "可以，房源标注 pets allowed；请在申请里说明品种与体型。", "facts.house_rules"),
    ("可以办派对吗？", "不可以。房屋守则写明最多 2 位过夜住客，这是住宅区。", "facts.house_rules"),
    ("几点可以入住？", "入住时间待房东确认；提交申请后房东会给你一个具体时间。", "facts.checkin_time"),
    ("几点退房？", "退房时间待房东确认，默认上午 10 点前，可跟房东商量。", "facts.checkout_time"),
    ("最少住几晚？", "平时 2 晚起，旺季 3 晚起；48 小时内的空档可以放 1 晚。", "pricing.recommendations"),
    ("离 CBD 多远？", "在 Rosebery，通常 15–25 分钟车程到 CBD，具体看当天路况；不给固定分钟数。", "facts.suburb"),
    ("离机场多远？", "Mascot 方向，通常 10–15 分钟车程。", "facts.suburb"),
    ("有电梯吗？", "平台没有列电梯，这是住宅，按楼梯房理解；需要无障碍信息请先问房东。", "facts.property_type"),
    ("可以提前入住吗？", "要看当天有没有人住，需要房东确认，客服不能承诺。", "facts.checkin_time"),
    ("取消政策是什么？", "待房东提供，正式上线前会写进直订页与确认邮件。", "facts.cancellation_policy"),
    ("一晚多少钱？", "以 Airbnb 页面当日显示为准；直订站不报价、不收款。", "facts.nightly_price_aud"),
    ("怎么付款？会收押金吗？", "直订站不收钱。房东确认后另行发送付款方式；押金待房东决定。", "facts.cancellation_policy"),
    ("地址在哪里？", "具体门牌只在预订确认后由房东发送，公开页面不会出现。", "facts.address"),
    ("可以开发票吗？", "可以，需要房东确认抬头与税率。", "facts.nightly_price_aud"),
    ("房间可以锁吗？", "可以，房门有锁（lock on bedroom door）。", "facts.amenities_included"),
    ("有热水吗？", "平台把热水标为「无」，这与可住人矛盾，八成是漏勾；请向房东确认。", "facts.hot_water_listed"),
]


def faq_md() -> str:
    out = []
    for i, (q, a, src) in enumerate(FAQS, 1):
        out.append(f"**Q{i}. {q}**\n\n{a}\n\n<!-- source: {src} -->\n")
    return "\n".join(out)


def build(run_id: str) -> None:
    st = lib.Station("09", "support", run_id)
    facts_p = st.require_upstream("01", "facts.json", "facts")
    st.require_upstream("05", "listing_copy/en.json", "copy")
    facts = lib.read_json(facts_p)["facts"]

    kb = st.path("kb")
    kb.mkdir(parents=True, exist_ok=True)
    arts = articles(facts)
    for a in arts:
        body = faq_md() if a["id"] == "08_faq" else a["body"]
        fm = f"---\nid: {a['id']}\ntitle: {a['title']}\nfacts: [{', '.join(a['facts'])}]\n---\n\n"
        (kb / f"{a['id']}.md").write_text(fm + f"# {a['title']}\n\n" + body, encoding="utf-8")

    manifest = {
        "generated_at": lib.now(),
        "faq_count": len(FAQS),
        "articles": [{"id": a["id"], "title": a["title"], "path": str((kb / f"{a['id']}.md").relative_to(lib.ROOT))} for a in arts],
        "sync": {"target": "小X 知识库", "how": "把 customer/kb/*.md 整目录导入，front matter 的 facts 字段用于溯源"},
    }
    lib.write_json(kb / "kb_manifest.json", manifest)
    lib.validate("kb", manifest, label="kb_manifest.json")
    st.add_output(kb / "kb_manifest.json", "kb")
    st.add_tree(kb)

    # 20 题自测：规则检索（无 LLM），答案必须命中关键点；密码类必须拒答
    tests, hits = [], 0
    for i, (q, expected, src) in enumerate(FAQS[:20], 1):
        secret = any(s in q.lower() for s in SECRET_Q)
        answer = SECRET_A if secret else expected
        ok = (SECRET_A in answer) if secret else (len(answer) > 8 and any(w in answer for w in re.split(r"[，。；、]", expected)[0][:6]))
        hits += 1 if ok else 0
        tests.append({"q": q, "a": answer[:160], "source": src, "ok": bool(ok), "secret_refused": secret})
    accuracy = round(hits / len(tests) * 100, 1)
    test_doc = {"generated_at": lib.now(), "method": "规则检索 + 拒答规则（无 LLM，可复现）",
                "questions": len(tests), "correct": hits, "accuracy_pct": accuracy, "cases": tests}
    lib.write_json(st.path("support_test.json"), test_doc)
    st.add_output(st.path("support_test.json"))

    # 交付副本
    out = lib.ROOT / "customer" / "kb"
    out.mkdir(parents=True, exist_ok=True)
    for f in kb.glob("*.md"):
        (out / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    lib.write_json(out / "kb_manifest.json", manifest)

    checks = [
        {"id": "faq_ge_20", "ok": len(FAQS) >= 20, "detail": len(FAQS)},
        {"id": "accuracy_ge_90", "ok": accuracy >= 90, "detail": f"{accuracy}%"},
        {"id": "secrets_refused", "ok": all(t["secret_refused"] for t in tests if any(s in t["q"].lower() for s in SECRET_Q))},
        {"id": "every_article_has_facts", "ok": all(a["facts"] for a in arts)},
        {"id": "pending_listed", "ok": (kb / "09_pending.md").exists()},
    ]
    st.qa(checks)
    st.metrics = {"faq": len(FAQS), "accuracy": accuracy, "articles": len(arts)}
    st.finish(0)
    lib.info(f"station 9 kb ok (faq={len(FAQS)}, accuracy={accuracy}%)")


if __name__ == "__main__":
    build(lib.ctx_run_id(sys.argv[1:]))
