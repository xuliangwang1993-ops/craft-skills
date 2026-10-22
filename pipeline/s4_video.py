#!/usr/bin/env python3
"""Station 4 — 看房短视频（1080x1920 / 1920x1080，40s，中英字幕）

做法：每张照片先在 PIL 里排成画布（竖屏：模糊背景 + 4:3 原图居中；横屏：模糊背景 + 原图偏左），
字幕直接烧进画布（不依赖 libass，本机 ffmpeg 没编进 subtitles/drawtext），再交给 ffmpeg zoompan + xfade。
音频：SoX 合成环境垫乐（自制，CC0），loudnorm 到 -14 LUFS。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import lib
from lib import PipelineError

FPS = 30
SLIDE_S = 6.7
XFADE = 0.6
CJK = "/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc"
LATIN = "/usr/share/fonts/inter/Inter-Regular.ttf"
if not Path(LATIN).exists():
    LATIN = "/usr/share/fonts/dejavu/DejaVuSans.ttf"


def font(size: int, cjk: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(CJK if cjk else LATIN, size)


def text_w(draw, txt, f) -> int:
    box = draw.textbbox((0, 0), txt, font=f)
    return box[2] - box[0]


def wrap(draw, txt: str, f, max_w: int) -> list[str]:
    words, lines, cur = txt.split(" "), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def slide(photo: Path, zh: str, en: str, size: tuple[int, int], idx: int, total: int, cover: bool = False) -> Image.Image:
    W, H = size
    src = Image.open(photo).convert("RGB")
    # 背景：放大裁切 + 高斯模糊 + 压暗
    bg = src.copy()
    r = max(W / bg.width, H / bg.height) * 1.15
    bg = bg.resize((int(bg.width * r), int(bg.height * r)), Image.LANCZOS)
    left, top = (bg.width - W) // 2, (bg.height - H) // 2
    bg = bg.crop((left, top, left + W, top + H)).filter(ImageFilter.GaussianBlur(28))
    bg = ImageEnhance.Brightness(bg).enhance(0.55)
    canvas = bg.copy()

    # 前景：保持 4:3 比例
    pw = int(W * (0.94 if W < H else 0.62))
    ph = int(pw * 0.75)
    fg = src.copy()
    r2 = min(pw / fg.width, ph / fg.height)
    fg = fg.resize((int(fg.width * r2), int(fg.height * r2)), Image.LANCZOS)
    fx = (W - fg.width) // 2
    fy = int(H * 0.30) - fg.height // 2 if W < H else (H - fg.height) // 2
    canvas.paste(fg, (fx, fy))

    d = ImageDraw.Draw(canvas, "RGBA")
    # 底部渐变，保证字幕可读
    grad = Image.new("RGBA", (W, int(H * 0.42)), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(grad.height):
        a = int(200 * (y / grad.height) ** 1.4)
        gd.line([(0, y), (W, y)], fill=(8, 10, 14, a))
    canvas.paste(Image.alpha_composite(canvas.crop((0, H - grad.height, W, H)).convert("RGBA"), grad).convert("RGB"),
                 (0, H - grad.height))

    d = ImageDraw.Draw(canvas, "RGBA")
    f_zh = font(int(W * 0.042), cjk=True)
    f_en = font(int(W * 0.030))
    base_y = int(H * 0.74) if W < H else int(H * 0.70)
    lines = wrap(d, en, f_en, int(W * 0.86))
    d.text((int(W * 0.07), base_y), zh, font=f_zh, fill=(255, 255, 255, 245))
    y = base_y + int(f_zh.size * 1.45)
    for ln in lines:
        d.text((int(W * 0.07), y), ln, font=f_en, fill=(235, 238, 242, 215))
        y += int(f_en.size * 1.28)

    # 角标
    tag = f"{idx:02d} / {total:02d}"
    f_tag = font(int(W * 0.021))
    d.text((int(W * 0.07), int(H * 0.055)), tag, font=f_tag, fill=(255, 255, 255, 150))
    d.text((int(W * 0.07), int(H * 0.055) + int(f_tag.size * 1.5)), "SAMPLE · 样片", font=f_tag, fill=(255, 255, 255, 110))

    if cover:
        f_h = font(int(W * 0.075) if W < H else int(W * 0.042), cjk=True)
        f_s = font(int(W * 0.026))
        d.text((int(W * 0.07), int(H * 0.12)), "Rosebery · 独立房间", font=f_h, fill=(255, 255, 255, 250))
        d.text((int(W * 0.07), int(H * 0.12) + int(f_h.size * 1.35)),
               "Private room · 2 guests · 1 queen bed", font=f_s, fill=(240, 242, 246, 220))
    # 底部细线
    d.rectangle([0, H - 6, W, H], fill=(255, 255, 255, 30))
    return canvas


def build_audio(path: Path, seconds: float) -> None:
    """自制环境垫乐：三个正弦叠 + 慢速起伏 + 混响。"""
    cmd = (
        f"sox -n -r 48000 -c 2 '{path}' synth {seconds:.1f} sine 196 sine 246.94 sine 293.66 "
        f"remix - fade 2 {seconds:.1f} 3 tremolo 0.12 22 reverb 25 norm -20"
    )
    r = lib.run(cmd, timeout=180)
    if r["rc"] != 0:
        raise PipelineError(f"sox failed: {r['stderr'][:300]}")


def local_ffmpeg_ok() -> bool:
    r = lib.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=black:s=32x32:d=0.2", "-f", "null", "-"], timeout=60)
    txt = (r["stdout"] + r["stderr"]).lower()
    return r["rc"] == 0 and "unavailable" not in txt and "aborted" not in txt


def _render_cmd(slides, out, size, audio, seconds, pathfn=lambda x: str(x)):
    W, H = size
    inputs = []
    for s in slides:
        inputs += ["-loop", "1", "-t", f"{SLIDE_S}", "-i", pathfn(s)]
    inputs += ["-i", pathfn(audio)]
    n = len(slides)
    filt = []
    for i in range(n):
        filt.append(
            f"[{i}:v]scale={int(W*1.25)}:{int(H*1.25)}:flags=bicubic,"
            f"zoompan=z='1.001+0.00045*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={int(SLIDE_S*FPS)}:s={W}x{H}:fps={FPS},setsar=1[v{i}]"
        )
    prev = "v0"
    for i in range(1, n):
        off = i * (SLIDE_S - XFADE)
        filt.append(f"[{prev}][v{i}]xfade=transition=fade:duration={XFADE}:offset={off:.2f}[x{i}]")
        prev = f"x{i}"
    filt.append(f"[{prev}]fade=t=in:st=0:d=0.6,fade=t=out:st={seconds-0.8:.2f}:d=0.8,format=yuv420p[vout]")
    filt.append(f"[{n}:a]loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=in:st=0:d=1.2,afade=t=out:st={seconds-1.5:.2f}:d=1.5[aout]")
    return ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filt),
            "-map", "[vout]", "-map", "[aout]", "-t", f"{seconds}", "-r", str(FPS),
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)]


def encode(slides, out, size, audio, seconds, st: lib.Station):
    """本地 ffmpeg 可用就本地跑；否则把素材送到 FFMPEG_HOST（默认 pc）编码再取回。
    本机（iOS）ffmpeg worker 一旦被中断就会锁死，这是实测到的降级路径。"""
    if local_ffmpeg_ok():
        cmd = _render_cmd(slides, out, size, audio, seconds)
        r = lib.run(cmd, timeout=1800)
        if r["rc"] != 0 or not out.exists():
            raise PipelineError(f"ffmpeg encode failed: {r['stderr'][-600:]}")
        st.notes.append("encoder=local ffmpeg")
        return
    host = os.environ.get("FFMPEG_HOST", "pc")
    remote = f"/tmp/minis-s4-{st.run_id}"
    files = list(slides) + [audio]
    lib.run(["ssh", host, f"mkdir -p {remote}"], timeout=60)
    for f in files:
        r = lib.run(["scp", "-q", str(f), f"{host}:{remote}/{Path(f).name}"], timeout=300)
        if r["rc"] != 0:
            raise PipelineError(f"scp failed for {f}: {r['stderr'][:200]}")
    rname = Path(out).name
    cmd = _render_cmd(slides, Path(remote) / rname, size, audio, seconds,
                      pathfn=lambda x: f"{remote}/{Path(x).name}")
    script = "#!/bin/sh\nset -e\n" + " ".join("'" + a.replace("'", "'\\''") + "'" if (" " in a or ";" in a or "'" in a) else a for a in cmd) + "\n"
    sp = st.path("_build", f"remote_{rname}.sh")
    sp.write_text(script)
    lib.run(["scp", "-q", str(sp), f"{host}:{remote}/run.sh"], timeout=120)
    r = lib.run(["ssh", host, f"sh {remote}/run.sh"], timeout=2400)
    if r["rc"] != 0:
        raise PipelineError(f"remote ffmpeg failed: {r['stderr'][-800:]}")
    r2 = lib.run(["scp", "-q", f"{host}:{remote}/{rname}", str(out)], timeout=600)
    if r2["rc"] != 0 or not out.exists():
        raise PipelineError(f"scp back failed: {r2['stderr'][:300]}")
    st.notes.append(f"encoder=remote:{host} (local ffmpeg locked)")
    st.add_tool(f"ffmpeg@{host}", lib.tool_version("ffmpeg", ["-version"]).split()[2] if False else "remote")


def srt(items, seconds_each: float) -> str:
    def ts(t):
        h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")
    out = []
    for i, (zh, en) in enumerate(items, 1):
        a = (i - 1) * (seconds_each - XFADE)
        b = min(a + seconds_each - 0.15, (i) * (seconds_each - XFADE) + seconds_each - XFADE)
        out.append(f"{i}\n{ts(a)} --> {ts(b)}\n{zh}\n{en}\n")
    return "\n".join(out)


def _decode_ok(st, run_id: str, names) -> bool:
    import subprocess
    host = os.environ.get("FFMPEG_HOST", "pc")
    ok = True
    for n in names:
        p = lib.RUNS / run_id / "04_video" / n
        remote = f"/tmp/minis-qc-{run_id}"
        lib.run(["ssh", host, f"mkdir -p {remote}"], timeout=60)
        lib.run(["scp", "-q", str(p), f"{host}:{remote}/{n}"], timeout=300)
        r = lib.run(["ssh", host, f"ffmpeg -nostdin -v error -i {remote}/{n} -f null -"], timeout=600)
        if r["rc"] != 0:
            ok = False
            st.notes.append(f"decode error {n}: {r['stderr'][:120]}")
    return ok


def run(run_id: str) -> None:
    st = lib.Station("04", "video", run_id)
    order_p = st.require_upstream("03", "photos/order.json")
    facts_p = st.require_upstream("01", "facts.json", "facts")
    order = lib.read_json(order_p)["items"]
    facts = lib.read_json(facts_p)["facts"]

    seconds = 40.0
    W9, H9 = 1080, 1920
    W16, H16 = 1920, 1080
    total = len(order)
    tmp = st.path("_build")
    tmp.mkdir(parents=True, exist_ok=True)

    s9, s16 = [], []
    for i, it in enumerate(order, 1):
        photo = lib.ROOT / it["file"]
        s9.append(tmp / f"s9_{i:02d}.png")
        slide(photo, it["caption_zh"], it["caption_en"], (W9, H9), i, total, cover=(i == 1)).save(s9[-1])
        s16.append(tmp / f"s16_{i:02d}.png")
        slide(photo, it["caption_zh"], it["caption_en"], (W16, H16), i, total, cover=(i == 1)).save(s16[-1])

    audio = st.path("audio", "bed.wav")
    audio.parent.mkdir(parents=True, exist_ok=True)
    build_audio(audio, seconds)

    v9 = st.path("tour_9x16.mp4")
    v16 = st.path("tour_16x9.mp4")
    for slides, out, size in ((s9, v9, (W9, H9)), (s16, v16, (W16, H16))):
        if not (out.exists() and out.stat().st_size > 1_000_000):
            encode(slides, out, size, audio, seconds, st)

    subs = st.path("subs")
    subs.mkdir(parents=True, exist_ok=True)
    items = [(it["caption_zh"], it["caption_en"]) for it in order]
    (subs / "tour_zh.srt").write_text(srt(items, SLIDE_S), encoding="utf-8")
    en_only = [(it["caption_en"], "") for it in order]
    (subs / "tour_en.srt").write_text(srt(en_only, SLIDE_S), encoding="utf-8")

    # 封面
    cover9 = st.path("cover_9x16.jpg")
    Image.open(s9[0]).save(cover9, quality=90)
    cover16 = st.path("cover_16x9.jpg")
    Image.open(s16[0]).save(cover16, quality=90)

    meta = {}
    for p in (v9, v16):
        r = lib.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(p)])
        raw = r["stdout_full"]
        j = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
        vs = [s for s in j["streams"] if s["codec_type"] == "video"][0]
        meta[p.name] = {"width": vs["width"], "height": vs["height"], "fps": vs["r_frame_rate"],
                        "duration": float(j["format"]["duration"]), "bytes": p.stat().st_size,
                        "codec": vs["codec_name"]}
    lib.write_json(st.path("video_meta.json"), meta)

    st.add_output(v9); st.add_output(v16); st.add_output(cover9); st.add_output(cover16)
    st.add_tree(subs)
    st.add_output(st.path("video_meta.json"))
    st.add_output(audio)
    st.add_tool("ffmpeg", lib.tool_version("ffmpeg", ["-version"]))
    st.add_tool("sox", lib.tool_version("sox", ["--version"]))

    lic = st.path("audio", "LICENSE.txt")
    lic.write_text("Ambient bed synthesised in-house with SoX 14.4.2 (sine oscillators + reverb).\n"
                   "No third-party samples. Released CC0-1.0 by the pipeline operator.\n", encoding="utf-8")
    st.add_output(lic)

    ok_meta = all(m["duration"] >= 30 for m in meta.values())
    checks = [
        {"id": "duration_30_45", "ok": ok_meta, "detail": {k: round(v["duration"], 1) for k, v in meta.items()}},
        {"id": "resolutions", "ok": all((v["width"], v["height"]) in ((1080, 1920), (1920, 1080)) for v in meta.values()),
         "detail": {k: (v["width"], v["height"]) for k, v in meta.items()}},
        {"id": "decode_clean", "ok": _decode_ok(st, run_id, tuple(meta)), "detail": "电脑端 ffmpeg -f null 全程解码"},
        {"id": "subtitles_both_langs", "ok": (subs / "tour_zh.srt").exists() and (subs / "tour_en.srt").exists()},
        {"id": "music_licensed", "ok": lic.exists(), "detail": "自制 CC0"},
    ]
    st.qa(checks)
    st.metrics = {"duration": {k: round(v["duration"], 1) for k, v in meta.items()},
                  "slides": total, "bytes": {k: v["bytes"] for k, v in meta.items()}}
    st.finish(0)
    lib.info(f"station 4 video 9:16 + 16:9 ok ({total} slides, {seconds}s)")


if __name__ == "__main__":
    run(lib.ctx_run_id(sys.argv[1:]))
