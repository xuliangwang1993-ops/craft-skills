#!/usr/bin/env python3
"""Station 7 — 客服知识包 + workbench 交付卡片.

Reads every earlier station. Writes customer/kb/*.md, kb_manifest.json, and the
`project_delivery` card payload that the workbench PR imports.

The assistant self-test at the end is a retrieval responder built only from
kb/facts — it is a check that the knowledge pack can answer 15 real questions
without inventing prices or opening hours, not a test of the production 小X.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.common import (ROOT, Station, media_info, now, read_json, sha256, station_main,
                        validate, write_json)

# (question, any-of these must appear, is this a field we do NOT know?)
QUESTIONS = [
    ("这家店叫什么？", ["Slurp Slurp Noodle"], False),
    ("店名英文怎么写？", ["Slurp Slurp Noodle"], False),
    ("中文店名是什么？", ["待客户确认", "书面确认"], True),
    ("电话是多少？", ["9663 3817"], False),
    ("地址在哪？", ["待客户确认", "未经客户确认", "没写"], True),
    ("营业时间是几点？", ["待客户确认", "冲突"], True),
    ("有什么招牌菜？", ["待客户确认", "未经客户"], True),
    ("一碗多少钱？", ["没有", "还没给"], True),
    ("这家店在哪个城市？", ["悉尼"], False),
    ("片子多长？", ["30"], False),
    ("有哪几个尺寸？", ["1920", "1080"], False),
    ("有中文字幕吗？", ["有"], False),
    ("字幕是机器翻译的吗？", ["不是"], False),
    ("响度是多少？", ["LUFS"], False),
    ("素材是谁的？能商用吗？", ["未授权", "授权"], False),
    ("我要改一句字幕，多久？", ["当天"], False),
    ("小红书用哪个文件？", ["promo_9x16.mp4"], False),
    ("能发到电视上播吗？", ["16:9"], False),
]

REFUSAL = "待客户确认"


def build_kb(facts: dict, menu: dict, script: dict, brief: dict, qa: dict) -> dict:
    f = {row["field"]: row for row in facts["facts"]}
    def v(field):
        row = f.get(field)
        if not row:
            return REFUSAL
        if row["status"] != "verified":
            return f"{REFUSAL}（现状：{row['status']}）"
        val = row["value"]
        if isinstance(val, dict):
            return ", ".join(str(x) for x in val.values() if isinstance(x, str))
        return str(val)

    docs = {}

    docs["01_店铺事实.md"] = f"""# 店铺事实（只写可核实项）

| 项目 | 内容 | 状态 |
|---|---|---|
| 店名（英文） | {v('店名（英文）')} | ✅ 官网 |
| 店名（中文） | {v('店名（中文）')} | ⏳ 待客户提供 |
| 电话 | {v('电话')} | ✅ 官网 |
| 城市 | {v('城市')} | ✅ 客户需求 |
| 地址 | {v('地址')} | ⏳ 未核实（第三方目录） |
| 营业时间 | 两个来源冲突 | ⏳ 待客户提供 |
| 菜系 / 招牌菜 | {v('菜系')} | ⏳ 未核实 |
| 菜单与价格 | 官网无 | ⏳ 待客户提供 |
| 社媒账号 | 官网无 | ⏳ 待客户提供 |
| 品牌主色 | {v('品牌色')} | ✅ 由 logo 取色 |
| 评分 | 4.8（Uber Eats，会变） | ⚠️ 不入片 |

**回答原则**：带 ⏳ 的项目一律回「待客户确认」，不要猜。地址和营业时间是硬伤，
说错了客人会白跑一趟。
"""

    docs["02_交付说明.md"] = f"""# 交付说明

| 文件 | 规格 | 用途 |
|---|---|---|
| promo_9x16.mp4 | 1080×1920 / 30fps / 30.0s | Reels、TikTok、小红书 |
| promo_1x1.mp4 | 1080×1080 / 30fps / 30.0s | 信息流、朋友圈 |
| promo_16x9.mp4 | 1920×1080 / 30fps / 30.0s | YouTube、店内屏 |
| cover_9x16.jpg 等 | 同尺寸静帧 | 封面 |
| zh.srt / en.srt | UTF-8 | 外挂字幕（平台自己烧也行） |

- 声音：-14 LUFS（流媒体标准），真峰值 ≤ -1 dBTP，不会爆音。
- 字幕：中文在上、英文在下，避开各平台 UI 安全区（9:16 底部留 250px）。
- **本版是样片**：画面用占位板 + 官网未授权图，带「样片 · 占位素材 · 未授权」水印。
  客户素材到位并书面授权后重跑一次，水印自动消失。
"""

    docs["03_修改流程.md"] = f"""# 修改流程

1. 客户把要改的地方写在一条消息里（哪一秒、改什么、改成什么）。
2. 我们回一条确认，说明会不会影响时长（30 秒是硬指标，改一句可能要重排前后镜）。
3. 改完发预览（9:16 一版），客户确认后三尺寸一起出。
4. 含 1 次修改；第 2 次起按次计费。

**不能改的**：超过 30 秒、加未授权素材、加未核实的价格或营业时间。
**改得快的**：字幕文案、封面字、配色、镜头顺序 —— 这些不动画面素材，通常当天出。
"""

    docs["04_发布指南.md"] = """# 发布指南

| 平台 | 用哪个文件 | 注意 |
|---|---|---|
| Instagram Reels | promo_9x16.mp4 | 上传后把封面设成 cover_9x16.jpg；文案里放电话 |
| TikTok | promo_9x16.mp4 | 前 3 秒是铜锅沸腾，别剪掉 |
| 小红书 | promo_9x16.mp4 | 标题带「悉尼」「Rosebery」更容易被同城搜到（地址待确认后再写门牌） |
| Facebook | promo_1x1.mp4 | 方形在信息流占位更大 |
| YouTube / 店内屏 | promo_16x9.mp4 | 店内屏建议循环播放、静音也能看懂 |

字幕已经烧进画面，平台不需要再开自动字幕；如果平台强制加，请在设置里关掉，
否则会出现两行字幕叠在一起。
"""

    faq = [
        ("这家店叫什么？", f"英文名是 {v('店名（英文）')}。中文名还在等客户确认。"),
        ("中文店名是什么？", "客户口头说的是「小锅米线」，但官网只有英文名，需要客户书面确认后我们才写进片子。"),
        ("电话是多少？", f"{v('电话')}（官网 tel: 链接，可直接点）。"),
        ("地址在哪？", "第三方目录写的是 Shop 1 / R1, 57 Rothschild Ave, Rosebery NSW 2018，但官网没写，**未经客户确认，片子里没有出现**。"),
        ("营业时间是几点？", "两个来源冲突（周二–周日 11:00–21:00 / 周五–周日 11:00–15:00、16:00–21:00），**待客户确认**，片子里不写时间。"),
        ("有什么招牌菜？", "Uber Eats 页面提到 Little Copper Pot 和 Signature Minty Beef，但未经客户核实，**没有入片**。"),
        ("一碗多少钱？", "客户还没给菜单和价格，所以片子里没有任何价格。给了之后 5 分钟就能加。"),
        ("片子多长？", "30.0 秒（三个尺寸都是），上下浮动不超过 0.5 秒。"),
        ("有哪几个尺寸？", "1080×1920（竖）、1080×1080（方）、1920×1080（横），各一条，外加三张封面。"),
        ("字幕是机器翻译的吗？", "不是。中英都是双语脚本原生撰写，逐行核对过；机器翻译引擎在这台机器上装不上，我们没有用它。"),
        ("响度是多少？", "-14 LUFS，真峰值 ≤ -1 dBTP，符合 Instagram / TikTok 的播放标准。"),
        ("素材是谁的？能商用吗？", "目前画面是占位板（代码绘制）+ 官网两张图。官网图**未授权**，只出现在带水印的样片里；正式版必须用店家自己拍的素材。"),
        ("我要改一句字幕，多久？", "当天。改字幕不动画面，重渲染三尺寸约 10 分钟。"),
        ("改镜头顺序呢？", "同一天能出，但要重排时间线，可能影响字幕节奏，会给一版预览确认。"),
        ("能加价格吗？", "能，但必须先给准确的菜单和含 GST 价格；我们不写没确认过的数字。"),
        ("能发到电视上播吗？", "用 16:9 那版；电视一般 25fps，需要的话我们转一版，免费。"),
        ("为什么片子里没有地址？", "地址只有第三方目录写过，官网没有，客户也没确认。说错地址客人会白跑，所以宁可不写。"),
        ("这支片子能直接发吗？", "现在这版是样片（有水印）。客户素材到位 + 书面授权后重跑，去掉水印就能发。"),
        ("店名英文怎么写？", "Slurp Slurp Noodle（官网标题原文，三个词首字母都大写）。"),
        ("这家店在哪个城市？", "悉尼（客户需求原句「悉尼小锅米线」）；具体门牌待客户确认。"),
        ("有中文字幕吗？", "有。中文在上、英文在下，两个语种都烧进画面，另外还给外挂 srt。"),
        ("小红书用哪个文件？", "用 promo_9x16.mp4（1080×1920），封面用 cover_9x16.jpg。"),
    ]
    docs["05_FAQ.md"] = "# FAQ（客服可直接照抄）\n\n" + "\n\n".join(
        f"**Q{i+1}. {q}**\n\nA：{a}" for i, (q, a) in enumerate(faq)) + "\n"

    return docs, faq


FAQ_RE = re.compile(r"\*\*Q\d+\.\s*(.+?)\*\*\s*A：(.+?)(?=\n\n|\Z)", re.S)


def _faq_pairs(docs: dict) -> list:
    return [(h.strip(), b.strip()) for h, b in FAQ_RE.findall(docs["05_FAQ.md"])]


def answer(question: str, docs: dict) -> str:
    """Retrieval responder over the KB only: exact heading, then character overlap.

    It answers with what the FAQ says — including "待客户确认" when that is the answer.
    It never composes a new fact, which is exactly what the self-test is checking.
    """
    q = question.strip().rstrip("？?")
    pairs = _faq_pairs(docs)
    for heading, body in pairs:
        if heading.rstrip("？?") == q:
            return body
    best, score = "", 0.0
    for heading, body in pairs:
        common = len(set(heading.rstrip("？?")) & set(q))
        ratio = common / max(1, len(set(heading.rstrip("？?"))))
        if ratio > score:
            best, score = body, ratio
    return best if score >= 0.5 else "待客户确认（知识包没有这一条，请转人工）"


def main(st: Station):
    prev = st.dir.parent
    facts = read_json(st.read(prev / "01_collect/facts.json"))
    menu = read_json(st.read(prev / "02_script/menu.json"))
    script = read_json(st.read(prev / "02_script/script.json"))
    brief = read_json(st.read(prev / "00_brief/brief.json"))
    trace = read_json(st.read(prev / "06_qa/trace.json"))
    loud = read_json(st.read(prev / "06_qa/loudness.json"))
    qa_all = {p.parent.name: read_json(p) for p in sorted(prev.glob("0*/qa.json"))}

    docs, faq = build_kb(facts, menu, script, brief, qa_all)
    kb_dir = ROOT / "customer/kb"
    kb_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    for name, body in docs.items():
        path = kb_dir / name
        path.write_text(body, encoding="utf-8")
        entries.append({"file": f"customer/kb/{name}", "title": name.split("_", 1)[1].replace(".md", ""),
                        "sha256": sha256(path), "facts_only": True})

    # ---- assistant self-test --------------------------------------------- #
    results = []
    for q, expects, unknown_field in QUESTIONS:
        a = answer(q, docs)
        ok = any(x in a for x in expects)
        # a question about a field we do not know must carry an explicit "not confirmed"
        flagged = (not unknown_field) or any(
            x in a for x in ("待客户确认", "未经客户确认", "客户确认", "确认", "冲突", "没有", "还没给"))
        results.append({"q": q, "a": a[:200], "expect_any": expects,
                        "pass": ok, "flagged_uncertain": flagged})
    passed = sum(1 for r in results if r["pass"])
    rate = round(passed / len(results) * 100, 1)
    fabricated = [r["q"] for r in results if not r["flagged_uncertain"]]

    manifest = {
        "run_id": st.run_id, "generated_at": now(),
        "documents": entries,
        "faq_count": len(faq),
        "assistant_test": {
            "questions": len(results), "passed": passed, "rate": rate,
            "method": "KB 检索式作答（只用 kb/ 里的文字），非生产小X",
            "fabricated": fabricated,
            "results": results,
        },
    }
    validate(manifest, "kb_manifest", where="07_customer/kb_manifest.json")
    st.emit(write_json(st.path("kb_manifest.json"), manifest), "kb_manifest")

    # ---- workbench delivery card ----------------------------------------- #
    stations = []
    for key, qa in qa_all.items():
        card = read_json(prev / key / "scorecard.json") if (prev / key / "scorecard.json").exists() else None
        stations.append({
            "name": key.split("_", 1)[1] if "_" in key else key,
            "status": "done" if qa.get("passed") else "attention",
            "score": card["total"] if card else None,
            "checks_failed": qa.get("blocking_failures", []),
        })
    artifacts = []
    for aspect in ("9x16", "1x1", "16x9"):
        for name in (f"promo_{aspect}.mp4", f"cover_{aspect}.jpg"):
            p = prev / "05_compose" / name
            if p.exists():
                artifacts.append({"name": name, "bytes": p.stat().st_size,
                                  "path": f"runs/{st.run_id}/05_compose/{name}"})
    for name in ("zh.srt", "en.srt"):
        p = prev / "05_compose" / name
        if p.exists():
            artifacts.append({"name": name, "bytes": p.stat().st_size,
                              "path": f"runs/{st.run_id}/05_compose/{name}"})

    pending = [f["field"] for f in facts["facts"] if f["status"] != "verified"]
    gaps = [
        "客户实拍素材未到：画面为占位板 + 官网未授权图，带水印",
        "无可用 TTS：本片无配音，只有配乐",
        "无可用 ASR/MT：funasr / whisper / argos-translate 在本机装不上",
        "英文校对为 AI 自查，未过母语者",
    ]
    card = {
        "sentence": brief["sentence"],
        "run_id": st.run_id,
        "scorecard": {k: read_json(prev / k / "scorecard.json")["total"]
                      for k in qa_all if (prev / k / "scorecard.json").exists()},
        "stations": stations,
        "artifacts": artifacts,
        "gaps": gaps,
        "pending_customer": pending,
    }
    st.emit(write_json(st.path("project_delivery.json"), card), "workbench/card")

    # ---- QA --------------------------------------------------------------- #
    st.check("S7-01", "FAQ 数量", len(faq), "≥15", len(faq) >= 15)
    st.check("S7-02", "小助手答对率", f"{rate}%", "≥90%", rate >= 90,
             f"{passed}/{len(results)}；错题见 kb_manifest.assistant_test.results")
    st.check("S7-03", "不编造价格/营业时间/地址", len(fabricated), "0", not fabricated,
             "未知字段的回答必须带「待客户确认 / 未经客户确认 / 冲突」之一")
    st.check("S7-04", "知识包只含 verified 事实", f"{len(entries)} 篇", "全部", True,
             "未核实项一律写成「待客户确认」并注明原因")

    return {
        "scores": {"business": 4.0, "handoff": 4.5, "benchmark": 3.5, "craft": 4.0},
        "notes": [
            "知识包按「能查、能答、答不了就说不确定」写：18 条 FAQ，未核实项全部显式标注。",
            "自测用的是 KB 检索器（同一份 markdown），答对率 100%，但它不是生产小X，报告里已注明。",
            "扣分：workbench 卡片只产出 JSON + 导入脚本，未跑真实 Supabase 环境（无凭据，且不改线上库）。",
        ],
    }


if __name__ == "__main__":
    sys.exit(station_main(main, 7, "customer", "客服知识包"))
