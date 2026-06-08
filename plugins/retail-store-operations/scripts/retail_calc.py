#!/usr/bin/env python3
"""retail_calc.py — a zero-dependency brick-and-mortar inventory decision calculator.

Removes arithmetic error from three recurring store-operations decisions a
merchandiser / inventory planner / store-ops lead runs constantly:

  gmroi          GMROI = gross margin $ / average inventory cost — the
                 capital-efficiency lens ("does this inventory earn its
                 carrying cost?"). Flags inventory that turns but doesn't
                 earn, and inventory whose GMROI is below the 1.0 "earns
                 back its own cost" floor. Pairs with the
                 sell-through-and-wos-are-the-vital-signs rule and the
                 knowledge metric/formula map (GMROI = gross margin $ /
                 average inventory cost).

  sell-through   Sell-through % = units sold / units received over a window,
                 plus weeks-of-supply (WOS = on-hand / average weekly demand)
                 and the implied weeks-to-clear. The vital-signs read:
                 normalizes raw on-hand to the demand rate before calling a
                 position over- or under-stocked, and states the window.
                 Pairs with sell-through-and-wos-are-the-vital-signs and the
                 markdown-is-a-decision-not-a-default trigger.

  otb            Open-to-buy = planned sales - planned markdowns
                 + planned (target) EOM stock - planned BOM stock, where
                 planned BOM stock = on-hand + on-order. OTB caps forward
                 commitment; a negative OTB means you're over-bought and the
                 next buy pre-commits a markdown (the most expensive mistake
                 in retail). Pairs with open-to-buy-is-a-budget.

This is a CALCULATOR, not a data source — it does not fetch sales, costs, or
on-hand. The user supplies every input; the tool does the arithmetic and shows
the formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not financial/accounting advice. Every
metric is ambiguous until you state the numerator, denominator, and window —
re-verify each definition against the consumer's reporting system before
defending a decision on it (definitions drift between retailers).

Examples
--------
  # GMROI: $42,000 gross margin $ on $30,000 average inventory at cost
  python3 retail_calc.py gmroi --gross-margin 42000 --avg-inventory-cost 30000

  # Sell-through + WOS: 650 of 1000 units sold over 6 weeks, 350 on hand
  python3 retail_calc.py sell-through --units-sold 650 --units-received 1000 \\
      --weeks 6 --on-hand 350

  # Open-to-buy: $120k planned sales, $15k planned markdowns, $90k target EOM,
  # $80k on-hand + $25k on-order at BOM (all at retail $)
  python3 retail_calc.py otb --planned-sales 120000 --planned-markdowns 15000 \\
      --target-eom 90000 --on-hand 80000 --on-order 25000
"""

from __future__ import annotations

import argparse
import sys


def cmd_gmroi(args: argparse.Namespace) -> int:
    if args.avg_inventory_cost <= 0:
        print("error: --avg-inventory-cost must be > 0", file=sys.stderr)
        return 2

    gmroi = args.gross_margin / args.avg_inventory_cost

    print("GMROI — does this inventory earn its carrying cost?")
    print(f"  gross margin $            : {args.gross_margin:,.2f}")
    print(f"  average inventory (cost)  : {args.avg_inventory_cost:,.2f}")
    print("  ------------------------- ")
    print(f"  = GMROI                   : {gmroi:.2f}   (gross margin $ / avg inventory cost)")
    print()
    if gmroi < 1.0:
        print("  -> BELOW 1.0 — this inventory does NOT earn back its own cost. It is")
        print("     trapped capital regardless of how fast it turns. Cut, mark down, or")
        print("     re-mix before adding more (sell-through-and-wos-are-the-vital-signs).")
    elif gmroi < 2.0:
        print("  -> Thin. Earns its cost but little headroom. Check whether margin or turn")
        print("     is the constraint before defending the space (shelf-space-is-finite-capital).")
    else:
        print("  -> Healthy capital efficiency. This inventory earns its carrying cost; judge")
        print("     it alongside sell-through / weeks-of-supply, never raw on-hand units.")
    print("  note: GMROI is the CAPITAL lens; sell-through + WOS are the FLOW lens. Read")
    print("        both — fast-turning low-margin inventory can still fail the GMROI test.")
    return 0


def cmd_sell_through(args: argparse.Namespace) -> int:
    if args.units_received <= 0:
        print("error: --units-received must be > 0", file=sys.stderr)
        return 2
    if args.weeks <= 0:
        print("error: --weeks must be > 0", file=sys.stderr)
        return 2
    if args.units_sold < 0 or args.on_hand < 0:
        print("error: --units-sold and --on-hand must be >= 0", file=sys.stderr)
        return 2

    sell_through = args.units_sold / args.units_received * 100.0
    weekly_demand = args.units_sold / args.weeks
    wos = args.on_hand / weekly_demand if weekly_demand > 0 else float("inf")

    print(f"Sell-through + weeks-of-supply (window: {args.weeks:g} weeks)")
    print(f"  units sold                : {args.units_sold:,.0f}")
    print(f"  units received            : {args.units_received:,.0f}")
    print(f"  -> sell-through %         : {sell_through:.1f}%   (units sold / units received)")
    print(f"  avg weekly demand         : {weekly_demand:,.1f} units/wk   (units sold / {args.weeks:g} wk)")
    print(f"  on-hand                   : {args.on_hand:,.0f}")
    if weekly_demand > 0:
        print(f"  -> weeks-of-supply (WOS)  : {wos:.1f} wk   (on-hand / avg weekly demand)")
    else:
        print("  -> weeks-of-supply (WOS)  : n/a (no demand in window — zero sell-through)")
    print()
    if weekly_demand <= 0:
        print("  -> No sell-through in the window. This is a clear-or-cut candidate, not a")
        print("     replenish one — check whether it's a price or an assortment problem")
        print("     (markdown-is-a-decision-not-a-default) before discounting.")
    elif wos > args.high_wos:
        print(f"  -> WOS above {args.high_wos:g}wk — OVERSTOCKED relative to the demand rate. Don't")
        print("     replenish; reallocate by WOS or trigger a markdown. Raw on-hand units lie;")
        print("     normalize to the demand rate (sell-through-and-wos-are-the-vital-signs).")
    elif wos < args.low_wos:
        print(f"  -> WOS below {args.low_wos:g}wk — at stockout risk. Replenish to a WOS target within")
        print("     open-to-buy; size safety stock to a NAMED service level, not 'more buffer'.")
    else:
        print("  -> WOS in a healthy band. Judge by this flow, not raw units; re-check the")
        print("     window each cycle and set the markdown/replenish trigger on the metric.")
    print("  note: 'sell-through' with no window is ambiguous — always state the period.")
    return 0


def cmd_otb(args: argparse.Namespace) -> int:
    if args.target_eom < 0:
        print("error: --target-eom must be >= 0", file=sys.stderr)
        return 2

    bom_stock = args.on_hand + args.on_order
    otb = args.planned_sales - args.planned_markdowns + args.target_eom - bom_stock

    print("Open-to-buy — the forward-buy budget (retail $)")
    print(f"  planned sales             : {args.planned_sales:,.2f}")
    print(f"  - planned markdowns       : {args.planned_markdowns:,.2f}")
    print(f"  + target (EOM) stock      : {args.target_eom:,.2f}")
    print(f"  - planned BOM stock       : {bom_stock:,.2f}   (on-hand {args.on_hand:,.0f} + on-order {args.on_order:,.0f})")
    print("  ------------------------- ")
    print(f"  = OPEN-TO-BUY             : {otb:,.2f}")
    print("    (planned sales - markdowns + target EOM - (on-hand + on-order))")
    print()
    if otb < 0:
        print("  -> NEGATIVE OTB — you are OVER-BOUGHT. The next buy pre-commits a markdown:")
        print("     it clears margin the store never earned (open-to-buy-is-a-budget). Re-plan")
        print("     or clear before committing more; don't buy your way out of an overstock.")
    elif otb == 0:
        print("  -> OTB exhausted — no room to buy against this plan. Any new commitment needs")
        print("     a re-plan (higher planned sales or lower target EOM), not an override.")
    else:
        print("  -> Positive OTB — room to buy within the budget. Buy only where the store-SKU")
        print("     weeks-of-supply is below target (allocate-at-the-store-sku-level), not in")
        print("     aggregate; vendor lead time / MOQ route to procurement-sourcing.")
    print("  note: OTB is usually held at a category/month level in retail $ — keep the unit")
    print("        (retail vs. cost) and the window consistent across every term.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="retail_calc.py",
        description="Brick-and-mortar inventory calculator (stdlib only). "
        "Decision-support, not financial/accounting advice — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    gm = sub.add_parser(
        "gmroi", help="GMROI = gross margin $ / average inventory cost"
    )
    gm.add_argument(
        "--gross-margin", type=float, required=True, help="gross margin dollars (over the window)"
    )
    gm.add_argument(
        "--avg-inventory-cost",
        type=float,
        required=True,
        help="average inventory valued AT COST over the same window",
    )
    gm.set_defaults(func=cmd_gmroi)

    st = sub.add_parser(
        "sell-through",
        help="Sell-through % + weeks-of-supply over a period",
    )
    st.add_argument("--units-sold", type=float, required=True, help="units sold over the window")
    st.add_argument(
        "--units-received", type=float, required=True, help="units received over the window"
    )
    st.add_argument(
        "--weeks", type=float, required=True, help="length of the window in weeks"
    )
    st.add_argument(
        "--on-hand", type=float, default=0.0, help="current on-hand units (for weeks-of-supply)"
    )
    st.add_argument(
        "--high-wos",
        type=float,
        default=12.0,
        help="weeks-of-supply above which to flag OVERSTOCK (default 12)",
    )
    st.add_argument(
        "--low-wos",
        type=float,
        default=2.0,
        help="weeks-of-supply below which to flag stockout risk (default 2)",
    )
    st.set_defaults(func=cmd_sell_through)

    ob = sub.add_parser(
        "otb",
        help="Open-to-buy from planned sales / markdowns / EOM-BOM stock",
    )
    ob.add_argument("--planned-sales", type=float, required=True, help="planned sales (retail $)")
    ob.add_argument(
        "--planned-markdowns", type=float, default=0.0, help="planned markdowns (retail $)"
    )
    ob.add_argument(
        "--target-eom",
        type=float,
        required=True,
        help="target / planned end-of-month stock (retail $)",
    )
    ob.add_argument(
        "--on-hand", type=float, required=True, help="beginning-of-month on-hand stock (retail $)"
    )
    ob.add_argument(
        "--on-order", type=float, default=0.0, help="on-order / in-transit stock (retail $)"
    )
    ob.set_defaults(func=cmd_otb)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
