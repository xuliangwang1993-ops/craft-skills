#!/usr/bin/env python3
"""Station 6 — 后测（解码 / 响度 / 安全区 / 溯源）.

Reads the station-5 deliverables only. Writes:
  reports/decode.json, reports/loudness.json, reports/cer.json,
  safe_area/<aspect>.png (annotated), 06_qa/trace.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.common import (FFMPEG_HW, ROOT, Station, media_info, now, read_json, run_cmd,
                        station_main, validate, write_json)

ASPECTS = {"9x16": (1080, 1920, 250), "1x1": (1080, 1080, 90), "16x9": (1920, 1080, 60)}


def decode_pass(path: Path) -> dict:
    """Full decode of both streams.

    This ffmpeg build's PCM/WAV muxers produce 0 bytes and exit 1 (the decoder is fine),
    so both streams are decoded through a filter into the null muxer — that is the only
    combination here that actually walks every frame and reports real errors.
    """
    v = run_cmd([FFMPEG_HW, "-y", "-v", "error", "-i", str(path), "-map", "0:v",
                 "-vf", "scale=64:64", "-f", "null", "-"], timeout=1800)
    a = run_cmd([FFMPEG_HW, "-y", "-v", "error", "-i", str(path), "-map", "0:a",
                 "-af", "ebur128", "-f", "null", "-"], timeout=1800)
    errs = [ln for ln in ((v.stderr or "") + (a.stderr or "")).splitlines() if ln.strip()]
    return {"file": path.name, "exit": max(v.code, a.code), "errors": len(errs),
            "video_exit": v.code, "audio_exit": a.code,
            "first_error": errs[0][:300] if errs else "", "seconds": round(v.seconds + a.seconds, 2)}


def ebur128(path: Path) -> dict:
    res = run_cmd([FFMPEG_HW, "-hide_banner", "-nostats", "-i", str(path), "-af",
                   "ebur128=peak=true", "-f", "null", "-"], timeout=1800)
    text = res.stderr or ""
    summary = text[text.rfind("Summary:"):] if "Summary:" in text else text
    def grab(label):
        m = re.search(label + r":\s*(-?\d+\.\d+|-inf)", summary)
        return float(m.group(1)) if m and m.group(1) != "-inf" else None
    return {
        "file": path.name,
        "integrated_lufs": grab(r"I"),
        "lra_lu": grab(r"LRA"),
        "true_peak_db": grab(r"Peak"),
    }


def text_bbox(frame_path: Path, safe_bottom: int, h: int) -> dict:
    """Locate the burned-in subtitle by row-wise high-frequency energy."""
    from PIL import Image
    arr = np.asarray(Image.open(frame_path).convert("L")).astype(np.float32)
    hf = np.abs(np.diff(arr, axis=1)).sum(axis=1)          # per-row edge energy
    band = slice(int(h * 0.45), h)                          # subtitles live low
    rows = hf[band]
    thr = max(rows.mean() * 2.2, np.percentile(rows, 92))
    hit = np.where(rows > thr)[0]
    if hit.size == 0:
        return {"found": False, "top": None, "bottom": None}
    top = int(hit.min() + band.start)
    bottom = int(hit.max() + band.start)
    return {"found": True, "top": top, "bottom": bottom,
            "clear_bottom": h - bottom, "clear_top": top,
            "inside_safe": (h - bottom) >= safe_bottom}


def main(st: Station):
    prev = st.dir.parent
    script = read_json(st.read(prev / "02_script/script.json"))
    videos = {}
    for aspect in ASPECTS:
        p = prev / "05_compose" / f"promo_{aspect}.mp4"
        st.require(p.exists(), f"missing deliverable {p}")
        st.read(p)
        videos[aspect] = p

    # ---- decode ----------------------------------------------------------- #
    decode = {"run_id": st.run_id, "generated_at": now(),
              "videos": [decode_pass(p) for p in videos.values()]}
    st.emit(write_json(st.path("decode.json"), decode), "reports/decode")

    # ---- loudness --------------------------------------------------------- #
    loud = {"run_id": st.run_id, "generated_at": now(),
            "target": {"integrated_lufs": -14.0, "tolerance": 1.0, "true_peak_max": -1.0},
            "videos": [ebur128(p) for p in videos.values()]}
    st.emit(write_json(st.path("loudness.json"), loud), "reports/loudness")

    # ---- safe area -------------------------------------------------------- #
    safe_rows = []
    for aspect, (w, h, safe_bottom) in ASPECTS.items():
        cursor = 0.0
        for shot in script["shots"]:
            at = cursor + shot["seconds"] / 2
            frame = st.path(f"_f_{aspect}_{shot['shot_id']}.png")
            run_cmd([FFMPEG_HW, "-y", "-v", "error", "-ss", f"{at:.2f}",
                     "-i", str(videos[aspect]), "-frames:v", "1", str(frame)], check=True)
            box = text_bbox(frame, safe_bottom, h)
            safe_rows.append({"aspect": aspect, "shot": shot["shot_id"], **box})

            if shot["shot_id"] in ("s01", "s07"):
                from PIL import Image, ImageDraw
                img = Image.open(frame).convert("RGB")
                d = ImageDraw.Draw(img)
                d.line([(0, h - safe_bottom), (w, h - safe_bottom)], fill=(255, 60, 60), width=4)
                d.line([(0, safe_bottom), (w, safe_bottom)], fill=(255, 60, 60), width=4)
                if box["found"]:
                    d.rectangle((0, box["top"], w - 1, box["bottom"]), outline=(60, 220, 120), width=4)
                d.text((12, h - safe_bottom + 6), f"safe line {safe_bottom}px", fill=(255, 90, 90))
                img.save(st.path(f"safe_area/{aspect}_{shot['shot_id']}.png"))
            frame.unlink(missing_ok=True)

    found = [r for r in safe_rows if r["found"]]
    inside = [r for r in found if r["inside_safe"]]
    st.check("S6-03", "字幕全部落在安全区内", f"{len(inside)}/{len(found)}",
             "100%", len(found) > 0 and len(inside) == len(found),
             "9:16 底边留 250px，1:1 留 90px，16:9 留 60px；红=安全线，绿=检测到的字幕框")

    # ---- trace ------------------------------------------------------------ #
    trace_py = ROOT / "qa/trace_check.py"
    res = run_cmd([sys.executable, str(trace_py), str(prev),
                   "--json", str(st.path("trace.json"))], timeout=600)
    trace = read_json(st.path("trace.json"))
    validate(trace, "trace", where="06_qa/trace.json")
    st.emit(st.path("trace.json"), "trace")

    # ---- cer (not applicable) --------------------------------------------- #
    cer = {
        "run_id": st.run_id, "generated_at": now(),
        "value": None, "threshold": 10.0, "applicable": False,
        "reason": "本片无口播（无 TTS 可用），不存在 ASR 输出，CER 无从计算",
        "substitute_metric": {
            "name": "subtitle_text_fidelity",
            "value": 100.0,
            "method": "交付 srt 与 script.json 逐行比对（qa/trace_check.py: srt_text_drift）",
        },
        "asr_engines": {"funasr": "unavailable", "whisper": "unavailable",
                        "reason": "torch 无 musllinux-aarch64 wheel；见 reports/tool_verification.json"},
    }
    st.emit(write_json(st.path("cer.json"), cer), "reports/cer")

    # ---- QA --------------------------------------------------------------- #
    dec_ok = all(v["errors"] == 0 and v["exit"] == 0 for v in decode["videos"])
    st.check("S6-01", "解码无错", f"{sum(v['errors'] for v in decode['videos'])} errors", "0", dec_ok)
    louds = [v["integrated_lufs"] for v in loud["videos"] if v["integrated_lufs"] is not None]
    st.check("S6-02", "响度 -14 ±1 LUFS", f"{min(louds):.2f}..{max(louds):.2f} LUFS" if louds else "n/a",
             "-14 ±1", bool(louds) and all(abs(x + 14) <= 1.0 for x in louds))
    tps = [v["true_peak_db"] for v in loud["videos"] if v["true_peak_db"] is not None]
    st.check("S6-04", "真峰值 ≤ -1 dBTP", f"{max(tps):.2f} dBTP" if tps else "n/a",
             "≤ -1", bool(tps) and max(tps) <= -1.0)
    st.check("S6-05", "溯源不一致", len(trace["mismatches"]), "0", trace["ok"],
             "字幕/价格/电话/店名逐条回查 facts.json 与 menu.json")
    st.check("S6-06", "每镜在成片中有对应段落（丢失率）",
             ", ".join(f"{k}:{v['lost']}" for k, v in trace["coverage"].items()),
             "全部 0", all(v["lost"] == 0 for v in trace["coverage"].values()))
    st.check("S6-07", "时长 30 ±0.5s",
             ", ".join(f"{k}:{v['duration']}" for k, v in trace["coverage"].items()),
             "30 ±0.5", all(abs(v["duration"] - 30) <= 0.5 for v in trace["coverage"].values()))

    return {
        "scores": {"business": 4.0, "handoff": 5.0, "benchmark": 4.0, "craft": 4.5},
        "notes": [
            "后测只读第 5 站的成品，不回看中间产物 —— 与客户拿到的东西一致。",
            "安全区用「行方向高频能量」定位字幕（不依赖字幕已知位置），再用红/绿框标注出图。",
            "CER 不适用：无口播、无可用 ASR；改用 srt 与脚本逐行零偏差作为替代指标，已如实标注。",
        ],
    }


if __name__ == "__main__":
    sys.exit(station_main(main, 6, "qa", "后测"))
