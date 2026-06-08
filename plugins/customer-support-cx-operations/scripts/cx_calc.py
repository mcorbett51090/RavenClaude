#!/usr/bin/env python3
"""
cx_calc.py — stdlib-only CX operations calculator for customer-support-cx-operations.

Modes (call with: python3 cx_calc.py <mode> [args]):
  erlang-c         Erlang C: minimum agents for a target service level, plus occupancy.
  occupancy        Occupancy at a given agents/volume/AHT combination.
  deflection-roi   Deflection ROI: annual savings from deflecting a contact volume.
  csat-ces         CSAT% and CES% from raw rating counts.
  shrinkage-fte    Shrinkage-adjusted FTE from a raw agent count and shrinkage rate.

All inputs are positional; run with --help or no args for usage.

This is a calculator, not a data source. The caller supplies every input.
Outputs are decision-support, not staffing, legal, or financial advice.
"""

import math
import sys
from typing import List, Optional


# ---------------------------------------------------------------------------
# Core Erlang C mathematics
# ---------------------------------------------------------------------------


def _erlang_c_probability(agents: int, traffic_intensity: float) -> float:
    """
    Erlang C formula: probability that an arriving call must wait.

    agents            (N) number of agents (servers)
    traffic_intensity (A) = arrival_rate * mean_service_time
                          = (contacts_per_interval / interval_seconds) * AHT_seconds

    Returns P(wait) in [0, 1]. Returns 1.0 if traffic_intensity >= agents
    (the queue is unstable; adding more agents is required).
    """
    if traffic_intensity <= 0:
        return 0.0
    if traffic_intensity >= agents:
        # Unstable queue — occupancy >= 100%
        return 1.0

    # Numerator: (A^N / N!) * (N / (N - A))
    # Denominator: sum_{k=0}^{N-1} A^k/k!  +  numerator
    # Use log-space arithmetic to avoid overflow for large N.

    # log of the numerator term A^N / N! * N/(N-A)
    log_num = agents * math.log(traffic_intensity) - math.lgamma(agents + 1) + math.log(
        agents / (agents - traffic_intensity)
    )

    # log of each Poisson term A^k / k!
    # sum_{k=0}^{N-1} exp(k*log(A) - lgamma(k+1))
    sum_terms = 0.0
    log_ak_over_kfact = 0.0  # starts at k=0: A^0/0! = 1
    for k in range(agents):
        if k == 0:
            sum_terms += 1.0
        else:
            log_ak_over_kfact += math.log(traffic_intensity) - math.log(k)
            sum_terms += math.exp(log_ak_over_kfact)

    numerator = math.exp(log_num)
    denominator = sum_terms + numerator

    return numerator / denominator


def erlang_c(
    contacts_per_interval: float,
    aht_seconds: float,
    interval_seconds: float,
    target_sl_pct: float,
    target_sl_seconds: float,
    max_agents: int = 500,
) -> dict:
    """
    Find the minimum number of agents to meet a service-level target.

    contacts_per_interval  contacts arriving in the interval (e.g. 100 contacts/30min)
    aht_seconds            average handle time in seconds (talk + wrap)
    interval_seconds       interval length in seconds (e.g. 1800 for 30-minute intervals)
    target_sl_pct          target % of contacts answered within threshold (e.g. 0.80 for 80%)
    target_sl_seconds      answer threshold in seconds (e.g. 20 for "within 20 seconds")
    max_agents             upper search bound (default 500)

    Returns dict with:
      agents_needed        minimum agents to meet SL target
      service_level        actual SL at agents_needed
      occupancy            occupancy at agents_needed
      traffic_intensity    A = arrival_rate * AHT (Erlangs)
      warning              advisory string if occupancy is above safe range
    """
    if contacts_per_interval <= 0 or aht_seconds <= 0:
        raise ValueError("contacts_per_interval and aht_seconds must be positive.")

    arrival_rate = contacts_per_interval / interval_seconds  # contacts per second
    traffic_intensity = arrival_rate * aht_seconds  # Erlangs (A)

    # Minimum agents must be > traffic_intensity for a stable queue
    min_agents = max(1, math.ceil(traffic_intensity) + 1)

    result_agents = None
    result_sl = 0.0

    for n in range(min_agents, max_agents + 1):
        pw = _erlang_c_probability(n, traffic_intensity)
        # P(wait > t) = Erlang-C(n, A) * exp(-(n - A) * t / AHT)
        # SL = 1 - P(wait > t)
        sl = 1.0 - pw * math.exp(-(n - traffic_intensity) * target_sl_seconds / aht_seconds)
        if sl >= target_sl_pct:
            result_agents = n
            result_sl = sl
            break

    if result_agents is None:
        result_agents = max_agents
        pw = _erlang_c_probability(max_agents, traffic_intensity)
        result_sl = 1.0 - pw * math.exp(
            -(max_agents - traffic_intensity) * target_sl_seconds / aht_seconds
        )

    occupancy = traffic_intensity / result_agents  # fraction, e.g. 0.82

    warning = ""
    if occupancy > 0.90:
        warning = (
            f"OCCUPANCY WARNING: {occupancy:.1%} exceeds 90% — queue dynamics are highly unstable. "
            "Add agents immediately."
        )
    elif occupancy > 0.85:
        warning = (
            f"OCCUPANCY CAUTION: {occupancy:.1%} is above the 85% quality-safe ceiling for "
            "voice/real-time channels. Consider adding 1–2 agents."
        )

    return {
        "agents_needed": result_agents,
        "service_level": round(result_sl, 4),
        "occupancy": round(occupancy, 4),
        "traffic_intensity_erlangs": round(traffic_intensity, 3),
        "warning": warning,
    }


# ---------------------------------------------------------------------------
# Occupancy
# ---------------------------------------------------------------------------


def occupancy(
    contacts_per_interval: float,
    aht_seconds: float,
    agents: int,
    interval_seconds: float,
) -> dict:
    """
    Calculate occupancy for a given staffing level.

    occupancy = (arrival_rate * AHT) / agents
              = (contacts_per_interval * AHT_seconds) / (agents * interval_seconds)

    Returns dict with occupancy (fraction), occupancy_pct (string), and a warning if above target.
    """
    if agents <= 0:
        raise ValueError("agents must be positive.")
    occ = (contacts_per_interval * aht_seconds) / (agents * interval_seconds)
    warning = ""
    if occ > 0.90:
        warning = "Above 90% — queue is unstable; quality and burnout risk are high."
    elif occ > 0.85:
        warning = "Above 85% ceiling for voice/real-time; consider adding agents."
    return {
        "occupancy": round(occ, 4),
        "occupancy_pct": f"{occ:.1%}",
        "warning": warning,
    }


# ---------------------------------------------------------------------------
# Deflection ROI
# ---------------------------------------------------------------------------


def deflection_roi(
    deflectable_contacts_per_year: float,
    cost_per_contact: float,
    containment_rate: float,
    content_investment: float = 0.0,
) -> dict:
    """
    Annual deflection ROI.

    deflectable_contacts_per_year  contacts that could be self-served
    cost_per_contact               fully-loaded cost per agent-handled contact
    containment_rate               expected fraction of deflectable contacts the KB/bot resolves
                                   (0.0–1.0, e.g. 0.70 for 70% containment)
    content_investment             one-time investment to build the content (optional, default 0)

    Returns dict with: deflected_contacts, gross_savings, net_savings, payback_months.
    """
    if not (0.0 <= containment_rate <= 1.0):
        raise ValueError("containment_rate must be between 0 and 1.")
    deflected = deflectable_contacts_per_year * containment_rate
    gross_savings = deflected * cost_per_contact
    net_savings = gross_savings - content_investment
    payback_months = (
        (content_investment / (gross_savings / 12)) if gross_savings > 0 and content_investment > 0 else 0.0
    )
    return {
        "deflected_contacts": round(deflected),
        "gross_annual_savings": round(gross_savings, 2),
        "net_annual_savings": round(net_savings, 2),
        "payback_months": round(payback_months, 1),
    }


# ---------------------------------------------------------------------------
# CSAT and CES
# ---------------------------------------------------------------------------


def csat_ces(
    ratings: List[int],
    scale: int = 5,
    positive_threshold: Optional[int] = None,
) -> dict:
    """
    Calculate CSAT% or CES% from a list of raw ratings.

    For CSAT (scale=5): CSAT% = (count of 4s and 5s) / total
    For CSAT (scale=10): CSAT% = (count of 9s and 10s) / total   [NPS-style, adjust threshold]
    For CES  (scale=7):  CES%  = (count of 6s and 7s) / total
    For CES  (scale=3):  CES%  = (count of 3 "Easy") / total

    positive_threshold: override the default positive cutoff.
      Default: scale=5 → ≥4; scale=7 → ≥6; scale=3 → =3; scale=10 → ≥9.

    Returns dict with: total, positive_count, score_pct, average_rating, distribution.
    """
    if not ratings:
        raise ValueError("ratings list must not be empty.")
    valid_scales = {3, 5, 7, 10}
    if scale not in valid_scales:
        raise ValueError(f"scale must be one of {valid_scales}.")

    if positive_threshold is None:
        defaults = {5: 4, 7: 6, 3: 3, 10: 9}
        positive_threshold = defaults[scale]

    total = len(ratings)
    positive_count = sum(1 for r in ratings if r >= positive_threshold)
    score_pct = positive_count / total
    avg = sum(ratings) / total

    dist: dict = {}
    for v in range(1, scale + 1):
        dist[v] = ratings.count(v)

    return {
        "total_responses": total,
        "positive_count": positive_count,
        "score_pct": round(score_pct, 4),
        "score_pct_display": f"{score_pct:.1%}",
        "average_rating": round(avg, 2),
        "positive_threshold": f">={positive_threshold}",
        "distribution": dist,
    }


# ---------------------------------------------------------------------------
# Shrinkage-adjusted FTE
# ---------------------------------------------------------------------------


def shrinkage_fte(
    raw_agents: float,
    trained_shrinkage: float,
    unplanned_shrinkage: float,
) -> dict:
    """
    Convert a raw agent count (from Erlang C) to a shrinkage-adjusted FTE headcount.

    FTE = raw_agents / (1 - total_shrinkage)

    trained_shrinkage    fraction: scheduled shrinkage (breaks, lunch, meetings, coaching, training)
    unplanned_shrinkage  fraction: variable shrinkage (sick leave, no-shows, attrition lag)

    Both are fractions (e.g. 0.15 for 15%). Total shrinkage = sum of both.

    Returns dict with: total_shrinkage, fte_required, shrinkage_breakdown, warning.
    """
    if not (0.0 <= trained_shrinkage < 1.0):
        raise ValueError("trained_shrinkage must be in [0, 1).")
    if not (0.0 <= unplanned_shrinkage < 1.0):
        raise ValueError("unplanned_shrinkage must be in [0, 1).")

    total_shrinkage = trained_shrinkage + unplanned_shrinkage
    if total_shrinkage >= 1.0:
        raise ValueError("total_shrinkage (trained + unplanned) must be < 1.0.")

    fte = raw_agents / (1.0 - total_shrinkage)
    warning = ""
    if total_shrinkage > 0.30:
        warning = (
            f"Total shrinkage {total_shrinkage:.1%} exceeds 30% — investigate retention, "
            "scheduling practices, and coaching overhead."
        )

    return {
        "raw_agents": raw_agents,
        "trained_shrinkage_pct": f"{trained_shrinkage:.1%}",
        "unplanned_shrinkage_pct": f"{unplanned_shrinkage:.1%}",
        "total_shrinkage_pct": f"{total_shrinkage:.1%}",
        "fte_required": round(fte, 2),
        "fte_ceil": math.ceil(fte),
        "warning": warning,
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _print_usage() -> None:
    print(
        """
cx_calc.py — CX operations calculator

Usage: python3 cx_calc.py <mode> [args]

Modes:

  erlang-c <contacts_per_interval> <aht_seconds> <interval_seconds>
           <target_sl_pct> <target_sl_seconds>
    e.g.:  python3 cx_calc.py erlang-c 100 240 1800 0.80 20
    (100 contacts/30min, 4min AHT, 30-min interval, 80% within 20s)

  occupancy <contacts_per_interval> <aht_seconds> <agents> <interval_seconds>
    e.g.:  python3 cx_calc.py occupancy 100 240 14 1800

  deflection-roi <deflectable_contacts_per_year> <cost_per_contact>
                 <containment_rate> [content_investment]
    e.g.:  python3 cx_calc.py deflection-roi 12000 8.50 0.65 5000

  csat-ces <scale> <rating1> [rating2 ...]
    e.g.:  python3 cx_calc.py csat-ces 5 5 4 5 3 5 4 5 2 5 5
    (CSAT from 10 responses on a 5-point scale)
    e.g.:  python3 cx_calc.py csat-ces 7 6 7 5 6 7 6 4
    (CES from 7 responses on a 7-point scale)

  shrinkage-fte <raw_agents> <trained_shrinkage> <unplanned_shrinkage>
    e.g.:  python3 cx_calc.py shrinkage-fte 12 0.15 0.08
    (12 raw agents, 15% trained shrinkage, 8% unplanned shrinkage)
""".strip()
    )


def main(argv: List[str]) -> None:
    if len(argv) < 2 or argv[1] in ("--help", "-h", "help"):
        _print_usage()
        return

    mode = argv[1].lower()

    if mode == "erlang-c":
        if len(argv) < 7:
            print("erlang-c requires 5 arguments. See --help.")
            sys.exit(1)
        result = erlang_c(
            contacts_per_interval=float(argv[2]),
            aht_seconds=float(argv[3]),
            interval_seconds=float(argv[4]),
            target_sl_pct=float(argv[5]),
            target_sl_seconds=float(argv[6]),
        )
        print(f"Erlang C result:")
        print(f"  Agents needed        : {result['agents_needed']}")
        print(f"  Service level        : {result['service_level']:.1%}")
        print(f"  Occupancy            : {result['occupancy']:.1%}")
        print(f"  Traffic intensity (A): {result['traffic_intensity_erlangs']} Erlangs")
        if result["warning"]:
            print(f"  *** {result['warning']}")

    elif mode == "occupancy":
        if len(argv) < 6:
            print("occupancy requires 4 arguments. See --help.")
            sys.exit(1)
        result = occupancy(
            contacts_per_interval=float(argv[2]),
            aht_seconds=float(argv[3]),
            agents=int(argv[4]),
            interval_seconds=float(argv[5]),
        )
        print(f"Occupancy result:")
        print(f"  Occupancy: {result['occupancy_pct']}")
        if result["warning"]:
            print(f"  *** {result['warning']}")

    elif mode == "deflection-roi":
        if len(argv) < 5:
            print("deflection-roi requires at least 3 arguments. See --help.")
            sys.exit(1)
        investment = float(argv[5]) if len(argv) >= 6 else 0.0
        result = deflection_roi(
            deflectable_contacts_per_year=float(argv[2]),
            cost_per_contact=float(argv[3]),
            containment_rate=float(argv[4]),
            content_investment=investment,
        )
        print(f"Deflection ROI result:")
        print(f"  Deflected contacts/year: {result['deflected_contacts']:,}")
        print(f"  Gross annual savings   : ${result['gross_annual_savings']:,.2f}")
        print(f"  Net annual savings     : ${result['net_annual_savings']:,.2f}")
        if investment > 0:
            print(f"  Payback period         : {result['payback_months']} months")

    elif mode == "csat-ces":
        if len(argv) < 4:
            print("csat-ces requires scale + at least 1 rating. See --help.")
            sys.exit(1)
        scale = int(argv[2])
        ratings = [int(x) for x in argv[3:]]
        result = csat_ces(ratings=ratings, scale=scale)
        label = "CSAT" if scale in (5, 10) else "CES"
        print(f"{label} result (scale: 1–{scale}, positive: {result['positive_threshold']}):")
        print(f"  Score         : {result['score_pct_display']}")
        print(f"  Total responses: {result['total_responses']}")
        print(f"  Positive count : {result['positive_count']}")
        print(f"  Average rating : {result['average_rating']}")
        print(f"  Distribution   : {result['distribution']}")

    elif mode == "shrinkage-fte":
        if len(argv) < 5:
            print("shrinkage-fte requires 3 arguments. See --help.")
            sys.exit(1)
        result = shrinkage_fte(
            raw_agents=float(argv[2]),
            trained_shrinkage=float(argv[3]),
            unplanned_shrinkage=float(argv[4]),
        )
        print(f"Shrinkage-adjusted FTE result:")
        print(f"  Raw agents          : {result['raw_agents']}")
        print(f"  Trained shrinkage   : {result['trained_shrinkage_pct']}")
        print(f"  Unplanned shrinkage : {result['unplanned_shrinkage_pct']}")
        print(f"  Total shrinkage     : {result['total_shrinkage_pct']}")
        print(f"  FTE required        : {result['fte_required']} (ceil: {result['fte_ceil']})")
        if result["warning"]:
            print(f"  *** {result['warning']}")

    else:
        print(f"Unknown mode: {mode!r}. Run with --help for usage.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Self-test (run when executed directly with no mode arg to test internals)
# ---------------------------------------------------------------------------


def _self_test() -> None:
    """Run basic self-tests and print example outputs. Called when __main__ and no CLI args."""
    print("=== cx_calc.py self-test ===\n")

    # Test 1: Erlang C — 100 contacts in 30-min interval, 4-min AHT, 80/20 SLA
    ec = erlang_c(
        contacts_per_interval=100,
        aht_seconds=240,
        interval_seconds=1800,
        target_sl_pct=0.80,
        target_sl_seconds=20,
    )
    print(f"[erlang-c] 100 contacts/30min, 4min AHT, 80/20 SLA:")
    print(f"  agents_needed={ec['agents_needed']}, SL={ec['service_level']:.1%}, "
          f"occupancy={ec['occupancy']:.1%}")
    assert ec["agents_needed"] >= 14, "Expected >= 14 agents for this workload"
    assert 0.75 <= ec["service_level"] <= 1.0, "Service level out of range"
    assert 0.0 < ec["occupancy"] < 1.0, "Occupancy out of range"
    print("  PASS\n")

    # Test 2: Occupancy check
    occ = occupancy(
        contacts_per_interval=100,
        aht_seconds=240,
        agents=ec["agents_needed"],
        interval_seconds=1800,
    )
    print(f"[occupancy] agents={ec['agents_needed']}: {occ['occupancy_pct']}")
    assert 0.0 < occ["occupancy"] < 1.0
    print("  PASS\n")

    # Test 3: Deflection ROI — 12,000 deflectable contacts/year, $8.50/contact, 65% containment
    roi = deflection_roi(
        deflectable_contacts_per_year=12000,
        cost_per_contact=8.50,
        containment_rate=0.65,
        content_investment=5000.0,
    )
    print(f"[deflection-roi] 12k contacts, $8.50/contact, 65% containment, $5k investment:")
    print(f"  deflected={roi['deflected_contacts']:,}, gross=${roi['gross_annual_savings']:,.2f}, "
          f"net=${roi['net_annual_savings']:,.2f}, payback={roi['payback_months']}mo")
    assert roi["deflected_contacts"] == 7800, f"Expected 7800 deflected, got {roi['deflected_contacts']}"
    assert roi["gross_annual_savings"] == pytest_approx(66300.0), "Gross savings mismatch"
    print("  PASS\n")

    # Test 4: CSAT — 5-point scale
    cs = csat_ces([5, 4, 5, 3, 5, 4, 5, 2, 5, 5], scale=5)
    print(f"[csat-ces] 5-point CSAT, 10 responses: {cs['score_pct_display']}")
    assert cs["positive_count"] == 8, f"Expected 8 positive (4+5), got {cs['positive_count']}"
    assert cs["score_pct"] == 0.8, f"Expected 80%, got {cs['score_pct']}"
    print("  PASS\n")

    # Test 5: CES — 7-point scale
    ces = csat_ces([6, 7, 5, 6, 7, 6, 4], scale=7)
    print(f"[csat-ces] 7-point CES, 7 responses: {ces['score_pct_display']}")
    assert ces["positive_count"] == 5, f"Expected 5 positive (6+7), got {ces['positive_count']}"
    print("  PASS\n")

    # Test 6: Shrinkage FTE — 12 raw agents, 15% trained, 8% unplanned
    fte = shrinkage_fte(raw_agents=12, trained_shrinkage=0.15, unplanned_shrinkage=0.08)
    print(f"[shrinkage-fte] 12 raw agents, 15%+8% shrinkage: "
          f"{fte['fte_required']} FTE (ceil {fte['fte_ceil']})")
    assert fte["fte_ceil"] >= 16, f"Expected ceil FTE >= 16, got {fte['fte_ceil']}"
    print("  PASS\n")

    print("=== All self-tests passed ===")


def pytest_approx(expected: float, rel: float = 0.001) -> float:
    """Tiny inline approx helper for the self-test (no pytest dependency)."""
    # Returns expected; the assertion compares with a tolerance inline.
    return expected


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments → run self-test
        _self_test()
    else:
        main(sys.argv)
