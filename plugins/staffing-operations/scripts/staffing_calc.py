#!/usr/bin/env python3
"""staffing_calc.py — a zero-dependency staffing-operations decision calculator.

Removes arithmetic error from three recurring staffing-analytics decisions a
consultant runs constantly. The plugin already ships a static BI scorecard
(bi-report/data.json + report.html); this is the complementary *parametric*
calculator — you supply the inputs, it does the decomposition the scorecard
only displays.

  margin       The bill - pay - BURDEN spread decomposition (CLAUDE.md §3 #3).
               Itemize the burden stack, print gross margin and markup, and
               name the SINGLE burden line driving the spread so a margin slide
               isn't misdiagnosed as a pricing problem. Pairs with
               knowledge/healthcare-staffing-economics.md §1 and the
               "Margin / spread is compressing" decision tree.

  fill-rate    The fill-rate DENOMINATOR comparison (CLAUDE.md §3 #1, §3 #6).
               Most "fill rate fell" findings are a denominator shift, not a
               sourcing change. Computes fill on orders-received vs. workable
               and shows the gap, so a dead/on-hold order pileup can't hide as
               a fill problem. Pairs with knowledge/staffing-kpi-glossary.md §A.1.

  funnel-leak  The worst-converting STAGE in the recruiting funnel. Multiplies
               the stage conversion rates to an end-to-end yield, prints the
               cumulative survival at each stage, and flags the single weakest
               link to fix first (incl. the accept->start credentialing stage,
               §3 #7). Pairs with knowledge/staffing-decision-trees.md
               "Fill rate has declined".

This is a CALCULATOR, not a data source — it does not fetch benchmarks, rates,
or live client data. The user supplies every input; the tool does the arithmetic
and shows the formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not legal, immigration, medical-licensure,
tax, or financial advice (see ../CLAUDE.md §2). Validate every figure against the
client's actual de-identified ATS/VMS data before any deliverable (CLAUDE.md §3 #1,
§3 #9). No candidate/client PII goes in or out of this tool (§3 #10).

Examples
--------
  # Margin: $90.50 bill, $56 pay, with a travel burden stack
  python3 staffing_calc.py margin --bill 90.50 --pay 56 \\
      --burden payroll_taxes=4.5 --burden housing_stipend=6.8 \\
      --burden workers_comp=1.3 --burden credentialing=1.1 --burden benefits=1.9

  # Fill rate: 140 filled, 200 received, but only 165 were workable
  python3 staffing_calc.py fill-rate --filled 140 --received 200 --workable 165

  # Funnel leak: localize the worst stage across six conversion rates
  python3 staffing_calc.py funnel-leak \\
      --stage order_to_workable=0.82 --stage workable_to_submittal=0.61 \\
      --stage submittal_to_interview=0.34 --stage interview_to_offer=0.52 \\
      --stage offer_to_accept=0.74 --stage accept_to_start=0.91
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


def _parse_kv_amount(s: str) -> tuple[str, float]:
    """Parse a 'label=amount' pair (e.g. 'housing_stipend=6.8')."""
    if "=" not in s:
        raise argparse.ArgumentTypeError(f"must be label=amount, got {s!r}")
    label, _, val = s.partition("=")
    label = label.strip()
    if not label:
        raise argparse.ArgumentTypeError(f"empty label in {s!r}")
    try:
        return label, float(val)
    except ValueError:
        raise argparse.ArgumentTypeError(f"amount must be a number in {s!r}")


def _parse_kv_rate(s: str) -> tuple[str, float]:
    """Parse a 'label=rate' pair where rate is '0.61' or '61%'."""
    if "=" not in s:
        raise argparse.ArgumentTypeError(f"must be label=rate, got {s!r}")
    label, _, val = s.partition("=")
    label = label.strip()
    if not label:
        raise argparse.ArgumentTypeError(f"empty label in {s!r}")
    return label, _parse_rate(val)


def cmd_margin(args: argparse.Namespace) -> int:
    if args.bill <= 0:
        print("error: --bill must be > 0", file=sys.stderr)
        return 2
    if args.pay <= 0:
        print("error: --pay must be > 0", file=sys.stderr)
        return 2
    # Aggregate (don't overwrite) duplicate --burden labels — dict() would keep
    # only the last value per key and silently drop the earlier amount.
    burden_lines: dict[str, float] = {}
    for label, amt in args.burden or []:
        burden_lines[label] = burden_lines.get(label, 0.0) + amt
    burden_total = sum(burden_lines.values())
    cost = args.pay + burden_total
    margin = args.bill - cost
    margin_pct = margin / args.bill * 100.0
    markup_pct = ((args.bill / args.pay - 1.0) * 100.0) if args.pay else float("nan")

    print("Bill - pay - burden margin decomposition")
    print(f"  bill rate        : {args.bill:>10,.2f}")
    print(f"  pay rate         : {args.pay:>10,.2f}")
    print(f"  burden total     : {burden_total:>10,.2f}")
    if burden_lines:
        print("  burden stack:")
        for label, amt in sorted(burden_lines.items(), key=lambda kv: -kv[1]):
            share = amt / burden_total * 100.0 if burden_total else 0.0
            print(f"    {label:<26}: {amt:>8,.2f}  ({share:>4.0f}% of burden)")
    print(f"  total cost       : {cost:>10,.2f}  (pay + burden)")
    print(f"  → spread/margin  : {margin:>10,.2f}")
    print(f"  → gross margin   : {margin_pct:>9.1f}%  ((bill - pay - burden) / bill)")
    if args.pay:
        print(f"  → markup         : {markup_pct:>9.1f}%  (bill / pay - 1)")

    if burden_lines:
        top_label, top_amt = max(burden_lines.items(), key=lambda kv: kv[1])
        print()
        print(
            f"  largest burden line: {top_label} ({top_amt:,.2f}, "
            f"{top_amt / burden_total * 100:.0f}% of burden)"
        )
        print("  → before calling a margin slide a PRICING problem, confirm this line")
        print("    didn't move (§3 #3). In travel, housing/stipend is the usual culprit;")
        print("    in locums, malpractice; idle/bench time is the redeployment lever.")
    if margin < 0:
        print("  WARNING: spread is NEGATIVE — this placement loses money at these inputs.")
    return 0


def cmd_fill_rate(args: argparse.Namespace) -> int:
    if args.received <= 0:
        print("error: --received must be > 0", file=sys.stderr)
        return 2
    if args.workable is not None and args.workable <= 0:
        print("error: --workable must be > 0", file=sys.stderr)
        return 2
    if args.filled < 0:
        print("error: --filled must be >= 0", file=sys.stderr)
        return 2

    on_received = args.filled / args.received
    print("Fill-rate denominator comparison")
    print(f"  orders filled        : {args.filled:>8,.0f}")
    print(f"  orders received      : {args.received:>8,.0f}")
    print(f"  → fill (÷ received)  : {on_received * 100:>7.1f}%")

    if args.workable is not None:
        if args.workable > args.received:
            print("  note: --workable exceeds --received; check your inputs.")
        on_workable = args.filled / args.workable
        dead = args.received - args.workable
        dead_pct = dead / args.received * 100.0 if args.received else 0.0
        print(
            f"  orders workable      : {args.workable:>8,.0f}  "
            f"({dead:,.0f} dead/on-hold/uncompetitive = {dead_pct:.0f}% of received)"
        )
        print(f"  → fill (÷ workable)  : {on_workable * 100:>7.1f}%")
        gap = (on_workable - on_received) * 100.0
        print(f"  → denominator gap    : {gap:>7.1f} pts (workable-base fill is higher)")
        print()
        print("  → If 'fill fell' but the workable-base fill held, the move is a")
        print("    DENOMINATOR shift (dead/on-hold orders inflating the received base),")
        print("    NOT a sourcing failure (§3 #1, §3 #6). Clean the denominator first;")
        print("    split aged/on-hold orders out before any capacity or recruiter read.")
    else:
        print()
        print("  Provide --workable to expose a denominator shift. Fill on orders-RECEIVED")
        print("  alone hides a dead-order pileup as a fill problem (§3 #6).")
    print("  Always pair fill rate with time-to-fill (§3 #2) — they are different diseases.")
    return 0


def cmd_funnel_leak(args: argparse.Namespace) -> int:
    stages = list(args.stage or [])
    if not stages:
        print("error: provide at least one --stage label=rate", file=sys.stderr)
        return 2
    for label, rate in stages:
        if not 0.0 <= rate <= 1.0:
            print(f"error: stage {label!r} rate must be in [0%, 100%], got {rate}", file=sys.stderr)
            return 2

    print("Recruiting-funnel leak localization")
    print("  stage                        | conv rate | cumulative survival")
    print("  -----------------------------+-----------+--------------------")
    cumulative = 1.0
    worst = None  # (label, rate)
    for label, rate in stages:
        cumulative *= rate
        if worst is None or rate < worst[1]:
            worst = (label, rate)
        print(f"  {label:<28} | {rate * 100:>7.1f}%  | {cumulative * 100:>7.2f}%")

    print()
    print(f"  → end-to-end yield   : {cumulative * 100:.2f}%  (product of all stage rates)")
    print(f"  → worst-converting   : {worst[0]} at {worst[1] * 100:.1f}%")
    print("  → Fix the weakest link FIRST — it caps the whole funnel. A 1-pt gain at")
    print("    the worst stage beats a 1-pt gain anywhere else. If the worst stage is")
    print("    accept→start, that's the CREDENTIALING clock (§3 #7), not recruiting.")
    print("  reminder: localize the leak before adding headcount or blaming a recruiter")
    print("            (§3 #4) — diagnose supply vs. order-quality vs. speed (§3 #6).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="staffing_calc.py",
        description="Staffing-operations decision calculator (stdlib only). "
        "Decision-support, not legal/tax/medical/financial advice — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    mar = sub.add_parser("margin", help="Bill - pay - burden spread decomposition")
    mar.add_argument("--bill", type=float, required=True, help="hourly bill rate to the client")
    mar.add_argument("--pay", type=float, required=True, help="hourly pay rate to the worker")
    mar.add_argument(
        "--burden",
        type=_parse_kv_amount,
        action="append",
        metavar="LABEL=AMT",
        help="a burden line, e.g. housing_stipend=6.8 (repeatable)",
    )
    mar.set_defaults(func=cmd_margin)

    fr = sub.add_parser("fill-rate", help="Fill-rate denominator comparison")
    fr.add_argument("--filled", type=float, required=True, help="orders filled in the period")
    fr.add_argument("--received", type=float, required=True, help="orders received in the period")
    fr.add_argument(
        "--workable",
        type=float,
        default=None,
        help="workable orders (excludes dead/on-hold/uncompetitive); optional",
    )
    fr.set_defaults(func=cmd_fill_rate)

    fl = sub.add_parser("funnel-leak", help="Localize the worst-converting funnel stage")
    fl.add_argument(
        "--stage",
        type=_parse_kv_rate,
        action="append",
        metavar="LABEL=RATE",
        help="a stage conversion rate, e.g. submittal_to_interview=0.34 (repeatable)",
    )
    fl.set_defaults(func=cmd_funnel_leak)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
