#!/usr/bin/env python3
"""trace_check：成片字幕 ↔ script.json ↔ facts/menu 逐项比对。用法：python qa/trace_check.py runs/<run_id>
不一致或丢失 > 0 → 退出码 1。产出 reports/trace.json、trace_manifest.json。"""
import json, pathlib, re, sys

rd = pathlib.Path(sys.argv[1]); J = lambda p: json.loads((rd / p).read_text())
facts, menu, script, media = J("01_ingest/facts.json"), J("02_script/menu.json"), J("02_script/script.json"), J("01_ingest/media_manifest.json")
src = {s["source_id"]: s for s in facts["sources"]}
verified = {f["field"]: f for f in facts["facts"] if f["status"] == "verified"}
unver = [f for f in facts["facts"] if f["status"] != "verified" and isinstance(f["value"], (str, list))]
prices = {i["price_aud_inc_gst"] for i in menu["items"]}
med = {m["media_id"]: m for m in media["media"]}
PHONE = re.compile(r"0\d[ \d]{8,11}\d"); PRICE = re.compile(r"\$\s?(\d+(?:\.\d{1,2})?)"); TIME = re.compile(r"\d{1,2}:\d{2}")


def srt(p):
    out = {}
    for blk in (rd / p).read_text().strip().split("\n\n"):
        L = blk.strip().splitlines(); out[int(L[0])] = " ".join(L[2:])
    return out


mism, miss, manifest = [], [], []
norm = lambda s: re.sub(r"\s+", " ", s).strip()
for lang in ("zh", "en"):
    lines = srt(f"05_export/{lang}.srt")
    for i, s in enumerate(script["shots"], 1):
        if i not in lines: miss.append(f"{lang}.srt 缺 {s['shot_id']}"); continue
        got = lines[i]
        if norm(got).replace(" ", "") != norm(s[f"sub_{lang}"]).replace(" ", ""):
            mism.append(f"{lang}.srt {s['shot_id']} 字幕 {got!r} ≠ script {s[f'sub_{lang}']!r}")
        for ph in PHONE.findall(got):
            if "phone" not in verified or re.sub(r"\D", "", ph) != re.sub(r"\D", "", verified["phone"]["value"]):
                mism.append(f"{lang}.srt {s['shot_id']} 电话 {ph} 不在 verified facts")
        for pr in PRICE.findall(got):
            if float(pr) not in prices: mism.append(f"{lang}.srt {s['shot_id']} 价格 ${pr} 不在 menu.json(verified)")
        if TIME.search(got): mism.append(f"{lang}.srt {s['shot_id']} 出现营业时间（facts 为 conflict）")
        for f in unver:
            vals = f["value"] if isinstance(f["value"], list) else [f["value"]]
            for v in vals:
                if len(v) >= 3 and v in got: mism.append(f"{lang}.srt {s['shot_id']} 含 {f['status']} 事实 {f['field']}={v!r}")
        if "name_en" in verified and verified["name_en"]["value"].lower() in got.lower() and "facts:name_en" not in s["refs"]:
            mism.append(f"{lang}.srt {s['shot_id']} 用了店名但 refs 未声明")
        m = med.get(s["media_id"], {})
        manifest.append({"lang": lang, "line": i, "text": got, "shot_id": s["shot_id"], "time": [s["start"], s["end"]],
                         "media": {"media_id": s["media_id"], "path": m.get("path"), "origin": m.get("origin"), "permission": m.get("permission")},
                         "facts": [{"ref": r, "value": verified.get(r.split(":", 1)[1], {}).get("value"), "source": src.get(verified.get(r.split(":", 1)[1], {}).get("source_id"), {}).get("url")} for r in s["refs"]]})
for k in ("9x16", "1x1", "16x9"):
    p = rd / f"05_export/subs_{k}.ass"
    if not p.exists(): miss.append(f"缺 {p.name}"); continue
    n = sum(1 for l in p.read_text().splitlines() if l.startswith("Dialogue:"))
    if n != 2 * len(script["shots"]): miss.append(f"{p.name} 字幕事件 {n} ≠ {2*len(script['shots'])}")
    if not (rd / f"05_export/promo_{k}.mp4").exists(): miss.append(f"缺 promo_{k}.mp4")
for s in script["shots"]:
    if med.get(s["media_id"], {}).get("origin") == "placeholder" and med[s["media_id"]].get("permission") != "granted":
        pass  # 占位素材允许出现在样片，交付闸门见 licenses.json deliverable_ok
rep = rd / "reports"; rep.mkdir(exist_ok=True)
res = {"mismatch_count": len(mism), "missing_count": len(miss), "mismatch": mism, "missing": miss, "lines_checked": len(manifest),
       "delivery_gate": "BLOCKED: 含 placeholder/permission pending 素材，仅可作样片" if any(m["origin"] == "placeholder" and m["permission"] != "granted" for m in [med[s["media_id"]] for s in script["shots"]]) else "OK"}
(rep / "trace.json").write_text(json.dumps(res, ensure_ascii=False, indent=2))
(rep / "trace_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
print(json.dumps({k: res[k] for k in ("mismatch_count", "missing_count", "lines_checked", "delivery_gate")}, ensure_ascii=False))
for x in mism + miss: print("  ✗", x)
sys.exit(1 if mism or miss else 0)
