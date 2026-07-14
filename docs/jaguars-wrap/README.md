# Jaguars Model Y wrap — logo drop folder

This is the hand-off point for finishing the Jacksonville Jaguars Tesla Model Y wrap
with your own copy of the team logo.

## What's here

| File | What it is |
|------|-----------|
| `JAX_Jaguars_Wrap_clean.png` | The finished wrap **canvas** — Tesla's official Model Y (2025+ Premium) `Leopard.png` recolored into Jaguars teal & gold. Panel-perfect, transparent masks preserved, under 1 MB. |
| `place_logo.py` | Places **your** logo file, mirrored + front-facing, on both door panels and writes the final wrap. |
| `my_logo.png` | **← You add this.** Your transparent PNG of the jaguar head. |

## How to use it

1. **Drop your logo here** as `my_logo.png` — a **transparent-background PNG**, head facing **left**
   (the direction of the classic leaping-jaguar head). Any size; the script scales it.
2. Tell me it's in place and I'll run the placement + verify it lands on the door panels, **or**
   run it yourself:
   ```bash
   cd docs/jaguars-wrap
   pip install pillow          # if needed
   python3 place_logo.py
   ```
3. Out comes **`JAX_Jaguars_Wrap_FINAL.png`** — load it onto a USB (`Wraps` folder, exFAT) →
   Toybox → Paint Shop → Wraps.

## Notes

- Placement is pre-verified against Tesla's UV layout: on each side panel the car's **front = up**,
  so the script rotates the head to point up and mirrors it across the centerline — both doors face
  the front of the car.
- Tune knobs live at the top of `place_logo.py` (`TARGET_W`, `CX`, `CY`, `FACING`).
- The wrap skins the **digital 3D car** in the UI, not the real paint.
