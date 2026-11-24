#!/usr/bin/env python3
"""news-image-20261123 — one-page newspaper poster for Monday 23 Nov 2026.

Draws the poster with a hand-built 5x7 bitmap font and a hand-built PNG
encoder. Python 3 standard library only; no network; deterministic.
Writes entry.png to $MAKEFUN_OUTPUT_DIR (or ./entry.png as fallback).
"""

import os
import struct
import sys
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font -----
# Each glyph is 7 rows of exactly 5 pixels, "#" = on, "." = off.
GLYPHS = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "\u2014": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "\u2022": (".....", ".....", ".##..", ".##..", ".##..", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", ".#.##", "#..##"),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
}

# Fail loudly on a malformed glyph instead of drawing garbage.
for _ch, _rows in GLYPHS.items():
    assert len(_rows) == 7, "glyph %r has %d rows" % (_ch, len(_rows))
    for _row in _rows:
        assert len(_row) == 5, "glyph %r row %r is not 5 wide" % (_ch, _row)


def text_width(text, scale, spacing=None):
    if spacing is None:
        spacing = scale
    adv = 5 * scale + spacing
    return len(text) * adv - spacing


def wrap_text(text, max_width, scale, spacing=None):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    if spacing is None:
        spacing = scale
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if text_width(trial, scale, spacing) <= max_width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


# -------------------------------------------------------------- canvas -----
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = r
                self.px[i + 1] = g
                self.px[i + 2] = b

    def draw_glyph(self, x, y, ch, scale, color):
        glyph = GLYPHS.get(ch)
        if glyph is None:
            glyph = GLYPHS["?"]
        r, g, b = color
        for row_i, row in enumerate(glyph):
            for col_i, cell in enumerate(row):
                if cell != "#":
                    continue
                px0 = x + col_i * scale
                py0 = y + row_i * scale
                for dy in range(scale):
                    yy = py0 + dy
                    if yy < 0 or yy >= self.h:
                        continue
                    base = (yy * self.w + px0) * 3
                    for dx in range(scale):
                        xx = px0 + dx
                        if xx < 0 or xx >= self.w:
                            continue
                        i = base + dx * 3
                        self.px[i] = r
                        self.px[i + 1] = g
                        self.px[i + 2] = b

    def text(self, x, y, s, scale, color, spacing=None, align="left"):
        if spacing is None:
            spacing = scale
        adv = 5 * scale + spacing
        if align == "right":
            x -= text_width(s, scale, spacing)
        elif align == "center":
            x -= text_width(s, scale, spacing) // 2
        for ch in s:
            self.draw_glyph(x, y, ch, scale, color)
            x += adv

    def text_block(self, x, y, lines, scale, color, line_gap, spacing=None):
        for i, line in enumerate(lines):
            self.text(x, y + i * (7 * scale + line_gap), line, scale, color, spacing)


# ------------------------------------------------------------ png write ----
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, canvas):
    raw = bytearray()
    row_len = canvas.w * 3
    for yy in range(canvas.h):
        raw.append(0)  # filter: none
        start = yy * row_len
        raw += canvas.px[start:start + row_len]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# -------------------------------------------------------------- colours ----
NAVY = (10, 30, 60)        # masthead + footer band
HERO_BG = (16, 38, 74)     # hero panel
CREAM = (247, 242, 231)    # tile background / cream text
GOLD = (201, 162, 39)      # gold rules, kicker, date
WHITE = (255, 255, 255)
RED = (176, 58, 46)        # divider
DARK = (20, 33, 61)        # tile headline
GREY = (88, 88, 88)        # tile deck
TEAL = (14, 124, 107)
STEEL = (31, 78, 121)
AMBER = (146, 96, 16)
GREEN = (34, 112, 74)

MARGIN = 40
CONTENT_W = W - 2 * MARGIN  # 944


def draw_poster():
    c = Canvas(W, H, CREAM)

    # ---- masthead: deep-navy band, cream title left, gold date right ----
    c.rect(0, 0, W, 104, NAVY)
    c.text(MARGIN, 38, "THE WORLD TODAY", 4, CREAM)
    c.text(W - MARGIN, 38, "MONDAY, 23 NOVEMBER 2026", 4, GOLD,
           spacing=1, align="right")
    c.rect(0, 104, W, 4, GOLD)

    # ---- hero panel ----
    c.rect(0, 108, W, 312, HERO_BG)
    c.text(48, 132, "LIBYA \u2022 THE WAR AT SEA SPREADS", 3, GOLD)
    c.rect(48, 162, 120, 4, GOLD)
    c.text(48, 182, "UKRAINE DRONES HIT", 6, CREAM)
    c.text(48, 234, "RUSSIAN SHIPS IN LIBYA", 6, CREAM)
    deck = wrap_text(
        "KYIV CONFIRMS NAVAL DRONES STRUCK TWO RUSSIAN SHIPS AT BENGHAZI "
        "PORT \u2014 THE WAR REACHES THE MEDITERRANEAN.",
        928, 3)
    c.text_block(48, 306, deck, 3, WHITE, 8)

    # ---- red divider ----
    c.rect(0, 420, W, 8, RED)

    # ---- 2x2 grid of tiles ----
    tiles = [
        ("THE GULF", TEAL,
         "IRAN'S BIGGEST MISSILE WEEK IN A YEAR",
         "TRUMP SAYS TEHRAN FIRED ITS HEAVIEST WEEK OF MISSILES AND DRONES "
         "IN OVER A YEAR; IRAN SAYS IT HIT US PATRIOT RADARS IN BAHRAIN."),
        ("NATO \u2022 POLAND", STEEL,
         "NATO MEETS AS JETS SCRAMBLE",
         "EMERGENCY MEETING IN BRUSSELS AS NATO SENDS EARLY-WARNING "
         "AIRCRAFT TO POLAND; FINLAND SUMMONS RUSSIA'S ENVOY."),
        ("MARKETS", AMBER,
         "BITCOIN SINKS TO 2-YEAR LOW",
         "BITCOIN FALLS TO ABOUT $55,100, ITS LOWEST SINCE SEPTEMBER 2024, "
         "THEN REBOUNDS TOWARD $61,000; NVIDIA SUFFERS ITS WORST WEEK "
         "SINCE 2008."),
        ("INDONESIA", GREEN,
         "FACTORY FIRE KILLS 24",
         "A BLAZE AT A SWEETS FACTORY LEAVES AT LEAST 24 DEAD AND ABOUT 30 "
         "MISSING; THE SEARCH GOES ON."),
    ]
    tile_w = (CONTENT_W - 12) // 2   # 466
    tile_h = 244
    grid_y = 428
    for idx, (kicker, accent, headline, deck_text) in enumerate(tiles):
        tx = MARGIN + (idx % 2) * (tile_w + 12)
        ty = grid_y + (idx // 2) * (tile_h + 12)
        c.rect(tx, ty, tile_w, tile_h, CREAM)
        c.rect(tx, ty, tile_w, 8, accent)
        c.text(tx + 20, ty + 22, kicker, 2, accent)
        head_lines = wrap_text(headline, tile_w - 40, 4)
        c.text_block(tx + 20, ty + 50, head_lines, 4, DARK, 8)
        deck_lines = wrap_text(deck_text, tile_w - 40, 2)
        deck_y = ty + 50 + len(head_lines) * (7 * 4 + 8) + 8
        c.text_block(tx + 20, deck_y, deck_lines, 2, GREY, 4)

    # ---- footer band ----
    c.rect(0, 928, W, 96, NAVY)
    c.text(MARGIN, 946,
           "EVERY STORY ABOVE HAPPENED, OR WAS FIRST REPORTED, "
           "ON MONDAY 23 NOVEMBER 2026.", 2, WHITE, spacing=1)
    c.text(MARGIN, 974, "SOURCES: REUTERS \u2022 BBC \u2022 COINDESK \u2022 AL JAZEERA",
           2, GOLD)

    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "."
    path = os.path.join(out_dir, "entry.png")
    canvas = draw_poster()
    size = write_png(path, canvas)
    sys.stdout.write("wrote %s (%d bytes)\n" % (path, size))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
