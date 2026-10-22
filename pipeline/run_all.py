#!/usr/bin/env python3
"""One-command pipeline: 0 → 9，任何一站失败立即停（非 0 退出）。

用法:
    make run SENTENCE="给我家 Airbnb 做全套上架包"
    python3 pipeline/run_all.py --sentence "..." --run-id R20261022-airbnb
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
import lib

STATIONS = [
    ("s0_brief", "00"),
    ("s1_collect", "01"),
    ("s2_pricing", "02"),
    ("s3_photos", "03"),
    ("s4_video", "04"),
    ("s5_copy", "05"),
    ("s6_guide", "06"),
    ("s7_site", "07"),
    ("s9_support", "09"),   # 知识包先就位，后测才能查覆盖率
    ("s8_qc", "08"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sentence", default=os.environ.get("SENTENCE", "给我家 Airbnb 做全套上架包"))
    ap.add_argument("--run-id", default=os.environ.get("RUN_ID", ""))
    ap.add_argument("--from", dest="start", default="")
    args = ap.parse_args()

    run_id = args.run_id or f"R{time.strftime('%Y%m%d-%H%M')}-airbnb"
    os.environ["RUN_ID"] = run_id
    os.environ["SENTENCE"] = args.sentence
    os.environ.setdefault("PYTHONHASHSEED", "0")
    print(f"== run {run_id} · {args.sentence}")

    started = args.start
    for mod_name, num in STATIONS:
        if started and num < started:
            continue
        mod = importlib.import_module(mod_name)
        fn = getattr(mod, "run", None) or getattr(mod, "build")
        t0 = time.time()
        try:
            fn(run_id)
        except Exception as exc:               # 任何一站失败 → 停，不写半成品交接
            print(f"\n[STOP] station {num} failed after {time.time()-t0:.1f}s: {exc}", file=sys.stderr)
            traceback.print_exc()
            return 2
        ho = lib.read_json(lib.RUNS / run_id / f"{num}_{mod_name.split('_', 1)[1]}" / "handoff.json")
        print(f"   handoff {ho['station']}: exit={ho['exit_code']} outputs={len(ho['outputs'])} "
              f"in {ho['duration_s']}s")

    # 收尾：评分卡 + 故障注入 + 工具验证
    import scorecards, failtest, verify_tools
    scorecards.main(run_id)
    failtest.main(run_id)
    verify_tools.main(run_id)
    print(f"\n== done. artifacts: runs/{run_id}/  reports/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
