# poster.py — draws "The World in One Day", a 1024x1024 poster summing up
# the world news of Thursday 26 November 2026.
#
# Pure Python 3 standard library: the PNG bytes are encoded by hand
# (zlib + struct + binascii) and the text is set with a small bitmap
# font defined below, so the program needs no network and no fonts
# installed on the machine that runs it. The render is fully
# deterministic: the same input always produces the same PNG bytes.

import binascii
import struct
import sys
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------- font
# A 5x7 bitmap font. Each glyph is 7 rows of 5 cells; '#' is ink.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    "q": ("00000", "01111", "10001", "10001", "01111", "00001", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11110", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10001", "01111"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "\u00b7": ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    "\u2022": ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    "\u00b0": ("01100", "10010", "10010", "01100", "00000", "00000", "00000"),
    "\u20ac": ("00111", "01000", "11110", "01000", "11110", "01000", "00111"),
    "\u00d7": ("00000", "10001", "01010", "00100", "01010", "10001", "00000"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    "\u2014": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "\u2019": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
}
BLANK = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")

# ------------------------------------------------------------- palette
BG = (13, 27, 46)
HEADER_BG = (10, 21, 38)
PANEL = (19, 42, 69)
PANEL_EDGE = (38, 68, 100)
WHITE = (245, 247, 250)
LIGHT = (184, 196, 212)
DIM = (126, 147, 171)
AMBER = (242, 169, 0)
AMBER_DARK = (214, 148, 0)
RULE = (46, 78, 112)

# Region accent colours, one per section.
ACCENTS = {
    "TOP STORIES": (242, 169, 0),
    "UNITED STATES": (76, 154, 255),
    "LATIN AMERICA": (46, 204, 113),
    "EUROPE": (155, 126, 222),
    "MIDDLE EAST": (255, 107, 94),
    "AFRICA": (255, 176, 32),
    "ASIA": (56, 198, 198),
    "PACIFIC": (126, 217, 87),
    "TRADE & MARKETS": (232, 106, 168),
    "SCIENCE & CLIMATE": (143, 211, 255),
}

# ------------------------------------------------------------- content
# (headline, detail) pairs, all events of Thursday 26 November 2026
# as first reported that day by wire and press reports.
SECTIONS = [
    ("TOP STORIES", [
        ("US proposes tariffs on 14", "China up to 20%; Vietnam 35%"),
        ("Tankers \u2018hit by mines\u2019", "Iran claims Hormuz mine strike"),
        ("Kyiv mall hit in strikes", "7 wounded in overnight attacks"),
    ]),
    ("UNITED STATES", [
        ("Macy\u2019s parade postponed", "First delay in 100 years: storm"),
        ("Storm knocks out power", "Hundreds of thousands in dark"),
        ("Birthright order blocked", "Court lets Trump freeze aid"),
    ]),
    ("LATIN AMERICA", [
        ("Cartagena siege ends", "30 hostages freed after 17 hours"),
        ("Mexico slams DEA tip lines", "President criticises US agency"),
        ("Milei reforms face Senate", "Upper house votes on package"),
    ]),
    ("EUROPE", [
        ("EU split over Ukraine loan", "\u20ac45bn for 2027 divides leaders"),
        ("Synagogue plot foiled", "Two suspects arrested in Germany"),
        ("UK migration at 77,000", "Lowest since 1997 outside Covid"),
    ]),
    ("MIDDLE EAST", [
        ("Gaza strikes kill nine", "Hamas official among the dead"),
        ("Netanyahu charge in doubt", "Judges urge bribery case dropped"),
        ("Houthis hit Saudi refinery", "One worker killed at Jazan"),
    ]),
    ("AFRICA", [
        ("Cairo tanker fire kills 31", "Ring Road crash chars 27 vehicles"),
        ("Ebola cases pass 12,000", "Fighting forces responders to flee"),
        ("Kenya halts Ebola facility", "Court cites lack of consultation"),
    ]),
    ("ASIA", [
        ("Kim to build more nukes", "Tours sites, snubs Trump overture"),
        ("Bangkok refinery blast", "Explosion injures nine workers"),
        ("Bogor mine flood kills 13", "Illegal gold mine; 13 still missing"),
    ]),
    ("PACIFIC", [
        ("Solomons choose Australia", "Treaty bars foreign military bases"),
        ("Bushfire summer looms", "Extreme heatwaves forecast"),
        ("NZ awaits next government", "Close election decided on Friday"),
    ]),
    ("TRADE & MARKETS", [
        ("F-16 support for Ukraine", "US approves $522m package"),
        ("Oil climbs on Hormuz fears", "Houthi refinery strike lifts prices"),
        ("Nvidia halts China chips", "Curbs tighten via third countries"),
    ]),
    ("SCIENCE & CLIMATE", [
        ("2\u00b0C topped for six days", "Copernicus: first time on record"),
        ("Ozone hole near record", "ESA: 27.3m sq km at its peak"),
        ("Gauteng streets flooded", "Severe storms batter South Africa"),
    ]),
]

FOOTER_1 = "30 stories \u00b7 10 regions \u00b7 Thursday 26 November 2026, as first reported"
FOOTER_2 = "Unconfirmed claims labelled as claims \u00b7 Wire reports of 26 November 2026"

# ------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(bg * (width * height))

    def _idx(self, x, y):
        return (y * self.w + x) * 3

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            span = (x1 - x0) * 3
            self.px[base:base + span] = bytes(color) * (x1 - x0)

    def hline(self, x, y, w, color):
        self.fill_rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.fill_rect(x, y, 1, h, color)

    def circle(self, cx, cy, r, color):
        # Midpoint circle outline.
        x = 0
        y = r
        d = 1 - r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y),
                           (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.set(px, py, color)
            x += 1
            if d < 0:
                d += 2 * x + 1
            else:
                y -= 1
                d += 2 * (x - y) + 1

    def ellipse_arc(self, cx, cy, rx, ry, color):
        # A vertical meridian: sample the ellipse and plot points.
        import math
        steps = 360
        for i in range(steps):
            a = 2 * math.pi * i / steps
            x = int(round(cx + rx * math.cos(a)))
            y = int(round(cy + ry * math.sin(a)))
            self.set(x, y, color)

# ------------------------------------------------------------- text
def text_width(text, scale, bold=False):
    w = 0
    for ch in text:
        w += 6 * scale
    if text:
        w -= scale  # no trailing gap after the last glyph
    if bold:
        w += 1
    return w


def draw_text(cv, x, y, text, scale, color, bold=False):
    cx = x
    for ch in text:
        glyph = FONT.get(ch, BLANK)
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    cv.fill_rect(cx + col * scale, y + row * scale,
                                 scale, scale, color)
                    if bold:
                        cv.fill_rect(cx + col * scale + 1, y + row * scale,
                                     scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_right(cv, right, y, text, scale, color, bold=False):
    draw_text(cv, right - text_width(text, scale, bold), y, text, scale,
              color, bold)

# ------------------------------------------------------------- png
def encode_png(width, height, px):
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)  # filter: none
        raw += px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))

# ------------------------------------------------------------- poster
def render_poster():
    cv = Canvas(WIDTH, HEIGHT, BG)
    cv.fill_rect(0, 0, WIDTH, 124, HEADER_BG)

    # Globe emblem in the header.
    gx, gy, gr = 66, 62, 38
    cv.circle(gx, gy, gr, AMBER)
    cv.circle(gx, gy, gr - 2, AMBER_DARK)
    cv.ellipse_arc(gx, gy, 16, gr - 3, AMBER_DARK)
    cv.ellipse_arc(gx, gy, 30, gr - 3, AMBER_DARK)
    cv.hline(gx - gr + 3, gy, 2 * gr - 6, AMBER_DARK)
    cv.hline(gx - 30, gy - 22, 60, AMBER_DARK)
    cv.hline(gx - 30, gy + 22, 60, AMBER_DARK)
    cv.set(gx - 18, gy - 12, AMBER)
    cv.set(gx + 12, gy + 14, AMBER)

    # Header text.
    draw_text(cv, 124, 26, "THE WORLD IN ONE DAY", 4, AMBER, bold=True)
    draw_text(cv, 124, 74, "Thursday 26 November 2026", 4, WHITE, bold=True)
    draw_text_right(cv, WIDTH - 16, 30, "30 STORIES", 2, LIGHT, bold=True)
    draw_text_right(cv, WIDTH - 16, 52, "10 REGIONS", 2, LIGHT, bold=True)
    draw_text_right(cv, WIDTH - 16, 74, "ONE DAY", 2, LIGHT, bold=True)
    draw_text_right(cv, WIDTH - 16, 96, "AS REPORTED", 2, DIM)
    cv.fill_rect(0, 124, WIDTH, 3, AMBER)

    # Story grid: 2 columns x 5 rows of region blocks.
    margin = 16
    gap_x = 16
    gap_y = 11
    col_w = (WIDTH - 2 * margin - gap_x) // 2
    row_h = 158
    top = 136
    for idx, (region, stories) in enumerate(SECTIONS):
        col = idx % 2
        row = idx // 2
        bx = margin + col * (col_w + gap_x)
        by = top + row * (row_h + gap_y)
        accent = ACCENTS[region]
        cv.fill_rect(bx, by, col_w, row_h, PANEL)
        cv.fill_rect(bx, by, col_w, 3, accent)
        cv.fill_rect(bx, by, 4, row_h, accent)
        # Region label.
        draw_text(cv, bx + 14, by + 12, region, 2, accent, bold=True)
        # Stories.
        sy = by + 36
        for head, detail in stories:
            draw_text(cv, bx + 14, sy, head, 3, WHITE, bold=True)
            draw_text(cv, bx + 14, sy + 23, detail, 2, LIGHT)
            sy += 42

    # Footer.
    cv.fill_rect(0, 978, WIDTH, 1, RULE)
    draw_text(cv, margin, 986, FOOTER_1, 2, DIM)
    draw_text(cv, margin, 1002, FOOTER_2, 2, DIM)
    return encode_png(WIDTH, HEIGHT, cv.px)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "poster.png"
    with open(path, "wb") as fh:
        fh.write(render_poster())


if __name__ == "__main__":
    main()
