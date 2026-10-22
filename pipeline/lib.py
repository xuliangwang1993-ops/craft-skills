"""craft-skills pipeline common library.

Every station is a python module `sN_*.py` with a `run(ctx)` entry point.
The library enforces the contract:
  * read only the previous station's outputs (declared in inputs[])
  * validate every structured input against schemas/
  * write handoff.json / qa.json / scorecard.json
  * exit non-zero on any failed gate
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
RUNS = ROOT / "runs"

try:  # jsonschema is a pure-python dep, always installable
    import jsonschema
except Exception:  # pragma: no cover
    jsonschema = None


class PipelineError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, obj) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write("\n")
    os.replace(tmp, path)
    return path


def load_schema(name: str) -> dict:
    return read_json(SCHEMAS / f"{name}.schema.json")


def validate(name: str, obj, label: str = "") -> None:
    """Validate obj against schemas/<name>.schema.json. Raises PipelineError."""
    if jsonschema is None:
        raise PipelineError("jsonschema missing: pip install jsonschema")
    schema = load_schema(name)
    try:
        jsonschema.validate(obj, schema)
    except jsonschema.ValidationError as exc:
        where = "/".join(str(p) for p in exc.absolute_path)
        raise PipelineError(
            f"schema {name} rejected {label or ''} at {where}: {exc.message}"
        ) from exc


def validate_file(name: str, path: Path) -> None:
    validate(name, read_json(path), label=str(path))


def run(cmd, cwd: Path | None = None, timeout: int = 1800, env: dict | None = None):
    """Run a command, capture output, never raise on non-zero."""
    t0 = time.time()
    proc = subprocess.run(
        cmd,
        shell=isinstance(cmd, str),
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, **(env or {})},
    )
    return {
        "cmd": cmd if isinstance(cmd, str) else " ".join(cmd),
        "rc": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stdout_full": proc.stdout[-1_000_000:],
        "stderr": proc.stderr[-4000:],
        "seconds": round(time.time() - t0, 2),
    }


@dataclass
class Station:
    num: str
    slug: str
    run_id: str
    inputs: list = field(default_factory=list)
    outputs: list = field(default_factory=list)
    tools: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    notes: list = field(default_factory=list)
    started: float = field(default_factory=time.time)

    @property
    def dir(self) -> Path:
        d = RUNS / self.run_id / f"{self.num}_{self.slug}"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def prev_dir(self) -> Path:
        """Directory of the previous station, resolved from the run root."""
        self.dir.mkdir(parents=True, exist_ok=True)  # materialise own station dir first
        runroot = RUNS / self.run_id
        nums = sorted(p.name for p in runroot.iterdir() if p.is_dir() and re.match(r"^\d\d_", p.name))
        idx = [n for n in nums if n.startswith(self.num + "_")]
        if not idx:
            raise PipelineError(f"station dir not found for {self.num}")
        i = nums.index(idx[0])
        if i == 0:
            raise PipelineError(f"station {self.num} has no predecessor")
        return runroot / nums[i - 1]

    def path(self, *parts) -> Path:
        p = self.dir.joinpath(*parts)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def require_prev(self, filename: str, schema: str | None = None) -> Path:
        p = self.prev_dir / filename
        if not p.exists():
            raise PipelineError(
                f"{self.num}: missing upstream artifact {p} — previous station did not finish"
            )
        if schema:
            validate_file(schema, p)
        self.add_input(p)
        return p

    def require_upstream(self, station_num: str, filename: str, schema: str | None = None) -> Path:
        """Fetch an artifact from ANY upstream station, and prove it is the same bytes
        that station declared in handoff.outputs (sha256 match). Stronger than adjacency."""
        runroot = RUNS / self.run_id
        self.dir.mkdir(parents=True, exist_ok=True)
        cands = [p for p in runroot.iterdir() if p.is_dir() and p.name.startswith(station_num + "_")]
        if not cands:
            raise PipelineError(f"{self.num}: upstream station {station_num} not found")
        p = cands[0] / filename
        if not p.exists():
            raise PipelineError(f"{self.num}: {p} missing")
        if schema:
            validate_file(schema, p)
        h = sha256_file(p)
        handoff = read_json(cands[0] / "handoff.json")
        declared = {o["path"]: o["sha256"] for o in handoff["outputs"]}
        rel = str(p.relative_to(ROOT))
        if declared.get(rel) != h:
            raise PipelineError(
                f"{self.num}: {rel} sha256 {h[:12]} does not match upstream handoff "
                f"{str(declared.get(rel))[:12]} — artifact was modified after handoff")
        self.add_input(p)
        return p

    def add_input(self, path: Path):
        self.inputs.append({"path": str(path.relative_to(ROOT)), "sha256": sha256_file(path)})

    def add_output(self, path: Path, schema: str | None = None):
        rel = str(path.relative_to(ROOT))
        if schema:
            validate_file(schema, path)
        self.outputs.append({"path": rel, "sha256": sha256_file(path), "schema": schema})
        return path

    def add_tree(self, directory: Path, pattern: str = "**/*"):
        for p in sorted(directory.glob(pattern)):
            if p.is_file():
                self.add_output(p)

    def add_tool(self, name: str, version: str):
        self.tools.append({"name": name, "version": version})

    def qa(self, checks: list[dict]) -> dict:
        passed = all(c.get("ok") for c in checks)
        doc = {
            "station": f"{self.num}_{self.slug}",
            "checked_at": now(),
            "passed": passed,
            "checks": checks,
        }
        write_json(self.dir / "qa.json", doc)
        return doc

    def finish(self, exit_code: int = 0, error: str | None = None):
        handoff = {
            "station": f"{self.num}_{self.slug}",
            "run_id": self.run_id,
            "started_at": datetime.fromtimestamp(self.started, timezone.utc).replace(microsecond=0).isoformat(),
            "ended_at": now(),
            "duration_s": round(time.time() - self.started, 2),
            "exit_code": exit_code,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "tools": self.tools,
            "metrics": self.metrics,
            "notes": self.notes,
            "error": error,
        }
        write_json(self.dir / "handoff.json", handoff)
        validate_file("handoff", self.dir / "handoff.json")
        return handoff


def ctx_run_id(argv) -> str:
    run_id = os.environ.get("RUN_ID")
    for i, a in enumerate(argv):
        if a == "--run-id" and i + 1 < len(argv):
            run_id = argv[i + 1]
    if not run_id:
        raise PipelineError("RUN_ID not set (export RUN_ID=... or --run-id)")
    return run_id


def ensure_tool(name: str) -> str | None:
    return shutil.which(name)


def tool_version(cmd: str, args=("--version",)) -> str:
    if not shutil.which(cmd):
        return "missing"
    try:
        r = run([cmd, *args], timeout=25)
    except Exception:
        return "timeout"
    txt = (r["stdout"] or r["stderr"]).strip().splitlines()
    return txt[0][:120] if txt else "unknown"


def die(msg: str, code: int = 1):
    print(f"[FAIL] {msg}", file=sys.stderr)
    raise SystemExit(code)


def info(msg: str):
    print(f"[ok] {msg}")
