#!/usr/bin/env python3
"""Invented passport spread for the Republic of Zembla.

Draws, with PIL only, an open passport spread (data page + visa page) for a
country that does not exist, and writes it to entry.png (1024x1024, < 1 MiB).
No network, no copied-in image: every line, stamp and the portrait are drawn
programmatically. Run:  python3 main.py   (writes entry.png next to main.py,
or to /output/entry.png when /output exists, as the grader expects).
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants
W, H = 1024, 1024
PAPER = (246, 241, 227)          # cream passport paper
PAPER_DARK = (233, 226, 205)
INK = (26, 32, 48)               # near-black blue ink
BLUE = (24, 64, 128)             # entry-stamp blue
RED = (158, 28, 28)              # endorsement red
GREEN = (28, 96, 64)
GOLD = (176, 138, 52)
LEATHER = (28, 34, 58)           # dark navy passport-cover background

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF = lambda s: font("DejaVuSerif.ttf", s)
SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF_I = lambda s: ImageFont.truetype(
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
MONO = lambda s: font("DejaVuSansMono.ttf", s)
MONO_B = lambda s: font("DejaVuSansMono-Bold.ttf", s)


def text(draw, xy, s, f, fill=INK, anchor="la"):
    draw.text(xy, s, font=f, fill=fill, anchor=anchor)


def centre(draw, cx, y, s, f, fill=INK):
    draw.text((cx, y), s, font=f, fill=fill, anchor="ma")


# ------------------------------------------------------- MRZ (ICAO 9303)
def mrz_check(s):
    weights = (7, 3, 1)
    total = 0
    for i, ch in enumerate(s):
        if ch == "<":
            v = 0
        elif ch.isdigit():
            v = int(ch)
        else:
            v = ord(ch) - 55  # A=10 .. Z=35
        total += v * weights[i % 3]
    return str(total % 10)


def mrz_line1(surname, given):
    name = (surname + "<<" + given.replace(" ", "<")).ljust(39, "<")[:39]
    return "P<ZMB" + name


def mrz_line2(passport_no, dob, sex, expiry, personal=""):
    p = passport_no.ljust(9, "<")[:9]
    pers = personal.ljust(14, "<")[:14]
    line = (p + mrz_check(p) + "ZMB" + dob + mrz_check(dob) + sex + expiry
            + mrz_check(expiry) + pers + mrz_check(pers))
    # composite check over positions 1-10, 14-20, 22-43 (1-based)
    line += mrz_check(line[0:10] + line[13:20] + line[21:43])
    return line[:44]


def mrz_lines():
    l1 = mrz_line1("KORVIN", "ELENA MARA")
    l2 = mrz_line2("ZB0048217", "910512", "F", "340313")
    assert len(l1) == 44 and len(l2) == 44, (l1, l2)
    return l1, l2


# ------------------------------------------------------------- small helpers
def guilloche(draw, box, colour, step=14, alpha=26):
    """Faint overlapping arcs, like a passport's security print."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    for cx in range(x0 - 120, x1 + 120, step * 3):
        for cy in range(y0 - 120, y1 + 120, step * 3):
            r = 46
            ld.ellipse([cx - r, cy - r, cx + r, cy + r],
                       outline=colour + (alpha,), width=1)
    img = layer.crop(box)
    return img


def circle_text(draw, cx, cy, r, s, f, fill, start_deg=-90):
    """Draw a string along a circle, letters upright on the ring."""
    n = len(s)
    span = 270.0
    for i, ch in enumerate(s):
        ang = math.radians(start_deg - span / 2 + span * i / max(n - 1, 1))
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang)
        tmp = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        td.text((30, 30), ch, font=f, fill=fill, anchor="mm")
        tmp = tmp.rotate(-math.degrees(ang) - 90, resample=Image.BICUBIC,
                         center=(30, 30))
        draw._image.paste(tmp, (int(x) - 30, int(y) - 30), tmp)


def stamp_box(width, lines, ink, border=3, rotate=0, line_fonts=None):
    """A rectangular ink stamp on its own transparent layer, rotated.
    Height is sized to fit every line inside the border."""
    step, top, pad = 19, 27, 20
    h = top + step * (len(lines) - 1) + pad
    w = width
    layer = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=6,
                        outline=ink + (215,), width=border)
    d.rounded_rectangle([24, 24, 16 + w, 16 + h], radius=4,
                        outline=ink + (215,), width=1)
    y = top
    for i, line in enumerate(lines):
        f = (line_fonts[i] if line_fonts and i < len(line_fonts)
             else SANS_B(15))
        d.text((20 + w // 2, y), line, font=f, fill=ink + (225,),
               anchor="ma")
        y += step
    return layer.rotate(rotate, resample=Image.BICUBIC, expand=True)

# ------------------------------------------------------------ coat of arms
def draw_arms(draw, cx, cy, s):
    """Zembla's arms: crowned shield, a star over three waves, gold on blue."""
    w, h = s, int(s * 1.25)
    x0, y0 = cx - w // 2, cy - h // 2
    # crown
    draw.polygon([(x0 + 8, y0 + 14), (x0 + w // 2, y0 - 6),
                  (x0 + w - 8, y0 + 14), (x0 + w - 8, y0 + 20),
                  (x0 + 8, y0 + 20)], fill=GOLD)
    draw.ellipse([x0 + w // 2 - 3, y0 - 8, x0 + w // 2 + 3, y0 - 2],
                 fill=GOLD)
    # shield
    draw.polygon([(x0, y0 + 22), (x0 + w, y0 + 22), (x0 + w, y0 + h - 18),
                  (x0 + w // 2, y0 + h), (x0, y0 + h - 18)],
                 fill=BLUE, outline=GOLD, width=2)
    # star
    sx, sy, r = cx, y0 + h // 2 - 8, 9
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    draw.polygon(pts, fill=(240, 220, 140))
    # three waves
    for j, wy in enumerate((y0 + h - 34, y0 + h - 26, y0 + h - 18)):
        pts = []
        for k in range(21):
            px = x0 + 6 + k * (w - 12) / 20
            py = wy + 3 * math.sin(k * math.pi / 2.5 + j)
            pts.append((px, py))
        draw.line(pts, fill=(240, 240, 235), width=2)


# ---------------------------------------------------------------- portrait
def draw_portrait(draw, box):
    """Stylised flat passport photo of the holder, drawn, not pasted."""
    x0, y0, x1, y1 = box
    # backdrop: pale blue-grey with a faint diagonal watermark
    for i in range(y1 - y0):
        t = i / max(y1 - y0 - 1, 1)
        c = tuple(int(168 + (216 - 168) * t) for _ in range(3))
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=(c[0], c[1] + 8, c[2] + 22))
    wm = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm)
    wd.text((70, 95), "ZEMBLA", font=SANS_B(13), fill=(255, 255, 255, 60),
            anchor="mm")
    wm = wm.rotate(-38, resample=Image.BICUBIC, center=(70, 95))
    draw._image.paste(wm, (x0, y0), wm)
    cx = (x0 + x1) // 2
    skin = (226, 188, 158)
    hair = (58, 38, 26)
    # shoulders / teal jacket, white shirt V
    draw.polygon([(x0 + 8, y1), (x0 + 42, y1 - 52), (cx - 16, y1 - 62),
                  (cx + 16, y1 - 62), (x1 - 42, y1 - 52), (x1 - 8, y1)],
                 fill=(32, 96, 92))
    draw.polygon([(cx - 16, y1 - 62), (cx, y1 - 34), (cx + 16, y1 - 62)],
                 fill=(244, 242, 236))
    # neck + head
    draw.rectangle([cx - 11, y1 - 78, cx + 11, y1 - 52], fill=skin)
    draw.ellipse([cx - 30, y0 + 34, cx + 30, y0 + 108], fill=skin)
    # hair: dark cap with a side parting
    draw.pieslice([cx - 32, y0 + 28, cx + 32, y0 + 96], 180, 360, fill=hair)
    draw.polygon([(cx - 30, y0 + 62), (cx - 8, y0 + 40), (cx + 6, y0 + 58),
                  (cx + 30, y0 + 62), (cx + 30, y0 + 44), (cx, y0 + 30),
                  (cx - 30, y0 + 44)], fill=hair)
    # brows, eyes, nose, mouth — minimal, front-facing
    draw.line([(cx - 22, y0 + 74), (cx - 8, y0 + 72)], fill=hair, width=2)
    draw.line([(cx + 8, y0 + 72), (cx + 22, y0 + 74)], fill=hair, width=2)
    draw.ellipse([cx - 19, y0 + 78, cx - 11, y0 + 84], fill=(40, 32, 28))
    draw.ellipse([cx + 11, y0 + 78, cx + 19, y0 + 84], fill=(40, 32, 28))
    draw.line([(cx, y0 + 84), (cx - 2, y0 + 94), (cx + 2, y0 + 96)],
              fill=(180, 140, 120), width=2)
    draw.line([(cx - 9, y0 + 104), (cx + 9, y0 + 104)],
              fill=(150, 84, 72), width=2)
    draw.rectangle([x0, y0, x1, y1], outline=(90, 100, 120), width=2)


# -------------------------------------------------------------- data page
def draw_data_page(img, draw):
    x0, y0, x1, y1 = 40, 150, 512, 874
    draw.rectangle([x0, y0, x1, y1], fill=PAPER)
    img.paste(guilloche(draw, (x0, y0, x1, y1), (120, 130, 160)),
              (x0, y0), guilloche(draw, (x0, y0, x1, y1), (120, 130, 160)))
    draw_arms(draw, 276, 208, 46)
    centre(draw, 276, 246, "REPUBLIC OF ZEMBLA", SERIF_B(27))
    centre(draw, 276, 276, "ZEMBLA REPUBLIK  \u2022  PASSPORT", SANS(11),
           fill=(90, 90, 100))
    draw.line([(70, 300), (482, 300)], fill=INK, width=2)
    centre(draw, 276, 308, "Type  P      Code  ZMB      No.  ZB0048217",
           MONO_B(15))
    draw.line([(70, 332), (482, 332)], fill=(150, 140, 110), width=1)

    # photo + fields
    draw_portrait(draw, (70, 348, 220, 538))
    centre(draw, 145, 544, "ELENA MARA KORVIN", SANS_B(10))
    fields = [
        ("Surname / Efternamn", "KORVIN"),
        ("Given names / Fornavn", "ELENA MARA"),
        ("Nationality / Nasjonalitet", "ZEMBLAN"),
        ("Date of birth / F\u00f8dt", "12 MAY 1991"),
        ("Place of birth / F\u00f8dested", "ONHAVA, ZEMBLA"),
        ("Sex / Kj\u00f8nn", "F"),
        ("Date of issue / Utstedt", "14 MAR 2024"),
        ("Date of expiry / Utl\u00f8per", "13 MAR 2034"),
        ("Authority / Myndighet", "MINISTRY OF THE INTERIOR"),
        ("", "ONHAVA"),
    ]
    fy = 348
    for label, value in fields:
        text(draw, (238, fy), label, SANS(9), fill=(110, 105, 90))
        text(draw, (238, fy + 11), value, SANS_B(13))
        fy += 26 if label else 14
    # signature
    draw.line([(238, 640), (482, 640)], fill=INK, width=1)
    text(draw, (238, 646), "Holder's signature / Signatur", SANS(9),
         fill=(110, 105, 90))
    text(draw, (240, 660), "Elena Korvin", SERIF_I(20))
    # MRZ strip
    l1, l2 = mrz_lines()
    draw.rectangle([70, 712, 482, 772], fill=(238, 234, 220))
    text(draw, (76, 718), l1, MONO(12))
    text(draw, (76, 740), l2, MONO(12))
    text(draw, (70, 856), "2", SANS(10), fill=(120, 115, 100))


# -------------------------------------------------------------- visa page
def draw_visa_page(img, draw):
    x0, y0, x1, y1 = 512, 150, 984, 874
    draw.rectangle([x0, y0, x1, y1], fill=PAPER)
    img.paste(guilloche(draw, (x0, y0, x1, y1), (120, 130, 160)),
              (x0, y0), guilloche(draw, (x0, y0, x1, y1), (120, 130, 160)))
    centre(draw, 748, 168, "VISAS", SERIF_B(24))
    centre(draw, 748, 196, "VISA  \u2022  VISUM", SANS(10),
           fill=(90, 90, 100))
    draw.line([(542, 218), (954, 218)], fill=INK, width=2)

    # --- visa sticker: Kingdom of Thule (issued 21 Aug 2025, valid Sep–Nov 2025)
    vx0, vy0, vx1, vy1 = 542, 232, 954, 330
    draw.rectangle([vx0, vy0, vx1, vy1], fill=(250, 248, 240),
                   outline=GREEN, width=2)
    draw.rectangle([vx0, vy0, vx1, vy0 + 26], fill=GREEN)
    centre(draw, 748, vy0 + 4, "VISA  \u2014  KINGDOM OF THULE", SANS_B(13),
           fill=(255, 255, 255))
    vfields = [("Type", "C  \u2014  SHORT STAY"), ("Entries", "SINGLE"),
               ("Valid", "01 SEP 2025 \u2013 30 NOV 2025"),
               ("Issued", "21 AUG 2025 \u2014 ONHAVA")]
    vy = vy0 + 34
    for k, v in vfields:
        text(draw, (556, vy), k, SANS_B(10), fill=GREEN)
        text(draw, (640, vy), v, SANS(11))
        vy += 16
    draw.ellipse([906, vy0 + 34, 946, vy0 + 74], outline=GREEN, width=2)
    centre(draw, 926, vy0 + 48, "TH", SANS_B(12), fill=GREEN)

    # --- Arcadia entry / exit stamps (June 2024 — after the 14 Mar 2024 issue)
    s1 = stamp_box(196,
                   ["ARCADIA", "ARRIVED", "02 JUN 2024", "LIDIA AIRPORT"],
                   BLUE, rotate=-7,
                   line_fonts=[SANS_B(16), SANS_B(13), MONO_B(14), SANS(10)])
    img.paste(s1, (552, 344), s1)
    s2 = stamp_box(196,
                   ["ARCADIA", "DEPARTED", "18 JUN 2024", "LIDIA AIRPORT"],
                   BLUE, rotate=6,
                   line_fonts=[SANS_B(16), SANS_B(13), MONO_B(14), SANS(10)])
    img.paste(s2, (748, 344), s2)

    # --- round Karnia transit stamp (11 May 2025)
    layer = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.ellipse([10, 10, 190, 190], outline=(122, 44, 122, 225), width=3)
    ld.ellipse([26, 26, 174, 174], outline=(122, 44, 122, 225), width=1)
    circle_text(ld, 100, 100, 76, "REPUBLIC OF KARNIA \u2022 TRANSIT \u2022",
                SANS_B(11), (122, 44, 122, 225))
    ld.text((100, 92), "11 MAY", font=SANS_B(15),
            fill=(122, 44, 122, 230), anchor="ma")
    ld.text((100, 112), "2025", font=SANS_B(15),
            fill=(122, 44, 122, 230), anchor="ma")
    layer = layer.rotate(12, resample=Image.BICUBIC, expand=True)
    img.paste(layer, (556, 496), layer)

    # --- Thule entry stamp (09 Sep 2025 — inside the visa's validity)
    s3 = stamp_box(196,
                   ["THULE", "ENTERED", "09 SEP 2025", "PORT OF ONHAVA"],
                   (28, 96, 64), rotate=-5,
                   line_fonts=[SANS_B(16), SANS_B(13), MONO_B(14), SANS(10)])
    img.paste(s3, (748, 512), s3)

    # --- the telling detail: red endorsement + fee stamp
    s4 = stamp_box(330,
                   ["NOT VALID FOR TRAVEL TO", "THE NORTHERN MARCHES"],
                   RED, rotate=3,
                   line_fonts=[SANS_B(14), SANS_B(14)])
    img.paste(s4, (582, 652), s4)
    s5 = stamp_box(150, ["FEE PAID", "40 KRONA"], GOLD, rotate=-4,
                   line_fonts=[SANS_B(12), MONO_B(13)])
    img.paste(s5, (600, 740), s5)
    text(draw, (772, 756),
         "Endorsement: Ministry of the Interior,\nOnhava, 14 Mar 2024.",
         SANS(10), fill=(110, 105, 90))
    text(draw, (954, 856), "3", SANS(10), fill=(120, 115, 100),
         anchor="ra")

# ------------------------------------------------------------------- build
def build():
    random.seed(20261121)
    img = Image.new("RGB", (W, H), LEATHER)
    draw = ImageDraw.Draw(img)
    # leather speckle + vignette
    for _ in range(2600):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        v = random.randint(-14, 14)
        px = img.getpixel((x, y))
        img.putpixel((x, y), tuple(max(0, min(255, c + v)) for c in px))
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-220, -220, W + 220, H + 220], fill=255)
    img = Image.composite(img, Image.new("RGB", (W, H), (10, 12, 24)), vig)
    draw = ImageDraw.Draw(img)

    # spread shadow + pages
    draw.rectangle([48, 158, 992, 882], fill=(12, 14, 26))
    draw_data_page(img, draw)
    draw_visa_page(img, draw)
    # centre seam
    draw.rectangle([508, 150, 516, 874], fill=(120, 110, 88))
    draw.line([(510, 150), (510, 874)], fill=(60, 54, 40), width=1)
    draw.rectangle([40, 150, 984, 874], outline=(150, 138, 100), width=2)

    # caption strip above the spread, like a cover title
    centre(draw, 512, 96, "THE PASSPORT PAGE OF A COUNTRY THAT ISN'T THERE",
           SERIF_B(20), fill=(232, 226, 205))
    centre(draw, 512, 124, "REPUBLIC OF ZEMBLA  \u2022  EST. 1921  \u2022  ONHAVA",
           SANS(11), fill=(170, 164, 140))
    centre(draw, 512, 906, "Specimen document \u2014 the Northern Marches "
           "are closed to holders of this passport.", SANS(11), fill=(170, 164, 140))

    out_dir = "/output" if os.path.isdir("/output") else "."
    path = os.path.join(out_dir, "entry.png")
    img.save(path, "PNG", optimize=True)
    size = os.path.getsize(path)
    assert img.size == (1024, 1024), img.size
    assert size <= 1_048_576, size
    print(f"wrote {path}: 1024x1024 PNG, {size} bytes")
    return path


if __name__ == "__main__":
    build()
