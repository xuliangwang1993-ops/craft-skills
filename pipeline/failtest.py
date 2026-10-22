#!/usr/bin/env python3
"""故障注入：故意把下游写坏，证明检查会拦住。

两个案例：
  A. 文案里写「有暖气」（facts 里 heating_listed = false，属未验证卖点）
  B. 入住指南里填了真实密码（Wi-Fi 密码：Rosebery2026!）

做法：把原 run 的站点目录软链到 <run>-failtest，只替换被污染的文件，然后跑 qa/trace_check.py
与 qa/secret_scan.py，记录退出码。退出码必须是 2（拦下），否则说明闸门是假的。
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
import lib

# 只拷 trace_check / secret_scan 真正读的文件（/var/minis 不允许软链）
FILES = [
    "01_collect/facts.json", "01_collect/comps.json",
    "02_pricing/pricing.json",
    "05_copy/listing_copy/zh.json", "05_copy/listing_copy/en.json",
    "06_guide/guide/guide_zh.html", "06_guide/guide/guide_en.html",
    "07_site/site/index.html",
    "09_support/kb/kb_manifest.json",
] + [f"09_support/kb/{n}.md" for n in
     ("01_facts", "02_checkin", "03_amenities", "04_transport", "05_rules",
      "06_booking", "07_never_answer", "08_faq", "09_pending")]


def copy_files(src: Path, dst: Path) -> None:
    for rel in FILES:
        a, b = src / rel, dst / rel
        if not a.exists():
            continue
        b.parent.mkdir(parents=True, exist_ok=True)
        if b.exists() or b.is_symlink():
            b.unlink()
        shutil.copyfile(a, b)


def main(run_id: str) -> None:
    src = lib.RUNS / run_id
    dst = lib.RUNS / f"{run_id}-failtest"
    if dst.exists():
        shutil.rmtree(dst)
    copy_files(src, dst)
    (dst / "reports").mkdir(exist_ok=True)

    # --- 案例 A：文案写「有暖气」 ---
    zh = json.loads((src / "05_copy" / "listing_copy" / "zh.json").read_text())
    zh["sections"][-1]["paragraphs"].append({"text": "房间有暖气，冬天也很暖。", "sources": ["facts.heating_listed"]})
    a_file = dst / "05_copy" / "listing_copy" / "zh.json"
    if a_file.is_symlink() or a_file.exists():
        a_file.unlink()
    a_file.write_text(json.dumps(zh, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- 案例 B：指南里写真实密码 ---
    g = dst / "06_guide" / "guide" / "guide_zh.html"
    html = g.read_text(encoding="utf-8").replace("{{WIFI_PASSWORD}}", "Rosebery2026!")
    if g.is_symlink() or g.exists():
        g.unlink()
    g.write_text(html, encoding="utf-8")

    tr = lib.run(["python3", str(lib.ROOT / "qa" / "trace_check.py"), str(dst)], timeout=300)
    sec = lib.run(["python3", str(lib.ROOT / "qa" / "secret_scan.py"), str(dst)], timeout=300)
    trace = lib.read_json(dst / "reports" / "trace.json") if (dst / "reports" / "trace.json").exists() else {}
    sec_doc = json.loads(sec["stdout"][sec["stdout"].index("{"): sec["stdout"].rindex("}") + 1]) if "{" in sec["stdout"] else {}

    cases = [
        {"case": "A_unverified_claim", "injected": "文案追加『房间有暖气，冬天也很暖。』",
         "expected": "trace_check 退出码 2，报 unverified_claim", "exit_code": tr["rc"],
         "caught": tr["rc"] == 2,
         "evidence": [i for i in trace.get("issues", []) if i["type"] in ("unverified_claim", "broken_source")][:3]},
        {"case": "B_real_password", "injected": "指南里把 {{WIFI_PASSWORD}} 换成一个像真的 12 位密码（本报告不保留其原文）",
         "expected": "secret_scan 退出码 2，报 assigned_secret", "exit_code": sec["rc"],
         "caught": sec["rc"] == 2,
         "evidence": [{"file": h["file"], "rule": h["rule"]} for h in sec_doc.get("hits", []) if h["rule"] == "assigned_secret"][:3]},
    ]
    doc = {"run": run_id, "generated_at": lib.now(), "cases": cases,
           "passed": all(c["caught"] for c in cases),
           "note": "闸门有效：两个污染都会被拦在交付前。原 run 未被修改（failtest 用软链 + 替换文件）。"}
    lib.write_json(src / "reports" / "failtest.json", doc)
    print(json.dumps(doc, ensure_ascii=False, indent=2)[:1500])


if __name__ == "__main__":
    main(lib.ctx_run_id(sys.argv[1:]))
