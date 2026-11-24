#!/usr/bin/env python3
"""news-image-20261123 v3: a 1024x1024 newspaper front page summing up
Monday 23 November 2026's world news. Pure Python standard library only.
Draws every pixel itself (hand-written 5x7 bitmap font, minimal PNG writer)
and writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).
Deterministic: no randomness, no clock, no network."""

import hashlib
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 242, 231)
INK = (26, 26, 26)
NAVY = (20, 33, 61)
GOLD = (201, 162, 39)
RED = (179, 39, 30)
WHITE = (255, 255, 255)
GREY = (141, 153, 174)
DIM = (60, 60, 60)
DUSK = (43, 58, 74)
NIGHT = (16, 16, 16)
FLAME = (232, 93, 4)
FLAME2 = (250, 163, 7)
MOON = (244, 211, 94)

# 5x7 bitmap font: each glyph is 7 rows of 5 characters, '#' = on.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".....", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".....", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ':': (".....", ".##..", ".....", ".....", ".....", ".##..", "....."),
    ';': (".....", ".##..", ".....", ".....", ".....", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '%': ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(c)

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.fill_rect(x - t // 2, y - t // 2, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def fill_circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.px(xx, yy, c)

    def fill_triangle(self, a, b, c, col):
        pts = sorted([a, b, c], key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = pts

        def interp(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)

        for y in range(y0, y2 + 1):
            if y < y1:
                xa = interp(x0, y0, x2, y2, y)
                xb = interp(x0, y0, x1, y1, y)
            else:
                xa = interp(x0, y0, x2, y2, y)
                xb = interp(x1, y1, x2, y2, y)
            xlo, xhi = int(min(xa, xb)), int(max(xa, xb))
            self.fill_rect(xlo, y, xhi - xlo + 1, 1, col)

    def text(self, x, y, s, scale, c, align="left"):
        s = s.upper()  # font is uppercase-only; captions render as caps
        w = len(s) * 6 * scale - scale
        if align == "center":
            x -= w // 2
        cx = x
        for ch in s:
            g = FONT.get(ch)
            if g:
                for r in range(7):
                    row = g[r]
                    for col in range(5):
                        if row[col] == "#":
                            self.fill_rect(cx + col * scale, y + r * scale,
                                           scale, scale, c)
            cx += 6 * scale
        return w

    @staticmethod
    def wrap(s, max_chars):
        lines, cur = [], ""
        for wd in s.split(" "):
            if cur and len(cur) + 1 + len(wd) > max_chars:
                lines.append(cur)
                cur = wd
            else:
                cur = (cur + " " + wd) if cur else wd
        if cur:
            lines.append(cur)
        return lines


def write_png(path, cv):
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + bytes(cv.buf[y * cv.w * 3:(y + 1) * cv.w * 3])
                   for y in range(cv.h))
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return png


# ---------------- panel art strips (ax, ay, aw, ah) = 304 x 60 ----------------

def art_gaza(cv, ax, ay, aw, ah):
    cv.fill_rect(ax, ay, aw, 20, (217, 192, 138))
    cv.fill_rect(ax, ay + 20, aw, 20, (122, 122, 58))
    cv.fill_rect(ax, ay + 40, aw, 20, (107, 79, 42))
    cv.fill_triangle((ax + 205, ay + 56), (ax + 255, ay + 56),
                     (ax + 230, ay + 6), MOON)
    cv.text(ax + 224, ay + 28, "!", 2, INK)


def art_hormuz(cv, ax, ay, aw, ah):
    cv.fill_rect(ax, ay, aw, 24, (232, 224, 208))
    cv.fill_rect(ax, ay + 24, aw, 36, (27, 73, 101))
    cv.fill_rect(ax + 40, ay + 18, 20, 16, RED)
    cv.fill_rect(ax + 62, ay + 18, 20, 16, (0, 56, 147))
    cv.fill_rect(ax + 84, ay + 22, 20, 12, (19, 136, 8))
    cv.fill_triangle((ax + 120, ay + 34), (ax + 132, ay + 12),
                     (ax + 144, ay + 34), FLAME)
    cv.fill_triangle((ax + 20, ay + 34), (ax + 150, ay + 34),
                     (ax + 140, ay + 52), NIGHT)
    cv.fill_triangle((ax + 20, ay + 34), (ax + 140, ay + 52),
                     (ax + 30, ay + 52), NIGHT)
    for wx in (170, 210, 250):
        cv.fill_rect(ax + wx, ay + 44, 24, 3, WHITE)


def art_delhi(cv, ax, ay, aw, ah):
    cv.fill_rect(ax, ay, aw, ah, (244, 227, 192))
    cv.fill_rect(ax + 18, ay + 8, 2, 40, INK)
    cv.fill_rect(ax + 20, ay + 8, 36, 7, (255, 153, 51))
    cv.fill_rect(ax + 20, ay + 15, 36, 6, WHITE)
    cv.fill_rect(ax + 20, ay + 21, 36, 7, (19, 136, 8))
    cv.fill_rect(ax + 68, ay + 8, 2, 40, INK)
    cv.fill_rect(ax + 70, ay + 8, 30, 20, (0, 56, 147))
    cv.fill_rect(ax + 72, ay + 10, 26, 16, (220, 20, 60))
    cv.fill_rect(ax + 130, ay + 26, 50, 26, (0, 100, 0))
    cv.fill_rect(ax + 184, ay + 30, 40, 22, (0, 80, 0))
    cv.fill_rect(ax + 228, ay + 30, 40, 22, (0, 80, 0))
    for wx in (140, 160, 192, 208, 236, 252):
        cv.fill_rect(ax + wx, ay + 32, 10, 8, MOON)
    for wx in (145, 165, 200, 244):
        cv.fill_circle(ax + wx, ay + 54, 4, NIGHT)
    cv.fill_rect(ax + 120, ay + 58, 160, 2, INK)


def art_seoul(cv, ax, ay, aw, ah):
    cv.fill_rect(ax, ay, aw, ah, (232, 232, 228))
    cv.fill_triangle((ax + 85, ay + 20), (ax + 215, ay + 20),
                     (ax + 150, ay + 4), (120, 120, 120))
    cv.fill_rect(ax + 90, ay + 20, 120, 36, (120, 120, 120))
    for i in range(4):
        cv.fill_rect(ax + 100 + i * 28, ay + 26, 8, 30, WHITE)
    cv.fill_rect(ax + 142, ay + 40, 16, 16, NIGHT)
    cv.fill_rect(ax + 250, ay + 6, 2, 50, INK)
    cv.fill_rect(ax + 252, ay + 6, 28, 18, WHITE)
    cv.fill_circle(ax + 266, ay + 12, 5, RED)
    cv.fill_circle(ax + 266, ay + 18, 5, (0, 56, 147))


def art_nvidia(cv, ax, ay, aw, ah):
    cv.fill_rect(ax, ay, aw, ah, (15, 15, 15))
    for px in (30, 42, 54):
        cv.fill_rect(ax + px, ay + 2, 8, 6, (118, 185, 0))
        cv.fill_rect(ax + px, ay + 52, 8, 6, (118, 185, 0))
    for py in (14, 26, 38):
        cv.fill_rect(ax + 24, ay + py, 6, 8, (118, 185, 0))
        cv.fill_rect(ax + 74, ay + py, 6, 8, (118, 185, 0))
    cv.fill_rect(ax + 30, ay + 8, 44, 44, (118, 185, 0))
    cv.fill_rect(ax + 42, ay + 20, 20, 20, (15, 15, 15))
    cv.fill_triangle((ax + 110, ay + 50), (ax + 130, ay + 14),
                     (ax + 150, ay + 50), (118, 185, 0))
    cv.fill_rect(ax + 124, ay + 34, 12, 20, (118, 185, 0))
    cv.text(ax + 200, ay + 26, "NVDA", 2, WHITE)


def art_markets(cv, ax, ay, aw, ah):
    cv.fill_rect(ax, ay, aw, ah, WHITE)
    cv.fill_rect(ax + 20, ay + 50, 240, 2, INK)
    cv.fill_rect(ax + 20, ay + 8, 2, 42, INK)
    pts = [(30, 20), (70, 30), (110, 26), (150, 44), (190, 40), (230, 28)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        col = RED if x1 <= 150 else (19, 136, 8)
        cv.line(ax + x0, ay + y0, ax + x1, ay + y1, col, 3)
    for (px, py) in pts:
        cv.fill_circle(ax + px, ay + py, 3, INK)


PANELS = [
    ("GAZA", RED, ["99% OF GAZA", "CONTAMINATED"],
     "Oxfam: war debris poisons soil and water.", art_gaza),
    ("STRAIT OF HORMUZ", (27, 73, 101), ["TANKERS HIT", "AT WAR HIGH"],
     "Iran says two tankers hit mines.", art_hormuz),
    ("NEW DELHI", (19, 136, 8), ["MODI MEETS", "NEPAL'S PM"],
     "Eight deals signed; train flagged off.", art_delhi),
    ("SEOUL", (0, 56, 147), ["LEE SHUFFLES", "THE CABINET"],
     "Four new ministers after exam scandal.", art_seoul),
    ("SANTA CLARA", (118, 185, 0), ["HUANG'S BACK", "AT NVIDIA"],
     "Co-founder returns as CEO after quitting.", art_nvidia),
    ("ASIA MARKETS", (107, 79, 42), ["ASIA ACTS ON", "STOCK SLIDE"],
     "Regulators step in after the AI stock sell-off.", art_markets),
]


def draw_hero(cv):
    ax, ay, aw, ah = 16, 120, 384, 304
    cv.fill_rect(ax, ay, aw, ah, DUSK)
    for (sx, sy) in [(40, 140), (90, 132), (150, 146), (210, 134), (260, 150),
                     (330, 138), (370, 160), (60, 170), (300, 180), (180, 128)]:
        cv.fill_rect(sx, sy, 3, 3, (220, 220, 200))
    cv.fill_rect(ax, ay + 220, aw, ah - 220, (24, 24, 24))
    for (cx, cy, r) in [(296, 168, 14), (312, 148, 17), (330, 128, 13),
                        (300, 196, 11)]:
        cv.fill_circle(cx, cy, r, GREY)
    cv.fill_rect(276, 190, 26, 150, NIGHT)
    cv.fill_rect(312, 214, 22, 126, NIGHT)
    cv.fill_rect(52, 250, 210, 90, NIGHT)
    cv.fill_triangle((52, 250), (92, 222), (132, 250), NIGHT)
    cv.fill_triangle((132, 250), (172, 222), (212, 250), NIGHT)
    cv.fill_triangle((212, 250), (242, 226), (262, 250), NIGHT)
    for wx in (70, 110, 150, 190, 225):
        cv.fill_rect(wx, 280, 16, 20, MOON)
    cv.fill_triangle((80, 250), (104, 196), (128, 250), FLAME)
    cv.fill_triangle((96, 250), (112, 214), (128, 250), FLAME2)
    cv.fill_triangle((150, 250), (176, 200), (202, 250), FLAME)
    cv.fill_triangle((166, 250), (180, 218), (196, 250), FLAME2)
    cv.fill_triangle((222, 250), (240, 212), (258, 250), FLAME)
    cv.fill_rect(424, 128, 240, 30, RED)
    cv.text(436, 135, "CIKANDE, INDONESIA", 2, WHITE)
    cv.text(424, 176, "FACTORY FIRE", 6, INK)
    cv.text(424, 224, "TOLL: 24 DEAD", 6, INK)
    cap = ("Indonesia confirms 24 killed and about 30 still missing after "
           "a fire at a candy factory in Banten.")
    y = 296
    for ln in Canvas.wrap(cap, 32):
        cv.text(424, y, ln, 3, DIM)
        y += 28


def draw_panel(cv, x, y, tag, tagc, head, cap, art):
    cv.fill_rect(x, y, 320, 272, WHITE)
    cv.fill_rect(x, y, 320, 2, INK)
    cv.fill_rect(x, y + 270, 320, 2, INK)
    cv.fill_rect(x, y, 2, 272, INK)
    cv.fill_rect(x + 318, y, 2, 272, INK)
    art(cv, x + 8, y + 8, 304, 60)
    tw = len(tag) * 12 + 16
    cv.fill_rect(x + 8, y + 76, tw, 22, tagc)
    cv.text(x + 16, y + 81, tag, 2, WHITE)
    hy = y + 106
    for ln in head:
        cv.text(x + 16, hy, ln, 4, INK)
        hy += 36
    cy = y + 184
    for ln in Canvas.wrap(cap, 16)[:3]:
        cv.text(x + 16, cy, ln, 3, DIM)
        cy += 26


def draw_page(cv):
    cv.fill_rect(0, 0, W, 100, NAVY)
    cv.text(512, 14, "MONDAY - THE WORLD IN ONE DAY", 3, GOLD, "center")
    cv.text(512, 40, "23 NOVEMBER 2026", 8, WHITE, "center")
    cv.fill_rect(0, 100, W, 4, GOLD)
    draw_hero(cv)
    cv.fill_rect(16, 448, W - 32, 2, INK)
    for i, (tag, tagc, head, cap, art) in enumerate(PANELS):
        col, row = i % 3, i // 3
        x = 16 + col * (320 + 12)
        y = 456 + row * (272 + 8)
        draw_panel(cv, x, y, tag, tagc, head, cap, art)
    cv.text(512, 1006, "ALL EVENTS REPORTED ON MONDAY 23 NOVEMBER 2026",
            2, (120, 120, 120), "center")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = Canvas(W, H, PAPER)
    draw_page(cv)
    path = os.path.join(out_dir, "entry.png")
    png = write_png(path, cv)
    print("wrote %s %d bytes sha256=%s" % (path, len(png),
          hashlib.sha256(png).hexdigest()))


if __name__ == "__main__":
    main()
