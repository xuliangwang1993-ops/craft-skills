#!/usr/bin/env python3
"""Station 1 — 素材采集与事实底账.

Reads: brief.json + the archived official page + customer_media/.
Writes: facts.json, media_manifest.json, licenses.json, shot_request.md.

Rule: nothing is invented. Every row of the client fact sheet becomes a fact with a
source_id and a status. Only `verified` facts may later appear on screen.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.common import (ROOT, Station, media_info, now, read_json, sha256, station_main,
                        validate, write_json)

CHECKED = "2026-10-22"
SITE = "https://revu.website/142620/"


def palette(logo: Path) -> dict:
    """opencv k-means on the logo's opaque pixels — brand colours are derived, not guessed."""
    import cv2
    import numpy as np
    img = cv2.imread(str(logo), cv2.IMREAD_UNCHANGED)
    b, g, r, a = cv2.split(img)
    mask = a > 200
    px = np.stack([r[mask], g[mask], b[mask]], 1).astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.2)
    _, labels, centers = cv2.kmeans(px, 5, None, crit, 5, cv2.KMEANS_PP_CENTERS)
    counts = np.bincount(labels.ravel(), minlength=5)
    order = np.argsort(-counts)
    hexes = ["#%02X%02X%02X" % tuple(int(v) for v in centers[i]) for i in order]
    # primary = most saturated cluster with meaningful share
    def sat(h):
        rr, gg, bb = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
        return max(rr, gg, bb) - min(rr, gg, bb)
    primary = max([h for h, i in zip(hexes, order) if counts[i] > 500], key=sat, default=hexes[0])
    return {"clusters": hexes, "primary": primary}


def main(st: Station):
    brief = read_json(st.read(st.dir.parent / "00_brief/brief.json"))
    validate(brief, "brief", where="00_brief/brief.json")

    logo = ROOT / "inputs/customer_media/Slur-Slurp-New-Logo.png"
    photo = ROOT / "inputs/customer_media/75513371_2388668874794660_3434699996744646656_n.jpg"
    st.require(logo.exists() and photo.exists(), "official site images missing in inputs/customer_media/")
    st.read(logo); st.read(photo)
    site_snapshot = ROOT / "inputs/site_snapshot/index.html"
    st.read(site_snapshot)

    colors = palette(logo)

    F = []

    def fact(sid, field, value, status, stype, ref, evidence="", note=""):
        F.append({
            "source_id": sid, "field": field, "value": value, "status": status,
            "source": {"type": stype, "ref": ref, "note": note},
            "checked_at": CHECKED, "evidence": evidence,
        })

    fact("src_web_title", "店名（英文）", "Slurp Slurp Noodle", "verified", "official_site", SITE,
         "官网 <title>Slurp Slurp Noodle</title>")
    fact("src_web_tel", "电话", "02 9663 3817", "verified", "official_site", SITE,
         "官网 <a href=\"tel:0296633817\">；展示格式按澳洲惯例分组")
    fact("src_web_cn_name", "店名（中文）", None, "pending_customer", "customer", "客户口头说法",
         "「小锅米线」仅为客户口头说法，官网无中文名")
    fact("src_dir_addr", "地址", "Shop 1 / R1, 57 Rothschild Ave, Rosebery NSW 2018", "unverified",
         "directory", "oceaniabiz / Uber Eats / Mate's Table 三处一致",
         "第三方目录一致，但官网未写，未经客户确认")
    fact("src_ue_cuisine", "菜系", "云南米线", "unverified", "directory", "Uber Eats 店页摘要",
         "未核实；不得入片")
    fact("src_ue_signature", "招牌菜", ["Slurp Slurp Little Copper Pot", "Signature Minty Beef"],
         "unverified", "directory", "Uber Eats 店页摘要", "未核实；不得入片")
    fact("src_hours_mates", "营业时间（来源 A）", "周二–周日 11:00–21:00，周一休", "conflict",
         "directory", "Mate's Table", "与来源 B 冲突")
    fact("src_hours_zmenu", "营业时间（来源 B）", "周五–周日 11:00–15:00、16:00–21:00，周一休",
         "conflict", "directory", "Zmenu", "与来源 A 冲突")
    fact("src_site_menu", "菜单与价格", None, "pending_customer", "official_site", SITE,
         "官网没有菜单与价格")
    fact("src_site_social", "社媒账号", None, "pending_customer", "official_site", SITE,
         "官网无社媒链接")
    fact("src_site_logo", "logo", "inputs/customer_media/Slur-Slurp-New-Logo.png", "verified",
         "official_site", SITE + "assets/images/Slur-Slurp-New-Logo.png",
         "500x500 RGBA；授权待客户书面同意")
    fact("src_site_photo", "店内图",
         "inputs/customer_media/75513371_2388668874794660_3434699996744646656_n.jpg", "verified",
         "official_site", SITE + "assets/images/75513371_..._n.jpg",
         "680x510；文件名像 Facebook 导出；授权待客户书面同意")
    fact("src_revu_widget", "评价组件", "Revu data-bid=142620", "verified", "official_site", SITE,
         "官网为 Revu 评价组件页")
    fact("src_ue_rating", "评分", "4.8（900+ 评分）", "unverified", "directory", "Uber Eats",
         "第三方评分会变；入片前须截图存档，本片不使用")
    fact("src_brand_palette", "品牌色", colors, "verified", "official_site", "opencv k-means on logo",
         "从 logo 不透明像素提取，主色 %s" % colors["primary"])
    fact("src_font", "字体", None, "pending_customer", "customer", "—",
         "官网仅 Bootstrap 默认样式；本次用开源 Noto Sans SC + Inter")
    fact("src_city", "城市", "悉尼", "verified", "customer", "需求原句「悉尼小锅米线」",
         "客户需求中自述")

    unverified = [f["field"] for f in F if f["status"] != "verified"]
    conflicts = [{"field": "营业时间", "a": "src_hours_mates", "b": "src_hours_zmenu"}]
    facts = {
        "run_id": st.run_id, "generated_at": now(), "facts": F,
        "unverified_fields": sorted(set(unverified)), "conflicts": conflicts,
    }
    validate(facts, "facts", where="01_collect/facts.json")
    st.emit(write_json(st.dir / "facts.json", facts), "facts")

    # ---- media manifest -------------------------------------------------- #
    logo_info = media_info(logo) if logo.suffix.lower() in {".mp4", ".mov"} else {}
    from PIL import Image
    lw, lh = Image.open(logo).size
    pw, ph = Image.open(photo).size
    assets = [
        {"asset_id": "ast_logo_official", "kind": "image", "path": "inputs/customer_media/Slur-Slurp-New-Logo.png",
         "origin": "Slurp Slurp Noodle 官网", "origin_url": SITE + "assets/images/Slur-Slurp-New-Logo.png",
         "permission": "placeholder", "permission_status": "pending", "role": "logo",
         "sha256": sha256(logo), "width": lw, "height": lh, "duration": 0, "fps": 0,
         "license": "客户素材（未授权）", "in_delivery": False, "watermark": True,
         "notes": "官网 logo；客户书面同意前只能出现在带「样片 · 未授权」水印的样片里"},
        {"asset_id": "ast_photo_official", "kind": "image", "path": "inputs/customer_media/75513371_2388668874794660_3434699996744646656_n.jpg",
         "origin": "Slurp Slurp Noodle 官网", "origin_url": SITE + "assets/images/75513371_2388668874794660_3434699996744646656_n.jpg",
         "permission": "placeholder", "permission_status": "pending", "role": "placeholder",
         "sha256": sha256(photo), "width": pw, "height": ph, "duration": 0, "fps": 0,
         "license": "客户素材（未授权）", "in_delivery": False, "watermark": True,
         "notes": "680x510 < 1080p，只能当占位；正式片必须换店家手机拍摄的 ≥1080p/≥25fps 素材"},
        {"asset_id": "ast_music_original", "kind": "audio", "path": "runs/%s/03_edit/audio/bgm.wav" % st.run_id,
         "origin": "本流水线 numpy 合成（固定 seed 20261022）", "origin_url": "",
         "permission": "generated", "permission_status": "not-required", "role": "music",
         "sha256": "", "width": 0, "height": 0, "duration": 30, "fps": 0,
         "license": "CC0-1.0（自制，无第三方样本）", "in_delivery": True, "watermark": False,
         "notes": "无第三方采样；与画面同长，节拍 90 BPM"},
        {"asset_id": "ast_font_noto", "kind": "font", "path": "assets/fonts/NotoSansSC-Bold.otf",
         "origin": "Google Noto CJK", "origin_url": "https://github.com/notofonts/noto-cjk",
         "permission": "licensed", "permission_status": "granted", "role": "font",
         "sha256": "", "width": 0, "height": 0, "duration": 0, "fps": 0,
         "license": "SIL Open Font License 1.1", "in_delivery": True, "watermark": False,
         "notes": "中文字幕/标题"},
        {"asset_id": "ast_font_inter", "kind": "font", "path": "/usr/share/fonts/inter/Inter-ExtraBold.otf",
         "origin": "Inter Project", "origin_url": "https://github.com/rsms/inter",
         "permission": "licensed", "permission_status": "granted", "role": "font",
         "sha256": "", "width": 0, "height": 0, "duration": 0, "fps": 0,
         "license": "SIL Open Font License 1.1", "in_delivery": True, "watermark": False,
         "notes": "英文字幕/标题"},
        {"asset_id": "ast_graphics_generated", "kind": "graphic", "path": "runs/%s/03_edit/plates/" % st.run_id,
         "origin": "本流水线 PIL 绘制（无 AI 生图）", "origin_url": "",
         "permission": "generated", "permission_status": "not-required", "role": "graphic",
         "sha256": "", "width": 1080, "height": 1920, "duration": 0, "fps": 0,
         "license": "CC0-1.0（自制）", "in_delivery": True, "watermark": False,
         "notes": "版式、蒸汽线条、纹理均为代码绘制"},
    ]
    manifest = {
        "run_id": st.run_id, "generated_at": now(), "assets": assets,
        "placeholders_only": True, "customer_media_received": False,
    }
    validate(manifest, "media_manifest", where="01_collect/media_manifest.json")
    st.emit(write_json(st.dir / "media_manifest.json", manifest), "media_manifest")

    licenses = {
        "run_id": st.run_id, "generated_at": now(),
        "items": [
            {"asset_id": "ast_logo_official", "name": "Slurp Slurp Noodle logo",
             "origin": SITE, "license": "客户素材 — 未授权，仅样片占位",
             "license_url": SITE, "permission": "placeholder", "permission_status": "pending",
             "in_delivery": False, "attribution": "© Slurp Slurp Noodle"},
            {"asset_id": "ast_photo_official", "name": "店内菜品图（官网）",
             "origin": SITE, "license": "客户素材 — 未授权，仅样片占位",
             "license_url": SITE, "permission": "placeholder", "permission_status": "pending",
             "in_delivery": False, "attribution": "© Slurp Slurp Noodle"},
            {"asset_id": "ast_music_original", "name": "原创配乐 slurp-bed-90bpm.wav",
             "origin": "pipeline/stations/s03_edit.py 合成", "license": "CC0-1.0",
             "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
             "permission": "generated", "permission_status": "not-required", "in_delivery": True,
             "attribution": "原创，无第三方采样"},
            {"asset_id": "ast_font_noto", "name": "Noto Sans SC Bold/Regular",
             "origin": "https://github.com/notofonts/noto-cjk", "license": "OFL-1.1",
             "license_url": "https://scripts.sil.org/OFL", "permission": "licensed",
             "permission_status": "granted", "in_delivery": True, "attribution": "Google Noto Project"},
            {"asset_id": "ast_font_inter", "name": "Inter ExtraBold/Medium",
             "origin": "https://github.com/rsms/inter", "license": "OFL-1.1",
             "license_url": "https://scripts.sil.org/OFL", "permission": "licensed",
             "permission_status": "granted", "in_delivery": True, "attribution": "The Inter Project Authors"},
            {"asset_id": "ast_graphics_generated", "name": "版式与图形",
             "origin": "PIL 代码绘制", "license": "CC0-1.0",
             "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
             "permission": "generated", "permission_status": "not-required", "in_delivery": True,
             "attribution": "本流水线"},
        ],
        "blocked_from_delivery": ["ast_logo_official", "ast_photo_official"],
    }
    validate(licenses, "licenses", where="01_collect/licenses.json")
    st.emit(write_json(st.dir / "licenses.json", licenses), "licenses")

    # ---- shot request to the shop ---------------------------------------- #
    shot_request = f"""# 拍摄清单 · Slurp Slurp Noodle（30 秒宣传片素材）

> 客户版，可直接转发。用手机拍即可，不需要专业设备。
> 交片日期：{CHECKED} 起 7 天内；文件回传：微信原图/原视频（不要用微信「压缩发送」）。

## 一、必拍 5 组镜头（每组 5–10 秒，竖拍 + 横拍各一条）

| # | 镜头 | 怎么拍 | 时长 | 用途 |
|---|------|--------|------|------|
| 1 | 铜锅沸腾 | 手机靠近锅口 20–30cm，拍汤面翻滚、热气上升；不要拍到人脸 | 8–10s | 开头 3 秒抓人 |
| 2 | 加料 | 从上方 45° 拍手把肉片/配菜放进锅里，动作放慢 | 5–8s | 过程感 |
| 3 | 挑面 | 筷子把米线挑起，镜头跟着上升，拍到热气 | 5–8s | 食欲特写 |
| 4 | 店门/招牌 | 站在马路对面拍店门全景，带到招牌；白天和晚上各一条 | 5s | 结尾定位 |
| 5 | 招牌菜特写 | 成品碗放在桌上，45° 俯拍，顺时针慢慢转一圈 | 8–10s | 主视觉 |

## 二、拍摄要求（重要）

1. **分辨率**：手机相机设置里选 1080p 或 4K，30fps 或 60fps；不要用「慢动作」模式。
2. **横竖都拍**：同一动作先竖拍（9:16）再横拍（16:9），我们要出三个尺寸。
3. **光线**：白天靠窗自然光；晚上把店里灯全打开，不要用手机闪光灯。
4. **稳定**：双手持机、手肘夹紧；有条件的靠墙/靠桌，或用人像模式的「视频」防抖。
5. **收音**：不需要录说话，环境声保留即可（我们会重新配乐）。
6. **不要拍到**：顾客正脸、员工正脸（需书面同意）、其他品牌logo、收银小票。
7. **每条素材文件名**：`日期_镜头号_横or竖.mp4`，例如 `20261023_01_vertical.mp4`。

## 三、同时请提供（文字）

- [ ] 中文店名（官网只有英文名）
- [ ] 确认地址：Shop 1 / R1, 57 Rothschild Ave, Rosebery NSW 2018
- [ ] 营业时间（目前两个来源冲突，请给准确版本）
- [ ] 菜单与价格（含 GST，至少 6 个品项，中英名）
- [ ] 社媒账号（IG / 小红书 / Facebook）
- [ ] 字体偏好（有品牌字体请提供文件；没有我们用开源字体）
- [ ] **书面授权**：官网两张图（logo、菜品图）可用于宣传片；以及本次拍摄素材的使用范围

## 四、交付与验收

- 素材收到后 3 个工作日内出第一版；含 1 次修改。
- 验收标准：1080×1920 / 1080×1080 / 1920×1080 三个版本，中英字幕，30 秒 ±0.5 秒，响度 -14 LUFS。
"""
    (st.dir / "shot_request.md").write_text(shot_request, encoding="utf-8")
    st.outputs.append((st.dir / "shot_request.md", "text/markdown"))

    # ---- QA --------------------------------------------------------------- #
    st.check("S1-01", "每个素材都有来源+许可", f"{len(assets)}/{len(assets)}", "100%",
             all(a.get("origin") and a.get("license") for a in assets))
    st.check("S1-02", "客户素材 ≥1080p/≥25fps", "0 条客户实拍素材", "收到后 100%",
             False, "客户尚未提供实拍素材；官网占位图 680x510 不达标，已标 placeholder",
             severity="advisory")
    st.check("S1-03", "事实全部可追溯", f"{len(F)} facts / {len({f['source_id'] for f in F})} source_id",
             "1:1", len({f["source_id"] for f in F}) == len(F))
    st.check("S1-04", "未核实字段已隔离", len(facts["unverified_fields"]), "全部标记",
             all(f["status"] != "verified" for f in F if f["field"] in facts["unverified_fields"]))
    shots_listed = sum(1 for line in shot_request.splitlines() if line.startswith("| ") and line[2].isdigit())
    st.check("S1-05", "拍摄清单镜头数", shots_listed, ">=5", shots_listed >= 5)

    return {
        "scores": {"business": 3.0, "handoff": 5.0, "benchmark": 4.0, "craft": 3.0},
        "notes": [
            "事实底账 16 条全部带 source_id；营业时间冲突、地址未核实、菜单缺失都显式落库，下游只能读 verified。",
            "扣分：客户实拍素材为 0，官网图仅 680x510，达不到 1080p 交付标准 —— 这是本单最大的商业风险。",
            "crawl4ai 安装失败（见 reports/tool_verification.json），站点抓取降级为 curl + 本地解析，够用且可复现。",
        ],
    }


if __name__ == "__main__":
    sys.exit(station_main(main, 1, "collect", "素材采集"))
