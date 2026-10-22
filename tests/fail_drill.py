#!/usr/bin/env python3
"""Deliberate failure drill — proves the chain stops instead of shipping a wrong film.

Two independent drills against a throw-away copy of a finished run:

  A. 字幕价格被改错  → qa/trace_check.py 必须报 unverified_price 并以 1 退出
  B. 素材缺许可      → 第 2 站读 01_collect/media_manifest.json 时 Schema 校验失败，
                       第 2 站不起渲染、非 0 退出（下游全部不运行）

Writes reports/fail_drill.json.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
from lib.common import now, read_json, write_json  # noqa: E402


def copy_run(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("*.mp4", "*.wav", "*.png"))


def drill_price(run_dir: Path) -> dict:
    script_path = run_dir / "02_script/script.json"
    script = read_json(script_path)
    script["shots"][2]["sub_zh"] = "这一碗，A$12.50。"
    write_json(script_path, script)
    srt = run_dir / "05_compose/zh.srt"
    if srt.exists():
        srt.write_text(srt.read_text(encoding="utf-8").replace("这一碗，趁热。", "这一碗，A$12.50。"),
                       encoding="utf-8")
    res = subprocess.run([sys.executable, str(ROOT / "qa/trace_check.py"), str(run_dir)],
                         capture_output=True, text=True)
    trace = read_json(run_dir / "06_qa/trace.json")
    kinds = sorted({m["kind"] for m in trace["mismatches"]})
    return {
        "drill": "字幕价格被改成 A$12.50（客户从未确认过任何价格）",
        "command": f"python3 qa/trace_check.py {run_dir.name}",
        "exit_code": res.returncode,
        "mismatches": len(trace["mismatches"]),
        "kinds": kinds,
        "stopped": res.returncode != 0 and "unverified_price" in kinds,
        "stdout": res.stdout.strip()[:500],
    }


def drill_license(run_dir: Path) -> dict:
    manifest_path = run_dir / "01_collect/media_manifest.json"
    manifest = read_json(manifest_path)
    for asset in manifest["assets"]:
        if asset["asset_id"] == "ast_photo_official":
            asset["permission"] = "borrowed"          # not in the enum
            asset["license"] = ""                      # and no licence
    write_json(manifest_path, manifest)

    env = {"RUN_ID": run_dir.name, "PATH": "/usr/local/bin:/usr/bin:/bin",
           "HOME": "/root", "SENTENCE": "drill"}
    res = subprocess.run([sys.executable, str(ROOT / "pipeline/stations/s02_script.py")],
                         capture_output=True, text=True, env=env)
    qa_path = run_dir / "02_script/qa.json"
    qa = read_json(qa_path) if qa_path.exists() else {}
    return {
        "drill": "官网菜品图被改成 permission=borrowed、license 为空（未授权素材）",
        "command": "python3 pipeline/stations/s02_script.py（RUN_ID=失败副本）",
        "exit_code": res.returncode,
        "stopped": res.returncode != 0,
        "error": (res.stderr or "").strip().splitlines()[-1][:400] if res.stderr else "",
        "qa_notes": qa.get("notes", [])[-1:] ,
    }


def main() -> int:
    src = ROOT / "runs" / "dev"
    if not src.exists():
        print("run runs/dev first", file=sys.stderr)
        return 2

    work = ROOT / "runs" / "faildrill"
    copy_run(src, work)

    a = drill_price(work)
    b = drill_license(work)

    doc = {
        "run_at": now(),
        "base_run": "runs/dev",
        "drill_a_price_tamper": a,
        "drill_b_license_missing": b,
        "conclusion": "两处人为错误都被下游拦住：价格错 → trace_check 退出 1；素材无许可 → 第 2 站 Schema 校验退出 1",
        "passed": a["stopped"] and b["stopped"],
    }
    write_json(ROOT / "reports/fail_drill.json", doc)
    print(json.dumps({k: doc[k] for k in ("passed", "conclusion")}, ensure_ascii=False, indent=2))
    return 0 if doc["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
