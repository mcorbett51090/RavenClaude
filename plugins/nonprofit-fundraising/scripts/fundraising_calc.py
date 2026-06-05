#!/usr/bin/env python3
"""fundraising_calc.py — a zero-dependency nonprofit-fundraising decision calculator.

Removes arithmetic error from three recurring development-office decisions a
fundraiser / development director / consultant runs constantly:

  gift-pyramid    The GIFT RANGE CHART (a.k.a. gift pyramid) for a campaign or
                  annual-fund goal. Given a goal, a top-gift fraction, and a
                  tier ladder, it builds the tiered table of gifts-needed,
                  prospects-needed (gifts x a prospect-multiplier), and the
                  running cumulative — the standard top-down feasibility tool.
                  Pairs with knowledge/nonprofit-campaign-readiness-decision-tree.md.

  cost-per-dollar The COST-TO-RAISE-A-DOLLAR per channel, NEVER blended (house
                  opinion #4). For each channel you supply spend + revenue; it
                  prints per-channel CRD and ROI, the blended CRD, and flags the
                  channel that is subsidizing the others. Pairs with
                  knowledge/fundraising-economics.md and the read-cost-per-dollar skill.

  donor-ltv       The DONOR LIFETIME VALUE: average gift x gifts/year x donor
                  lifespan. Lifespan can be given directly OR derived from a
                  retention rate (lifespan ~= 1 / (1 - retention)), the standard
                  conversion. Prints LTV and the retain-vs-acquire payback so the
                  "retention is the cheapest dollar" call is quantified. Pairs
                  with the protect-donor-retention skill.

This is a CALCULATOR, not a data source — it does not fetch benchmarks, gift
capacities, or live costs. The user supplies every input; the tool does the
arithmetic and shows the formula. Stdlib only (argparse); runs anywhere Python
3.8+ is present.

IMPORTANT: outputs are decision-support, not tax, legal, gift-acceptance, or
licensed financial advice (see ../CLAUDE.md §2). Validate every figure against
the org's actual data before any deliverable (CLAUDE.md §3 #8).

Examples
--------
  # Gift pyramid for a $500k campaign: top gift 15% of goal, default ladder,
  # needing ~4 qualified prospects per gift
  python3 fundraising_calc.py gift-pyramid --goal 500000 --top-gift-pct 15% \\
      --prospects-per-gift 4

  # Cost-per-dollar across four channels (label:spend:revenue triples)
  python3 fundraising_calc.py cost-per-dollar \\
      --channel major-gifts:25000:500000 \\
      --channel grants:40000:200000 \\
      --channel direct-mail:60000:90000 \\
      --channel events:80000:160000

  # Donor LTV from a 65% retention rate: $120 avg gift, 1.5 gifts/year,
  # acquisition cost $180, retain cost $25
  python3 fundraising_calc.py donor-ltv --avg-gift 120 --gifts-per-year 1.5 \\
      --retention 65% --acquire-cost 180 --retain-cost 25
"""

from __future__ import annotations

import argparse
import sys

# Default gift-range ladder: each row is (label, fraction-of-top-gift, count).
# A conventional top-down chart steps the gift size down and widens the count as
# it descends — the classic pyramid. The counts encode the rule of thumb that a
# campaign needs only a handful of top gifts but many small ones. The user
# overrides the whole ladder with --tier (label:fraction:count) for real capacity.
_DEFAULT_LADDER = [
    ("Lead gift", 1.0, 1),
    ("Second tier", 0.50, 2),
    ("Third tier", 0.25, 4),
    ("Fourth tier", 0.10, 10),
    ("Fifth tier", 0.05, 20),
    ("Base / many", 0.02, 50),
]


def _parse_rate(s: str) -> float:
    """Parse a rate like '65%' or '0.65' into a fraction (0.65)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '65%' or '0.65', got {s!r}")


def _parse_channel(s: str) -> tuple[str, float, float]:
    """Parse a 'label:spend:revenue' triple."""
    parts = s.split(":")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(
            f"must be 'label:spend:revenue', got {s!r}"
        )
    label, spend_s, rev_s = parts
    try:
        spend = float(spend_s)
        revenue = float(rev_s)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"spend and revenue must be numbers in {s!r}"
        )
    if spend < 0 or revenue < 0:
        raise argparse.ArgumentTypeError(f"spend and revenue must be >= 0 in {s!r}")
    return (label.strip() or "(unnamed)", spend, revenue)


def _parse_tier(s: str) -> tuple[str, float, int]:
    """Parse a 'label:fraction:count' tier override (fraction of the top gift)."""
    parts = s.split(":")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(
            f"must be 'label:fraction:count', got {s!r}"
        )
    label, frac_s, count_s = parts
    frac = _parse_rate(frac_s)
    if not 0.0 < frac <= 1.0:
        raise argparse.ArgumentTypeError(f"tier fraction must be in (0, 1], got {s!r}")
    try:
        count = int(count_s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"tier count must be an integer in {s!r}")
    if count < 1:
        raise argparse.ArgumentTypeError(f"tier count must be >= 1 in {s!r}")
    return (label.strip() or "(tier)", frac, count)


def cmd_gift_pyramid(args: argparse.Namespace) -> int:
    if args.goal <= 0:
        print("error: --goal must be > 0", file=sys.stderr)
        return 2
    if not 0.0 < args.top_gift_pct <= 1.0:
        print("error: --top-gift-pct must be in (0%, 100%]", file=sys.stderr)
        return 2
    if args.prospects_per_gift < 1.0:
        print("error: --prospects-per-gift must be >= 1", file=sys.stderr)
        return 2

    ladder = args.tier if args.tier else _DEFAULT_LADDER
    top_gift = args.goal * args.top_gift_pct

    print("Gift range chart (gift pyramid)")
    print(f"  campaign / annual-fund goal : {args.goal:,.0f}")
    print(f"  lead (top) gift             : {top_gift:,.0f} ({args.top_gift_pct * 100:g}% of goal)")
    print(f"  prospects needed per gift   : {args.prospects_per_gift:g}x")
    print("  tier            | gift size | gifts | prospects | tier total | cumulative")
    print("  ----------------+-----------+-------+-----------+------------+-----------")

    cumulative = 0.0
    total_gifts = 0
    total_prospects = 0.0
    for label, frac, count in ladder:
        gift_size = top_gift * frac
        if gift_size <= 0 or count <= 0:
            continue
        tier_total = gift_size * count
        prospects = count * args.prospects_per_gift
        cumulative += tier_total
        total_gifts += count
        total_prospects += prospects
        print(
            f"  {label:<15} | {gift_size:>9,.0f} | {count:>5} | "
            f"{prospects:>9,.0f} | {tier_total:>10,.0f} | {cumulative:>10,.0f}"
        )

    print("  ----------------+-----------+-------+-----------+------------+-----------")
    print(f"  {'TOTAL':<15} | {'':>9} | {total_gifts:>5} | {total_prospects:>9,.0f} | "
          f"{cumulative:>10,.0f} |")

    print()
    pct_of_goal = (cumulative / args.goal * 100.0) if args.goal else 0.0
    print(f"  → ladder raises {cumulative:,.0f} = {pct_of_goal:.0f}% of the {args.goal:,.0f} goal.")
    if cumulative < args.goal:
        gap = args.goal - cumulative
        print(f"    GAP of {gap:,.0f} — widen a tier's count, raise the top gift, or trim the goal.")
    elif cumulative > args.goal * 1.15:
        print("    Ladder over-raises by >15% — you can trim a tier's count (build in some cushion).")
    print("  → 80/20 reality check: the top ~10-20% of gifts typically carry 50-80%+ of the goal.")
    print("    Validate every tier against your ACTUAL rated prospects — a pyramid the")
    print("    prospect pool can't fill is a feasibility flag, not a plan (§3 #8).")
    return 0


def cmd_cost_per_dollar(args: argparse.Namespace) -> int:
    channels = args.channel
    if not channels:
        print("error: supply at least one --channel label:spend:revenue", file=sys.stderr)
        return 2

    print("Cost to raise a dollar — by channel (never blended; §3 #4)")
    print("  channel         |     spend |   revenue |   CRD | ROI ($/$ )")
    print("  ----------------+-----------+-----------+-------+-----------")

    total_spend = 0.0
    total_revenue = 0.0
    rows = []
    for label, spend, revenue in channels:
        total_spend += spend
        total_revenue += revenue
        crd = (spend / revenue) if revenue > 0 else float("inf")
        roi = (revenue / spend) if spend > 0 else float("inf")
        rows.append((label, spend, revenue, crd, roi))
        crd_s = "  n/a" if crd == float("inf") else f"{crd:>5.2f}"
        roi_s = "  n/a" if roi == float("inf") else f"{roi:>6.2f}"
        print(f"  {label:<15} | {spend:>9,.0f} | {revenue:>9,.0f} | {crd_s} | {roi_s}")

    blended_crd = (total_spend / total_revenue) if total_revenue > 0 else float("inf")
    print("  ----------------+-----------+-----------+-------+-----------")
    blended_s = "  n/a" if blended_crd == float("inf") else f"{blended_crd:>5.2f}"
    print(f"  {'BLENDED':<15} | {total_spend:>9,.0f} | {total_revenue:>9,.0f} | {blended_s} |")

    print()
    # Identify the cheapest and most-expensive channels (finite CRD only).
    finite = [r for r in rows if r[3] != float("inf")]
    if finite:
        cheapest = min(finite, key=lambda r: r[3])
        priciest = max(finite, key=lambda r: r[3])
        if cheapest[3] > 0:
            print(f"  → cheapest channel  : {cheapest[0]} at {cheapest[3]:.2f} CRD "
                  f"(${1.0 / cheapest[3]:,.2f} raised per $1 spent)")
        else:
            print(f"  → cheapest channel  : {cheapest[0]} (zero spend)")
        if priciest[3] > blended_crd and priciest[0] != cheapest[0]:
            print(f"  → most expensive    : {priciest[0]} at {priciest[3]:.2f} CRD — "
                  "the blended number is HIDING this; read by channel.")
    print("  note: a channel above the blended CRD is being SUBSIDIZED by a cheaper one.")
    print("        Acquisition channels (direct-mail acq, events) run costlier than")
    print("        renewal/major-gift channels — judge each on its OWN role, not the blend.")
    return 0


def cmd_donor_ltv(args: argparse.Namespace) -> int:
    if args.avg_gift <= 0:
        print("error: --avg-gift must be > 0", file=sys.stderr)
        return 2
    if args.gifts_per_year <= 0:
        print("error: --gifts-per-year must be > 0", file=sys.stderr)
        return 2

    # Lifespan: explicit, or derived from retention (lifespan ~= 1/(1-retention)).
    if args.lifespan is not None:
        lifespan = args.lifespan
        lifespan_src = f"{lifespan:g} years (given)"
    elif args.retention is not None:
        if not 0.0 <= args.retention < 1.0:
            print("error: --retention must be in [0%, 100%)", file=sys.stderr)
            return 2
        lifespan = 1.0 / (1.0 - args.retention)
        lifespan_src = (f"{lifespan:.2f} years (derived from {args.retention * 100:g}% "
                        "retention: 1 / (1 - r))")
    else:
        print("error: supply either --lifespan or --retention", file=sys.stderr)
        return 2

    if lifespan <= 0:
        print("error: lifespan must be > 0", file=sys.stderr)
        return 2

    ltv = args.avg_gift * args.gifts_per_year * lifespan
    annual_value = args.avg_gift * args.gifts_per_year

    print("Donor lifetime value")
    print(f"  average gift            : {args.avg_gift:,.2f}")
    print(f"  gifts per year          : {args.gifts_per_year:g}")
    print(f"  annual donor value      : {annual_value:,.2f}")
    print(f"  donor lifespan          : {lifespan_src}")
    print(f"  → LTV (gift x freq x lifespan) : {ltv:,.2f}")

    if args.acquire_cost is not None:
        net_first_year = annual_value - args.acquire_cost
        print()
        print(f"  acquisition cost        : {args.acquire_cost:,.2f}")
        print(f"  first-year net          : {net_first_year:,.2f} "
              f"({'recovered in year 1' if net_first_year >= 0 else 'underwater in year 1'})")
        if annual_value > 0 and net_first_year < 0:
            payback_years = args.acquire_cost / annual_value
            print(f"  acquisition payback     : {payback_years:.2f} years of giving to recoup")
        if args.retain_cost is not None and args.retain_cost > 0:
            ratio = args.acquire_cost / args.retain_cost
            print(f"  retain cost             : {args.retain_cost:,.2f}")
            print(f"  → acquire vs retain     : {ratio:.1f}x more expensive to acquire than retain")
            print("    (sector rule of thumb: keeping a donor is far cheaper than finding one — §3 #1)")
    print("  note: model lifespan from your OWN cohort retention, not a guess. A small")
    print("        retention gain compounds LTV sharply (lifespan = 1/(1-r) is convex).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="fundraising_calc.py",
        description="Nonprofit-fundraising decision calculator (stdlib only). "
        "Decision-support, not tax/legal/financial advice — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pyr = sub.add_parser("gift-pyramid", help="Gift range chart / pyramid for a goal")
    pyr.add_argument("--goal", type=float, required=True, help="campaign / annual-fund goal")
    pyr.add_argument("--top-gift-pct", type=_parse_rate, default=0.15,
                     help="lead (top) gift as a fraction of the goal (default 15%%)")
    pyr.add_argument("--prospects-per-gift", type=float, default=4.0,
                     help="qualified prospects needed per closed gift (default 4)")
    pyr.add_argument("--tier", type=_parse_tier, action="append", default=None,
                     help="override a ladder row as 'label:fraction-of-top-gift:count' "
                     "(repeatable; replaces the default ladder entirely)")
    pyr.set_defaults(func=cmd_gift_pyramid)

    cpd = sub.add_parser("cost-per-dollar", help="Cost-to-raise-a-dollar by channel")
    cpd.add_argument("--channel", type=_parse_channel, action="append", default=None,
                     help="a 'label:spend:revenue' triple (repeatable, one per channel)")
    cpd.set_defaults(func=cmd_cost_per_dollar)

    ltv = sub.add_parser("donor-ltv", help="Donor lifetime value + retain-vs-acquire")
    ltv.add_argument("--avg-gift", type=float, required=True, help="average gift amount")
    ltv.add_argument("--gifts-per-year", type=float, required=True,
                     help="average gifts per donor per year (frequency)")
    ltv.add_argument("--lifespan", type=float, default=None,
                     help="donor lifespan in years (or supply --retention to derive it)")
    ltv.add_argument("--retention", type=_parse_rate, default=None,
                     help="annual retention rate; lifespan derived as 1/(1-r) (e.g. 65%%)")
    ltv.add_argument("--acquire-cost", type=float, default=None,
                     help="cost to acquire one donor (optional; enables payback math)")
    ltv.add_argument("--retain-cost", type=float, default=None,
                     help="cost to retain one donor (optional; enables the ratio)")
    ltv.set_defaults(func=cmd_donor_ltv)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
