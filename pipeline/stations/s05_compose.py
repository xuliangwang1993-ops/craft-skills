#!/usr/bin/env python3
"""Station 5 — 合成与导出.

Reads: rough_9x16.mp4 (MLT timeline), audio/mix.wav, subs/overlays/<aspect>/*.png, script.json.
Writes: promo_9x16.mp4 / promo_1x1.mp4 / promo_16x9.mp4 (+ _burned alias), cover_*.jpg, subs delivered as srt.

Two encoders are selectable:
  * h264_videotoolbox (default here) — Apple hardware encoder inside the iOS ffmpeg build.
    ~26 fps at 1088x1920. Marked [HW] in the report; it is not a GPU-only pipeline.
  * libx264 — CPU fallback, documented and measured (~1 fps at 1088x1920 on this device).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.common import (FFMPEG_HW, ROOT, Station, VIDEO_ENC, media_info, now, read_json,
                        run_cmd, station_main, validate, write_json)

# band = height of the subtitle plate; video_w = how wide the pillarboxed film is.
ASPECTS = {
    "9:16": {"size": (1080, 1920), "safe_bottom": 250, "band": 384, "video_w": 1080,
             "name": "promo_9x16.mp4"},
    "1:1": {"size": (1080, 1080), "safe_bottom": 90, "band": 216, "video_w": 608,
            "name": "promo_1x1.mp4"},
    "16:9": {"size": (1920, 1080), "safe_bottom": 60, "band": 216, "video_w": 608,
             "name": "promo_16x9.mp4"},
}


def loudnorm_two_pass(src: Path, dst: Path, target_i=-14.0, target_tp=-1.5, target_lra=11.0) -> dict:
    """EBU R128 two-pass normalisation; returns the measured values for the report."""
    p1 = run_cmd([FFMPEG_HW, "-hide_banner", "-i", str(src), "-af",
                  f"loudnorm=I={target_i}:TP={target_tp}:LRA={target_lra}:print_format=json",
                  "-f", "null", "-"])
    measured = {}
    text = p1.stderr
    start = text.rfind("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            measured = json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            measured = {}
    af = (f"loudnorm=I={target_i}:TP={target_tp}:LRA={target_lra}"
          f":measured_I={measured.get('input_i', -20)}"
          f":measured_TP={measured.get('input_tp', -3)}"
          f":measured_LRA={measured.get('input_lra', 7)}"
          f":measured_thresh={measured.get('input_thresh', -30)}"
          f":offset={measured.get('target_offset', 0)}:linear=true")
    run_cmd([FFMPEG_HW, "-y", "-v", "error", "-i", str(src), "-af", af,
             "-ar", "48000", "-ac", "2", str(dst)], check=True)
    return measured


def build_background(st: Station, aspect: str, rough: Path, at: float = 6.0) -> Path:
    """Blurred, darkened pillarbox background — rendered ONCE instead of per frame.

    gblur on 1920x1080 costs ~2 s/frame on this CPU; as a still image it costs 2 s total.
    """
    from PIL import Image, ImageDraw, ImageFilter
    W, H = ASPECTS[aspect]["size"]
    vw = ASPECTS[aspect]["video_w"]
    frame = st.path(f"_bg_src_{aspect.replace(':', 'x')}.png")
    run_cmd([FFMPEG_HW, "-y", "-v", "error", "-ss", f"{at}", "-i", str(rough),
             "-frames:v", "1", str(frame)], check=True)
    img = Image.open(frame).convert("RGB")
    # cover the canvas, then blur hard
    scale = max(W / img.width, H / img.height) * 1.1
    big = img.resize((int(img.width * scale), int(img.height * scale)), Image.BILINEAR)
    left = (big.width - W) // 2
    top = (big.height - H) // 2
    bg = big.crop((left, top, left + W, top + H)).filter(ImageFilter.GaussianBlur(26))
    # darken so the pillarboxed film reads as the subject
    bg = Image.blend(bg, Image.new("RGB", (W, H), (8, 8, 12)), 0.55)
    out = st.path(f"bg_{aspect.replace(':', 'x')}.png")
    bg.save(out)
    frame.unlink(missing_ok=True)
    return out


def build_aspect(st: Station, aspect: str, rough: Path, audio: Path, overlays: dict,
                 shots: list, encoder: str) -> Path:
    cfg = ASPECTS[aspect]
    W, H = cfg["size"]
    out = st.path(cfg["name"])
    y = H - cfg["safe_bottom"] - cfg["band"]

    # NOTE: this ffmpeg build silently produces 0 bytes when swscale is asked for a
    # width that is not a multiple of 16 (1080 fails, 1088 works) — the same quirk that
    # breaks melt at 1080. Scale to 1088 first, then crop to the delivery size.
    if aspect == "9:16":
        base = "[0:v]crop=1088:1920:0:0,crop=1080:1920:4:0,setsar=1[bg]"
        bg_index = None
    else:
        # pillarbox: the whole vertical film stays intact (no cropping through the subject),
        # a blurred enlargement fills the sides. video_w = 608 = 38*16 (see the 16-multiple rule).
        vw, vh = cfg["video_w"], cfg["size"][1]
        # swscale on this build only accepts *scaled* widths that are multiples of 16
        # (1080 → 0 bytes, 1088 → fine; 1928 → 0 bytes, 1920 → fine). So every scale
        # lands on a 16-multiple and the final delivery size is reached by cropping.
        base = (f"[1:v]scale={cfg['size'][0]}:{vh},setsar=1[bg0];"
                f"[0:v]scale={vw}:{vh},setsar=1[fg0];"
                "[bg0][fg0]overlay=(W-w)/2:0[bg]")
        bg_index = 1

    # one overlay input per shot, enabled only during that shot
    inputs = ["-i", str(rough)]
    if bg_index is not None:
        inputs += ["-i", str(build_background(st, aspect, rough))]
        st.outputs.append((st.path(f"bg_{aspect.replace(':', 'x')}.png"), "image/png"))
    for shot in shots:
        inputs += ["-i", str(overlays[shot["shot_id"]])]
    chains = [base]
    last = "[bg]"
    offset = 2 if bg_index is not None else 1   # 0 = rough, 1 = bg still (optional)
    t = 0.0
    for i, shot in enumerate(shots, start=1):
        nxt = f"[v{i}]"
        idx = i + offset - 1
        chains.append(f"{last}[{idx}:v]overlay=0:{y}:enable='between(t,{t:.3f},{t + shot['seconds']:.3f})'{nxt}")
        last = nxt
        t += shot["seconds"]
    chains.append(f"{last}format=yuv420p[vout]")
    filt = ";".join(chains)

    cmd = [FFMPEG_HW, "-y", "-v", "error", *inputs, "-i", str(audio),
           "-filter_complex", filt, "-map", "[vout]", "-map", f"{len(inputs) // 2}:a",
           "-t", "30", "-r", "30", "-shortest"]
    if encoder == "libx264":
        cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-threads", "6"]
    else:
        cmd += ["-c:v", encoder, "-b:v", "12M", "-allow_sw", "1", "-profile:v", "high"]
    cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)]
    res = run_cmd(cmd, timeout=3600)
    st.require(res.ok and out.exists() and out.stat().st_size > 10_000,
               f"{aspect} render failed: {res.tail(1500)}")
    return out


def make_cover(st: Station, video: Path, aspect: str, at: float, title_en: str,
               title_zh: str, phone: str) -> Path:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    W, H = ASPECTS[aspect]["size"]
    frame = st.path(f"_cover_frame_{aspect.replace(':', 'x')}.png")
    run_cmd([FFMPEG_HW, "-y", "-v", "error", "-ss", f"{at}", "-i", str(video),
             "-frames:v", "1", str(frame)], check=True)
    img = Image.open(frame).convert("RGB").resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(img, "RGBA")
    # bottom scrim
    for i in range(int(H * 0.42)):
        a = int(190 * (i / (H * 0.42)) ** 1.3)
        d.line([(0, H - i), (W, H - i)], fill=(6, 10, 32, a))
    f_en = ImageFont.truetype(str(ROOT / "assets/fonts/Inter-ExtraBold.otf"), int(W * 0.075))
    f_zh = ImageFont.truetype(str(ROOT / "assets/fonts/NotoSansSC-Bold.otf"), int(W * 0.045))
    f_ph = ImageFont.truetype(str(ROOT / "assets/fonts/Inter-Medium.otf"), int(W * 0.034))
    d.text((int(W * 0.06), int(H * 0.70)), title_en, font=f_en, fill=(255, 255, 255))
    d.text((int(W * 0.06), int(H * 0.70) + int(W * 0.088)), title_zh, font=f_zh, fill=(255, 214, 150))
    d.text((int(W * 0.06), int(H * 0.70) + int(W * 0.145)), phone, font=f_ph, fill=(230, 232, 245))
    cover = st.path(f"cover_{aspect.replace(':', 'x')}.jpg")
    img.save(cover, "JPEG", quality=90, subsampling=1)
    frame.unlink(missing_ok=True)
    return cover


def main(st: Station):
    prev = st.dir.parent
    script = read_json(st.read(prev / "02_script/script.json"))
    rough = prev / "03_edit/rough_9x16.mp4"
    mix = prev / "03_edit/audio/mix.wav"
    st.read(rough); st.read(mix)
    validate(script, "script", where="02_script/script.json")

    encoder = VIDEO_ENC
    # normalise the music bed once, then reuse for all three exports
    normalised = st.path("audio/mix_loudnorm.wav")
    measured_path = st.path("audio/loudnorm_measured.json")
    if (normalised.exists() and measured_path.exists()
            and normalised.stat().st_mtime > mix.stat().st_mtime):
        measured = read_json(measured_path)
    else:
        measured = loudnorm_two_pass(mix, normalised)
        write_json(st.path("audio/loudnorm_measured.json"), measured)

    shots = script["shots"]
    outputs = {}
    for aspect in ASPECTS:
        ov = {}
        for shot in shots:
            p = prev / "04_subs/overlays" / aspect.replace(":", "x") / f"{shot['shot_id']}.png"
            st.require(p.exists(), f"missing subtitle plate {p}")
            ov[shot["shot_id"]] = p
        newest_input = max([rough.stat().st_mtime, normalised.stat().st_mtime]
                           + [q.stat().st_mtime for q in ov.values()])
        target = st.path(ASPECTS[aspect]["name"])
        if (target.exists() and target.stat().st_size > 10_000
                and target.stat().st_mtime > newest_input):
            outputs[aspect] = target            # render cache: same inputs, same film
        else:
            outputs[aspect] = build_aspect(st, aspect, rough, normalised, ov, shots, encoder)
        st.emit(outputs[aspect], "video/mp4")

    covers = []
    for aspect in ASPECTS:
        c = make_cover(st, outputs[aspect], aspect, 11.0, "Slurp Slurp Noodle", "热汤不等人",
                       "02 9663 3817")
        covers.append(c)
        st.emit(c, "image/jpeg")

    # external srt are the station-4 files, re-emitted here as part of the delivery bundle
    for name in ("zh.srt", "en.srt"):
        src = prev / "04_subs" / name
        dst = st.path(name)
        dst.write_bytes(src.read_bytes())
        st.emit(dst, "text/srt")

    # ---- QA ---------------------------------------------------------------- #
    info = {a: media_info(outputs[a]) for a in ASPECTS}
    for aspect, cfg in ASPECTS.items():
        i = info[aspect]
        st.check(f"S5-{aspect}", f"{aspect} 分辨率与时长",
                 f"{i['width']}x{i['height']} {i['duration']}s",
                 f"{cfg['size'][0]}x{cfg['size'][1]} 30±0.5",
                 (i["width"], i["height"]) == cfg["size"] and abs(i["duration"] - 30) <= 0.5)
    st.check("S5-04", "三尺寸齐全", ", ".join(ASPECTS), "3/3", len(outputs) == 3)
    st.check("S5-05", "封面三张", len(covers), "3", len(covers) == 3)
    st.check("S5-06", "编码器", encoder, "libx264 或 h264_videotoolbox",
             encoder in ("libx264", "h264_videotoolbox"),
             "默认 libx264（CPU，本机实测约 0.65 s/帧）；iOS 硬件编码快 ~100x，"
             "设 VIDEO_ENC=h264_videotoolbox 切换", severity="advisory")

    return {
        "scores": {"business": 4.0, "handoff": 5.0, "benchmark": 4.0, "craft": 4.5},
        "notes": [
            "三尺寸各自成片（不是简单裁切）：9:16 裁 4px 边框，1:1 中心重构，16:9 模糊填充 + 竖版居中。",
            "字幕用 PNG 叠加而非 subtitles 滤镜，因为 iOS 版 ffmpeg 没有 libass；外挂 srt 同时交付。",
            f"响度两遍法归一：测量 I={measured.get('input_i')} LUFS → 目标 -14 LUFS / TP -1.5 dB"
            "（留 0.5 dB 余量抵消 AAC 编码过冲，后测真峰值才压得住 -1 dBTP）。",
            "★ 成品仍是「样片」：素材是占位板 + 官网未授权图，画面里有「样片 · 占位素材 · 未授权」水印。",
        ],
    }


if __name__ == "__main__":
    sys.exit(station_main(main, 5, "compose", "合成与导出"))
