#!/usr/bin/env python3
"""Render a simplified Flag of Florida (public-domain state flag) as a PNG:
white field, red saltire, and a circular state-seal medallion."""

import math
import os

from PIL import Image, ImageDraw

SS = 4
W, H = 300 * SS, 200 * SS
RED = (206, 17, 38)
WHITE = (255, 255, 255)
SKY = (150, 200, 230)
WATER = (40, 110, 165)
GROUND = (150, 170, 110)
SUN = (240, 200, 70)
PALM = (35, 110, 55)
GOLD = (196, 160, 70)
INK = (60, 45, 30)

im = Image.new("RGBA", (W, H), WHITE + (255,))
d = ImageDraw.Draw(im)
# red saltire (corner-to-corner diagonals)
bw = int(H * 0.16)
d.line([(0, 0), (W, H)], fill=RED, width=bw)
d.line([(W, 0), (0, H)], fill=RED, width=bw)

# central seal medallion
cx, cy = W // 2, H // 2
R = int(H * 0.40)
d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=GOLD)  # outer ring
r = int(R * 0.86)
d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE)  # inner field
# clip scene to inner circle via a mask
scene = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(scene)
sd.rectangle([cx - r, cy - r, cx + r, cy + int(r * 0.15)], fill=SKY)  # sky
sd.rectangle([cx - r, cy + int(r * 0.15), cx + r, cy + r], fill=WATER)  # water
sd.rectangle([cx - r, cy + int(r * 0.05), cx + r, cy + int(r * 0.22)], fill=GROUND)  # shoreline
# sun + rays (left)
sx, sy, sr = cx - int(r * 0.42), cy - int(r * 0.30), int(r * 0.20)
for a in range(0, 360, 30):
    sd.line(
        [
            (sx, sy),
            (sx + math.cos(math.radians(a)) * sr * 1.9, sy + math.sin(math.radians(a)) * sr * 1.9),
        ],
        fill=SUN,
        width=SS * 2,
    )
sd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=SUN)
# sabal palm (right): trunk + fronds
tx, ty = cx + int(r * 0.34), cy + int(r * 0.10)
sd.line([(tx, ty), (tx - int(r * 0.05), cy - int(r * 0.45))], fill=(120, 90, 55), width=SS * 4)
hx, hy = tx - int(r * 0.05), cy - int(r * 0.45)
for a in (150, 175, 205, 235, 265, 300):
    sd.line(
        [
            (hx, hy),
            (hx + math.cos(math.radians(a)) * r * 0.42, hy + math.sin(math.radians(a)) * r * 0.42),
        ],
        fill=PALM,
        width=SS * 3,
    )
mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(mask).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
im.paste(scene, (0, 0), Image.composite(mask, Image.new("L", (W, H), 0), scene.split()[3]))
d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=SS * 2)  # seal outline
d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=INK, width=SS)  # ring outline

im = im.resize((300, 200), Image.LANCZOS)
here = os.path.dirname(os.path.abspath(__file__))
im.save(os.path.join(here, "florida_flag.png"))
print("saved florida_flag.png", im.size)
