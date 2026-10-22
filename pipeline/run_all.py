#!/usr/bin/env python3
"""One-command entry point: `make run SENTENCE="..."`.

Creates runs/<run_id>/ and walks stations 00 → 07. A station that exits non-zero
stops the chain (that is the point of the exercise: the next station never sees a
broken handoff). Writes runs/<run_id>/run_manifest.json either way.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIONS = [
    ("00_brief", "s00_brief.py", "需求解析"),
    ("01_collect", "s01_collect.py", "素材采集"),
    ("02_script", "s02_script.py", "脚本/分镜"),
    ("03_edit", "s03_edit.py", "切镜/调色/清音/响度"),
    ("04_subs", "s04_subs.py", "字幕"),
    ("05_compose", "s05_compose.py", "合成"),
    ("06_qa", "s06_qa.py", "后测"),
    ("07_customer", "s07_customer.py", "客服知识包"),
]


def main() -> int:
    sentence = os.environ.get("SENTENCE", "").strip()
    if not sentence:
        print('SENTENCE is required, e.g. make run SENTENCE="给...做一支 30 秒宣传短视频"', file=sys.stderr)
        return 2
    run_id = os.environ.get("RUN_ID") or time.strftime("%Y%m%dT%H%M%S")
    run_dir = ROOT / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "run_id": run_id,
        "sentence": sentence,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python": sys.version.split()[0],
        "stations": [],
        "status": "running",
    }
    env = dict(os.environ, RUN_ID=run_id, SENTENCE=sentence)

    for folder, script, title in STATIONS:
        print(f"\n=== {folder} · {title} ===", flush=True)
        t0 = time.time()
        proc = subprocess.run([sys.executable, str(ROOT / "pipeline/stations" / script)],
                              env=env, cwd=str(ROOT))
        elapsed = round(time.time() - t0, 1)
        manifest["stations"].append({"station": folder, "title": title,
                                     "exit_code": proc.returncode, "seconds": elapsed})
        if proc.returncode != 0:
            manifest["status"] = "stopped"
            manifest["stopped_at"] = folder
            manifest["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            (run_dir / "run_manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"\nCHAIN STOPPED at {folder} (exit {proc.returncode}). "
                  f"Downstream stations did not run.", file=sys.stderr)
            return proc.returncode

    manifest["status"] = "done"
    manifest["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (run_dir / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # reports are regenerated from the run's own station outputs
    subprocess.run([sys.executable, str(ROOT / "pipeline/report.py"), run_id],
                   env=env, cwd=str(ROOT), check=False)
    print(f"\nDONE → {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
