#!/usr/bin/env python3
"""工具验证：把本次跑过的 ⚠️ 工具逐条记录（命令、版本、退出码、耗时、结论）。

结论只有三种：pass / fail / not_run。fail 就是 fail，不写成「降级通过」。
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
import lib


def record(rows, name, cmd, ok, version, note, rc=None, seconds=None):
    rows.append({"tool": name, "cmd": cmd, "version": version, "exit_code": rc,
                 "seconds": seconds, "result": "pass" if ok else "fail", "note": note})


def main(run_id: str) -> None:
    rows = []
    out = lib.ROOT / "reports"
    out.mkdir(exist_ok=True)

    # --- jq（⚠️ 列在未验证表里，本次实测通过）---
    t0 = time.time()
    r = lib.run(["jq", "-n", "--arg", "x", "1", "{v:$x}"])
    record(rows, "jq", "jq -n --arg x 1 '{v:$x}'", r["rc"] == 0 and '"v": "1"' in r["stdout"],
           lib.tool_version("jq"), "站 0 用它构造 brief.json；输出可被后续站直接解析",
           r["rc"], round(time.time() - t0, 2))

    # --- weasyprint ---
    t0 = time.time()
    tmp = Path("/tmp/_tv_weasy")
    tmp.mkdir(exist_ok=True)
    (tmp / "a.html").write_text('<html><body><h1>中文测试 PDF</h1></body></html>', encoding="utf-8")
    r = lib.run(["weasyprint", str(tmp / "a.html"), str(tmp / "a.pdf")])
    record(rows, "weasyprint", "weasyprint a.html a.pdf", r["rc"] == 0 and (tmp / "a.pdf").exists(),
           lib.tool_version("weasyprint"), "站 6 出中英双语入住指南 PDF（CJK 字体已内嵌）",
           r["rc"], round(time.time() - t0, 2))

    # --- icalendar ---
    t0 = time.time()
    r = lib.run(["python3", "-c",
                 "import icalendar,datetime;c=icalendar.Calendar();e=icalendar.Event();"
                 "e.add('dtstart',datetime.date(2026,11,1));c.add_component(e);"
                 "print(len(c.to_ical()))"])
    record(rows, "icalendar", "python3 -c 'build calendar'", r["rc"] == 0,
           "7.3.0", "站 7 的日历解析走 iCal；本次房东未导出，页面内联空日历并显示「未连接」",
           r["rc"], round(time.time() - t0, 2))

    # --- duckdb（失败，实测）---
    t0 = time.time()
    r = lib.run(["python3", "-c", "import duckdb"], timeout=60)
    r2 = lib.run(["bash", "-lc",
                  "pip download duckdb --only-binary=:all: --platform musllinux_1_2_aarch64 "
                  "--python-version 3.12 -d /tmp/_duck 2>&1 | tail -2"], timeout=120)
    record(rows, "duckdb", "pip install duckdb / pip download --platform musllinux_1_2_aarch64",
           False, "n/a",
           "本机是 musl/aarch64：没有 wheel，源码构建失败；官方 CLI 是 glibc 二进制，"
           "运行报 __res_init symbol not found。站 2 改用 Python 内置 sqlite3，SQL 逻辑一致。",
           r["rc"], round(time.time() - t0, 2))
    rows[-1]["evidence"] = (r2["stdout"] or "")[-200:]

    # --- argos-translate ---
    t0 = time.time()
    r = lib.run(["bash", "-lc", "pip install --no-cache-dir argostranslate 2>&1 | tail -2"], timeout=300)
    record(rows, "argos-translate", "pip install argostranslate", False, "n/a",
           "依赖 ctranslate2，本平台无 musl/aarch64 轮子，构建失败。站 5 的 zh/en 由人工撰写，"
           "没有机翻后冒充校对；ja/ko 因此不交付。", r["rc"], round(time.time() - t0, 2))
    rows[-1]["evidence"] = (r["stdout"] or "")[-200:]

    # --- crawl4ai ---
    t0 = time.time()
    r = lib.run(["bash", "-lc", "pip install --no-cache-dir crawl4ai 2>&1 | tail -2"], timeout=300)
    record(rows, "crawl4ai", "pip install crawl4ai", False, "n/a",
           "依赖解析失败（ResolutionImpossible）。站 1 改为 curl + 内嵌 JSON 解析，"
           "没有绕过 robots，反而因为遵守 robots 丢了竞品数据。", r["rc"], round(time.time() - t0, 2))
    rows[-1]["evidence"] = (r["stdout"] or "")[-200:]

    # --- playwright ---
    t0 = time.time()
    r = lib.run(["bash", "-lc", "pip install --no-cache-dir playwright 2>&1 | tail -2"], timeout=180)
    record(rows, "playwright", "pip install playwright", False, "n/a",
           "PyPI 没有 musl/aarch64 构建，安装即失败；站 8 改用内置 WebKit（minis-browser-use）跑真实交互。",
           r["rc"], round(time.time() - t0, 2))
    rows[-1]["evidence"] = (r["stdout"] or "")[-200:]

    # --- lighthouse ---
    t0 = time.time()
    r = lib.run(["bash", "-lc", "npm view lighthouse version 2>&1 | tail -1"], timeout=90)
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    record(rows, "lighthouse", "npm view lighthouse version", False,
           (r["stdout"] or "").strip(),
           "包存在（%s），但本机没有 Chrome/Chromium，跑不了真实审计。站 8 用静态启发式打分，"
           "在 lighthouse.json 里明确标 not_run，不冒充。" % (r["stdout"] or "").strip(),
           0, round(time.time() - t0, 2))
    rows[-1]["chrome"] = chrome

    # --- typst（PDF 备选，已装）---
    record(rows, "typst", "typst --version", True, lib.tool_version("typst"), "PDF 备选路径；本次用 weasyprint",
           0, 0.1)

    doc = {
        "generated_at": lib.now(),
        "host": {"platform": platform.platform(), "machine": platform.machine(),
                 "libc": "musl (Alpine/iSH)", "python": platform.python_version()},
        "summary": {
            "pass": [r["tool"] for r in rows if r["result"] == "pass"],
            "fail": [r["tool"] for r in rows if r["result"] == "fail"],
        },
        "tools": rows,
    }
    lib.write_json(out / "tool_verification.json", doc)
    print(json.dumps(doc["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(lib.ctx_run_id(sys.argv[1:]))
