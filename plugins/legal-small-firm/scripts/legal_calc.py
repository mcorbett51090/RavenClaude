#!/usr/bin/env python3
"""legal_calc.py — a zero-dependency small-firm legal-practice decision calculator.

Removes arithmetic error from four recurring practice-economics + compliance
checks a solo / small-firm attorney (who is also the rainmaker and the COO) runs
constantly:

  realization     The realization CASCADE and the effective hourly rate. Walks
                  standard value (hours worked x standard rate) -> billed value
                  (after write-downs) -> collected value (after write-offs), and
                  prints utilization / realization / collection as ratios plus
                  the effective hourly rate (collected / hours worked). Pairs with
                  knowledge/legal-practice-decision-trees.md (Billing Rate Review).

  matter-profit   Single-matter (or attorney) profitability against the RULE OF
                  THIRDS. collected revenue - (comp + overhead) = profit; flags
                  whether collected revenue clears the >=3x fully-loaded-cost
                  hiring/keep threshold. Pairs with
                  knowledge/legal-practice-kpi-glossary.md (Rule of Thirds).

  utilization     The billable-hour ratio and the NON-BILLABLE split (delegable
                  admin vs attorney-only). Flags how much billable attorney
                  capacity is locked in delegable work. Pairs with the
                  utilization-capacity scenario + best-practices.

  trust-recon     The THREE-WAY trust/IOLTA reconciliation check: bank statement
                  balance == trust book balance == sum of client ledgers. Prints
                  the two pairwise differences and PASS/FAIL. This is a compliance
                  arithmetic aid, NOT an ethics ruling. Pairs with
                  knowledge/legal-intake-and-trust-decision-trees.md (IOLTA tree).

This is a CALCULATOR, not a data source — it does not fetch benchmarks, rates,
or live balances. The user supplies every input; the tool does the arithmetic and
shows the formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, NOT legal advice, an ethics ruling, or
licensed financial advice (see ../CLAUDE.md SS2). A trust-recon FAIL is an
arithmetic flag to route to the responsible attorney + the state bar rules, never
a finding of misconduct. Validate every figure against the firm's actual data and
state rules before any deliverable (CLAUDE.md SS3 #6, #8).

Examples
--------
  # Realization cascade: 1500 hrs worked at $300 standard, $1000 available hrs
  # base, billed $405,000 (write-downs), collected $375,000 (write-offs)
  python3 legal_calc.py realization --hours-worked 1500 --standard-rate 300 \\
      --available-hours 2000 --billed 405000 --collected 375000

  # Matter / attorney profitability vs Rule of Thirds: $450k collected,
  # $150k fully-loaded comp, 30% overhead load on collected revenue
  python3 legal_calc.py matter-profit --collected 450000 --comp 150000 \\
      --overhead-rate 30%

  # Utilization: 1500 billable of 2000 available hrs; 300 delegable + 200
  # attorney-only non-billable hrs
  python3 legal_calc.py utilization --billable-hours 1500 --available-hours 2000 \\
      --delegable-nonbillable 300 --attorney-nonbillable 200

  # Three-way trust reconciliation: bank $52,300, book $52,300, client ledgers
  # sum to $52,000 (a $300 gap -> FAIL -> route to the attorney)
  python3 legal_calc.py trust-recon --bank 52300 --book 52300 --ledgers-sum 52000
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '30%' or '0.30' into a fraction (0.30)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '30%' or '0.30', got {s!r}")


def cmd_realization(args: argparse.Namespace) -> int:
    if args.hours_worked <= 0:
        print("error: --hours-worked must be > 0", file=sys.stderr)
        return 2
    if args.available_hours <= 0:
        print("error: --available-hours must be > 0", file=sys.stderr)
        return 2
    if args.standard_rate <= 0:
        print("error: --standard-rate must be > 0", file=sys.stderr)
        return 2

    standard_value = args.hours_worked * args.standard_rate
    if args.billed > standard_value:
        print("warning: --billed exceeds standard value (hours-worked x standard-rate)",
              file=sys.stderr)
    if args.collected > args.billed:
        print("warning: --collected exceeds --billed", file=sys.stderr)

    utilization = args.hours_worked / args.available_hours
    realization = args.billed / standard_value if standard_value else 0.0
    collection = args.collected / args.billed if args.billed else 0.0
    net_effect = utilization * realization * collection
    effective_rate = args.collected / args.hours_worked

    print("Realization cascade + effective hourly rate")
    print(f"  hours worked            : {args.hours_worked:,.1f}")
    print(f"  available hours         : {args.available_hours:,.1f}")
    print(f"  standard rate           : {args.standard_rate:,.2f}/hr")
    print(f"  standard value          : {standard_value:,.0f} (worked x rate)")
    print(f"  billed value            : {args.billed:,.0f} (after write-downs)")
    print(f"  collected value         : {args.collected:,.0f} (after write-offs)")
    print("  ----")
    print(f"  utilization             : {utilization * 100:.1f}%  (worked / available)")
    print(f"  realization             : {realization * 100:.1f}%  (billed / standard)")
    print(f"  collection              : {collection * 100:.1f}%  (collected / billed)")
    print(f"  net effect (compounded) : {net_effect * 100:.1f}%  (util x real x coll)")
    print(f"  -> EFFECTIVE hourly rate: {effective_rate:,.2f}/hr  (collected / worked)")
    print()
    print("  read: a low REALIZATION is usually a write-down (billing-narrative /")
    print("        scope) problem, not the standard rate; a low COLLECTION is an A/R /")
    print("        engagement-terms problem. Build the waterfall before changing rates.")
    print("        Benchmarks (Clio 2025, [verify-at-use]): util ~38% / real ~88% /")
    print("        coll ~93%. Calibrate to the firm's own numbers (CLAUDE.md SS3 #1).")
    return 0


def cmd_matter_profit(args: argparse.Namespace) -> int:
    if args.collected < 0 or args.comp < 0:
        print("error: --collected and --comp must be >= 0", file=sys.stderr)
        return 2
    if not 0.0 <= args.overhead_rate < 1.0:
        print("error: --overhead-rate must be in [0%, 100%)", file=sys.stderr)
        return 2

    overhead = args.collected * args.overhead_rate
    fully_loaded_cost = args.comp + overhead
    profit = args.collected - fully_loaded_cost
    margin = (profit / args.collected * 100.0) if args.collected else 0.0
    threshold = args.comp * 3.0
    clears = args.collected >= threshold

    print("Matter / attorney profitability vs the Rule of Thirds")
    print(f"  collected revenue       : {args.collected:,.0f}")
    print(f"  compensation (loaded)   : {args.comp:,.0f}")
    print(f"  overhead                : {overhead:,.0f}  ({args.overhead_rate * 100:g}% of collected)")
    print(f"  fully-loaded cost       : {fully_loaded_cost:,.0f}  (comp + overhead)")
    print(f"  -> PROFIT               : {profit:,.0f}  ({margin:.1f}% margin)")
    print()
    print(f"  Rule-of-Thirds threshold: {threshold:,.0f}  (>= 3x compensation)")
    verdict = "CLEARS" if clears else "BELOW"
    print(f"  -> collected vs 3x comp : {verdict} the threshold")
    print()
    print("  read: the Rule of Thirds is a GUIDELINE, not a commandment - overhead")
    print("        commonly runs 45-50% in practice, so the 1/3-profit target is")
    print("        aspirational. Intentional deviations are fine; accidental ones are")
    print("        the warning. [verify-at-use] against the firm's actuals (CLAUDE.md SS3 #8).")
    return 0


def cmd_utilization(args: argparse.Namespace) -> int:
    if args.available_hours <= 0:
        print("error: --available-hours must be > 0", file=sys.stderr)
        return 2
    if args.billable_hours < 0:
        print("error: --billable-hours must be >= 0", file=sys.stderr)
        return 2

    utilization = args.billable_hours / args.available_hours
    nonbillable_total = args.delegable_nonbillable + args.attorney_nonbillable
    delegable_share = (
        args.delegable_nonbillable / nonbillable_total if nonbillable_total else 0.0
    )

    print("Utilization + non-billable load split")
    print(f"  billable hours          : {args.billable_hours:,.1f}")
    print(f"  available hours         : {args.available_hours:,.1f}")
    print(f"  -> UTILIZATION          : {utilization * 100:.1f}%  (billable / available)")
    print("  ----")
    print(f"  delegable non-billable  : {args.delegable_nonbillable:,.1f} hrs (admin a paralegal could do)")
    print(f"  attorney-only non-bill. : {args.attorney_nonbillable:,.1f} hrs (BD, firm mgmt)")
    print(f"  non-billable total      : {nonbillable_total:,.1f} hrs")
    if nonbillable_total:
        print(f"  -> DELEGABLE share      : {delegable_share * 100:.1f}% of non-billable load")
        recoverable = args.delegable_nonbillable
        print(f"  -> recoverable capacity : ~{recoverable:,.1f} attorney hrs if delegated")
    print()
    print("  read: low utilization + a high DELEGABLE share = a delegation/workflow")
    print("        problem, not a lawyer shortage. Rule out the cheap levers (delegate")
    print("        admin, fix intake/billing workflow) before hiring an attorney.")
    print("        Benchmark (Clio 2025, [verify-at-use]): avg utilization ~38%.")
    return 0


def cmd_trust_recon(args: argparse.Namespace) -> int:
    bank = args.bank
    book = args.book
    ledgers = args.ledgers_sum
    tol = args.tolerance

    bank_book = round(bank - book, 2)
    book_ledgers = round(book - ledgers, 2)
    bank_ledgers = round(bank - ledgers, 2)
    passes = (
        abs(bank_book) <= tol
        and abs(book_ledgers) <= tol
        and abs(bank_ledgers) <= tol
    )

    print("Three-way trust / IOLTA reconciliation check")
    print(f"  adjusted bank statement : {bank:,.2f}")
    print(f"  trust book balance      : {book:,.2f}")
    print(f"  sum of client ledgers   : {ledgers:,.2f}")
    print(f"  tolerance               : {tol:,.2f}")
    print("  ----")
    print(f"  bank  - book   diff     : {bank_book:,.2f}")
    print(f"  book  - ledgers diff    : {book_ledgers:,.2f}")
    print(f"  bank  - ledgers diff    : {bank_ledgers:,.2f}")
    print()
    if passes:
        print("  -> RECONCILED: all three figures agree within tolerance.")
        print("     This is the control that proves no client's funds were used for")
        print("     another's. Keep it monthly, with a named owner and a calendared date.")
    else:
        print("  -> FAIL: the three figures DO NOT agree.")
        print("     This is an arithmetic flag, NOT a finding of misconduct. STOP and")
        print("     route to the responsible attorney + the applicable state bar rules.")
        print("     A two-way (bank vs book) reconcile that 'balances' can still hide a")
        print("     client-ledger gap - the third leg is the one that matters.")
    print()
    print("  note: trust/IOLTA rules are STATE-SPECIFIC and volatile (the ABA Model")
    print("        Rule 1.15 floor is a 5-yr retention; several states require a 30-day")
    print("        cadence + mandatory three-way by 2026). [verify-at-use]. Ethics calls")
    print("        route to the attorney - this tool gives no legal advice (CLAUDE.md SS2, SS3 #6).")
    return 0 if passes else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="legal_calc.py",
        description="Small-firm legal-practice decision calculator (stdlib only). "
        "Decision-support, NOT legal/ethics/financial advice - validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    rea = sub.add_parser("realization", help="Realization cascade + effective hourly rate")
    rea.add_argument("--hours-worked", type=float, required=True,
                     help="hours actually worked on billable matters")
    rea.add_argument("--standard-rate", type=float, required=True,
                     help="standard billing rate per hour")
    rea.add_argument("--available-hours", type=float, required=True,
                     help="available working hours in the window (utilization denominator)")
    rea.add_argument("--billed", type=float, required=True,
                     help="value actually billed after pre-bill write-downs")
    rea.add_argument("--collected", type=float, required=True,
                     help="value actually collected after write-offs/discounts")
    rea.set_defaults(func=cmd_realization)

    mp = sub.add_parser("matter-profit", help="Matter/attorney profitability vs Rule of Thirds")
    mp.add_argument("--collected", type=float, required=True,
                    help="collected revenue for the matter / attorney")
    mp.add_argument("--comp", type=float, required=True,
                    help="fully-loaded compensation (salary + benefits + payroll tax)")
    mp.add_argument("--overhead-rate", type=_parse_rate, default=0.33,
                    help="overhead as a fraction of collected revenue (default 33%%)")
    mp.set_defaults(func=cmd_matter_profit)

    ut = sub.add_parser("utilization", help="Utilization ratio + non-billable load split")
    ut.add_argument("--billable-hours", type=float, required=True,
                    help="billable hours in the window")
    ut.add_argument("--available-hours", type=float, required=True,
                    help="available working hours in the window")
    ut.add_argument("--delegable-nonbillable", type=float, default=0.0,
                    help="non-billable hours a paralegal/assistant could do")
    ut.add_argument("--attorney-nonbillable", type=float, default=0.0,
                    help="attorney-only non-billable hours (BD, firm management)")
    ut.set_defaults(func=cmd_utilization)

    tr = sub.add_parser("trust-recon", help="Three-way trust/IOLTA reconciliation check")
    tr.add_argument("--bank", type=float, required=True,
                    help="adjusted bank statement balance")
    tr.add_argument("--book", type=float, required=True,
                    help="trust account book/checkbook balance")
    tr.add_argument("--ledgers-sum", type=float, required=True,
                    help="sum of all individual client ledger balances")
    tr.add_argument("--tolerance", type=float, default=0.0,
                    help="acceptable rounding tolerance (default 0.00 - trust must be exact)")
    tr.set_defaults(func=cmd_trust_recon)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
