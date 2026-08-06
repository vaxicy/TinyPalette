#!/usr/bin/env python3
"""Capture TinyPalette Chrome Web Store screenshots via headless Chromium (Playwright).

Renders a real browser mockup (Chrome toolbar + pixel popup with picker open) so the
pixel font is rendered by the browser itself, avoiding the 16px PIL bitmap artifacts.
Outputs 1280x800 PNGs, one per language, with the picker panel open and a toast shown.
"""
import base64
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parent.parent
ICON = BASE / "icons" / "icon48.png"
MOCKUP = BASE / "scripts" / "screenshot-mockup.html"
OUT_DIR = BASE / "store-assets" / "screenshots"
W, H = 1280, 800


def main():
    icon_b64 = base64.b64encode(ICON.read_bytes()).decode("ascii")
    icon_src = f"data:image/png;base64,{icon_b64}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
        page.goto(MOCKUP.as_uri())
        page.evaluate(f"(src) => {{ document.getElementById('extIcon').src = src; }}", icon_src)

        for lang, folder in (("en", "en"), ("zh", "zh_CN")):
            page.evaluate(f"(l) => window.applyLang(l)", lang)
            out = OUT_DIR / folder / "screenshot1.png"
            out.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": W, "height": H})
            print(f"Saved: {out}")

        browser.close()
    print("Done.")


if __name__ == "__main__":
    main()
