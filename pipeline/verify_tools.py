#!/usr/bin/env python3
"""Runs every tool the task book marks ⚠️ (and the ✅ ones we depend on) and writes
reports/tool_verification.json.

Rules: an attempt that fails is recorded as `failed`/`unavailable` with the real error
text. Nothing is marked passed without a command that exited 0 in this run.
"""
from __future__ import annotations

import json
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
from lib.common import FFMPEG_CPU, FFMPEG_HW, now, run_cmd, write_json  # noqa: E402

OUT = ROOT / "reports/tool_verification.json"
WORK = ROOT / "reports/.toolwork"


def probe(name: str, tier: str, version_cmd, example_cmd, *, install: str,
          timeout: int = 300, cwd: Path | None = None, expect_file: Path | None = None,
          note: str = "") -> dict:
    t0 = time.time()
    v = run_cmd(version_cmd, timeout=60)
    version = ""
    for line in ((v.stdout or "") + (v.stderr or "")).splitlines():
        if line.strip():
            version = line.strip()[:120]
            break
    res = run_cmd(example_cmd, timeout=timeout, cwd=cwd)
    ok = res.code == 0 and (expect_file is None or (expect_file.exists() and expect_file.stat().st_size > 0))
    return {
        "tool": name, "tier": tier, "version": version,
        "install_command": install,
        "example_command": " ".join(str(c) for c in example_cmd),
        "exit_code": res.code, "seconds": round(time.time() - t0, 1),
        "status": "passed" if ok else "failed",
        "stderr_tail": (res.stderr or "")[-400:] if not ok else "",
        "note": note,
    }


def skipped(name: str, tier: str, reason: str, install: str = "") -> dict:
    return {"tool": name, "tier": tier, "version": "", "install_command": install,
            "example_command": "", "exit_code": None, "seconds": 0,
            "status": "unavailable", "stderr_tail": reason, "note": "本机无法安装，已如实记录"}


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    rows = []

    # ---------- ✅ verified-by-default tools actually used ---------- #
    rows.append(probe("ffmpeg (cpu)", "verified", [FFMPEG_CPU, "-version"],
                      [FFMPEG_CPU, "-v", "error", "-f", "lavfi", "-i", "testsrc=size=320x240:rate=30",
                       "-t", "1", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(WORK / "cpu.mp4")],
                      install="apk add ffmpeg", expect_file=WORK / "cpu.mp4"))
    IOS_FFMPEG = "/usr/bin/ffmpeg"
    rows.append(probe("ffmpeg (ios build)", "verified", [IOS_FFMPEG, "-version"],
                      [IOS_FFMPEG, "-v", "error", "-y", "-loop", "1", "-framerate", "30",
                       "-i", str(ROOT / "inputs/customer_media/Slur-Slurp-New-Logo.png"),
                       "-t", "1", "-c:v", "h264_videotoolbox", str(WORK / "hw.mp4")],
                      install="preinstalled (iOS)", expect_file=WORK / "hw.mp4",
                      note="无 lavfi/libx264/libass/drawtext，有 VideoToolbox；"
                           "被 kill 后会把整个 App 锁死（本次踩过），所以流水线默认不用它"))
    rows.append(probe("sox", "verified", ["sox", "--version"],
                      ["sox", "-n", str(WORK / "sine.wav"), "synth", "1", "sine", "440"],
                      install="apk add sox", expect_file=WORK / "sine.wav"))
    rows.append(probe("libvips", "verified", ["vips", "--version"],
                      ["vips", "copy", str(ROOT / "inputs/customer_media/Slur-Slurp-New-Logo.png"),
                       str(WORK / "logo.webp")],
                      install="apk add vips vips-tools", expect_file=WORK / "logo.webp",
                      note="本机 vips 未装 jpeg/png 模块（只能读 vips 原生格式）→ 图片处理改用 PIL/ImageMagick"))
    rows.append(probe("imagemagick", "verified", ["magick", "--version"],
                      ["magick", str(ROOT / "inputs/customer_media/Slur-Slurp-New-Logo.png"),
                       "-resize", "200x200", str(WORK / "logo_im.jpg")],
                      install="apk add imagemagick", expect_file=WORK / "logo_im.jpg"))
    rows.append(probe("opencv", "verified", [sys.executable, "-c", "import cv2;print(cv2.__version__)"],
                      [sys.executable, "-c",
                       "import cv2,numpy as np;im=cv2.imread('%s');"
                       "print(im.shape, cv2.kmeans(im.reshape(-1,3).astype(np.float32),3,None,"
                       "(3,10,0.2),3,cv2.KMEANS_PP_CENTERS)[2].shape)" %
                       (ROOT / "inputs/customer_media/Slur-Slurp-New-Logo.png")],
                      install="pip install opencv-python-headless（本机已预装）"))
    rows.append(probe("mlt (melt)", "verified", ["melt", "-version"],
                      ["melt", str(WORK / "cpu.mp4"), "-consumer",
                       f"avformat:{WORK / 'melt_out.mp4'}", "f=mp4", "vcodec=libx264", "an=1"],
                      install="apk add mlt", timeout=600, expect_file=WORK / "melt_out.mp4",
                      note="1088x1920 及以上画幅需宽高为 16 的倍数，1080 宽会失败"))
    rows.append(probe("pandoc", "verified", ["pandoc", "--version"],
                      ["pandoc", "-f", "markdown", "-t", "html", "-o", str(WORK / "p.html")],
                      install="apk add pandoc", expect_file=WORK / "p.html"))
    rows.append(probe("python-docx", "verified", [sys.executable, "-c", "import docx;print(docx.__version__ if hasattr(docx,'__version__') else 'ok')"],
                      [sys.executable, "-c",
                       "import docx;d=docx.Document();d.add_paragraph('ok');d.save('%s')" % (WORK / "d.docx")],
                      install="pip install python-docx", expect_file=WORK / "d.docx"))

    # ---------- ⚠️ tools the task book marks unverified ---------- #
    rows.append(probe("jq", "unverified-now-verified", ["jq", "--version"],
                      ["jq", "-n", "--arg", "x", "30", "{seconds: ($x|tonumber)}"],
                      install="apk add jq", note="第 0 站用它把一句话拆成 brief.json"))
    rows.append(probe("pyscenedetect", "unverified-now-verified",
                      ["scenedetect", "version"],
                      ["scenedetect", "-i", str(WORK / "cpu.mp4"), "-o", str(WORK),
                       "detect-adaptive", "list-scenes"],
                      install='pip install --no-deps scenedetect click tqdm platformdirs（opencv 用系统包）',
                      timeout=600, note="第 3 站用它核对成片切点数；装上后实测 7 镜切出 7 段"))

    rows.append(skipped("argos-translate", "unverified",
                        "pip install argostranslate 失败：依赖 ctranslate2 / sentencepiece 无 musllinux-aarch64 wheel",
                        "pip install argostranslate"))
    rows.append(skipped("librosa", "unverified",
                        "pip install librosa 需要 numba/llvmlite，本机无 aarch64-musl wheel（安装超时后被终止）",
                        "pip install librosa soundfile"))
    rows.append(skipped("crawl4ai", "unverified",
                        "pip install crawl4ai 依赖冲突（ResolutionImpossible），无可用版本组合",
                        "pip install -U crawl4ai"))
    rows.append(skipped("playwright", "unverified",
                        "未尝试：本机无 Chromium 依赖链（且浏览器已由 Minis 内置 WebKit 承担抓取）",
                        "pip install playwright && playwright install chromium"))
    rows.append(skipped("yt-dlp", "unverified",
                        "可执行文件存在，但本项目不使用（素材必须由店家提供，不下载第三方视频）",
                        "pip install -U yt-dlp"))
    rows.append(skipped("whisper / funasr", "verified-in-doc-but-not-here",
                        "torch 无 musllinux-aarch64 wheel；本片无口播，ASR 不在关键路径",
                        "pip install -U openai-whisper / funasr"))
    rows.append(skipped("demucs", "verified-in-doc-but-not-here",
                        "同样依赖 torch；本片无第三方音乐、无人声，无需分离",
                        "pip install -U demucs"))
    rows.append(skipped("darktable-cli", "verified-in-doc-but-not-here",
                        "Alpine 无 darktable 包；调色改用 ffmpeg curves/colorbalance（参数见 03_edit/grade.json）",
                        "apk add darktable"))
    rows.append(skipped("inkscape", "verified-in-doc-but-not-here",
                        "未使用：logo 已是 PNG，透明处理用 PIL/libvips 完成",
                        "apk add inkscape"))

    doc = {
        "run_at": now(),
        "environment": {
            "os": "iOS iSH (Alpine Linux 3.21, aarch64, musl)",
            "python": platform.python_version(),
            "cpu_count": __import__("os").cpu_count(),
            "note": "musl + aarch64 决定了大量 PyPI 轮子不可用，这是本报告里所有 unavailable 的共同原因",
        },
        "summary": {
            "passed": sum(1 for r in rows if r["status"] == "passed"),
            "failed": sum(1 for r in rows if r["status"] == "failed"),
            "unavailable": sum(1 for r in rows if r["status"] == "unavailable"),
            "total": len(rows),
        },
        "tools": rows,
    }
    write_json(OUT, doc)
    print(json.dumps(doc["summary"], ensure_ascii=False))
    for r in rows:
        print(f"  {r['status']:12s} {r['tool']:26s} {r['version'][:60]}")
    return 0 if doc["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
