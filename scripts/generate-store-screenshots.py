#!/usr/bin/env python3
"""Generate TinyPalette Chrome Web Store screenshots (zh + en)."""

import colorsys
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Project paths
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(BASE, "fonts", "PressStart2P-Regular.ttf")
ICON_PATH = os.path.join(BASE, "icons", "icon48.png")
OUT_DIR = os.path.join(BASE, "store-assets", "screenshots")

# Canvas
W, H = 1280, 800

# TinyPalette default theme colors
BG = "#FFF0F5"
PANEL = "#FFFDF9"
PRIMARY = "#E8A0BF"
PRIMARY_DARK = "#C97A9B"
TEXT = "#5A3D4D"
TEXT_SOFT = "#A87E8F"
PLACEHOLDER = "#DCC8D0"
BORDER_STRONG = "rgba(232, 160, 191, 0.85)"
SHADOW = "#5A3D4D1F"

# Demo color
DEMO_HEX = "#E8A0BF"
DEMO_RGB = "232, 160, 191"
DEMO_HSL = "340°, 64%, 77%"


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgba(h, a):
    r, g, b = hex_to_rgb(h)
    return (r, g, b, int(a * 255))


def load_font(size):
    return ImageFont.truetype(FONT_PATH, size)


def load_cn_font(size):
    """Load a system Chinese font; fall back to default if unavailable."""
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",      # Microsoft YaHei
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/simhei.ttf",    # SimHei
        "C:/Windows/Fonts/simsun.ttc",    # SimSun
        "/System/Library/Fonts/PingFang.ttc",  # macOS
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return load_font(size)


def has_cn(text):
    return any("\u4e00" <= c <= "\u9fff" for c in text)


def get_font(text, size):
    return load_cn_font(size) if has_cn(text) else load_font(size)


def draw_rounded_rect(d, xy, radius, fill, outline=None, width=1):
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_pixel_shadow_rect(d, xy, fill, shadow_color, border_color, border_width=2, shadow_offset=(2, 2)):
    """Draw a pixel-style rect: solid shadow offset, then fill, then border."""
    x1, y1, x2, y2 = xy
    ox, oy = shadow_offset
    # shadow
    d.rectangle([x1 + ox, y1 + oy, x2 + ox, y2 + oy], fill=shadow_color)
    # fill
    d.rectangle([x1, y1, x2, y2], fill=fill, outline=border_color, width=border_width)


def text_size(d, text, font):
    bbox = d.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_text(d, x, y, text, size, fill, anchor="lt"):
    """Draw text with auto font selection (pixel for Latin, system for CJK)."""
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


def draw_popup_mockup(img, cx, cy, lang):
    """Draw the pixel-style TinyPalette popup centered at (cx, cy)."""
    d = ImageDraw.Draw(img)

    # Dimensions (2x scale of real popup)
    pw, ph = 400, 540
    px, py = cx - pw // 2, cy - ph // 2

    # Labels / values based on language
    if lang == "zh":
        brand = "TinyPalette"
        copy_css = "复制 CSS"
        labels = {"HEX": "HEX", "RGB": "RGB", "HSL": "HSL"}
        toast_msg = "已复制！"
    else:
        brand = "TinyPalette"
        copy_css = "Copy CSS"
        labels = {"HEX": "HEX", "RGB": "RGB", "HSL": "HSL"}
        toast_msg = "Copied!"

    # --- popup background shadow + panel ---
    draw_pixel_shadow_rect(d, [px, py, px + pw, py + ph], PANEL, SHADOW, TEXT, border_width=3)

    # --- header ---
    header_y = py + 24
    # brand dot
    d.rectangle([cx - 60, header_y, cx - 40, header_y + 20], fill=PRIMARY, outline=TEXT, width=3)
    # brand text
    draw_text(d, cx, header_y + 2, brand, 16, TEXT, anchor="mt")
    # lang toggle diamond
    d.text((cx + 60, header_y + 2), "◆", font=load_font(12), fill=PRIMARY_DARK)

    # --- input row ---
    row_y = header_y + 50
    rw, rh = 360, 52
    rx = cx - rw // 2
    draw_pixel_shadow_rect(d, [rx, row_y, rx + rw, row_y + rh], PANEL, SHADOW, PRIMARY_DARK, border_width=2)
    # hash
    draw_text(d, rx + 14, row_y + 18, "#", 14, TEXT_SOFT)
    # hex value
    draw_text(d, rx + 36, row_y + 18, "E8A0BF", 14, TEXT)
    # color picker swatch
    d.rectangle([rx + rw - 52, row_y + 12, rx + rw - 24, row_y + 40], fill=PRIMARY, outline=TEXT, width=2)
    # copy icon (simplified as two small rects)
    d.rectangle([rx + rw - 22, row_y + 12, rx + rw - 6, row_y + 28], outline=TEXT, width=2)
    d.rectangle([rx + rw - 30, row_y + 20, rx + rw - 14, row_y + 36], outline=TEXT, width=2)

    # --- info rows ---
    row_h = 58
    gap = 10
    start_y = row_y + rh + gap
    for i, key in enumerate(["HEX", "RGB", "HSL"]):
        y = start_y + i * (row_h + gap)
        draw_pixel_shadow_rect(d, [rx, y, rx + rw, y + row_h], PANEL, SHADOW, PRIMARY_DARK, border_width=2)
        # label
        draw_text(d, rx + 14, y + 20, labels[key], 12, TEXT_SOFT)
        # value
        val = DEMO_HEX if key == "HEX" else DEMO_RGB if key == "RGB" else DEMO_HSL
        draw_text(d, rx + 70, y + 20, val, 11, TEXT)
        # copy icon
        d.rectangle([rx + rw - 28, y + 16, rx + rw - 10, y + 32], outline=TEXT, width=2)
        d.rectangle([rx + rw - 36, y + 24, rx + rw - 18, y + 40], outline=TEXT, width=2)

    # --- copy css button ---
    btn_y = start_y + 3 * (row_h + gap) + 8
    draw_pixel_shadow_rect(d, [rx, btn_y, rx + rw, btn_y + 46], PRIMARY, SHADOW, TEXT, border_width=2)
    draw_text(d, cx, btn_y + 16, copy_css, 12, "#FFFFFF", anchor="mt")

    # --- color picker panel preview (open) ---
    panel_y = btn_y + 46 + 14
    ph_h = 160
    draw_pixel_shadow_rect(d, [rx, panel_y, rx + rw, panel_y + ph_h], PANEL, SHADOW, PRIMARY_DARK, border_width=2)

    # SV canvas gradient block
    sv_y = panel_y + 12
    sv_h = 86
    # simulate gradient: white->primary horizontally, transparent->black vertically
    sv_img = Image.new("RGBA", (rw - 24, sv_h))
    sv_d = ImageDraw.Draw(sv_img)
    base_rgb = hex_to_rgb(PRIMARY)
    for x in range(sv_img.width):
        ratio = x / max(sv_img.width - 1, 1)
        r = int(255 + (base_rgb[0] - 255) * ratio)
        g = int(255 + (base_rgb[1] - 255) * ratio)
        b = int(255 + (base_rgb[2] - 255) * ratio)
        sv_d.line([(x, 0), (x, sv_h)], fill=(r, g, b))
    for y in range(sv_h):
        alpha = int(255 * (y / max(sv_h - 1, 1)))
        overlay = Image.new("RGBA", (rw - 24, 1), (0, 0, 0, alpha))
        sv_img.paste(overlay, (0, y), overlay)
    img.paste(sv_img, (rx + 12, sv_y), sv_img)
    d.rectangle([rx + 12, sv_y, rx + rw - 12, sv_y + sv_h], outline=TEXT, width=2)

    # hue bar
    hue_y = sv_y + sv_h + 10
    hue_h = 18
    hue_img = Image.new("RGBA", (rw - 24, hue_h))
    hue_d = ImageDraw.Draw(hue_img)
    for x in range(hue_img.width):
        hue = int(360 * x / max(hue_img.width - 1, 1))
        r, g, b = colorsys.hls_to_rgb(hue / 360.0, 0.5, 1.0)
        hue_d.line([(x, 0), (x, hue_h)], fill=(int(r * 255), int(g * 255), int(b * 255)))
    img.paste(hue_img, (rx + 12, hue_y), hue_img)
    d.rectangle([rx + 12, hue_y, rx + rw - 12, hue_y + hue_h], outline=TEXT, width=2)

    # picker footer
    foot_y = hue_y + hue_h + 10
    # preview dot
    d.rectangle([rx + 14, foot_y, rx + 40, foot_y + 26], fill=PRIMARY, outline=TEXT, width=2)
    # hex input
    d.rectangle([rx + 50, foot_y, rx + 150, foot_y + 26], fill=PANEL, outline=PRIMARY_DARK, width=2)
    draw_text(d, rx + 58, foot_y + 7, "E8A0BF", 10, TEXT)
    # OK button
    d.rectangle([rx + 160, foot_y, rx + 220, foot_y + 26], fill=PRIMARY, outline=TEXT, width=2)
    ok_text = "确定" if lang == "zh" else "OK"
    draw_text(d, rx + 190, foot_y + 8, ok_text, 10, "#FFFFFF", anchor="mt")

    # --- toast ---
    toast_w, toast_h = 140, 34
    toast_x, toast_y = cx - toast_w // 2, py + ph - 50
    d.rectangle([toast_x, toast_y, toast_x + toast_w, toast_y + toast_h], fill=TEXT, outline=TEXT, width=2)
    draw_text(d, cx, toast_y + 10, toast_msg, 10, "#FFFFFF", anchor="mt")

    # --- toolbar hint above popup ---
    hint = "点击工具栏图标打开" if lang == "zh" else "Click the toolbar icon to open"
    draw_text(d, cx, py - 28, hint, 10, TEXT_SOFT, anchor="mt")


def draw_toolbar(img):
    """Draw a minimal Chrome toolbar at the top with the TinyPalette icon."""
    d = ImageDraw.Draw(img)
    # toolbar bar
    d.rectangle([0, 0, W, 56], fill="#DEE1E6", outline="#C7CBD1", width=1)
    # address bar
    d.rounded_rectangle([120, 14, W - 180, 42], radius=12, fill="#FFFFFF", outline="#C7CBD1", width=1)
    # extension icons area (right side)
    icon_x = W - 160
    icon_y = 10
    try:
        icon = Image.open(ICON_PATH).convert("RGBA")
        icon = icon.resize((32, 32), Image.NEAREST)
        img.paste(icon, (icon_x, icon_y), icon)
    except Exception:
        d.rectangle([icon_x, icon_y, icon_x + 32, icon_y + 32], fill=PRIMARY, outline=TEXT, width=2)


def draw_background(img):
    d = ImageDraw.Draw(img)
    # soft pastel gradient-ish fill using theme tint
    d.rectangle([0, 0, W, H], fill=BG)
    # decorative blurred color blobs
    blob1 = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blob1)
    bd.ellipse([0, 0, 400, 400], fill=rgba(PRIMARY, 0.22))
    blob1 = blob1.filter(ImageFilter.GaussianBlur(radius=60))
    img.paste(blob1, (80, 120), blob1)

    blob2 = Image.new("RGBA", (320, 320), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blob2)
    bd.ellipse([0, 0, 320, 320], fill=(201, 182, 232, int(0.18 * 255)))
    blob2 = blob2.filter(ImageFilter.GaussianBlur(radius=50))
    img.paste(blob2, (W - 360, H - 380), blob2)


def generate(lang, filename):
    img = Image.new("RGB", (W, H), BG)
    draw_background(img)
    draw_toolbar(img)
    draw_popup_mockup(img, W // 2 + 180, H // 2 + 30, lang)

    # Tagline text on the left
    d = ImageDraw.Draw(img)
    if lang == "zh":
        title = "TinyPalette"
        tagline = "小巧可爱的像素风调色伙伴"
        feats = [
            "输入 HEX 即时预览",
            "自动转换 RGB / HSL",
            "一键复制 CSS 代码"
        ]
    else:
        title = "TinyPalette"
        tagline = "A tiny pixel-style color companion"
        feats = [
            "Enter HEX to preview",
            "Auto-convert RGB / HSL",
            "One-click copy CSS"
        ]

    draw_text(d, 120, 200, title, 32, TEXT)
    draw_text(d, 120, 248, tagline, 14, TEXT_SOFT)

    y = 310
    for feat in feats:
        # small dot
        d.rectangle([120, y + 4, 132, y + 16], fill=PRIMARY, outline=TEXT, width=2)
        draw_text(d, 146, y, feat, 12, TEXT)
        y += 34

    out_path = os.path.join(OUT_DIR, "zh_CN" if lang == "zh" else "en", filename)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG")
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    generate("en", "screenshot1.png")
    generate("zh", "screenshot1.png")
    print("Done.")
