#!/usr/bin/env python3
"""growth_calc.py — a zero-dependency content-and-growth-marketing calculator.

Removes arithmetic error from three recurring content/SEO/lifecycle decisions a
content strategist, SEO lead, or lifecycle engineer runs constantly:

  funnel    The demand-gen FUNNEL — stage-to-stage conversion and DROP-OFF across
            visitor -> lead -> MQL -> SQL -> win. Shows the conversion rate and the
            absolute + percentage drop at each step, flags the worst-leaking stage,
            and (with --revenue-per-win) the implied pipeline/revenue. This is the
            "where is the funnel leaking" read (CLAUDE.md s4 #4) — measure the
            STAGE, not a single blended rate.

  cac-ltv   The acquisition math — blended CAC (spend / new customers), LTV
            (ARPA x gross-margin% x expected lifetime from monthly churn), the
            LTV:CAC ratio against the 3:1 / 2:1 lines, and CAC PAYBACK in months.
            Pairs the throughput number with the outcome (s4 #4) — list/traffic
            growth is vanity unless it clears the acquisition-economics line.

  email     The email read — deliverability-weighted reach and the open/click
            funnel, plus a LIST-DECAY projection (a list erodes ~_n_%/yr without
            acquisition). Shows delivered, inbox-placed, opened, clicked, and the
            engaged list after N months of decay. Deliverability is the foundation
            (s4 #5): an email in spam converts at zero, and open rate is a vanity
            metric next to engaged-list health.

This is a CALCULATOR, not a data source — it does not fetch benchmarks, search
volumes, or live analytics. The user supplies every input; the tool does the
arithmetic and shows the formula. Stdlib only (argparse); runs anywhere Python
3.8+ is present.

IMPORTANT: outputs are decision-support, not a guarantee. Validate every figure
against the team's actual analytics/ESP data before any deliverable, and name the
source + freshness of every number (CLAUDE.md s4 #4, best-practices/
cite-the-source-and-date-never-fabricate-a-number.md).

Examples
--------
  # Funnel: 50000 visitors -> 2500 leads -> 800 MQL -> 200 SQL -> 50 wins,
  # at $12000 per won deal
  python3 growth_calc.py funnel --visitors 50000 --leads 2500 --mql 800 \\
      --sql 200 --wins 50 --revenue-per-win 12000

  # CAC/LTV: $30000 spend, 250 new customers, $90/mo ARPA, 75% gross margin,
  # 4% monthly churn
  python3 growth_calc.py cac-ltv --spend 30000 --new-customers 250 \\
      --arpa 90 --gross-margin 75% --monthly-churn 4%

  # Email: 180000 sent, 98% delivered, 92% inbox placement, 28% open,
  # 3.5% click, 25%/yr list decay projected over 12 months
  python3 growth_calc.py email --sent 180000 --delivered-rate 98% \\
      --inbox-rate 92% --open-rate 28% --click-rate 3.5% \\
      --annual-decay 25% --months 12
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
        raise argparse.ArgumentTypeError(
            f"must be like '28%' or '0.28', got {s!r}"
        ) from None


def _drop(prev: float, cur: float) -> tuple[float, float]:
    """Return (conversion_fraction, dropoff_fraction) from prev -> cur."""
    if prev <= 0:
        return 0.0, 0.0
    conv = cur / prev
    return conv, 1.0 - conv


def cmd_funnel(args: argparse.Namespace) -> int:
    stages = [
        ("visitors", args.visitors),
        ("leads", args.leads),
        ("MQL", args.mql),
        ("SQL", args.sql),
        ("wins", args.wins),
    ]
    for name, val in stages:
        if val < 0:
            print(f"error: --{name.lower()} must be >= 0", file=sys.stderr)
            return 2
    if args.visitors <= 0:
        print("error: --visitors must be > 0", file=sys.stderr)
        return 2
    # Each stage must be <= the one before it (a funnel only narrows).
    for (pname, pval), (cname, cval) in zip(stages, stages[1:]):
        if cval > pval:
            print(
                f"error: {cname} ({cval:g}) exceeds {pname} ({pval:g}) — "
                "a funnel stage cannot be larger than the one before it",
                file=sys.stderr,
            )
            return 2

    print("Demand-gen funnel — stage conversion & drop-off")
    print(f"  {'visitors':<10}: {args.visitors:>12,.0f}")
    worst_name = None
    worst_drop = -1.0
    for (pname, pval), (cname, cval) in zip(stages, stages[1:]):
        conv, drop = _drop(pval, cval)
        lost = pval - cval
        print(
            f"  {cname:<10}: {cval:>12,.0f}   "
            f"conv {conv * 100:6.2f}%   drop {drop * 100:6.2f}%  (-{lost:,.0f})"
        )
        if drop > worst_drop:
            worst_drop = drop
            worst_name = f"{pname} -> {cname}"

    overall, _ = _drop(args.visitors, args.wins)
    print("  --------------------------------------------------")
    print(f"  visitor -> win   : {overall * 100:.3f}%  end-to-end")
    if worst_name is not None:
        print(
            f"  -> worst leak    : {worst_name}  "
            f"({worst_drop * 100:.2f}% drop) — attack this stage first (s4 #4)."
        )
    if args.revenue_per_win is not None:
        if args.revenue_per_win < 0:
            print("error: --revenue-per-win must be >= 0", file=sys.stderr)
            return 2
        pipeline = args.wins * args.revenue_per_win
        print(
            f"  -> won revenue   : {pipeline:,.2f}  "
            f"({args.wins:,.0f} wins x {args.revenue_per_win:,.2f})"
        )
        if args.wins > 0:
            rev_per_visitor = pipeline / args.visitors
            print(
                f"  -> revenue/visit : {rev_per_visitor:,.4f}  "
                "(the outcome metric — not raw traffic, s4 #4)."
            )
    print(
        "  note: read the STAGE, not a blended rate — a healthy visitor->lead can "
        "hide a dead MQL->SQL. Name the source/window of every count (s4 #4)."
    )
    return 0


def cmd_cac_ltv(args: argparse.Namespace) -> int:
    if args.spend < 0 or args.new_customers <= 0 or args.arpa <= 0:
        print(
            "error: --spend >= 0, --new-customers > 0, --arpa > 0 required",
            file=sys.stderr,
        )
        return 2
    if not 0.0 < args.gross_margin <= 1.0:
        print("error: --gross-margin must be in (0%, 100%]", file=sys.stderr)
        return 2
    if not 0.0 < args.monthly_churn <= 1.0:
        print("error: --monthly-churn must be in (0%, 100%]", file=sys.stderr)
        return 2

    cac = args.spend / args.new_customers
    lifetime_months = 1.0 / args.monthly_churn
    margin_per_month = args.arpa * args.gross_margin
    ltv = margin_per_month * lifetime_months
    ratio = ltv / cac if cac > 0 else float("inf")
    payback_months = cac / margin_per_month if margin_per_month > 0 else float("inf")

    print("CAC / LTV — acquisition economics")
    print(f"  spend                 : {args.spend:,.2f}")
    print(f"  new customers         : {args.new_customers:,.0f}")
    print(f"  -> blended CAC        : {cac:,.2f}  (spend / new customers)")
    print(f"  ARPA                  : {args.arpa:,.2f}/mo")
    print(f"  gross margin          : {args.gross_margin * 100:g}%")
    print(f"  monthly churn         : {args.monthly_churn * 100:g}%")
    print(
        f"  -> expected lifetime  : {lifetime_months:,.1f} mo  "
        f"(1 / {args.monthly_churn * 100:g}% churn)"
    )
    print(
        f"  -> LTV (margin-based) : {ltv:,.2f}  "
        f"({margin_per_month:,.2f}/mo x {lifetime_months:,.1f} mo)"
    )
    print(f"  -> LTV:CAC            : {ratio:.2f} : 1")
    print(f"  -> CAC payback        : {payback_months:,.1f} months")
    print()
    if ratio < 2.0:
        print(
            "  -> BELOW 2:1 — immediate problem. Acquiring at a loss against "
            "realized LTV; fix retention/ARPA or cut CAC before scaling spend."
        )
    elif ratio < 3.0:
        print(
            "  -> Between 2:1 and 3:1 — under the 3:1 sustainability line. "
            "Workable but fragile; protect retention before adding spend."
        )
    else:
        print(
            "  -> At or above 3:1 — clears the sustainability line. Headroom to "
            "scale, but watch payback as a separate CASH constraint."
        )
    print(
        "  note: list/traffic growth is VANITY unless it clears this line (s4 #4). "
        "LTV here is gross-margin LTV, not revenue. Cite the source of each input."
    )
    return 0


def cmd_email(args: argparse.Namespace) -> int:
    if args.sent <= 0:
        print("error: --sent must be > 0", file=sys.stderr)
        return 2
    for name, val in (
        ("--delivered-rate", args.delivered_rate),
        ("--inbox-rate", args.inbox_rate),
        ("--open-rate", args.open_rate),
        ("--click-rate", args.click_rate),
        ("--annual-decay", args.annual_decay),
    ):
        if not 0.0 <= val <= 1.0:
            print(f"error: {name} must be in [0%, 100%]", file=sys.stderr)
            return 2
    if args.months < 0:
        print("error: --months must be >= 0", file=sys.stderr)
        return 2

    delivered = args.sent * args.delivered_rate
    inboxed = delivered * args.inbox_rate
    # Opens/clicks are taken against the INBOX-PLACED count — mail in the spam
    # folder converts at ~zero (s4 #5), so placement gates the whole funnel.
    opened = inboxed * args.open_rate
    clicked = inboxed * args.click_rate

    print("Email — deliverability-weighted reach & engagement funnel")
    print(f"  sent              : {args.sent:>12,.0f}")
    print(
        f"  delivered         : {delivered:>12,.0f}   "
        f"({args.delivered_rate * 100:g}% of sent)"
    )
    print(
        f"  inbox-placed      : {inboxed:>12,.0f}   "
        f"({args.inbox_rate * 100:g}% of delivered)"
    )
    print(
        f"  opened            : {opened:>12,.0f}   "
        f"({args.open_rate * 100:g}% of inbox-placed)"
    )
    print(
        f"  clicked           : {clicked:>12,.0f}   "
        f"({args.click_rate * 100:g}% of inbox-placed)"
    )
    eff = inboxed / args.sent if args.sent > 0 else 0.0
    print(
        f"  -> effective reach: {eff * 100:.2f}%  of sent actually reached an inbox "
        "(the number that matters, not 'delivered', s4 #5)."
    )

    if args.annual_decay > 0 and args.months > 0:
        # Compound monthly: a list erodes ~annual_decay%/yr without acquisition.
        monthly_retention = (1.0 - args.annual_decay) ** (1.0 / 12.0)
        remaining_frac = monthly_retention ** args.months
        engaged = args.sent * remaining_frac
        lost = args.sent - engaged
        print()
        print(
            f"  list-decay projection ({args.annual_decay * 100:g}%/yr, "
            f"{args.months} mo, no acquisition):"
        )
        print(
            f"  -> engaged list   : {engaged:>12,.0f}   "
            f"({remaining_frac * 100:.1f}% retained; -{lost:,.0f})"
        )
        print(
            "     a list is a leaking bucket — re-engagement + steady acquisition "
            "offset decay; list SIZE is vanity, engaged-list health is the metric."
        )
    print(
        "  note: opens are an unreliable vanity metric (privacy proxies inflate "
        "them). Judge on inbox placement, click, and revenue per recipient (s4 #4/#5)."
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="growth_calc.py",
        description="Content-and-growth-marketing calculator (stdlib only). "
        "Decision-support, not a guarantee — validate every input, cite every source.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    fn = sub.add_parser(
        "funnel", help="Demand-gen funnel conversion + drop-off by stage"
    )
    fn.add_argument("--visitors", type=float, required=True, help="top-of-funnel visitors")
    fn.add_argument("--leads", type=float, required=True, help="leads (captured)")
    fn.add_argument("--mql", type=float, required=True, help="marketing-qualified leads")
    fn.add_argument("--sql", type=float, required=True, help="sales-qualified leads")
    fn.add_argument("--wins", type=float, required=True, help="closed-won deals")
    fn.add_argument(
        "--revenue-per-win",
        type=float,
        default=None,
        help="avg revenue per won deal, to print pipeline + revenue/visitor (optional)",
    )
    fn.set_defaults(func=cmd_funnel)

    cl = sub.add_parser("cac-ltv", help="CAC, LTV, LTV:CAC ratio + payback months")
    cl.add_argument("--spend", type=float, required=True, help="acquisition spend")
    cl.add_argument(
        "--new-customers", type=float, required=True, help="new customers acquired"
    )
    cl.add_argument("--arpa", type=float, required=True, help="avg revenue per account / month")
    cl.add_argument(
        "--gross-margin",
        type=_parse_rate,
        required=True,
        help="gross margin as a fraction (e.g. 75%%)",
    )
    cl.add_argument(
        "--monthly-churn",
        type=_parse_rate,
        required=True,
        help="monthly churn (e.g. 4%%); expected lifetime = 1/churn",
    )
    cl.set_defaults(func=cmd_cac_ltv)

    em = sub.add_parser(
        "email", help="Deliverability/open/click funnel + list-decay projection"
    )
    em.add_argument("--sent", type=float, required=True, help="emails sent")
    em.add_argument(
        "--delivered-rate",
        type=_parse_rate,
        default=1.0,
        help="fraction delivered (e.g. 98%%); default 100%%",
    )
    em.add_argument(
        "--inbox-rate",
        type=_parse_rate,
        default=1.0,
        help="inbox placement as a fraction of delivered (e.g. 92%%); default 100%%",
    )
    em.add_argument(
        "--open-rate",
        type=_parse_rate,
        default=0.0,
        help="open rate as a fraction of inbox-placed (e.g. 28%%)",
    )
    em.add_argument(
        "--click-rate",
        type=_parse_rate,
        default=0.0,
        help="click rate as a fraction of inbox-placed (e.g. 3.5%%)",
    )
    em.add_argument(
        "--annual-decay",
        type=_parse_rate,
        default=0.0,
        help="annual list decay without acquisition (e.g. 25%%)",
    )
    em.add_argument(
        "--months",
        type=int,
        default=12,
        help="months to project list decay over (default 12)",
    )
    em.set_defaults(func=cmd_email)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
