#!/usr/bin/env python3
"""dtc_calc.py — a zero-dependency DTC unit-economics decision calculator.

Removes arithmetic error from three recurring direct-to-consumer decisions a
founder / growth lead / analyst runs constantly:

  contribution-margin  The per-order CONTRIBUTION MARGIN net of the real costs —
                       COGS, fulfillment/shipping, payment fees, and the
                       return-loaded cost (return rate x reverse-logistics cost
                       per returned order). Revenue net of these, NOT gross, is
                       the scoreboard (CLAUDE.md s3 #2). Flags a category that
                       converts well but loses money once returns are loaded in
                       (s3 #6). Pairs with knowledge/ecommerce-unit-economics.md.

  ltv-cac              The master ratio (s3 #1). Computes LTV from AOV x
                       contribution-margin% x purchase frequency over a horizon
                       (with optional monthly churn -> expected lifetime), then
                       LTV:CAC and the cash PAYBACK in orders. Prints whether the
                       ratio clears the 3:1 line and whether it is below the 2:1
                       immediate-problem floor. Pairs with skills/read-ltv-cac.

  breakeven-roas       The MER / blended-ROAS FLOOR from contribution margin:
                       breakeven MER = 1 / contribution-margin%. Below this, ad
                       spend buys revenue at a loss (s3 #5). Prints the floor and,
                       at a target ROAS, the implied CAC headroom per order. Pairs
                       with knowledge/ecommerce-decision-trees.md (CAC is climbing).

This is a CALCULATOR, not a data source — it does not fetch benchmarks, costs,
or live ad data. The user supplies every input; the tool does the arithmetic and
shows the formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not financial/tax/accounting advice
(see ../CLAUDE.md s2). Validate every figure against the brand's actual data
before any deliverable (CLAUDE.md s3 #8).

Examples
--------
  # Contribution margin: $80 AOV, 35% COGS, $9 fulfillment, 3% payment fee,
  # 35% return rate costing $22/returned order all-in (reverse logistics)
  python3 dtc_calc.py contribution-margin --aov 80 --cogs-pct 35% \\
      --fulfillment 9 --payment-fee 3% --return-rate 35% --return-cost 22

  # LTV:CAC: $80 AOV, 32% contribution margin, 4 orders/yr, $60 CAC,
  # 5% monthly churn (-> expected lifetime), 24-month horizon
  python3 dtc_calc.py ltv-cac --aov 80 --margin 32% --freq 4 --cac 60 \\
      --monthly-churn 5% --horizon-months 24

  # Breakeven ROAS/MER from a 30% contribution margin, checking a 3.5x target
  python3 dtc_calc.py breakeven-roas --margin 30% --target-roas 3.5 --aov 80
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '35%' or '0.35' into a fraction (0.35)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '35%' or '0.35', got {s!r}")


def cmd_contribution_margin(args: argparse.Namespace) -> int:
    for name, val in (("--cogs-pct", args.cogs_pct), ("--payment-fee", args.payment_fee),
                      ("--return-rate", args.return_rate)):
        if not 0.0 <= val <= 1.0:
            print(f"error: {name} must be in [0%, 100%]", file=sys.stderr)
            return 2
    if args.aov <= 0:
        print("error: --aov must be > 0", file=sys.stderr)
        return 2

    cogs = args.aov * args.cogs_pct
    payment = args.aov * args.payment_fee
    # Return cost is spread across ALL orders: return_rate x per-returned-order cost.
    return_load = args.return_rate * args.return_cost
    cm = args.aov - cogs - args.fulfillment - payment - return_load
    cm_pct = cm / args.aov * 100.0

    print("Per-order contribution margin (net of returns)")
    print(f"  AOV                       : {args.aov:,.2f}")
    print(f"  - COGS ({args.cogs_pct * 100:g}%)            : {cogs:,.2f}")
    print(f"  - fulfillment/shipping    : {args.fulfillment:,.2f}")
    print(f"  - payment fee ({args.payment_fee * 100:g}%)       : {payment:,.2f}")
    print(f"  - return load ({args.return_rate * 100:g}% x {args.return_cost:g}) : {return_load:,.2f}")
    print("  -------------------------- ")
    print(f"  = CONTRIBUTION MARGIN     : {cm:,.2f}  ({cm_pct:.1f}% of AOV)")
    print()
    if cm < 0:
        print("  -> NEGATIVE contribution margin. This category/order LOSES money once")
        print("     returns are loaded in (s3 #2, #6). A high conversion rate or strong")
        print("     AOV does NOT save it. Attack the return DRIVER (fit/PDP) or reprice.")
    elif cm_pct < 20:
        print("  -> Thin margin. Little headroom to fund CAC; a small return-rate or COGS")
        print("     move flips it negative. Stress-test the return rate before scaling.")
    else:
        print("  -> Positive. This is the number that funds acquisition + overhead — the")
        print("     scoreboard, not gross revenue (s3 #2).")
    print("  note: load the return cost from REAL reverse-logistics invoices, not a guess —")
    print("        return cost runs ~20-65% of item price all-in for apparel (s3 #6).")
    return 0


def cmd_ltv_cac(args: argparse.Namespace) -> int:
    if not 0.0 <= args.margin <= 1.0:
        print("error: --margin must be in [0%, 100%]", file=sys.stderr)
        return 2
    if args.aov <= 0 or args.cac <= 0 or args.freq <= 0:
        print("error: --aov, --cac, --freq must all be > 0", file=sys.stderr)
        return 2

    # Effective number of orders over the horizon. If a monthly churn is given,
    # expected lifetime (months) = 1 / churn, capped by the horizon; orders =
    # freq-per-year x lifetime-years. Otherwise just freq x horizon-years.
    horizon_years = args.horizon_months / 12.0
    if args.monthly_churn is not None:
        if not 0.0 < args.monthly_churn <= 1.0:
            print("error: --monthly-churn must be in (0%, 100%]", file=sys.stderr)
            return 2
        lifetime_months = min(1.0 / args.monthly_churn, args.horizon_months)
        lifetime_years = lifetime_months / 12.0
        churn_note = (f"expected lifetime {lifetime_months:,.1f} mo "
                      f"(1 / {args.monthly_churn * 100:g}% churn, capped at horizon)")
    else:
        lifetime_years = horizon_years
        churn_note = f"full horizon {args.horizon_months} mo (no churn supplied)"

    orders = args.freq * lifetime_years
    cm_per_order = args.aov * args.margin
    ltv = orders * cm_per_order  # contribution-margin LTV
    ratio = ltv / args.cac
    # Payback in ORDERS: how many orders of contribution margin to recover CAC.
    payback_orders = args.cac / cm_per_order if cm_per_order > 0 else float("inf")

    print("LTV:CAC — the master ratio")
    print(f"  AOV                  : {args.aov:,.2f}")
    print(f"  contribution margin  : {args.margin * 100:g}%  -> {cm_per_order:,.2f}/order")
    print(f"  purchase frequency   : {args.freq:g}/yr")
    print(f"  horizon              : {churn_note}")
    print(f"  -> orders in window  : {orders:,.2f}")
    print(f"  -> LTV (margin-based): {ltv:,.2f}")
    print(f"  CAC                  : {args.cac:,.2f}")
    print(f"  -> LTV:CAC           : {ratio:.2f} : 1")
    print(f"  -> payback           : {payback_orders:,.1f} orders to recover CAC")
    print()
    if ratio < 2.0:
        print("  -> BELOW 2:1 — immediate problem (s3 #1). The brand is acquiring at a loss")
        print("     against realized lifetime value. Fix retention/AOV or cut CAC before scaling.")
    elif ratio < 3.0:
        print("  -> Between 2:1 and 3:1 — under the 3:1 sustainability line (s3 #1). Workable")
        print("     but fragile; protect it with retention before adding acquisition spend.")
    else:
        print("  -> At or above 3:1 — clears the sustainability line (s3 #1). Headroom to scale,")
        print("     but watch payback as a separate CASH constraint, not just the ratio.")
    print("  note: LTV here is CONTRIBUTION-margin LTV, not revenue. Read CAC by channel +")
    print("        cohort (s3 #5) — a blended ratio hides a subsidized channel.")
    return 0


def cmd_breakeven_roas(args: argparse.Namespace) -> int:
    if not 0.0 < args.margin < 1.0:
        print("error: --margin must be in (0%, 100%)", file=sys.stderr)
        return 2

    breakeven = 1.0 / args.margin
    print("Breakeven ROAS / MER from contribution margin")
    print(f"  contribution margin   : {args.margin * 100:g}%")
    print(f"  -> breakeven MER/ROAS : {breakeven:.2f}x   (1 / contribution-margin%)")
    print("     below this, every dollar of ad spend buys revenue at a loss (s3 #5).")

    if args.target_roas is not None:
        if args.target_roas <= 0:
            print("error: --target-roas must be > 0", file=sys.stderr)
            return 2
        verdict = "ABOVE breakeven (profitable)" if args.target_roas >= breakeven \
            else "BELOW breakeven (buying at a loss)"
        print()
        print(f"  at target ROAS/MER    : {args.target_roas:g}x  -> {verdict}")
        if args.aov is not None:
            if args.aov <= 0:
                print("error: --aov must be > 0", file=sys.stderr)
                return 2
            # Contribution margin per order, minus the ad cost implied by the
            # target ROAS (AOV / ROAS = ad spend per order), is the headroom.
            cm_per_order = args.aov * args.margin
            ad_per_order = args.aov / args.target_roas
            headroom = cm_per_order - ad_per_order
            print(f"  per-order CM          : {cm_per_order:,.2f}  (AOV {args.aov:g} x {args.margin * 100:g}%)")
            print(f"  ad cost / order       : {ad_per_order:,.2f}  (AOV / {args.target_roas:g}x ROAS)")
            tag = "positive — room for overhead/profit" if headroom >= 0 else "NEGATIVE — loss per order"
            print(f"  -> CAC headroom/order : {headroom:,.2f}  ({tag})")
    print("  note: MER (total revenue / total ad spend) can't be inflated by per-platform")
    print("        attribution overlap the way last-click ROAS can — cross-check against it (s3 #5).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dtc_calc.py",
        description="DTC unit-economics calculator (stdlib only). "
        "Decision-support, not financial/accounting advice — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    cm = sub.add_parser("contribution-margin",
                        help="Per-order contribution margin net of returns")
    cm.add_argument("--aov", type=float, required=True, help="average order value")
    cm.add_argument("--cogs-pct", type=_parse_rate, required=True,
                    help="COGS as a fraction of AOV (e.g. 35%%)")
    cm.add_argument("--fulfillment", type=float, default=0.0,
                    help="fulfillment + outbound shipping cost per order")
    cm.add_argument("--payment-fee", type=_parse_rate, default=0.0,
                    help="payment processing fee as a fraction of AOV (e.g. 3%%)")
    cm.add_argument("--return-rate", type=_parse_rate, default=0.0,
                    help="fraction of orders returned (e.g. 35%%)")
    cm.add_argument("--return-cost", type=float, default=0.0,
                    help="all-in reverse-logistics cost per RETURNED order "
                    "(return shipping + inspection + restock + write-off)")
    cm.set_defaults(func=cmd_contribution_margin)

    lc = sub.add_parser("ltv-cac", help="LTV:CAC ratio + payback in orders")
    lc.add_argument("--aov", type=float, required=True, help="average order value")
    lc.add_argument("--margin", type=_parse_rate, required=True,
                    help="contribution margin as a fraction of AOV (e.g. 32%%)")
    lc.add_argument("--freq", type=float, required=True,
                    help="purchase frequency per year")
    lc.add_argument("--cac", type=float, required=True, help="customer acquisition cost")
    lc.add_argument("--monthly-churn", type=_parse_rate, default=None,
                    help="monthly churn (e.g. 5%%); if set, lifetime = 1/churn capped at horizon")
    lc.add_argument("--horizon-months", type=int, default=24,
                    help="lifetime horizon in months (default 24)")
    lc.set_defaults(func=cmd_ltv_cac)

    br = sub.add_parser("breakeven-roas",
                        help="Breakeven MER/ROAS from contribution margin")
    br.add_argument("--margin", type=_parse_rate, required=True,
                    help="contribution margin as a fraction of revenue (e.g. 30%%)")
    br.add_argument("--target-roas", type=float, default=None,
                    help="a target ROAS/MER to test against the breakeven (optional)")
    br.add_argument("--aov", type=float, default=None,
                    help="AOV, to print per-order CAC headroom at the target ROAS (optional)")
    br.set_defaults(func=cmd_breakeven_roas)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
