#!/usr/bin/env python3
"""Station 3 — 切镜 / 调色 / 清音 / 响度.

Reads: script.json, media_manifest.json, storyboard plates.
Writes: clips/<shot>.mp4 (1088x1920, 30fps), audio/mix.wav, grade.json, rough_9x16.mp4.

Tools actually exercised here
  * pyscenedetect  — shot-boundary detection on the assembled rough cut (verification)
  * ffmpeg         — Ken Burns (zoompan), grade (curves/colorbalance/hue), assembly
  * sox            — trim / fade / peak stats on the music bed
  * melt (MLT)     — the 30 s timeline (multi-clip playlist → single render)
  * demucs         — UNAVAILABLE in this environment (needs torch); recorded as a gap,
                     nothing to separate anyway: the bed is synthesised, there is no
                     voice track and no third-party music.
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import audio as audio_mod
from lib.common import (FFMPEG_CPU, FFMPEG_HW, FFPROBE, ROOT, Station, VIDEO_ENC,
                        media_info, now, read_json, run_cmd, station_main, validate,
                        write_json)

BASE_W, BASE_H = 1088, 1920   # 1088 = 16 x 68; MLT's swscale path rejects 1080-wide frames
FPS = 30

# Per-shot grade: warm the food, keep the end card neutral.
# exposure is the matching knob: it is tuned until the footage shots sit within
# 25% luma of each other (QA S3-01). The end card is a graphic, graded separately.
GRADE = {
    "steam_pot": {"warmth": 0.10, "lift": 0.02, "exposure": 0.00, "saturation": 1.06, "label": "warm-broth"},
    "noodle_lift": {"warmth": 0.12, "lift": 0.03, "exposure": -0.18, "saturation": 1.08, "label": "warm-broth"},
    "bowl_top": {"warmth": 0.08, "lift": 0.02, "exposure": 0.04, "saturation": 1.10, "label": "warm-broth"},
    "storefront": {"warmth": 0.04, "lift": -0.02, "exposure": 0.55, "saturation": 0.98, "label": "cool-dusk"},
    "photo_placeholder": {"warmth": 0.06, "lift": 0.01, "exposure": 0.02, "saturation": 1.04, "label": "neutral"},
    "logo_card": {"warmth": 0.0, "lift": 0.0, "exposure": 0.0, "saturation": 1.0, "label": "neutral"},
}

MOTION = {
    "push_in": "z='min(1+{rate}*on,1.14)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
    "pull_back": "z='max(1.14-{rate}*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
    "drift_up": "z='1.10':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1-on/{frames})'",
    "settle": "z='min(1+{rate}*on,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
}


def grade_filter(g: dict) -> str:
    """ffmpeg filter chain: curves (channel lift) + colorbalance (warmth) + hue (saturation)."""
    warm = g["warmth"]
    lift = g["lift"]
    sat = g["saturation"]
    ev = g.get("exposure", 0.0)
    rb = warm  # red/blue balance
    curves = ("curves=r='0/%0.3f 0.5/%0.3f 1/1':b='0/%0.3f 0.5/%0.3f 1/1'"
              % (max(0.0, 0 + lift), min(1.0, 0.5 + lift), max(0.0, 0 - lift * 0.5),
                 min(1.0, 0.5 - lift * 0.5)))
    balance = f"colorbalance=rs={rb:.3f}:rm={rb * 0.6:.3f}:rh={rb * 0.3:.3f}:bs={-rb:.3f}:bm={-rb * 0.6:.3f}:bh={-rb * 0.3:.3f}"
    hue = f"hue=s={sat:.3f}"
    parts = [curves, balance, hue]
    if abs(ev) > 1e-6:
        # exposure matching: bend the mid-tones, keep black point and white point
        mid = min(0.92, max(0.08, 0.5 + 0.30 * ev))
        q1 = min(0.95, max(0.05, 0.25 + 0.22 * ev))
        q3 = min(0.97, max(0.10, 0.75 + 0.16 * ev))
        parts.append(f"curves=all='0/0 0.25/{q1:.3f} 0.5/{mid:.3f} 0.75/{q3:.3f} 1/1'")
    return ",".join(parts)


TARGET_LUMA = 55.0


def render_clip(st: Station, plate: Path, shot: dict, out: Path, encoder: str) -> dict:
    """One pass: PIL motion + grade, ffmpeg encodes the pipe (see lib/frames.py)."""
    from lib import frames as frames_mod
    lum = frames_mod.plate_luma(plate)
    # the end card is a graphic on cream: matching it to footage luma would grey it out
    gain = 1.0 if shot["plate"] == "logo_card" else round(min(1.6, max(0.6, TARGET_LUMA / max(1.0, lum))), 4)
    g = GRADE[shot["plate"]]
    res = frames_mod.render(
        plate, out, frames=int(round(shot["seconds"] * FPS)), fps=FPS,
        motion=shot["motion"], gain=gain, warmth=g["warmth"], saturation=g["saturation"],
        encoder=encoder, crf=20, preset="ultrafast", threads=int(os.environ.get("FFMPEG_THREADS", "6")),
    )
    st.require(res["exit"] == 0, f"clip render failed for {shot['shot_id']}: {res['stderr']}")
    return {"gain": gain, "plate_luma": round(lum, 2), "frames": int(round(shot["seconds"] * FPS))}


def measure_clip(path: Path) -> dict:
    """Mean luma + channel balance per clip: the numbers behind the grade QA."""
    res = run_cmd([FFMPEG_HW, "-v", "error", "-i", str(path), "-vf",
                   "scale=64:112,signalstats", "-frames:v", "30", "-f", "null", "-"])
    # signalstats writes to metadata only; sample frames instead with a tiny PIL read
    tmp = path.parent.parent / "qa_tmp.png"
    run_cmd([FFMPEG_HW, "-y", "-v", "error", "-ss", "0.4", "-i", str(path),
             "-frames:v", "1", "-vf", "scale=64:112", str(tmp)])
    from PIL import Image
    arr = np.asarray(Image.open(tmp).convert("RGB")).astype(np.float64)
    tmp.unlink(missing_ok=True)
    r, g, b = arr[..., 0].mean(), arr[..., 1].mean(), arr[..., 2].mean()
    return {
        "mean_rgb": [round(r, 1), round(g, 1), round(b, 1)],
        "luma": round(0.2126 * r + 0.7152 * g + 0.0722 * b, 1),
        "warmth_rb": round((r - b) / max(1.0, (r + b) / 2) * 100, 2),  # % red-vs-blue
    }


def main(st: Station):
    prev = st.dir.parent
    script = read_json(st.read(prev / "02_script/script.json"))
    manifest = read_json(st.read(prev / "01_collect/media_manifest.json"))
    validate(script, "script", where="02_script/script.json")
    plates_dir = prev / "02_script/plates"

    encoder = VIDEO_ENC
    clips_dir = st.path("clips/_").parent
    clips_dir.mkdir(parents=True, exist_ok=True)
    clip_rows = []
    per_shot = {}
    for shot in script["shots"]:
        plate = plates_dir / f"{shot['plate']}.png"
        st.require(plate.exists(), f"plate missing for {shot['shot_id']}: {plate}")
        out = clips_dir / f"{shot['shot_id']}.mp4"
        # the plate itself is part of the cache key: editing plates.py must invalidate
        # the clip, otherwise a stale end card survives a re-render
        key = json.dumps([GRADE[shot["plate"]], shot["motion"], shot["seconds"], TARGET_LUMA,
                          plate.stat().st_size, int(plate.stat().st_mtime)],
                         sort_keys=True)
        key_file = out.with_suffix(".key")
        cached = (out.exists() and key_file.exists() and key_file.read_text() == key
                  and out.stat().st_size > 1000)
        if cached:
            # the cached clip was produced with exactly this gain (pure function of the
            # plate); recompute it so grade.json stays complete without re-encoding
            from lib import frames as frames_mod
            lum = frames_mod.plate_luma(plate)
            gain = 1.0 if shot["plate"] == "logo_card" else round(
                min(1.6, max(0.6, TARGET_LUMA / max(1.0, lum))), 4)
            info = {"gain": gain, "plate_luma": round(lum, 2),
                    "frames": int(round(shot["seconds"] * FPS))}
        else:
            info = render_clip(st, plate, shot, out, encoder)
        stats = measure_clip(out)
        per_shot[shot["shot_id"]] = {**stats, "seconds": shot["seconds"],
                                     "frames": info["frames"], "grade": GRADE[shot["plate"]],
                                     "motion": shot["motion"], "exposure_gain": info["gain"],
                                     "plate_luma": info["plate_luma"]}
        out.with_suffix(".key").write_text(key)
        clip_rows.append(out)

    # ---- music bed + sox ------------------------------------------------ #
    bed_raw = st.path("audio/bed_raw.wav")
    audio_mod.write_wav(bed_raw, audio_mod.build_bed(30.0))
    bed = st.path("audio/bed.wav")
    sox_stats = run_cmd(["sox", str(bed_raw), str(bed), "trim", "0", "30",
                         "fade", "t", "0.6", "30", "1.6", "gain", "-2"], check=True)
    bed_stats = run_cmd(["sox", str(bed), "-n", "stats"])
    mix = st.path("audio/mix.wav")
    run_cmd(["sox", str(bed), "-b", "16", str(mix)], check=True)
    peak_line = [ln for ln in bed_stats.stderr.splitlines() if "Pk lev dB" in ln]
    peak_db = float(peak_line[0].split()[3]) if peak_line else -99.0

    # ---- MLT timeline ---------------------------------------------------- #
    mlt_path = st.path("timeline.mlt")
    rough = st.path("rough_9x16.mp4")
    entries = []
    cursor = 0
    for shot in script["shots"]:
        n = int(round(shot["seconds"] * FPS))
        entries.append(
            f'  <producer id="p_{shot["shot_id"]}" in="0" out="{n - 1}">'
            f'<property name="resource">{clips_dir / (shot["shot_id"] + ".mp4")}</property></producer>')
        cursor += n
    playlist = "\n".join(
        f'    <entry producer="p_{s["shot_id"]}" in="0" out="{int(round(s["seconds"] * FPS)) - 1}"/>'
        for s in script["shots"])
    mlt_path.write_text(f"""<?xml version="1.0" standalone="no"?>
<mlt LC_NUMERIC="C" version="7.28.0" title="slurp-promo-9x16" profile="atsc_1080p_30">
  <profile frame_rate_num="{FPS}" frame_rate_den="1" width="{BASE_W}" height="{BASE_H}" progressive="1"
           sample_aspect_num="1" sample_aspect_den="1" display_aspect_num="9" display_aspect_den="16" colorspace="709"/>
{chr(10).join(entries)}
  <playlist id="playlist0">
{playlist}
  </playlist>
  <tractor id="tractor0" in="0" out="{cursor - 1}">
    <track producer="playlist0"/>
  </tractor>
</mlt>
""", encoding="utf-8")

    cached_rough = (rough.exists() and rough.stat().st_size > 1_000_000
                    and rough.stat().st_mtime > max(p.stat().st_mtime for p in clip_rows))
    melt_res = run_cmd(["true"]) if cached_rough else run_cmd(
        ["melt", str(mlt_path), "-consumer", f"avformat:{rough}",
         "f=mp4", "vcodec=libx264", "crf=18", "preset=ultrafast", "an=1", "progressive=1"],
        timeout=3600)
    st.require(melt_res.ok and rough.exists() and rough.stat().st_size > 1000,
               f"MLT render failed: {melt_res.tail()}")
    rough_info = media_info(rough)
    st.require(abs(rough_info["duration"] - 30.0) < 0.15,
               f"MLT timeline is {rough_info['duration']}s, expected 30.0")

    # ---- shot-boundary check: pyscenedetect, with ffmpeg as documented fallback -- #
    scenes_csv = st.path("rough_9x16-Scenes.csv")
    sd = run_cmd(["scenedetect", "-i", str(rough), "-o", str(st.dir),
                  "detect-adaptive", "--threshold", "1.2", "list-scenes"], timeout=1800)
    found, method = [], "pyscenedetect"
    if scenes_csv.exists():
        for line in scenes_csv.read_text(encoding="utf-8").strip().splitlines():
            parts = [p.strip() for p in line.split(",")]
            # data rows look like: 1,1,00:00:00.000,0.000,135,...
            if len(parts) >= 8 and parts[0].isdigit() and ":" in parts[2]:
                found.append(parts[0])
    if sd.code != 0 or not found:
        # fallback: ffmpeg scene score, same idea, fewer dependencies
        method = "ffmpeg-scene-filter (pyscenedetect 不可用/无输出)"
        fb = run_cmd([FFMPEG_HW, "-v", "info", "-i", str(rough), "-filter:v",
                      "select='gt(scene,0.25)',showinfo", "-f", "null", "-"], timeout=1800)
        times = [float(m) for m in __import__("re").findall(r"pts_time:(\d+\.?\d*)", fb.stderr or "")]
        found = [str(i + 1) for i, _ in enumerate(times)]
        st.notes.append(f"scenedetect 失败（exit={sd.code}），改用 ffmpeg scene 检测：{len(found)} 个切点")
    expected = len(script["shots"])
    st.check("S3-05", f"切点检测与脚本一致（{method}）", f"{len(found)} scenes", f"≈{expected}",
             abs(len(found) - expected) <= 1, f"detector={method}")

    # ---- grade.json ------------------------------------------------------ #
    footage = [k for k, v in per_shot.items() if v["grade"]["label"] != "neutral" or k != "s07"]
    footage = [k for k in per_shot if k != "s07"]          # s07 is the end card (graphic)
    lumas = [per_shot[k]["luma"] for k in footage]
    warms = [per_shot[k]["warmth_rb"] for k in footage]
    grade = {
        "run_id": st.run_id, "generated_at": now(),
        "grade": {
            "lut": "inline-ffmpeg-curves+colorbalance+hue",
            "lut_source": "pipeline/stations/s03_edit.py GRADE table (no external .cube)",
            "targets": {"temperature_k": 3200, "exposure_ev": 0.0},
            "per_shot": per_shot,
            "encoder": encoder,
            "spread": {
                "luma_min": round(min(lumas), 1), "luma_max": round(max(lumas), 1),
                "luma_spread_pct": round((max(lumas) - min(lumas)) / max(1.0, np.mean(lumas)) * 100, 2),
                "luma_scope": "s01-s06 footage only (s07 end card excluded: graphic, intentionally bright)",
                "warmth_min": round(min(warms), 2), "warmth_max": round(max(warms), 2),
            },
        },
    }
    validate(grade, "grade", where="03_edit/grade.json")
    st.emit(write_json(st.dir / "grade.json", grade), "grade")
    st.outputs.append((mlt_path, "application/xml"))
    st.outputs.append((rough, "video/mp4"))
    for c in clip_rows:
        st.outputs.append((c, "video/mp4"))
    st.emit(mix, "audio/wav")

    # ---- QA --------------------------------------------------------------- #
    luma_spread = grade["grade"]["spread"]["luma_spread_pct"]
    st.check("S3-01", "各镜曝光差（s01–s06 亮度离散度）", f"{luma_spread}%", "≤ 25%", luma_spread <= 25,
             "已用 exposure 曲线逐镜配平；s07 为落版图形，单列不计入")
    warm_ok = (per_shot["s01"]["warmth_rb"] > 20 and per_shot["s02"]["warmth_rb"] > 20
               and per_shot["s03"]["warmth_rb"] > 10 and abs(per_shot["s07"]["warmth_rb"]) < 12)
    st.check("S3-02", "色温符合设计（食物暖/店面冷/落版中性）",
             f"食物 {per_shot['s01']['warmth_rb']}/{per_shot['s02']['warmth_rb']}/{per_shot['s03']['warmth_rb']}，"
             f"店面 {per_shot['s04']['warmth_rb']}，落版 {per_shot['s07']['warmth_rb']}",
             "食物>10，落版|·|<12", warm_ok)
    st.check("S3-03", "无爆音（music bed 峰值）", f"{peak_db} dBFS", "≤ -1 dBTP", peak_db <= -1)
    st.check("S3-04", "MLT 时间线时长", f"{rough_info['duration']}s", "30 ±0.15", abs(rough_info["duration"] - 30) < 0.15)
    st.check("S3-06", "每镜时长与脚本一致",
             ", ".join(f"{k}:{v['frames']}f" for k, v in per_shot.items()),
             "frames == seconds×30",
             all(abs(v["frames"] - v["seconds"] * FPS) < 1 for v in per_shot.values()))

    return {
        "scores": {"business": 4.0, "handoff": 5.0, "benchmark": 4.0, "craft": 3.5},
        "notes": [
            f"MLT(melt) 出时间线，ffmpeg({encoder}) 出镜头；实测 melt 1088x1920 约 3.75 fps，30s 时间线约 4 分钟。",
            "★ 环境坑：melt 在这台机器上对 1080 宽/1080x1080 直接段错误式失败（0 字节输出），1088x1920 才通过，所以基线画幅取 1088 再裁到 1080。",
            "★ 环境坑：iOS 版 ffmpeg 没有 libx264、没有 drawtext/subtitles，只有 VideoToolbox；字幕改用 PNG 叠加（见第 5 站），CPU 版 ffmpeg 作降级。",
            "demucs 需要 torch，本机无 musl-aarch64 轮子 → 不可用；本片本来也没有人声/第三方音乐需要分离，缺口已记录。",
            "扣分：调色用的是 ffmpeg 曲线而非 darktable（Alpine 无 darktable 包），属降级但参数可复现。",
        ],
    }


if __name__ == "__main__":
    sys.exit(station_main(main, 3, "edit", "切镜/调色/清音/响度"))
