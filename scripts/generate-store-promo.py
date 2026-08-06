#!/usr/bin/env python3
"""Generate TinyPalette Chrome Web Store promo tiles (bilingual English + Chinese)."""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(BASE, "fonts", "PressStart2P-Regular.ttf")
ICON_PATH = os.path.join(BASE, "icons", "icon48.png")
OUT_DIR = os.path.join(BASE, "store-assets", "promo")

# TinyPalette theme colors
BG = "#FFF0F5"
PANEL = "#FFFDF9"
PRIMARY = "#E8A0BF"
PRIMARY_DARK = "#C97A9B"
TEXT = "#5A3D4D"
TEXT_SOFT = "#A87E8F"
SHADOW_RGBA = (90, 61, 77, 31)

DEMO = "#E8A0BF"
DEMO_RGB = "232, 160, 191"
DEMO_HSL = "340°, 64%, 77%"
SWATCHES = ["#E8A0BF", "#A0C4E8", "#C9B6E4", "#B5E0C5"]


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgba(h, a):
    r, g, b = hex_to_rgb(h)
    return (r, g, b, int(a * 255))


def load_font(size):
    return ImageFont.truetype(FONT_PATH, size)


def load_cn_font(size):
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return load_font(size)


def has_cn(text):
    return any("\u4e00" <= c <= "\u9fff" for c in text)


def get_font(text, size):
    return load_cn_font(size) if has_cn(text) else load_font(size)


def draw_text(d, x, y, text, size, fill, anchor="lt"):
    font = get_font(text, size)
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    dx, dy = 0, 0
    if anchor == "mt":
        dx, dy = -tw // 2, 0
    elif anchor == "mm":
        dx, dy = -tw // 2, -th // 2
    elif anchor == "rt":
        dx, dy = -tw, 0
    d.text((x + dx - bbox[0], y + dy - bbox[1]), text, font=font, fill=fill)


def draw_pixel_shadow_rect(d, box, fill, radius=6, border=None, border_width=2):
    x1, y1, x2, y2 = box
    d.rounded_rectangle([x1 + 4, y1 + 4, x2 + 4, y2 + 4], radius=radius, fill=SHADOW_RGBA)
    d.rounded_rectangle(box, radius=radius, fill=fill)
    if border:
        d.rounded_rectangle(box, radius=radius, outline=border, width=border_width)


def draw_popup_mock(d, x, y, w, h):
    draw_pixel_shadow_rect(d, [x, y, x + w, y + h], PANEL, radius=16, border=rgba(PRIMARY, 0.7), border_width=2)

    cx = x + w // 2
    dot_r = 5
    for i, col in enumerate(SWATCHES[:3]):
        dx = (i - 1) * 16
        d.rounded_rectangle([cx + dx - dot_r, y + 16 - dot_r, cx + dx + dot_r, y + 16 + dot_r],
                            radius=dot_r, fill=col, outline=TEXT, width=1)
    draw_text(d, cx, y + 34, "TinyPalette", 10, TEXT, anchor="mt")

    py = y + 58
    ph = 70
    draw_pixel_shadow_rect(d, [x + 20, py, x + w - 20, py + ph], DEMO, radius=8,
                           border=rgba(PRIMARY, 0.7), border_width=2)

    hy = py + ph + 14
    rh = 38
    draw_pixel_shadow_rect(d, [x + 20, hy, x + w - 20, hy + rh], PANEL, radius=6,
                           border=rgba(PRIMARY, 0.7), border_width=2)
    draw_text(d, x + 34, hy + 13, "#", 12, TEXT_SOFT)
    draw_text(d, x + 56, hy + 13, "E8A0BF", 12, TEXT)

    row_y = hy + rh + 10
    row_h = 44
    gap = 8
    labels = [("HEX", "#E8A0BF"), ("RGB", DEMO_RGB), ("HSL", DEMO_HSL)]
    for i, (label, value) in enumerate(labels):
        ry = row_y + i * (row_h + gap)
        draw_pixel_shadow_rect(d, [x + 20, ry, x + w - 20, ry + row_h], PANEL, radius=6,
                               border=rgba(PRIMARY, 0.5), border_width=2)
        draw_text(d, x + 34, ry + 16, label, 10, TEXT_SOFT)
        draw_text(d, x + w - 34, ry + 16, value, 9, TEXT, anchor="rt")

    by = row_y + 3 * (row_h + gap) + 4
    bw = w - 40
    bh = 32
    draw_pixel_shadow_rect(d, [x + 20, by, x + 20 + bw, by + bh], PRIMARY_DARK, radius=6)
    draw_text(d, x + 20 + bw // 2, by + 10, "Copy CSS", 11, "#FFFFFF", anchor="mt")

    sy = by + bh + 12
    sw = 34
    gap_s = 12
    start_x = x + (w - (4 * sw + 3 * gap_s)) // 2
    for i, col in enumerate(SWATCHES):
        sx = start_x + i * (sw + gap_s)
        draw_pixel_shadow_rect(d, [sx, sy, sx + sw, sy + sw], col, radius=4,
                               border=rgba(PRIMARY, 0.6), border_width=2)


def draw_440():
    W, H = 440, 280
    img = Image.new("RGBA", (W, H), hex_to_rgb(BG) + (255,))
    d = ImageDraw.Draw(img)
    cx = W // 2

    icon = Image.open(ICON_PATH).convert("RGBA")
    img.paste(icon, (cx - icon.width // 2, 55), icon)

    draw_text(d, cx, 120, "TinyPalette", 24, TEXT, anchor="mt")
    draw_text(d, cx, 154, "Pixel color picker", 10, TEXT_SOFT, anchor="mt")
    draw_text(d, cx, 175, "像素调色伙伴", 12, TEXT_SOFT, anchor="mt")

    sw = 20
    gap = 10
    start_x = cx - (4 * sw + 3 * gap) // 2
    sy = 205
    for i, col in enumerate(SWATCHES):
        sx = start_x + i * (sw + gap)
        draw_pixel_shadow_rect(d, [sx, sy, sx + sw, sy + sw], col, radius=4,
                               border=rgba(PRIMARY, 0.7), border_width=2)

    bw, bh = 190, 28
    bx, by = cx - bw // 2, 240
    draw_pixel_shadow_rect(d, [bx, by, bx + bw, by + bh], PRIMARY_DARK, radius=8)
    draw_text(d, cx, by + 8, "Try It Now · 立即体验", 10, "#FFFFFF", anchor="mt")

    out_path = os.path.join(OUT_DIR, "440x280.png")
    img.convert("RGB").save(out_path, "PNG")
    print("Saved", out_path)


def draw_1400():
    W, H = 1400, 560
    img = Image.new("RGBA", (W, H), hex_to_rgb(BG) + (255,))
    d = ImageDraw.Draw(img)

    lx = 120
    draw_text(d, lx, 175, "TinyPalette", 48, TEXT)
    draw_text(d, lx, 250, "A tiny pixel-style color companion", 18, TEXT_SOFT)
    draw_text(d, lx, 280, "小巧可爱的像素风调色伙伴", 16, TEXT_SOFT)

    chips = [
        ("HEX → RGB / HSL", "HEX 自动转换"),
        ("Copy CSS", "一键复制"),
        ("Custom Theme", "随心换色"),
    ]
    chip_w, chip_h = 190, 58
    chip_gap = 16
    cy = 325
    for i, (en, zh) in enumerate(chips):
        cx = lx + i * (chip_w + chip_gap)
        draw_pixel_shadow_rect(d, [cx, cy, cx + chip_w, cy + chip_h], PANEL, radius=8,
                               border=rgba(PRIMARY, 0.6), border_width=2)
        draw_text(d, cx + chip_w // 2, cy + 12, en, 11, TEXT, anchor="mt")
        draw_text(d, cx + chip_w // 2, cy + 34, zh, 10, TEXT_SOFT, anchor="mt")

    bw, bh = 280, 44
    bx, by = lx, 420
    draw_pixel_shadow_rect(d, [bx, by, bx + bw, by + bh], PRIMARY_DARK, radius=10)
    draw_text(d, bx + bw // 2, by + 14, "Add to Chrome · 添加到 Chrome", 12, "#FFFFFF", anchor="mt")

    mw, mh = 320, 400
    mx = W - mw - 140
    my = (H - mh) // 2
    draw_popup_mock(d, mx, my, mw, mh)

    out_path = os.path.join(OUT_DIR, "1400x560.png")
    img.convert("RGB").save(out_path, "PNG")
    print("Saved", out_path)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    draw_440()
    draw_1400()
    print("Done.")
