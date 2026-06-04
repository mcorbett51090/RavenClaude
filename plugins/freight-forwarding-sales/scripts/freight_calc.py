#!/usr/bin/env python3
"""freight_calc.py — a zero-dependency freight-quoting calculator.

Removes arithmetic error from the three calculations a freight-forwarding
seller does constantly:

  air    Air CHARGEABLE weight — volumetric (Σ L×W×H cm ÷ divisor) vs actual
         gross, takes the higher. IATA divisor 6000 by default; many couriers
         use 5000. (IATA: 1 m³ ≈ 167 kg.)

  ocean  Ocean LCL CHARGEABLE BASIS — CBM (L×W×H in cm ÷ 1,000,000) vs
         weight/measure (W/M) revenue ton, where 1 W/M = the greater of
         1,000 kg or 1 CBM.

  quote  An ALL-IN sell price — base rate + an arbitrary list of named
         surcharges, then margin applied either on-cost (markup, default) or
         on-sell (gross margin). Prints buy, sell, margin absolute and %.

This is a CALCULATOR, not a rate source — it does not fetch live rates. The
seller supplies the buy rate and surcharge amounts. Stdlib only (argparse);
runs anywhere Python 3.8+ is present.

Examples
--------
  # Air: 4 pieces of 120x80x100 cm, 350 kg actual
  python3 freight_calc.py air --pieces 4 --dims 120x80x100 --weight 350

  # Air with a courier 5000 divisor
  python3 freight_calc.py air --pieces 4 --dims 120x80x100 --weight 350 --divisor 5000

  # Ocean LCL: 8 cartons of 120x100x110 cm, 800 kg total
  python3 freight_calc.py ocean --pieces 8 --dims 120x100x110 --weight 800

  # Quote: 1800 base + surcharges, 12% markup
  python3 freight_calc.py quote --base 1800 --surcharge OTHC=210 --surcharge BAF=180 --margin 12%

  # Quote with gross margin (margin on sell) instead of markup
  python3 freight_calc.py quote --base 1800 --surcharge OTHC=210 --margin 12% --margin-on-sell
"""

from __future__ import annotations

import argparse
import sys

IATA_DIVISOR = 6000  # cm³ per kg → 1 m³ ≈ 167 kg


def _parse_dims(s: str) -> tuple[float, float, float]:
    """Parse 'LxWxH' (any of x/X/* separators) into three floats (cm or m)."""
    parts = s.replace("X", "x").replace("*", "x").split("x")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(f"--dims must be LxWxH, got {s!r}")
    try:
        l, w, h = (float(p) for p in parts)
    except ValueError:
        raise argparse.ArgumentTypeError(f"--dims values must be numbers, got {s!r}")
    if min(l, w, h) <= 0:
        raise argparse.ArgumentTypeError("--dims values must be positive")
    return l, w, h


def _parse_margin(s: str) -> float:
    """Parse a margin like '12%' or '0.12' into a fraction (0.12)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"--margin must be like '12%' or '0.12', got {s!r}")


def _parse_surcharge(s: str) -> tuple[str, float]:
    """Parse 'NAME=amount' into (name, amount)."""
    if "=" not in s:
        raise argparse.ArgumentTypeError(f"--surcharge must be NAME=amount, got {s!r}")
    name, _, amt = s.partition("=")
    name = name.strip()
    try:
        return name, float(amt)
    except ValueError:
        raise argparse.ArgumentTypeError(f"--surcharge amount must be a number, got {amt!r}")


def cmd_air(args: argparse.Namespace) -> int:
    l, w, h = args.dims
    per_piece_vol = (l * w * h) / args.divisor  # kg
    volumetric = per_piece_vol * args.pieces
    actual = args.weight
    chargeable = max(volumetric, actual)
    governs = "volumetric" if volumetric >= actual else "actual gross"

    print("Air chargeable weight")
    print(f"  pieces            : {args.pieces} × {l:g}×{w:g}×{h:g} cm")
    print(f"  divisor           : {args.divisor} (cm³/kg)")
    print(f"  volumetric weight : {volumetric:,.2f} kg  ({per_piece_vol:,.2f} kg/piece)")
    print(f"  actual gross      : {actual:,.2f} kg")
    print(f"  → CHARGEABLE      : {chargeable:,.2f} kg   ({governs} governs)")
    if abs(volumetric - actual) / max(chargeable, 1) < 0.15:
        print("  note: actual and volumetric are close — confirm the carrier's divisor.")
    return 0


def cmd_ocean(args: argparse.Namespace) -> int:
    l, w, h = args.dims  # centimetres
    per_piece_cbm = (l * w * h) / 1_000_000.0  # cm³ → m³ (CBM)
    cbm = per_piece_cbm * args.pieces
    tonnes = args.weight / 1000.0
    wm = max(cbm, tonnes)
    governs = "volume (CBM)" if cbm >= tonnes else "weight (tonnes)"
    wm_billed = max(wm, args.min_wm)

    print("Ocean LCL chargeable basis (weight/measure)")
    print(f"  pieces            : {args.pieces} × {l:g}×{w:g}×{h:g} cm")
    print(f"  total volume      : {cbm:,.3f} CBM")
    print(f"  total weight      : {args.weight:,.1f} kg  ({tonnes:,.3f} t)")
    print(f"  → W/M revenue tons: {wm:,.3f}   ({governs} governs)")
    if wm_billed > wm:
        print(f"  → BILLED (min {args.min_wm:g} W/M floor): {wm_billed:,.3f}")
    print("  rule: 1 W/M = greater of 1,000 kg or 1 CBM; multiply by your per-W/M rate.")
    return 0


def cmd_quote(args: argparse.Namespace) -> int:
    surcharges = args.surcharge or []
    surcharge_total = sum(amt for _, amt in surcharges)
    buy = args.base + surcharge_total

    if args.margin_on_sell:
        if args.margin >= 1.0:
            print("error: --margin-on-sell requires margin < 100%", file=sys.stderr)
            return 2
        sell = buy / (1.0 - args.margin)
        method = "on-sell (gross margin)"
    else:
        sell = buy * (1.0 + args.margin)
        method = "on-cost (markup)"

    margin_abs = sell - buy
    margin_on_sell_pct = (margin_abs / sell * 100.0) if sell else 0.0
    cur = args.currency

    print("All-in quote")
    print(f"  base freight      : {args.base:,.2f} {cur}")
    for name, amt in surcharges:
        print(f"  + {name:<15} : {amt:,.2f} {cur}")
    print(f"  = BUY (cost)      : {buy:,.2f} {cur}")
    print(f"  margin method     : {method} @ {args.margin * 100:g}%")
    print(f"  → SELL            : {sell:,.2f} {cur}")
    print(f"  → MARGIN          : {margin_abs:,.2f} {cur}  ({margin_on_sell_pct:.1f}% of sell)")
    print("  reminder: add a 'valid until' date, the Incoterm scope, and an exclusions line.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="freight_calc.py",
        description="Freight chargeable-weight and all-in-quote calculator (stdlib only).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("air", help="air chargeable weight (volumetric vs actual)")
    a.add_argument("--pieces", type=int, default=1, help="number of identical pieces (default 1)")
    a.add_argument("--dims", type=_parse_dims, required=True, help="LxWxH per piece, in CM")
    a.add_argument("--weight", type=float, required=True, help="total actual gross weight, kg")
    a.add_argument("--divisor", type=float, default=IATA_DIVISOR, help="volumetric divisor (default 6000; couriers often 5000)")
    a.set_defaults(func=cmd_air)

    o = sub.add_parser("ocean", help="ocean LCL chargeable basis (CBM vs W/M ton)")
    o.add_argument("--pieces", type=int, default=1, help="number of identical pieces (default 1)")
    o.add_argument("--dims", type=_parse_dims, required=True, help="LxWxH per piece, in CM (converted to CBM)")
    o.add_argument("--weight", type=float, required=True, help="total actual gross weight, kg")
    o.add_argument("--min-wm", type=float, default=1.0, help="LCL minimum W/M floor (default 1.0)")
    o.set_defaults(func=cmd_ocean)

    q = sub.add_parser("quote", help="all-in sell price = base + surcharges + margin")
    q.add_argument("--base", type=float, required=True, help="base freight buy rate")
    q.add_argument("--surcharge", type=_parse_surcharge, action="append", metavar="NAME=AMT", help="a surcharge line (repeatable)")
    q.add_argument("--margin", type=_parse_margin, default=0.0, help="margin, e.g. '12%%' or '0.12'")
    q.add_argument("--margin-on-sell", action="store_true", help="treat margin as gross-margin on sell (default is markup on cost)")
    q.add_argument("--currency", default="USD", help="currency label (default USD)")
    q.set_defaults(func=cmd_quote)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
