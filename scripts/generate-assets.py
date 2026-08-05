#!/usr/bin/env python3
"""Code-first asset generation for TinyPalette (icons + store assets)."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS = os.path.join(ROOT, "icons")
STORE = os.path.join(ROOT, "store-assets")

for d in (ICONS, STORE, os.path.join(STORE, "screenshots", "en"), os.path.join(STORE, "screenshots", "zh_CN")):
    os.makedirs(d, exist_ok=True)

PINK = (223, 167, 176)
LAV = (200, 182, 232)
BLUE = (184, 200, 232)
CREAM = (255, 249, 245)
TEXT = (74, 70, 80)
TEXT_SOFT = (140, 133, 149)


def font(size, bold=True, chinese=False):
    if chinese:
        candidates = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
        ]
    else:
        candidates = [
            "C:/Windows/Fonts/SegoeUI-Bold.ttf" if bold else "C:/Windows/Fonts/SegoeUI.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def round_rect(draw, box, r, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=r, fill=fill)
    if outline:
        draw.rounded_rectangle(box, radius=r, outline=outline, width=width)


# ---------- ICONS ----------
def make_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = int(size * 0.14)
    round_rect(d, [pad, pad, size - pad, size - pad], int(size * 0.28), CREAM + (255,))
    cx = size / 2
    cy = size / 2
    r = size * 0.13
    gap = size * 0.20
    for i, col in enumerate([PINK, LAV, BLUE]):
        x = cx + (i - 1) * gap
        d.ellipse([x - r, cy - r, x + r, cy + r], fill=col + (255,))
    path = os.path.join(ICONS, f"icon{size}.png")
    img.save(path)
    print("icon", path)


for s in (16, 48, 128):
    make_icon(s)


# ---------- STORE SCREENSHOT ----------
def draw_copy_icon(draw, box, color):
    x, y, x2, y2 = box
    w = x2 - x
    pad = max(1, int(w * 0.18))
    r = max(2, int(w * 0.16))
    thick = max(1, int(w * 0.10))
    draw.rounded_rectangle(
        [x + pad, y + int(pad * 1.6), x2 - int(pad * 0.6), y2 - int(pad * 0.4)],
        radius=r, outline=color, width=thick
    )
    draw.rounded_rectangle(
        [x + int(pad * 2.4), y + pad, x2 - pad, y2 - int(pad * 1.4)],
        radius=r, outline=color, width=thick
    )


def draw_heart(draw, cx, cy, r, fill):
    d = r
    draw.ellipse([cx - d - r * 0.1, cy - d * 0.55, cx + r * 0.1, cy + d * 0.65], fill=fill)
    draw.ellipse([cx - r * 0.1, cy - d * 0.55, cx + d + r * 0.1, cy + d * 0.65], fill=fill)
    draw.polygon([
        (cx - d * 0.92, cy + d * 0.25),
        (cx + d * 0.92, cy + d * 0.25),
        (cx, cy + d * 1.25)
    ], fill=fill)


def make_screenshot(lang="en"):
    zh = lang == "zh_CN"
    t = {
        "en": {
            "tagline": "a tiny color companion",
            "tapToCopy": "Tap to copy",
            "hex": "HEX",
            "rgb": "RGB",
            "hsl": "HSL",
            "copyCss": "Copy CSS",
            "recent": "Recent",
            "favorites": "Favorites",
            "title": "TinyPalette",
            "subtitle": "A tiny beautiful color companion for everyday creators."
        },
        "zh_CN": {
            "tagline": "小巧可爱的调色小助手",
            "tapToCopy": "点击复制",
            "hex": "HEX",
            "rgb": "RGB",
            "hsl": "HSL",
            "copyCss": "复制 CSS",
            "recent": "最近使用",
            "favorites": "收藏夹",
            "title": "TinyPalette",
            "subtitle": "为日常创作者准备的可爱调色伴侣。"
        }
    }[lang]

    W, H = 1280, 800
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    blob_size = 520
    blobs = [
        (-120, -120, LAV, 110),
        (980, -80, BLUE, 110),
        (760, 560, PINK, 120),
        (160, 520, (223, 200, 176), 70)
    ]
    for bx, by, col, alpha in blobs:
        od.ellipse([bx, by, bx + blob_size, by + blob_size], fill=col + (alpha,))
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=42))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(img)

    px, py, pw, ph = 460, 135, 360, 550
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for offset in range(24, 0, -1):
        alpha = int(8 - offset * 0.28)
        if alpha < 0:
            alpha = 0
        sd.rounded_rectangle(
            [px + offset, py + offset, px + pw + offset, py + ph + offset],
            radius=28, fill=(223, 167, 176, alpha)
        )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=10))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
    d = ImageDraw.Draw(img)

    round_rect(d, [px, py, px + pw, py + ph], 28, (255, 255, 255, 245))
    d.rounded_rectangle([px, py, px + pw, py + ph], radius=28, outline=(255, 255, 255, 235), width=2)

    cx = px + pw / 2
    dot_r = 9
    gd = 16
    for i, col in enumerate([PINK, LAV, BLUE]):
        x = cx + (i - 1) * gd
        d.ellipse([x - dot_r, py + 40 - dot_r, x + dot_r, py + 40 + dot_r], fill=col)

    d.text((cx, py + 62), t["title"], font=font(22, chinese=zh), fill=TEXT, anchor="mm")
    d.text((cx, py + 86), t["tagline"], font=font(12, bold=False, chinese=zh), fill=TEXT_SOFT, anchor="mm")

    iy = py + 118
    round_rect(d, [px + 24, iy, px + pw - 24, iy + 44], 12, (255, 255, 255, 255))
    d.rounded_rectangle([px + 24, iy, px + pw - 24, iy + 44], radius=12, outline=(223, 167, 176, 120), width=1)
    d.text((px + 24 + 16, iy + 22), "#", font=font(18), fill=TEXT_SOFT, anchor="mm")
    d.text((px + 24 + 34, iy + 22), "FFF7EB", font=font(17), fill=TEXT, anchor="lm")
    d.rounded_rectangle([px + pw - 24 - 34, iy + 7, px + pw - 24 - 4, iy + 37], radius=8,
                        fill=(255, 247, 235), outline=(255, 255, 255, 255), width=2)

    vy = iy + 66
    round_rect(d, [px + 24, vy, px + pw - 24, vy + 96], 18, (255, 247, 235))
    d.rounded_rectangle([px + 24, vy, px + pw - 24, vy + 96], radius=18, outline=(255, 255, 255, 220), width=2)
    d.text((cx, vy + 76), t["tapToCopy"], font=font(11, bold=False, chinese=zh), fill=TEXT, anchor="mm")

    infos = [
        (t["hex"], "#FFF7EB", PINK),
        (t["rgb"], "255, 247, 235", LAV),
        (t["hsl"], "34°, 100%, 96%", BLUE)
    ]
    card_y = vy + 112
    card_h = 58
    for i, (label, val, col) in enumerate(infos):
        y = card_y + i * (card_h + 8)
        round_rect(d, [px + 24, y, px + pw - 24, y + card_h], 12, (255, 255, 255, 242))
        d.rounded_rectangle([px + 24, y, px + pw - 24, y + card_h], radius=12, outline=(255, 255, 255, 235), width=1)
        d.text((px + 40, y + 17), label, font=font(10, bold=False), fill=TEXT_SOFT, anchor="lm")
        d.text((px + 40, y + 37), val, font=font(15), fill=TEXT, anchor="lm")
        chip_x = px + pw - 24 - 34
        d.rounded_rectangle([chip_x, y + 18, chip_x + 28, y + 40], radius=7, fill=col + (55,))
        draw_copy_icon(d, [chip_x + 5, y + 21, chip_x + 23, y + 37], TEXT)

    by = card_y + len(infos) * (card_h + 8) + 2
    round_rect(d, [px + 24, by, px + pw - 24, by + 42], 12, PINK)
    d.text((cx, by + 21), t["copyCss"], font=font(14, chinese=zh), fill=(255, 255, 255), anchor="mm")

    board_x = px + pw + 64
    d.text((board_x, py + 22), t["recent"], font=font(16, chinese=zh), fill=TEXT, anchor="lm")
    recent_cols = [
        (255, 247, 235), (200, 182, 232), (184, 200, 232), (223, 167, 176),
        (190, 230, 200), (245, 210, 160), (160, 210, 230), (230, 180, 200)
    ]
    sw = 56
    for i, col in enumerate(recent_cols):
        r = i % 4
        c = i // 4
        x = board_x + r * (sw + 14)
        y = py + 50 + c * (sw + 14)
        round_rect(d, [x, y, x + sw, y + sw], 14, col)
        d.rounded_rectangle([x, y, x + sw, y + sw], radius=14, outline=(255, 255, 255, 235), width=2)

    fav_y = py + 50 + 2 * (sw + 14) + 32
    d.text((board_x, fav_y), t["favorites"], font=font(16, chinese=zh), fill=TEXT, anchor="lm")
    favs = [(223, 167, 176), (200, 182, 232)]
    for i, col in enumerate(favs):
        x = board_x + i * (sw + 14)
        y = fav_y + 30
        round_rect(d, [x, y, x + sw, y + sw], 14, col)
        d.rounded_rectangle([x, y, x + sw, y + sw], radius=14, outline=(255, 255, 255, 235), width=2)
        d.ellipse([x + sw - 14, y - 4, x + sw + 2, y + 12], fill=(255, 255, 255))
        draw_heart(d, x + sw - 6, y + 4, 4, PINK)

    d.text((80, 94), t["title"], font=font(34, chinese=zh), fill=TEXT, anchor="lm")
    d.text((80, 136), t["subtitle"], font=font(16, bold=False, chinese=zh), fill=TEXT_SOFT, anchor="lm")

    out = os.path.join(STORE, "screenshots", lang, "tiny-palette-screenshot.png")
    img.save(out)
    print("screenshot", out)


# ---------- PROMO TILES ----------
def draw_center(d, text, cx, cy, f, fill):
    b = d.textbbox((0, 0), text, font=f)
    d.text((cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2), text, font=f, fill=fill)


def make_promo_440():
    W, H = 440, 280
    for lang in ("en", "zh_CN"):
        zh = lang == "zh_CN"
        title = "TinyPalette"
        subtitle = "A tiny color companion" if lang == "en" else "小巧可爱的调色小助手"
        cta = "Try It Now · 立即体验" if lang == "en" else "立即体验 · Try It Now"

        img = Image.new("RGB", (W, H), CREAM)
        d = ImageDraw.Draw(img)

        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([-80, -90, 180, 190], fill=LAV + (90,))
        od.ellipse([260, -60, 520, 200], fill=BLUE + (80,))
        od.ellipse([200, 180, 500, 420], fill=PINK + (85,))
        overlay = overlay.filter(ImageFilter.GaussianBlur(radius=26))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        d = ImageDraw.Draw(img)

        # card
        cx, cy = W / 2, H / 2
        card_w, card_h = 172, 118
        card_x, card_y = cx - card_w / 2, cy - 26
        round_rect(d, [card_x, card_y, card_x + card_w, card_y + card_h], 18, (255, 255, 255, 245))
        d.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=18, outline=(255, 255, 255, 240), width=2)

        # preview inside card
        round_rect(d, [card_x + 14, card_y + 14, card_x + card_w - 14, card_y + 58], 10, (255, 247, 235))
        d.text((cx, card_y + 84), "#FFF7EB", font=font(14), fill=TEXT, anchor="mm")

        # dots
        dot_r = 5
        for i, col in enumerate([PINK, LAV, BLUE]):
            dx = cx + (i - 1) * 10
            d.ellipse([dx - dot_r, card_y - 18 - dot_r, dx + dot_r, card_y - 18 + dot_r], fill=col)

        # title / subtitle / cta
        draw_center(d, title, cx, 44, font(22, chinese=zh), TEXT)
        draw_center(d, subtitle, cx, 70, font(11, bold=False, chinese=zh), TEXT_SOFT)

        btn_w, btn_h = 140, 32
        btn_x, btn_y = cx - btn_w / 2, H - 50
        round_rect(d, [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], 16, PINK)
        draw_center(d, cta, cx, btn_y + btn_h / 2, font(12, chinese=zh), (255, 255, 255))

        out = os.path.join(STORE, "promo", "440x280.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        img.save(out)
        print("promo 440", out)


def make_promo_1400():
    W, H = 1400, 560
    for lang in ("en", "zh_CN"):
        zh = lang == "zh_CN"
        subtitle = "A tiny color companion for everyday creators" if lang == "en" else "为日常创作者准备的可爱调色伴侣"
        cta = "Try It Now · 立即体验" if lang == "en" else "立即体验 · Try It Now"

        img = Image.new("RGB", (W, H), CREAM)
        d = ImageDraw.Draw(img)

        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([-120, -120, 420, 420], fill=LAV + (95,))
        od.ellipse([980, -80, 1500, 460], fill=BLUE + (85,))
        od.ellipse([1080, 260, 1500, 700], fill=PINK + (90,))
        overlay = overlay.filter(ImageFilter.GaussianBlur(radius=34))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        d = ImageDraw.Draw(img)

        # left text
        d.text((92, 210), "TinyPalette", font=font(56, chinese=zh), fill=TEXT, anchor="lm")
        d.text((92, 280), subtitle, font=font(20, bold=False, chinese=zh), fill=TEXT_SOFT, anchor="lm")

        # CTA button
        btn_w, btn_h = 180, 46
        btn_x, btn_y = 92, 330
        round_rect(d, [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], 23, PINK)
        draw_center(d, cta, btn_x + btn_w / 2, btn_y + btn_h / 2, font(15, chinese=zh), (255, 255, 255))

        # right popup card
        px, py, pw, ph = 880, 115, 360, 360
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        for offset in range(20, 0, -1):
            alpha = int(7 - offset * 0.3)
            if alpha < 0:
                alpha = 0
            sd.rounded_rectangle([px + offset, py + offset, px + pw + offset, py + ph + offset], radius=24, fill=(223, 167, 176, alpha))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=8))
        img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
        d = ImageDraw.Draw(img)

        round_rect(d, [px, py, px + pw, py + ph], 24, (255, 255, 255, 248))
        d.rounded_rectangle([px, py, px + pw, py + ph], radius=24, outline=(255, 255, 255, 240), width=2)

        cx = px + pw / 2
        dot_r = 7
        for i, col in enumerate([PINK, LAV, BLUE]):
            x = cx + (i - 1) * 12
            d.ellipse([x - dot_r, py + 34 - dot_r, x + dot_r, py + 34 + dot_r], fill=col)
        d.text((cx, py + 58), "TinyPalette", font=font(18, chinese=zh), fill=TEXT, anchor="mm")

        iy = py + 92
        round_rect(d, [px + 28, iy, px + pw - 28, iy + 38], 10, (255, 255, 255, 255))
        d.rounded_rectangle([px + 28, iy, px + pw - 28, iy + 38], radius=10, outline=(223, 167, 176, 120), width=1)
        d.text((px + 28 + 14, iy + 19), "#", font=font(16), fill=TEXT_SOFT, anchor="mm")
        d.text((px + 28 + 30, iy + 19), "FFF7EB", font=font(15), fill=TEXT, anchor="lm")

        vy = iy + 52
        round_rect(d, [px + 28, vy, px + pw - 28, vy + 80], 14, (255, 247, 235))
        d.text((cx, vy + 62), "Tap to copy" if lang == "en" else "点击复制", font=font(10, bold=False, chinese=zh), fill=TEXT, anchor="mm")

        infos = [
            ("HEX", "#FFF7EB", PINK),
            ("RGB", "255, 247, 235", LAV),
            ("HSL", "34°, 100%, 96%", BLUE)
        ]
        card_y = vy + 94
        card_h = 46
        for i, (label, val, col) in enumerate(infos):
            y = card_y + i * (card_h + 8)
            round_rect(d, [px + 28, y, px + pw - 28, y + card_h], 10, (255, 255, 255, 242))
            d.text((px + 44, y + 15), label, font=font(9, bold=False), fill=TEXT_SOFT, anchor="lm")
            d.text((px + 44, y + 31), val, font=font(12), fill=TEXT, anchor="lm")
            d.rounded_rectangle([px + pw - 28 - 26, y + 13, px + pw - 28 - 4, y + 33], radius=6, fill=col + (55,))

        out = os.path.join(STORE, "promo", "1400x560.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        img.save(out)
        print("promo 1400", out)


make_screenshot("en")
make_screenshot("zh_CN")
make_promo_440()
make_promo_1400()
print("DONE")
