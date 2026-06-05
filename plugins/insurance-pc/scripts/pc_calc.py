#!/usr/bin/env python3
"""pc_calc.py — a zero-dependency P&C underwriting decision calculator.

Removes arithmetic error from four recurring P&C portfolio decisions an
underwriter / actuary / claims leader / agency analyst runs constantly:

  combined-ratio  Decompose a combined ratio into loss + expense, and the loss
                  ratio into ATTRITIONAL vs CATASTROPHE. Prints the combined
                  ratio, the underwriting margin (100 - CR), and the cat load
                  in points, so a deteriorating result is diagnosed correctly
                  (loss vs expense; attritional vs cat) before any fix. Pairs
                  with knowledge/pc-decision-trees.md and the
                  decompose-the-combined-ratio skill.

  rate-indication The loss-ratio-method INDICATED RATE CHANGE:
                  (trended loss ratio / permissible loss ratio) - 1, where the
                  permissible loss ratio = 1 - (expense ratio + profit/contingency
                  load). Optionally credibility-weights the trended loss ratio
                  against the trended permissible loss ratio. Prints the
                  permissible loss ratio, the indicated change, and a plain-English
                  read. Pairs with the price-to-rate-adequacy skill. This is the
                  standard procedure for an overall rate-adequacy evaluation
                  (loss-ratio method; CAS Basic Ratemaking).

  loss-ratio      Split a loss-ratio MOVE into FREQUENCY and SEVERITY. Given a
                  base and current frequency (claims per exposure) and severity
                  (avg cost per claim), prints the pure-premium change and how
                  much of the loss-ratio move each driver explains, since they
                  have opposite responses (risk selection vs social inflation).
                  Pairs with the separate-frequency-from-severity skill.

  reserve-runoff  Read a one-year loss-RESERVE RUNOFF: ultimate(now) vs
                  ultimate(prior estimate). Prints the adverse / favorable
                  development in dollars and as a percent of the prior estimate,
                  and flags the direction. Adverse development on prior years is
                  where optimistic underwriting comes home (reserve adequacy is
                  the truth-teller). Pairs with knowledge/pc-reserving-and-
                  rate-indication-decision-trees.md.

This is a CALCULATOR, not a data source — it does not fetch benchmarks, loss
trends, or rate filings. The user supplies every input; the tool does the
arithmetic and shows the formula. Stdlib only (argparse); runs anywhere
Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not actuarial, legal, or filed-rate
advice (see ../CLAUDE.md §2). Pricing/reserving guidance is decision-support for
a credentialed actuary; validate every figure against the book's actual data
before any deliverable (CLAUDE.md §3 #8).

Examples
--------
  # Combined ratio: 62% attritional loss + 8 pts cat + 28% expense
  python3 pc_calc.py combined-ratio --attritional-loss 62% --cat-loss 8% \\
      --expense 28%

  # Rate indication: trended loss ratio 72%, expense ratio 26%, profit load 5%
  python3 pc_calc.py rate-indication --trended-loss-ratio 72% --expense 26% \\
      --profit 5%

  # ...with 60% credibility against the trended permissible loss ratio
  python3 pc_calc.py rate-indication --trended-loss-ratio 72% --expense 26% \\
      --profit 5% --credibility 60%

  # Loss-ratio move: frequency 5.0->5.4 per 100, severity 8000->9200
  python3 pc_calc.py loss-ratio --base-frequency 5.0 --cur-frequency 5.4 \\
      --base-severity 8000 --cur-severity 9200

  # Reserve runoff: prior ultimate 10.0M, re-estimated to 10.8M
  python3 pc_calc.py reserve-runoff --prior-ultimate 10000000 \\
      --current-ultimate 10800000
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '28%' or '0.28' into a fraction (0.28)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '28%' or '0.28', got {s!r}")


def cmd_combined_ratio(args: argparse.Namespace) -> int:
    if args.attritional_loss < 0 or args.cat_loss < 0 or args.expense < 0:
        print("error: ratios must be >= 0", file=sys.stderr)
        return 2

    loss_ratio = args.attritional_loss + args.cat_loss
    combined = loss_ratio + args.expense
    margin = 1.0 - combined

    print("Combined ratio — loss + expense, attritional + cat")
    print(f"  attritional loss ratio : {args.attritional_loss * 100:6.1f}")
    print(f"  catastrophe loss ratio : {args.cat_loss * 100:6.1f}  (cat load in points)")
    print(f"  total loss ratio       : {loss_ratio * 100:6.1f}")
    print(f"  expense ratio          : {args.expense * 100:6.1f}")
    print(f"  → COMBINED RATIO       : {combined * 100:6.1f}")

    if combined < 1.0:
        print(f"  → underwriting MARGIN  : {margin * 100:6.1f} pts profit (CR under 100)")
    elif combined > 1.0:
        print(f"  → underwriting LOSS    : {-margin * 100:6.1f} pts (CR over 100)")
    else:
        print("  → underwriting result  : break-even (CR = 100)")

    if loss_ratio > 0:
        cat_share = args.cat_loss / loss_ratio * 100.0
        print(f"  note: cat is {cat_share:.0f}% of the loss ratio — strip it to judge the")
        print("        attritional book (§3 #4). A clean attritional CR can still hide a")
        print("        line-of-business mix shift (§3 #6).")
    return 0


def cmd_rate_indication(args: argparse.Namespace) -> int:
    permissible = 1.0 - (args.expense + args.profit)
    if permissible <= 0:
        print("error: expense + profit load >= 100% — permissible loss ratio is non-positive",
              file=sys.stderr)
        return 2
    if not 0.0 <= args.credibility <= 1.0:
        print("error: --credibility must be in [0%, 100%]", file=sys.stderr)
        return 2

    print("Rate indication — loss-ratio method")
    print(f"  trended loss ratio     : {args.trended_loss_ratio * 100:6.1f}")
    print(f"  expense ratio          : {args.expense * 100:6.1f}")
    print(f"  profit/contingency load: {args.profit * 100:6.1f}")
    print(f"  → permissible loss ratio (1 - expense - profit): {permissible * 100:6.1f}")

    raw_indication = args.trended_loss_ratio / permissible - 1.0

    if args.credibility < 1.0:
        # Complement of credibility: the trended permissible loss ratio. With no
        # separate trended-permissible input, the permissible LR is the complement
        # anchor (a 0% indication), so the weighted indication scales by credibility.
        weighted_indication = raw_indication * args.credibility
        print(f"  credibility (Z)        : {args.credibility * 100:6.1f}")
        print(f"  → indicated change @ full credibility : {raw_indication * 100:+6.1f}%")
        print(f"  → CREDIBILITY-WEIGHTED indicated change: {weighted_indication * 100:+6.1f}%")
        print("    (complement = trended permissible loss ratio → a 0% indication anchor)")
        indication = weighted_indication
    else:
        print(f"  → INDICATED RATE CHANGE: {raw_indication * 100:+6.1f}%")
        indication = raw_indication

    if indication > 0.001:
        print(f"  read: the rate is INADEQUATE — indicated +{indication * 100:.1f}%. Price to the")
        print("        indication, not the competitor (§3 #2); matching a low rate grows a loss.")
    elif indication < -0.001:
        print(f"  read: the rate is REDUNDANT — indicated {indication * 100:.1f}%. Room to compete")
        print("        on price without growing into a loss.")
    else:
        print("  read: the rate is approximately ADEQUATE at the current level.")
    print("  note: the trend assumption drives the result — stress it (§3 #3). Decision-support")
    print("        for a credentialed actuary; not a filed rate (§2).")
    return 0


def cmd_loss_ratio(args: argparse.Namespace) -> int:
    if args.base_frequency <= 0 or args.base_severity <= 0:
        print("error: base frequency and severity must be > 0", file=sys.stderr)
        return 2
    if args.cur_frequency < 0 or args.cur_severity < 0:
        print("error: current frequency and severity must be >= 0", file=sys.stderr)
        return 2

    base_pp = args.base_frequency * args.base_severity
    cur_pp = args.cur_frequency * args.cur_severity
    freq_change = args.cur_frequency / args.base_frequency - 1.0
    sev_change = args.cur_severity / args.base_severity - 1.0
    pp_change = cur_pp / base_pp - 1.0

    print("Loss-ratio move — frequency vs severity decomposition")
    print(f"  frequency  : {args.base_frequency:g} → {args.cur_frequency:g}  ({freq_change * 100:+.1f}%)")
    print(f"  severity   : {args.base_severity:,.0f} → {args.cur_severity:,.0f}  ({sev_change * 100:+.1f}%)")
    print(f"  pure premium (freq × sev): {base_pp:,.0f} → {cur_pp:,.0f}  ({pp_change * 100:+.1f}%)")

    # Multiplicative decomposition of the pure-premium change into the two drivers.
    print(f"  → pure-premium change   : {pp_change * 100:+.1f}%  (this drives the loss ratio at flat rate)")
    print(f"     from frequency       : {freq_change * 100:+.1f}%")
    print(f"     from severity        : {sev_change * 100:+.1f}%")

    if abs(sev_change) > abs(freq_change):
        print("  read: SEVERITY-dominated — often social inflation / large-loss / litigation.")
        print("        A severity story is not fixed by tightening risk selection alone (§3 #3).")
    elif abs(freq_change) > abs(sev_change):
        print("  read: FREQUENCY-dominated — often risk selection / exposure / mix.")
        print("        A frequency story responds to underwriting selection (§3 #3).")
    else:
        print("  read: frequency and severity moved comparably — investigate both (§3 #3).")
    return 0


def cmd_reserve_runoff(args: argparse.Namespace) -> int:
    if args.prior_ultimate <= 0:
        print("error: --prior-ultimate must be > 0", file=sys.stderr)
        return 2

    development = args.current_ultimate - args.prior_ultimate
    pct = development / args.prior_ultimate * 100.0

    print("Reserve runoff — prior-year development")
    print(f"  prior ultimate estimate  : {args.prior_ultimate:,.0f}")
    print(f"  current ultimate estimate: {args.current_ultimate:,.0f}")
    print(f"  → development            : {development:+,.0f}  ({pct:+.1f}% of prior estimate)")

    if development > 0:
        print("  → ADVERSE development — reserves were deficient; the prior result was")
        print("    flattered. Adverse development is where optimistic underwriting comes")
        print("    home (§3 #5). Show prior-year development separately from the current")
        print("    accident year so the calendar-year combined ratio is honest.")
    elif development < 0:
        print("  → FAVORABLE development — reserves were redundant; releasing into income.")
        print("    Confirm it is genuine redundancy, not under-reserving the current year.")
    else:
        print("  → reserves ran off on estimate — no development this period.")
    print("  note: reserve adequacy is the truth-teller (§3 #5). Decision-support for a")
    print("        credentialed actuary; not an opinion on reserve sufficiency (§2).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pc_calc.py",
        description="P&C underwriting decision calculator (stdlib only). "
        "Decision-support, not actuarial/legal/filed-rate advice — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    cr = sub.add_parser("combined-ratio", help="Decompose the combined ratio (loss/expense, attritional/cat)")
    cr.add_argument("--attritional-loss", type=_parse_rate, required=True,
                    help="attritional (non-cat) loss ratio, e.g. 62%%")
    cr.add_argument("--cat-loss", type=_parse_rate, default=0.0,
                    help="catastrophe loss ratio (the cat load in points), e.g. 8%% (default 0)")
    cr.add_argument("--expense", type=_parse_rate, required=True,
                    help="expense ratio (acquisition + internal), e.g. 28%%")
    cr.set_defaults(func=cmd_combined_ratio)

    ri = sub.add_parser("rate-indication", help="Loss-ratio-method indicated rate change")
    ri.add_argument("--trended-loss-ratio", type=_parse_rate, required=True,
                    help="trended, developed loss ratio, e.g. 72%%")
    ri.add_argument("--expense", type=_parse_rate, required=True,
                    help="expense ratio (commission + general + other acq + taxes/fees), e.g. 26%%")
    ri.add_argument("--profit", type=_parse_rate, default=0.0,
                    help="profit + contingency load, e.g. 5%% (default 0)")
    ri.add_argument("--credibility", type=_parse_rate, default=1.0,
                    help="credibility Z of the trended loss ratio (default 100%% = full)")
    ri.set_defaults(func=cmd_rate_indication)

    lr = sub.add_parser("loss-ratio", help="Split a loss-ratio move into frequency and severity")
    lr.add_argument("--base-frequency", type=float, required=True,
                    help="base-period frequency (claims per exposure unit)")
    lr.add_argument("--cur-frequency", type=float, required=True,
                    help="current-period frequency (same exposure unit)")
    lr.add_argument("--base-severity", type=float, required=True,
                    help="base-period severity (avg cost per claim)")
    lr.add_argument("--cur-severity", type=float, required=True,
                    help="current-period severity (avg cost per claim)")
    lr.set_defaults(func=cmd_loss_ratio)

    rr = sub.add_parser("reserve-runoff", help="Read prior-year reserve development (adverse/favorable)")
    rr.add_argument("--prior-ultimate", type=float, required=True,
                    help="prior ultimate-loss estimate for the cohort")
    rr.add_argument("--current-ultimate", type=float, required=True,
                    help="current (re-estimated) ultimate-loss estimate for the same cohort")
    rr.set_defaults(func=cmd_reserve_runoff)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
