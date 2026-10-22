"""Shared plumbing for every station: hashing, schema checks, handoff/qa/scorecard.

Design rules (from the task book):
  * a station only reads the previous station's files;
  * every handoff records input sha256, output sha256, schema name, tool versions,
    wall time and exit code;
  * every qa.json records metric + threshold + measured value;
  * any schema violation raises StationStop and exits non-zero.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "schemas"
RUNS = ROOT / "runs"
REPORTS = ROOT / "reports"

# Fixed tool locations (this device ships an iOS ffmpeg first on PATH; /opt/ffmpeg
# holds the Alpine build with libx264/libass/loudnorm). Override via env in CI.
# Two ffmpeg builds are in play on this device and both are needed:
#   FFMPEG_CPU  Alpine 6.1.2 — libx264, libass, drawtext (slow: ~1 fps at 1088x1920)
#   FFMPEG_HW   iOS build  — Apple VideoToolbox encoder + zoompan/overlay (fast: ~26 fps)
# Station 3 uses HW for clip renders; the CPU build is the documented fallback and the
# only one that can encode libx264.
FFMPEG_CPU = os.environ.get("FFMPEG_CPU", "/opt/ffmpeg/bin/ffmpeg")
FFMPEG_HW = os.environ.get("FFMPEG_HW", "/opt/ffmpeg/bin/ffmpeg")
FFMPEG = FFMPEG_CPU
VIDEO_ENC = os.environ.get("VIDEO_ENC", "libx264")  # CPU only
THREADS = os.environ.get("FFMPEG_THREADS", "6")

FFPROBE = os.environ.get("FFPROBE_BIN", "/opt/ffmpeg/bin/ffprobe")
FONT_ZH = os.environ.get("FONT_ZH", str(ROOT / "assets/fonts/NotoSansSC-Bold.otf"))
FONT_ZH_REG = os.environ.get("FONT_ZH_REG", str(ROOT / "assets/fonts/NotoSansSC-Regular.otf"))
FONT_EN = os.environ.get("FONT_EN", "/usr/share/fonts/inter/Inter-ExtraBold.otf")
FONT_EN_BODY = os.environ.get("FONT_EN_BODY", "/usr/share/fonts/inter/Inter-Medium.otf")

VIDEO_EXTS = {".mp4", ".mov", ".m4v"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}


class StationStop(Exception):
    """Raised when a station refuses to continue (schema / fact / asset gate)."""


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, obj) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write("\n")
    os.replace(tmp, path)
    return path


def rel(path: Path) -> str:
    """Repository-relative path, stable across machines."""
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


# --------------------------------------------------------------------------- #
# Schema validation
# --------------------------------------------------------------------------- #
def load_schema(name: str) -> dict:
    return read_json(SCHEMA_DIR / f"{name}.schema.json")


def validate(obj, schema_name: str, *, where: str = "") -> None:
    """Validate with jsonschema; any error stops the station."""
    try:
        import jsonschema
    except ImportError as exc:  # pragma: no cover
        raise StationStop(f"jsonschema missing: {exc}") from exc

    schema = load_schema(schema_name)
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        lines = [f"{where or schema_name}: {len(errors)} schema violation(s)"]
        for err in errors[:12]:
            loc = "/".join(str(p) for p in err.path) or "<root>"
            lines.append(f"  - {loc}: {err.message}")
        raise StationStop("\n".join(lines))


# --------------------------------------------------------------------------- #
# Tiny command runner with timing + captured output
# --------------------------------------------------------------------------- #
@dataclass
class CmdResult:
    cmd: list
    code: int
    seconds: float
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.code == 0

    def tail(self, n: int = 600) -> str:
        text = (self.stderr or self.stdout or "").strip()
        return text[-n:]


def run_cmd(cmd, *, cwd=None, timeout=1800, check=False, env=None) -> CmdResult:
    started = time.time()
    proc = subprocess.run(
        [str(c) for c in cmd],
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
        timeout=timeout,
        env=env,
    )
    res = CmdResult([str(c) for c in cmd], proc.returncode, round(time.time() - started, 2),
                    proc.stdout, proc.stderr)
    if check and not res.ok:
        raise StationStop(f"command failed ({res.code}): {' '.join(res.cmd)}\n{res.tail(1200)}")
    return res


def ffprobe_json(path: Path) -> dict:
    res = run_cmd([FFPROBE, "-v", "error", "-show_format", "-show_streams",
                   "-of", "json", str(path)], check=True)
    return json.loads(res.stdout)


def media_info(path: Path) -> dict:
    """Normalised probe record used by media_manifest and QA."""
    data = ffprobe_json(path)
    v = next((s for s in data["streams"] if s.get("codec_type") == "video"), {})
    a = next((s for s in data["streams"] if s.get("codec_type") == "audio"), {})
    num, den = (v.get("r_frame_rate") or "0/1").split("/")
    fps = float(num) / float(den) if float(den or 1) else 0.0
    return {
        "duration": round(float(data["format"].get("duration", 0) or 0), 3),
        "size_bytes": int(data["format"].get("size", 0) or 0),
        "width": int(v.get("width", 0) or 0),
        "height": int(v.get("height", 0) or 0),
        "fps": round(fps, 3),
        "vcodec": v.get("codec_name"),
        "acodec": a.get("codec_name"),
        "channels": int(a.get("channels", 0) or 0),
        "sample_rate": int(a.get("sample_rate", 0) or 0),
    }


def tool_version(cmd, pattern=r"(\d+\.\d+(?:\.\d+)?)") -> str:
    try:
        res = run_cmd(cmd, timeout=30)
        text = (res.stdout or "") + (res.stderr or "")
        m = re.search(pattern, text)
        return m.group(1) if m else (text.splitlines()[0][:80] if text else "unknown")
    except Exception:  # pragma: no cover
        return "missing"


def toolchain_versions() -> dict:
    import cv2
    import numpy
    import PIL
    return {
        "python": platform.python_version(),
        "ffmpeg": tool_version([FFMPEG, "-version"]),
        "ffprobe": tool_version([FFPROBE, "-version"]),
        "pillow": PIL.__version__,
        "opencv": cv2.__version__,
        "numpy": numpy.__version__,
        "sox": tool_version(["sox", "--version"]),
        "vips": tool_version(["vips", "--version"]),
        "melt": tool_version(["melt", "-version"]),
    }


# --------------------------------------------------------------------------- #
# Station context: makes handoff.json + qa.json + scorecard.json mandatory
# --------------------------------------------------------------------------- #
@dataclass
class Station:
    run_id: str
    num: int
    slug: str
    title: str
    reads: list = field(default_factory=list)     # list[Path]
    outputs: list = field(default_factory=list)   # list[(Path, schema_name)]
    checks: list = field(default_factory=list)
    started: float = field(default_factory=time.time)
    seed: int = 20261022
    notes: list = field(default_factory=list)

    @property
    def dir(self) -> Path:
        return RUNS / self.run_id / f"{self.num:02d}_{self.slug}"

    def path(self, *parts) -> Path:
        p = self.dir.joinpath(*parts)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def read(self, path: Path) -> Path:
        self.reads.append(Path(path))
        return Path(path)

    def emit(self, path: Path, schema: str) -> Path:
        self.outputs.append((Path(path), schema))
        return Path(path)

    def check(self, cid: str, desc: str, value, threshold: str, passed: bool, detail: str = "",
              severity: str = "blocking"):
        self.checks.append({
            "id": cid, "desc": desc, "value": value, "threshold": threshold,
            "pass": bool(passed), "severity": severity, "detail": detail,
        })
        return passed

    def require(self, cond: bool, msg: str):
        if not cond:
            raise StationStop(f"[{self.num:02d} {self.slug}] {msg}")

    # -- writers ----------------------------------------------------------- #
    def finish(self, tool_versions: dict, exit_code: int = 0) -> dict:
        seconds = round(time.time() - self.started, 2)
        handoff = {
            "run_id": self.run_id,
            "station": f"{self.num:02d}_{self.slug}",
            "title": self.title,
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.started)),
            "finished_at": now(),
            "elapsed_seconds": seconds,
            "exit_code": exit_code,
            "seed": self.seed,
            "inputs": [{"path": rel(p), "sha256": sha256(p)} for p in self.reads if p.exists()],
            "outputs": [
                {"path": rel(p), "sha256": sha256(p), "schema": s, "bytes": p.stat().st_size}
                for p, s in self.outputs if p.exists()
            ],
            "tool_versions": tool_versions,
        }
        write_json(self.dir / "handoff.json", handoff)
        qa = {
            "run_id": self.run_id,
            "station": f"{self.num:02d}_{self.slug}",
            "generated_at": now(),
            "checks": self.checks,
            "passed": all(c["pass"] for c in self.checks if c.get("severity") == "blocking") and bool(self.checks),
            "blocking_failures": [c["id"] for c in self.checks if c["severity"] == "blocking" and not c["pass"]],
            "advisory_failures": [c["id"] for c in self.checks if c["severity"] != "blocking" and not c["pass"]],
            "notes": self.notes,
        }
        write_json(self.dir / "qa.json", qa)
        return handoff


def write_scorecard(station_dir: Path, station: str, scores: dict, notes: list) -> dict:
    for key in ("business", "handoff", "benchmark", "craft"):
        if key not in scores:
            raise StationStop(f"scorecard {station}: missing dimension {key}")
        if not 0 <= float(scores[key]) <= 5:
            raise StationStop(f"scorecard {station}: {key} out of range")
    total = (scores["business"] * 0.35 + scores["handoff"] * 0.25
             + scores["benchmark"] * 0.15 + scores["craft"] * 0.25)
    card = {
        "station": station,
        "scores": {k: round(float(v), 2) for k, v in scores.items()},
        "weights": {"business": 0.35, "handoff": 0.25, "benchmark": 0.15, "craft": 0.25},
        "total": round(total, 2),
        "notes": notes,
        "generated_at": now(),
    }
    write_json(station_dir / "scorecard.json", card)
    return card


def station_main(fn, num: int, slug: str, title: str):
    """Wrap a station entry point with uniform error handling (non-zero exit)."""
    run_id = os.environ.get("RUN_ID", "")
    if not run_id:
        print("RUN_ID missing", file=sys.stderr)
        sys.exit(2)
    st = Station(run_id, num, slug, title)
    st.dir.mkdir(parents=True, exist_ok=True)
    try:
        result = fn(st)
        versions = toolchain_versions()
        if isinstance(result, dict) and "scores" in result:
            write_scorecard(st.dir, f"{num:02d}_{slug}", result["scores"], result.get("notes", []))
        st.finish(versions, 0)
        print(f"[{num:02d} {slug}] OK  {st.dir}")
        return 0
    except StationStop as exc:
        st.notes.append(str(exc))
        st.finish(toolchain_versions(), 1)
        print(f"[{num:02d} {slug}] STOP: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # unexpected: keep the trace for the failure report
        st.notes.append(f"{type(exc).__name__}: {exc}")
        st.finish(toolchain_versions(), 1)
        traceback.print_exc()
        return 1
