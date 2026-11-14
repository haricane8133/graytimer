#!/usr/bin/env python3
"""
Build the README title banner: the GRAY TIMER wordmark (sources/pop/processed/wordmark.png)
with "A watch made by Hari Rajesh" under it in the Prince of Persia in-game font
(../myfonts/PrinceOfPersia1x7b.h), both on one pixel grid and centred on each other.

Usage:
    python3 generate_readme_banner.py
    -> ../docs/pics/banner_light.png (black text) and banner_dark.png (white text),
       transparent, for GitHub's light and dark themes
"""

from pathlib import Path

from PIL import Image, ImageDraw

from render_watchface import GFXFont

HERE = Path(__file__).parent
CREDIT = "A watch made by Hari Rajesh"
GAP = 4      # rows between the wordmark and the credit
SCALE = 3    # screen pixels per art pixel


def build():
    mark = Image.open(HERE / "sources" / "pop" / "processed" / "wordmark.png").convert("L")
    mark = mark.crop(mark.getbbox())
    font = GFXFont(str(HERE.parent / "myfonts" / "PrinceOfPersia1x7b.h"))
    x1, y1, w, h = font.get_text_bounds(CREDIT)
    width = max(mark.width, w)
    ink = Image.new("1", (width, mark.height + GAP + h), 1)
    ink.paste(0, ((width - mark.width) // 2, 0), mark.point(lambda v: 255 if v > 128 else 0).convert("1"))
    font.render_text(CREDIT, (width - w) // 2 - x1, mark.height + GAP - y1, ImageDraw.Draw(ink))
    alpha = ink.convert("L").point(lambda v: 255 - v).resize((width * SCALE, ink.height * SCALE), Image.NEAREST)
    for name, colour in (("banner_light.png", (0, 0, 0)), ("banner_dark.png", (255, 255, 255))):
        out = Image.new("RGBA", alpha.size, colour + (0,))
        out.putalpha(alpha)
        out.save(HERE.parent / "docs" / "pics" / name)
        print("wrote docs/pics/" + name, out.size)


if __name__ == "__main__":
    build()
