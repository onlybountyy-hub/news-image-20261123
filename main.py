"""news-image-20261123 v3 — one-day world news poster for Monday 23 Nov 2026.

Draws the poster from scratch with pure Python 3.13 stdlib: own 5x7 bitmap
font, own drawing primitives (rects, circles, lines, triangles, dotted
curves) and own manual PNG encoder. Writes entry.png into
MAKEFUN_OUTPUT_DIR (or ./entry.png when unset). Deterministic: no
randomness, no wall clock, no network.
"""

import math
import os
import struct
import sys
import zlib

W = 1024
H = 1024

# ---- palette ---------------------------------------------------------------
NAVY = (13, 27, 62)
NAVY_DARK = (9, 19, 44)
NAVY_MID = (21, 38, 80)
CREAM = (245, 238, 214)
GOLD = (212, 175, 55)
GOLD_DARK = (190, 150, 40)
WHITE = (255, 255, 255)
GREY = (110, 116, 128)
GREY_DARK = (70, 76, 90)
GREY_LIGHT = (200, 204, 212)
RED = (178, 34, 34)
RED_BRIGHT = (220, 60, 50)
ORANGE = (232, 120, 30)
YELLOW = (245, 200, 60)
BLUE = (40, 90, 180)
BLUE_SKY = (110, 165, 220)
GREEN = (34, 139, 60)
GREEN_BRIGHT = (60, 180, 90)
TILE_BG = (250, 246, 236)
SEA = (16, 52, 96)
SEA_LIGHT = (28, 78, 138)
SKY_NIGHT = (18, 28, 58)

# ---- 5x7 bitmap font -------------------------------------------------------
# Each glyph is 7 rows; each row is a 5-bit value (bit 4 = leftmost pixel).
# All poster text is rendered uppercase through this font.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "+": (0, 0x04, 0x04, 0x0E, 0x04, 0x04, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    "\u2022": (0, 0, 0x0E, 0x0E, 0x0E, 0, 0),  # bullet
}


# ---- canvas and drawing primitives ----------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

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
                self.px[i], self.px[i + 1], self.px[i + 2] = r, g, b

    def hline(self, x0, x1, y, color):
        self.rect(min(x0, x1), y, abs(x1 - x0) + 1, 1, color)

    def vline(self, x, y0, y1, color):
        self.rect(x, min(y0, y1), 1, abs(y1 - y0) + 1, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            if thick <= 1:
                self.set(x0, y0, color)
            else:
                self.rect(x0 - thick // 2, y0 - thick // 2, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color, thick=2):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if (r - thick) * (r - thick) <= d2 <= (r + thick) * (r + thick):
                    self.set(xx, yy, color)

    def triangle(self, pts, color):
        # Filled triangle by scanline.
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin = min(y0, y1, y2)
        ymax = max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by) or (yy == ymax and yy == max(ay, by)):
                    t = (yy - ay) / (by - ay)
                    xs.append(ax + t * (bx - ax))
            if len(xs) >= 2:
                self.hline(int(min(xs)), int(max(xs)), yy, color)

    def quad(self, pts, color):
        self.triangle((pts[0], pts[1], pts[2]), color)
        self.triangle((pts[0], pts[2], pts[3]), color)

    def dotted_curve(self, p0, p1, p2, color, step=0.02, dot=2):
        # Dotted quadratic bezier from p0 via control p1 to p2.
        t = 0.0
        while t <= 1.0 + 1e-9:
            u = 1.0 - t
            x = int(u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0])
            y = int(u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])
            self.circle(x, y, dot, color)
            t += step * 3.0

    def burst(self, cx, cy, r, color, color2=None):
        # Starburst: radiating spikes plus a filled core.
        for k in range(12):
            ang = k * 30.0 * math.pi / 180.0
            ex = int(cx + r * math.cos(ang))
            ey = int(cy + r * math.sin(ang))
            self.line(cx, cy, ex, ey, color, thick=3)
        self.circle(cx, cy, max(3, r // 3), color2 or YELLOW)


# ---- text ------------------------------------------------------------------
def text_width(text, scale):
    return len(text) * 6 * scale


def draw_text(cv, x, y, text, color, scale=2):
    """Draw text (uppercased) with top-left corner at (x, y)."""
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT["?"])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    cv.rect(cx + col * scale, y + row * scale, scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_right(cv, x_right, y, text, color, scale=2):
    draw_text(cv, x_right - text_width(text.upper(), scale), y, text, color, scale)


def draw_text_center(cv, cx, y, text, color, scale=2):
    draw_text(cv, cx - text_width(text.upper(), scale) // 2, y, text, color, scale)


def wrap_text(text, max_w, scale):
    """Greedy word wrap; returns a list of lines, each fitting max_w px."""
    per = max(1, max_w // (6 * scale))
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= per:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # A single over-long word is hard-split.
            while len(word) > per:
                lines.append(word[:per])
                word = word[per:]
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---- PNG encoder -----------------------------------------------------------
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png


# ---- picture scenes --------------------------------------------------------
def draw_hero_scene(cv, x0, y0, x1, y1):
    """Night sea, warship, two drones, blast flash. Region x0..x1, y0..y1."""
    cv.rect(x0, y0, x1 - x0, y1 - y0, SKY_NIGHT)
    # Stars.
    for sx, sy in ((30, 18), (90, 40), (150, 14), (210, 48), (260, 22),
                   (330, 44), (390, 16), (440, 52), (60, 70), (180, 66),
                   (300, 70), (420, 30), (120, 92), (360, 92)):
        cv.set(x0 + sx, y0 + sy, CREAM)
        cv.set(x0 + sx + 1, y0 + sy, CREAM)
    # Moon.
    cv.circle(x0 + 430, y0 + 40, 22, CREAM)
    cv.circle(x0 + 424, y0 + 34, 18, SKY_NIGHT)
    sea_top = y0 + (y1 - y0) * 3 // 5
    # Layered wave bands.
    cv.rect(x0, sea_top, x1 - x0, y1 - sea_top, SEA)
    cv.rect(x0, sea_top + 34, x1 - x0, 12, SEA_LIGHT)
    cv.rect(x0, sea_top + 76, x1 - x0, 10, SEA_LIGHT)
    for wx in range(x0 + 8, x1 - 8, 46):
        cv.hline(wx, wx + 26, sea_top + 20, SEA_LIGHT)
        cv.hline(wx + 12, wx + 38, sea_top + 58, (60, 120, 180))
        cv.hline(wx, wx + 22, sea_top + 96, (60, 120, 180))
    # Warship silhouette, centred low.
    ship_y = y1 - 118
    hull = [(x0 + 90, ship_y + 30), (x0 + 400, ship_y + 30),
            (x0 + 370, ship_y + 62), (x0 + 120, ship_y + 62)]
    cv.quad(hull, GREY_DARK)
    cv.rect(x0 + 150, ship_y, 180, 30, GREY)
    cv.rect(x0 + 200, ship_y - 26, 60, 26, GREY)
    cv.vline(x0 + 230, ship_y - 62, ship_y - 26, GREY_LIGHT)
    cv.triangle(((x0 + 230, ship_y - 62), (x0 + 230, ship_y - 44),
                 (x0 + 258, ship_y - 53)), RED_BRIGHT)  # small flag
    # Funnel with smoke.
    cv.rect(x0 + 300, ship_y - 14, 22, 16, GREY_DARK)
    cv.circle(x0 + 311, ship_y - 26, 8, GREY)
    cv.circle(x0 + 318, ship_y - 40, 10, GREY)
    # Two quadcopter drones with dotted flight paths.
    for dx, dy in ((x0 + 120, y0 + 118), (x0 + 330, y0 + 96)):
        cv.dotted_curve((dx, dy), (dx + 40, dy + 60), (x0 + 250, ship_y + 8),
                        GOLD_DARK, step=0.02, dot=2)
        cv.rect(dx - 10, dy - 5, 20, 10, GREY_LIGHT)
        cv.hline(dx - 18, dx - 8, dy - 8, WHITE)
        cv.hline(dx + 8, dx + 18, dy - 8, WHITE)
        cv.hline(dx - 18, dx - 8, dy + 8, WHITE)
        cv.hline(dx + 8, dx + 18, dy + 8, WHITE)
        cv.circle(dx, dy + 12, 3, RED_BRIGHT)
    # Orange blast flash near the ship's bow.
    cv.burst(x0 + 408, ship_y + 18, 26, ORANGE, YELLOW)
    draw_text(cv, x0 + 12, y1 - 26, "BENGHAZI PORT, LIBYA", GOLD, scale=2)


def draw_missile_scene(cv, x0, y0, x1, y1):
    """Dark sky, missile arc with dotted trail, explosion burst."""
    cv.rect(x0, y0, x1 - x0, y1 - y0, SKY_NIGHT)
    for sx, sy in ((14, 10), (60, 22), (110, 8), (170, 18), (230, 10),
                   (300, 20), (370, 12), (420, 24), (40, 34), (260, 32)):
        cv.set(x0 + sx, y0 + sy, CREAM)
    # Ground line and launch smoke.
    cv.rect(x0, y1 - 10, x1 - x0, 10, GREY_DARK)
    cv.circle(x0 + 52, y1 - 18, 12, GREY)
    cv.circle(x0 + 66, y1 - 26, 9, GREY)
    # Missile arc: dotted trail rising to the right, rocket at its head.
    cv.dotted_curve((x0 + 60, y1 - 22), (x0 + 240, y0 + 6),
                    (x0 + 420, y0 + 34), GOLD, step=0.02, dot=2)
    mx, my = x0 + 420, y0 + 34
    cv.triangle(((mx, my - 16), (mx - 8, my + 6), (mx + 8, my + 6)), WHITE)
    cv.rect(mx - 8, my + 6, 16, 12, GREY_LIGHT)
    cv.triangle(((mx - 6, my + 18), (mx + 6, my + 18), (mx, my + 30)),
                ORANGE)
    # Explosion burst at the arc's far end.
    cv.burst(x0 + 452, y0 + 22, 16, ORANGE, YELLOW)


def draw_jets_scene(cv, x0, y0, x1, y1):
    """Blue sky, two jet silhouettes, radar sweep arc."""
    cv.rect(x0, y0, x1 - x0, y1 - y0, BLUE_SKY)
    cv.circle(x0 + 430, y0 + 18, 16, CREAM)  # sun
    for cx, cy in ((20, 44), (90, 56), (200, 40), (320, 52)):
        cv.circle(x0 + cx, y0 + cy, 8, WHITE)
        cv.circle(x0 + cx + 12, y0 + cy + 3, 7, WHITE)
    # Radar sweep, fully inside the picture strip (bottom-left).
    rcx, rcy = x0 + 58, y1 - 30
    cv.ring(rcx, rcy, 26, NAVY, thick=2)
    cv.ring(rcx, rcy, 15, NAVY, thick=2)
    cv.line(rcx, rcy, rcx + 22, rcy - 20, NAVY, thick=2)
    cv.circle(rcx, rcy, 4, NAVY)
    # Two jets flying right.
    for jx, jy in ((210, 26), (300, 48)):
        cv.triangle(((x0 + jx, y0 + jy), (x0 + jx + 44, y0 + jy + 6),
                     (x0 + jx, y0 + jy + 12)), NAVY_DARK)
        cv.triangle(((x0 + jx + 14, y0 + jy), (x0 + jx + 22, y0 + jy - 12),
                     (x0 + jx + 26, y0 + jy)), NAVY_DARK)
        cv.triangle(((x0 + jx + 14, y0 + jy + 12), (x0 + jx + 22, y0 + jy + 24),
                     (x0 + jx + 26, y0 + jy + 12)), NAVY_DARK)
        cv.hline(x0 + jx - 26, x0 + jx - 2, y0 + jy + 6, WHITE)


def draw_chart_scene(cv, x0, y0, x1, y1):
    """Falling candlestick chart: red bars stepping down, one green bar up."""
    cv.rect(x0, y0, x1 - x0, y1 - y0, WHITE)
    cv.hline(x0 + 8, x1 - 8, y1 - 12, GREY)
    cv.vline(x0 + 12, y0 + 8, y1 - 12, GREY)
    bars = [(34, 16, 34, RED_BRIGHT), (86, 24, 40, RED_BRIGHT),
            (138, 34, 38, RED_BRIGHT), (190, 44, 36, RED_BRIGHT),
            (242, 52, 34, RED_BRIGHT), (294, 46, 30, RED_BRIGHT),
            (346, 36, 26, RED_BRIGHT), (398, 20, 34, GREEN_BRIGHT)]
    for bx, by, bh, col in bars:
        cv.vline(x0 + bx + 8, y0 + by - 6, y0 + by + bh + 6, col)
        cv.rect(x0 + bx, y0 + by, 16, bh, col)
    # Down arrow.
    cv.line(x0 + 40, y0 + 8, x0 + 360, y0 + 44, RED, thick=2)
    cv.triangle(((x0 + 360, y0 + 44), (x0 + 348, y0 + 38),
                 (x0 + 352, y0 + 52)), RED)
    draw_text_right(cv, x1 - 12, y0 + 4, "$55,100", RED, scale=2)


def draw_factory_scene(cv, x0, y0, x1, y1):
    """Factory block with orange flames and grey smoke columns."""
    cv.rect(x0, y0, x1 - x0, y1 - y0, (232, 220, 200))
    cv.rect(x0, y1 - 12, x1 - x0, 12, GREY_DARK)  # ground
    # Factory block and chimney.
    cv.rect(x0 + 90, y1 - 52, 220, 40, GREY_DARK)
    cv.rect(x0 + 330, y1 - 66, 26, 54, GREY)
    for wx in range(110, 290, 36):
        cv.rect(x0 + wx, y1 - 44, 16, 14, GOLD)
    # Flames on the roof.
    for fx in (130, 180, 235, 285):
        cv.triangle(((x0 + fx, y1 - 52), (x0 + fx + 12, y1 - 52),
                     (x0 + fx + 6, y1 - 78)), ORANGE)
        cv.triangle(((x0 + fx + 3, y1 - 52), (x0 + fx + 9, y1 - 52),
                     (x0 + fx + 6, y1 - 66)), YELLOW)
    # Smoke columns.
    for sx, sy, sr in ((360, 34, 12), (372, 18, 14), (352, 8, 10),
                       (170, 22, 10), (178, 8, 12)):
        cv.circle(x0 + sx, y0 + sy, sr, GREY)
    # Fire glow at the door.
    cv.rect(x0 + 196, y1 - 30, 24, 18, ORANGE)


# ---- poster assembly -------------------------------------------------------
def draw_tile(cv, x, y, w, h, scene, kicker, kicker_color, headline, deck):
    cv.rect(x, y, w, h, TILE_BG)
    cv.rect(x, y, w, 2, kicker_color)
    scene(cv, x + 1, y + 2, x + w - 1, y + 76)
    ky = y + 86
    draw_text(cv, x + 16, ky, kicker, kicker_color, scale=2)
    hy = ky + 24
    for line in wrap_text(headline, w - 32, 3):
        draw_text(cv, x + 16, hy, line, NAVY_DARK, scale=3)
        hy += 24
    dy = hy + 6
    for line in wrap_text(deck, w - 32, 2):
        draw_text(cv, x + 16, dy, line, GREY_DARK, scale=2)
        dy += 16


def build_poster():
    cv = Canvas(W, H, CREAM)
    # Masthead.
    cv.rect(0, 0, W, 100, NAVY)
    draw_text(cv, 24, 36, "THE WORLD TODAY", CREAM, scale=4)
    draw_text_right(cv, 1000, 36, "MONDAY 23 NOVEMBER 2026", GOLD, scale=4)
    cv.rect(0, 100, W, 4, GOLD)
    # Hero panel.
    cv.rect(0, 104, W, 392, NAVY_DARK)
    draw_hero_scene(cv, 16, 104, 512, 496)
    tx = 528
    draw_text(cv, tx, 140, "LIBYA \u2022 THE WAR AT SEA SPREADS", GOLD, scale=2)
    hy = 176
    for line in ("UKRAINE DRONES", "HIT RUSSIAN SHIPS", "IN LIBYA"):
        draw_text(cv, tx, hy, line, CREAM, scale=4)
        hy += 36
    dy = 300
    deck = ("KYIV CONFIRMS NAVAL DRONES STRUCK TWO RUSSIAN SHIPS AT "
            "BENGHAZI PORT - THE WAR REACHES THE MEDITERRANEAN.")
    for line in wrap_text(deck, 472, 2):
        draw_text(cv, tx, dy, line, WHITE, scale=2)
        dy += 18
    draw_text(cv, tx, 452, "SOURCE: REUTERS", GOLD, scale=2)
    # Red divider.
    cv.rect(0, 496, W, 6, RED)
    # 2x2 grid of tiles.
    tiles = [
        (16, 502, draw_missile_scene, "THE GULF", RED,
         "IRAN'S BIGGEST MISSILE WEEK IN A YEAR",
         "TEHRAN'S HEAVIEST WEEK OF MISSILES AND DRONES IN OVER A YEAR, "
         "TRUMP SAYS."),
        (520, 502, draw_jets_scene, "NATO \u2022 POLAND", BLUE,
         "NATO MEETS AS JETS SCRAMBLE",
         "EMERGENCY BRUSSELS MEETING; EARLY-WARNING PLANES SENT TO POLAND."),
        (16, 725, draw_chart_scene, "MARKETS", GREEN,
         "BITCOIN SINKS TO 2-YEAR LOW",
         "BITCOIN FALLS TO ABOUT $55,100, LOWEST SINCE SEPTEMBER 2024, "
         "THEN REBOUNDS."),
        (520, 725, draw_factory_scene, "INDONESIA", ORANGE,
         "FACTORY FIRE KILLS 24",
         "BLAZE AT A SWEETS FACTORY LEAVES 24 DEAD, ABOUT 30 MISSING."),
    ]
    for tx0, ty, scene, kicker, kcol, headline, deck in tiles:
        draw_tile(cv, tx0, ty, 488, 211, scene, kicker, kcol, headline, deck)
    # Footer.
    cv.rect(0, 936, W, 88, NAVY)
    draw_text_center(cv, 512, 952,
                     "EVERY STORY HAPPENED, OR WAS FIRST REPORTED, "
                     "ON MONDAY 23 NOVEMBER 2026.", WHITE, scale=2)
    draw_text_center(cv, 512, 978,
                     "SOURCES: REUTERS \u2022 BBC \u2022 COINDESK \u2022 AL JAZEERA",
                     WHITE, scale=2)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "."
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(build_poster())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    print("wrote %s (%d bytes)" % (path, len(png)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
