"""站 7：客服知识包 + 15 问自测。"""
import json, re
from common import ROOT, Station, StationFail, rjson, wjson, validate

ASK = "请向店家确认"


def faq(F, name, phone):
    v = lambda k: F[k]["status"] == "verified"
    return [
        ("店名叫什么？", f"{name}。中文店名{ASK}（客户口头说法为「小锅米线」，未书面确认）。"),
        ("电话是多少？", f"{phone}（来源：官网 tel 链接）。"),
        ("地址在哪里？", f"地址{ASK}（第三方目录有记录，但官网未写，未核实）。"),
        ("营业时间是几点到几点？", f"营业时间{ASK}：两个第三方来源相互冲突，我们不提供具体时间。"),
        ("周一开门吗？", f"是否周一营业{ASK}，可致电 {phone}。"),
        ("一碗米线多少钱？", f"价格{ASK}：店家尚未提供菜单与价格。"),
        ("有什么招牌菜？", f"招牌菜{ASK}（第三方平台有提及，未核实，不对外宣称）。"),
        ("是哪里的菜系？", f"菜系{ASK}（第三方资料称云南米线，未核实）。"),
        ("可以外卖吗？", f"外卖渠道{ASK}。"),
        ("有社交媒体账号吗？", f"社媒账号{ASK}，官网未列出。"),
        ("评分怎么样？", f"第三方评分会变动，我们不引用；{ASK}。"),
        ("这支视频交付了什么？", "30 秒宣传短视频 9:16、1:1、16:9 三个尺寸，各带封面；中英文字幕（烧录版 + 外挂 srt）。"),
        ("现在的视频能直接发吗？", "不能。当前是样片：画面用官网占位图并带「样片 · 未授权」水印，需店家提供实拍素材并书面授权后出交付版。"),
        ("要店家拍什么素材？", "见拍摄清单 shot_request.md：铜锅沸腾、加料、挑面、店门、招牌菜特写，每段 5–10 秒，竖拍和横拍各一份。"),
        ("怎么修改视频？", "基础包含 1 次修改：把修改意见（第几秒、改什么）发给我们，2 个工作日内出修改版。"),
        ("字幕错了怎么办？", "字幕由脚本逐字生成并自动核对；发现错字告诉我们镜头编号，改脚本后全链重跑，不手工改片。"),
        ("视频里为什么没有营业时间和地址？", "规则是只放已核实的信息。营业时间来源冲突、地址未核实，店家确认后才能加。"),
        ("怎么发布到小红书/抖音/Reels？", "9:16 版用于 Reels/TikTok/小红书，1:1 用于 FB/IG 帖子，16:9 用于 YouTube；上传烧录版，或上传无字幕版+外挂 srt（平台支持时）。"),
        ("logo 为什么没用？", "官网的 logo 文件画面是「上座 SHANG ZUO」字样，与店名不符，已暂停使用，请店家提供正确 logo。"),
        ("视频的音乐有版权问题吗？", "没有。垫乐由流水线合成，CC0；字体为 Noto Sans CJK（SIL OFL）。"),
    ]


TESTS = [("你们电话多少", "phone"), ("请问地址是哪", "ask"), ("晚上几点关门", "ask"), ("米线什么价格", "ask"), ("店名是什么", "name"),
         ("周一营业吗", "ask"), ("招牌菜是什么", "ask"), ("能不能外卖", "ask"), ("视频交付哪些尺寸", "三个尺寸"), ("现在能直接发布吗", "不能"),
         ("要拍哪些素材", "shot_request"), ("想修改视频怎么办", "修改"), ("字幕有错字", "镜头编号"), ("音乐会侵权吗", "CC0"), ("为什么没放logo", "上座")]


def bigr(s):
    s = re.sub(r"[\s？?，。、/]", "", s.lower()); return {s[i:i + 2] for i in range(len(s) - 1)} | set(s)


def answer(kb, q):
    return max(kb, key=lambda qa: len(bigr(q) & bigr(qa[0])) * 2 + len(bigr(q) & bigr(qa[1])) * 0.2)


def s7_kb(rd, facts_p, menu_p, qa_dir):
    with Station(rd, "07_kb", inputs=[facts_p, menu_p, qa_dir / "qa.json"], tools=[{"name": "python", "version": "3 stdlib（检索式问答桩）"}]) as st:
        facts = validate(facts_p, "facts", st.name, "上游校验"); validate(menu_p, "menu", st.name, "上游校验")
        F = {f["field"]: f for f in facts["facts"]}; name, phone = F["name_en"]["value"], F["phone"]["value"]
        up = rjson(qa_dir / "qa.json")
        kd = ROOT / "customer" / "kb"; kd.mkdir(parents=True, exist_ok=True)
        fm = lambda t, d: f"---\ntitle: {t}\ndescription: {d}\nsource: craft-skills/runs/{rd.name}\nscope: customer/slurp-slurp-noodle\n---\n\n"
        rows = "\n".join(f"| {f['field']} | {f['value'] if f['status']=='verified' else ASK} | {f['status']} | {f['source_id']} |" for f in facts["facts"])
        docs = {
            "店铺事实.md": fm("Slurp Slurp Noodle 店铺事实", "只列已核实事实，其余请向店家确认") + f"# 店铺事实\n\n| 字段 | 值 | 状态 | 来源 |\n|---|---|---|---|\n{rows}\n\n> 规则：状态非 verified 的一律回答「{ASK}」，不编造价格、营业时间、地址。\n",
            "交付说明.md": fm("宣传短视频交付说明", "交付物与验收") + "# 交付说明\n\n- promo_9x16.mp4（1080×1920）、promo_1x1.mp4（1080×1080）、promo_16x9.mp4（1920×1080），30 秒，-14 LUFS\n- cover_*.jpg 封面；zh.srt / en.srt 外挂字幕；烧录版已含中英字幕\n- 当前状态：**样片**（占位素材 + 水印），交付闸门 BLOCKED，待客户素材与授权\n",
            "修改流程.md": fm("修改流程", "如何提修改") + "# 修改流程\n\n1. 客户写明镜头编号/秒数 + 修改内容\n2. 改 script.json 或替换 customer_media，`make run` 全链重跑（不手工改成片）\n3. 第 6 站后测全过 → 发新版；基础包含 1 次修改\n",
            "发布指南.md": fm("发布指南", "各平台用哪个尺寸") + "# 发布指南\n\n| 平台 | 文件 | 说明 |\n|---|---|---|\n| Instagram Reels / TikTok / 小红书 | promo_9x16.mp4 | 字幕在上下 250px 安全区内 |\n| Facebook / IG 帖子 | promo_1x1.mp4 | |\n| YouTube | promo_16x9.mp4 | 可另传 en.srt / zh.srt |\n",
        }
        kb = faq(F, name, phone)
        docs["FAQ.md"] = fm("常见问题 FAQ", f"{len(kb)} 问") + "# FAQ\n\n" + "\n".join(f"### Q{i}. {q}\n{a}\n" for i, (q, a) in enumerate(kb, 1))
        for n, t in docs.items():
            (kd / n).write_text(t); st.out(kd / n)
        wjson(kd / "kb_manifest.json", {"run_id": rd.name, "files": sorted(docs), "verified_fields": [k for k, f in F.items() if f["status"] == "verified"], "faq_count": len(kb)})
        st.out(kd / "kb_manifest.json")
        res = []
        for q, exp in TESTS:
            qq, a = answer(kb, q)
            ok = {"phone": phone in a, "ask": ASK in a, "name": name in a}.get(exp, exp in a)
            fabricated = bool(re.search(r"\$\s?\d|\d{1,2}:\d{2}|Rothschild", re.sub(r"9:16|16:9|1:1", "", a)))
            res.append({"q": q, "matched": qq, "answer": a, "expect": exp, "correct": ok and not fabricated, "fabricated": fabricated})
        acc = sum(r["correct"] for r in res) / len(res)
        wjson(st.dir / "assistant_test.json", {"engine": "本地检索式问答桩（非线上小X，仅用 KB 内容作答）", "accuracy": acc, "results": res}); st.out(st.dir / "assistant_test.json")
        st.check("FAQ ≥ 15 问", len(kb) >= 15, len(kb), 15)
        st.check("15 问答对率 ≥ 90%", acc >= 0.9, round(acc, 3), 0.9)
        st.check("不编造价格/营业时间", not any(r["fabricated"] for r in res), sum(r["fabricated"] for r in res), 0)
        st.check("上游后测通过", up["pass"], up["pass"])
        st.score = {"commercial": 4, "handoff": 5, "craft": 5 if all(c["pass"] for c in st.checks) else 3, "benchmark": 2,
                    "reasons": {"commercial": "客户常问的价格/时间都能安全兜底，转人工话术一致",
                                "craft": f"FAQ {len(kb)} 问；自测答对率 {acc:.0%}",
                                "benchmark": "测试用的是本地检索桩，不是线上小X；未接入向量检索（qdrant 未落地）→ 弱格"}}
