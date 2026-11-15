#!/usr/bin/env python3
"""
Build the README title art: the GRAY TIMER wordmark (sources/pop/processed/wordmark.png)
with "A watch made by Hari Rajesh" under it in the Prince of Persia in-game font
(../myfonts/PrinceOfPersia1x7b.h), both on one pixel grid and centred on each other.

Usage:
    python3 generate_readme_banner.py [photo]
    -> ../docs/pics/banner_light.png (black text) and banner_dark.png (white text),
       transparent, for GitHub's light and dark themes
    -> ../docs/pics/hero.jpg: the title in white over the dark top of a photo
       (default ../raw_images/highlights/IMG_5817.jpeg), if the photo is there,
       and hero_crop.jpg: the same cut off a little below the watch, for the README
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from render_watchface import GFXFont

HERE = Path(__file__).parent
CREDIT = "A watch made by Hari Rajesh"
GAP = 4      # rows between the wordmark and the credit
SCALE = 3    # screen pixels per art pixel

HERO_PHOTO = HERE.parent / "raw_images" / "highlights" / "IMG_5817.jpeg"
HERO_GAP = 6      # rows between the wordmark and the credit on the photo
HERO_SCALE = 4    # photo pixels per art pixel, before HERO_REDUCE
HERO_TOP = 230    # photo rows above the wordmark, before HERO_REDUCE
HERO_REDUCE = 2   # shrink the finished photo by this much for the README
HERO_CROP = 2160  # photo rows kept in hero_crop.jpg, before HERO_REDUCE


def title_alpha(gap, scale):
    """The wordmark and credit as an L mask (255 = ink), each art pixel scale x scale."""
    mark = Image.open(HERE / "sources" / "pop" / "processed" / "wordmark.png").convert("L")
    mark = mark.crop(mark.getbbox())
    font = GFXFont(str(HERE.parent / "myfonts" / "PrinceOfPersia1x7b.h"))
    x1, y1, w, h = font.get_text_bounds(CREDIT)
    width = max(mark.width, w)
    ink = Image.new("1", (width, mark.height + gap + h), 1)
    ink.paste(0, ((width - mark.width) // 2, 0), mark.point(lambda v: 255 if v > 128 else 0).convert("1"))
    font.render_text(CREDIT, (width - w) // 2 - x1, mark.height + gap - y1, ImageDraw.Draw(ink))
    return ink.convert("L").point(lambda v: 255 - v).resize((width * scale, ink.height * scale), Image.NEAREST)


def build_hero(photo_path):
    photo = ImageOps.exif_transpose(Image.open(photo_path)).convert("RGB")
    alpha = title_alpha(HERO_GAP, HERO_SCALE)
    # keep the art grid on multiples of HERO_REDUCE so each art pixel stays a sharp square
    x = (photo.width - alpha.width) // 2 // HERO_REDUCE * HERO_REDUCE
    photo.paste((255, 255, 255), (x, HERO_TOP, x + alpha.width, HERO_TOP + alpha.height), alpha)
    for name, rows in (("hero.jpg", photo.height), ("hero_crop.jpg", HERO_CROP)):
        out = photo.crop((0, 0, photo.width, rows)).reduce(HERO_REDUCE)
        out.save(HERE.parent / "docs" / "pics" / name, quality=88, optimize=True, progressive=True)
        print("wrote docs/pics/" + name, out.size)


def build():
    alpha = title_alpha(GAP, SCALE)
    for name, colour in (("banner_light.png", (0, 0, 0)), ("banner_dark.png", (255, 255, 255))):
        out = Image.new("RGBA", alpha.size, colour + (0,))
        out.putalpha(alpha)
        out.save(HERE.parent / "docs" / "pics" / name)
        print("wrote docs/pics/" + name, out.size)


if __name__ == "__main__":
    build()
    photo = Path(sys.argv[1]) if len(sys.argv) > 1 else HERO_PHOTO
    if photo.exists():
        build_hero(photo)
    else:
        print("no photo at", photo, "- skipped docs/pics/hero.jpg")
