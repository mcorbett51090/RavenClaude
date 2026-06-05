#!/usr/bin/env python3
"""sourcing_calc.py — a zero-dependency strategic-sourcing decision calculator.

Removes arithmetic error from three recurring sourcing decisions a category
manager / sourcing lead / spend analyst runs constantly:

  tco             TOTAL COST OF OWNERSHIP per supplier bid. Adds the cost stack
                  the unit price hides — freight, inventory carry, quality/defect
                  cost, switching/transition, and recurring operating cost over a
                  horizon — and compares two or more bids on TCO/unit, not list
                  price. Flags the bid whose LOW unit price loses on total cost
                  (the §3 #2 trap). Pairs with knowledge/sourcing-economics.md
                  and the source-on-tco skill.

  savings         SAVINGS REALIZATION. Walks negotiated savings down to the
                  number Finance recognizes: applies the realized-volume fraction
                  (volume miss), the compliance/maverick fraction (off-contract
                  buying), and the in-budget offset (already in the AOP -> cost
                  avoidance, not incremental). Prints negotiated, realized, the
                  leakage gap, and the realization rate. Pairs with the
                  validate-realized-savings skill and the savings decision tree.

  terms           PAYMENT-TERMS net-present-value of a terms change (e.g.
                  Net-30 -> Net-60), as the working-capital benefit of holding
                  cash longer, and what an early-pay discount must beat to be
                  worth taking (the discount's implied annualized rate). Pairs
                  with knowledge/sourcing-economics.md (§3 #7 demand/terms lever).

This is a CALCULATOR, not a data source — it does not fetch indices, benchmarks,
or live rates. The user supplies every input; the tool does the arithmetic and
shows the formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not legal, audit, or financial advice
(see ../CLAUDE.md s2). Validate every figure against the client's actual data and
Finance-agreed baseline before any deliverable (CLAUDE.md s3 #3, #8).

Examples
--------
  # TCO: compare two bids on a 1-year horizon, 10,000 units.
  #   Bid A: $10.00 unit, $0.40 freight/unit, 8% carry, 2% defect, $5,000 switch
  #   Bid B: $9.40 unit (incumbent), $0.55 freight/unit, 8% carry, 4% defect, $0 switch
  python3 sourcing_calc.py tco --units 10000 \\
      --bid "A:10.00:0.40:0.02:5000" \\
      --bid "B:9.40:0.55:0.04:0" \\
      --carry-rate 8%

  # Savings realization: $1,000,000 negotiated, 85% of volume realized,
  #   90% on-contract compliance, 30% already in budget.
  python3 sourcing_calc.py savings --negotiated 1000000 \\
      --volume-realized 85% --compliance 90% --in-budget 30%

  # Payment terms: extend Net-30 -> Net-60 on $5,000,000 annual spend at a
  #   12% cost of capital; and test a 2/10 net-30 early-pay discount.
  python3 sourcing_calc.py terms --annual-spend 5000000 \\
      --days-current 30 --days-new 60 --cost-of-capital 12% \\
      --discount 2% --discount-days 10 --net-days 30
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '8%' or '0.08' into a fraction (0.08)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '8%' or '0.08', got {s!r}")


def cmd_tco(args: argparse.Namespace) -> int:
    if args.units <= 0:
        print("error: --units must be > 0", file=sys.stderr)
        return 2
    if not 0.0 <= args.carry_rate < 1.0:
        print("error: --carry-rate must be in [0%, 100%)", file=sys.stderr)
        return 2

    bids = []
    for raw in args.bid:
        parts = raw.split(":")
        if len(parts) != 5:
            print(
                f"error: --bid must be NAME:UNIT:FREIGHT:DEFECT_RATE:SWITCH, got {raw!r}",
                file=sys.stderr,
            )
            return 2
        name, unit_s, freight_s, defect_s, switch_s = parts
        try:
            unit = float(unit_s)
            freight = float(freight_s)
            defect = _parse_rate(defect_s)
            switch = float(switch_s)
        except (ValueError, argparse.ArgumentTypeError):
            print(f"error: non-numeric field in --bid {raw!r}", file=sys.stderr)
            return 2
        if not 0.0 <= defect < 1.0:
            print(f"error: defect rate in {raw!r} must be in [0%, 100%)", file=sys.stderr)
            return 2
        bids.append((name, unit, freight, defect, switch))

    print(f"Total cost of ownership — {args.units:,.0f} units, {args.horizon_years:g}-year horizon")
    print(f"  carry rate on landed value : {args.carry_rate * 100:g}%/yr")
    print(
        "  bid | landed/unit | quality | carry | switch | recurring | TOTAL | TCO/unit"
    )
    print(
        "  ----+-------------+---------+-------+--------+-----------+-------+---------"
    )

    results = []
    for name, unit, freight, defect, switch in bids:
        landed_unit = unit + freight
        landed_total = landed_unit * args.units
        # quality cost: defective units must be re-bought at landed unit cost
        quality = landed_total * defect
        # inventory carry on average inventory; approximated as carry_rate * landed
        # value held, scaled by horizon (a held-cash cost, not a per-turn model)
        carry = landed_total * args.carry_rate * args.horizon_years
        recurring = args.operating * args.horizon_years
        total = landed_total + quality + carry + switch + recurring
        tco_unit = total / args.units
        results.append((name, total, tco_unit))
        print(
            f"  {name:<3} | {landed_unit:>11,.2f} | {quality:>7,.0f} | {carry:>5,.0f} | "
            f"{switch:>6,.0f} | {recurring:>9,.0f} | {total:>5,.0f} | {tco_unit:>7,.3f}"
        )

    print()
    results.sort(key=lambda r: r[1])
    best = results[0]
    print(f"  -> lowest TCO : {best[0]} at {best[1]:,.0f} ({best[2]:,.3f}/unit)")
    # surface the unit-price trap: did the lowest LIST price also win on TCO?
    by_unit = sorted(bids, key=lambda b: b[1] + b[2])
    cheapest_list = by_unit[0][0]
    if cheapest_list != best[0]:
        print(
            f"  -> NOTE: {cheapest_list} had the lowest landed unit price but LOST on TCO."
        )
        print("     The unit-price 'savings' was erased by quality/carry/switching (s3 #2).")
    print("  note: this is decision-support — validate freight, defect, carry, and")
    print("        switching with the client's actuals before any award (s3 #8).")
    return 0


def cmd_savings(args: argparse.Namespace) -> int:
    for label, val in (
        ("--volume-realized", args.volume_realized),
        ("--compliance", args.compliance),
        ("--in-budget", args.in_budget),
    ):
        if not 0.0 <= val <= 1.0:
            print(f"error: {label} must be in [0%, 100%]", file=sys.stderr)
            return 2

    negotiated = args.negotiated
    # leakage chain: negotiated * realized-volume * on-contract-compliance
    after_volume = negotiated * args.volume_realized
    realized = after_volume * args.compliance
    # in-budget portion is cost avoidance vs the plan, not incremental savings
    incremental = realized * (1.0 - args.in_budget)
    realization_rate = (realized / negotiated * 100.0) if negotiated else 0.0
    incremental_rate = (incremental / negotiated * 100.0) if negotiated else 0.0

    print("Savings realization — negotiated walked down to the P&L")
    print(f"  negotiated savings        : {negotiated:,.0f}")
    print(f"  x volume realized {args.volume_realized * 100:>5g}%   : {after_volume:,.0f}")
    print(f"  x on-contract {args.compliance * 100:>5g}%       : {realized:,.0f}  (REALIZED)")
    print(f"  leakage vs negotiated     : {negotiated - realized:,.0f}")
    print(f"  -> realization rate       : {realization_rate:.1f}% of negotiated")
    print()
    print(f"  in-budget (AOP) portion   : {args.in_budget * 100:g}% -> cost avoidance, not incremental")
    print(f"  -> INCREMENTAL vs budget  : {incremental:,.0f}  ({incremental_rate:.1f}% of negotiated)")
    print("  note: only REALIZED counts to the P&L, and only the above-budget portion")
    print("        is incremental (s3 #3). Agree the baseline with Finance FIRST.")
    if realization_rate < 60.0:
        print("  flag: realization < 60% — typical leakage range is 30-60% without")
        print("        tracking; locate the leak (volume miss vs maverick) before re-sourcing.")
    return 0


def cmd_terms(args: argparse.Namespace) -> int:
    if args.annual_spend <= 0:
        print("error: --annual-spend must be > 0", file=sys.stderr)
        return 2
    if not 0.0 <= args.cost_of_capital < 1.0:
        print("error: --cost-of-capital must be in [0%, 100%)", file=sys.stderr)
        return 2
    delta_days = args.days_new - args.days_current
    daily_spend = args.annual_spend / 365.0
    # extra cash held = daily spend * extra days outstanding
    extra_cash_held = daily_spend * delta_days
    annual_benefit = extra_cash_held * args.cost_of_capital

    print("Payment-terms working-capital value")
    print(f"  annual spend              : {args.annual_spend:,.0f}")
    print(f"  terms                     : Net-{args.days_current:g} -> Net-{args.days_new:g} ({delta_days:+g} days)")
    print(f"  cost of capital           : {args.cost_of_capital * 100:g}%")
    print(f"  extra cash held (1-time)  : {extra_cash_held:,.0f}  (daily spend x {delta_days:+g}d)")
    print(f"  -> annual carry benefit   : {annual_benefit:,.0f}/yr")
    if delta_days < 0:
        print("  note: terms SHORTENED — this is a cost (you fund the supplier sooner).")

    if args.discount is not None:
        if not 0.0 <= args.discount < 1.0:
            print("error: --discount must be in [0%, 100%)", file=sys.stderr)
            return 2
        early_days = args.net_days - args.discount_days
        if early_days <= 0:
            print("error: --net-days must exceed --discount-days", file=sys.stderr)
            return 2
        # implied annualized rate of taking an early-pay discount:
        #   (d / (1 - d)) * (365 / early_days)
        implied = (args.discount / (1.0 - args.discount)) * (365.0 / early_days)
        print()
        print(
            f"  early-pay discount        : {args.discount * 100:g}/{args.discount_days:g} "
            f"net {args.net_days:g}"
        )
        print(f"  days paid early           : {early_days:g}")
        print(f"  -> implied annualized rate: {implied * 100:.1f}%")
        verdict = "TAKE the discount" if implied > args.cost_of_capital else "KEEP the cash (skip discount)"
        print(
            f"  -> vs cost of capital {args.cost_of_capital * 100:g}% : {verdict}"
        )
    print("  note: decision-support — confirm spend timing and the firm's true cost")
    print("        of capital with Finance before acting (s3 #8).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sourcing_calc.py",
        description="Strategic-sourcing decision calculator (stdlib only). "
        "Decision-support, not legal/audit/financial advice — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    tco = sub.add_parser("tco", help="Total cost of ownership — compare bids")
    tco.add_argument("--units", type=float, required=True, help="annual unit volume")
    tco.add_argument(
        "--bid",
        action="append",
        required=True,
        metavar="NAME:UNIT:FREIGHT:DEFECT_RATE:SWITCH",
        help="repeatable; e.g. 'A:10.00:0.40:0.02:5000' "
        "(unit price, freight/unit, defect rate, one-time switching cost)",
    )
    tco.add_argument(
        "--carry-rate",
        type=_parse_rate,
        default=0.0,
        help="annual inventory-carry rate on landed value (default 0%%)",
    )
    tco.add_argument(
        "--operating",
        type=float,
        default=0.0,
        help="annual recurring operating cost per bid (training, support; default 0)",
    )
    tco.add_argument(
        "--horizon-years",
        type=float,
        default=1.0,
        help="cost horizon in years (default 1)",
    )
    tco.set_defaults(func=cmd_tco)

    sav = sub.add_parser("savings", help="Savings realization — negotiated to realized")
    sav.add_argument("--negotiated", type=float, required=True, help="negotiated savings amount")
    sav.add_argument(
        "--volume-realized",
        type=_parse_rate,
        default=1.0,
        help="fraction of contracted volume actually purchased (default 100%%)",
    )
    sav.add_argument(
        "--compliance",
        type=_parse_rate,
        default=1.0,
        help="fraction bought on-contract, not maverick (default 100%%)",
    )
    sav.add_argument(
        "--in-budget",
        type=_parse_rate,
        default=0.0,
        help="fraction already in the AOP/budget -> cost avoidance (default 0%%)",
    )
    sav.set_defaults(func=cmd_savings)

    trm = sub.add_parser("terms", help="Payment-terms working-capital value + early-pay test")
    trm.add_argument("--annual-spend", type=float, required=True, help="annual spend with the supplier")
    trm.add_argument("--days-current", type=float, required=True, help="current payment terms (days)")
    trm.add_argument("--days-new", type=float, required=True, help="proposed payment terms (days)")
    trm.add_argument(
        "--cost-of-capital",
        type=_parse_rate,
        required=True,
        help="annual cost of capital / hurdle rate (e.g. 12%%)",
    )
    trm.add_argument(
        "--discount",
        type=_parse_rate,
        default=None,
        help="optional early-pay discount to test (e.g. 2%%)",
    )
    trm.add_argument("--discount-days", type=float, default=10.0, help="early-pay window (default 10)")
    trm.add_argument("--net-days", type=float, default=30.0, help="net due date (default 30)")
    trm.set_defaults(func=cmd_terms)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
