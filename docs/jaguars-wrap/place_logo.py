#!/usr/bin/env python3
"""
Place YOUR logo onto the recolored Jaguars Model Y wrap, mirrored so it lands on
both door panels with both copies facing the front of the car.

Drop a transparent logo PNG in this folder (it's auto-detected). Set FACING below
to match which way your art points, then run.

HOW TO RUN (copy/paste):
    cd /workspaces/RavenClaude/docs/jaguars-wrap
    pip install pillow          # only if PIL isn't installed
    python3 place_logo.py       # -> writes JAX_Jaguars_Wrap_FINAL.png

PREVIEW IT (composites over a dark bg so the transparent masks read):
    python3 -c "from PIL import Image; b=Image.new('RGBA',(1024,1024),(18,24,30,255)); b.alpha_composite(Image.open('JAX_Jaguars_Wrap_FINAL.png').convert('RGBA')); b.convert('RGB').save('preview.png')"
    # then open preview.png

LOAD INTO THE CAR:
    USB (exFAT, not NTFS) -> folder named 'Wraps' at the root -> copy the FINAL png in
    (<=1 MB, name <=30 chars) -> front USB-C port -> Toybox > Paint Shop > Wraps > tap it.
"""

import os

from PIL import Image

# --- tune here -------------------------------------------------------------
# ROTATE: degrees to spin your logo (counter-clockwise) BEFORE it's placed.
#   The head must end up pointing UP (= front of the car). For a source whose
#   head faces RIGHT, 90 stands it up facing FRONT (verified). Cheat sheet:
#     90  = head-faces-RIGHT -> points up/front     270 = -> points down/rear
#     270 = head-faces-LEFT  -> points up/front      90 = -> points down/rear
#   If it ends up rear-facing, use the OTHER of 90/270 (don't use FLIP_H for that).
ROTATE = 90
# FLIP_H: head points up (front) either way; this only chooses which side the
#   jaguar's belly/legs face. False = belly toward the image EDGE = the ground/
#   bottom of the car (correct). True put the belly toward center = the roof.
FLIP_H = True
MAX_W, MAX_H = 150, 350  # full size restored
# On this UV, the car's GROUND/wheel side = the image EDGE (not the image bottom).
# So "toward the rear wheel well" = shift the left-door logo toward the LEFT edge;
# the right door auto-mirrors, moving its logo toward the RIGHT edge. Lower CX = more
# outward (toward the wheel well); CY = up/down along the car.
CX, CY = 180, 770  # lifted 30px so the tail clears the panel seam gap (was clipping at 800)

# --- Florida state flag (public-domain), added to both doors ---------------
ADD_FLAG = True
# Per-side rotation so the seal sits UPRIGHT on the car (sky toward the roof).
# The doors need OPPOSITE spins because the roof = image-CENTER on both sides.
# Want a plain horizontal flag in the flat file instead? set both to 0.
FLAG_ROTATE_L, FLAG_ROTATE_R = 270, 90
FLAG_MAX_W, FLAG_MAX_H = 24, 36  # 70% larger than the tiny version (rotated flag is portrait)
FLAG_CX, FLAG_CY = 240, 317  # nudged 5px toward the outside (down the car)
# ---------------------------------------------------------------------------

import glob

HERE = os.path.dirname(os.path.abspath(__file__))
WRAP = os.path.join(HERE, "JAX_Jaguars_Wrap_clean.png")
OUT = os.path.join(HERE, "JAX_Jaguars_Wrap_FINAL.png")

# auto-detect the logo you dropped in: any PNG here that isn't the wrap/output
_skip = {os.path.basename(WRAP).lower(), os.path.basename(OUT).lower(), "florida_flag.png"}
_cands = [
    p for p in glob.glob(os.path.join(HERE, "*.png")) if os.path.basename(p).lower() not in _skip
]
if not _cands:
    raise SystemExit("Drop your transparent logo PNG in this folder, then rerun.")
LOGO = (
    os.path.join(HERE, "my_logo.png")
    if os.path.exists(os.path.join(HERE, "my_logo.png"))
    else _cands[0]
)
print("using logo:", os.path.basename(LOGO))

wrap = Image.open(WRAP).convert("RGBA")
logo = Image.open(LOGO).convert("RGBA")
logo = logo.crop(logo.getbbox())  # trim empty margins

# rotate so the head points UP = the front of the car (per Tesla's UV orientation)
if ROTATE % 360:
    logo = logo.rotate(ROTATE, expand=True, resample=Image.BICUBIC)
    logo = logo.crop(logo.getbbox())

# mirror left-right so the head faces the FRONT (not the rear) of the car
if FLIP_H:
    logo = logo.transpose(Image.FLIP_LEFT_RIGHT)

# scale to FIT inside the door box (whichever of width/height is tighter) -> no overflow
fit = min(MAX_W / logo.width, MAX_H / logo.height)
logo = logo.resize(
    (max(1, round(logo.width * fit)), max(1, round(logo.height * fit))), Image.LANCZOS
)

left = Image.new("RGBA", wrap.size, (0, 0, 0, 0))
left.alpha_composite(logo, (CX - logo.width // 2, CY - logo.height // 2))
right = left.transpose(Image.FLIP_LEFT_RIGHT)  # mirror to the right door

out = wrap.copy()
out.alpha_composite(left)
out.alpha_composite(right)

# Florida flag on both doors; per-side rotation -> seal upright on the car, never mirrored
FLAG = os.path.join(HERE, "florida_flag.png")
if ADD_FLAG and os.path.exists(FLAG):
    _flag_base = Image.open(FLAG).convert("RGBA")

    def _prep_flag(rot):
        f = _flag_base.rotate(rot, expand=True, resample=Image.BICUBIC) if rot % 360 else _flag_base
        s = min(FLAG_MAX_W / f.width, FLAG_MAX_H / f.height)
        return f.resize((max(1, round(f.width * s)), max(1, round(f.height * s))), Image.LANCZOS)

    flL, flR = _prep_flag(FLAG_ROTATE_L), _prep_flag(FLAG_ROTATE_R)
    out.alpha_composite(flL, (FLAG_CX - flL.width // 2, FLAG_CY - flL.height // 2))  # left door
    out.alpha_composite(
        flR, (wrap.width - FLAG_CX - flR.width // 2, FLAG_CY - flR.height // 2)
    )  # right
    print(f"flags placed L{flL.size} R{flR.size} at CX={FLAG_CX} CY={FLAG_CY}")

out.save(OUT, optimize=True)

kb = os.path.getsize(OUT) / 1024
if kb > 1000:  # stay under Tesla's 1 MB cap
    out.quantize(colors=220, method=Image.FASTOCTREE).save(OUT, optimize=True)
    kb = os.path.getsize(OUT) / 1024
print(f"wrote {OUT}  ({kb:.0f} KB, {out.size[0]}x{out.size[1]})")
