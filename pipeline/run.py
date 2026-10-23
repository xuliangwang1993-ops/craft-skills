#!/usr/bin/env python3
"""统一入口：python pipeline/run.py "一句话需求"  （或 make run SENTENCE="..."）"""
import datetime, json, os, pathlib, random, sys, time, traceback
sys.path.insert(0, str(pathlib.Path(__file__).parent))
random.seed(20261023); os.environ.setdefault("PYTHONHASHSEED", "0")
from common import ROOT, StationFail, wjson
import stations_a as A, stations_b as B, station_c as C


def main():
    sentence = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SENTENCE", "")
    if not sentence: print("需要 SENTENCE"); sys.exit(64)
    rid = os.environ.get("RUN_ID") or datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ("-fault-" + os.environ["FAULT"] if os.environ.get("FAULT") else "")
    rd = ROOT / "runs" / rid; rd.mkdir(parents=True, exist_ok=True)
    t0 = time.time(); man = {"run_id": rid, "sentence": sentence, "fault": os.environ.get("FAULT"), "stations": []}
    try:
        b = A.s0_brief(rd, sentence); man["stations"].append("00_brief")
        fp, mp, lp = A.s1_ingest(rd, b); man["stations"].append("01_ingest")
        sp, menu = A.s2_script(rd, fp, mp); man["stations"].append("02_script")
        g = B.s3_grade(rd, sp, mp); man["stations"].append("03_grade")
        sd = B.s4_subs(rd, sp, g); man["stations"].append("04_subs")
        ex = B.s5_export(rd, sp, g, sd); man["stations"].append("05_export")
        B.s6_qa(rd, sp, ex); man["stations"].append("06_qa")
        C.s7_kb(rd, fp, menu, rd / "06_qa"); man["stations"].append("07_kb")
        man.update(status="ok", exit_code=0)
    except StationFail as e:
        man.update(status="failed", exit_code=2, failed_station=e.station, failed_step=e.step, why=e.why)
        print(f"\n✗ 停在 {e.station} / {e.step}\n  {e.why}", file=sys.stderr)
    except Exception as e:
        man.update(status="crashed", exit_code=3, why=repr(e), trace=traceback.format_exc()[-1500:]); traceback.print_exc()
    man["elapsed_s"] = round(time.time() - t0, 1)
    wjson(rd / "manifest.json", man)
    print(json.dumps({k: man.get(k) for k in ("run_id", "status", "failed_station", "failed_step", "elapsed_s")}, ensure_ascii=False))
    sys.exit(man["exit_code"])


if __name__ == "__main__":
    main()
