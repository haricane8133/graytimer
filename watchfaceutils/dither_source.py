#!/usr/bin/env python3
"""
Turn a colour render into a pre-dithered 1-bit source for Canvas.bitmap() in
generate_geometric.py: transparent (or plain white) background removed, trimmed,
scaled to fit WxH, then Floyd-Steinberg dithered at that final size. Dither
patterns must not be resampled afterwards, so W and H are the face's box size.

Usage:
    python3 dither_source.py in.png out.png 192 132 [--gamma 0.8] [--contrast 1.2] [--luma 0.5]
"""

import argparse

from PIL import Image, ImageChops, ImageEnhance, ImageOps


def dither(src, dst, w, h, gamma=1.0, contrast=1.0, luma=1.0, crop=None):
    im = Image.open(src).convert("RGBA")
    if crop:
        im = im.crop((round(crop[0] * im.width), round(crop[1] * im.height),
                      round(crop[2] * im.width), round(crop[3] * im.height)))
    alpha = im.getchannel("A")
    flat = Image.new("RGBA", im.size, "white")
    flat.alpha_composite(im)
    gray = flat.convert("L")

    # Subject = opaque and not near-white (covers both alpha renders and white-background art)
    ink = ImageChops.multiply(alpha.point(lambda v: 255 if v > 40 else 0), gray.point(lambda v: 255 if v < 245 else 0))
    if luma < 1.0:
        # Blend luma with HSV value (brightest channel): saturated reds/purples
        # stay light instead of going near-black, while ink outlines stay black.
        gray = Image.blend(flat.convert("RGB").convert("HSV").getchannel("V"), gray, luma)
    gray, alpha = gray.crop(ink.getbbox()), alpha.crop(ink.getbbox())

    sc = min(w / gray.width, h / gray.height)
    size = (max(1, round(gray.width * sc)), max(1, round(gray.height * sc)))
    gray = gray.resize(size, Image.LANCZOS)
    alpha = alpha.resize(size, Image.LANCZOS)

    gray = ImageOps.autocontrast(gray, cutoff=1)
    if contrast != 1.0:
        gray = ImageEnhance.Contrast(gray).enhance(contrast)
    if gamma != 1.0:
        gray = gray.point(lambda v: round(255 * (v / 255) ** gamma))
    gray = Image.composite(gray, Image.new("L", size, 255), alpha.point(lambda v: 255 if v > 100 else 0))
    gray.convert("1", dither=Image.FLOYDSTEINBERG).save(dst)
    print(f"wrote {dst} {size[0]}x{size[1]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("w", type=int)
    ap.add_argument("h", type=int)
    ap.add_argument("--gamma", type=float, default=1.0, help="<1 lightens mid-tones, >1 darkens")
    ap.add_argument("--contrast", type=float, default=1.0)
    ap.add_argument("--luma", type=float, default=1.0,
                    help="weight of luma vs brightest channel; <1 keeps saturated colours light")
    ap.add_argument("--crop", type=float, nargs=4, metavar=("L", "T", "R", "B"),
                    help="crop the source first, as fractions of its size")
    a = ap.parse_args()
    dither(a.src, a.dst, a.w, a.h, a.gamma, a.contrast, a.luma, a.crop)
