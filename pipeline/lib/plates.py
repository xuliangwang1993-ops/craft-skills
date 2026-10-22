"""Code-drawn placeholder plates.

No AI image generation, no stock footage: when the shop has not sent real
footage yet, every frame is drawn here with PIL from the logo's own palette.
Each plate is 1088x1920 (a multiple of 16 — MLT's swscale path rejects 1080-wide
frames, see docs), cropped to 1080x1920 downstream.
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1088, 1920
NAVY = (16, 34, 113)
INK = (12, 22, 60)
CREAM = (248, 243, 254)
ACCENT = (66, 71, 203)
COPPER = (196, 116, 66)
COPPER_HI = (232, 160, 96)
NOODLE = (232, 190, 122)
HERB = (86, 140, 82)
SEED = 20261022


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def _vgrad(size, top, bottom) -> Image.Image:
    w, h = size
    img = Image.new("RGB", (1, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        d.point((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img.resize((w, h), Image.BILINEAR)


def _noise(img: Image.Image, amount: int = 6, seed: int = SEED) -> Image.Image:
    rnd = random.Random(seed)
    px = img.load()
    w, h = img.size
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            n = rnd.randint(-amount, amount)
            r, g, b = px[x, y]
            px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)))
    return img


def _steam(draw: ImageDraw.ImageDraw, cx: int, base_y: int, height: int, alpha: int, seed: int):
    rnd = random.Random(seed)
    for i in range(5):
        x = cx + rnd.randint(-120, 120)
        pts = []
        for k in range(24):
            t = k / 23
            pts.append((x + int(math.sin(t * 5 + i) * 26), base_y - int(t * height)))
        draw.line(pts, fill=(255, 255, 255, alpha), width=rnd.choice([3, 4, 6]))


def plate_steam_pot(brand: dict) -> Image.Image:
    """Copper pot mouth seen from above, steam rising. Shot 1."""
    img = _vgrad((W, H), (26, 18, 44), (74, 30, 22))
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy, r = W // 2, 1180, 430
    d.ellipse((cx - r - 46, cy - r - 46, cx + r + 46, cy + r + 46), fill=(90, 46, 30, 255))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=COPPER + (255,))
    d.ellipse((cx - r + 34, cy - r + 34, cx + r - 34, cy + r - 34), fill=(150, 78, 44, 255))
    d.ellipse((cx - r + 62, cy - r + 62, cx + r - 62, cy + r - 62), fill=(176, 82, 40, 255))
    rnd = random.Random(SEED)
    for i in range(150):  # broth bubbles
        a = rnd.random() * math.tau
        rad = rnd.random() ** 0.6 * (r - 70)
        bx, by = cx + int(math.cos(a) * rad), cy + int(math.sin(a) * rad)
        rr = rnd.randint(3, 12)
        d.ellipse((bx - rr, by - rr, bx + rr, by + rr), fill=(210, 120, 60, 170))
    for i in range(40):  # herbs
        a = rnd.random() * math.tau
        rad = rnd.random() ** 0.5 * (r - 90)
        bx, by = cx + int(math.cos(a) * rad), cy + int(math.sin(a) * rad)
        d.ellipse((bx - 9, by - 5, bx + 9, by + 5), fill=HERB + (200,))
    _steam(d, cx, cy - r - 20, 620, 70, SEED)
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 0, W, 250), fill=(0, 0, 0, 0))
    return _noise(img, 4)


def plate_noodle_lift(brand: dict) -> Image.Image:
    """Chopsticks lifting a cluster of noodles out of broth. Shot 2."""
    img = _vgrad((W, H), (30, 22, 46), (96, 44, 28))
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy = W // 2, 1330
    d.ellipse((cx - 470, cy - 300, cx + 470, cy + 360), fill=(120, 60, 36, 255))
    d.ellipse((cx - 430, cy - 270, cx + 430, cy + 320), fill=(178, 92, 46, 255))
    rnd = random.Random(SEED + 1)
    # a lifted bundle: strands converge toward the chopstick pinch point
    pinch = (cx, cy - 640)
    for i in range(22):
        spread = (i - 11) * 21
        pts = []
        for k in range(26):
            t = k / 25
            x = pinch[0] + spread * t + int(math.sin(t * 3.1 + i * 0.7) * 30 * t)
            y = pinch[1] + int((cy + 210 - pinch[1]) * t) - int(math.sin(t * math.pi) * 26)
            pts.append((x, y))
        d.line(pts, fill=NOODLE + (255,), width=12)
        d.line([(p[0], p[1] - 3) for p in pts], fill=(255, 226, 168, 130), width=3)
    # dangling tails below the pinch, into the broth
    for i in range(9):
        x0 = pinch[0] - 150 + i * 38
        d.line([(x0, pinch[1]), (x0 + rnd.randint(-24, 24), cy + 200)], fill=NOODLE + (235,), width=9)
    for off in (-118, 128):  # chopsticks, slightly splayed
        d.line([(cx + off - 74, cy + 300), (cx + off + 26, pinch[1] - 230)], fill=(64, 42, 30, 255), width=27)
        d.line([(cx + off - 64, cy + 300), (cx + off + 36, pinch[1] - 230)], fill=(132, 96, 70, 255), width=8)
    _steam(d, cx, cy - 180, 560, 62, SEED + 1)
    return _noise(img.filter(ImageFilter.GaussianBlur(0.5)), 4)


def plate_bowl_top(brand: dict) -> Image.Image:
    """Signature bowl, 45° top-down. Shot 3."""
    img = _vgrad((W, H), (18, 16, 38), (60, 34, 30))
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy = W // 2, 1080
    d.ellipse((cx - 480, cy - 340, cx + 480, cy + 340), fill=(58, 40, 34, 255))
    d.ellipse((cx - 430, cy - 300, cx + 430, cy + 300), fill=CREAM + (255,))
    d.ellipse((cx - 380, cy - 255, cx + 380, cy + 255), fill=(150, 74, 40, 255))
    rnd = random.Random(SEED + 2)
    # noodle nest: nested arcs, not dots
    for ring in range(9):
        rad = 90 + ring * 26
        for arc_i in range(3):
            start = arc_i * 120 + ring * 23
            d.arc((cx - rad, cy - int(rad * 0.62), cx + rad, cy + int(rad * 0.62)),
                  start=start, end=start + 96, fill=NOODLE + (255,), width=17)
            d.arc((cx - rad, cy - int(rad * 0.62) - 5, cx + rad, cy + int(rad * 0.62) - 5),
                  start=start, end=start + 96, fill=(255, 226, 168, 120), width=4)
    for i in range(14):  # toppings
        a = rnd.random() * math.tau
        rad = rnd.random() ** 0.5 * 300
        bx, by = cx + int(math.cos(a) * rad), cy + int(math.sin(a) * rad * 0.62)
        rr = rnd.randint(16, 34)
        col = rnd.choice([(206, 92, 70), (240, 240, 232), (86, 140, 82), (168, 44, 40)])
        d.ellipse((bx - rr, by - rr // 2, bx + rr, by + rr // 2), fill=col + (255,))
    for i in range(3):  # egg halves
        bx = cx - 190 + i * 190
        d.ellipse((bx - 62, cy + 60, bx + 62, cy + 130), fill=(250, 240, 228, 255))
        d.ellipse((bx - 26, cy + 78, bx + 26, cy + 112), fill=(242, 158, 46, 255))
    return _noise(img.filter(ImageFilter.GaussianBlur(0.7)), 4)


def plate_storefront(brand: dict) -> Image.Image:
    """Shop front at dusk, signboard lit. Shot 4."""
    img = _vgrad((W, H), (14, 20, 54), (44, 30, 58))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 1260, W, H), fill=(28, 26, 34, 255))
    d.rectangle((60, 980, W - 60, 1270), fill=(24, 30, 74, 255))
    d.rectangle((60, 980, W - 60, 1270), outline=ACCENT + (255,), width=5)
    for x in range(120, W - 200, 200):  # window glow
        d.rectangle((x, 1046, x + 150, 1236), fill=(255, 196, 120, 58))
        d.rectangle((x, 1046, x + 150, 1236), outline=(255, 214, 150, 120), width=3)
    d.rectangle((W // 2 - 78, 1010, W // 2 + 78, 1268), fill=(255, 208, 140, 90))
    d.rectangle((W // 2 - 78, 1010, W // 2 + 78, 1268), outline=(255, 226, 170, 160), width=3)
    d.rounded_rectangle((120, 560, W - 120, 900), radius=24, fill=(10, 18, 58, 255))
    d.rounded_rectangle((120, 560, W - 120, 900), radius=24, outline=COPPER_HI + (255,), width=6)
    try:
        f1 = _font(brand["font_en"], 116)
        f2 = _font(brand["font_zh"], 62)
    except Exception:
        f1 = f2 = ImageFont.load_default()
    d.text((W // 2, 700), "SLURP SLURP", font=f1, fill=(255, 244, 224, 255), anchor="mm")
    d.text((W // 2, 810), "N O O D L E", font=f2, fill=COPPER_HI + (255,), anchor="mm")
    for i in range(9):  # hanging lights
        x = 110 + i * 108
        d.line([(x, 900), (x, 980)], fill=(80, 80, 90, 255), width=3)
        d.ellipse((x - 16, 980, x + 16, 1012), fill=(255, 210, 140, 220))
    return _noise(img.filter(ImageFilter.GaussianBlur(0.5)), 5)


def load_logo_transparent(path: str) -> Image.Image:
    """The client's logo PNG ships with an opaque white background.

    Keying it out is lossless here: every near-white pixel is background, the mark itself
    is navy/violet. Without this the end card shows a white box on the cream card.
    """
    from PIL import ImageChops
    img = Image.open(path).convert("RGBA")
    r, g, b, a = img.split()
    # pure PIL: this numpy build segfaults on .min(axis=2) over a strided view
    brightest = ImageChops.lighter(ImageChops.lighter(r, g), b)
    darkest = ImageChops.darker(ImageChops.darker(r, g), b)
    bright_enough = darkest.point(lambda v: 255 if v > 232 else 0)
    low_sat = ImageChops.difference(brightest, darkest).point(lambda v: 255 if v < 18 else 0)
    background = ImageChops.multiply(bright_enough, low_sat)
    img.putalpha(ImageChops.multiply(a, ImageChops.invert(background)))
    return img


def plate_logo_card(brand: dict) -> Image.Image:
    """End card: logo + phone on cream. Shot 7."""
    img = _vgrad((W, H), (250, 247, 255), (232, 226, 248))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((W // 2 - 520, -260, W // 2 + 520, 780), fill=ACCENT + (26,))
    logo = load_logo_transparent(brand["logo"])
    lw = 780
    logo = logo.resize((lw, lw), Image.LANCZOS)
    img.paste(logo, (W // 2 - lw // 2, 330), logo)
    f1 = _font(brand["font_en"], 96)
    f2 = _font(brand["font_zh"], 58)
    d.text((W // 2, 1290), "Slurp Slurp Noodle", font=f1, fill=NAVY + (255,), anchor="mm")
    d.text((W // 2, 1410), "S Y D N E Y", font=f2, fill=ACCENT + (255,), anchor="mm")
    # the phone number lives in the subtitle track, not here — printing it twice reads as a bug
    return _noise(img, 3)


def plate_photo_placeholder(brand: dict) -> Image.Image:
    """Official site photo, letterboxed on brand ground. Shot 5/6 filler."""
    base = _vgrad((W, H), (16, 26, 74), (10, 16, 48))
    photo = Image.open(brand["photo"]).convert("RGB")
    scale = (W - 80) / photo.width
    ph = photo.resize((W - 80, int(photo.height * scale)), Image.LANCZOS)
    base.paste(photo.resize((W - 80, int(photo.height * scale)), Image.LANCZOS),
               (40, (H - ph.height) // 2), )
    d = ImageDraw.Draw(base, "RGBA")
    d.rectangle((40, (H - ph.height) // 2 - 3, W - 40, (H - ph.height) // 2 + ph.height + 3),
                outline=COPPER_HI + (255,), width=4)
    return base


PLATES = {
    "steam_pot": plate_steam_pot,
    "noodle_lift": plate_noodle_lift,
    "bowl_top": plate_bowl_top,
    "storefront": plate_storefront,
    "logo_card": plate_logo_card,
    "photo_placeholder": plate_photo_placeholder,
}


def render(name: str, brand: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}.png"
    PLATES[name](brand).save(path, "PNG")
    return path
