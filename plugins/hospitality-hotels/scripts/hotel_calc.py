#!/usr/bin/env python3
"""hotel_calc.py - a zero-dependency hotel revenue calculator.

Removes arithmetic error from six recurring hotel revenue and operations decisions:

  revpar           Revenue Per Available Room — two methods:
                   (1) ADR x occupancy %  (2) Total room revenue / available rooms.
                   Both should agree; if they don't, one of your inputs is wrong.

  adr              Average Daily Rate: total room revenue / rooms sold. Also runs
                   in reverse: given RevPAR and occupancy, solve for ADR.

  occupancy        Occupancy percentage: rooms sold / rooms available. Also runs
                   in reverse: given RevPAR and ADR, solve for occupancy %.

  goppar           Gross Operating Profit Per Available Room: GOP / available rooms.
                   Shows cost discipline behind the RevPAR headline. Requires
                   total revenue, total departmental expenses, and undistributed
                   operating expenses (USALI framing).

  net-adr          Net ADR after OTA commission and per-transaction fees:
                   Net ADR = Gross ADR x (1 - commission rate) - per-transaction fees.
                   The number the hotel actually captures from an OTA booking.

  displacement     RevPAR displacement analysis for a length-of-stay (LOS) restriction
                   (MinLOS) or overbooking decision:
                   Compares the RevPAR of the restricted scenario vs the unrestricted
                   baseline so you can decide whether the restriction or overbook is
                   RevPAR-positive.

This is a CALCULATOR, not a data source. It does not fetch benchmarks, OTA commission
rates, or market data. The user supplies every input; the tool does the arithmetic and
shows the formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not accounting, audit, tax, or investment
advice. Source-cite every input and validate against the property's actual data before
any deliverable.

Examples
--------
  # RevPAR: 180-room hotel, $145 ADR, 78% occupancy
  python3 hotel_calc.py revpar --adr 145 --occupancy 78%

  # RevPAR by revenue: $24,000 room revenue, 200 available rooms
  python3 hotel_calc.py revpar --revenue 24000 --available-rooms 200

  # ADR: $36,000 room revenue, 200 rooms sold
  python3 hotel_calc.py adr --revenue 36000 --rooms-sold 200

  # ADR from RevPAR and occupancy: RevPAR $112, occupancy 70%
  python3 hotel_calc.py adr --revpar 112 --occupancy 70%

  # Occupancy: 140 rooms sold, 180 available
  python3 hotel_calc.py occupancy --rooms-sold 140 --available-rooms 180

  # GOPPAR: $850,000 total revenue, $420,000 dept expenses, $175,000 undistributed, 180 rooms, 30 days
  python3 hotel_calc.py goppar --total-revenue 850000 --dept-expenses 420000 \\
      --undistributed 175000 --available-rooms 180 --days 30

  # Net ADR after OTA commission: $185 gross ADR, 18% commission
  python3 hotel_calc.py net-adr --gross-adr 185 --commission 18%

  # Net ADR with per-transaction fee: $185 gross, 18% commission, $3 fee
  python3 hotel_calc.py net-adr --gross-adr 185 --commission 18% --fee 3

  # Displacement: MinLOS decision — restricted vs. unrestricted RevPAR
  python3 hotel_calc.py displacement --restricted-adr 220 --restricted-occ 68% \\
      --unrestricted-adr 175 --unrestricted-occ 88%
"""

from __future__ import annotations

import argparse
import sys


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def _parse_pct(s: str) -> float:
    """Parse a percentage like '78%' or '0.78' into a fraction (0.78)."""
    s = s.strip()
    try:
        if s.endswith("%"):
            val = float(s[:-1])
            if not (0.0 <= val <= 100.0):
                raise argparse.ArgumentTypeError(
                    f"percentage out of range [0,100]: {s!r}"
                )
            return val / 100.0
        val = float(s)
        # Accept fractions like 0.78 directly
        if 0.0 <= val <= 1.0:
            return val
        raise argparse.ArgumentTypeError(
            f"must be like '78%' or '0.78', got {s!r}"
        )
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"must be like '78%' or '0.78', got {s!r}"
        )


def _fmt(value: float, prefix: str = "$") -> str:
    """Format a dollar value to 2 decimal places."""
    return f"{prefix}{value:,.2f}"


def _fmt_pct(value: float) -> str:
    """Format a fraction (0.78) as a percentage string '78.00%'."""
    return f"{value * 100:.2f}%"


# ---------------------------------------------------------------------------
# Core calculation functions
# ---------------------------------------------------------------------------


def calc_revpar(
    adr: float | None = None,
    occupancy: float | None = None,
    revenue: float | None = None,
    available_rooms: int | None = None,
) -> dict:
    """
    Compute RevPAR via either method:
    - Method 1: ADR * occupancy
    - Method 2: total room revenue / available rooms
    Returns a dict with result and formula used.
    """
    results = {}
    if adr is not None and occupancy is not None:
        revpar = adr * occupancy
        results["method1"] = {
            "revpar": revpar,
            "formula": f"ADR ({_fmt(adr)}) × occupancy ({_fmt_pct(occupancy)}) = {_fmt(revpar)}",
        }
    if revenue is not None and available_rooms is not None:
        if available_rooms <= 0:
            raise ValueError("available-rooms must be > 0")
        revpar = revenue / available_rooms
        results["method2"] = {
            "revpar": revpar,
            "formula": (
                f"Room revenue ({_fmt(revenue)}) ÷ available rooms ({available_rooms}) "
                f"= {_fmt(revpar)}"
            ),
        }
    if not results:
        raise ValueError(
            "Provide --adr + --occupancy (method 1) and/or "
            "--revenue + --available-rooms (method 2)."
        )
    return results


def calc_adr(
    revenue: float | None = None,
    rooms_sold: int | None = None,
    revpar: float | None = None,
    occupancy: float | None = None,
) -> dict:
    """
    Compute ADR.
    - Method 1: total room revenue / rooms sold
    - Method 2 (reverse): RevPAR / occupancy
    """
    results = {}
    if revenue is not None and rooms_sold is not None:
        if rooms_sold <= 0:
            raise ValueError("rooms-sold must be > 0")
        adr = revenue / rooms_sold
        results["method1"] = {
            "adr": adr,
            "formula": (
                f"Room revenue ({_fmt(revenue)}) ÷ rooms sold ({rooms_sold}) = {_fmt(adr)}"
            ),
        }
    if revpar is not None and occupancy is not None:
        if occupancy <= 0:
            raise ValueError("occupancy must be > 0")
        adr = revpar / occupancy
        results["method2"] = {
            "adr": adr,
            "formula": (
                f"RevPAR ({_fmt(revpar)}) ÷ occupancy ({_fmt_pct(occupancy)}) = {_fmt(adr)}"
            ),
        }
    if not results:
        raise ValueError(
            "Provide --revenue + --rooms-sold (method 1) or "
            "--revpar + --occupancy (reverse solve)."
        )
    return results


def calc_occupancy(
    rooms_sold: int | None = None,
    available_rooms: int | None = None,
    revpar: float | None = None,
    adr: float | None = None,
) -> dict:
    """
    Compute occupancy %.
    - Method 1: rooms sold / available rooms
    - Method 2 (reverse): RevPAR / ADR
    """
    results = {}
    if rooms_sold is not None and available_rooms is not None:
        if available_rooms <= 0:
            raise ValueError("available-rooms must be > 0")
        occ = rooms_sold / available_rooms
        results["method1"] = {
            "occupancy": occ,
            "formula": (
                f"Rooms sold ({rooms_sold}) ÷ available rooms ({available_rooms}) "
                f"= {_fmt_pct(occ)}"
            ),
        }
    if revpar is not None and adr is not None:
        if adr <= 0:
            raise ValueError("adr must be > 0")
        occ = revpar / adr
        results["method2"] = {
            "occupancy": occ,
            "formula": (
                f"RevPAR ({_fmt(revpar)}) ÷ ADR ({_fmt(adr)}) = {_fmt_pct(occ)}"
            ),
        }
    if not results:
        raise ValueError(
            "Provide --rooms-sold + --available-rooms (method 1) or "
            "--revpar + --adr (reverse solve)."
        )
    return results


def calc_goppar(
    total_revenue: float,
    dept_expenses: float,
    undistributed: float,
    available_rooms: int,
    days: int = 1,
) -> dict:
    """
    Compute GOPPAR (Gross Operating Profit Per Available Room).
    GOP = Total Revenue - Departmental Expenses - Undistributed Operating Expenses
    GOPPAR = GOP / (available_rooms * days)
    """
    if available_rooms <= 0:
        raise ValueError("available-rooms must be > 0")
    if days <= 0:
        raise ValueError("days must be > 0")
    gop = total_revenue - dept_expenses - undistributed
    gop_pct = (gop / total_revenue * 100) if total_revenue > 0 else 0.0
    available_room_nights = available_rooms * days
    goppar = gop / available_room_nights
    return {
        "total_revenue": total_revenue,
        "dept_expenses": dept_expenses,
        "undistributed": undistributed,
        "gop": gop,
        "gop_pct": gop_pct,
        "available_room_nights": available_room_nights,
        "goppar": goppar,
        "formula": (
            f"GOP = Revenue ({_fmt(total_revenue)}) − Dept expenses ({_fmt(dept_expenses)}) "
            f"− Undistributed ({_fmt(undistributed)}) = {_fmt(gop)} ({gop_pct:.1f}% GOP%)\n"
            f"GOPPAR = GOP ({_fmt(gop)}) ÷ available room-nights "
            f"({available_rooms} rooms × {days} days = {available_room_nights}) = {_fmt(goppar)}"
        ),
    }


def calc_net_adr(
    gross_adr: float,
    commission: float,
    fee: float = 0.0,
) -> dict:
    """
    Compute net ADR after OTA commission and optional per-transaction fee.
    Net ADR = Gross ADR * (1 - commission) - fee
    """
    if not (0.0 <= commission < 1.0):
        raise ValueError("commission must be a fraction in [0, 1) e.g. 0.18 for 18%")
    net_adr = gross_adr * (1.0 - commission) - fee
    commission_dollars = gross_adr * commission
    return {
        "gross_adr": gross_adr,
        "commission_rate": commission,
        "commission_dollars": commission_dollars,
        "fee": fee,
        "net_adr": net_adr,
        "formula": (
            f"Net ADR = Gross ADR ({_fmt(gross_adr)}) × (1 − {commission * 100:.1f}%) "
            f"− fee ({_fmt(fee)}) = {_fmt(net_adr)}\n"
            f"Commission cost: {_fmt(commission_dollars)} per booking"
        ),
    }


def calc_displacement(
    restricted_adr: float,
    restricted_occ: float,
    unrestricted_adr: float,
    unrestricted_occ: float,
) -> dict:
    """
    Compare RevPAR of a restricted scenario (e.g., MinLOS or overbook policy applied)
    vs. the unrestricted baseline.

    Restricted scenario: e.g., MinLOS applied → higher ADR but lower occupancy
    Unrestricted: baseline ADR × baseline occupancy

    Returns the RevPAR delta and whether the restriction is RevPAR-positive.
    """
    revpar_restricted = restricted_adr * restricted_occ
    revpar_unrestricted = unrestricted_adr * unrestricted_occ
    delta = revpar_restricted - revpar_unrestricted
    is_positive = delta > 0
    return {
        "restricted": {
            "adr": restricted_adr,
            "occupancy": restricted_occ,
            "revpar": revpar_restricted,
        },
        "unrestricted": {
            "adr": unrestricted_adr,
            "occupancy": unrestricted_occ,
            "revpar": revpar_unrestricted,
        },
        "delta": delta,
        "is_revpar_positive": is_positive,
        "verdict": "RESTRICTION IS RevPAR-POSITIVE" if is_positive else "RESTRICTION IS NOT RevPAR-POSITIVE — hold the baseline",
        "formula": (
            f"Restricted RevPAR = ADR ({_fmt(restricted_adr)}) × occ ({_fmt_pct(restricted_occ)}) "
            f"= {_fmt(revpar_restricted)}\n"
            f"Unrestricted RevPAR = ADR ({_fmt(unrestricted_adr)}) × occ ({_fmt_pct(unrestricted_occ)}) "
            f"= {_fmt(revpar_unrestricted)}\n"
            f"Delta = {_fmt(delta, prefix='' if delta < 0 else '$').replace('$-', '-$')} per available room"
        ),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hotel_calc.py",
        description="Hotel revenue calculator — RevPAR, ADR, occupancy, GOPPAR, net ADR, displacement.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    # revpar
    p_revpar = sub.add_parser("revpar", help="Revenue Per Available Room")
    p_revpar.add_argument("--adr", type=float, help="Average Daily Rate ($)")
    p_revpar.add_argument("--occupancy", type=_parse_pct, help="Occupancy % (e.g. 78%% or 0.78)")
    p_revpar.add_argument("--revenue", type=float, help="Total room revenue ($)")
    p_revpar.add_argument("--available-rooms", type=int, help="Number of available rooms")

    # adr
    p_adr = sub.add_parser("adr", help="Average Daily Rate")
    p_adr.add_argument("--revenue", type=float, help="Total room revenue ($)")
    p_adr.add_argument("--rooms-sold", type=int, help="Number of rooms sold")
    p_adr.add_argument("--revpar", type=float, help="RevPAR (for reverse solve)")
    p_adr.add_argument("--occupancy", type=_parse_pct, help="Occupancy % (for reverse solve)")

    # occupancy
    p_occ = sub.add_parser("occupancy", help="Occupancy percentage")
    p_occ.add_argument("--rooms-sold", type=int, help="Rooms sold")
    p_occ.add_argument("--available-rooms", type=int, help="Available rooms")
    p_occ.add_argument("--revpar", type=float, help="RevPAR (for reverse solve)")
    p_occ.add_argument("--adr", type=float, help="ADR (for reverse solve)")

    # goppar
    p_gop = sub.add_parser("goppar", help="Gross Operating Profit Per Available Room")
    p_gop.add_argument("--total-revenue", type=float, required=True, help="Total hotel revenue ($)")
    p_gop.add_argument("--dept-expenses", type=float, required=True, help="Total departmental expenses ($)")
    p_gop.add_argument("--undistributed", type=float, required=True, help="Undistributed operating expenses ($)")
    p_gop.add_argument("--available-rooms", type=int, required=True, help="Number of available rooms")
    p_gop.add_argument("--days", type=int, default=1, help="Number of days in the period (default: 1)")

    # net-adr
    p_net = sub.add_parser("net-adr", help="Net ADR after OTA commission")
    p_net.add_argument("--gross-adr", type=float, required=True, help="Gross ADR ($)")
    p_net.add_argument("--commission", type=_parse_pct, required=True, help="Commission rate (e.g. 18%% or 0.18)")
    p_net.add_argument("--fee", type=float, default=0.0, help="Per-transaction fee ($, default 0)")

    # displacement
    p_dis = sub.add_parser("displacement", help="RevPAR displacement / LOS control analysis")
    p_dis.add_argument("--restricted-adr", type=float, required=True, help="ADR under restriction ($)")
    p_dis.add_argument("--restricted-occ", type=_parse_pct, required=True, help="Occupancy under restriction")
    p_dis.add_argument("--unrestricted-adr", type=float, required=True, help="Baseline ADR ($)")
    p_dis.add_argument("--unrestricted-occ", type=_parse_pct, required=True, help="Baseline occupancy")

    return parser


def run(args: argparse.Namespace) -> None:  # noqa: C901
    if args.mode == "revpar":
        results = calc_revpar(
            adr=args.adr,
            occupancy=args.occupancy,
            revenue=args.revenue,
            available_rooms=args.available_rooms,
        )
        print("=== RevPAR ===")
        for method, r in results.items():
            print(f"  {method}: {r['formula']}")
        if len(results) == 2:
            v1 = results["method1"]["revpar"]
            v2 = results["method2"]["revpar"]
            diff = abs(v1 - v2)
            note = "✓ consistent" if diff < 0.01 else f"⚠ discrepancy of {_fmt(diff)} — check inputs"
            print(f"  Consistency check: {note}")

    elif args.mode == "adr":
        results = calc_adr(
            revenue=args.revenue,
            rooms_sold=args.rooms_sold,
            revpar=args.revpar,
            occupancy=args.occupancy,
        )
        print("=== ADR ===")
        for method, r in results.items():
            print(f"  {method}: {r['formula']}")

    elif args.mode == "occupancy":
        results = calc_occupancy(
            rooms_sold=args.rooms_sold,
            available_rooms=args.available_rooms,
            revpar=args.revpar,
            adr=args.adr,
        )
        print("=== Occupancy ===")
        for method, r in results.items():
            print(f"  {method}: {r['formula']}")

    elif args.mode == "goppar":
        r = calc_goppar(
            total_revenue=args.total_revenue,
            dept_expenses=args.dept_expenses,
            undistributed=args.undistributed,
            available_rooms=args.available_rooms,
            days=args.days,
        )
        print("=== GOPPAR (USALI framing) ===")
        print(f"  {r['formula']}")

    elif args.mode == "net-adr":
        r = calc_net_adr(
            gross_adr=args.gross_adr,
            commission=args.commission,
            fee=args.fee,
        )
        print("=== Net ADR after OTA Commission ===")
        print(f"  {r['formula']}")

    elif args.mode == "displacement":
        r = calc_displacement(
            restricted_adr=args.restricted_adr,
            restricted_occ=args.restricted_occ,
            unrestricted_adr=args.unrestricted_adr,
            unrestricted_occ=args.unrestricted_occ,
        )
        print("=== Displacement / LOS Control Analysis ===")
        print(f"  {r['formula']}")
        print(f"  Verdict: {r['verdict']}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        run(args)
    except (ValueError, argparse.ArgumentTypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Self-test (run as: python3 hotel_calc.py or via __main__)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    # If command-line arguments are provided, run the CLI normally.
    if len(sys.argv) > 1:
        main()
        sys.exit(0)

    # Otherwise, run the self-test suite.
    print("=== hotel_calc.py self-test ===\n")

    # Test 1: RevPAR method 1 (ADR × occupancy)
    r = calc_revpar(adr=145.00, occupancy=0.78)
    assert abs(r["method1"]["revpar"] - 113.10) < 0.01, f"RevPAR method1 fail: {r}"
    print(f"Test 1 — RevPAR (method 1): {r['method1']['formula']}")

    # Test 2: RevPAR method 2 (revenue / available rooms)
    r = calc_revpar(revenue=24000.0, available_rooms=200)
    assert abs(r["method2"]["revpar"] - 120.00) < 0.01, f"RevPAR method2 fail: {r}"
    print(f"Test 2 — RevPAR (method 2): {r['method2']['formula']}")

    # Test 3: ADR from revenue / rooms sold
    r = calc_adr(revenue=36000.0, rooms_sold=200)
    assert abs(r["method1"]["adr"] - 180.00) < 0.01, f"ADR method1 fail: {r}"
    print(f"Test 3 — ADR (method 1): {r['method1']['formula']}")

    # Test 4: ADR reverse solve from RevPAR / occupancy
    r = calc_adr(revpar=112.00, occupancy=0.70)
    assert abs(r["method2"]["adr"] - 160.00) < 0.01, f"ADR method2 fail: {r}"
    print(f"Test 4 — ADR (reverse solve): {r['method2']['formula']}")

    # Test 5: Occupancy %
    r = calc_occupancy(rooms_sold=140, available_rooms=180)
    assert abs(r["method1"]["occupancy"] - (140 / 180)) < 0.0001, f"Occupancy fail: {r}"
    print(f"Test 5 — Occupancy: {r['method1']['formula']}")

    # Test 6: Occupancy reverse solve from RevPAR / ADR
    r = calc_occupancy(revpar=112.00, adr=160.00)
    assert abs(r["method2"]["occupancy"] - 0.70) < 0.0001, f"Occupancy reverse fail: {r}"
    print(f"Test 6 — Occupancy (reverse solve): {r['method2']['formula']}")

    # Test 7: GOPPAR
    r = calc_goppar(
        total_revenue=850_000,
        dept_expenses=420_000,
        undistributed=175_000,
        available_rooms=180,
        days=30,
    )
    expected_gop = 850_000 - 420_000 - 175_000  # 255,000
    expected_goppar = expected_gop / (180 * 30)  # 255,000 / 5,400 = 47.22...
    assert abs(r["gop"] - expected_gop) < 0.01, f"GOP fail: {r}"
    assert abs(r["goppar"] - expected_goppar) < 0.01, f"GOPPAR fail: {r}"
    print(f"Test 7 — GOPPAR: {r['formula']}")

    # Test 8: Net ADR — 18% commission, no fee
    r = calc_net_adr(gross_adr=185.00, commission=0.18)
    expected = 185.00 * (1 - 0.18)  # 151.70
    assert abs(r["net_adr"] - expected) < 0.01, f"Net ADR fail: {r}"
    print(f"Test 8 — Net ADR (no fee): {r['formula']}")

    # Test 9: Net ADR — 18% commission + $3 fee
    r = calc_net_adr(gross_adr=185.00, commission=0.18, fee=3.00)
    expected = 185.00 * (1 - 0.18) - 3.00  # 148.70
    assert abs(r["net_adr"] - expected) < 0.01, f"Net ADR with fee fail: {r}"
    print(f"Test 9 — Net ADR (with fee): {r['formula']}")

    # Test 10: Displacement — restriction IS RevPAR-positive
    # Restricted: $240 ADR × 72% occ = $172.80 RevPAR
    # Unrestricted: $175 ADR × 88% occ = $154.00 RevPAR → restriction is +$18.80
    r = calc_displacement(
        restricted_adr=240.0,
        restricted_occ=0.72,
        unrestricted_adr=175.0,
        unrestricted_occ=0.88,
    )
    assert r["is_revpar_positive"] is True, f"Displacement positive fail: {r}"
    print(f"Test 10 — Displacement (positive): {r['formula']}")
    print(f"          Verdict: {r['verdict']}")

    # Test 11: Displacement — restriction is NOT RevPAR-positive
    # Restricted: $200 ADR × 55% occ = $110.00 RevPAR
    # Unrestricted: $160 ADR × 90% occ = $144.00 RevPAR → restriction is -$34.00
    r = calc_displacement(
        restricted_adr=200.0,
        restricted_occ=0.55,
        unrestricted_adr=160.0,
        unrestricted_occ=0.90,
    )
    assert r["is_revpar_positive"] is False, f"Displacement negative fail: {r}"
    print(f"Test 11 — Displacement (not positive): {r['formula']}")
    print(f"          Verdict: {r['verdict']}")

    print("\n=== All self-tests passed ===")
