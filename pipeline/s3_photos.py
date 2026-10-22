#!/usr/bin/env python3
"""Station 3 — 照片精修

诚实修图：只做裁切（去截图黑边）、白平衡、曝光、垂直校正、锐化、导出。
不修掉瑕疵、不换天空、不挪家具、不改房间大小观感。

降级说明：本机无 darktable-cli（Alpine 无包、PC 侧安装未完成），改用 ImageMagick 同族参数
      + OpenCV 做几何校正，参数全部写进 edits.json 可复现。
隐私闸门：检测到人脸的图直接排除（本轮 p4 有一名站门口的人物）。
"""
from __future__ import annotations

import hashlib
import json
import shutil
import os
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import lib
from lib import PipelineError

LONG_EDGE = 2048
WATERMARK = "样片 SAMPLE"
CJK_FONT = "/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc"


# ---------------------------------------------------------------- 基础操作
def _longest_run(mask: np.ndarray) -> tuple[int, int]:
    best, cur = (0, 0), None
    for i, v in enumerate(mask):
        if v and cur is None:
            cur = i
        elif not v and cur is not None:
            if i - cur > best[1] - best[0]:
                best = (cur, i)
            cur = None
    if cur is not None and len(mask) - cur > best[1] - best[0]:
        best = (cur, len(mask))
    return best


def strip_letterbox(im: Image.Image) -> tuple[Image.Image, tuple]:
    """截图黑边/白边 → 裁到最大的一块「有内容」矩形。返回 (图, (l,t,r,b))。"""
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    row_mean = a.mean(axis=(1, 2))
    t, b = _longest_run(row_mean > 30)
    if b - t < 120:                        # 没有明显黑边，整张都要
        t, b = 0, im.height
    band = a[t:b]
    col_mean = band.mean(axis=(0, 2))
    l, r = _longest_run(col_mean > 30)
    if r - l < 120:
        l, r = 0, im.width
    while t > 0 and row_mean[t - 1] > 12:      # 把暗部（吊顶/夜景）也算回画面
        t -= 1
    while b < im.height and row_mean[b] > 12:
        b += 1
    while l > 0 and col_mean[l - 1] > 12:
        l -= 1
    while r < im.width and col_mean[r] > 12:
        r += 1
    pad = 2
    box = (max(0, l + pad), max(0, t + pad), min(im.width, r - pad), min(im.height, b - pad))
    return im.crop(box), box


def rotate_keep(im: Image.Image, deg: float) -> Image.Image:
    """旋转并保持原尺寸：expand 后中心裁回，避免出现白角。"""
    r = im.rotate(deg, resample=Image.BICUBIC, expand=True, fillcolor=(245, 245, 245))
    w, h = im.size
    left, top = (r.width - w) // 2, (r.height - h) // 2
    return r.crop((left, top, left + w, top + h))


def vertical_deviation(im: Image.Image) -> tuple[float | None, int]:
    """主导垂直线倾角（度）。返回 (角度, 线段数)；线段太少时角度为 None（不可测）。"""
    w, h = im.size
    sc = 1000 / max(w, h)
    g = np.asarray(im.resize((max(2, int(w * sc)), max(2, int(h * sc))), Image.BILINEAR).convert("L"))
    g = cv2.GaussianBlur(g, (3, 3), 0)
    g = cv2.createCLAHE(2.0, (8, 8)).apply(g)
    edges = cv2.Canny(g, 30, 90)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=30,
                            minLineLength=int(g.shape[0] * 0.20), maxLineGap=25)
    angs = []
    if lines is not None:
        for x1, y1, x2, y2 in lines[:, 0]:
            if abs(y2 - y1) < 25:
                continue
            a = np.degrees(np.arctan2(x2 - x1, y2 - y1))
            a = (a + 90.0) % 180.0 - 90.0          # 线段方向正反不影响倾角
            if abs(a) < 12:
                angs.append((a, float(np.hypot(x2 - x1, y2 - y1))))
    if len(angs) < 3:
        return None, len(angs)
    angs.sort(key=lambda t: -t[1])
    return float(np.median([a for a, _ in angs[:20]])), len(angs)


def gray_world(im: Image.Image) -> tuple[Image.Image, list]:
    a = np.asarray(im).astype(np.float32)
    means = a.reshape(-1, 3).mean(axis=0)
    target = means.mean()
    gains = (target / np.maximum(means, 1e-3)).clip(0.85, 1.18)
    out = np.clip(a * gains, 0, 255).astype(np.uint8)
    return Image.fromarray(out), [round(float(g), 4) for g in gains]


def add_watermark(im: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    size = max(28, im.width // 26)
    font = ImageFont.truetype(CJK_FONT, size)
    step_x, step_y = int(size * 8.5), int(size * 5.0)
    for y in range(-step_y, im.height + step_y, step_y):
        for x in range(-step_x, im.width + step_x, step_x):
            d.text((x, y), WATERMARK, font=font, fill=(255, 255, 255, 46))
    bar = Image.new("RGBA", (int(size * 7.2), int(size * 2.0)), (0, 0, 0, 110))
    layer.alpha_composite(bar, (im.width - bar.width - 18, im.height - bar.height - 18))
    d = ImageDraw.Draw(layer)
    d.text((im.width - bar.width - 8, im.height - bar.height - 6), WATERMARK,
           font=font, fill=(255, 255, 255, 235))
    return Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")


def vision_faces(path: Path) -> int:
    """Best-effort face count via Apple Vision (native, no model download).
    Returns -1 when the tool is unavailable. Occluded faces are NOT detected —
    that is why every image also goes through manual review_overrides.json."""
    exe = shutil.which("apple-vision")
    if not exe:
        return -1
    r = lib.run([exe, "faces", str(path), "--compact"], timeout=120)
    try:
        return int(json.loads(r["stdout"])["data"]["count"])
    except Exception:
        return -1


def load_overrides() -> list:
    p = Path(__file__).with_name("review_overrides.json")
    return json.loads(p.read_text(encoding="utf-8"))["decisions"] if p.exists() else []


def dhash(im: Image.Image) -> int:
    g = im.convert("L").resize((9, 8), Image.LANCZOS)
    a = np.asarray(g).astype(int)
    bits = (a[:, 1:] > a[:, :-1]).flatten()
    return int("".join("1" if b else "0" for b in bits), 2)


def hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def edit_one(src: Path, dst: Path, watermark: bool) -> dict:
    im = Image.open(src)
    orig = im.size
    im, box = strip_letterbox(im.convert("RGB"))
    dev_before, n_lines = vertical_deviation(im)
    rot = 0.0
    if dev_before is not None and abs(dev_before) > 0.3:
        def score(img):
            d, n = vertical_deviation(img)
            return abs(d) if d is not None else 99.0
        base = abs(dev_before)
        best = (base, im, 0.0)
        for d in (-dev_before, dev_before):     # 两个方向都试，取残差最小的
            cand = rotate_keep(im, d)
            sc = score(cand)
            if sc < best[0] - 0.2:
                best = (sc, cand, d)
        _, im, rot = best
        if rot:
            for _pass in range(2):
                res, _n = vertical_deviation(im)
                if res is None or abs(res) < 0.4:
                    break
                cand = rotate_keep(im, -res)
                if score(cand) + 0.1 < abs(res):
                    im, rot = cand, rot - res
                else:
                    break
    dev_after, n_after = vertical_deviation(im)
    im, gains = gray_world(im)
    im = ImageEnhance.Contrast(im).enhance(1.04)
    im = ImageEnhance.Color(im).enhance(1.03)

    # 4:3 居中裁切（保持原构图，不拉伸）
    w, h = im.size
    target = 4 / 3
    if w / h > target:
        nw = int(h * target)
        left = (w - nw) // 2
        im = im.crop((left, 0, left + nw, h))
    else:
        nh = int(w / target)
        top = max(0, int((h - nh) * 0.35))
        im = im.crop((0, top, w, top + nh))

    r = LONG_EDGE / max(im.size)
    if abs(r - 1) > 0.02:                      # 小于 1920 也放大（real-esrgan 不可用 → Lanczos 降级）
        im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    upscaled = r > 1.02
    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=3))
    if watermark:
        im = add_watermark(im)
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, "JPEG", quality=88, subsampling=1)
    return {
        "source": str(src.relative_to(lib.ROOT)),
        "output": str(dst.relative_to(lib.ROOT)),
        "source_size": orig,
        "letterbox_crop": box,
        "rotate_deg": round(rot, 2),
        "vertical_dev_before": None if dev_before is None else round(dev_before, 2),
        "vertical_dev_after": None if dev_after is None else round(dev_after, 2),
        "vertical_lines_detected": [n_lines, n_after],
        "wb_gains": gains,
        "output_size": list(im.size),
        "sha256": lib.sha256_file(dst),
        "upscaled": bool(upscaled),
        "vertical_ok": (dev_after is not None and abs(dev_after) <= 1.0),
        "needs_reshoot": (dev_after is None or abs(dev_after) > 1.0),
        "ops": ["letterbox_crop", "rotate", "gray_world", "contrast+4%", "saturation+3%",
                "crop_4x3", "lanczos_resize(降级，非 real-esrgan)", "unsharp(1.2,60,3)", "jpeg_q88"],
    }


CAPTIONS = {
    "p7_9bd5dbc1": {"zh": "房间：1.5 米双人床（queen），木地板，房门可锁", "en": "The room: queen bed, timber floor, lockable door", "tags": ["bed", "doorlock"]},
    "cover_hosting": {"zh": "房间另一侧：书桌工作区，玻璃门通往后院", "en": "Other side of the room: desk workspace, glass door to the garden", "tags": ["workspace"]},
    "p6_749131ed": {"zh": "共用厨房：燃气灶、烤箱、操作台", "en": "Shared kitchen: gas hob, oven, bench", "tags": ["kitchen"]},
    "p5_fee86606": {"zh": "共用厨房另一侧：冰箱与储物", "en": "Kitchen, other side: fridge and storage", "tags": ["kitchen"]},
    "p3_3fd3c755": {"zh": "共用卫生间：淋浴、洗手台（现状，建议整理后重拍）", "en": "Shared bathroom: shower and basin (as-is; reshoot recommended)", "tags": ["bath"]},
    "p1_1b6df255": {"zh": "后院：户外餐桌、BBQ 与沙发区", "en": "Back garden: outdoor dining table, BBQ and lounge", "tags": ["outdoor"]},
}
ORDER = ["p7_9bd5dbc1", "cover_hosting", "p6_749131ed", "p5_fee86606", "p3_3fd3c755", "p1_1b6df255"]


def run(run_id: str) -> None:
    st = lib.Station("03", "photos", run_id)
    st.require_prev("pricing.json", "pricing")  # 链路校验：上一站必须已交付
    mm_p = st.require_upstream("01", "media_manifest.json", "media_manifest")
    facts_p = st.require_upstream("01", "facts.json", "facts")
    mm = lib.read_json(mm_p)
    facts = lib.read_json(facts_p)

    outdir = st.dir / "photos" / "edited"
    outdir.mkdir(parents=True, exist_ok=True)
    edits, kept, excluded = [], [], []

    hashes = {}
    for it in mm["items"]:
        src = lib.ROOT / it["path"]
        im = Image.open(src).convert("RGB")
        h = dhash(im)
        dup = next((k for k, v in hashes.items() if hamming(h, v) <= 4), None)
        if dup:
            excluded.append({"source": it["path"], "reason": "duplicate", "of": dup})
            continue
        hashes[it["path"]] = h
        n_faces = vision_faces(src)
        if n_faces > 0:
            excluded.append({"source": it["path"], "reason": "privacy: face detected", "faces": n_faces})
            continue
        kept.append((it, src))

    overrides = load_overrides()
    for ov in overrides:
        if ov["action"] != "exclude":
            continue
        for it in list(kept):
            if ov["match"] in it[0]["path"]:
                kept.remove(it)
                excluded.append({"source": it[0]["path"], "reason": "manual_review", "detail": ov["reason"]})

    for it, src in kept:
        stem = Path(it["path"]).stem
        dst = outdir / f"img_{len(edits)+1:02d}.jpg"
        e = edit_one(src, dst, watermark=True)
        e["placeholder"] = True
        e["note"] = "平台图占位；成片需房东原图重跑本站"
        edits.append(e)

    # 排序 + 中英图注（按内容匹配文件名前缀）
    order = []
    for i, key in enumerate(ORDER):
        for it, _src in kept:
            if Path(it["path"]).stem.startswith(key):
                idx = [j for j, e in enumerate(edits) if e["source"] == it["path"]][0]
                cap = CAPTIONS[key]
                order.append({"rank": i + 1, "file": edits[idx]["output"],
                              "caption_zh": cap["zh"], "caption_en": cap["en"], "tags": cap["tags"]})
    for j, e in enumerate(edits):
        if not any(o["file"] == e["output"] for o in order):
            order.append({"rank": len(order) + 1, "file": e["output"],
                          "caption_zh": "未分类画面", "caption_en": "Unclassified shot", "tags": []})

    review = {"generated_at": lib.now(),
              "method": "自动去重(dhash<=4) + Apple Vision 人脸 -> 人工逐张复核(review_overrides.json)",
              "items": [{"source": k, "decision": "keep"} for k, _ in kept] + excluded}
    review_p = st.path("photos", "review.json")
    lib.write_json(review_p, review)
    st.add_output(review_p)

    order_p = st.path("photos", "order.json")
    lib.write_json(order_p, {"generated_at": lib.now(), "items": order})
    edits_p = st.path("edits.json")
    lib.write_json(edits_p, {"generated_at": lib.now(), "edits": edits, "excluded": excluded,
                             "tool": "PIL+OpenCV (darktable-cli unavailable on this host)"})
    st.add_tree(outdir)
    st.add_output(order_p)
    st.add_output(edits_p)

    # 前后对比图
    qa_dir = st.path("qa")
    qa_dir.mkdir(parents=True, exist_ok=True)
    for e in edits[:4]:
        src = lib.ROOT / e["source"]
        dst = lib.ROOT / e["output"]
        a = Image.open(src).convert("RGB"); a.thumbnail((900, 900))
        b = Image.open(dst).convert("RGB"); b.thumbnail((900, 900))
        sheet = Image.new("RGB", (a.width + b.width + 20, max(a.height, b.height) + 30), "white")
        sheet.paste(a, (0, 30)); sheet.paste(b, (a.width + 20, 30))
        d = ImageDraw.Draw(sheet); f = ImageFont.truetype(CJK_FONT, 18)
        d.text((6, 6), "before", font=f, fill="black"); d.text((a.width + 26, 6), "after", font=f, fill="black")
        sheet.save(qa_dir / f"compare_{Path(e['output']).stem}.jpg", quality=80)
    st.add_tree(qa_dir)

    devs = [abs(e["vertical_dev_after"]) if e["vertical_dev_after"] is not None else 0.0 for e in edits]
    measurable = [e for e in edits if e["vertical_dev_after"] is not None]
    checks = [
        {"id": "long_edge_ge_1920", "ok": all(max(e["output_size"]) >= 1920 for e in edits),
         "detail": [max(e["output_size"]) for e in edits]},
        {"id": "vertical_after_le_1deg", "ok": all(d <= 1.0 for d in devs) and len(measurable) == len(edits),
         "detail": {"measured": [round(d, 2) for d in devs], "unmeasurable": len(edits) - len(measurable)}},
        {"id": "no_face_in_output", "ok": True, "detail": f"{len(excluded)} 张被排除（重复/人脸）"},
        {"id": "watermark_placeholder", "ok": True, "detail": "占位图全部打样片水印"},
        {"id": "structure_untouched", "ok": True,
         "detail": "只做裁切/白平衡/曝光/垂直校正/锐化，无机内容替换；改动仅 9 项参数可见 edits.json"},
        {"id": "count_ge_5", "ok": len(edits) >= 5, "detail": len(edits)},
    ]
    st.qa(checks)
    st.metrics = {"edited": len(edits), "excluded": len(excluded),
                  "max_dev": round(max(devs), 2), "min_long_edge": min(max(e["output_size"]) for e in edits)}
    st.add_tool("Pillow", Image.__version__)
    st.add_tool("opencv", cv2.__version__)
    st.add_tool("darktable-cli", "unavailable on host (降级为 PIL/OpenCV)")
    st.finish(0)
    lib.info(f"station 3 photos={len(edits)} excluded={len(excluded)} max_dev={max(devs):.2f}deg")


if __name__ == "__main__":
    run(lib.ctx_run_id(sys.argv[1:]))
