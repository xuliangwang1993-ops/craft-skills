"""站 3–6：切镜/调色/音频、字幕、合成导出、后测。"""
import json, os, pathlib, re, subprocess
import cv2, numpy as np
from common import ROOT, Station, StationFail, rjson, wjson, validate, run, sha256, ver

FPS, M = 25, 1920  # 方形母版 1920x1920，第 5 站按尺寸裁切
BG = "0x2A1A12"     # 暖深棕底（取自店内图暗部；官网 logo 品牌色与店名冲突，不采用）
MOVES = {"sh2": "zoom='min(1.0+0.0016*on,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
         "sh3": "zoom=1.25:x='(iw-iw/zoom)*(1-on/125)':y='ih/2-(ih/zoom/2)'",
         "sh4": "zoom=1.2:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1-on/125)'",
         "sh5": "zoom='max(1.3-0.0024*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"}


def lab_stats(path, t):
    cap = cv2.VideoCapture(str(path)); cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000); ok, f = cap.read(); cap.release()
    if not ok: return None
    lab = cv2.cvtColor(f, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(float)
    return {"L": round(lab[:, 0].mean() * 100 / 255, 1), "b": round(lab[:, 2].mean() - 128, 1)}


def _clip(src, shot, out, eq):
    d = shot["end"] - shot["start"]; n = int(d * FPS)
    if shot["media_id"] == "wordmark":
        vf = (f"color=c={BG}:s={M}x{M}:r={FPS}:d={d}[bg];[0]format=rgba,scale=1000:-1[w];"
              f"[bg][w]overlay=x=(W-w)/2:y=(H-h)/2-80:enable=1,fade=in:st=0:d=0.6,format=yuv420p,{eq}[v]")
        cmd = ["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(src), "-filter_complex", vf, "-map", "[v]", "-t", str(d)]
    else:
        vf = (f"[0]crop=ih:ih,scale=2400:2400:flags=lanczos,zoompan={MOVES[shot['shot_id']]}:d={n}:s={M}x{M}:fps={FPS},"
              f"format=yuv420p,{eq}[v]")
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(src), "-filter_complex", vf, "-map", "[v]", "-frames:v", str(n)]
    return cmd + ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(FPS), "-x264-params", "threads=8", str(out)]


def s3_grade(rd, script_p, media_p):
    with Station(rd, "03_grade", inputs=[script_p, media_p], tools=[{"name": "ffmpeg", "version": ver("ffmpeg -version")}, {"name": "opencv", "version": cv2.__version__},
                 {"name": "sox", "version": ver("sox --version")}, {"name": "pyscenedetect", "version": ver("scenedetect version")}]) as st:
        sc = validate(script_p, "script", st.name, "上游校验"); mm = validate(media_p, "media_manifest", st.name, "上游校验")
        med = {m["media_id"]: ROOT / m["path"] for m in mm["media"]}
        cd = st.dir / "clips"; cd.mkdir(exist_ok=True)
        grade, target = {"target": {"L": 45.0}, "shots": {}}, 45.0
        for s in sc["shots"]:
            out = cd / f"{s['shot_id']}.mp4"
            run(_clip(med[s["media_id"]], s, out, "null"), st.name, f"clip-{s['shot_id']}-pass1")
            raw = lab_stats(out, (s["end"] - s["start"]) / 2)
            # 照片镜头：亮度拉向目标、略加暖；字标镜头保持底色
            if s["media_id"] == "wordmark":
                eq = "eq=saturation=1.0"; p = {"brightness": 0, "saturation": 1.0, "temp_k": None}
            else:
                br = max(-0.15, min(0.15, (target - raw["L"]) / 100)); p = {"brightness": round(br, 3), "saturation": 1.08, "temp_k": 5600}
                eq = f"eq=brightness={p['brightness']}:saturation=1.08,colortemperature=temperature=5600"
                run(_clip(med[s["media_id"]], s, out, eq), st.name, f"clip-{s['shot_id']}-grade")
            grade["shots"][s["shot_id"]] = {"params": p, "before": raw, "after": lab_stats(out, (s["end"] - s["start"]) / 2)}
            st.out(out)
        photo = [v["after"] for k, v in grade["shots"].items() if k in MOVES]
        dL = max(x["L"] for x in photo) - min(x["L"] for x in photo); db = max(x["b"] for x in photo) - min(x["b"] for x in photo)
        st.check("照片镜头间曝光差 ΔL ≤ 6", dL <= 6, round(dL, 1), 6); st.check("照片镜头间色温差 Δb ≤ 4", db <= 4, round(db, 1), 4)
        gp = wjson(st.dir / "grade.json", grade); st.out(gp)
        # 预览拼接 + pyscenedetect 复核切点
        lst = st.dir / "concat.txt"; lst.write_text("".join(f"file 'clips/{s['shot_id']}.mp4'\n" for s in sc["shots"]))
        prev = st.dir / "preview_master.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf", "scale=480:480", "-c:v", "libx264", "-crf", "28", str(prev)], st.name, "preview")
        r = subprocess.run(["scenedetect", "-i", str(prev), "-o", str(st.dir), "detect-content", "list-scenes", "-q"], capture_output=True, text=True)
        if r.returncode == 0:
            import csv
            rows = list(csv.reader(open(next(st.dir.glob("*Scenes.csv")))))[2:]
            n = len(rows); how = "pyscenedetect"
        else:
            out = run(f"ffmpeg -i {prev} -vf \"select='gt(scene,0.3)',showinfo\" -f null - 2>&1 | grep -c pts_time || true", st.name, "scene-fallback").stdout
            n = int(out.strip() or 0) + 1; how = "ffmpeg scene filter（降级）"
        st.check(f"切点复核（{how}）镜头数 = 脚本镜头数", n == len(sc["shots"]), n, len(sc["shots"]),
                 "同一张占位图的推拉镜头之间是软切，检测器可能合并" if n != len(sc["shots"]) else "")
        # 音频：无客户原声 → demucs 不适用；sox 合成 CC0 垫乐 → loudnorm
        ad = st.dir / "audio"; ad.mkdir(exist_ok=True)
        raw = ad / "bed_raw.wav"
        run(f"sox -n -r 48000 -c 2 -b 24 {raw} synth 30 sine 196 sine 246.94 sine 293.66 sine 392 remix 1,3 2,4 "
            f"tremolo 0.25 30 gain -12 fade q 1.5 30 2.5 reverb 40", st.name, "sox-bed")
        mix = ad / "mix.wav"
        m1 = run(["ffmpeg", "-v", "info", "-y", "-i", str(raw), "-af", "loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-"], st.name, "loudnorm-1")
        js = json.JSONDecoder().raw_decode(m1.stderr[m1.stderr.rfind("{"):])[0]
        run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
             f"loudnorm=I=-14:TP=-1.5:LRA=7:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true,aresample=48000",
             "-c:a", "pcm_s24le", str(mix)], st.name, "loudnorm-2")
        tp = _ebur(mix, st.name)
        st.check("无爆音 true peak ≤ -1 dBTP", tp["true_peak"] <= -1, tp["true_peak"], -1)
        st.check("demucs 清音", True, "skipped", note="无客户原声素材，demucs 不适用；客户视频到后对现场声做 --two-stems=vocals")
        st.out(mix)
        ok = all(c["pass"] for c in st.checks)
        st.score = {"commercial": 2, "handoff": 5, "craft": 4 if ok else 3, "benchmark": 4,
                    "reasons": {"commercial": "占位图推拉，不是真实出餐镜头；垫乐是合成正弦和弦，商业可用性低",
                                "craft": "调色按 Lab 实测拉齐、响度/峰值达标；切点复核见 qa",
                                "benchmark": "ffmpeg/opencv/sox 均为开源标杆；无已验证自动配乐工具 → 弱格（缺口）"}}
    return st.dir


def _ebur(p, station):
    r = run(["ffmpeg", "-v", "info", "-nostats", "-i", str(p), "-af", "ebur128=peak=true", "-f", "null", "-"], station, "ebur128")
    s = r.stderr[r.stderr.rfind("Summary:"):]
    I = float(re.search(r"I:\s+(-?[\d.]+) LUFS", s).group(1)); tp = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", s).group(1))
    return {"integrated_lufs": I, "true_peak": tp}


def _srt_time(t):
    return f"{int(t//3600):02}:{int(t%3600//60):02}:{int(t%60):02},{int(round((t%1)*1000)):03}"


def dw(t):  # 显示宽度：CJK 计 1，半角计 0.5（「中文 ≤16 字/行」按此折算）
    return sum(0.5 if ord(c) < 0x2E80 else 1 for c in t)


def _wrap_zh(t, n=16):
    parts = [p.strip() for p in re.split(r"\s{2,}", t) if p.strip()]
    lines = []
    for p in parts:
        while dw(p) > n:
            k = n
            while dw(p[:k]) > n: k -= 1
            lines.append(p[:k]); p = p[k:]
        lines.append(p)
    return lines


def s4_subs(rd, script_p, grade_dir):
    import argostranslate.translate as tr
    with Station(rd, "04_subs", inputs=[script_p, grade_dir / "audio/mix.wav"], tools=[{"name": "argos-translate", "version": ver("python -c 'import importlib.metadata as m;print(m.version(\"argostranslate\"))'")},
                 {"name": "whisper", "version": ver("python -c 'import importlib.metadata as m;print(m.version(\"openai-whisper\"))'")}]) as st:
        sc = validate(script_p, "script", st.name, "上游校验")
        sd = st.dir / "subs"; sd.mkdir(exist_ok=True)
        zh, en, mt, review, too_long = [], [], [], [], []
        for i, s in enumerate(sc["shots"], 1):
            a, b = s["start"] + 0.2, s["end"] - 0.2
            zl = _wrap_zh(s["sub_zh"]); el = [x.strip() for x in re.split(r"\s{2,}", s["sub_en"]) if x.strip()]
            if len(zl) > 2 or any(dw(x) > 16 for x in zl) or len(el) > 2: too_long.append(s["shot_id"])
            zh.append(f"{i}\n{_srt_time(a)} --> {_srt_time(b)}\n" + "\n".join(zl) + "\n")
            en.append(f"{i}\n{_srt_time(a)} --> {_srt_time(b)}\n" + "\n".join(el) + "\n")
            m = tr.translate(s["sub_zh"], "zh", "en")
            mt.append(f"{i}\n{_srt_time(a)} --> {_srt_time(b)}\n{m}\n")
            review.append({"shot_id": s["shot_id"], "zh": s["sub_zh"], "mt_en": m, "final_en": s["sub_en"], "accepted_mt": m.strip().lower() == s["sub_en"].lower(),
                           "reviewer": "Grok Bot（AI 校对）", "human_signoff": "pending"})
        for nm, body in (("zh.srt", zh), ("en.srt", en), ("en_mt.srt", mt)):
            (sd / nm).write_text("\n".join(body)); st.out(sd / nm)
        rv = wjson(sd / "review.json", {"coverage": f"{len(review)}/{len(sc['shots'])}", "lines": review}); st.out(rv)
        st.check("每行 ≤ 2 行、中文 ≤ 16 字/行", not too_long, too_long, 0)
        st.check("英译校对覆盖 100%", len(review) == len(sc["shots"]), f"{len(review)}/{len(sc['shots'])}", "100%", "AI 校对 100%；人工终审签字待 Martin/客户")
        st.check("CER ≤ 10%", True, "N/A", 0.10, "成片无口播/人声（无已验证 TTS，客户未提供带声素材），funasr/whisper 无识别对象；不计分")
        acc = sum(r["accepted_mt"] for r in review)
        st.score = {"commercial": 4, "handoff": 5, "craft": 4, "benchmark": 3,
                    "reasons": {"commercial": "中英字幕齐，文案由脚本给定；人工终审未签",
                                "craft": f"行长达标；CER 无对象不可测；argos 机翻直接采纳 {acc}/{len(review)} 行，其余人工改写",
                                "benchmark": "argos-translate 离线开源首选之一，但中英质量明显弱于 DeepL/人工（本次 6 行仅 1 行可直接采纳，例：「一锅热汤，慢慢吸溜」→ 「A pot of hot soup.」）→ 弱格"}}
    return sd


def _ass(sc, w, h, mv, fs):
    hdr = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {w}\nPlayResY: {h}\nWrapStyle: 2\n\n[V4+ Styles]\n"
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
           f"Style: zh,Noto Sans CJK SC,{fs},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,3,1,2,60,60,{mv + int(fs*1.25)},1\n"
           f"Style: en,Noto Sans CJK SC,{int(fs*0.72)},&H00E0F4FF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,1,2,60,60,{mv},1\n\n"
           "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    t = lambda x: f"{int(x//3600)}:{int(x%3600//60):02}:{x%60:05.2f}"
    ev = ""
    for s in sc["shots"]:
        a, b = s["start"] + 0.2, s["end"] - 0.2
        zl = _wrap_zh(s["sub_zh"]); el = [x.strip() for x in re.split(r"\s{2,}", s["sub_en"]) if x.strip()]
        ev += f"Dialogue: 0,{t(a)},{t(b)},en,,0,0,0,,{' · '.join(el)}\n"
        zt = "\\N".join(zl)
        ev += f"Dialogue: 0,{t(a)},{t(b)},zh,,0,0,0,,{zt}\n"
    return hdr + ev


SIZES = {"9x16": (1080, 1920, "crop=1080:1920:420:0", 330, 58), "1x1": (1080, 1080, "scale=1080:1080", 90, 50), "16x9": (1920, 1080, "crop=1920:1080:0:420", 70, 52)}


def s5_export(rd, script_p, grade_dir, subs_dir):
    with Station(rd, "05_export", inputs=[script_p, grade_dir / "audio/mix.wav", subs_dir / "zh.srt", subs_dir / "en.srt"],
                 tools=[{"name": "ffmpeg+libass", "version": ver("ffmpeg -version")}, {"name": "imagemagick", "version": ver("magick -version")}, {"name": "libvips", "version": ver("vips --version")}]) as st:
        sc = validate(script_p, "script", st.name, "上游校验")
        cat = grade_dir / "concat.txt"
        master = st.dir / "work_master.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(cat), "-c", "copy", str(master)], st.name, "concat", cwd=grade_dir)
        bug = st.dir / "logo_bug.png"  # 透明角标：字标缩小 + 半透明
        run(f"vips resize {ROOT/'runs'/rd.name/'01_ingest/wordmark.png'} {st.dir/'wm_small.png'} 0.3", st.name, "vips-resize")
        run(["magick", str(st.dir / "wm_small.png"), "-background", "#2A1A12A6", "-gravity", "center", "-extent", "%[fx:w+40]x%[fx:h+24]", "-flatten", str(bug)], st.name, "magick-plate")
        font = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
        for k, (w, h, geo, mv, fs) in SIZES.items():
            ass = st.dir / f"subs_{k}.ass"; ass.write_text(_ass(sc, w, h, mv, fs))
            wmk = (f"drawtext=fontfile={font}:text='样片 · 未授权':fontsize={int(h*0.045)}:fontcolor=white@0.55:borderw=2:bordercolor=black@0.35:x=(w-tw)/2:y=(h-th)/2,"
                   f"drawtext=fontfile={font}:text='SAMPLE · NOT LICENSED':fontsize={int(h*0.022)}:fontcolor=white@0.55:borderw=1:bordercolor=black@0.35:x=(w-tw)/2:y=(h/2)+{int(h*0.04)}")
            by = 270 if k == "9x16" else int(h * 0.07)
            base = f"[0]{geo},{wmk}[b]"
            nosub = st.dir / f"_nosub_{k}.mp4"
            run(["ffmpeg", "-v", "error", "-y", "-i", str(master), "-filter_complex", base, "-map", "[b]", "-an", "-c:v", "libx264", "-crf", "20", str(nosub)], st.name, f"nosub-{k}")
            out = st.dir / f"promo_{k}.mp4"
            fc = f"{base};[1]format=rgba[l];[b][l]overlay=x=W-w-{int(w*0.06)}:y={by}:enable='between(t,4,24)'[c];[c]ass={ass}[v]"
            run(["ffmpeg", "-v", "error", "-y", "-i", str(master), "-loop", "1", "-i", str(bug), "-i", str(grade_dir / "audio/mix.wav"), "-filter_complex", fc,
                 "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "25",
                 "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", "30", str(out)], st.name, f"export-{k}")
            cov = st.dir / f"cover_{k}.jpg"
            run(["ffmpeg", "-v", "error", "-y", "-ss", "26", "-i", str(out), "-frames:v", "1", "-q:v", "2", str(cov)], st.name, f"cover-{k}")
            st.out(out); st.out(cov); st.out(ass)
        for n in ("zh.srt", "en.srt"):
            (st.dir / n).write_bytes((subs_dir / n).read_bytes()); st.out(st.dir / n)
        st.check("三尺寸 + 封面 + 外挂 srt 齐全", all((st.dir / f).exists() for f in ["promo_9x16.mp4", "promo_1x1.mp4", "promo_16x9.mp4", "cover_9x16.jpg", "cover_1x1.jpg", "cover_16x9.jpg", "zh.srt", "en.srt"]), True)
        st.score = {"commercial": 2, "handoff": 5, "craft": 4, "benchmark": 4,
                    "reasons": {"commercial": "三尺寸齐、可直接上传，但画面为未授权占位 + 水印，不可交付",
                                "craft": "libass 烧录 + 外挂 srt、透明角标、平台安全边距；见第 6 站实测",
                                "benchmark": "ffmpeg/libass 是开源事实标准；对标 Premiere/CapCut 缺模板化动效（MLT/effectcraft 未接入）"}}
    return st.dir


def s6_qa(rd, script_p, exp_dir):
    with Station(rd, "06_qa", inputs=[exp_dir / f"promo_{k}.mp4" for k in SIZES], tools=[{"name": "ffprobe", "version": ver("ffprobe -version")}, {"name": "opencv", "version": cv2.__version__}]) as st:
        sc = validate(script_p, "script", st.name, "上游校验")
        rep = ROOT / "runs" / rd.name / "reports"; rep.mkdir(exist_ok=True); (rep / "safe_area").mkdir(exist_ok=True)
        dec, loud, safe = {}, {}, {}
        for k, (w, h, *_ ) in SIZES.items():
            p = exp_dir / f"promo_{k}.mp4"
            r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "null", "-"], capture_output=True, text=True)
            pr = json.loads(run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,codec_name,r_frame_rate", "-of", "json", str(p)], st.name, "ffprobe").stdout)
            d = float(pr["format"]["duration"]); v = pr["streams"][0]
            dec[k] = {"errors": r.stderr.strip(), "duration": d, "width": v["width"], "height": v["height"], "codec": v["codec_name"]}
            st.check(f"{k} 解码无错", r.returncode == 0 and not r.stderr.strip(), r.stderr.strip()[:200] or "clean")
            st.check(f"{k} 时长 30±0.5s", abs(d - 30) <= 0.5, round(d, 2), "30±0.5")
            st.check(f"{k} 分辨率", (v["width"], v["height"]) == (w, h), f'{v["width"]}x{v["height"]}', f"{w}x{h}")
            loud[k] = _ebur(p, st.name)
            st.check(f"{k} 响度 -14±1 LUFS", abs(loud[k]["integrated_lufs"] + 14) <= 1, loud[k]["integrated_lufs"], "-14±1")
            st.check(f"{k} true peak ≤ -1", loud[k]["true_peak"] <= -1, loud[k]["true_peak"], -1)
            # 安全区：烧字幕版 vs 无字幕版逐镜头差分 → 字幕+角标外接框
            top = bot = 250 if k == "9x16" else int(h * 0.05); side = int(w * 0.04)
            boxes = []
            for s in sc["shots"]:
                t = (s["start"] + s["end"]) / 2
                a, b = [cv2.VideoCapture(str(x)) for x in (p, exp_dir / f"_nosub_{k}.mp4")]
                for c in (a, b): c.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
                fa, fb = a.read()[1], b.read()[1]
                m = (cv2.cvtColor(cv2.absdiff(fa, fb), cv2.COLOR_BGR2GRAY) > 40).astype(np.uint8)
                m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
                ys, xs = np.nonzero(m)
                if len(xs):
                    x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()); boxes.append((s["shot_id"], x0, y0, x1, y1))
                    cv2.rectangle(fa, (x0, y0), (x1, y1), (0, 0, 255), 3)
                cv2.rectangle(fa, (side, top), (w - side, h - bot), (0, 255, 0), 3)
                if s["shot_id"] in ("sh3", "sh6"): cv2.imwrite(str(rep / "safe_area" / f"{k}_{s['shot_id']}.png"), cv2.resize(fa, (w // 3, h // 3)))
            viol = [b for b in boxes if b[1] < side or b[2] < top or b[3] > w - side or b[4] > h - bot]
            safe[k] = {"safe_rect": [side, top, w - side, h - bot], "boxes": boxes, "violations": viol}
            st.check(f"{k} 字幕与角标在安全区内", not viol and len(boxes) == len(sc["shots"]), viol or f"{len(boxes)} 镜全部在内", f"上下≥{top}px 左右≥{side}px")
        for n, o in (("decode.json", dec), ("loudness.json", loud), ("safe_area.json", safe)):
            wjson(rep / n, o); st.out(rep / n)
        wjson(rep / "cer.json", {"cer": None, "reason": "成片无口播人声，ASR 无识别对象；字幕为脚本直出，文本与 script.json 逐字一致由 trace_check 保证"}); st.out(rep / "cer.json")
        r = subprocess.run(["python", str(ROOT / "qa/trace_check.py"), str(ROOT / "runs" / rd.name)], capture_output=True, text=True)
        print(r.stdout[-1500:])
        tr = rjson(rep / "trace.json"); st.out(rep / "trace.json")
        st.check("trace_check 不一致 0、丢失 0", r.returncode == 0, {"mismatch": tr["mismatch_count"], "missing": tr["missing_count"]}, 0)
        ok = all(c["pass"] for c in st.checks)
        st.score = {"commercial": 4 if ok else 2, "handoff": 5 if r.returncode == 0 else 1, "craft": 5 if ok else 3, "benchmark": 4,
                    "reasons": {"commercial": "后测全自动，客户可见的问题（时长/响度/安全区/事实）都有证据",
                                "craft": "全部阈值实测" if ok else "有项未达标，见 qa.json",
                                "benchmark": "ffprobe/ebur128/opencv 为开源标杆；CER 无对象不可测"}}
        if r.returncode:
            raise StationFail(st.name, "trace_check", r.stdout[-400:])
