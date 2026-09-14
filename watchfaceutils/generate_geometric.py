#!/usr/bin/env python3
"""
Procedurally generate geometric watchfaces (no source artwork needed).

Each face is drawn with PIL at 4x supersampling, thresholded to pure 1-bit
(no dithering - it looks muddy on the 200x200 e-paper), and written to
../mywatchfaces/<name>.h in the same format image2cpp produces.

Usage:
    python3 generate_geometric.py            # write all faces
    python3 generate_geometric.py tie orion  # write only these
"""

import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = 200          # display size
SS = 4           # supersample factor
OUT_DIR = Path(__file__).parent.parent / "mywatchfaces"
SRC_DIR = Path(__file__).parent / "sources"


# ---------------------------------------------------------------------------
# Drawing helpers (all coordinates in 200px display space)
# ---------------------------------------------------------------------------

class Canvas:
    def __init__(self, black_bg=False):
        self.black_bg = black_bg
        self.img = Image.new("L", (W * SS, W * SS), 0 if black_bg else 255)
        self.d = ImageDraw.Draw(self.img)
        self.ink = 255 if black_bg else 0
        self.paper = 0 if black_bg else 255

    def _s(self, v):
        return v * SS

    def line(self, p1, p2, width=2, color=None):
        c = self.ink if color is None else color
        self.d.line([(p1[0] * SS, p1[1] * SS), (p2[0] * SS, p2[1] * SS)],
                    fill=c, width=int(width * SS))

    def polyline(self, pts, width=2, color=None, closed=False):
        c = self.ink if color is None else color
        pts = [(x * SS, y * SS) for x, y in pts]
        if closed:
            pts.append(pts[0])
        self.d.line(pts, fill=c, width=int(width * SS), joint="curve")

    def polygon(self, pts, fill=None, outline=None, width=2):
        pts = [(x * SS, y * SS) for x, y in pts]
        if fill is not None:
            self.d.polygon(pts, fill=fill)
        if outline is not None:
            self.d.line(pts + [pts[0]], fill=outline, width=int(width * SS), joint="curve")

    def circle(self, c, r, width=2, fill=None, outline=None):
        box = [(c[0] - r) * SS, (c[1] - r) * SS, (c[0] + r) * SS, (c[1] + r) * SS]
        if fill is not None:
            self.d.ellipse(box, fill=fill)
        if outline is not None:
            self.d.ellipse(box, outline=outline, width=int(width * SS))

    def ellipse(self, c, rx, ry, width=2, fill=None, outline=None):
        box = [(c[0] - rx) * SS, (c[1] - ry) * SS, (c[0] + rx) * SS, (c[1] + ry) * SS]
        if fill is not None:
            self.d.ellipse(box, fill=fill)
        if outline is not None:
            self.d.ellipse(box, outline=outline, width=int(width * SS))

    def arc(self, c, r, a0, a1, width=2, color=None):
        """Arc of a circle, angles in degrees clockwise from +x (PIL convention)."""
        box = [(c[0] - r) * SS, (c[1] - r) * SS, (c[0] + r) * SS, (c[1] + r) * SS]
        self.d.arc(box, a0, a1, fill=self.ink if color is None else color, width=int(width * SS))

    def rrect(self, p0, p1, rad, width=2, fill=None, outline=None):
        box = [p0[0] * SS, p0[1] * SS, p1[0] * SS, p1[1] * SS]
        if fill is not None:
            self.d.rounded_rectangle(box, radius=rad * SS, fill=fill)
        if outline is not None:
            self.d.rounded_rectangle(box, radius=rad * SS, outline=outline, width=int(width * SS))

    def disc(self, c, r, color=None):
        self.circle(c, r, fill=self.ink if color is None else color)

    def ring(self, c, r, width=2, color=None):
        self.circle(c, r, width=width, outline=self.ink if color is None else color)

    def sparkle(self, c, size, color=None, thin=0.22):
        """4-point star (diamond spikes)."""
        col = self.ink if color is None else color
        x, y = c
        t = size * thin
        pts = [(x, y - size), (x + t, y - t), (x + size, y), (x + t, y + t),
               (x, y + size), (x - t, y + t), (x - size, y), (x - t, y - t)]
        self.polygon(pts, fill=col)

    def wedge(self, c, r_in, r_out, a0, a1, color=None):
        col = self.ink if color is None else color
        pts = []
        steps = 12
        for i in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * i / steps)
            pts.append((c[0] + r_out * math.cos(a), c[1] + r_out * math.sin(a)))
        for i in range(steps, -1, -1):
            a = math.radians(a0 + (a1 - a0) * i / steps)
            pts.append((c[0] + r_in * math.cos(a), c[1] + r_in * math.sin(a)))
        self.polygon(pts, fill=col)

    def silhouette(self, path, box, flip=False):
        """Paste a 1-bit silhouette PNG (black = ink) scaled to fit box=(x0,y0,x1,y1)."""
        im = Image.open(path).convert("L")
        if flip:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        bw, bh = box[2] - box[0], box[3] - box[1]
        sc = min(bw / im.width, bh / im.height)
        im = im.resize((int(im.width * sc * SS), int(im.height * sc * SS)), Image.LANCZOS)
        mask = im.point(lambda v: 255 if v < 128 else 0)
        x = int((box[0] + (bw - im.width / SS) / 2) * SS)
        y = int((box[1] + (bh - im.height / SS) / 2) * SS)
        self.img.paste(self.ink, (x, y), mask)

    def text(self, txt, font_path, size, center, index=0):
        """Draw text from a system/TTF font, centred at `center`."""
        f = ImageFont.truetype(font_path, int(size * SS), index=index)
        l, t, r, b = self.d.textbbox((0, 0), txt, font=f)
        self.d.text((center[0] * SS - (l + r) / 2, center[1] * SS - (t + b) / 2), txt, font=f, fill=self.ink)

    def to_bits(self):
        small = self.img.resize((W, W), Image.LANCZOS)
        bw = small.point(lambda v: 0 if v < 128 else 255, "1")
        return bw


def write_header(name, bw, face_cfg):
    """Write mywatchfaces/<name>.h in image2cpp format. bit=1 -> black."""
    px = bw.load()
    data = bytearray()
    for y in range(W):
        for x in range(0, W, 8):
            b = 0
            for i in range(8):
                if px[x + i, y] == 0:
                    b |= 0x80 >> i
            data.append(b)

    lines = []
    for i in range(0, len(data), 16):
        chunk = ", ".join(f"0x{v:02x}" for v in data[i:i + 16])
        lines.append("\t" + chunk + ("," if i + 16 < len(data) else ""))

    arr = f"epd_bitmap_{name}"
    body = "\n".join(lines)
    cfg = "\n".join(f"    {k} = {v};" for k, v in face_cfg)
    text = f"""// '{name}', 200x200px - generated by watchfaceutils/generate_geometric.py
const unsigned char {arr} [] PROGMEM = {{
{body}
}};

// Array of all bitmaps for convenience. (Total bytes used to store images in PROGMEM = {len(data)})
static const int {arr}_allArray_LEN = 1;
static const unsigned char* {arr}_allArray[1] = {{
\t{arr}
}};

struct WatchFace_{name} : public WatchFace {{
  WatchFace_{name}() {{
    bitmap = {arr};
{cfg}
  }}
}};
"""
    out = OUT_DIR / f"{name}.h"
    out.write_text(text)
    return out


# ---------------------------------------------------------------------------
# Faces
# ---------------------------------------------------------------------------

FACES = {}


def face(fn):
    FACES[fn.__name__] = fn
    return fn


@face
def tie():
    """TIE fighter, line art. Time below."""
    c = Canvas()
    cy = 80
    for cx in (36, 164):
        hexa = [(cx, 22), (cx + 16, 44), (cx + 16, 116), (cx, 138), (cx - 16, 116), (cx - 16, 44)]
        c.polygon(hexa, outline=c.ink, width=5)
        for p in hexa:
            c.line((cx, cy), p, width=2.5)
        c.disc((cx, cy), 5)
    # struts
    c.line((52, cy), (76, cy), width=7)
    c.line((124, cy), (148, cy), width=7)
    # cockpit ball + window
    c.disc((100, cy), 27, color=c.paper)
    c.ring((100, cy), 27, width=5)
    c.ring((100, cy), 11, width=3)
    for k in range(8):
        a = math.radians(k * 45)
        c.line((100 + 11 * math.cos(a), cy + 11 * math.sin(a)),
               (100 + 26 * math.cos(a), cy + 26 * math.sin(a)), width=2.5)
    return c, [
        ("layout", 1), ("noAMPM", "true"),
        ("text1x", -1), ("text1y", 74), ("text1font", "&StarJedi_DGRW20pt7b"),
        ("text2x", -1), ("text2y", 91), ("text2font", "&StarJedi_DGRW10pt7b"),
    ]


@face
def deathstar():
    """Death Star: sphere, superlaser dish, equatorial trench. Time inside."""
    c = Canvas()
    R = 90
    c.ring((100, 100), R, width=4)
    c.ring((66, 60), 27, width=3)
    c.ring((66, 60), 15, width=2)
    c.disc((66, 60), 3)
    # trench: two chords clipped to the sphere
    for y in (106, 112):
        half = math.sqrt(R * R - (y - 100) ** 2)
        c.line((100 - half, y), (100 + half, y), width=2)
    return c, [
        ("layout", 1), ("noAMPM", "true"),
        ("text1x", -1), ("text1y", 60), ("text1font", "&StarJedi_DGRW20pt7b"),
        ("text2x", -1), ("text2y", 77), ("text2font", "&StarJedi_DGRW10pt7b"),
    ]


@face
def hallows():
    """Deathly Hallows: triangle, circle, line. Time below."""
    c = Canvas()
    apex, bl, br = (100, 10), (32, 122), (168, 122)
    c.polygon([apex, br, bl], outline=c.ink, width=6)
    base = br[0] - bl[0]
    leg = math.hypot(base / 2, bl[1] - apex[1])
    area = 0.5 * base * (bl[1] - apex[1])
    r = area / ((base + 2 * leg) / 2)
    c.ring((100, bl[1] - r), r, width=6)
    c.line(apex, (100, bl[1]), width=6)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 66), ("text1font", "&HARRYP__20pt7b"),
        ("text2x", -1), ("text2y", 87), ("text2font", "&HARRYP__10pt7b"),
    ]


@face
def prism():
    """Dark Side of the Moon: prism on black, beam in, spectrum out. White text."""
    c = Canvas(black_bg=True)
    apex, bl, br = (100, 38), (46, 130), (154, 130)
    c.polygon([apex, br, bl], outline=c.ink, width=3)

    def left_edge_x(y):
        return apex[0] - (y - apex[1]) / (bl[1] - apex[1]) * (apex[0] - bl[0])

    def right_edge_x(y):
        return apex[0] + (y - apex[1]) / (br[1] - apex[1]) * (br[0] - apex[0])

    entry = (left_edge_x(96), 96)
    c.line((0, 108), entry, width=2)
    exit_ = (right_edge_x(92), 92)
    c.line(entry, exit_, width=2)
    for i in range(6):
        c.line(exit_, (200, 70 + i * 13), width=2)
    return c, [
        ("layout", 0),
        ("text1x", -1), ("text1y", 78),
        ("text1color", "GxEPD_WHITE"), ("text1font", "&CompactaBT20pt7b"),
        ("text2color", "GxEPD_WHITE"), ("text2font", "&CompactaBT10pt7b"),
    ]


@face
def orbit():
    """Concentric orbits with planets; time sits where the sun would be."""
    c = Canvas()
    for r in (62, 78, 94, 110, 126):
        c.ring((100, 100), r, width=1.5)
    planets = [(62, 205, 3.5), (78, 330, 5), (94, 50, 4.5), (110, 140, 6.5), (126, 290, 5.5)]
    for r, ang, size in planets:
        a = math.radians(ang)
        p = (100 + r * math.cos(a), 100 + r * math.sin(a))
        c.disc(p, size)
    # ringed planet on the 4th orbit
    a = math.radians(140)
    p = (100 + 110 * math.cos(a), 100 + 110 * math.sin(a))
    c.polyline([(p[0] - 12, p[1] + 3), (p[0] + 12, p[1] - 3)], width=2)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 41), ("text1font", "&CompactaBT20pt7b"),
        ("text2x", -1), ("text2y", 57), ("text2font", "&CompactaBT10pt7b"),
    ]


@face
def orion():
    """Orion on a black sky. White text at the bottom."""
    c = Canvas(black_bg=True)
    S = {
        "meissa": (100, 14, 2), "betelgeuse": (60, 40, 5), "bellatrix": (140, 38, 4),
        "alnitak": (86, 88, 3), "alnilam": (100, 84, 3), "mintaka": (114, 80, 3),
        "saiph": (76, 128, 3), "rigel": (136, 132, 5),
    }
    edges = [("meissa", "betelgeuse"), ("meissa", "bellatrix"), ("betelgeuse", "alnitak"),
             ("bellatrix", "mintaka"), ("alnitak", "alnilam"), ("alnilam", "mintaka"),
             ("alnitak", "saiph"), ("mintaka", "rigel")]
    for a, b in edges:
        c.line(S[a][:2], S[b][:2], width=1.2)
    # sword
    for p, s in (((98, 96), 1.5), ((97, 104), 2), ((96, 112), 1.5)):
        c.disc(p, s)
    for name, (x, y, s) in S.items():
        c.disc((x, y), s)
        if s >= 4:
            c.sparkle((x, y), s * 2.4, thin=0.16)
    rng = random.Random(7)
    for _ in range(28):
        x, y = rng.uniform(4, 196), rng.uniform(4, 150)
        if min(math.hypot(x - sx, y - sy) for sx, sy, _ in S.values()) > 12:
            c.disc((x, y), rng.choice((0.8, 0.8, 1.2)))
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 72),
        ("text1color", "GxEPD_WHITE"), ("text1font", "&ToughCookiesBold_owZ1d20pt7b"),
        ("text2x", -1), ("text2y", 90),
        ("text2color", "GxEPD_WHITE"), ("text2font", "&ToughCookiesBold_owZ1d10pt7b"),
    ]


@face
def kolam():
    """Kambi (chain) kolam border: dots with loops weaving around them."""
    c = Canvas()
    inset, rad = 13, 22
    lo, hi = inset, W - inset
    # rounded-rect path, sampled by arc length
    straight = (hi - lo) - 2 * rad
    segs = []  # (length, fn(t)->(x,y,nx,ny))
    corners = [((hi - rad, lo + rad), -90), ((hi - rad, hi - rad), 0),
               ((lo + rad, hi - rad), 90), ((lo + rad, lo + rad), 180)]
    lines = [((lo + rad, lo), (1, 0), (0, -1)), ((hi, lo + rad), (0, 1), (1, 0)),
             ((hi - rad, hi), (-1, 0), (0, 1)), ((lo, hi - rad), (0, -1), (-1, 0))]
    for (p0, d, n), (cc, a0) in zip(lines, corners):
        segs.append((straight, lambda t, p0=p0, d=d, n=n: (p0[0] + d[0] * t, p0[1] + d[1] * t, n[0], n[1])))
        arc = math.pi / 2 * rad
        def arcfn(t, cc=cc, a0=a0):
            a = math.radians(a0) + t / rad
            return (cc[0] + rad * math.cos(a), cc[1] + rad * math.sin(a), math.cos(a), math.sin(a))
        segs.append((arc, arcfn))
    total = sum(l for l, _ in segs)
    n_loops = 34
    s = total / n_loops
    amp = 7.5

    def at(t):
        t %= total
        for l, fn in segs:
            if t <= l:
                return fn(t)
            t -= l
        return segs[-1][1](segs[-1][0])

    steps = 1400
    up, dn = [], []
    for i in range(steps + 1):
        t = total * i / steps
        x, y, nx, ny = at(t)
        off = amp * math.sin(math.pi * t / s)
        up.append((x + nx * off, y + ny * off))
        dn.append((x - nx * off, y - ny * off))
    c.polyline(up, width=2)
    c.polyline(dn, width=2)
    for k in range(n_loops):
        x, y, _, _ = at(s * (k + 0.5))
        c.disc((x, y), 1.8)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 36), ("text1font", "&Caveat_VariableFont_wght20pt7b"),
        ("text2x", -1), ("text2y", 56), ("text2font", "&Caveat_VariableFont_wght10pt7b"),
    ]


@face
def vinyl():
    """Record with a label; time on the label."""
    c = Canvas()
    c.disc((100, 100), 97)
    for r in (56, 66, 76, 86, 93):
        c.ring((100, 100), r, width=0.8, color=c.paper)
    c.disc((100, 100), 47, color=c.paper)
    c.ring((100, 100), 44, width=1)
    return c, [
        ("layout", 1), ("noAMPM", "true"),
        ("text1x", -1), ("text1y", 41), ("text1font", "&CompactaBT20pt7b"),
        ("text2x", -1), ("text2y", 59), ("text2font", "&CompactaBT10pt7b"),
    ]


@face
def sunburst():
    """Alternating rays around a clear disc."""
    c = Canvas()
    R = 62
    n = 24
    for k in range(0, n, 2):
        a0 = k * 360 / n - 90
        c.wedge((100, 100), R + 4, 160, a0, a0 + 360 / n)
    c.ring((100, 100), R, width=3)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 40), ("text1font", "&Bootle_4B9l20pt7b"),
        ("text2x", -1), ("text2y", 57), ("text2font", "&Bootle_4B9l10pt7b"),
    ]


@face
def minimal():
    """Pure typography with a double border and a rule."""
    c = Canvas()
    c.polygon([(6, 6), (194, 6), (194, 194), (6, 194)], outline=c.ink, width=2.5)
    c.polygon([(11, 11), (189, 11), (189, 189), (11, 189)], outline=c.ink, width=1)
    c.line((60, 113), (140, 113), width=1.5)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 27), ("text1font", "&ToughCookiesBold_owZ1d30pt7b"),
        ("text2x", -1), ("text2y", 63), ("text2font", "&ToughCookiesBold_owZ1d15pt7b"),
    ]


@face
def moon():
    """Crescent moon and stars. Time below."""
    c = Canvas()
    c.disc((122, 66), 52)
    c.disc((142, 50), 46, color=c.paper)
    for p, s in (((38, 34), 9), ((72, 18), 5), ((26, 92), 6), ((60, 128), 4), ((176, 130), 5), ((150, 118), 3)):
        c.sparkle(p, s)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 74), ("text1font", "&DynaPuff_VariableFont_wdth_wght20pt7b"),
        ("text2x", -1), ("text2y", 90), ("text2font", "&DynaPuff_VariableFont_wdth_wght10pt7b"),
    ]


# ---------------------------------------------------------------------------
# Batch 2
# ---------------------------------------------------------------------------

@face
def glasses():
    """Harry's round glasses and the scar."""
    c = Canvas()
    for cx in (62, 138):
        c.ring((cx, 82), 30, width=5)
    c.line((92, 82), (108, 82), width=4)
    c.line((32, 82), (12, 72), width=4)
    c.line((168, 82), (188, 72), width=4)
    bolt = [(160, 6), (138, 34), (150, 34), (128, 66), (158, 30), (146, 30)]
    c.polygon(bolt, fill=c.ink)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 62), ("text1font", "&HARRYP__20pt7b"),
        ("text2x", -1), ("text2y", 85), ("text2font", "&HARRYP__10pt7b"),
    ]


@face
def snitch():
    """Golden Snitch: ball with a pair of wings."""
    c = Canvas()
    cx, cy, r = 100, 66, 24
    c.ring((cx, cy), r, width=4)
    for dy in (-7, 7):
        half = math.sqrt(r * r - dy * dy)
        c.line((cx - half, cy + dy), (cx + half, cy + dy), width=2)
    c.ring((cx, cy), 6, width=2)

    def wing(sign):
        pts = [(cx + sign * 22, cy - 10), (cx + sign * 50, cy - 34), (cx + sign * 82, cy - 46),
               (cx + sign * 92, cy - 38), (cx + sign * 74, cy - 22), (cx + sign * 88, cy - 18),
               (cx + sign * 68, cy - 4), (cx + sign * 82, cy + 4), (cx + sign * 58, cy + 12),
               (cx + sign * 22, cy + 10)]
        c.polygon(pts, outline=c.ink, width=3)
        c.line((cx + sign * 26, cy - 2), (cx + sign * 70, cy - 26), width=2)
        c.line((cx + sign * 28, cy + 4), (cx + sign * 64, cy - 8), width=2)
    wing(1)
    wing(-1)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 62), ("text1font", "&Neuton_Bold20pt7b"),
        ("text2x", -1), ("text2y", 82), ("text2font", "&Neuton_Bold10pt7b"),
    ]


@face
def lightsaber():
    """Lightsaber along the bottom, time above."""
    c = Canvas()
    y = 162
    # hilt
    c.polygon([(8, y - 9), (58, y - 9), (58, y + 9), (8, y + 9)], fill=c.ink)
    for x in range(14, 50, 8):
        c.line((x, y - 9), (x, y + 9), width=2, color=c.paper)
    c.polygon([(58, y - 12), (68, y - 12), (68, y + 12), (58, y + 12)], fill=c.ink)  # emitter
    # blade with a white core
    c.polygon([(68, y - 6), (190, y - 6), (196, y), (190, y + 6), (68, y + 6)], fill=c.ink)
    c.line((72, y), (188, y), width=2, color=c.paper)
    return c, [
        ("layout", 1), ("noAMPM", "true"),
        ("text1x", -1), ("text1y", 30), ("text1font", "&StarJedi_DGRW20pt7b"),
        ("text2x", -1), ("text2y", 50), ("text2font", "&StarJedi_DGRW10pt7b"),
    ]


@face
def rocket():
    """Tintin-style rocket with checkered skirt and fins."""
    c = Canvas()
    body = [(100, 6), (114, 26), (121, 50), (121, 94), (114, 104), (86, 104), (79, 94), (79, 50), (86, 26)]
    c.polygon(body, outline=c.ink, width=4)
    c.ring((100, 52), 9, width=3)
    # checker skirt
    for row, y0 in enumerate((72, 83)):
        for col, x0 in enumerate((81, 90.5, 100, 109.5)):
            if (row + col) % 2 == 0:
                c.polygon([(x0, y0), (x0 + 9.5, y0), (x0 + 9.5, y0 + 11), (x0, y0 + 11)], fill=c.ink)
    # fins
    c.polygon([(79, 80), (54, 112), (79, 104)], fill=c.ink)
    c.polygon([(121, 80), (146, 112), (121, 104)], fill=c.ink)
    # exhaust
    for x, l in ((93, 10), (100, 16), (107, 10)):
        c.line((x, 106), (x, 106 + l), width=3)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 65), ("text1font", "&BekingBold_1Gqdg20pt7b"),
        ("text2x", -1), ("text2y", 84), ("text2font", "&BekingBold_1Gqdg10pt7b"),
    ]


@face
def cassette():
    """Cassette tape: time above, date on the label."""
    c = Canvas()
    c.polygon([(12, 98), (188, 98), (188, 190), (12, 190)], outline=c.ink, width=4)
    c.polygon([(24, 106), (176, 106), (176, 130), (24, 130)], outline=c.ink, width=2)
    for cx in (64, 136):
        c.ring((cx, 154), 15, width=3)
        for k in range(6):
            a = math.radians(k * 60)
            c.line((cx + 8 * math.cos(a), 154 + 8 * math.sin(a)),
                   (cx + 14 * math.cos(a), 154 + 14 * math.sin(a)), width=2)
    c.polygon([(82, 146), (118, 146), (118, 162), (82, 162)], outline=c.ink, width=2)
    c.line((79, 154), (121, 154), width=1.5)
    c.polygon([(58, 190), (142, 190), (132, 176), (68, 176)], outline=c.ink, width=2)
    for x, y in ((20, 184), (180, 184), (20, 104), (180, 104)):
        c.disc((x, y), 2)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 20), ("text1font", "&Monster_AG20pt7b"),
        ("text2x", -1), ("text2y", 56), ("text2font", "&Monster_AG10pt7b"),
    ]


@face
def equalizer():
    """Equalizer bars along the bottom."""
    c = Canvas()
    heights = [32, 58, 84, 48, 100, 72, 112, 62, 90, 42, 68, 36]
    x = 12
    for h in heights:
        c.polygon([(x, 190 - h), (x + 10, 190 - h), (x + 10, 190), (x, 190)], fill=c.ink)
        for yy in range(190 - h + 6, 190, 7):  # segment gaps
            c.line((x, yy), (x + 10, yy), width=1.5, color=c.paper)
        x += 15
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 8), ("text1font", "&BADABB__20pt7b"),
        ("text2x", -1), ("text2y", 28), ("text2font", "&BADABB__10pt7b"),
    ]


@face
def mandala():
    """Eight-petal lotus frame; time in the centre."""
    c = Canvas()
    cx, cy = 100, 100

    def petal(angle, r1, r2, halfw, width=2.5, fill=None):
        pts = []
        for i in range(21):
            t = i / 20
            r = r1 + (r2 - r1) * t
            pts.append((r, halfw * math.sin(math.pi * t)))
        for i in range(20, -1, -1):
            t = i / 20
            r = r1 + (r2 - r1) * t
            pts.append((r, -halfw * math.sin(math.pi * t)))
        a = math.radians(angle)
        rot = [(cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)) for x, y in pts]
        if fill:
            c.polygon(rot, fill=c.ink)
        else:
            c.polygon(rot, outline=c.ink, width=width)

    for k in range(8):
        petal(k * 45, 60, 98, 15)
    for k in range(8):
        petal(k * 45 + 22.5, 62, 80, 6, fill=True)
    c.ring((cx, cy), 58, width=2)
    for k in range(24):
        a = math.radians(k * 15)
        c.disc((cx + 53 * math.cos(a), cy + 53 * math.sin(a)), 1.5)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 41), ("text1font", "&Helloworld_ovvY020pt7b"),
        ("text2x", -1), ("text2y", 56), ("text2font", "&Helloworld_ovvY010pt7b"),
    ]


@face
def forest():
    """Pine silhouettes along the bottom, stars above."""
    c = Canvas()
    trees = [(16, 64), (44, 92), (72, 58), (100, 104), (128, 74), (156, 96), (184, 62)]
    for x, h in sorted(trees, key=lambda t: -t[1]):  # tall trees behind
        top = 190 - h
        tiers = []
        for tier in range(3):
            y0 = top + tier * h * 0.26
            y1 = top + (tier + 1) * h * 0.33
            w = h * (0.12 + 0.065 * tier)
            tiers.append([(x, y0), (x + w, y1), (x - w, y1)])
        trunk = [(x - 2.5, 190 - h * 0.05), (x + 2.5, 190 - h * 0.05), (x + 2.5, 192), (x - 2.5, 192)]
        for poly in tiers + [trunk]:  # white halo first, so this tree stands off the one behind it
            c.polygon(poly, outline=c.paper, width=3)
        for poly in tiers + [trunk]:
            c.polygon(poly, fill=c.ink)
    c.line((0, 191), (200, 191), width=3)
    for p, s in (((26, 24), 5), ((60, 12), 3), ((150, 18), 6), ((178, 40), 3), ((110, 8), 2.5)):
        c.sparkle(p, s)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 16), ("text1font", "&Neuton_Bold20pt7b"),
        ("text2x", -1), ("text2y", 33), ("text2font", "&Neuton_Bold10pt7b"),
    ]


@face
def dial():
    """Classic dial ring with hour ticks, digital time in the centre."""
    c = Canvas()
    cx, cy, R = 100, 100, 94
    c.ring((cx, cy), R, width=3)
    for k in range(60):
        a = math.radians(k * 6 - 90)
        if k % 15 == 0:
            ln, w = 14, 4
        elif k % 5 == 0:
            ln, w = 9, 2.5
        else:
            ln, w = 4, 1
        c.line((cx + (R - 3) * math.cos(a), cy + (R - 3) * math.sin(a)),
               (cx + (R - 3 - ln) * math.cos(a), cy + (R - 3 - ln) * math.sin(a)), width=w)
    c.disc((cx, cy + 34), 3)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 38), ("text1font", "&Neuton_Bold20pt7b"),
        ("text2x", -1), ("text2y", 55), ("text2font", "&Neuton_Bold10pt7b"),
    ]


@face
def waves():
    """Rolling waves along the bottom with a sun; time in the sky."""
    c = Canvas()
    c.ring((164, 100), 13, width=3)
    for k in range(12):
        a = math.radians(k * 30)
        c.line((164 + 18 * math.cos(a), 100 + 18 * math.sin(a)),
               (164 + 25 * math.cos(a), 100 + 25 * math.sin(a)), width=2.5)
    for i, (base, amp, period, phase) in enumerate(((132, 6, 46, 0), (150, 7, 52, 1.2), (168, 8, 58, 2.6), (186, 6, 50, 0.6))):
        pts = [(x, base + amp * math.sin(2 * math.pi * x / period + phase)) for x in range(-5, 206, 2)]
        c.polyline(pts, width=3 + i * 0.5)
    return c, [
        ("layout", 1),
        ("text1x", 6), ("text1y", 14), ("text1font", "&OctoberTwilight_Ooe615pt7b"),
        ("text2x", 6), ("text2y", 36), ("text2font", "&OctoberTwilight_Ooe610pt7b"),
    ]


# ---------------------------------------------------------------------------
# Batch 3 - clip-art style
# ---------------------------------------------------------------------------

@face
def r2d2():
    """R2-D2 front view."""
    c = Canvas()
    # dome
    c.arc((100, 58), 30, 180, 360, width=4)
    c.line((70, 58), (130, 58), width=3)
    c.ring((108, 40), 6, width=2.5)
    c.disc((108, 40), 2)
    c.ring((92, 48), 3, width=2)
    c.line((84, 36), (96, 30), width=2)
    # body
    c.polygon([(70, 58), (130, 58), (130, 128), (70, 128)], outline=c.ink, width=4)
    c.polygon([(78, 66), (96, 66), (96, 82), (78, 82)], outline=c.ink, width=2)
    c.polygon([(104, 66), (122, 66), (122, 82), (104, 82)], outline=c.ink, width=2)
    for x0 in (78, 106):
        c.polygon([(x0, 92), (x0 + 16, 92), (x0 + 16, 116), (x0, 116)], outline=c.ink, width=2)
        for yy in (98, 104, 110):
            c.line((x0, yy), (x0 + 16, yy), width=1.5)
    # legs
    for x0 in (48, 134):
        c.polygon([(x0, 64), (x0 + 18, 64), (x0 + 18, 130), (x0, 130)], outline=c.ink, width=3.5)
        c.polygon([(x0 + 2, 66), (x0 + 16, 66), (x0 + 16, 76), (x0 + 2, 76)], fill=c.ink)
        c.polygon([(x0 - 4, 130), (x0 + 22, 130), (x0 + 18, 142), (x0, 142)], outline=c.ink, width=3)
    c.polygon([(88, 128), (112, 128), (108, 142), (92, 142)], outline=c.ink, width=3)
    return c, [
        ("layout", 1), ("noAMPM", "true"),
        ("text1x", -1), ("text1y", 74), ("text1font", "&StarJedi_DGRW20pt7b"),
        ("text2x", -1), ("text2y", 91), ("text2font", "&StarJedi_DGRW10pt7b"),
    ]


@face
def falcon():
    """Millennium Falcon, top-down, nose to the right."""
    c = Canvas()
    cx, cy, R = 84, 88, 54
    c.disc((cx, cy), R, color=c.paper)
    c.ring((cx, cy), R, width=4)
    c.ring((cx, cy), 40, width=1.5)
    for k in range(12):
        a = math.radians(k * 30 + 15)
        c.line((cx + 40 * math.cos(a), cy + 40 * math.sin(a)), (cx + 52 * math.cos(a), cy + 52 * math.sin(a)), width=1.5)
    # radar dish
    c.ring((cx - 20, cy - 24), 8, width=2.5)
    c.line((cx - 20, cy - 24), (cx - 10, cy - 32), width=2)
    # mandibles with the notch between them
    for y0 in (cy - 30, cy + 8):
        c.polygon([(cx + 36, y0), (cx + 108, y0), (cx + 108, y0 + 22), (cx + 36, y0 + 22)], fill=c.paper)
        c.polygon([(cx + 36, y0), (cx + 108, y0), (cx + 108, y0 + 22), (cx + 36, y0 + 22)], outline=c.ink, width=3.5)
        c.line((cx + 40, y0 + 11), (cx + 104, y0 + 11), width=1.5)
    c.polygon([(cx + 30, cy - 8), (cx + 110, cy - 8), (cx + 110, cy + 8), (cx + 30, cy + 8)], fill=c.paper)
    c.line((cx + 36, cy - 8), (cx + 36, cy + 8), width=3.5)
    c.line((cx + 36, cy - 8), (cx + 108, cy - 8), width=3.5)
    c.line((cx + 36, cy + 8), (cx + 108, cy + 8), width=3.5)
    # cockpit tube on top, pointing up-right
    a = math.radians(-45)
    p0 = (cx + 34 * math.cos(a), cy + 34 * math.sin(a))
    p1 = (cx + 80 * math.cos(a), cy + 80 * math.sin(a))
    c.line(p0, p1, width=13)
    c.line(p0, p1, width=7, color=c.paper)
    c.disc(p1, 10)
    c.disc(p1, 5, color=c.paper)
    return c, [
        ("layout", 1), ("noAMPM", "true"),
        ("text1x", -1), ("text1y", 75), ("text1font", "&StarJedi_DGRW20pt7b"),
        ("text2x", -1), ("text2y", 91), ("text2font", "&StarJedi_DGRW10pt7b"),
    ]


@face
def hedwig():
    """Owl on a branch."""
    c = Canvas()
    hx, hy = 100, 50
    # ear tufts
    c.polygon([(76, 34), (66, 12), (90, 26)], fill=c.ink)
    c.polygon([(124, 34), (134, 12), (110, 26)], fill=c.ink)
    # body then head
    c.ellipse((100, 104), 34, 42, fill=c.paper, outline=c.ink, width=4)
    c.disc((hx, hy), 30, color=c.paper)
    c.ring((hx, hy), 30, width=4)
    for ex in (86, 114):
        c.ring((ex, hy - 2), 11, width=3)
        c.disc((ex + 1, hy - 1), 4)
    c.polygon([(94, 60), (106, 60), (100, 72)], fill=c.ink)
    # wings
    c.polyline([(68, 92), (62, 118), (70, 142)], width=3)
    c.polyline([(132, 92), (138, 118), (130, 142)], width=3)
    # belly feathers
    for row, y in enumerate((96, 110, 124)):
        for x in range(88 - (row % 2) * 6, 118, 12):
            c.polyline([(x - 4, y), (x, y + 5), (x + 4, y)], width=1.5)
    # feet + branch
    for fx in (88, 112):
        for dx in (-5, 0, 5):
            c.line((fx, 144), (fx + dx, 152), width=2)
    c.line((24, 152), (176, 152), width=4)
    c.line((150, 152), (166, 140), width=3)
    return c, [
        ("layout", 0),
        ("text1x", -1), ("text1y", 79), ("text1font", "&HARRYP__20pt7b"),
        ("text2font", "&HARRYP__10pt7b"),
    ]


@face
def penguin():
    """Club Penguin style penguin."""
    c = Canvas()
    bx, by = 100, 94
    # flippers behind body
    c.polygon([(66, 84), (34, 118), (50, 126), (72, 104)], fill=c.paper, outline=c.ink, width=3.5)
    c.polygon([(134, 84), (166, 118), (150, 126), (128, 104)], fill=c.paper, outline=c.ink, width=3.5)
    c.ellipse((bx, by), 38, 46, fill=c.paper, outline=c.ink, width=4)
    c.ellipse((bx, by + 12), 26, 30, outline=c.ink, width=2)
    for ex in (89, 111):
        c.ring((ex, 78), 7, width=2.5)
        c.disc((ex + 1, 79), 3)
    c.polygon([(90, 90), (100, 85), (110, 90), (100, 98)], fill=c.paper, outline=c.ink, width=2.5)
    c.line((90, 90), (110, 90), width=1.5)
    for fx in (84, 116):
        c.ellipse((fx, 144), 15, 6, fill=c.paper, outline=c.ink, width=3)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 77), ("text1font", "&DynaPuff_VariableFont_wdth_wght20pt7b"),
        ("text2x", -1), ("text2y", 92), ("text2font", "&DynaPuff_VariableFont_wdth_wght10pt7b"),
    ]


@face
def headphones():
    """Headphones; time between the cups."""
    c = Canvas()
    c.arc((100, 104), 76, 180, 360, width=7)
    for x0 in (16, 154):
        c.line((x0 + 15, 96), (x0 + 15, 104), width=6)
        c.rrect((x0, 100), (x0 + 30, 152), 9, fill=c.ink)
        c.rrect((x0 + 8, 108), (x0 + 22, 144), 5, fill=c.paper)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 46), ("text1font", "&CompactaBT20pt7b"),
        ("text2x", -1), ("text2y", 64), ("text2font", "&CompactaBT10pt7b"),
    ]


@face
def ufo():
    """Flying saucer with the time caught in its beam."""
    c = Canvas()
    c.arc((100, 48), 26, 180, 360, width=4)
    c.ellipse((100, 54), 66, 15, fill=c.paper, outline=c.ink, width=4)
    for x in (52, 76, 100, 124, 148):
        c.disc((x, 60), 3)
    c.disc((92, 38), 2)
    c.disc((108, 38), 2)
    c.line((80, 68), (40, 196), width=2.5)
    c.line((120, 68), (160, 196), width=2.5)
    for y in (100, 130, 160, 190):
        half = 20 + 40 * (y - 68) / 128
        c.line((100 - half, y), (100 + half, y), width=1, color=c.ink)
    return c, [
        ("layout", 1), ("noAMPM", "true"),
        ("text1x", -1), ("text1y", 66), ("text1font", "&Bootle_4B9l20pt7b"),
        ("text2x", -1), ("text2y", 85), ("text2font", "&Bootle_4B9l10pt7b"),
    ]


@face
def balloon():
    """Hot-air balloon."""
    c = Canvas()
    cx, cy = 100, 60
    c.ellipse((cx, cy), 46, 50, fill=c.paper, outline=c.ink, width=4)
    c.ellipse((cx, cy), 30, 50, outline=c.ink, width=2)
    c.ellipse((cx, cy), 12, 50, outline=c.ink, width=2)
    c.line((cx - 46, cy), (cx + 46, cy), width=2)
    c.line((cx - 30, cy + 38), (cx - 12, cy + 72), width=3)
    c.line((cx + 30, cy + 38), (cx + 12, cy + 72), width=3)
    c.line((cx - 12, cy + 72), (cx - 12, cy + 80), width=2)
    c.line((cx + 12, cy + 72), (cx + 12, cy + 80), width=2)
    c.polygon([(cx - 16, cy + 80), (cx + 16, cy + 80), (cx + 16, cy + 98), (cx - 16, cy + 98)], outline=c.ink, width=3)
    for yy in (cy + 86, cy + 92):
        c.line((cx - 16, yy), (cx + 16, yy), width=1.2)
    for xx in (cx - 8, cx, cx + 8):
        c.line((xx, cy + 80), (xx, cy + 98), width=1.2)
    return c, [
        ("layout", 0),
        ("text1x", -1), ("text1y", 81), ("text1font", "&CompactaBT20pt7b"),
        ("text2font", "&CompactaBT10pt7b"),
    ]


@face
def lighthouse():
    """Lighthouse on the left, beam sweeping over the time."""
    c = Canvas()
    lx = 42
    top, bot = 46, 158
    def half_w(y):
        return 9 + 9 * (y - top) / (bot - top)
    c.polygon([(lx - half_w(top), top), (lx + half_w(top), top), (lx + half_w(bot), bot), (lx - half_w(bot), bot)],
              outline=c.ink, width=3.5)
    for y0, y1 in ((66, 84), (104, 122), (142, 158)):
        c.polygon([(lx - half_w(y0), y0), (lx + half_w(y0), y0), (lx + half_w(y1), y1), (lx - half_w(y1), y1)], fill=c.ink)
    c.polygon([(lx - 11, 30), (lx + 11, 30), (lx + 11, 46), (lx - 11, 46)], outline=c.ink, width=3)
    c.line((lx, 30), (lx, 46), width=2)
    c.polygon([(lx - 15, 30), (lx + 15, 30), (lx, 16)], fill=c.ink)
    c.disc((lx, 16), 3)
    # beam
    c.line((lx + 11, 38), (196, 18), width=2.5)
    c.line((lx + 11, 38), (196, 74), width=2.5)
    # rocks + water
    c.polygon([(lx - 30, 158), (lx + 30, 158), (lx + 42, 170), (lx - 42, 170)], fill=c.ink)
    for base, phase in ((176, 0), (188, 2)):
        pts = [(x, base + 4 * math.sin(2 * math.pi * x / 40 + phase)) for x in range(-5, 206, 2)]
        c.polyline(pts, width=2.5)
    return c, [
        ("layout", 1),
        ("text1x", 40), ("text1y", 44), ("text1font", "&CompactaBT20pt7b"),
        ("text2x", 40), ("text2y", 63), ("text2font", "&CompactaBT10pt7b"),
    ]


@face
def diya():
    """Oil lamp with a flame; time above."""
    c = Canvas()
    # flame: outer teardrop, inner glow
    def teardrop(cx, top, bottom, w):
        pts = []
        for i in range(25):
            t = i / 24
            y = top + (bottom - top) * t
            pts.append((cx + w * math.sin(math.pi * t) ** 0.8 * (0.35 + 0.65 * t), y))
        for i in range(24, -1, -1):
            t = i / 24
            y = top + (bottom - top) * t
            pts.append((cx - w * math.sin(math.pi * t) ** 0.8 * (0.35 + 0.65 * t), y))
        return pts
    c.polygon(teardrop(100, 66, 122, 16), fill=c.ink)
    c.polygon(teardrop(100, 94, 120, 7), fill=c.paper)
    # bowl
    bowl = [(40, 126), (160, 126)] + [(100 + 60 * math.cos(math.radians(a)), 126 + 24 * math.sin(math.radians(a))) for a in range(0, 181, 6)]
    c.polygon(bowl, fill=c.paper, outline=c.ink, width=4)
    c.line((40, 126), (160, 126), width=4)
    c.line((52, 134), (148, 134), width=1.5)
    c.polygon([(82, 150), (118, 150), (124, 160), (76, 160)], outline=c.ink, width=3)
    for p, sz in (((56, 78), 5), ((146, 84), 4), ((70, 100), 3), ((136, 106), 3)):
        c.sparkle(p, sz)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 8), ("text1font", "&Caveat_VariableFont_wght20pt7b"),
        ("text2x", -1), ("text2y", 26), ("text2font", "&Caveat_VariableFont_wght10pt7b"),
    ]


@face
def coffee():
    """Mug with steam; time on the mug."""
    c = Canvas()
    c.ellipse((100, 162), 64, 10, outline=c.ink, width=3)
    c.ring((146, 118), 20, width=6)
    c.rrect((50, 78), (140, 162), 10, fill=c.paper, outline=c.ink, width=4)
    for x in (76, 96, 116):
        pts = [(x + 5 * math.sin((y - 30) / 8), y) for y in range(30, 68, 2)]
        c.polyline(pts, width=2.5)
    return c, [
        ("layout", 1), ("noAMPM", "true"),
        ("text1x", -1), ("text1y", 46), ("text1font", "&Bootle_4B9l20pt7b"),
        ("text2x", -1), ("text2y", 65), ("text2font", "&Bootle_4B9l10pt7b"),
    ]


@face
def bicycle():
    """Bicycle; time above."""
    c = Canvas()
    rw, fw, bb = (46, 138), (154, 138), (100, 140)
    seat, head = (84, 88), (132, 88)
    for hub in (rw, fw):
        c.ring(hub, 34, width=4)
        for k in range(8):
            a = math.radians(k * 45 + 22)
            c.line(hub, (hub[0] + 32 * math.cos(a), hub[1] + 32 * math.sin(a)), width=1.2)
        c.disc(hub, 4)
    for a, b in ((rw, bb), (bb, seat), (seat, rw), (seat, head), (bb, head), (head, fw)):
        c.line(a, b, width=3.5)
    c.ring(bb, 8, width=3)
    c.line((72, 84), (96, 84), width=5)            # saddle
    c.line((84, 88), (86, 84), width=3)
    c.line(head, (126, 72), width=3.5)              # stem
    c.line((114, 70), (140, 70), width=4)           # handlebar
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 5), ("text1font", "&Neuton_Bold20pt7b"),
        ("text2x", -1), ("text2y", 22), ("text2font", "&Neuton_Bold10pt7b"),
    ]


@face
def whale():
    """Whale with a spout; time top-right."""
    c = Canvas()
    # tail first, body over it
    c.polygon([(150, 104), (184, 84), (176, 106), (188, 126), (150, 120)], fill=c.paper, outline=c.ink, width=3.5)
    c.ellipse((96, 112), 66, 34, fill=c.paper, outline=c.ink, width=4)
    c.polygon([(92, 134), (104, 154), (116, 138)], fill=c.paper, outline=c.ink, width=3)
    c.disc((48, 102), 3.5)
    c.polyline([(32, 118), (54, 124), (78, 124)], width=2.5)
    for y in (132, 140):
        c.line((44, y), (118, y), width=1.5)
    # spout
    c.polyline([(64, 78), (60, 62), (50, 46)], width=2.5)
    c.polyline([(64, 78), (68, 60), (78, 46)], width=2.5)
    for p in ((46, 40), (82, 40), (64, 44)):
        c.disc(p, 2.5)
    for base, phase in ((166, 0), (182, 2)):
        pts = [(x, base + 4 * math.sin(2 * math.pi * x / 44 + phase)) for x in range(-5, 206, 2)]
        c.polyline(pts, width=2.5)
    return c, [
        ("layout", 1),
        ("text1x", 40), ("text1y", 8), ("text1font", "&CompactaBT20pt7b"),
        ("text2x", 40), ("text2y", 27), ("text2font", "&CompactaBT10pt7b"),
    ]


# ---------------------------------------------------------------------------
# Batch 4 - Horizon Zero Dawn machines (silhouettes from sources/hzd) + more clip art
# ---------------------------------------------------------------------------

HZD_TIME = [("text1font", "&Orbitron_Bold15pt7b")]
HZD_DATE = [("text2font", "&Orbitron_Bold10pt7b")]


@face
def thunderjaw():
    c = Canvas()
    c.silhouette(SRC_DIR / "hzd/thunderjaw.png", (2, 84, 198, 198))
    return c, [("layout", 1), ("text1x", -1), ("text1y", 8)] + HZD_TIME + [("text2x", -1), ("text2y", 26)] + HZD_DATE


@face
def watcher():
    c = Canvas()
    c.silhouette(SRC_DIR / "hzd/watcher.png", (56, 40, 198, 190), flip=True)
    return c, [("layout", 1), ("text1x", 4), ("text1y", 5)] + HZD_TIME + [("text2x", 4), ("text2y", 86)] + HZD_DATE


@face
def sawtooth():
    c = Canvas()
    c.silhouette(SRC_DIR / "hzd/sawtooth.png", (50, 56, 198, 198))
    return c, [("layout", 1), ("text1x", 4), ("text1y", 5)] + HZD_TIME + [("text2x", 4), ("text2y", 22)] + HZD_DATE


@face
def stormbird():
    c = Canvas()
    c.silhouette(SRC_DIR / "hzd/stormbird.png", (30, 2, 170, 144))
    return c, [("layout", 1), ("text1x", -1), ("text1y", 75)] + HZD_TIME + [("text2x", -1), ("text2y", 90)] + HZD_DATE


@face
def strider():
    c = Canvas()
    c.silhouette(SRC_DIR / "hzd/strider.png", (16, 66, 184, 198))
    return c, [("layout", 1), ("text1x", -1), ("text1y", 8)] + HZD_TIME + [("text2x", -1), ("text2y", 26)] + HZD_DATE


@face
def vader():
    """Darth Vader helmet (from sources/sw/vader.png)."""
    c = Canvas()
    c.silhouette(SRC_DIR / "sw/vader.png", (30, 2, 170, 150))
    return c, [
        ("layout", 1), ("noAMPM", "true"),
        ("text1x", -1), ("text1y", 77), ("text1font", "&StarJedi_DGRW20pt7b"),
        ("text2x", -1), ("text2y", 92), ("text2font", "&StarJedi_DGRW10pt7b"),
    ]


@face
def mando():
    """Mandalorian helmet (from sources/sw/mando.png)."""
    c = Canvas()
    c.silhouette(SRC_DIR / "sw/mando.png", (10, 8, 190, 150))
    return c, [
        ("layout", 1), ("noAMPM", "true"),
        ("text1x", -1), ("text1y", 77), ("text1font", "&StarJedi_DGRW20pt7b"),
        ("text2x", -1), ("text2y", 92), ("text2font", "&StarJedi_DGRW10pt7b"),
    ]


@face
def boodoor():
    """Boo's door from Monsters Inc; time on the middle panel."""
    c = Canvas()
    c.polygon([(52, 14), (148, 14), (148, 186), (52, 186)], outline=c.ink, width=4)
    for y0, y1 in ((24, 72), (82, 130), (140, 176)):
        c.polygon([(62, y0), (138, y0), (138, y1), (62, y1)], outline=c.ink, width=2)
    c.disc((132, 106), 4)
    def flower(x, y, r):
        for k in range(5):
            a = math.radians(k * 72 - 90)
            c.ring((x + r * math.cos(a), y + r * math.sin(a)), r * 0.7, width=2)
        c.disc((x, y), r * 0.45)
    flower(80, 46, 8)
    flower(118, 52, 7)
    flower(100, 160, 6)
    c.line((70, 60), (80, 46), width=1.5)
    return c, [
        ("layout", 1), ("noAMPM", "true"),
        ("text1x", -1), ("text1y", 46), ("text1font", "&Monster_AG20pt7b"),
        ("text2x", -1), ("text2y", 60), ("text2font", "&Monster_AG10pt7b"),
    ]


@face
def astronaut():
    """Astronaut; time and date on one line below."""
    c = Canvas()
    # backpack, torso, arms, legs, then helmet on top
    c.polygon([(60, 84), (140, 84), (140, 126), (60, 126)], fill=c.paper, outline=c.ink, width=3)
    c.line((66, 92), (44, 124), width=12)
    c.line((134, 92), (156, 124), width=12)
    c.line((66, 92), (44, 124), width=6, color=c.paper)
    c.line((134, 92), (156, 124), width=6, color=c.paper)
    c.disc((42, 128), 7)
    c.disc((158, 128), 7)
    c.rrect((70, 80), (130, 134), 10, fill=c.paper, outline=c.ink, width=4)
    c.polygon([(84, 96), (116, 96), (116, 112), (84, 112)], outline=c.ink, width=2)
    c.disc((90, 104), 2); c.disc((100, 104), 2); c.disc((110, 104), 2)
    for x0 in (76, 106):
        c.rrect((x0, 132), (x0 + 18, 156), 4, fill=c.paper, outline=c.ink, width=3.5)
        c.rrect((x0 - 2, 152), (x0 + 20, 160), 3, fill=c.ink)
    c.disc((100, 48), 30, color=c.paper)
    c.ring((100, 48), 30, width=4)
    c.ellipse((100, 50), 21, 18, fill=c.ink)
    c.arc((100, 50), 14, 200, 300, width=3, color=c.paper)
    return c, [
        ("layout", 0),
        ("text1x", -1), ("text1y", 82), ("text1font", "&CompactaBT20pt7b"),
        ("text2font", "&CompactaBT10pt7b"),
    ]


@face
def cat():
    """Sitting cat silhouette; time top-left."""
    c = Canvas()
    c.polyline([(84, 176), (54, 178), (36, 160), (40, 134)], width=8)
    c.ellipse((116, 138), 36, 46, fill=c.ink)
    c.polygon([(114, 66), (118, 34), (134, 60)], fill=c.ink)
    c.polygon([(146, 60), (158, 32), (162, 66)], fill=c.ink)
    c.disc((138, 76), 26)
    for ex in (128, 148):
        c.ellipse((ex, 74), 5, 3, fill=c.paper)
        c.line((ex, 71), (ex, 77), width=1.5)
    c.polygon([(135, 84), (141, 84), (138, 88)], fill=c.paper)
    for y in (84, 88):
        c.line((110, y), (124, y + (y - 86) * 2), width=1.2)
        c.line((166, y), (152, y + (y - 86) * 2), width=1.2)
    c.line((70, 184), (162, 184), width=3)
    return c, [
        ("layout", 1),
        ("text1x", 4), ("text1y", 6), ("text1font", "&Neuton_Bold20pt7b"),
        ("text2x", 4), ("text2y", 22), ("text2font", "&Neuton_Bold10pt7b"),
    ]


@face
def camera():
    """Retro rangefinder camera."""
    c = Canvas()
    c.rrect((70, 66), (100, 78), 3, fill=c.paper, outline=c.ink, width=3)
    c.polygon([(140, 68), (150, 68), (150, 78), (140, 78)], fill=c.ink)
    c.polygon([(24, 76), (176, 76), (176, 88), (24, 88)], fill=c.paper, outline=c.ink, width=3)
    c.rrect((24, 88), (176, 166), 8, fill=c.paper, outline=c.ink, width=4)
    c.ring((100, 126), 30, width=4)
    c.ring((100, 126), 22, width=2)
    c.ring((100, 126), 12, width=2)
    c.disc((100, 126), 12)
    c.disc((94, 120), 3, color=c.paper)
    c.polygon([(36, 98), (58, 98), (58, 110), (36, 110)], outline=c.ink, width=2)
    c.polygon([(142, 98), (164, 98), (164, 110), (142, 110)], outline=c.ink, width=2)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 4), ("text1font", "&CompactaBT20pt7b"),
        ("text2x", -1), ("text2y", 21), ("text2font", "&CompactaBT10pt7b"),
    ]


@face
def sailboat():
    """Sailboat bottom-right, time top-left."""
    c = Canvas()
    c.polygon([(92, 160), (188, 160), (176, 178), (104, 178)], fill=c.ink)
    c.line((140, 66), (140, 160), width=4)
    c.polygon([(144, 72), (144, 152), (186, 152)], fill=c.paper, outline=c.ink, width=4)
    c.polygon([(136, 84), (136, 152), (100, 152)], fill=c.paper, outline=c.ink, width=4)
    c.polygon([(140, 60), (152, 64), (140, 68)], fill=c.ink)
    for base, phase in ((184, 0), (194, 2.2)):
        pts = [(x, base + 3.5 * math.sin(2 * math.pi * x / 40 + phase)) for x in range(-5, 206, 2)]
        c.polyline(pts, width=2.5)
    c.ring((40, 60), 12, width=3)
    for k in range(8):
        a = math.radians(k * 45)
        c.line((40 + 16 * math.cos(a), 60 + 16 * math.sin(a)), (40 + 22 * math.cos(a), 60 + 22 * math.sin(a)), width=2)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 4), ("text1font", "&Neuton_Bold20pt7b"),
        ("text2x", -1), ("text2y", 21), ("text2font", "&Neuton_Bold10pt7b"),
    ]


@face
def hari():
    """Tamil script - Hari, from the system Tamil font."""
    c = Canvas()
    c.text("\u0bb9\u0bb0\u0bbf", "/System/Library/Fonts/Supplemental/Tamil MN.ttc", 78, (100, 76), index=1)
    c.line((40, 132), (160, 132), width=2)
    return c, [
        ("layout", 1),
        ("text1x", -1), ("text1y", 70), ("text1font", "&Caveat_VariableFont_wght20pt7b"),
        ("text2x", -1), ("text2y", 87), ("text2font", "&Caveat_VariableFont_wght10pt7b"),
    ]


# ---------------------------------------------------------------------------

def main(names):
    names = names or list(FACES)
    for n in names:
        canvas, cfg = FACES[n]()
        out = write_header(n, canvas.to_bits(), cfg)
        print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
