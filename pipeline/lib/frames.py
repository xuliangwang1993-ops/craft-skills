"""Ken Burns + grade frame generator (PIL), piped to ffmpeg for encoding.

Why not ffmpeg's zoompan + curves?
    On this device (iSH / A12-class CPU) zoompan at 1088x1920 costs ~1.8 s/frame and
    curves adds ~2.8 s/frame more; a 135-frame shot took 10+ minutes. Doing the crop,
    the resize and the grade in PIL costs ~0.05 s/frame, so the encoder is the only
    real cost left. The visual result is the same arithmetic (crop → resize → curve),
    and every parameter stays in grade.json.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

# /usr/bin/ffmpeg is the iOS build; on this device it can lock itself out after a
# killed encode ("until the app is restarted"). Always encode with the Alpine build.
FFMPEG = os.environ.get("FFMPEG_CPU", "/opt/ffmpeg/bin/ffmpeg")

import numpy as np
from PIL import Image, ImageFilter

W, H = 1088, 1920
UPSCALE = 1.35  # headroom so a 1.14x zoom never reads past the source edge


def _lut(gain: float, warmth: float, saturation: float) -> list:
    """256-entry LUTs per channel: exposure gain, warm/cool balance, saturation."""
    x = np.arange(256, dtype=np.float64) / 255.0
    x = np.clip(x * gain, 0, 1)
    # gentle S-curve keeps black point and white point
    x = np.clip(0.5 + (x - 0.5) * 1.06, 0, 1)
    r = np.clip(x * (1.0 + warmth), 0, 1)
    g = np.clip(x * (1.0 + warmth * 0.35), 0, 1)
    b = np.clip(x * (1.0 - warmth * 0.85), 0, 1)
    if abs(saturation - 1.0) > 1e-6:
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
        r = np.clip(lum + (r - lum) * saturation, 0, 1)
        g = np.clip(lum + (g - lum) * saturation, 0, 1)
        b = np.clip(lum + (b - lum) * saturation, 0, 1)
    return [Image.fromarray((c * 255).round().astype(np.uint8)).point(lambda v: v) for c in (r, g, b)]


def prepare(plate: Path, gain: float, warmth: float, saturation: float) -> Image.Image:
    img = Image.open(plate).convert("RGB")
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    img = img.resize((int(W * UPSCALE), int(H * UPSCALE)), Image.LANCZOS)
    r, g, b = _lut(gain, warmth, saturation)
    return Image.merge("RGB", (img.split()[0].point(list(r.getdata())),
                               img.split()[1].point(list(g.getdata())),
                               img.split()[2].point(list(b.getdata()))))


def plate_luma(plate: Path) -> float:
    img = Image.open(plate).convert("L")
    return float(np.asarray(img, dtype=np.float64).mean())


def render(plate: Path, out: Path, *, frames: int, fps: int, motion: str,
           gain: float, warmth: float, saturation: float, encoder: str,
           crf: int = 20, preset: str = "ultrafast", threads: int = 6) -> dict:
    base = prepare(plate, gain, warmth, saturation)
    bw, bh = base.size
    zoom_max = 1.14

    cmd = [FFMPEG, "-y", "-v", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
           "-c:v", encoder, "-preset", preset, "-crf", str(crf), "-threads", str(threads),
           "-pix_fmt", "yuv420p", "-r", str(fps), str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    for i in range(frames):
        t = i / max(1, frames - 1)
        if motion == "push_in":
            z = 1.0 + (zoom_max - 1.0) * t
        elif motion == "pull_back":
            z = zoom_max - (zoom_max - 1.0) * t
        elif motion == "drift_up":
            z = 1.10
        else:  # settle
            z = 1.0 + 0.05 * (1 - (1 - t) ** 2)
        cw, ch = int(bw / z), int(bh / z)
        if motion == "drift_up":
            x = (bw - cw) // 2
            y = int((bh - ch) * t)
        else:
            x = (bw - cw) // 2
            y = (bh - ch) // 2
        frame = base.crop((x, y, x + cw, y + ch)).resize((W, H), Image.BILINEAR)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", "replace")
    code = proc.wait()
    return {"exit": code, "stderr": err[-500:]}
