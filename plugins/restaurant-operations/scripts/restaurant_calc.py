#!/usr/bin/env python3
"""restaurant_calc.py — a zero-dependency restaurant-operations decision calculator.

Removes arithmetic error from four recurring four-wall decisions an operator,
GM, or consultant runs constantly:

  prime-cost      Read the MASTER NUMBER. Computes food %, labor %, and prime
                  cost % from sales/food/labor dollars, and flags each against
                  segment benchmark bands (QSR vs full-service). Pairs with
                  knowledge/restaurant-unit-economics.md and the read-prime-cost
                  skill. Prime cost = (food + labor) / revenue (CLAUDE.md §3 #1).

  menu-item       Place an item on the MENU ENGINEERING MATRIX. Computes
                  contribution margin (price - plate cost), food-cost %, and the
                  star / plowhorse / puzzle / dog quadrant against the menu's
                  average CM and the 70%-of-even-share popularity threshold.
                  Pairs with knowledge/restaurant-menu-action-decision-tree.md.

  make-vs-buy     The MAKE-vs-BUY trade with the labor term most operators omit.
                  Fully-loaded scratch cost = ingredients + (prep-minutes/yield)
                  x loaded-wage/min + spoilage, vs a prepped price. Prints the
                  per-unit + monthly verdict. Pairs with
                  knowledge/restaurant-make-vs-buy-decision-tree.md.

  price-change    The PRICE-CHANGE BREAKEVEN. Given a price move and the item's
                  current price + plate cost, computes the volume change at which
                  total contribution dollars stay flat — so you see how much
                  volume a price cut must GAIN (or a hike can afford to LOSE)
                  before it helps or hurts. Pairs with the engineer-the-menu
                  skill (CLAUDE.md §3 #3 — resist the price cut as first lever).

This is a CALCULATOR, not a data source — it does not fetch benchmarks, prices,
or live costs. The user supplies every input; the tool does the arithmetic and
shows the formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not financial, legal, or tax advice
(see ../CLAUDE.md §2). Validate every figure against the unit's actual P&L and
POS data before any deliverable (CLAUDE.md §3 #8). Benchmark bands are dated,
segment-dependent rules of thumb — verify at use (CLAUDE.md §3 #8).

Examples
--------
  # Prime cost: $42,000 sales, $13,400 food, $15,800 labor, full-service
  python3 restaurant_calc.py prime-cost --sales 42000 --food 13400 \\
      --labor 15800 --segment full-service

  # Menu item: $24 price, $8.40 plate cost, 9.2% mix share on a 28-item menu,
  # menu-average contribution margin of $11.00
  python3 restaurant_calc.py menu-item --price 24 --plate-cost 8.40 \\
      --mix-share 9.2% --menu-items 28 --avg-cm 11.00

  # Make vs buy: scratch = $1.10 ingredients + 40 prep-min/batch yielding 50
  # units at a $0.55/min loaded wage + 5% spoilage, vs $2.20 prepped; 600/mo
  python3 restaurant_calc.py make-vs-buy --ingredient-cost 1.10 \\
      --prep-minutes 40 --batch-yield 50 --loaded-wage-min 0.55 \\
      --spoilage 5% --prepped-price 2.20 --volume 600

  # Price change: raise a $14.00 / $4.50-cost item by $1.00 — how much volume
  # can it afford to lose before contribution dollars fall?
  python3 restaurant_calc.py price-change --price 14.00 --plate-cost 4.50 \\
      --price-delta 1.00
"""

from __future__ import annotations

import argparse
import sys

# Dated, segment-dependent benchmark bands (rules of thumb — [verify-at-use]).
# Sources (retrieved 2026-06-05): 7shifts Restaurant Prime Cost Guide
# (https://www.7shifts.com/blog/restaurant-prime-cost-guide/); Toast Restaurant
# Payroll Percentage (https://pos.toasttab.com/blog/on-the-line/restaurant-payroll-percentage).
# Food cost optimal 28-35% (full-service industry avg ~32.4%); these are
# defaults the user can override and MUST validate against their own P&L.
_BANDS = {
    "qsr": {"food": (0.28, 0.32), "labor": (0.30, 0.32), "prime": (0.55, 0.60)},
    "full-service": {"food": (0.28, 0.35), "labor": (0.34, 0.40), "prime": (0.60, 0.65)},
}


def _parse_rate(s: str) -> float:
    """Parse a rate like '35%' or '0.35' into a fraction (0.35)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '35%' or '0.35', got {s!r}")


def _band_flag(value: float, band: tuple) -> str:
    lo, hi = band
    if value <= hi:
        return f"in/under band ({lo*100:g}-{hi*100:g}%)  ✓"
    return f"OVER band ({lo*100:g}-{hi*100:g}%)  ⚠ {((value-hi)*100):.1f} pts high"


def cmd_prime_cost(args: argparse.Namespace) -> int:
    if args.sales <= 0:
        print("error: --sales must be > 0", file=sys.stderr)
        return 2
    food_pct = args.food / args.sales
    labor_pct = args.labor / args.sales
    prime = food_pct + labor_pct
    band = _BANDS[args.segment]

    print("Prime cost — the master number")
    print(f"  segment            : {args.segment}")
    print(f"  sales              : {args.sales:,.0f}")
    print(f"  food (COGS)        : {args.food:,.0f}   = {food_pct*100:5.1f}%  {_band_flag(food_pct, band['food'])}")
    print(f"  labor              : {args.labor:,.0f}   = {labor_pct*100:5.1f}%  {_band_flag(labor_pct, band['labor'])}")
    print(f"  → PRIME COST       : {args.food+args.labor:,.0f}   = {prime*100:5.1f}%  {_band_flag(prime, band['prime'])}")
    print()
    # Which half is the driver?
    food_over = max(0.0, food_pct - band["food"][1])
    labor_over = max(0.0, labor_pct - band["labor"][1])
    if prime <= band["prime"][1]:
        print("  read: prime cost is in band. Watch the trend, not a single month.")
    elif food_over >= labor_over and food_over > 0:
        print("  read: FOOD is the larger driver — build a theoretical food cost and")
        print("        decompose actual-vs-theoretical (waste/portioning/price/theft) BEFORE")
        print("        a price move (§3 #2). Splitting the master number is step one (§3 #1).")
    elif labor_over > 0:
        print("  read: LABOR is the larger driver — schedule to demand BY DAYPART and read")
        print("        sales-per-labor-hour per daypart, not a blended weekly % (§3 #4).")
    else:
        print("  read: prime is over band but neither half is individually over its band —")
        print("        the mix is the issue; check the lower-volume/low-margin items (§3 #5).")
    print("  note: benchmark bands are dated, segment-dependent rules of thumb — validate")
    print("        against THIS unit's P&L and history before any deliverable (§3 #8).")
    return 0


def _quadrant(cm_high: bool, popular: bool) -> tuple:
    if cm_high and popular:
        return ("STAR", "PROTECT — feature it, hold quality; do not over-raise price and risk volume")
    if not cm_high and popular:
        return ("PLOWHORSE", "ENGINEER THE COST first (re-portion/re-spec); small nudge only — never a blanket cut")
    if cm_high and not popular:
        return ("PUZZLE", "PROMOTE — placement, name, server mention, bundling; raise demand before discounting")
    return ("DOG", "REWORK or CUT — earns neither margin nor traffic; keep only for a deliberate strategic reason")


def cmd_menu_item(args: argparse.Namespace) -> int:
    if args.price <= 0:
        print("error: --price must be > 0", file=sys.stderr)
        return 2
    if args.menu_items < 1:
        print("error: --menu-items must be >= 1", file=sys.stderr)
        return 2
    cm = args.price - args.plate_cost
    food_pct = args.plate_cost / args.price
    threshold = 0.70 * (1.0 / args.menu_items)
    popular = args.mix_share >= threshold
    cm_high = cm >= args.avg_cm
    label, action = _quadrant(cm_high, popular)

    print("Menu item — engineering matrix placement")
    print(f"  menu price             : {args.price:,.2f}")
    print(f"  plate (recipe) cost    : {args.plate_cost:,.2f}")
    print(f"  → contribution margin  : {cm:,.2f}   (food cost {food_pct*100:.1f}%)")
    print(f"  menu-average CM        : {args.avg_cm:,.2f}   → this item is {'HIGH' if cm_high else 'LOW'} margin")
    print(f"  mix share              : {args.mix_share*100:.1f}%")
    print(f"  popularity threshold   : {threshold*100:.2f}%  = 70% × (1 ÷ {args.menu_items} items)")
    print(f"                           → this item is {'POPULAR' if popular else 'UNPOPULAR'}")
    print()
    print(f"  → QUADRANT : {label}")
    print(f"    action   : {action}")
    print("  note: engineer on DOLLARS of contribution margin, not food-cost % (§3 #5).")
    print("        mix share must be real POS data; the quadrant flips on the threshold (§3 #8).")
    return 0


def cmd_make_vs_buy(args: argparse.Namespace) -> int:
    if args.batch_yield <= 0:
        print("error: --batch-yield must be > 0", file=sys.stderr)
        return 2
    if not 0.0 <= args.spoilage < 1.0:
        print("error: --spoilage must be in [0%, 100%)", file=sys.stderr)
        return 2
    labor_per_unit = (args.prep_minutes / args.batch_yield) * args.loaded_wage_min
    base = args.ingredient_cost + labor_per_unit
    # spoilage inflates the effective per-unit cost of what you actually sell
    scratch = base / (1.0 - args.spoilage)
    verdict = "MAKE" if scratch < args.prepped_price else "BUY PREPPED"

    print("Make vs buy — fully-loaded scratch cost (the labor term included)")
    print(f"  ingredient cost/unit   : {args.ingredient_cost:,.4f}")
    print(f"  prep labor/unit        : {labor_per_unit:,.4f}  "
          f"= ({args.prep_minutes:g} min ÷ {args.batch_yield:g} yield) × {args.loaded_wage_min:g}/min")
    print(f"  spoilage allowance     : {args.spoilage*100:g}%")
    print(f"  → fully-loaded scratch : {scratch:,.4f}/unit")
    print(f"  prepped price          : {args.prepped_price:,.4f}/unit")
    print()
    gap = args.prepped_price - scratch
    print(f"  per-unit gap (prepped − scratch): {gap:,.4f}")
    print(f"  → cheaper on cost      : {verdict}")
    if args.volume is not None:
        monthly_scratch = scratch * args.volume
        monthly_prepped = args.prepped_price * args.volume
        print()
        print(f"  at {args.volume:g} units/month:")
        print(f"    scratch monthly cost : {monthly_scratch:,.2f}")
        print(f"    prepped monthly cost : {monthly_prepped:,.2f}")
        print(f"    monthly difference   : {abs(monthly_scratch-monthly_prepped):,.2f} in favor of {verdict}")
    print("  reminder: cost is only one axis — brand/signature value, BOH capacity, and")
    print("            consistency can flip the call (see the make-vs-buy decision tree).")
    return 0


def cmd_price_change(args: argparse.Namespace) -> int:
    if args.price <= 0:
        print("error: --price must be > 0", file=sys.stderr)
        return 2
    old_cm = args.price - args.plate_cost
    new_price = args.price + args.price_delta
    new_cm = new_price - args.plate_cost
    if old_cm <= 0 or new_cm <= 0:
        print("error: contribution margin must be positive before and after the change", file=sys.stderr)
        return 2
    # Volume multiplier that keeps total contribution flat: old_cm = new_cm × (1 + dV)
    ratio = old_cm / new_cm
    vol_change = ratio - 1.0  # fractional change in volume needed to break even

    print("Price change — contribution-dollar breakeven")
    print(f"  current price          : {args.price:,.2f}   (CM {old_cm:,.2f})")
    print(f"  price change           : {args.price_delta:+,.2f}")
    print(f"  new price              : {new_price:,.2f}   (CM {new_cm:,.2f})")
    print()
    if args.price_delta > 0:
        print(f"  → a price INCREASE can afford to LOSE up to {abs(vol_change)*100:.1f}% of unit volume")
        print(f"    before total contribution dollars fall below today's.")
        print("    (lose less than that and you're ahead; this is usually the safer lever.)")
    elif args.price_delta < 0:
        print(f"  → a price CUT must GAIN at least {vol_change*100:.1f}% more unit volume")
        print(f"    just to hold today's contribution dollars — and more to actually help.")
        print("    (this is why a cut is rarely the first lever — §3 #3.)")
    else:
        print("  → no price change; no volume effect to break even on.")
    print("  note: this is the contribution-dollar breakeven only — it does NOT predict")
    print("        guest response. Model elasticity from real POS history (§3 #8).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="restaurant_calc.py",
        description="Restaurant four-wall decision calculator (stdlib only). "
        "Decision-support, not financial/legal/tax advice — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("prime-cost", help="Food %, labor %, prime cost % vs segment bands")
    pc.add_argument("--sales", type=float, required=True, help="total sales (revenue) for the window")
    pc.add_argument("--food", type=float, required=True, help="food cost (COGS) for the window")
    pc.add_argument("--labor", type=float, required=True, help="total labor cost for the window")
    pc.add_argument("--segment", choices=sorted(_BANDS), default="full-service",
                    help="benchmark band to flag against (default full-service)")
    pc.set_defaults(func=cmd_prime_cost)

    mi = sub.add_parser("menu-item", help="Menu engineering matrix quadrant for an item")
    mi.add_argument("--price", type=float, required=True, help="menu price")
    mi.add_argument("--plate-cost", type=float, required=True, help="plate (recipe) cost")
    mi.add_argument("--mix-share", type=_parse_rate, required=True,
                    help="item's share of menu mix (e.g. 9.2%% or 0.092)")
    mi.add_argument("--menu-items", type=int, required=True, help="number of items on the menu (for the 70%%×1/N threshold)")
    mi.add_argument("--avg-cm", type=float, required=True, help="menu-average contribution margin in dollars")
    mi.set_defaults(func=cmd_menu_item)

    mb = sub.add_parser("make-vs-buy", help="Fully-loaded scratch cost vs prepped price")
    mb.add_argument("--ingredient-cost", type=float, required=True, help="raw-ingredient cost per unit")
    mb.add_argument("--prep-minutes", type=float, required=True, help="prep minutes per batch")
    mb.add_argument("--batch-yield", type=float, required=True, help="units produced per batch")
    mb.add_argument("--loaded-wage-min", type=float, required=True,
                    help="loaded wage per minute (base + taxes + benefits)")
    mb.add_argument("--spoilage", type=_parse_rate, default=0.0,
                    help="spoilage/waste allowance on scratch product (default 0%%)")
    mb.add_argument("--prepped-price", type=float, required=True, help="prepped-product price per unit")
    mb.add_argument("--volume", type=float, default=None, help="projected units/month for a monthly verdict (optional)")
    mb.set_defaults(func=cmd_make_vs_buy)

    pch = sub.add_parser("price-change", help="Contribution-dollar breakeven for a price move")
    pch.add_argument("--price", type=float, required=True, help="current menu price")
    pch.add_argument("--plate-cost", type=float, required=True, help="plate (recipe) cost")
    pch.add_argument("--price-delta", type=float, required=True,
                     help="price change in dollars (e.g. 1.00 to raise, -1.00 to cut)")
    pch.set_defaults(func=cmd_price_change)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
