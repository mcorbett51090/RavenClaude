#!/usr/bin/env python3
"""hotel_calc.py — a zero-dependency hotel-operations decision calculator.

Removes arithmetic error from three recurring rooms-revenue decisions a revenue
manager, GM, or consultant runs constantly:

  revpar          The NORTH-STAR number. Computes RevPAR two equivalent ways —
                  from ADR x occupancy, and from room-revenue / available-rooms —
                  and reconciles them so a mismatch surfaces a bad input. Prints
                  ADR and occupancy implied by the revenue/rooms figures too.
                  Pairs with knowledge/...decision-trees.md and the
                  revenue-management-and-rate-strategy skill. RevPAR is the
                  north-star, read against GOPPAR (CLAUDE.md §4 #1).

  goppar          The PROFIT CHECK on a RevPAR strategy. Computes GOPPAR (gross
                  operating profit / available rooms) and, when RevPAR is given,
                  the GOP margin on revenue — so an occupancy/RevPAR "win" bought
                  with unprofitable cost is visible. GOPPAR is what keeps RevPAR
                  honest (CLAUDE.md §4 #1).

  channel-mix     The NET-ADR comparison across channels. Given each channel's
                  headline rate, OTA/channel commission %, and any per-booking
                  cost + loyalty/discount give-back, computes net ADR per channel
                  and the blended net ADR weighted by each channel's room share —
                  so channels are compared on contribution, not gross rate. Pairs
                  with price-on-net-adr-after-distribution (CLAUDE.md §4 #2).

This is a CALCULATOR, not a data source — it does not fetch rates, commissions,
PMS/RMS exports, or live demand. The user supplies every input; the tool does
the arithmetic and shows the formula. Stdlib only (argparse); runs anywhere
Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not financial, legal, or tax advice.
Validate every figure against the property's actual PMS/RMS and P&L data before
any deliverable. Commission and channel-cost figures are property- and
contract-specific — verify at use, never assume a market default.

Examples
--------
  # RevPAR from ADR x occupancy AND from room revenue / available rooms.
  # 140-room hotel, ADR $182, 85% occupancy, $21,658 room revenue last night.
  python3 hotel_calc.py revpar --adr 182 --occupancy 85% \\
      --room-revenue 21658 --available-rooms 140

  # GOPPAR: $640,000 GOP over a 140-room month (30 nights), RevPAR $154.70.
  python3 hotel_calc.py goppar --gop 640000 --available-rooms 140 \\
      --nights 30 --revpar 154.70

  # Channel mix net ADR: direct at $190 (no commission, $4 loyalty give-back,
  # 55% of rooms) vs Booking.com $190 at 18% commission (40%) vs GDS $185 at
  # 10% + $6/booking (5%).
  python3 hotel_calc.py channel-mix \\
      --channel "direct:190:0%:4:55%" \\
      --channel "booking.com:190:18%:0:40%" \\
      --channel "gds:185:10%:6:5%"
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '85%' or '0.85' into a fraction (0.85)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '85%' or '0.85', got {s!r}") from None


def cmd_revpar(args: argparse.Namespace) -> int:
    have_factors = args.adr is not None and args.occupancy is not None
    have_revenue = args.room_revenue is not None and args.available_rooms is not None
    if not have_factors and not have_revenue:
        print(
            "error: supply --adr + --occupancy, or --room-revenue + --available-rooms "
            "(both pairs to reconcile them)",
            file=sys.stderr,
        )
        return 2

    print("RevPAR — the north-star (revenue per available room)")
    revpar_factors = None
    revpar_revenue = None

    if have_factors:
        if args.adr <= 0:
            print("error: --adr must be > 0", file=sys.stderr)
            return 2
        if not 0.0 <= args.occupancy <= 1.0:
            print("error: --occupancy must be in [0%, 100%]", file=sys.stderr)
            return 2
        revpar_factors = args.adr * args.occupancy
        print(f"  ADR                    : {args.adr:,.2f}")
        print(f"  occupancy              : {args.occupancy * 100:.1f}%")
        print(f"  → RevPAR (ADR × Occ)   : {revpar_factors:,.2f}")

    if have_revenue:
        if args.available_rooms <= 0:
            print("error: --available-rooms must be > 0", file=sys.stderr)
            return 2
        revpar_revenue = args.room_revenue / args.available_rooms
        print(f"  room revenue           : {args.room_revenue:,.2f}")
        print(f"  available rooms        : {args.available_rooms:g}")
        print(f"  → RevPAR (Rev ÷ Avail) : {revpar_revenue:,.2f}")
        if args.rooms_sold is not None and args.rooms_sold > 0:
            implied_adr = args.room_revenue / args.rooms_sold
            implied_occ = args.rooms_sold / args.available_rooms
            print(f"  implied ADR            : {implied_adr:,.2f}   = revenue ÷ {args.rooms_sold:g} sold")
            print(f"  implied occupancy      : {implied_occ * 100:.1f}%   = {args.rooms_sold:g} sold ÷ avail")

    if revpar_factors is not None and revpar_revenue is not None:
        gap = abs(revpar_factors - revpar_revenue)
        print()
        if gap <= 0.01:
            print("  ✓ the two RevPAR computations agree — inputs are consistent.")
        else:
            print(f"  ⚠ the two RevPAR computations differ by {gap:,.2f} — an input is off")
            print("    (check ADR, occupancy, revenue, or the available-room count).")
    print()
    print("  note: RevPAR is the north-star, but read it against GOPPAR — an occupancy")
    print("        or ADR win that lowers RevPAR, or a RevPAR win that lowers GOPPAR, is")
    print("        a loss (CLAUDE.md §4 #1). Run `goppar` next.")
    return 0


def cmd_goppar(args: argparse.Namespace) -> int:
    if args.available_rooms <= 0:
        print("error: --available-rooms must be > 0", file=sys.stderr)
        return 2
    if args.nights <= 0:
        print("error: --nights must be > 0", file=sys.stderr)
        return 2
    available_room_nights = args.available_rooms * args.nights
    goppar = args.gop / available_room_nights

    print("GOPPAR — the profit check on a RevPAR strategy")
    print(f"  gross operating profit : {args.gop:,.2f}")
    print(f"  available rooms        : {args.available_rooms:g}")
    print(f"  nights in window       : {args.nights:g}")
    print(f"  available room-nights  : {available_room_nights:,.0f}")
    print(f"  → GOPPAR               : {goppar:,.2f}   = GOP ÷ available room-nights")

    if args.revpar is not None:
        if args.revpar <= 0:
            print("error: --revpar must be > 0", file=sys.stderr)
            return 2
        flow_through = goppar / args.revpar
        print(f"  RevPAR (for the window): {args.revpar:,.2f}")
        print(f"  → GOPPAR ÷ RevPAR       : {flow_through * 100:.1f}%  (profit kept per RevPAR dollar)")
        print()
        if flow_through < 0:
            print("  ⚠ GOPPAR is NEGATIVE while RevPAR is positive — this revenue is being")
            print("    bought with unprofitable cost. A RevPAR win here is a loss (§4 #1).")
        elif flow_through < 0.30:
            print("  ⚠ low flow-through — RevPAR dollars aren't converting to profit. Check")
            print("    distribution cost and the labor line before chasing more occupancy (§4 #1).")
        else:
            print("  read: RevPAR is converting to profit at a healthy rate for the window.")
    print()
    print("  note: GOPPAR is what keeps RevPAR honest — never optimize RevPAR without it.")
    print("        Validate GOP against the actual P&L; departmental cost allocation matters.")
    return 0


def _parse_channel(spec: str) -> dict:
    """Parse 'name:rate:commission:givebak:share' into a channel dict."""
    parts = spec.split(":")
    if len(parts) != 5:
        raise argparse.ArgumentTypeError(
            f"channel must be name:rate:commission:giveback:share, got {spec!r}"
        )
    name, rate_s, comm_s, give_s, share_s = parts
    try:
        rate = float(rate_s)
        giveback = float(give_s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"rate and giveback must be numbers in {spec!r}") from None
    commission = _parse_rate(comm_s)
    share = _parse_rate(share_s)
    return {
        "name": name.strip(),
        "rate": rate,
        "commission": commission,
        "giveback": giveback,
        "share": share,
    }


def cmd_channel_mix(args: argparse.Namespace) -> int:
    channels = args.channel
    for ch in channels:
        if ch["rate"] <= 0:
            print(f"error: rate for {ch['name']!r} must be > 0", file=sys.stderr)
            return 2
        if not 0.0 <= ch["commission"] < 1.0:
            print(f"error: commission for {ch['name']!r} must be in [0%, 100%)", file=sys.stderr)
            return 2

    total_share = sum(ch["share"] for ch in channels)

    print("Channel mix — net ADR after distribution (contribution, not gross)")
    print(f"  {'channel':<16}{'rate':>9}{'comm%':>8}{'give':>8}{'net ADR':>10}{'share':>8}")
    blended = 0.0
    for ch in channels:
        net = ch["rate"] * (1.0 - ch["commission"]) - ch["giveback"]
        ch["net"] = net
        blended += net * ch["share"]
        print(
            f"  {ch['name']:<16}{ch['rate']:>9,.2f}{ch['commission'] * 100:>7.1f}%"
            f"{ch['giveback']:>8,.2f}{net:>10,.2f}{ch['share'] * 100:>7.1f}%"
        )
    print()
    if abs(total_share - 1.0) > 0.005:
        print(f"  ⚠ channel shares sum to {total_share * 100:.1f}%, not 100% — blended net ADR")
        print("    is share-weighted as given; normalize the shares for a true blend.")
    blended_norm = blended / total_share if total_share > 0 else 0.0
    print(f"  → blended net ADR (as given)     : {blended:,.2f}")
    if abs(total_share - 1.0) > 0.005 and total_share > 0:
        print(f"  → blended net ADR (normalized)   : {blended_norm:,.2f}")

    best = max(channels, key=lambda c: c["net"])
    worst = min(channels, key=lambda c: c["net"])
    print()
    print(f"  best net ADR  : {best['name']} at {best['net']:,.2f}")
    print(f"  worst net ADR : {worst['name']} at {worst['net']:,.2f}")
    spread = best["net"] - worst["net"]
    print(f"  spread        : {spread:,.2f} per booking between best and worst channel")
    print()
    print("  note: compare channels on NET ADR, never headline rate (§4 #2). Drive direct")
    print("        share to cut distribution cost, but never strand demand the OTA uniquely")
    print("        reaches — the OTA is a paid acquisition channel with a known cost.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hotel_calc.py",
        description="Hotel rooms-revenue decision calculator (stdlib only). "
        "Decision-support, not financial/legal/tax advice — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    rp = sub.add_parser("revpar", help="RevPAR from ADR×Occ and from revenue÷available rooms")
    rp.add_argument("--adr", type=float, default=None, help="average daily rate")
    rp.add_argument("--occupancy", type=_parse_rate, default=None, help="occupancy (e.g. 85%% or 0.85)")
    rp.add_argument("--room-revenue", type=float, default=None, help="room revenue for the window")
    rp.add_argument("--available-rooms", type=float, default=None, help="available rooms (or room-nights)")
    rp.add_argument("--rooms-sold", type=float, default=None, help="rooms sold (optional, for implied ADR/Occ)")
    rp.set_defaults(func=cmd_revpar)

    gp = sub.add_parser("goppar", help="GOP per available room, the profit check on RevPAR")
    gp.add_argument("--gop", type=float, required=True, help="gross operating profit for the window")
    gp.add_argument("--available-rooms", type=float, required=True, help="available rooms in the property")
    gp.add_argument("--nights", type=float, default=1.0, help="nights in the window (default 1)")
    gp.add_argument("--revpar", type=float, default=None, help="RevPAR for the window (optional flow-through)")
    gp.set_defaults(func=cmd_goppar)

    cm = sub.add_parser("channel-mix", help="Net ADR per channel after commission + blended mix")
    cm.add_argument(
        "--channel",
        action="append",
        required=True,
        type=_parse_channel,
        metavar="name:rate:commission:giveback:share",
        help="one per channel, e.g. 'booking.com:190:18%%:0:40%%' (repeatable)",
    )
    cm.set_defaults(func=cmd_channel_mix)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
