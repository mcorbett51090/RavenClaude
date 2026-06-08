#!/usr/bin/env python3
"""Construction field-management calculator — pay apps, change orders, earned value.

Stdlib-only, argparse-driven. Three subcommands the cost-and-change-controls-lead
reaches for when checking a draw, a running contract sum, or schedule/cost performance:

  payapp       SOV %-complete -> work-completed, retainage, current payment due
               (AIA G702/G703 style: this-period billing net of retainage).
  changeorder  Original contract sum + a list of executed change orders ->
               the running adjusted contract sum (and net change).
  earned-value BCWP/ACWP/BCWS -> CV, SV, CPI, SPI, and a plain-language read.

Every dollar output is rounded to cents; ratios to three decimals. Nothing here
replaces the contract: retainage %, the change clause, and the SOV come from the
specific prime contract — verify before quoting a number to an owner.

Examples:
  construction_calc.py payapp --scheduled-value 1000000 --percent-complete 35 \\
      --stored-materials 20000 --retainage-pct 10 --previously-billed 280000
  construction_calc.py changeorder --original 1000000 --co 25000 --co -8000 --co 12000
  construction_calc.py earned-value --bcwp 320000 --acwp 350000 --bcws 300000
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence


def _money(value: float) -> float:
    """Round to cents."""
    return round(value + 0.0, 2)


def _ratio(value: float) -> float:
    """Round a performance ratio to three decimals."""
    return round(value + 0.0, 3)


def cmd_payapp(args: argparse.Namespace) -> int:
    """AIA G702/G703-style draw: work completed, retainage, current payment due."""
    if not 0.0 <= args.percent_complete <= 100.0:
        print("error: --percent-complete must be between 0 and 100", file=sys.stderr)
        return 2
    if not 0.0 <= args.retainage_pct <= 100.0:
        print("error: --retainage-pct must be between 0 and 100", file=sys.stderr)
        return 2

    work_completed = args.scheduled_value * (args.percent_complete / 100.0)
    completed_and_stored = work_completed + args.stored_materials
    retainage = completed_and_stored * (args.retainage_pct / 100.0)
    earned_less_retainage = completed_and_stored - retainage
    current_due = earned_less_retainage - args.previously_billed
    balance_to_finish = args.scheduled_value - work_completed

    print("Pay application (AIA G702/G703 style)")
    print(f"  Scheduled value (SOV total):      {_money(args.scheduled_value):>14,.2f}")
    print(f"  Percent complete:                 {args.percent_complete:>13.2f}%")
    print(f"  Work completed this date:         {_money(work_completed):>14,.2f}")
    print(f"  Stored materials:                 {_money(args.stored_materials):>14,.2f}")
    print(f"  Total completed + stored (G):     {_money(completed_and_stored):>14,.2f}")
    print(f"  Retainage @ {args.retainage_pct:.2f}%:                {_money(retainage):>14,.2f}")
    print(f"  Earned less retainage:            {_money(earned_less_retainage):>14,.2f}")
    print(f"  Less previous certificates:       {_money(args.previously_billed):>14,.2f}")
    print(f"  CURRENT PAYMENT DUE:              {_money(current_due):>14,.2f}")
    print(f"  Balance to finish (incl. ret.):   {_money(balance_to_finish + retainage):>14,.2f}")

    if current_due < 0:
        print(
            "  note: current payment due is negative — previously billed exceeds "
            "earned-less-retainage; check the SOV % or prior draws.",
            file=sys.stderr,
        )
    return 0


def cmd_changeorder(args: argparse.Namespace) -> int:
    """Running adjusted contract sum after a list of executed change orders."""
    cos = list(args.co)
    net_change = sum(cos)
    adjusted = args.original + net_change

    print("Change-order running total")
    print(f"  Original contract sum:            {_money(args.original):>14,.2f}")
    running = args.original
    for idx, co in enumerate(cos, start=1):
        running += co
        sign = "+" if co >= 0 else "-"
        print(
            f"  CO #{idx:<2} {sign}{abs(_money(co)):>12,.2f}"
            f"   -> running sum {_money(running):>14,.2f}"
        )
    print(f"  Net change ({len(cos)} CO(s)):              {_money(net_change):>14,.2f}")
    print(f"  ADJUSTED CONTRACT SUM:            {_money(adjusted):>14,.2f}")
    if args.original:
        pct = (net_change / args.original) * 100.0
        print(f"  Net change as % of original:      {pct:>13.2f}%")
    return 0


def cmd_earned_value(args: argparse.Namespace) -> int:
    """CV / SV / CPI / SPI from BCWP (EV), ACWP (AC), BCWS (PV)."""
    bcwp, acwp, bcws = args.bcwp, args.acwp, args.bcws
    cost_variance = bcwp - acwp
    schedule_variance = bcwp - bcws

    print("Earned-value performance")
    print(f"  BCWP / earned value (EV):         {_money(bcwp):>14,.2f}")
    print(f"  ACWP / actual cost (AC):          {_money(acwp):>14,.2f}")
    print(f"  BCWS / planned value (PV):        {_money(bcws):>14,.2f}")
    print(f"  Cost variance (CV = EV - AC):     {_money(cost_variance):>14,.2f}")
    print(f"  Schedule variance (SV = EV - PV): {_money(schedule_variance):>14,.2f}")

    if acwp:
        cpi = _ratio(bcwp / acwp)
        print(f"  CPI (EV / AC):                    {cpi:>14.3f}")
        cost_read = "on budget" if cpi == 1.0 else ("under budget" if cpi > 1.0 else "over budget")
        print(f"    -> cost: {cost_read} (CPI {'>' if cpi > 1 else '<' if cpi < 1 else '='} 1.0)")
    else:
        print("  CPI: n/a (ACWP is 0)")

    if bcws:
        spi = _ratio(bcwp / bcws)
        print(f"  SPI (EV / PV):                    {spi:>14.3f}")
        sched_read = (
            "on schedule" if spi == 1.0 else ("ahead of schedule" if spi > 1.0 else "behind schedule")
        )
        print(f"    -> schedule: {sched_read} (SPI {'>' if spi > 1 else '<' if spi < 1 else '='} 1.0)")
    else:
        print("  SPI: n/a (BCWS is 0)")

    if args.bac is not None and acwp:
        eac = args.bac / (bcwp / acwp) if bcwp else float("inf")
        print(f"  BAC (budget at completion):       {_money(args.bac):>14,.2f}")
        if eac != float("inf"):
            print(f"  EAC (BAC / CPI):                  {_money(eac):>14,.2f}")
            print(f"  VAC (BAC - EAC):                  {_money(args.bac - eac):>14,.2f}")
        else:
            print("  EAC: n/a (EV is 0)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="construction_calc.py",
        description="Construction field-management calculator: pay apps, change orders, earned value.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_pay = sub.add_parser(
        "payapp",
        help="SOV %-complete -> work completed, retainage, current payment due (AIA G702/G703).",
    )
    p_pay.add_argument("--scheduled-value", type=float, required=True, help="SOV total (contract sum).")
    p_pay.add_argument(
        "--percent-complete", type=float, required=True, help="Percent of scheduled value complete (0-100)."
    )
    p_pay.add_argument("--stored-materials", type=float, default=0.0, help="Materials stored but not installed.")
    p_pay.add_argument("--retainage-pct", type=float, default=10.0, help="Retainage withheld %% (default 10).")
    p_pay.add_argument(
        "--previously-billed", type=float, default=0.0, help="Sum of prior certificates (less retainage)."
    )
    p_pay.set_defaults(func=cmd_payapp)

    p_co = sub.add_parser("changeorder", help="Original contract sum + executed COs -> adjusted contract sum.")
    p_co.add_argument("--original", type=float, required=True, help="Original contract sum.")
    p_co.add_argument(
        "--co",
        type=float,
        action="append",
        default=[],
        metavar="AMOUNT",
        help="An executed change order amount (negative for a credit). Repeatable.",
    )
    p_co.set_defaults(func=cmd_changeorder)

    p_ev = sub.add_parser("earned-value", help="BCWP/ACWP/BCWS -> CV, SV, CPI, SPI (+ optional EAC/VAC).")
    p_ev.add_argument("--bcwp", type=float, required=True, help="Budgeted cost of work performed (earned value).")
    p_ev.add_argument("--acwp", type=float, required=True, help="Actual cost of work performed (actual cost).")
    p_ev.add_argument("--bcws", type=float, required=True, help="Budgeted cost of work scheduled (planned value).")
    p_ev.add_argument("--bac", type=float, default=None, help="Budget at completion (optional, enables EAC/VAC).")
    p_ev.set_defaults(func=cmd_earned_value)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
