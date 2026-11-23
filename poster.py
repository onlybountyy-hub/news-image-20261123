#!/usr/bin/env python3
"""Render THE WORLD TODAY — Monday 23 November 2026.
Draws a 1024x1024 front-page poster with PIL. Deterministic: no clock,
no randomness, fixed font paths and layout. Run: python3 poster.py
Writes entry.png next to this file.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 241, 231)
INK = (20, 33, 61)
NAVY = (18, 38, 66)
TEAL = (14, 58, 58)
TEAL_LT = (31, 106, 102)
GOLD = (201, 138, 20)
RED = (178, 24, 33)
WHITE = (255, 255, 255)
GREY = (74, 78, 86)
CARD = (255, 255, 255)
LINE = (203, 196, 180)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_globe(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(47, 143, 138),
              outline=(120, 220, 210), width=3)
    # continents as flat blobs
    d.ellipse([cx - r * 0.72, cy - r * 0.55, cx - r * 0.05, cy + r * 0.05],
              fill=(96, 196, 150))
    d.ellipse([cx + r * 0.08, cy - r * 0.15, cx + r * 0.62, cy + r * 0.55],
              fill=(96, 196, 150))
    d.ellipse([cx - r * 0.35, cy + r * 0.35, cx + r * 0.25, cy + r * 0.72],
              fill=(120, 205, 160))
    # latitude lines
    for k, yy in enumerate((-0.45, 0.0, 0.45)):
        y = cy + int(r * yy)
        half = int((r * r - (y - cy) ** 2) ** 0.5) if abs(y - cy) < r else 0
        d.arc([cx - half, y - 6, cx + half, y + 6], 0, 360,
              fill=(120, 220, 210), width=1)


def icon(d, kind, x, y, s, col):
    """Tiny pictogram inside a tile, top-left corner."""
    if kind == "ship":
        d.polygon([(x, y + s * 0.55), (x + s, y + s * 0.55),
                   (x + s * 0.85, y + s * 0.95), (x + s * 0.15, y + s * 0.95)],
                  fill=col)
        d.rectangle([x + s * 0.42, y, x + s * 0.58, y + s * 0.55], fill=col)
        for i, wy in enumerate((y + s * 1.05, y + s * 1.18)):
            d.arc([x, wy, x + s, wy + s * 0.22], 180, 360, fill=col, width=2)
    elif kind == "flame":
        d.polygon([(x + s * 0.5, y), (x + s * 0.95, y + s * 0.6),
                   (x + s * 0.7, y + s * 0.6), (x + s * 0.85, y + s),
                   (x + s * 0.15, y + s), (x + s * 0.3, y + s * 0.6),
                   (x + s * 0.05, y + s * 0.6)], fill=col)
    elif kind == "drone":
        d.line([x, y, x + s, y + s], fill=col, width=3)
        d.line([x + s, y, x, y + s], fill=col, width=3)
        for px, py in ((x, y), (x + s, y), (x, y + s), (x + s, y + s)):
            d.ellipse([px - 5, py - 5, px + 5, py + 5], outline=col, width=2)
        d.ellipse([x + s * 0.32, y + s * 0.32, x + s * 0.68, y + s * 0.68],
                  fill=col)
    elif kind == "building":
        d.rectangle([x + s * 0.1, y + s * 0.3, x + s * 0.9, y + s], fill=col)
        d.polygon([(x, y + s * 0.3), (x + s * 0.5, y),
                   (x + s, y + s * 0.3)], fill=col)
        for wy in (y + s * 0.45, y + s * 0.68):
            for wx in (x + s * 0.25, x + s * 0.45, x + s * 0.65):
                d.rectangle([wx, wy, wx + 7, wy + 7], fill=PAPER)
    elif kind == "doc":
        d.rectangle([x + s * 0.15, y, x + s * 0.85, y + s], fill=col)
        d.polygon([(x + s * 0.85, y), (x + s, y + s * 0.15),
                   (x + s * 0.85, y + s * 0.15)], fill=(255, 255, 255))
        for wy in (y + s * 0.35, y + s * 0.55, y + s * 0.75):
            d.line([x + s * 0.3, wy, x + s * 0.7, wy], fill=PAPER, width=2)
    elif kind == "castle":
        d.rectangle([x + s * 0.15, y + s * 0.45, x + s * 0.85, y + s],
                    fill=col)
        d.polygon([(x + s * 0.05, y + s * 0.5), (x + s * 0.5, y + s * 0.1),
                   (x + s * 0.95, y + s * 0.5)], fill=col)
        d.rectangle([x + s * 0.42, y + s * 0.68, x + s * 0.58, y + s],
                    fill=PAPER)
    elif kind == "train":
        d.rectangle([x, y + s * 0.1, x + s, y + s * 0.8], fill=col)
        for wx in (x + s * 0.12, x + s * 0.4, x + s * 0.68):
            d.rectangle([wx, y + s * 0.25, wx + s * 0.2, y + s * 0.5],
                        fill=PAPER)
        for wx in (x + s * 0.18, x + s * 0.68):
            d.ellipse([wx, y + s * 0.82, wx + 10, y + s * 0.82 + 10],
                      fill=col)
    elif kind == "ball":
        d.ellipse([x, y, x + s, y + s], outline=col, width=3)
        d.polygon([(x + s * 0.5, y + s * 0.28), (x + s * 0.72, y + s * 0.45),
                   (x + s * 0.63, y + s * 0.72), (x + s * 0.37, y + s * 0.72),
                   (x + s * 0.28, y + s * 0.45)], fill=col)
    elif kind == "bat":
        d.polygon([(x + s * 0.15, y + s * 0.85), (x + s * 0.55, y + s * 0.1),
                   (x + s * 0.8, y + s * 0.2), (x + s * 0.4, y + s * 0.95)],
                  fill=col)
        d.ellipse([x + s * 0.7, y + s * 0.7, x + s * 0.95, y + s * 0.95],
                  fill=RED)
    elif kind == "march":
        for i, ox in enumerate((0, s * 0.32, s * 0.64)):
            d.ellipse([x + ox, y, x + ox + 9, y + 9], fill=col)
            d.rectangle([x + ox, y + 11, x + ox + 9, y + s * 0.55], fill=col)
        d.rectangle([x, y + s * 0.72, x + s, y + s * 0.8], fill=col)
    elif kind == "drop":
        d.polygon([(x + s * 0.5, y), (x + s * 0.95, y + s * 0.62),
                   (x + s * 0.05, y + s * 0.62)], fill=col)
        d.ellipse([x + s * 0.05, y + s * 0.5, x + s * 0.95, y + s],
                  fill=col)


# (tag, colour, icon, headline, detail)
STORIES = [
    ("WAR AT SEA", (11, 94, 120), "ship",
     "Russian warship sunk at Benghazi",
     "Suspected Ukrainian sea drones hit the corvette Merkury; 10 hurt."),
    ("MIDDLE EAST", (178, 24, 33), "drop",
     "Tankers hit by mines; Houthis strike Saudi refinery",
     "Shipping attacks at their highest level since the war began."),
    ("UKRAINE", (11, 94, 120), "drone",
     "Drone hits flats near Kyiv",
     "2 killed, 14 missing in Dymer as rescuers dig through rubble."),
    ("SUDAN", (120, 72, 20), "building",
     "Drones hit UN site in Khartoum",
     "Strikes damage a UN facility; 3 killed in Omdurman."),
    ("DISASTER", (178, 24, 33), "flame",
     "Factory fire: 3 dead, 36 missing",
     "Candy plant in Banten burns; search resumes at dawn."),
    ("SEOUL", (11, 94, 120), "doc",
     "Minister quits over AI exam scandal",
     "Education chief resigns after CSAT anti-cheating chaos."),
    ("HERITAGE", (120, 72, 20), "castle",
     "Shuri Castle reopens",
     "Okinawa's main hall restored, 7 years after the fire."),
    ("DIPLOMACY", (11, 94, 120), "train",
     "Modi meets Nepal's PM Shah",
     "State visit brings pacts and a new Ayodhya–Janakpur train."),
    ("SPORT", (31, 106, 102), "ball",
     "Liverpool rout Man Utd",
     "Ten-man United beaten in Pochettino's debut."),
    ("SPORT", (31, 106, 102), "bat",
     "India post record 720/9d",
     "Wellington Test record as the Day 5 chase builds."),
    ("EUROPE", (120, 72, 20), "march",
     "Thousands march in Lisbon",
     "Living costs fuel anger on the streets of Portugal."),
]

FIGURES = [
    ("190+", "countries at COP31"),
    ("44 hrs", "of overtime in Antalya"),
    ("36", "missing in factory fire"),
    ("10", "hurt in Benghazi strike"),
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.rectangle([0, 0, W, 92], fill=NAVY)
    d.rectangle([0, 92, W, 96], fill=GOLD)
    f_title = font(SERIF_B, 58)
    d.text((W / 2, 46), "THE WORLD TODAY", font=f_title, fill=WHITE,
           anchor="mm")
    f_date = font(SANS_B, 20)
    d.text((16, 118), "MONDAY  23  NOVEMBER  2026", font=f_date, fill=INK)
    d.text((W - 16, 118), "12 STORIES  •  ONE DAY", font=f_date, fill=INK,
           anchor="ra")

    # ---- hero ----
    hx, hy, hw, hh = 16, 140, 992, 348
    d.rectangle([hx, hy, hx + hw, hy + hh], fill=TEAL)
    d.rectangle([hx, hy, hx + hw, hy + hh], outline=GOLD, width=3)
    d.text((hx + 28, hy + 22), "ANTALYA, TURKEY — CLIMATE",
           font=font(SANS_B, 19), fill=(255, 214, 120))
    f_hero = font(SERIF_B, 70)
    d.text((hx + 26, hy + 50), "COP31", font=f_hero, fill=WHITE)
    d.text((hx + 26, hy + 126), "COLLAPSES", font=f_hero, fill=WHITE)
    f_sub = font(SANS_B, 25)
    sub = wrap(d, "No deal on fossil fuels — the longest climate summit in history ends in chaos.",
               f_sub, 560)
    y = hy + 214
    for line in sub[:2]:
        d.text((hx + 28, y), line, font=f_sub, fill=(214, 232, 228))
        y += 32
    f_cap = font(SANS, 19)
    cap = wrap(d, "The EU and island states reject a pact that never names fossil fuels.",
               f_cap, 560)
    y += 6
    for line in cap[:2]:
        d.text((hx + 28, y), line, font=f_cap, fill=(170, 200, 192))
        y += 25
    # hero art: globe + NO DEAL stamp
    draw_globe(d, hx + 800, hy + 150, 105)
    stamp = Image.new("RGBA", (300, 90), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rectangle([4, 4, 296, 86], outline=(255, 255, 255), width=4)
    sd.text((150, 45), "NO DEAL", font=font(SANS_B, 44), fill=(255, 255, 255),
            anchor="mm")
    stamp = stamp.rotate(12, expand=True, resample=Image.BICUBIC)
    img.paste(stamp, (hx + 640, hy + 250), stamp)

    # ---- grid: 3 cols x 4 rows ----
    gx, gy = 16, 504
    cw, ch, gap = 325, 116, 8
    f_tag = font(SANS_B, 13)
    f_head = font(SANS_B, 20)
    f_det = font(SANS, 15)
    cells = STORIES + [None]  # last cell = figures box
    for i, cell in enumerate(cells):
        r, c = divmod(i, 3)
        x = gx + c * (cw + gap)
        y = gy + r * (ch + gap)
        d.rectangle([x, y, x + cw, y + ch], fill=CARD, outline=LINE, width=1)
        if cell is None:
            d.rectangle([x, y, x + cw, y + 26], fill=INK)
            d.text((x + 10, y + 13), "THE DAY IN NUMBERS",
                   font=font(SANS_B, 13), fill=WHITE, anchor="lm")
            fy = y + 34
            for num, lab in FIGURES:
                d.text((x + 10, fy), num, font=font(SANS_B, 20),
                       fill=RED, anchor="lm")
                d.text((x + 92, fy), lab, font=font(SANS, 15),
                       fill=GREY, anchor="lm")
                fy += 20
            continue
        tag, col, ic, head, det = cell
        d.rectangle([x, y, x + cw, y + 4], fill=col)
        icon(d, ic, x + cw - 34, y + 10, 22, col)
        d.text((x + 10, y + 13), tag, font=f_tag, fill=col)
        hl = wrap(d, head, f_head, cw - 20)
        hyy = y + 34
        for line in hl[:2]:
            d.text((x + 10, hyy), line, font=f_head, fill=INK)
            hyy += 23
        dl = wrap(d, det, f_det, cw - 20)
        for line in dl[:2]:
            d.text((x + 10, hyy), line, font=f_det, fill=GREY)
            hyy += 19

    # ---- footer ----
    d.text((16, 1006), "Compiled from wire reports — CNN • AP • Reuters • AFP • The Hindu • NPR",
           font=font(SANS, 13), fill=GREY)

    img.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    main()
