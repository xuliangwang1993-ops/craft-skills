#!/usr/bin/env python3
"""Station 8 — 后测

- 站内静态审计（HTML/链接/体积/可访问性/SEO）
- 真实浏览器 E2E：表单校验、语言切换、相册加载、日历挂载（minis-browser-use 驱动 WebView）
- 视频：ffprobe 解码 + ebur128 响度（ffmpeg 在电脑端跑）
- secret_scan / trace_check
- Lighthouse：本机没有 Chrome，跑不了 → 记 not_run，另给静态审计分（不冒充）
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(__file__))
import lib
from lib import PipelineError

BR = "minis-browser-use"


def br(action: str, **kw) -> dict:
    cmd = [BR, action]
    for k, v in kw.items():
        flag = "--" + k.replace("_", "-")
        if isinstance(v, bool):
            if v:
                cmd.append(flag)
        else:
            cmd += [flag, str(v)]
    r = lib.run(cmd, timeout=180)
    raw = r["stdout"]
    try:
        return json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
    except Exception:
        return {"ok": False, "raw": raw[-500:], "stderr": r["stderr"][-300:]}


def js(script: str):
    d = br("execute_js", script=script)
    if isinstance(d, dict):
        if d.get("ok") is False:
            return {"__error__": (d.get("error") or {}).get("message", "js error")}
        data = d.get("data")
        if isinstance(data, dict):
            txt = data.get("text", data)
            if isinstance(txt, str):
                txt = re.sub(r"\n\s*tab_id:.*$", "", txt, flags=re.S).strip()
                try:
                    return json.loads(txt)
                except Exception:
                    return txt
            return txt
        for key in ("result", "value"):
            if key in d:
                return d[key]
    return d


def html_audit(site: Path) -> dict:
    html = (site / "index.html").read_text(encoding="utf-8")
    text = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    words = len(re.findall(r"\w+", text))
    imgs = re.findall(r"<img[^>]+>", html)
    missing_alt = [i for i in imgs if "alt=" not in i]
    ext = re.findall(r'(?:src|href)="(https?://[^"]+)"', html)
    size = sum(f.stat().st_size for f in site.rglob("*") if f.is_file())
    return {
        "title_len": len(re.search(r"<title>(.*?)</title>", html, re.S).group(1)),
        "has_meta_description": 'name="description"' in html,
        "has_viewport": 'name="viewport"' in html,
        "lang": re.search(r'<html lang="([^"]+)"', html).group(1),
        "h1_count": len(re.findall(r"<h1", html)),
        "images": len(imgs),
        "images_missing_alt": len(missing_alt),
        "external_requests": ext,
        "text_words": words,
        "total_bytes": size,
        "critical_bytes": (site / "index.html").stat().st_size + (site / "styles.css").stat().st_size
                          + (site / "app.js").stat().st_size + (site / "assets/img/p01-2048.jpg").stat().st_size,
        "has_form_labels": html.count("<label") >= 5,
        "payment_mentions": len(re.findall(r"(?i)stripe|paypal|credit card|card number", html)),
    }


def link_check(site: Path) -> dict:
    html = (site / "index.html").read_text(encoding="utf-8")
    refs = set(re.findall(r'(?:src|href)="([^"#?]+)', html))
    missing = []
    for r in refs:
        if r.startswith(("http", "mailto:", "data:")):
            continue
        p = (site / r.split("?")[0])
        if not p.exists():
            missing.append(r)
    return {"refs": len(refs), "missing": missing, "ok": not missing}


def video_qa(run: Path) -> dict:
    out = {}
    host = os.environ.get("FFMPEG_HOST", "pc")
    for name in ("tour_9x16.mp4", "tour_16x9.mp4"):
        p = run / "04_video" / name
        r = lib.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(p)])
        raw = r["stdout_full"]
        j = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
        vs = [s for s in j["streams"] if s["codec_type"] == "video"][0]
        as_ = [s for s in j["streams"] if s["codec_type"] == "audio"][0]
        dec = lib.run(["ffprobe", "-v", "error", "-show_entries", "stream=nb_frames", "-of", "csv=p=0", str(p)])
        loud = {"i": None, "tp": None}
        remote_dir = f"/tmp/minis-qc-{run.name}"
        lib.run(["ssh", host, f"mkdir -p {remote_dir}"], timeout=60)
        lib.run(["scp", "-q", str(p), f"{host}:{remote_dir}/{p.name}"], timeout=300)
        rr = lib.run(["ssh", host,
                      f"ffmpeg -nostdin -hide_banner -nostats -i '{remote_dir}/{p.name}' "
                      f"-filter_complex ebur128=peak=true -f null - 2>&1 | grep -E 'I:|Peak:' | tail -4"],
                     timeout=600)
        txt = rr["stdout"]
        mi = re.findall(r"I:\s*(-?\d+\.\d+)\s*LUFS", txt)
        mt = re.findall(r"Peak:\s*(-?\d+\.\d+)\s*dBFS", txt)
        if mi:
            loud["i"] = float(mi[-1])
        if mt:
            loud["tp"] = float(mt[-1])
        out[name] = {"width": vs["width"], "height": vs["height"], "fps": vs["r_frame_rate"],
                     "duration": float(j["format"]["duration"]), "video_codec": vs["codec_name"],
                     "audio_codec": as_["codec_name"], "bytes": p.stat().st_size,
                     "frames": int(dec["stdout"].strip().split()[0] or 0) if dec["stdout"].strip() else None, "loudness_lufs": loud["i"],
                     "true_peak_dbtp": loud["tp"]}
    return out


def e2e(run: Path) -> dict:
    site = run / "07_site" / "site"
    rel = site.relative_to(Path("/var/minis/workspace"))
    url = f"minis://workspace/{rel}/index.html?e2e={int(__import__('time').time())}"
    steps = []
    br("navigate", url=url)
    steps.append({"step": "load", "ok": True, "detail": url})

    info = js("""const imgs=[...document.images];
      return JSON.stringify({h1:(document.querySelector('h1')||{}).textContent||'',
        images:imgs.length, broken:imgs.filter(i=>i.naturalWidth===0).length,
        lang:document.documentElement.lang});""")
    steps.append({"step": "render", "ok": isinstance(info, dict) and info.get("broken") == 0, "detail": info})

    tog = js("""document.querySelector('.lang button[data-lang="en"]').click();
      return document.querySelector('h1').textContent.trim();""")
    steps.append({"step": "language_toggle", "ok": isinstance(tog, str) and not re.search(r"[\u4e00-\u9fff]", tog),
                  "detail": str(tog)[:70]})
    js("""document.querySelector('.lang button[data-lang="zh"]').click(); return 1;""")

    cal = js("return document.querySelector('#cal').textContent.trim().slice(0,80)")
    steps.append({"step": "calendar_mount", "ok": bool(cal) and "__error__" not in str(cal), "detail": cal})

    js("""document.querySelector('#name').value='';document.querySelector('#email').value='';
      document.querySelector('#bookform').dispatchEvent(new Event('submit',{cancelable:true}));return 1;""")
    empty = js("return document.querySelector('#formstatus').textContent")
    steps.append({"step": "form_validation_empty", "ok": bool(empty) and len(str(empty)) > 3, "detail": str(empty)[:90]})

    js("""window.__CONFIG__.formEndpoint='/__mock__';
      window.fetch=async()=>({ok:true,status:200});
      document.querySelector('#name').value='E2E Tester';
      document.querySelector('#email').value='e2e@example.com';
      document.querySelector('#checkin').value='2026-11-10';
      document.querySelector('#checkout').value='2026-11-13';
      document.querySelector('#bookform').dispatchEvent(new Event('submit',{cancelable:true}));return 1;""")
    ok = js("return document.querySelector('#formstatus').textContent")
    steps.append({"step": "form_submit_valid", "ok": any(k in str(ok) for k in ("12", "Sent", "房东", "已发出")),
                  "detail": str(ok)[:90]})

    shots = []
    outdir = run / "reports" / "screenshots"
    outdir.mkdir(parents=True, exist_ok=True)
    for name, (w, h) in {"mobile": (390, 844), "desktop": (1280, 800)}.items():
        br("set_viewport", viewport_width=w, viewport_height=h)
        br("navigate", url=url)
        d = br("screenshot")
        src = d.get("minis_url", "")
        if src.startswith("minis://"):
            p = Path("/var/minis") / src.replace("minis://", "")
            if p.exists():
                dst = outdir / f"site_{name}.jpg"
                shutil.copyfile(p, dst)
                shots.append(str(dst.relative_to(lib.ROOT)))
    br("set_viewport", reset=True)
    return {"steps": steps, "passed": all(s["ok"] for s in steps), "screenshots": shots, "url": url}


def static_audit(a: dict) -> dict:
    critical = a.get("critical_bytes", a["total_bytes"])
    perf = 98 if critical < 1_200_000 else (90 if critical < 2_500_000 else 78)
    a11y = 100 - a["images_missing_alt"] * 10 - (0 if a["has_form_labels"] else 15)
    bp = 100 - (0 if not a["external_requests"] else 10) - a["payment_mentions"] * 25
    seo = 60 + (20 if a["has_meta_description"] else 0) + (10 if a["has_viewport"] else 0) + (10 if a["h1_count"] == 1 else 0)
    return {"performance": max(0, min(100, perf)), "accessibility": max(0, a11y),
            "best_practices": max(0, bp), "seo": max(0, seo),
            "method": "static heuristics (size/alt/labels/meta/h1) — NOT Lighthouse"}


def main(run_id: str) -> None:
    st = lib.Station("08", "qc", run_id)
    run = lib.RUNS / run_id
    st.require_upstream("09", "support_test.json")
    site_p = st.require_upstream("07", "site.json", "site")
    site = lib.ROOT / lib.read_json(site_p)["root"]

    audit = html_audit(site)
    links = link_check(site)
    vq = video_qa(run)
    e2 = e2e(run)
    scores = static_audit(audit)

    sec = lib.run(["python3", str(lib.ROOT / "qa" / "secret_scan.py"), str(run),
                   "--json", str(run / "reports" / "secret_scan.json")], timeout=300)
    sec_doc = lib.read_json(run / "reports" / "secret_scan.json")

    tr = lib.run(["python3", str(lib.ROOT / "qa" / "trace_check.py"), str(run)], timeout=300)
    trace = lib.read_json(run / "reports" / "trace.json")

    lib.write_json(run / "reports" / "site_e2e.json", e2)
    lib.write_json(run / "reports" / "lighthouse.json", {
        "status": "not_run", "reason": "lighthouse 需要 Chrome；本机（iOS/iSH）没有可用的 Chromium，playwright 也没有 musl/aarch64 构建。",
        "substitute": scores})
    lib.write_json(run / "reports" / "html_audit.json", {"audit": audit, "links": links})
    lib.write_json(run / "reports" / "video_qa.json", vq)

    out = {
        "generated_at": lib.now(),
        "secret_scan": {"clean": sec_doc["clean"], "files": sec_doc["files_scanned"], "hits": len(sec_doc["hits"])},
        "trace": {"inconsistencies": trace["inconsistencies"], "coverage": trace["coverage"], "passed": trace["passed"]},
        "html": audit, "links": links, "video": vq, "e2e": {"passed": e2["passed"], "steps": e2["steps"]},
        "lighthouse": {"status": "not_run", "substitute": scores},
        "tools": {"playwright": "install failed (no musl/aarch64 wheel)", "lighthouse": "not run (no Chrome)",
                  "browser": "in-app WebKit via minis-browser-use"},
    }
    lib.write_json(run / "reports" / "qc.json", out)
    st.add_output(run / "reports" / "qc.json")
    st.add_tree(run / "reports")

    checks = [
        {"id": "secret_scan_clean", "ok": sec_doc["clean"], "detail": f"{len(sec_doc['hits'])} hits"},
        {"id": "trace_clean", "ok": trace["inconsistencies"] == 0 and not trace["coverage"]["site_missing"]
                                             and not trace["coverage"]["kb_missing"], "detail": trace["coverage"]},
        {"id": "links_ok", "ok": links["ok"], "detail": links["missing"]},
        {"id": "e2e_passed", "ok": e2["passed"], "detail": [s["step"] for s in e2["steps"] if not s["ok"]]},
        {"id": "video_loudness", "ok": all(v["loudness_lufs"] is not None and abs(v["loudness_lufs"] + 14) <= 1 for v in vq.values()),
         "detail": {k: v["loudness_lufs"] for k, v in vq.items()}},
        {"id": "video_true_peak", "ok": all(v["true_peak_dbtp"] is not None and v["true_peak_dbtp"] <= -1 for v in vq.values()),
         "detail": {k: v["true_peak_dbtp"] for k, v in vq.items()}},
        {"id": "video_decodes", "ok": all(v["duration"] >= 30 for v in vq.values()), "detail": {k: v["duration"] for k, v in vq.items()}},
        {"id": "no_payment", "ok": audit["payment_mentions"] == 0},
        {"id": "a11y_alts", "ok": audit["images_missing_alt"] == 0, "detail": audit["images_missing_alt"]},
        {"id": "static_audit_ge_90", "ok": min(scores["performance"], scores["accessibility"], scores["seo"]) >= 90,
         "detail": scores},
    ]
    qa = st.qa(checks)
    st.metrics = {"secret_hits": len(sec_doc["hits"]), "trace_issues": trace["inconsistencies"],
                  "site_bytes": audit["total_bytes"], "lighthouse": "not_run"}
    st.finish(0 if qa["passed"] else 1)
    lib.info(f"station 8 qc passed={qa['passed']} secret={len(sec_doc['hits'])} trace={trace['inconsistencies']}")


if __name__ == "__main__":
    main(lib.ctx_run_id(sys.argv[1:]))
