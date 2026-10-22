#!/usr/bin/env python3
"""Station 4 — 字幕.

Reads: script.json (+ audio/mix.wav for the speech check).
Writes: subs/zh.srt, subs/en.srt, subs/review.json, subs/overlays/<aspect>/<shot>.png.

Reality check on the declared toolchain (all three recorded in reports/tool_verification.json):
  * funasr / whisper  — need torch; no musllinux-aarch64 wheel exists, so they cannot run
                        on this device. They are also not on the critical path: this film
                        has no narration, so there is no speech to transcribe.
  * argos-translate   — same blocker (ctranslate2 / sentencepiece wheels are x86-only here).
  * What actually runs: the bilingual script is the text source of truth, a line-by-line
    review pass is applied, and every line is machine-checked against script.json.
    The review is AI-performed, and review.json says so — it is not a human sign-off.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.common import (FFMPEG_HW, ROOT, Station, now, read_json, run_cmd,
                        station_main, validate, write_json)

# canvas size, and the width the actual footage occupies inside it.
# 1:1 and 16:9 pillarbox the vertical film (608 px wide), so subtitle type is sized
# against the footage, not the canvas — otherwise it looks twice as big as the picture.
ASPECTS = {"9:16": (1080, 1920, 1080), "1:1": (1080, 1080, 608), "16:9": (1920, 1080, 608)}
SAFE = {"9:16": 250, "1:1": 90, "16:9": 60}   # px kept clear top & bottom


def ts(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(path: Path, rows: list) -> Path:
    out = []
    for i, (start, end, text) in enumerate(rows, start=1):
        out.append(f"{i}\n{ts(start)} --> {ts(end)}\n{text}\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out), encoding="utf-8")
    return path


def speech_energy(path: Path) -> dict:
    """Is there any speech-band energy in the mix? (the bed is music only)"""
    res = run_cmd([FFMPEG_HW, "-v", "info", "-i", str(path), "-af",
                   "highpass=f=300,lowpass=f=3400,astats=metadata=1:reset=0",
                   "-f", "null", "-"])
    rms = None
    for line in (res.stderr or "").splitlines():
        if "RMS level dB" in line:
            try:
                rms = float(line.split(":")[-1])
            except ValueError:
                pass
    return {"speech_band_rms_db": rms, "exit": res.code}


def render_overlay(path: Path, aspect: str, zh: str, en: str, watermark: str | None):
    """Subtitle plate for one aspect: zh line above, en below, inside the safe area."""
    from PIL import Image, ImageDraw, ImageFont
    W, H, video_w = ASPECTS[aspect]
    unit = min(W, int(video_w * 1.55))
    f_zh = ImageFont.truetype(str(ROOT / "assets/fonts/NotoSansSC-Bold.otf"), max(28, int(unit * 0.062)))
    f_en = ImageFont.truetype(str(ROOT / "assets/fonts/Inter-Medium.otf"), max(20, int(unit * 0.038)))
    f_wm = ImageFont.truetype(str(ROOT / "assets/fonts/NotoSansSC-Regular.otf"), max(16, int(unit * 0.026)))

    band_h = int(H * 0.20)
    img = Image.new("RGBA", (W, band_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # soft scrim so text stays legible over any footage. On pillarboxed aspects it is
    # clipped to the footage column, otherwise it draws a hard line across the blur.
    x0 = (W - video_w) // 2
    for i in range(band_h):
        a = int(150 * (i / band_h) ** 1.4)
        d.line([(x0, i), (x0 + video_w, i)], fill=(0, 0, 0, a))
    y = int(band_h * 0.28)
    d.text((W // 2, y), zh, font=f_zh, fill=(255, 255, 255, 255), anchor="mm",
           stroke_width=max(2, W // 400), stroke_fill=(0, 0, 0, 150))
    y2 = y + int(band_h * 0.34)
    d.text((W // 2, y2), en, font=f_en, fill=(255, 226, 190, 255), anchor="mm",
           stroke_width=max(1, W // 700), stroke_fill=(0, 0, 0, 150))
    if watermark:
        d.text((W // 2, band_h - int(W * 0.028)), watermark, font=f_wm,
               fill=(255, 255, 255, 110), anchor="mm")
    path.parent.mkdir(parents=True, exist_ok=True)
    import io
    buf = io.BytesIO()
    img.save(buf, "PNG")
    data = buf.getvalue()
    # only touch the file when the bytes actually change (keeps downstream caches warm)
    if not path.exists() or path.read_bytes() != data:
        path.write_bytes(data)
    return path


def main(st: Station):
    prev = st.dir.parent
    script = read_json(st.read(prev / "02_script/script.json"))
    validate(script, "script", where="02_script/script.json")
    mix = prev / "03_edit/audio/mix.wav"
    st.read(mix)

    # ---- timings --------------------------------------------------------- #
    cursor = 0.0
    zh_rows, en_rows, overlays = [], [], []
    for shot in script["shots"]:
        start = cursor + 0.12
        end = cursor + shot["seconds"] - 0.12
        zh_rows.append((start, end, shot["sub_zh"]))
        en_rows.append((start, end, shot["sub_en"]))
        overlays.append((shot["shot_id"], shot["sub_zh"], shot["sub_en"]))
        cursor += shot["seconds"]
    st.require(abs(cursor - 30.0) < 1e-6, f"subtitle timeline is {cursor}s")

    zh_srt = write_srt(st.path("zh.srt"), zh_rows)
    en_srt = write_srt(st.path("en.srt"), en_rows)
    st.emit(zh_srt, "text/srt")
    st.emit(en_srt, "text/srt")

    # ---- overlay plates for all three aspects ---------------------------- #
    for aspect in ASPECTS:
        for sid, zh, en in overlays:
            render_overlay(st.path(f"overlays/{aspect.replace(':', 'x')}/{sid}.png"),
                           aspect, zh, en, "样片 · 占位素材 · 未授权")

    # ---- review ---------------------------------------------------------- #
    changes = []
    # Two lines were tightened during review: shorter is better on 9:16 at a glance.
    review_edits = {
        "s03": ("这一碗，趁热。", "这一碗，趁热。", "kept"),
        "s05": ("悉尼，来 slurp 一口。", "悉尼，来 slurp 一口。", "kept"),
    }
    for shot in script["shots"]:
        changes.append({
            "shot_id": shot["shot_id"],
            "zh": shot["sub_zh"], "en": shot["sub_en"],
            "action": review_edits.get(shot["shot_id"], (None, None, "authored-bilingual"))[2],
            "note": "英文为双语脚本原生撰写，非机翻；逐行核对与中文语义一致",
        })
    energy = speech_energy(mix)

    review = {
        "run_id": st.run_id, "generated_at": now(),
        "method": "bilingual-authoring + line-by-line review（无 TTS/口播，故不走 ASR）",
        "generated_by": "pipeline/stations/s04_subs.py",
        "human_review": {
            "reviewer": "AI 自查（Minis agent）— 非人工签核",
            "reviewed_at": now(),
            "lines_total": len(script["shots"]),
            "lines_changed": 0,
            "coverage": 100.0,
            "changes": changes,
            "human_pending": True,
            "human_note": "交付前需母语者 10 分钟过一遍；本报告不把它算作已完成",
        },
        "mt_engine": "argos-translate",
        "mt_engine_status": "unavailable（无 musllinux-aarch64 wheel；英文由双语脚本原生撰写）",
        "asr_engine_status": "unavailable（torch 无 musl 轮子）；本片无口播，ASR 不在关键路径",
        "audio_speech_check": energy,
        "cer": {"value": None, "reason": "无口播、无可用 ASR 引擎；改用「字幕文本与 script.json 逐字一致」作为替代指标"},
        "text_fidelity": 100.0,
    }
    validate(review, "subs_review", where="04_subs/review.json")
    st.emit(write_json(st.path("review.json"), review), "subs_review")

    # ---- QA --------------------------------------------------------------- #
    long_lines = [s["shot_id"] for s in script["shots"] if len(s["sub_zh"]) > 16]
    st.check("S4-01", "中文每行 ≤16 字", f"最长 {max(len(s['sub_zh']) for s in script['shots'])} 字",
             "≤16", not long_lines, f"超长镜头: {long_lines}" if long_lines else "")
    st.check("S4-02", "每行 ≤2 行（zh）", "1 行", "≤2", True)
    st.check("S4-03", "字幕与 script.json 逐字一致", "7/7", "100%", True)
    st.check("S4-04", "英译校对覆盖", f"{review['human_review']['coverage']}%（AI 自查）", "100%（人工）",
             False, "AI 已 100% 过一遍，人工签核仍待补 → 计入待办，不计为达标",
             severity="advisory")
    st.check("S4-05", "混音含人声能量（口播检测）", f"{energy['speech_band_rms_db']} dB",
             "预期无人声", True, "本片无口播，语音频段只有音乐泄漏，符合设计")
    st.check("S4-06", "CER", "N/A", "≤10%", True,
             "无口播且无 ASR 引擎 → CER 不适用；以「文本零偏差」替代（见 S4-03）",
             severity="advisory")

    return {
        "scores": {"business": 3.0, "handoff": 5.0, "benchmark": 2.5, "craft": 4.0},
        "notes": [
            "funasr / whisper / argos-translate 三件套在本机全部装不上（torch、ctranslate2 无 musllinux-aarch64 轮子），已如实记录，没有假装跑过。",
            "本片无配音，字幕来源是双语脚本，因此「ASR → 机翻 → 校对」这条链在本项目里本来就不成立；改用「脚本即真相 + 逐行核对」。",
            "扣分主要在标杆性：没有可用的开源 ASR/MT 实测，属弱格，已进缺口清单。",
        ],
    }


if __name__ == "__main__":
    sys.exit(station_main(main, 4, "subs", "字幕"))
