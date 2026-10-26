#!/usr/bin/env python3
"""
Convert a TTF/OTF font to an Adafruit GFX font header (same layout as
Adafruit-GFX's fontconvert: 141 DPI, 1-bit glyph bitmaps, chars 0x20-0x7E).

Usage:
    python3 ttf_to_gfx.py Orbitron.ttf 20 --name Orbitron_Bold --weight 700
    -> ../myfonts/Orbitron_Bold20pt7b.h defining `Orbitron_Bold20pt7b`
    python3 ttf_to_gfx.py Horizon.ttf 13 20 --name Horizon --fallback Orbitron.ttf --fallback-weight 400 \\
        --fallback-scale 0.73 --caps-from-lowercase
    -> Horizon's letters with Orbitron's digits and punctuation
"""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DPI = 141
FIRST, LAST = 0x20, 0x7E


def load(ttf, px, weight=None):
    font = ImageFont.truetype(str(ttf), int(round(px)))
    if weight is not None:
        try:
            font.set_variation_by_axes([weight])
        except OSError:
            pass  # not a variable font
    return font


def has_glyph(font, ch):
    """False if the font draws `ch` as its .notdef box (or not at all)"""
    notdef = font.getmask("\uffff")
    m = font.getmask(ch)
    return m.size != notdef.size or bytes(m) != bytes(notdef)


def convert(ttf, pt, name, weight=None, out_dir=Path(__file__).parent.parent / "myfonts",
            fallback=None, fallback_weight=None, fallback_scale=1.0, caps_from_lowercase=False):
    px = pt * DPI / 72
    primary = load(ttf, px, weight)
    secondary = load(fallback, px * fallback_scale, fallback_weight) if fallback else None

    bitmaps, glyphs = bytearray(), []
    for code in range(FIRST, LAST + 1):
        ch = chr(code)
        if caps_from_lowercase and ch.isupper():
            ch = ch.lower()  # e.g. Horizon's capitals have stems that reach into the next line
        font = primary
        if secondary and ch != " " and not has_glyph(primary, ch):
            font = secondary  # e.g. a letters-only display font borrowing digits and punctuation
        l, t, r, b = font.getbbox(ch, anchor="ls")
        w, h = r - l, b - t
        adv = int(round(font.getlength(ch)))
        if w <= 0 or h <= 0 or ch == " ":
            glyphs.append((len(bitmaps), 0, 0, adv, 0, 0))
            continue
        img = Image.new("L", (w, h), 0)
        ImageDraw.Draw(img).text((-l, -t), ch, font=font, fill=255, anchor="ls")
        px_ = img.load()
        offset = len(bitmaps)
        bit, cur = 0, 0
        for y in range(h):
            for x in range(w):
                cur = (cur << 1) | (1 if px_[x, y] >= 128 else 0)
                bit += 1
                if bit == 8:
                    bitmaps.append(cur); bit, cur = 0, 0
        if bit:
            bitmaps.append(cur << (8 - bit))
        glyphs.append((offset, w, h, adv, l, t))

    ascent, descent = primary.getmetrics()
    y_adv = ascent + descent
    sym = f"{name}{pt}pt7b"

    lines = [f"const uint8_t {sym}Bitmaps[] PROGMEM = {{"]
    for i in range(0, len(bitmaps), 12):
        lines.append("  " + ", ".join(f"0x{v:02X}" for v in bitmaps[i:i + 12]) + ",")
    lines[-1] = lines[-1].rstrip(",")
    lines.append("};\n")
    lines.append(f"const GFXglyph {sym}Glyphs[] PROGMEM = {{")
    for code, (off, w, h, adv, xo, yo) in zip(range(FIRST, LAST + 1), glyphs):
        lines.append(f"  {{ {off:5d}, {w:3d}, {h:3d}, {adv:3d}, {xo:4d}, {yo:4d} }},   // 0x{code:02X} '{chr(code)}'")
    lines[-1] = lines[-1].replace(" },   //", " } }; //")
    lines.append("")
    lines.append(f"const GFXfont {sym} PROGMEM = {{")
    lines.append(f"  (uint8_t  *){sym}Bitmaps,")
    lines.append(f"  (GFXglyph *){sym}Glyphs,")
    lines.append(f"  0x{FIRST:02X}, 0x{LAST:02X}, {y_adv} }};\n")
    lines.append(f"// Approx. {len(bitmaps) + len(glyphs) * 7 + 7} bytes")

    out = Path(out_dir) / f"{sym}.h"
    out.write_text("\n".join(lines) + "\n")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("ttf")
    ap.add_argument("pt", type=int, nargs="+")
    ap.add_argument("--name", required=True, help="symbol prefix, e.g. Orbitron_Bold")
    ap.add_argument("--weight", type=float, help="weight axis value for variable fonts")
    ap.add_argument("--fallback", help="font to take any glyph the main font lacks from")
    ap.add_argument("--fallback-weight", type=float, help="weight axis value for the fallback font")
    ap.add_argument("--fallback-scale", type=float, default=1.0, help="size of the fallback font relative to the main one")
    ap.add_argument("--caps-from-lowercase", action="store_true", help="draw A-Z with the font's a-z shapes")
    a = ap.parse_args()
    for pt in a.pt:
        print("wrote", convert(a.ttf, pt, a.name, a.weight, fallback=a.fallback, fallback_weight=a.fallback_weight,
                               fallback_scale=a.fallback_scale, caps_from_lowercase=a.caps_from_lowercase))
