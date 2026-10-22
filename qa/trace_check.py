#!/usr/bin/env python3
"""trace_check — the chain's fact-integrity gate.

Walks the delivered films backwards:
    subtitle line  →  script shot  →  asset ids  →  fact source_ids  →  facts.json row

and fails (exit 1) if
  * any claim-shaped token in a subtitle (phone / price / shop name / address / hours)
    does not resolve to a `verified` fact or a customer-confirmed menu item;
  * a shot in script.json has no matching segment in the film;
  * a subtitle line in the delivered srt differs from the script.

Usage:
  python3 qa/trace_check.py runs/<run_id> [--json runs/<run_id>/06_qa/trace.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
from lib.common import media_info, read_json, write_json  # noqa: E402

PHONE = re.compile(r"(?:\+?61\s?)?0?2\s?\d{4}\s?\d{4}")
PRICE = re.compile(r"(?:A?\$|AUD\s?)\s?(\d+(?:\.\d{1,2})?)")
# "12.50" is a price, not a time: hours need a colon, or an am/pm marker.
HOURS = re.compile(r"\b\d{1,2}:\d{2}\s?(?:am|pm|AM|PM)?\b|\b\d{1,2}\s?(?:am|pm|AM|PM)\b")
ADDRESS = re.compile(r"\b(?:Shop|Suite|Unit)\s?\d+|\b\d+\s+[A-Z][a-z]+\s(?:Ave|Avenue|St|Street|Rd|Road)\b")
BRAND = re.compile(r"Slurp\s*Slurp(?:\s*Noodle)?", re.I)


def norm_phone(s: str) -> str:
    return re.sub(r"\D", "", s)


def srt_rows(path: Path) -> list:
    text = path.read_text(encoding="utf-8").strip()
    rows = []
    for block in re.split(r"\n\s*\n", text):
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if len(lines) >= 3 and "-->" in lines[1]:
            start, end = [p.strip() for p in lines[1].split("-->")]
            rows.append({"start": start, "end": end, "text": " ".join(lines[2:])})
    return rows


def check(run_dir: Path) -> dict:
    facts = read_json(run_dir / "01_collect/facts.json")
    menu = read_json(run_dir / "02_script/menu.json")
    script = read_json(run_dir / "02_script/script.json")
    manifest = read_json(run_dir / "01_collect/media_manifest.json")

    verified = {f["source_id"]: f for f in facts["facts"] if f["status"] == "verified"}
    all_facts = {f["source_id"]: f for f in facts["facts"]}
    assets = {a["asset_id"]: a for a in manifest["assets"]}
    menu_items = {m["item_id"]: m for m in menu["items"]}

    # every verified value, normalised for containment tests
    verified_text = []
    for f in verified.values():
        v = f["value"]
        if isinstance(v, str):
            verified_text.append(v)
        elif isinstance(v, (int, float)):
            verified_text.append(str(v))
        elif isinstance(v, dict):
            verified_text.extend(str(x) for x in v.values() if isinstance(x, str))

    mismatches = []
    lines = []

    videos = {}
    for aspect in ("9x16", "1x1", "16x9"):
        p = run_dir / "05_compose" / f"promo_{aspect}.mp4"
        if p.exists():
            videos[aspect] = media_info(p)

    # ---- per-shot reverse trace ------------------------------------------- #
    cursor = 0.0
    for shot in script["shots"]:
        entry = {
            "shot_id": shot["shot_id"],
            "start": round(cursor, 3),
            "end": round(cursor + shot["seconds"], 3),
            "sub_zh": shot["sub_zh"],
            "sub_en": shot["sub_en"],
            "asset_ids": shot["asset_refs"],
            "fact_refs": shot["fact_refs"],
            "source_ids": [],
            "menu_refs": shot.get("menu_refs", []),
            "sources": [],
        }
        for ref in shot["fact_refs"]:
            f = all_facts.get(ref)
            if f is None:
                mismatches.append({"kind": "unknown_fact_ref", "shot": shot["shot_id"], "ref": ref})
                continue
            entry["source_ids"].append(ref)
            entry["sources"].append({"source_id": ref, "field": f["field"], "value": f["value"],
                                     "status": f["status"], "ref": f["source"]["ref"]})
        for a in shot["asset_refs"]:
            if a not in assets:
                mismatches.append({"kind": "unknown_asset", "shot": shot["shot_id"], "ref": a})
        lines.append(entry)
        cursor += shot["seconds"]

    # ---- claim scan on every subtitle ------------------------------------- #
    checks = 0
    for entry in lines:
        text = entry["sub_zh"] + " " + entry["sub_en"]
        for m in PHONE.finditer(text):
            checks += 1
            num = norm_phone(m.group())
            if not any(norm_phone(v).endswith(num[-9:]) for v in verified_text if norm_phone(v)):
                mismatches.append({"kind": "unverified_phone", "shot": entry["shot_id"], "token": m.group()})
        for m in PRICE.finditer(text):
            checks += 1
            price = float(m.group(1))
            if not any(abs(price - float(i["price_aud"])) < 0.005 and i["status"] == "verified"
                       and i["in_video"] for i in menu_items.values()):
                mismatches.append({"kind": "unverified_price", "shot": entry["shot_id"], "token": m.group()})
        for m in HOURS.finditer(text):
            checks += 1
            mismatches.append({"kind": "hours_claim_without_verified_fact", "shot": entry["shot_id"],
                               "token": m.group()})
        for m in ADDRESS.finditer(text):
            checks += 1
            if not any(m.group().lower() in v.lower() for v in verified_text):
                mismatches.append({"kind": "unverified_address", "shot": entry["shot_id"], "token": m.group()})
        for m in BRAND.finditer(text):
            checks += 1
            if not any("Slurp Slurp" in v for v in verified_text):
                mismatches.append({"kind": "unverified_brand", "shot": entry["shot_id"], "token": m.group()})

    # ---- delivered srt must equal the script ------------------------------- #
    for name, key in (("zh.srt", "sub_zh"), ("en.srt", "sub_en")):
        p = run_dir / "05_compose" / name
        if not p.exists():
            mismatches.append({"kind": "missing_srt", "file": name})
            continue
        rows = srt_rows(p)
        if len(rows) != len(script["shots"]):
            mismatches.append({"kind": "srt_line_count", "file": name,
                               "srt": len(rows), "script": len(script["shots"])})
        for row, shot in zip(rows, script["shots"]):
            checks += 1
            if row["text"].strip() != shot[key].strip():
                mismatches.append({"kind": "srt_text_drift", "file": name, "shot": shot["shot_id"],
                                   "srt": row["text"], "script": shot[key]})

    # ---- coverage: every shot must exist in the film ---------------------- #
    coverage = {}
    for aspect, info in videos.items():
        covered = sum(1 for e in lines if e["end"] <= info["duration"] + 0.25)
        coverage[aspect] = {
            "duration": info["duration"],
            "shots_covered": covered,
            "shots_expected": len(lines),
            "lost": len(lines) - covered,
        }
        if covered != len(lines):
            mismatches.append({"kind": "shot_lost_in_render", "aspect": aspect,
                               "lost": len(lines) - covered})

    return {
        "run_id": run_dir.name,
        "generated_at": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
        "ok": not mismatches,
        "checked": max(checks, 1),
        "mismatches": mismatches,
        "lines": lines,
        "coverage": coverage,
        "videos": videos,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--json", default="")
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    result = check(run_dir)
    out = Path(args.json) if args.json else run_dir / "06_qa/trace.json"
    write_json(out, result)
    bad = len(result["mismatches"])
    print(f"trace_check: {result['checked']} checks, {bad} mismatch(es) → {out}")
    for m in result["mismatches"][:10]:
        print("  !", json.dumps(m, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
