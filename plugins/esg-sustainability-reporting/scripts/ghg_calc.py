#!/usr/bin/env python3
"""ghg_calc.py — a zero-dependency GHG-inventory arithmetic calculator.

Removes arithmetic error from three recurring GHG Protocol inventory tasks an
ESG / sustainability analyst runs constantly. Every emission factor is a
USER-SUPPLIED input — this tool ships NO factor library, NO benchmarks, and NO
grid intensities. It does the activity-data x factor arithmetic, the unit
bookkeeping, and the dual-Scope-2 / category-rollup structure; the user brings
every number and is responsible for sourcing and vintaging each factor
(CLAUDE.md S4 #4: cite the factor source and vintage — always).

  scope2     Purchased-electricity Scope 2, BOTH methods (CLAUDE.md S4 #5).
             Location-based = kWh x grid factor; market-based = sum of
             (instrument kWh x instrument factor) + any residual kWh x residual
             factor. Prints both figures side by side so neither is silently
             dropped. Offsets are NOT a Scope-2 instrument and are not accepted
             here.

  inventory  Sum activity x factor across many lines, each tagged with a scope
             (1 / 2 / 3) and an optional Scope-3 category (1-15) and data-quality
             tier. Lines come from a CSV (no pandas — stdlib csv). Prints a
             per-scope total, a Scope-3 category breakdown, the gross total, and
             a data-quality-tier mix so the weakest-tier lines are visible.

  intensity  Emissions intensity = total emissions / a denominator (revenue,
             units produced, FTEs, floor area, ...). Prints the ratio with the
             unit label the user supplies. Intensity is a RATIO, not a reduction
             — a falling intensity with rising absolute emissions is not a cut.

This is a CALCULATOR, not a data source. It performs no factor lookup, applies
no benchmark, and renders no assurance or legal opinion (../CLAUDE.md S1, S4
#10). Stdlib only (argparse, csv); runs anywhere Python 3.8+ is present.

CSV format for `inventory` (header required; emission_factor is per activity
unit, in the SAME mass unit you want the output in, e.g. kgCO2e or tCO2e):

    line,scope,category,activity,unit,emission_factor,quality_tier
    grid electricity,2,,1250000,kWh,0.000417,primary
    diesel fleet,1,,48000,L,0.00268,primary
    purchased goods,3,1,5400000,USD,0.00031,spend
    business travel air,3,6,820000,km,0.00015,secondary

`category` is blank except for Scope 3 (1-15). `quality_tier` is free text
(e.g. primary / secondary / proxy / spend) and is summarized, not validated.

Examples
--------
  # Dual Scope 2: 1,250,000 kWh on a 0.000417 tCO2e/kWh grid factor;
  # 800,000 kWh covered by a PPA at 0.0 and the residual on the grid factor
  python3 ghg_calc.py scope2 --kwh 1250000 --grid-factor 0.000417 \\
      --instrument 800000:0.0 --residual-factor 0.000417

  # Inventory rollup from a CSV
  python3 ghg_calc.py inventory --csv inventory.csv

  # Intensity: 18,400 tCO2e over $240,000,000 revenue
  python3 ghg_calc.py intensity --emissions 18400 --denominator 240000000 \\
      --denominator-unit "USD revenue" --per 1000000
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict


def _instrument(s: str) -> tuple[float, float]:
    """Parse a 'kwh:factor' market-based instrument into (kwh, factor)."""
    parts = s.split(":")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(
            f"instrument must be 'kwh:factor', got {s!r}"
        )
    try:
        kwh, factor = float(parts[0]), float(parts[1])
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"instrument must be 'kwh:factor' numbers, got {s!r}"
        ) from None
    if kwh < 0 or factor < 0:
        raise argparse.ArgumentTypeError(
            f"instrument kwh and factor must be >= 0, got {s!r}"
        )
    return kwh, factor


def cmd_scope2(args: argparse.Namespace) -> int:
    if args.kwh <= 0:
        print("error: --kwh must be > 0", file=sys.stderr)
        return 2
    if args.grid_factor < 0:
        print("error: --grid-factor must be >= 0", file=sys.stderr)
        return 2

    location_based = args.kwh * args.grid_factor

    instrument_kwh = sum(kwh for kwh, _ in args.instrument)
    instrument_emissions = sum(kwh * f for kwh, f in args.instrument)
    residual_kwh = args.kwh - instrument_kwh
    if residual_kwh < -1e-6:
        print(
            "error: instrument kWh exceed total --kwh "
            f"({instrument_kwh:,.0f} > {args.kwh:,.0f})",
            file=sys.stderr,
        )
        return 2
    residual_kwh = max(residual_kwh, 0.0)
    residual_factor = (
        args.residual_factor
        if args.residual_factor is not None
        else args.grid_factor
    )
    residual_emissions = residual_kwh * residual_factor
    market_based = instrument_emissions + residual_emissions

    print("Scope 2 — dual reporting (location-based AND market-based)")
    print(f"  purchased electricity   : {args.kwh:,.0f} kWh")
    print(f"  grid (location) factor  : {args.grid_factor:g} per kWh")
    print(f"  -> LOCATION-BASED       : {location_based:,.4f}")
    print("  market-based instruments:")
    if args.instrument:
        for kwh, f in args.instrument:
            print(f"    {kwh:>14,.0f} kWh x {f:g} = {kwh * f:,.4f}")
    else:
        print("    (none supplied)")
    print(f"  residual (grid) kWh     : {residual_kwh:,.0f} x {residual_factor:g}"
          f" = {residual_emissions:,.4f}")
    print(f"  -> MARKET-BASED         : {market_based:,.4f}")
    print("  note: BOTH figures are reported where market instruments exist —")
    print("        never silently pick one (CLAUDE.md S4 #5). Name and quality-")
    print("        screen each instrument; offsets are NOT a Scope-2 instrument")
    print("        and are reported separately, never netted in.")
    return 0


def _read_inventory_csv(path: str) -> list[dict[str, str]]:
    if path == "-":
        return list(csv.DictReader(sys.stdin))
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def cmd_inventory(args: argparse.Namespace) -> int:
    try:
        rows = _read_inventory_csv(args.csv)
    except OSError as exc:
        print(f"error: cannot read CSV: {exc}", file=sys.stderr)
        return 2
    if not rows:
        print("error: CSV has no data rows", file=sys.stderr)
        return 2

    scope_totals: dict[str, float] = defaultdict(float)
    category_totals: dict[str, float] = defaultdict(float)
    tier_totals: dict[str, float] = defaultdict(float)
    gross = 0.0

    for i, row in enumerate(rows, start=2):
        try:
            activity = float(row["activity"])
            factor = float(row["emission_factor"])
        except (KeyError, ValueError):
            print(
                f"error: row {i} needs numeric 'activity' and "
                "'emission_factor' columns",
                file=sys.stderr,
            )
            return 2
        scope = (row.get("scope") or "").strip() or "?"
        emissions = activity * factor
        gross += emissions
        scope_totals[scope] += emissions
        tier_totals[(row.get("quality_tier") or "unspecified").strip()] += emissions
        if scope == "3":
            category = (row.get("category") or "").strip() or "uncategorized"
            category_totals[f"cat {category}"] += emissions

    print("GHG inventory rollup (activity x user-supplied factor)")
    print(f"  lines                   : {len(rows)}")
    print("  per-scope totals:")
    for scope in sorted(scope_totals):
        share = scope_totals[scope] / gross * 100 if gross else 0.0
        print(f"    Scope {scope:<2}             : {scope_totals[scope]:,.4f}"
              f"  ({share:.1f}%)")
    if category_totals:
        print("  Scope-3 category breakdown:")
        for cat in sorted(category_totals, key=_cat_sort_key):
            print(f"    {cat:<20} : {category_totals[cat]:,.4f}")
    print("  data-quality-tier mix:")
    for tier in sorted(tier_totals):
        share = tier_totals[tier] / gross * 100 if gross else 0.0
        print(f"    {tier:<20} : {tier_totals[tier]:,.4f}  ({share:.1f}%)")
    print(f"  -> GROSS TOTAL          : {gross:,.4f}")
    print("  note: each factor is YOUR input — cite its source and vintage; the")
    print("        tier mix shows where the weakest-tier lines sit (CLAUDE.md S4")
    print("        #4). Screen all 15 Scope-3 categories; this rolls up only")
    print("        what you supplied — a missing category is not a zero.")
    return 0


def _cat_sort_key(label: str) -> tuple[int, str]:
    """Sort 'cat 1'..'cat 15' numerically, others last alphabetically."""
    tail = label.replace("cat ", "", 1)
    return (int(tail), "") if tail.isdigit() else (10**9, label)


def cmd_intensity(args: argparse.Namespace) -> int:
    if args.denominator == 0:
        print("error: --denominator must be non-zero", file=sys.stderr)
        return 2
    intensity = args.emissions / args.denominator * args.per

    print("Emissions intensity (a ratio, not a reduction)")
    print(f"  emissions               : {args.emissions:,.4f}")
    print(f"  denominator             : {args.denominator:,.4f} "
          f"{args.denominator_unit}")
    if args.per != 1:
        print(f"  per                     : {args.per:,.0f} {args.denominator_unit}")
    print(f"  -> INTENSITY            : {intensity:,.6f} emissions per "
          f"{args.per:,.0f} {args.denominator_unit}")
    print("  note: intensity is a RATIO — a falling intensity with rising")
    print("        absolute emissions is NOT a cut. Report absolute and")
    print("        intensity together, on a consistent base year (CLAUDE.md S4 #6).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ghg_calc.py",
        description="GHG-inventory arithmetic calculator (stdlib only). Every "
        "emission factor is a user-supplied input; no factor library, no "
        "benchmarks. Decision-support, not an assurance or legal opinion.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s2 = sub.add_parser("scope2", help="Dual location- and market-based Scope 2")
    s2.add_argument("--kwh", type=float, required=True,
                    help="total purchased electricity (kWh)")
    s2.add_argument("--grid-factor", type=float, required=True,
                    help="grid-average emission factor per kWh (your input)")
    s2.add_argument("--instrument", type=_instrument, action="append", default=[],
                    metavar="KWH:FACTOR",
                    help="a market-based instrument as kwh:factor "
                    "(repeatable; e.g. 800000:0.0)")
    s2.add_argument("--residual-factor", type=float, default=None,
                    help="factor for kWh not covered by instruments "
                    "(default: the grid factor)")
    s2.set_defaults(func=cmd_scope2)

    inv = sub.add_parser("inventory", help="Sum activity x factor across scopes")
    inv.add_argument("--csv", required=True,
                     help="path to inventory CSV ('-' for stdin); see module "
                     "docstring for the header")
    inv.set_defaults(func=cmd_inventory)

    it = sub.add_parser("intensity", help="Emissions per revenue / output")
    it.add_argument("--emissions", type=float, required=True,
                    help="total emissions (your inventory total)")
    it.add_argument("--denominator", type=float, required=True,
                    help="revenue / units / FTEs / floor area / ...")
    it.add_argument("--denominator-unit", default="unit",
                    help="label for the denominator (e.g. 'USD revenue')")
    it.add_argument("--per", type=float, default=1.0,
                    help="scale the denominator (e.g. 1000000 for per-$M)")
    it.set_defaults(func=cmd_intensity)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
