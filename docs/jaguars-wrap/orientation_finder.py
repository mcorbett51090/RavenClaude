#!/usr/bin/env python3
"""
Orientation finder — renders YOUR logo in all 8 orientations on the door panel,
labeled, into one contact sheet so you can pick the right one by eye.

    cd /workspaces/RavenClaude/docs/jaguars-wrap
    python3 orientation_finder.py      # -> writes orientations.png

Open orientations.png, find the tile where the head is upright and facing the
FRONT (up), read its ROTATE / FLIP_H values, and set those at the top of
place_logo.py. Then run place_logo.py.
"""

import glob
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
WRAP = os.path.join(HERE, "JAX_Jaguars_Wrap_clean.png")
CX, CY = 183, 520  # door-column center
MAX_W, MAX_H = 150, 350  # same fit box as place_logo.py
CROP = (70, 300, 320, 770)  # door region to show in each tile

_skip = {
    os.path.basename(WRAP).lower(),
    "jax_jaguars_wrap_final.png",
    "orientations.png",
    "preview.png",
}
cands = [
    p for p in glob.glob(os.path.join(HERE, "*.png")) if os.path.basename(p).lower() not in _skip
]
if not cands:
    raise SystemExit("Drop your transparent logo PNG in this folder, then rerun.")
LOGO = (
    os.path.join(HERE, "my_logo.png")
    if os.path.exists(os.path.join(HERE, "my_logo.png"))
    else cands[0]
)
print("using logo:", os.path.basename(LOGO))

wrap = Image.open(WRAP).convert("RGBA")
src = Image.open(LOGO).convert("RGBA")
src = src.crop(src.getbbox())


def render(rotate, flip_h):
    lg = src
    if rotate % 360:
        lg = lg.rotate(rotate, expand=True, resample=Image.BICUBIC)
        lg = lg.crop(lg.getbbox())
    if flip_h:
        lg = lg.transpose(Image.FLIP_LEFT_RIGHT)
    fit = min(MAX_W / lg.width, MAX_H / lg.height)
    lg = lg.resize((max(1, round(lg.width * fit)), max(1, round(lg.height * fit))), Image.LANCZOS)
    layer = Image.new("RGBA", wrap.size, (0, 0, 0, 0))
    layer.alpha_composite(lg, (CX - lg.width // 2, CY - lg.height // 2))
    comp = Image.new("RGBA", wrap.size, (18, 24, 30, 255))
    comp.alpha_composite(wrap)
    comp.alpha_composite(layer)
    return comp.crop(CROP)


combos = [(r, f) for f in (False, True) for r in (0, 90, 180, 270)]
tiles = []
for i, (r, f) in enumerate(combos, 1):
    t = render(r, f).convert("RGB")
    lab = Image.new("RGB", (t.width, t.height + 30), (12, 16, 20))
    lab.paste(t, (0, 30))
    ImageDraw.Draw(lab).text((8, 9), f"#{i}   ROTATE={r}  FLIP_H={f}", fill=(233, 244, 240))
    tiles.append(lab)

tw, th = tiles[0].size
sheet = Image.new("RGB", (tw * 4, th * 2), (12, 16, 20))
for idx, t in enumerate(tiles):
    sheet.paste(t, ((idx % 4) * tw, (idx // 4) * th))
out = os.path.join(HERE, "orientations.png")
sheet.save(out)
print("wrote", out, "-> open it, pick the tile that's upright + facing UP, use its ROTATE/FLIP_H")
