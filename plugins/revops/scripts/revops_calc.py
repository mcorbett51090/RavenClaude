#!/usr/bin/env python3
"""revops_calc.py — a zero-dependency revenue-operations decision calculator.

Removes arithmetic error from three recurring RevOps decisions a revops-architect
/ pipeline-and-forecast-analyst / gtm-systems-engineer runs constantly:

  forecast        Roll up a weighted-by-stage forecast from a set of stages
                  (each with its open pipeline value AND its OWN historical
                  stage->close rate), report it beside the rep COMMIT roll-up,
                  and name the gap. Then derive the coverage target from the
                  blended win-rate (gap-to-target / win-rate, never a folk 3x)
                  and compare it to the coverage the inspected pipeline actually
                  provides. Pairs with knowledge/revops-decision-trees.md and
                  the forecast-is-a-methodology / coverage-is-derived-from-win-
                  rate best practices.

  funnel          Stage-to-stage conversion down a funnel (volumes entering each
                  stage), plus win-rate and the sales-velocity equation
                  ((open opps x win-rate x avg deal size) / cycle length). Prints
                  each stage's step conversion AND the cumulative top-to-bottom
                  conversion, so you can see which step leaks. Pairs with
                  knowledge/revops-decision-trees.md and one-funnel-one-
                  definition / stage-is-exit-criteria-not-vibes.

  quota-capacity  Bottoms-up capacity = (fully-ramped reps + ramping reps x ramp
                  fraction) x productivity-per-rep, reconciled against the board
                  target. Prints capacity, the surplus/gap, and whether the
                  quota is makeable from the heads you actually have. Pairs with
                  quota-is-bottoms-up-from-capacity and the quota-reconciles-to-
                  capacity tree.

This is a CALCULATOR, not a data source — it does not query a CRM, pull a
forecast tool, or read a warehouse. The user supplies every input; the tool does
the arithmetic and shows the formula. Stdlib only (argparse); runs anywhere
Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not a substitute for inspecting the
pipeline and back-testing the method against recent quarters (see ../CLAUDE.md
and the inspect-pipeline-before-the-math / forecast-is-a-methodology best
practices). Coverage on padded pipeline is precise nonsense; a stage rate the
tool accepts is still a hypothesis until it is back-tested against your own
historical stage->close conversion.

Examples
--------
  # Forecast: three stages (name:open_value:stage_close_rate), a rep commit of
  # 1,200,000, and a gap-to-target of 2,000,000.
  python3 revops_calc.py forecast \\
      --stage discovery:3000000:0.15 \\
      --stage proposal:1800000:0.35 \\
      --stage negotiation:900000:0.65 \\
      --commit 1200000 --gap-to-target 2000000

  # Funnel: volumes entering each stage (name:volume), an avg deal size, and a
  # cycle length in days. Win-rate is derived from the last->... unless given.
  python3 revops_calc.py funnel \\
      --stage lead:5000 --stage mql:1200 --stage sql:400 \\
      --stage opp:150 --stage won:30 \\
      --avg-deal-size 25000 --cycle-days 90

  # Quota-capacity: 8 fully-ramped reps + 4 ramping at 50% ramp, each carrying
  # 1,000,000 of productivity, against a 12,000,000 board target.
  python3 revops_calc.py quota-capacity \\
      --ramped-reps 8 --ramping-reps 4 --ramp-fraction 0.5 \\
      --productivity-per-rep 1000000 --board-target 12000000
"""

from __future__ import annotations

import argparse
import sys


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def _parse_rate(s: str) -> float:
    """Parse a rate like '35%' or '0.35' into a fraction (0.35)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"must be like '35%' or '0.35', got {s!r}"
        ) from None


def _parse_fc_stage(s: str) -> tuple:
    """Parse 'name:open_value:stage_close_rate' for the forecast roll-up."""
    parts = s.split(":")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(
            f"stage must be name:open_value:stage_close_rate, got {s!r}"
        )
    name = parts[0]
    try:
        value = float(parts[1])
        rate = _parse_rate(parts[2])
    except (ValueError, argparse.ArgumentTypeError):
        raise argparse.ArgumentTypeError(
            f"open_value must be a number and stage_close_rate a 0-1 rate in {s!r}"
        ) from None
    if value < 0:
        raise argparse.ArgumentTypeError(f"open_value must be >= 0 in {s!r}")
    if not 0.0 <= rate <= 1.0:
        raise argparse.ArgumentTypeError(
            f"stage_close_rate must be a 0-1 rate, got {rate} in {s!r}"
        )
    return (name, value, rate)


def _parse_vol_stage(s: str) -> tuple:
    """Parse 'name:volume' for the funnel conversion walk."""
    parts = s.split(":")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(f"stage must be name:volume, got {s!r}")
    name = parts[0]
    try:
        volume = float(parts[1])
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"volume must be a number in {s!r}"
        ) from None
    if volume < 0:
        raise argparse.ArgumentTypeError(f"volume must be >= 0 in {s!r}")
    return (name, volume)


def cmd_forecast(args: argparse.Namespace) -> int:
    stages = args.stage
    if len(stages) < 1:
        print("error: at least one --stage is required", file=sys.stderr)
        return 2
    if args.gap_to_target <= 0:
        print("error: --gap-to-target must be > 0", file=sys.stderr)
        return 2

    total_open = sum(v for _, v, _ in stages)
    if total_open <= 0:
        print("error: total open pipeline value is 0", file=sys.stderr)
        return 2

    print("Forecast — weighted-by-stage vs commit (name the bias, name the gap)")
    print("  stage            |  open value | stage rate | weighted")
    print("  -----------------+-------------+------------+------------")
    weighted = 0.0
    for name, value, rate in stages:
        contribution = value * rate
        weighted += contribution
        print(
            f"  {name[:16]:<16} | {value:>11,.0f} | {_pct(rate):>10} "
            f"| {contribution:>10,.0f}"
        )
    # Blended win-rate the weighted forecast implies across the open pipeline.
    blended_wr = weighted / total_open
    print()
    print(f"  → weighted-by-stage forecast : {weighted:,.0f}")
    print(f"  → blended win-rate (weighted/open) : {_pct(blended_wr)}")
    if args.commit is not None:
        gap = args.commit - weighted
        print(f"  → rep commit roll-up         : {args.commit:,.0f}")
        print(f"  → commit - weighted gap      : {gap:,.0f}")
        if gap > 0:
            print("    note: commit ABOVE weighted — possible happy-ears; ask which")
            print("          deals carry the optimism and what buyer action backs it.")
        elif gap < 0:
            print("    note: commit BELOW weighted — possible sandbagging; the")
            print("          weighted method may be over-counting early stages too.")

    # Coverage: derive the target from the blended win-rate, NOT a folk 3x.
    print()
    if blended_wr <= 0:
        print("  coverage: blended win-rate is 0 — cannot derive a target.")
        return 0
    required_cov = 1.0 / blended_wr
    have_cov = total_open / args.gap_to_target
    print("  Coverage — derived from win-rate, never a folk 3x")
    print(f"    gap-to-target                : {args.gap_to_target:,.0f}")
    print(f"    open pipeline (inspected?)   : {total_open:,.0f}")
    print(f"    → required coverage = 1 / win-rate : {required_cov:.2f}x")
    print(f"    → coverage you have = open / gap   : {have_cov:.2f}x")
    if have_cov + 1e-9 >= required_cov:
        print("    → coverage MET on this pipeline — now watch win-rate drift,")
        print("      not just the ratio. Confirm the pipeline was inspected first.")
    else:
        short = (required_cov - have_cov) * args.gap_to_target
        print(f"    → coverage GAP: short ~{short:,.0f} of pipeline at this win-rate.")
        print("      Drive build/velocity; name which lever moves the number.")
    print("  reminder: coverage on padded pipeline is precise nonsense — inspect")
    print("            for stuck/aged/past-close-date deals before trusting any of")
    print("            this. Back-test the weighted method against recent quarters.")
    return 0


def cmd_funnel(args: argparse.Namespace) -> int:
    stages = args.stage
    if len(stages) < 2:
        print("error: at least two --stage values are required", file=sys.stderr)
        return 2
    top_name, top_vol = stages[0]
    if top_vol <= 0:
        print("error: the top-of-funnel volume must be > 0", file=sys.stderr)
        return 2

    print("Funnel — stage conversion + win-rate + velocity")
    print("  step                       |   entered |  step conv | cumulative")
    print("  ---------------------------+-----------+------------+-----------")
    print(f"  {top_name[:26]:<26} | {top_vol:>9,.0f} | {'—':>10} | {'100.0%':>10}")
    prev_name, prev_vol = top_name, top_vol
    for name, vol in stages[1:]:
        step_conv = vol / prev_vol if prev_vol > 0 else 0.0
        cumulative = vol / top_vol if top_vol > 0 else 0.0
        label = f"{prev_name[:10]}->{name[:12]}"
        print(
            f"  {label[:26]:<26} | {vol:>9,.0f} | {_pct(step_conv):>10} "
            f"| {_pct(cumulative):>10}"
        )
        prev_name, prev_vol = name, vol

    # Win-rate: caller-supplied, else derived from the last two stages as a proxy
    # (won / the stage that feeds it — an opp->won proxy, not a true won/closed).
    bottom_name, bottom_vol = stages[-1]
    if args.win_rate is not None:
        win_rate = args.win_rate
        wr_src = "supplied"
    elif len(stages) >= 2 and stages[-2][1] > 0:
        win_rate = bottom_vol / stages[-2][1]
        wr_src = f"proxy: {bottom_name}/{stages[-2][0]}"
    else:
        win_rate = 0.0
        wr_src = "n/a"

    print()
    print(f"  → win-rate ({wr_src}) : {_pct(win_rate)}")
    if args.win_rate is None:
        print("    note: this is an opp->won PROXY, not won/(won+lost). Supply")
        print("          --win-rate from your own closed-opp history for the real one.")

    # Sales velocity = (open opps x win-rate x avg deal size) / cycle length.
    if args.avg_deal_size is not None and args.cycle_days is not None:
        if args.cycle_days <= 0:
            print("error: --cycle-days must be > 0", file=sys.stderr)
            return 2
        open_opps = args.open_opps if args.open_opps is not None else bottom_vol
        velocity = (open_opps * win_rate * args.avg_deal_size) / args.cycle_days
        print()
        print("  Sales velocity = (open opps x win-rate x avg deal) / cycle days")
        print(f"    open opps      : {open_opps:,.0f}"
              f"{' (defaulted to bottom-stage volume)' if args.open_opps is None else ''}")
        print(f"    avg deal size  : {args.avg_deal_size:,.0f}")
        print(f"    cycle length   : {args.cycle_days:g} days")
        print(f"    → velocity     : {velocity:,.0f} of new revenue per day")
        print("    velocity isolates which input a change moves — use it to tell a")
        print("    real lever from a vanity initiative.")
    print("  reminder: one funnel, one definition — every stage means one thing")
    print("            org-wide, instrumented once. A leaky step is a definition or")
    print("            an exit-criteria problem before it is a volume problem.")
    return 0


def cmd_quota_capacity(args: argparse.Namespace) -> int:
    if args.ramped_reps < 0 or args.ramping_reps < 0:
        print("error: rep counts must be >= 0", file=sys.stderr)
        return 2
    if not 0.0 <= args.ramp_fraction <= 1.0:
        print("error: --ramp-fraction must be a 0-1 fraction", file=sys.stderr)
        return 2
    if args.productivity_per_rep <= 0:
        print("error: --productivity-per-rep must be > 0", file=sys.stderr)
        return 2
    if args.board_target <= 0:
        print("error: --board-target must be > 0", file=sys.stderr)
        return 2

    # Effective heads = fully-ramped + ramping discounted by their ramp fraction.
    effective_heads = args.ramped_reps + args.ramping_reps * args.ramp_fraction
    capacity = effective_heads * args.productivity_per_rep
    delta = capacity - args.board_target
    cov = capacity / args.board_target

    print("Quota vs capacity — bottoms-up, never top-down from the board number")
    print(f"  fully-ramped reps            : {args.ramped_reps:g}")
    print(f"  ramping reps                 : {args.ramping_reps:g} "
          f"@ {_pct(args.ramp_fraction)} ramp")
    print(f"  → effective heads            : {effective_heads:.2f}")
    print(f"  productivity per rep         : {args.productivity_per_rep:,.0f}")
    print()
    print(f"  → bottoms-up capacity        : {capacity:,.0f}")
    print(f"  → board target               : {args.board_target:,.0f}")
    print(f"  → capacity / target          : {cov:.2f}x")
    print()
    if delta >= 0:
        print(f"  → MAKEABLE — capacity exceeds target by {delta:,.0f}.")
        print("    Assign it; watch the ramp + productivity assumptions as reality")
        print("    lands. Surplus is headroom, not a reason to raise the number blind.")
    else:
        gap_heads = (-delta) / args.productivity_per_rep
        print(f"  → SHORT — board ask exceeds capacity by {-delta:,.0f}")
        print(f"    (~{gap_heads:.1f} more fully-ramped reps' worth at this productivity).")
        print("    The gap is a STAFFING / ramp / productivity decision — never a")
        print("    bigger number stapled onto the same heads. Name the lever:")
        print("    hire+ramp earlier, raise productivity (name the enablement), or")
        print("    flag the accepted gap explicitly. An un-makeable quota breaks comp")
        print("    behavior, not just the forecast.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="revops_calc.py",
        description="Revenue-operations decision calculator (stdlib only). "
        "Decision-support, not a substitute for pipeline inspection + a back-test "
        "— a stage rate it accepts is a hypothesis until back-tested.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    fc = sub.add_parser(
        "forecast",
        help="weighted-by-stage roll-up vs commit + win-rate-derived coverage",
    )
    fc.add_argument(
        "--stage", type=_parse_fc_stage, action="append", default=[],
        metavar="NAME:OPEN_VALUE:STAGE_CLOSE_RATE",
        help="a stage: open pipeline value + its OWN historical stage->close rate "
        "(repeatable)",
    )
    fc.add_argument("--commit", type=float, default=None,
                    help="the rep commit roll-up, to report beside weighted")
    fc.add_argument("--gap-to-target", type=float, required=True,
                    help="gap-to-target the pipeline must cover (for coverage)")
    fc.set_defaults(func=cmd_forecast)

    fn = sub.add_parser(
        "funnel",
        help="stage-to-stage conversion + win-rate + sales velocity",
    )
    fn.add_argument(
        "--stage", type=_parse_vol_stage, action="append", default=[],
        metavar="NAME:VOLUME",
        help="a funnel stage and the volume entering it, top to bottom (repeatable)",
    )
    fn.add_argument("--win-rate", type=_parse_rate, default=None,
                    help="won/(won+lost) win-rate; else an opp->won proxy is used")
    fn.add_argument("--avg-deal-size", type=float, default=None,
                    help="average deal size, to compute sales velocity")
    fn.add_argument("--cycle-days", type=float, default=None,
                    help="average sales-cycle length in days, for velocity")
    fn.add_argument("--open-opps", type=float, default=None,
                    help="open opportunities for velocity (default: bottom-stage volume)")
    fn.set_defaults(func=cmd_funnel)

    qc = sub.add_parser(
        "quota-capacity",
        help="bottoms-up capacity (reps x productivity x ramp) vs the board target",
    )
    qc.add_argument("--ramped-reps", type=float, required=True,
                    help="number of fully-ramped reps")
    qc.add_argument("--ramping-reps", type=float, default=0.0,
                    help="number of still-ramping reps")
    qc.add_argument("--ramp-fraction", type=_parse_rate, default=0.5,
                    help="0-1 fraction of full productivity a ramping rep carries")
    qc.add_argument("--productivity-per-rep", type=float, required=True,
                    help="expected productivity (bookings) per fully-ramped rep")
    qc.add_argument("--board-target", type=float, required=True,
                    help="the top-down board target to reconcile against")
    qc.set_defaults(func=cmd_quota_capacity)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
