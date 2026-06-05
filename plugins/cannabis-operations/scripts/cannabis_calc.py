#!/usr/bin/env python3
"""cannabis_calc.py — a zero-dependency cannabis-operations decision calculator.

Removes arithmetic error from three recurring cannabis-operations decisions a
licensed operator / compliance lead / finance analyst runs constantly:

  effective-280e  The federal effective tax rate under IRC 280E as a function of
                  how much of total cost is DEFENSIBLE COGS. Because 280E
                  disallows ordinary deductions for a Schedule I/II operator,
                  only COGS shelters income. Shows the effective rate at the
                  operator's current COGS share and the rate at a target share,
                  and the tax delta a defensible 471 cost study could move.
                  Pairs with knowledge/cannabis-compliance-economics.md and the
                  frame-280e-cogs skill. CPA decision-support, NOT tax advice.

  inventory-turns The inventory turns, days-on-hand (DIO), and the CASH trapped
                  vs an optimal days-on-hand target. Turns are a cash AND a
                  compliance metric (aged/perishable flower is trapped cash plus
                  expiry/traceability risk). Pairs with the read-inventory-turns
                  skill and knowledge/cannabis-kpi-glossary.md.

  saleable-yield  Converts HARVEST yield to SALEABLE yield by subtracting a
                  cause-tagged test-fail rate, then runs the remediate-vs-destroy
                  economic test on the failed portion. Pairs with
                  knowledge/cannabis-testing-remediation-decision-tree.md.

This is a CALCULATOR, not a data source — it does not fetch tax rates, market
prices, fail rates, or live costs. The user supplies every input; the tool does
the arithmetic and shows the formula. Stdlib only (argparse); runs anywhere
Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not tax, legal, licensing, or financial
advice (see ../CLAUDE.md §2). 280E/471 positions are CPA decision-support; the
2026 partial rescheduling did NOT remove 280E for state-licensed ADULT-USE
operators — confirm the operator's segment and the current federal posture before
relying on any number (CLAUDE.md §2, §3 #3, #8). Validate every figure against the
operator's actual data and state regulator before any deliverable.

Examples
--------
  # 280E effective rate: $5M revenue, $2M operating expense, currently 40% of
  # the $2.6M total cost classified as COGS; modeling a defensible 55% target.
  # Federal statutory rate 21%.
  python3 cannabis_calc.py effective-280e --revenue 5000000 --total-cost 2600000 \\
      --cogs-share 40% --target-cogs-share 55% --statutory-rate 21%

  # Inventory turns: $1.2M annual COGS, $180k average inventory, target 28 DIO
  python3 cannabis_calc.py inventory-turns --annual-cogs 1200000 \\
      --avg-inventory 180000 --target-days 28

  # Saleable yield: 100 lb harvest, 12% fail rate; of failures 70% are microbial.
  # Microbial remediation costs $400/lb, lot is worth $1200/lb saleable.
  python3 cannabis_calc.py saleable-yield --harvest-lbs 100 --fail-rate 12% \\
      --microbial-share 70% --remediation-cost-per-lb 400 --value-per-lb 1200
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '40%' or '0.40' into a fraction (0.40)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '40%' or '0.40', got {s!r}")


def _effective_rate(revenue: float, total_cost: float, cogs_share: float,
                    statutory: float) -> tuple[float, float, float]:
    """Return (taxable_income, tax, effective_rate_on_book_profit).

    Under 280E only COGS reduces taxable income; non-COGS operating costs are
    non-deductible. Book (economic) profit = revenue - total_cost. Effective rate
    is tax / book profit (the number an operator actually feels).
    """
    cogs = total_cost * cogs_share
    taxable_income = max(revenue - cogs, 0.0)  # only COGS deducted
    tax = taxable_income * statutory
    book_profit = revenue - total_cost
    effective = (tax / book_profit) if book_profit > 0 else float("inf")
    return taxable_income, tax, effective


def cmd_effective_280e(args: argparse.Namespace) -> int:
    if not 0.0 <= args.cogs_share <= 1.0:
        print("error: --cogs-share must be in [0%, 100%]", file=sys.stderr)
        return 2
    if args.total_cost > args.revenue:
        print("note: total cost exceeds revenue — book profit is negative; "
              "effective-rate-on-profit is undefined (still pays tax on revenue-COGS).",
              file=sys.stderr)

    print("280E effective federal tax rate vs COGS share")
    print(f"  revenue                  : {args.revenue:,.0f}")
    print(f"  total cost               : {args.total_cost:,.0f}")
    print(f"  statutory rate           : {args.statutory_rate * 100:g}%")
    book_profit = args.revenue - args.total_cost
    print(f"  book (economic) profit   : {book_profit:,.0f}")
    print()

    def _line(label: str, share: float) -> float:
        ti, tax, eff = _effective_rate(args.revenue, args.total_cost, share, args.statutory_rate)
        cogs = args.total_cost * share
        eff_s = "n/a (no book profit)" if eff == float("inf") else f"{eff * 100:.1f}%"
        print(f"  {label}")
        print(f"    COGS classified ({share * 100:g}%) : {cogs:,.0f}")
        print(f"    taxable income (rev-COGS) : {ti:,.0f}")
        print(f"    federal tax               : {tax:,.0f}")
        print(f"    effective rate on profit  : {eff_s}")
        return tax

    tax_now = _line("at current COGS share:", args.cogs_share)
    if args.target_cogs_share is not None:
        if not 0.0 <= args.target_cogs_share <= 1.0:
            print("error: --target-cogs-share must be in [0%, 100%]", file=sys.stderr)
            return 2
        print()
        tax_target = _line("at target COGS share:", args.target_cogs_share)
        print()
        print(f"  → tax delta from a DEFENSIBLE COGS shift: {tax_now - tax_target:,.0f} saved/yr")
        print("    (only if the reclassification is documented + defensible under §471 —")
        print("     an undocumented reclassification is a disallowed one. CPA decision-support.)")
    print()
    print("  reminder: 280E still applies to state-licensed ADULT-USE operators after the")
    print("            April-2026 partial (medical-only) rescheduling. Confirm segment + posture.")
    return 0


def cmd_inventory_turns(args: argparse.Namespace) -> int:
    if args.avg_inventory <= 0:
        print("error: --avg-inventory must be > 0", file=sys.stderr)
        return 2
    turns = args.annual_cogs / args.avg_inventory
    dio = 365.0 / turns if turns > 0 else float("inf")

    print("Inventory turns / days-on-hand")
    print(f"  annual COGS              : {args.annual_cogs:,.0f}")
    print(f"  average inventory        : {args.avg_inventory:,.0f}")
    print(f"  → inventory turns        : {turns:,.2f} x / year")
    print(f"  → days inventory (DIO)   : {dio:,.1f} days (365 / turns)")

    if args.target_days is not None:
        if args.target_days <= 0:
            print("error: --target-days must be > 0", file=sys.stderr)
            return 2
        daily_cogs = args.annual_cogs / 365.0
        target_inventory = daily_cogs * args.target_days
        trapped = args.avg_inventory - target_inventory
        print(f"  target days-on-hand      : {args.target_days:g} days")
        print(f"  inventory at target      : {target_inventory:,.0f}")
        if trapped > 0:
            print(f"  → CASH trapped vs target : {trapped:,.0f} (cash you could free by hitting target)")
            print("    aged/perishable flower is trapped cash AND an expiry/traceability risk (§3 #5).")
        else:
            print(f"  → already at/under target by {-trapped:,.0f} — watch for stockout/menu gaps instead.")
    print("  note: optimal days-on-hand commonly cited ~20–35 [verify-at-use]; calibrate by")
    print("        category — perishable flower turns faster than durable accessories.")
    return 0


def cmd_saleable_yield(args: argparse.Namespace) -> int:
    if not 0.0 <= args.fail_rate <= 1.0:
        print("error: --fail-rate must be in [0%, 100%]", file=sys.stderr)
        return 2
    if not 0.0 <= args.microbial_share <= 1.0:
        print("error: --microbial-share must be in [0%, 100%]", file=sys.stderr)
        return 2

    failed_lbs = args.harvest_lbs * args.fail_rate
    passed_lbs = args.harvest_lbs - failed_lbs
    microbial_lbs = failed_lbs * args.microbial_share
    pesticide_lbs = failed_lbs - microbial_lbs  # pesticide/heavy-metal = destruction default

    print("Saleable yield + remediate-vs-destroy economics")
    print(f"  harvest yield            : {args.harvest_lbs:,.2f} lb")
    print(f"  test-fail rate (tagged)  : {args.fail_rate * 100:g}%")
    print(f"  → failed                 : {failed_lbs:,.2f} lb  (microbial {microbial_lbs:,.2f} / "
          f"pesticide+metal {pesticide_lbs:,.2f})")
    print(f"  → SALEABLE before remediation : {passed_lbs:,.2f} lb")
    print()
    print("  Pesticide/heavy-metal portion: destruction default (no remediation path) →")
    print(f"    write-off value          : {pesticide_lbs * args.value_per_lb:,.0f}  (fix the INPUT)")

    if args.remediation_cost_per_lb is not None and microbial_lbs > 0:
        remed_cost = microbial_lbs * args.remediation_cost_per_lb
        recovered_value = microbial_lbs * args.value_per_lb * (1.0 - args.buyer_haircut)
        print()
        print("  Microbial portion: remediate-vs-destroy test (only WHERE state permits resale):")
        print(f"    remediation cost         : {remed_cost:,.0f} "
              f"({args.remediation_cost_per_lb:g}/lb x {microbial_lbs:,.2f} lb)")
        print(f"    recovered saleable value : {recovered_value:,.0f} "
              f"(after {args.buyer_haircut * 100:g}% buyer haircut)")
        verdict = "REMEDIATE" if recovered_value > remed_cost else "DESTROY"
        print(f"    → verdict                : {verdict} "
              f"(net {recovered_value - remed_cost:,.0f})")
        if verdict == "REMEDIATE":
            print(f"    saleable if remediated   : {passed_lbs + microbial_lbs:,.2f} lb total")
    print()
    print("  reminder: 'remediable' != 'saleable in your state' — confirm the state permits")
    print("            resale of remediated product, and record destruction in track-and-trace.")
    print("            Use YOUR measured fail rate, [ESTIMATE] until batches accrue (§3 #6).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cannabis_calc.py",
        description="Cannabis-operations decision calculator (stdlib only). "
        "Decision-support, not tax/legal/financial advice — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("effective-280e", help="280E effective tax rate vs COGS share")
    e.add_argument("--revenue", type=float, required=True, help="total revenue")
    e.add_argument("--total-cost", type=float, required=True,
                   help="total cost (COGS + operating expense)")
    e.add_argument("--cogs-share", type=_parse_rate, required=True,
                   help="fraction of total cost currently classified as defensible COGS")
    e.add_argument("--target-cogs-share", type=_parse_rate, default=None,
                   help="optional target COGS share to model a §471 cost-study shift")
    e.add_argument("--statutory-rate", type=_parse_rate, default=0.21,
                   help="federal statutory rate (default 21%%)")
    e.set_defaults(func=cmd_effective_280e)

    t = sub.add_parser("inventory-turns", help="Inventory turns, DIO, and trapped cash")
    t.add_argument("--annual-cogs", type=float, required=True, help="annual COGS")
    t.add_argument("--avg-inventory", type=float, required=True,
                   help="average inventory value on hand")
    t.add_argument("--target-days", type=float, default=None,
                   help="optional target days-on-hand for a trapped-cash readout")
    t.set_defaults(func=cmd_inventory_turns)

    y = sub.add_parser("saleable-yield", help="Harvest→saleable yield + remediate-vs-destroy")
    y.add_argument("--harvest-lbs", type=float, required=True, help="gross harvest yield (lb)")
    y.add_argument("--fail-rate", type=_parse_rate, required=True,
                   help="test-fail rate (use your own measured rate)")
    y.add_argument("--microbial-share", type=_parse_rate, default=1.0,
                   help="fraction of failures that are microbial (remediable); "
                   "remainder treated as pesticide/heavy-metal destruction (default 100%%)")
    y.add_argument("--value-per-lb", type=float, required=True,
                   help="saleable value per lb")
    y.add_argument("--remediation-cost-per-lb", type=float, default=None,
                   help="microbial remediation cost per lb (enables the remediate-vs-destroy test)")
    y.add_argument("--buyer-haircut", type=_parse_rate, default=0.0,
                   help="price haircut a buyer applies to remediated product (default 0%%)")
    y.set_defaults(func=cmd_saleable_yield)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
