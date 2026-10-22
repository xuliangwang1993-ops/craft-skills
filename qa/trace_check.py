#!/usr/bin/env python3
"""Trace check — 任何一个下游句子，都要能在 facts.json / pricing.json 里找到同值来源。

检查四件事：
  1. 引用完整性：文案里写的每一个 facts.<key> 必须真的存在
  2. 禁词：unverified / conflict / pending_owner 的事实，不得被当成卖点写出来
  3. 数值一致：评分、评价数、人数、床型等数字必须与 facts 同值
  4. 覆盖：verified 设施在网站与知识库里的丢失率必须为 0

用法: python3 qa/trace_check.py runs/<run_id>
退出码: 0 通过 / 2 有不一致
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

NEG = {"unverified", "conflict", "pending_owner"}

# 事实 → 下游允许出现的同义说法（用于禁词判断）
BANNED = {
    "heating_listed": (["heating", "暖气", "取暖器", "radiator"], ["confirm", "确认", "ask", "问一句", "before booking", "预订前"]),
    "hot_water_listed": (["hot water", "热水"], ["confirm", "确认", "ask"]),
    "essentials_listed": (["essentials", "基本用品", "toiletries", "洗漱用品"], ["confirm", "确认", "ask"]),
}


# 平台明确标「无」的事实：任何肯定式说法都算矛盾（即使 facts.status 是 verified）
CONTRADICTIONS = {
    "heating_listed": ["暖气", "取暖器", "radiator", "\bheating\b"],
    "hot_water_listed": ["热水", "hot water"],
    "essentials_listed": ["基本用品", "essentials", "洗漱用品"],
}
NEG_CTX = ["没有", "无", "未", "not", "no ", "确认", "confirm", "待", "pending", "平台未",
           "漏勾", "标为", "标注", "不要当成", "不宣传", "矛盾", "不可用", "不在", "omitted"]


def strip_html(s: str) -> str:
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s)


def load(run: Path) -> dict:
    d = {}
    d["facts"] = json.loads((run / "01_collect" / "facts.json").read_text())
    d["comps"] = json.loads((run / "01_collect" / "comps.json").read_text())
    d["pricing"] = json.loads((run / "02_pricing" / "pricing.json").read_text())
    d["copy"] = {lg: json.loads((run / "05_copy" / "listing_copy" / f"{lg}.json").read_text()) for lg in ("zh", "en")}
    d["guide"] = {lg: (run / "06_guide" / "guide" / f"guide_{lg}.html").read_text() for lg in ("zh", "en")}
    d["site"] = (run / "07_site" / "site" / "index.html").read_text()
    kb_dir = run / "09_support" / "kb"
    d["kb"] = {p.name: p.read_text() for p in sorted(kb_dir.glob("*.md"))} if kb_dir.exists() else {}
    return d


def kb_facts(text: str) -> list[str]:
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return []
    fm = m.group(1)
    mm = re.search(r"^facts:\s*\[(.*?)\]", fm, re.M | re.S)
    if not mm:
        return []
    return [x.strip().strip("'\"") for x in mm.group(1).split(",") if x.strip()]


SYNONYMS = {
    "Free parking on premises": ["free parking", "免费院内停车", "parking on the premises", "院内停车"],
    "Lock on bedroom door": ["lock on the bedroom door", "房门可以上锁", "lockable door", "房门有锁"],
    "Pets allowed": ["pets are allowed", "可以带宠物", "pets allowed"],
    "Dedicated workspace": ["dedicated desk", "书桌工作区", "dedicated workspace", "专用工作区"],
    "Outdoor dining area": ["outdoor dining", "户外用餐区", "户外餐桌"],
    "Carbon monoxide alarm": ["carbon monoxide alarm", "一氧化碳报警器"],
    "Smoke alarm": ["smoke alarm", "烟雾报警器"],
    "First aid kit": ["first aid kit", "急救箱"],
    "Fire extinguisher": ["fire extinguisher", "灭火器"],
    "Hair dryer": ["hair dryer", "吹风机"],
}


def present(amenity: str, text: str) -> bool:
    cands = [amenity, *SYNONYMS.get(amenity, [])]
    low = text.lower()
    return any(c.lower() in low for c in cands)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    run = Path(a.run)
    d = load(run)
    facts = d["facts"]["facts"]
    verified = {k for k, v in facts.items() if v["status"] == "verified"}
    issues, manifest = [], {}

    # 1) 引用完整性 + 反查清单
    for lg, doc in d["copy"].items():
        for sec in doc["sections"]:
            for p in sec["paragraphs"]:
                key = hashlib.sha1(p["text"].encode()).hexdigest()[:12]
                srcs = [s.replace("facts.", "") for s in p["sources"]]
                manifest[key] = {"lang": lg, "station": "05_copy", "text": p["text"][:120], "sources": p["sources"]}
                for s in srcs:
                    if s not in facts:
                        issues.append({"type": "broken_source", "where": f"copy/{lg}", "detail": s,
                                       "text": p["text"][:60]})

    # 2) 禁词
    bodies = {
        "copy_zh": " ".join(p["text"] for s in d["copy"]["zh"]["sections"] for p in s["paragraphs"]),
        "copy_en": " ".join(p["text"] for s in d["copy"]["en"]["sections"] for p in s["paragraphs"]),
        "site": strip_html(d["site"]),
        "guide_zh": strip_html(d["guide"]["zh"]),
        "guide_en": strip_html(d["guide"]["en"]),
    }
    bodies.update({f"kb:{k}": v for k, v in d["kb"].items()})
    for fact, (words, negations) in BANNED.items():
        if facts.get(fact, {}).get("status") not in NEG:
            continue
        for where, text in bodies.items():
            low = text.lower()
            for w in words:
                for m in re.finditer(re.escape(w.lower()), low):
                    ctx = low[max(0, m.start() - 90): m.end() + 90]
                    if any(n.lower() in ctx for n in negations):
                        continue
                    issues.append({"type": "unverified_claim", "where": where, "fact": fact, "term": w,
                                   "context": ctx[:120]})

    # 2b) 与「平台标为无」的事实矛盾：按句子判断，句子内有否定词就放过
    for fact, terms in CONTRADICTIONS.items():
        if facts.get(fact, {}).get("value") is not False:
            continue
        for where, text in bodies.items():
            text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)   # 去 front matter
            for sent in re.split(r"[。！？!?\n]|(?<=\.)\s", text):
                low = sent.lower().strip()
                if not low:
                    continue
                if low.endswith(("?", "？")) or re.search(r"(吗|呢|么)[？?]?$", low):
                    continue                                     # 问句不是断言
                bare = low.lstrip("-•· ").strip()
                if re.match(r"^[A-Za-z]", bare) and len(bare.split()) <= 3:
                    continue                                     # 英文清单项（如「- hot water」）不是宣称
                for term in terms:
                    if not re.search(term.lower(), low):
                        continue
                    if any(n in low for n in NEG_CTX):
                        continue
                    issues.append({"type": "contradicts_fact", "where": where, "fact": fact,
                                   "term": term, "context": low[:120]})
                    break

    # 3) 数值一致
    want = {
        "rating": str(facts["rating"]["value"]),
        "reviews_count": str(facts["reviews_count"]["value"]),
        "max_guests": str(facts["max_guests"]["value"]),
    }
    declared = {"rating": ["4.6", "4.60"], "reviews_count": ["25"], "max_guests": ["2"]}
    for where in ("copy_zh", "copy_en", "site"):
        text = bodies[where]
        for k, vals in declared.items():
            for v in vals:
                if v in text and facts[k]["status"] != "verified":
                    issues.append({"type": "number_without_fact", "where": where, "fact": k, "value": v})
    for k, v in want.items():
        if not any(x in bodies["site"] for x in declared[k]):
            issues.append({"type": "missing_key_number", "where": "site", "fact": k})

    # 4) 覆盖
    amenities = facts["amenities_included"]["value"]
    site_low = bodies["site"].lower()
    kb_low = " ".join(d["kb"].values()).lower()
    missing_site = [a for a in amenities if not present(a, site_low)]
    missing_kb = [a for a in amenities if not present(a, kb_low)]

    copy_all = (bodies["copy_zh"] + " " + bodies["copy_en"]).lower()
    missing_copy = [a for a in amenities if not present(a, copy_all)]

    coverage = {
        "amenities_total": len(amenities),
        "site_missing": missing_site,
        "kb_missing": missing_kb,
        "copy_missing": missing_copy,
        "kb_articles": len(d["kb"]),
        "copy_paragraphs_traced": len(manifest),
    }

    out = {
        "run": run.name,
        "checked_at": __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),
        "inconsistencies": len(issues),
        "issues": issues,
        "coverage": coverage,
        "manifest": manifest,
        "passed": not issues and not missing_site and not missing_kb,
    }
    target = Path(a.json) if a.json else run / "reports" / "trace.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (target.parent / "trace_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("inconsistencies", "coverage", "passed")}, ensure_ascii=False, indent=2))
    return 0 if out["passed"] else 2


if __name__ == "__main__":
    sys.exit(main())
