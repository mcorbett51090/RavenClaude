#!/usr/bin/env python3
"""ria_calc.py - a zero-dependency RIA-practice decision-support calculator.

Removes arithmetic error from three recurring decisions a financial planner or
portfolio analyst at a Registered Investment Adviser works through constantly.
Every input is supplied by the USER (or the licensed adviser); the tool does the
arithmetic and shows the rule it applied. It is decision-SUPPORT over those
inputs, never a personalized recommendation.

  withdrawal   A starting safe-withdrawal figure from portfolio + annual spend +
               horizon, plus the Guyton-Klinger-style GUARDRAIL bands (an upper
               and lower withdrawal-rate guardrail off the starting rate) that
               turn a blind fixed percentage into a monitored, pre-agreed
               cut/raise rule. Pairs with the "Which retirement withdrawal
               strategy?" decision tree (knowledge/...-decision-trees.md) and the
               surface-every-assumption best-practice. Sequence-of-returns risk
               is named, never hidden inside one confident number.

  rebalance    The drift of each holding from its IPS target weight, flagged
               against a tolerance band, decomposed into a BUY/SELL trade list
               that returns the portfolio to target. Pairs with the
               "Calendar or threshold/bands rebalancing?" tree and the
               rebalancing-is-a-written-rule best-practice. The rule lives in the
               IPS; this tool only does the band math the rule specifies.

  allocation   A risk-tier / glidepath target equity-vs-bond split from a risk
               score (1-5) and years-to-goal, with the classic age-based
               "110 - age" heuristic as a cross-check. Pairs with the
               asset-allocation-dominates-selection best-practice. Output is a
               starting frame for the IPS conversation, NOT an allocation
               prescription for a specific person.

This is a CALCULATOR, not a data source - it does not fetch returns, market
levels, fund data, or a client's actual holdings. Stdlib only (argparse); runs
anywhere Python 3.8+ is present.

IMPORTANT: outputs are EDUCATIONAL / OPERATIONAL decision-support, NOT
personalized investment, tax, or legal advice, and NOT a recommendation to buy
or sell any security (see ../CLAUDE.md sec.0). A licensed human adviser applies
these frameworks to a specific client only after confirming suitability; a CPA /
attorney owns the tax and legal conclusions. The withdrawal rate is a planning
HYPOTHESIS to monitor, not a guarantee.

Examples
--------
  # Safe withdrawal + guardrails: $1.2M portfolio, $48k/yr spend, 30-yr horizon
  python3 ria_calc.py withdrawal --portfolio 1200000 --spend 48000 --horizon 30

  # Rebalance drift: targets must sum to 100%, holdings are current dollar values
  python3 ria_calc.py rebalance --band 5% \\
      --target US-equity=50% Intl-equity=20% Bonds=25% Cash=5% \\
      --holding US-equity=700000 Intl-equity=240000 Bonds=240000 Cash=20000

  # Allocation frame: risk score 3 of 5, 20 years to the goal, client age 45
  python3 ria_calc.py allocation --risk 3 --years 20 --age 45
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '5%' or '0.05' into a fraction (0.05)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"must be like '5%' or '0.05', got {s!r}"
        ) from None


def _parse_named_pairs(items: list[str], what: str) -> dict[str, float]:
    """Parse ['name=value', ...] into an ordered dict; value may carry a '%'."""
    out: dict[str, float] = {}
    for raw in items:
        if "=" not in raw:
            raise argparse.ArgumentTypeError(
                f"{what} entry {raw!r} must be name=value"
            )
        name, _, value = raw.partition("=")
        name = name.strip()
        if not name:
            raise argparse.ArgumentTypeError(f"{what} entry {raw!r} has empty name")
        if name in out:
            raise argparse.ArgumentTypeError(f"{what} names a duplicate {name!r}")
        out[name] = _parse_rate(value)
    return out


def cmd_withdrawal(args: argparse.Namespace) -> int:
    if args.portfolio <= 0:
        print("error: --portfolio must be > 0", file=sys.stderr)
        return 2
    if args.spend < 0:
        print("error: --spend must be >= 0", file=sys.stderr)
        return 2
    if args.horizon <= 0:
        print("error: --horizon must be > 0 years", file=sys.stderr)
        return 2

    # Starting safe-withdrawal RATE: a horizon-aware heuristic anchored on the
    # 4%-rule tradition (longer horizon -> lower rate to survive a bad sequence).
    # This is a planning anchor the adviser overrides, not a fact about a client.
    if args.start_rate is not None:
        start_rate = args.start_rate
        rate_note = "user-supplied starting rate"
    elif args.horizon >= 30:
        start_rate = 0.040
        rate_note = "30+ yr horizon -> 4.0% anchor"
    elif args.horizon >= 20:
        start_rate = 0.045
        rate_note = "20-29 yr horizon -> 4.5% anchor"
    else:
        start_rate = 0.050
        rate_note = "<20 yr horizon -> 5.0% anchor"

    supported = args.portfolio * start_rate
    requested_rate = args.spend / args.portfolio

    # Guyton-Klinger-style guardrails: an upper/lower withdrawal-RATE band off the
    # starting rate. If the portfolio falls so the current rate drifts above the
    # upper guardrail, the rule cuts spending; if it rises past the lower
    # guardrail, the rule allows a raise.
    upper_guard = start_rate * (1.0 + args.guardrail)
    lower_guard = start_rate * (1.0 - args.guardrail)
    # Portfolio levels (holding spend fixed) at which each guardrail trips.
    cut_below = args.spend / upper_guard
    raise_above = args.spend / lower_guard

    print("Safe withdrawal + guardrails - a monitored hypothesis, not a guarantee")
    print(f"  portfolio              : {args.portfolio:,.0f}")
    print(f"  planned annual spend   : {args.spend:,.0f}")
    print(f"  horizon                : {args.horizon:g} years")
    print(f"  starting rate          : {start_rate * 100:g}%  ({rate_note})")
    print(f"  -> supported spend     : {supported:,.0f}/yr at the starting rate")
    print(f"  -> requested rate      : {requested_rate * 100:.2f}% of the portfolio")
    margin = supported - args.spend
    if margin >= 0:
        print(
            f"  -> headroom            : {margin:,.0f}/yr "
            "(planned spend within the starting rate)"
        )
    else:
        print(
            f"  -> SHORTFALL           : {-margin:,.0f}/yr "
            "(planned spend above the starting rate - tight plan)"
        )
    print(f"  guardrails (+/- {args.guardrail * 100:g}% of the starting rate):")
    print(
        f"    upper guardrail rate : {upper_guard * 100:.2f}%  "
        f"-> CUT spending if the portfolio falls below {cut_below:,.0f}"
    )
    print(
        f"    lower guardrail rate : {lower_guard * 100:.2f}%  "
        f"-> may RAISE spending if the portfolio rises above {raise_above:,.0f}"
    )
    print("  note: the rate is a planning HYPOTHESIS to monitor, not a promise.")
    print("        Sequence-of-returns risk (bad EARLY years), longevity, inflation,")
    print("        and real return are client-specific assumptions to surface and")
    print("        confirm with the licensed adviser. Not investment advice.")
    return 0


def cmd_rebalance(args: argparse.Namespace) -> int:
    targets = _parse_named_pairs(args.target, "--target")
    holdings = _parse_named_pairs(args.holding, "--holding")

    target_sum = sum(targets.values())
    if abs(target_sum - 1.0) > 1e-6:
        print(
            f"error: --target weights sum to {target_sum * 100:g}%, must sum to 100%",
            file=sys.stderr,
        )
        return 2
    missing = set(targets) - set(holdings)
    extra = set(holdings) - set(targets)
    if missing:
        print(
            f"error: --holding missing target asset(s): {', '.join(sorted(missing))}",
            file=sys.stderr,
        )
        return 2
    if extra:
        print(
            f"error: --holding has untargeted asset(s): {', '.join(sorted(extra))}",
            file=sys.stderr,
        )
        return 2

    total = sum(holdings.values())
    if total <= 0:
        print("error: total of --holding values must be > 0", file=sys.stderr)
        return 2

    print("Rebalance drift - against IPS targets (the rule lives in the IPS)")
    print(f"  total portfolio : {total:,.0f}")
    print(f"  tolerance band  : +/- {args.band * 100:g}% (absolute weight)")
    print("  asset            | target |  actual |   drift | trade")
    print("  -----------------+--------+---------+---------+----------------")

    trades: list[tuple[str, float]] = []
    for name, tgt_w in targets.items():
        actual_v = holdings[name]
        actual_w = actual_v / total
        drift = actual_w - tgt_w
        target_v = tgt_w * total
        delta_v = target_v - actual_v  # +ve = buy, -ve = sell
        if abs(drift) > args.band:
            action = "BUY" if delta_v > 0 else "SELL"
            trades.append((name, delta_v))
            trade_str = f"{action} {abs(delta_v):,.0f}"
        else:
            trade_str = "in band"
        print(
            f"  {name:<16} | {tgt_w * 100:>5.1f}% | {actual_w * 100:>6.1f}% "
            f"| {drift * 100:>+6.1f}% | {trade_str}"
        )

    print()
    if not trades:
        print("  -> no trades: every asset is within the tolerance band.")
    else:
        buys = sum(v for _, v in trades if v > 0)
        sells = -sum(v for _, v in trades if v < 0)
        print("  -> trade list to return to target:")
        for name, delta_v in trades:
            verb = "BUY " if delta_v > 0 else "SELL"
            print(f"       {verb} {abs(delta_v):>12,.0f}  {name}")
        print(f"  -> buys {buys:,.0f} | sells {sells:,.0f} | net {buys - sells:,.0f}")
    print("  note: in TAXABLE accounts prefer bands + tax-aware execution (use new")
    print("        contributions and harvested losses first; mind the wash-sale")
    print("        rule across the household). The band rule and tax posture are")
    print("        IPS/adviser decisions. Not investment or tax advice.")
    return 0


def cmd_allocation(args: argparse.Namespace) -> int:
    if not 1 <= args.risk <= 5:
        print("error: --risk must be an integer 1-5", file=sys.stderr)
        return 2
    if args.years <= 0:
        print("error: --years must be > 0", file=sys.stderr)
        return 2

    # Risk tier -> baseline equity weight (the willingness/CAPACITY frame the
    # adviser confirms; capacity is NOT the same as a questionnaire's tolerance).
    risk_equity = {1: 0.30, 2: 0.45, 3: 0.60, 4: 0.75, 5: 0.90}
    base_equity = risk_equity[args.risk]

    # Glidepath: a short horizon de-risks the baseline (sequence risk near the
    # goal); a long horizon allows a modest tilt back toward equity.
    if args.years < 5:
        glide = -0.20
        glide_note = "<5 yr to goal -> de-risk 20pts (sequence risk near the goal)"
    elif args.years < 10:
        glide = -0.10
        glide_note = "5-9 yr to goal -> de-risk 10pts"
    elif args.years >= 20:
        glide = 0.05
        glide_note = "20+ yr to goal -> +5pts equity tilt"
    else:
        glide = 0.0
        glide_note = "10-19 yr to goal -> no glide adjustment"

    equity = max(0.0, min(1.0, base_equity + glide))
    bonds = 1.0 - equity

    print("Allocation frame - a starting point for the IPS conversation")
    print(f"  risk tier              : {args.risk} of 5  (baseline equity {base_equity * 100:g}%)")
    print(f"  years to goal          : {args.years:g}  ({glide_note})")
    print(f"  -> target equity       : {equity * 100:.0f}%")
    print(f"  -> target bonds/cash   : {bonds * 100:.0f}%")
    if args.age is not None:
        if args.age <= 0:
            print("error: --age must be > 0", file=sys.stderr)
            return 2
        age_equity = max(0.0, min(1.0, (110 - args.age) / 100.0))
        print(
            f"  cross-check (110-age)  : age {args.age:g} -> {age_equity * 100:.0f}% "
            "equity (a coarse heuristic only)"
        )
    print("  note: asset ALLOCATION dominates security selection - this is the big")
    print("        lever. The split above is a starting frame, NOT a prescription:")
    print("        risk tolerance AND capacity, horizon, liquidity, and tax status")
    print("        are client-specific facts the licensed adviser confirms before")
    print("        an IPS is written. Not personalized investment advice.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ria_calc.py",
        description="RIA-practice decision-support calculator (stdlib only). "
        "Educational/operational decision-support over USER inputs - NOT "
        "personalized investment, tax, or legal advice, and not a buy/sell "
        "recommendation. A licensed adviser confirms suitability first.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    wd = sub.add_parser(
        "withdrawal", help="Safe-withdrawal start + Guyton-Klinger-style guardrails"
    )
    wd.add_argument("--portfolio", type=float, required=True, help="portfolio value")
    wd.add_argument("--spend", type=float, required=True, help="planned annual spend")
    wd.add_argument(
        "--horizon", type=float, required=True, help="planning horizon in years"
    )
    wd.add_argument(
        "--start-rate",
        type=_parse_rate,
        default=None,
        help="override the starting withdrawal rate (e.g. 4%% or 0.04)",
    )
    wd.add_argument(
        "--guardrail",
        type=_parse_rate,
        default=0.20,
        help="guardrail band as a fraction of the start rate (default 20%%)",
    )
    wd.set_defaults(func=cmd_withdrawal)

    rb = sub.add_parser("rebalance", help="Drift vs IPS targets -> trade list")
    rb.add_argument(
        "--target",
        nargs="+",
        required=True,
        metavar="NAME=WEIGHT",
        help="target weights, e.g. US-equity=50%% Bonds=50%% (must sum to 100%%)",
    )
    rb.add_argument(
        "--holding",
        nargs="+",
        required=True,
        metavar="NAME=VALUE",
        help="current dollar value per asset, e.g. US-equity=700000",
    )
    rb.add_argument(
        "--band",
        type=_parse_rate,
        default=0.05,
        help="tolerance band on absolute weight (default 5%%)",
    )
    rb.set_defaults(func=cmd_rebalance)

    al = sub.add_parser(
        "allocation", help="Risk-tier + glidepath target equity/bond frame"
    )
    al.add_argument(
        "--risk", type=int, required=True, help="risk tier 1 (low) to 5 (high)"
    )
    al.add_argument("--years", type=float, required=True, help="years to the goal")
    al.add_argument(
        "--age", type=float, default=None, help="optional age for a 110-age cross-check"
    )
    al.set_defaults(func=cmd_allocation)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
