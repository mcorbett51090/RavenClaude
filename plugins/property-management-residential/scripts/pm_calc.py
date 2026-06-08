#!/usr/bin/env python3
"""pm_calc.py — a zero-dependency residential property-management calculator.

Removes arithmetic error from three recurring owner-reporting decisions a
leasing-and-tenant-ops / maintenance-coordinator / owner-and-portfolio-
reporting-analyst runs constantly:

  rentroll     Gross potential rent (GPR), economic vs. physical occupancy,
               and the loss-to-lease gap from a list of units. Each unit is
               market_rent[:actual_rent[:status]] — market_rent drives GPR,
               actual_rent drives collected/economic, status (occupied |
               vacant | notice | down) drives physical occupancy. Loss-to-
               lease = GPR - in-place rent on OCCUPIED units; it isolates the
               "we're under market" gap from the "the unit is empty" gap so
               you don't blame vacancy for a pricing problem (or vice versa).

  noi          Net operating income = operating income - operating expenses,
               EXCLUDING debt service, capex, and depreciation by construction.
               The tool REFUSES to net out a flagged --debt-service / --capex /
               --depreciation line into NOI and instead prints them BELOW the
               NOI line, because NOI is operating-only and is NOT cash flow.
               Prints NOI, the operating-expense ratio, and the below-the-line
               items so the levered-cash-flow question is answered separately.

  delinquency  Accounts-receivable aging into buckets (current / 1-30 / 31-60 /
               61-90 / 90+) from a list of balances, each amount[:days_past_due],
               plus each bucket as a % of the monthly rent roll. Surfaces the
               delinquency rate and which bucket the exposure sits in — the
               input to the collections ladder, not a substitute for applying
               it uniformly to every account.

This is a CALCULATOR, not a data source — it does not read a PM system, pull a
rent roll, or fetch a ledger. The user supplies every input; the tool does the
arithmetic and shows the formula. Stdlib only (argparse); runs anywhere Python
3.8+ is present.

IMPORTANT: outputs are decision-support, not the books of record. The rent roll
must reconcile to the system of record before any number is trusted (see
../CLAUDE.md and rent-roll-is-the-source-of-truth). NOI here is operating-only
and is NOT cash flow — the trust-account, GL posting, and tax treatment belong
to `finance`. Nothing here is legal advice: a delinquency number is the input
to a documented collections ladder whose pay-or-quit / eviction rungs flag to
counsel, never an instruction to act.

Examples
--------
  # Rent roll from five units (market[:actual[:status]]); a vacant/notice/down
  # unit contributes to GPR but not to collected rent or physical occupancy.
  python3 pm_calc.py rentroll \\
      --unit 1500:1450:occupied \\
      --unit 1500:1500:occupied \\
      --unit 1600:1550:occupied \\
      --unit 1500::vacant \\
      --unit 1550:1550:notice

  # NOI: operating income and operating expenses only; the debt-service, capex,
  # and depreciation lines are reported BELOW the NOI line, never netted in.
  python3 pm_calc.py noi \\
      --operating-income 240000 \\
      --operating-expense 96000 \\
      --debt-service 120000 --capex 30000 --depreciation 45000

  # Delinquency aging from balances (amount[:days_past_due]) against a monthly
  # rent roll of 7,650.
  python3 pm_calc.py delinquency --rent-roll 7650 \\
      --balance 1450:5 --balance 1500:40 --balance 3100:95
"""

from __future__ import annotations

import argparse
import sys

_STATUSES = ("occupied", "vacant", "notice", "down")


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def _parse_unit(s: str) -> tuple:
    """Parse 'market[:actual[:status]]' into (market, actual, status)."""
    parts = s.split(":")
    if not parts or parts[0] == "":
        raise argparse.ArgumentTypeError(f"unit needs a market rent, got {s!r}")
    try:
        market = float(parts[0])
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"market rent must be a number in {s!r}"
        ) from None
    actual_raw = parts[1].strip() if len(parts) >= 2 else ""
    try:
        actual = float(actual_raw) if actual_raw != "" else 0.0
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"actual rent must be a number in {s!r}"
        ) from None
    status = parts[2].strip().lower() if len(parts) >= 3 and parts[2].strip() else "occupied"
    if status not in _STATUSES:
        raise argparse.ArgumentTypeError(
            f"status must be one of {_STATUSES}, got {status!r} in {s!r}"
        )
    if market < 0 or actual < 0:
        raise argparse.ArgumentTypeError(f"rents must be >= 0 in {s!r}")
    return (market, actual, status)


def _parse_balance(s: str) -> tuple:
    """Parse 'amount[:days_past_due]' into (amount, days_past_due)."""
    parts = s.split(":")
    try:
        amount = float(parts[0])
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"balance amount must be a number in {s!r}"
        ) from None
    days = 0
    if len(parts) >= 2 and parts[1].strip():
        try:
            days = int(float(parts[1]))
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"days-past-due must be a number in {s!r}"
            ) from None
    if amount < 0:
        raise argparse.ArgumentTypeError(f"balance amount must be >= 0 in {s!r}")
    if days < 0:
        raise argparse.ArgumentTypeError(f"days-past-due must be >= 0 in {s!r}")
    return (amount, days)


def cmd_rentroll(args: argparse.Namespace) -> int:
    units = args.unit
    if not units:
        print("error: at least one --unit is required", file=sys.stderr)
        return 2

    total = len(units)
    occupied = [u for u in units if u[2] == "occupied"]
    # GPR = market rent across EVERY unit (occupied or not) — the ceiling.
    gpr = sum(market for market, _, _ in units)
    # Collected/economic = actual rent on occupied units (the rent in place).
    collected = sum(actual for _, actual, status in units if status == "occupied")
    # In-place market on occupied units — used to isolate loss-to-lease from
    # vacancy: the gap to market on units that ARE rented, not the empty ones.
    occupied_market = sum(market for market, _, status in units if status == "occupied")
    loss_to_lease = occupied_market - collected

    physical_occ = len(occupied) / total if total else 0.0
    economic_occ = collected / gpr if gpr > 0 else 0.0
    vacancy_loss = gpr - occupied_market  # the market rent of the non-occupied units

    print("Rent roll — GPR, occupancy, loss-to-lease")
    print(f"  units                              : {total}")
    print(f"  occupied                           : {len(occupied)}")
    print(f"  gross potential rent (GPR, market) : {gpr:,.2f}")
    print(f"  in-place market on occupied        : {occupied_market:,.2f}")
    print(f"  collected (actual on occupied)     : {collected:,.2f}")
    print()
    print(f"  → physical occupancy (units)       : {_pct(physical_occ)}")
    print(f"  → economic occupancy (collected/GPR): {_pct(economic_occ)}")
    print(f"  → loss-to-lease (occ. market-actual): {loss_to_lease:,.2f}")
    print(f"  → vacancy loss (GPR-occ. market)   : {vacancy_loss:,.2f}")
    print()
    if loss_to_lease > 0:
        print("  note: loss-to-lease is the gap to market on units that ARE")
        print("        rented — a PRICING gap, fixed at renewal, not by leasing.")
    if vacancy_loss > 0:
        print("  note: vacancy loss is the market rent of empty/notice/down")
        print("        units — a LEASING/turn gap, fixed by filling units.")
    print("  reminder: separate loss-to-lease (under market) from vacancy")
    print("            (empty) — they have different fixes. Reconcile every")
    print("            number to the system of record before trusting it.")
    return 0


def cmd_noi(args: argparse.Namespace) -> int:
    if args.operating_income < 0 or args.operating_expense < 0:
        print("error: operating income/expense must be >= 0", file=sys.stderr)
        return 2

    noi = args.operating_income - args.operating_expense
    opex_ratio = (
        args.operating_expense / args.operating_income
        if args.operating_income > 0
        else 0.0
    )

    print("NOI — operating income minus operating expense (operating-only)")
    print(f"  operating income           : {args.operating_income:,.2f}")
    print(f"  - operating expense        : {args.operating_expense:,.2f}")
    print(f"  → NET OPERATING INCOME     : {noi:,.2f}")
    print(f"  → operating-expense ratio  : {_pct(opex_ratio)}")

    below_line = (
        ("debt service", args.debt_service),
        ("capex", args.capex),
        ("depreciation", args.depreciation),
    )
    flagged = [(name, val) for name, val in below_line if val]
    if flagged:
        print()
        print("  BELOW the NOI line — NOT netted into NOI (operating-only rule):")
        for name, val in flagged:
            print(f"    {name:<22}: {val:,.2f}")
        remaining = noi - sum(val for _, val in flagged)
        print(f"    → after below-the-line   : {remaining:,.2f}  (levered/cash view)")
        print("  ⚠ this 'after below-the-line' figure is NOT NOI. NOI excludes")
        print("    debt service, capex, and depreciation by construction; mixing")
        print("    them in answers the cash-flow question, a different question.")
    print("  reminder: NOI is operating-only and is NOT cash flow. The trust")
    print("            account, GL posting, and tax treatment belong to finance.")
    return 0


def cmd_delinquency(args: argparse.Namespace) -> int:
    balances = args.balance
    if not balances:
        print("error: at least one --balance is required", file=sys.stderr)
        return 2
    if args.rent_roll <= 0:
        print("error: --rent-roll must be > 0", file=sys.stderr)
        return 2

    buckets = {
        "current (0)": 0.0,
        "1-30": 0.0,
        "31-60": 0.0,
        "61-90": 0.0,
        "90+": 0.0,
    }
    for amount, days in balances:
        if days <= 0:
            buckets["current (0)"] += amount
        elif days <= 30:
            buckets["1-30"] += amount
        elif days <= 60:
            buckets["31-60"] += amount
        elif days <= 90:
            buckets["61-90"] += amount
        else:
            buckets["90+"] += amount

    total = sum(buckets.values())
    past_due = total - buckets["current (0)"]

    print("Delinquency — A/R aging buckets + % of rent roll")
    print(f"  monthly rent roll          : {args.rent_roll:,.2f}")
    print(f"  total outstanding balance  : {total:,.2f}")
    print()
    print("  bucket          |     amount | % of rent roll")
    print("  ----------------+------------+----------------")
    for label, amount in buckets.items():
        share = amount / args.rent_roll if args.rent_roll > 0 else 0.0
        print(f"  {label:<15} | {amount:>10,.2f} | {_pct(share):>14}")
    print()
    delinquency_rate = past_due / args.rent_roll if args.rent_roll > 0 else 0.0
    print(f"  → past-due (excl. current) : {past_due:,.2f}")
    print(f"  → delinquency rate         : {_pct(delinquency_rate)} of rent roll")
    if buckets["90+"] > 0:
        print("  ⚠ 90+ exposure present — the oldest bucket is the hardest to")
        print("    collect; assess charge-off vs. still-collectible separately.")
    print("  reminder: this is the INPUT to a documented collections ladder")
    print("            applied uniformly to every account (no selective")
    print("            enforcement). The pay-or-quit / eviction rungs FLAG to")
    print("            counsel — this number is not an instruction to act.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pm_calc.py",
        description="Residential property-management decision calculator (stdlib "
        "only). Decision-support, not the books of record — reconcile to the "
        "system of record; NOI is operating-only, not cash flow; delinquency "
        "feeds a uniform collections ladder whose legal rungs flag to counsel.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    rr = sub.add_parser(
        "rentroll",
        help="GPR + physical/economic occupancy + loss-to-lease vs. vacancy",
    )
    rr.add_argument(
        "--unit",
        type=_parse_unit,
        action="append",
        default=[],
        metavar="MARKET[:ACTUAL[:STATUS]]",
        help="a unit: market rent, optional actual rent, optional status "
        "(occupied|vacant|notice|down; default occupied). Repeatable.",
    )
    rr.set_defaults(func=cmd_rentroll)

    noi = sub.add_parser(
        "noi",
        help="NOI = operating income - operating expense (excludes debt/capex/dep.)",
    )
    noi.add_argument("--operating-income", type=float, required=True,
                     help="operating income (rent + other operating revenue)")
    noi.add_argument("--operating-expense", type=float, required=True,
                     help="operating expenses (taxes, insurance, repairs, mgmt, utilities)")
    noi.add_argument("--debt-service", type=float, default=0.0,
                     help="debt service — reported BELOW the NOI line, never netted in")
    noi.add_argument("--capex", type=float, default=0.0,
                     help="capital expenditure — below the NOI line, never netted in")
    noi.add_argument("--depreciation", type=float, default=0.0,
                     help="depreciation — below the NOI line, never netted in")
    noi.set_defaults(func=cmd_noi)

    dl = sub.add_parser(
        "delinquency",
        help="A/R aging buckets + delinquency rate as a % of the rent roll",
    )
    dl.add_argument("--rent-roll", type=float, required=True,
                    help="monthly rent roll (denominator for the delinquency rate)")
    dl.add_argument(
        "--balance",
        type=_parse_balance,
        action="append",
        default=[],
        metavar="AMOUNT[:DAYS_PAST_DUE]",
        help="an outstanding balance: amount, optional days-past-due (default 0 = "
        "current). Repeatable.",
    )
    dl.set_defaults(func=cmd_delinquency)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
