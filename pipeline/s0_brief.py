#!/usr/bin/env python3
"""Station 0 — 需求解析（工具：jq）

一句话需求 -> brief.json。用 jq 构造 JSON，证明 ⚠️jq 在本机可用且版本可记录。
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import lib
from lib import PipelineError

SENTENCE_DEFAULT = "给我家 Airbnb（Home in Rosebery · 独立房间）做全套上架包"
LISTING_ID = "1286789934809628478"

DELIVERABLES = [
    "photos",           # 精修照片 + 排序 + 中英图注
    "tour_video_9x16",  # 1080x1920
    "tour_video_16x9",  # 1920x1080
    "listing_copy",     # zh / en
    "guest_guide_pdf",  # zh / en
    "direct_booking_site",
    "support_kb",
]


def jq_build(sentence: str, run_id: str) -> dict:
    """Build brief.json with jq (single source of shape, not python dict dumps)."""
    tpl = {
        "run_id": None, "sentence": None, "listing_id": None,
        "deliverable": DELIVERABLES, "languages": ["zh", "en"],
        "video": {"sizes": ["9:16", "16:9"], "duration_s": 40},
        "created_at": None,
    }
    script = (
        '.run_id=$run | .sentence=$sentence | .listing_id=$lid | .created_at=$ts'
    )
    r = lib.run([
        "jq", "-n",
        "--argjson", "tpl", json.dumps(tpl, ensure_ascii=False),
        "--arg", "run", run_id,
        "--arg", "sentence", sentence,
        "--arg", "lid", LISTING_ID,
        "--arg", "ts", lib.now(),
        "$tpl | " + script,
    ])
    if r["rc"] != 0:
        raise PipelineError(f"jq failed: {r['stderr']}")
    return json.loads(r["stdout"])


def run(run_id: str) -> None:
    st = lib.Station("00", "brief", run_id)
    st.add_tool("jq", lib.tool_version("jq"))
    sentence = os.environ.get("SENTENCE", SENTENCE_DEFAULT)
    brief = jq_build(sentence, run_id)
    out = st.path("brief.json")
    lib.write_json(out, brief)
    st.add_output(out, "brief")

    st.qa([
        {"id": "listing_id_present", "ok": bool(brief["listing_id"]), "detail": brief["listing_id"]},
        {"id": "deliverables_ge_5", "ok": len(brief["deliverable"]) >= 5, "detail": len(brief["deliverable"])},
        {"id": "languages", "ok": set(brief["languages"]) >= {"zh", "en"}, "detail": brief["languages"]},
        {"id": "video_sizes", "ok": set(brief["video"]["sizes"]) == {"9:16", "16:9"}},
    ])
    st.finish(0)
    lib.info(f"station 0 brief -> {out.relative_to(lib.ROOT)}")


if __name__ == "__main__":
    run(lib.ctx_run_id(sys.argv[1:]))
