#!/usr/bin/env python3
"""
revops_calc.py — Revenue Operations calculator (stdlib only, Python 3.8+).

Modes:
  quota-attainment      Quota attainment percentage and over/under amount.
  pipeline-coverage     Pipeline coverage ratio (pipeline ÷ remaining quota gap).
  weighted-forecast     Weighted probability forecast from stage breakdown.
  win-rate              Win rate from historical closed deal data.
  sales-velocity        Sales velocity (#opps × win% × ACV) ÷ cycle-length.

This is a CALCULATOR, not a data source. The caller supplies every input.
Outputs are decision-support only — not accounting, audit, or investment advice.

Usage examples (self-test runs automatically when invoked as __main__):
  python3 revops_calc.py quota-attainment --quota 1000000 --attained 873000
  python3 revops_calc.py pipeline-coverage --pipeline 4500000 --quota-remaining 1500000 --win-rate 0.28
  python3 revops_calc.py weighted-forecast --stages '{"Discovery":{"acv":800000,"prob":0.15},"Proposal":{"acv":600000,"prob":0.50},"Commit":{"acv":300000,"prob":0.80}}'
  python3 revops_calc.py win-rate --won 42 --lost 118 --total 200
  python3 revops_calc.py sales-velocity --opps 80 --win-rate 0.25 --acv 45000 --cycle-days 90
"""

import argparse
import json
import sys
from typing import Dict, Optional


# ---------------------------------------------------------------------------
# Core calculation functions
# ---------------------------------------------------------------------------


def quota_attainment(quota: float, attained: float) -> Dict:
    """
    Calculate quota attainment percentage and the over/under dollar amount.

    Args:
        quota:    The target quota in dollars (or any currency unit).
        attained: The closed-won amount achieved in the same period and units.

    Returns:
        Dict with attainment_pct, over_under, status.
    """
    if quota <= 0:
        raise ValueError("quota must be > 0")
    pct = attained / quota * 100.0
    over_under = attained - quota
    status = "above quota" if over_under >= 0 else "below quota"
    return {
        "quota": quota,
        "attained": attained,
        "attainment_pct": round(pct, 2),
        "over_under": round(over_under, 2),
        "status": status,
    }


def pipeline_coverage(
    pipeline: float, quota_remaining: float, win_rate: Optional[float] = None
) -> Dict:
    """
    Calculate pipeline coverage ratio.

    Coverage ratio = open pipeline ÷ remaining quota gap.
    A common heuristic is 3× coverage, but the required multiple is 1 ÷ win_rate.
    Always state the win rate alongside the coverage ratio.

    Args:
        pipeline:        Open pipeline ACV (sum of all open deal amounts).
        quota_remaining: The quota still to be closed in the period.
        win_rate:        Historical blended win rate (0.0–1.0). Optional but recommended.

    Returns:
        Dict with coverage_ratio, required_coverage (if win_rate provided), status.
    """
    if quota_remaining <= 0:
        raise ValueError("quota_remaining must be > 0")
    ratio = pipeline / quota_remaining
    result = {
        "pipeline": pipeline,
        "quota_remaining": quota_remaining,
        "coverage_ratio": round(ratio, 2),
        "win_rate_used": win_rate,
    }
    if win_rate is not None:
        if not (0 < win_rate <= 1):
            raise ValueError("win_rate must be between 0 (exclusive) and 1 (inclusive)")
        required = 1.0 / win_rate
        result["required_coverage_at_this_win_rate"] = round(required, 2)
        gap = ratio - required
        result["coverage_gap"] = round(gap, 2)
        result["status"] = "sufficient" if gap >= 0 else "insufficient — add pipeline or reduce quota gap"
    else:
        result["note"] = (
            "win_rate not provided; 3x is a common heuristic but required coverage = 1 / win_rate. "
            "Provide --win-rate for an accurate assessment."
        )
        result["status"] = "above 3x heuristic" if ratio >= 3.0 else "below 3x heuristic"
    return result


def weighted_forecast(stages: Dict[str, Dict]) -> Dict:
    """
    Calculate a weighted probability forecast from a breakdown by stage.

    Args:
        stages: Dict mapping stage_name -> {"acv": float, "prob": float (0.0-1.0)}.
                Example: {"Proposal": {"acv": 600000, "prob": 0.50}}

    Returns:
        Dict with per-stage weighted values and total weighted forecast.
    """
    stage_results = []
    total_pipeline = 0.0
    total_weighted = 0.0

    for stage_name, data in stages.items():
        acv = float(data.get("acv", 0))
        prob = float(data.get("prob", 0))
        if not (0.0 <= prob <= 1.0):
            raise ValueError(f"prob for stage '{stage_name}' must be between 0 and 1; got {prob}")
        weighted = acv * prob
        stage_results.append(
            {
                "stage": stage_name,
                "pipeline_acv": round(acv, 2),
                "probability": prob,
                "weighted_value": round(weighted, 2),
            }
        )
        total_pipeline += acv
        total_weighted += weighted

    return {
        "stages": stage_results,
        "total_pipeline_acv": round(total_pipeline, 2),
        "total_weighted_forecast": round(total_weighted, 2),
        "blended_probability": round(total_weighted / total_pipeline, 4) if total_pipeline > 0 else 0,
        "note": (
            "Probabilities must be empirically calibrated from historical win-rate data by stage. "
            "Vendor default probabilities (e.g., Salesforce 10/20/40/60/80) are wrong for most companies."
        ),
    }


def win_rate(won: int, lost: int, total: Optional[int] = None) -> Dict:
    """
    Calculate win rate from historical closed deal data.

    Win rate = won / (won + lost). Optionally accepts a total that includes
    deals still open (which lowers the denominator and the rate).

    Args:
        won:   Number of deals closed won.
        lost:  Number of deals closed lost.
        total: Total deals created in the same cohort (including open). Optional.
               If provided, calculates win rate on total cohort basis (more conservative).

    Returns:
        Dict with win_rate_closed and (if total provided) win_rate_total_cohort.
    """
    closed = won + lost
    if closed == 0:
        raise ValueError("won + lost must be > 0")
    rate_closed = won / closed
    result = {
        "won": won,
        "lost": lost,
        "closed": closed,
        "win_rate_closed": round(rate_closed, 4),
        "win_rate_closed_pct": round(rate_closed * 100, 2),
    }
    if total is not None:
        if total < closed:
            raise ValueError("total must be >= won + lost")
        rate_total = won / total
        result["total_cohort"] = total
        result["open_still"] = total - closed
        result["win_rate_total_cohort"] = round(rate_total, 4)
        result["win_rate_total_cohort_pct"] = round(rate_total * 100, 2)
        result["note"] = (
            "win_rate_closed is the standard for pipeline-coverage calculations. "
            "win_rate_total_cohort is more conservative (includes open deals that may never close)."
        )
    return result


def sales_velocity(opps: int, win_rate_val: float, acv: float, cycle_days: float) -> Dict:
    """
    Calculate sales velocity.

    Sales velocity = (# opportunities × win rate × average ACV) ÷ average cycle length (days).
    Measures the rate of revenue flow through the pipeline (dollars per day).

    Args:
        opps:         Number of open opportunities.
        win_rate_val: Historical win rate (0.0–1.0).
        acv:          Average contract value in dollars.
        cycle_days:   Average sales cycle length in days.

    Returns:
        Dict with daily_velocity, monthly_velocity, annual_velocity.
    """
    if not (0 < win_rate_val <= 1):
        raise ValueError("win_rate must be between 0 (exclusive) and 1 (inclusive)")
    if cycle_days <= 0:
        raise ValueError("cycle_days must be > 0")
    if opps < 0:
        raise ValueError("opps must be >= 0")

    daily = (opps * win_rate_val * acv) / cycle_days
    monthly = daily * 30.4375  # average days per month
    annual = daily * 365.25

    return {
        "inputs": {
            "opportunities": opps,
            "win_rate": win_rate_val,
            "average_acv": acv,
            "average_cycle_days": cycle_days,
        },
        "daily_velocity": round(daily, 2),
        "monthly_velocity": round(monthly, 2),
        "annual_velocity": round(annual, 2),
        "note": (
            "Sales velocity measures the rate of revenue flow through the pipeline. "
            "A declining velocity trend is an early-warning signal before the forecast number is impacted. "
            "Track weekly by segment (SMB / mid-market / enterprise)."
        ),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _fmt(d: Dict, indent: int = 2) -> str:
    return json.dumps(d, indent=indent)


def main():
    parser = argparse.ArgumentParser(
        description="RevOps calculator — quota attainment, pipeline coverage, forecast, win rate, sales velocity."
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # quota-attainment
    p_qa = subparsers.add_parser("quota-attainment", help="Quota attainment % and over/under")
    p_qa.add_argument("--quota", type=float, required=True, help="Target quota in dollars")
    p_qa.add_argument("--attained", type=float, required=True, help="Closed-won amount")

    # pipeline-coverage
    p_pc = subparsers.add_parser("pipeline-coverage", help="Pipeline coverage ratio")
    p_pc.add_argument("--pipeline", type=float, required=True, help="Open pipeline ACV")
    p_pc.add_argument("--quota-remaining", type=float, required=True, help="Remaining quota gap")
    p_pc.add_argument("--win-rate", type=float, default=None, help="Historical win rate 0-1 (optional)")

    # weighted-forecast
    p_wf = subparsers.add_parser("weighted-forecast", help="Weighted probability forecast")
    p_wf.add_argument(
        "--stages",
        type=str,
        required=True,
        help='JSON dict: \'{"Stage": {"acv": 500000, "prob": 0.50}, ...}\'',
    )

    # win-rate
    p_wr = subparsers.add_parser("win-rate", help="Win rate from closed-deal data")
    p_wr.add_argument("--won", type=int, required=True, help="Deals closed won")
    p_wr.add_argument("--lost", type=int, required=True, help="Deals closed lost")
    p_wr.add_argument("--total", type=int, default=None, help="Total deals created (optional)")

    # sales-velocity
    p_sv = subparsers.add_parser("sales-velocity", help="Sales velocity (revenue/day)")
    p_sv.add_argument("--opps", type=int, required=True, help="Number of open opportunities")
    p_sv.add_argument("--win-rate", type=float, required=True, dest="win_rate_val", help="Win rate 0-1")
    p_sv.add_argument("--acv", type=float, required=True, help="Average contract value")
    p_sv.add_argument("--cycle-days", type=float, required=True, help="Average sales cycle in days")

    args = parser.parse_args()

    if args.mode == "quota-attainment":
        result = quota_attainment(args.quota, args.attained)
    elif args.mode == "pipeline-coverage":
        result = pipeline_coverage(args.pipeline, args.quota_remaining, args.win_rate)
    elif args.mode == "weighted-forecast":
        try:
            stages_data = json.loads(args.stages)
        except json.JSONDecodeError as e:
            print(f"ERROR: --stages must be valid JSON: {e}", file=sys.stderr)
            sys.exit(1)
        result = weighted_forecast(stages_data)
    elif args.mode == "win-rate":
        result = win_rate(args.won, args.lost, args.total)
    elif args.mode == "sales-velocity":
        result = sales_velocity(args.opps, args.win_rate_val, args.acv, args.cycle_days)
    else:
        parser.print_help()
        sys.exit(1)

    print(_fmt(result))


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


def _run_self_tests():
    """Run self-tests and print example outputs. Called when module is run directly."""
    import traceback

    tests_passed = 0
    tests_failed = 0

    def _test(label: str, fn, *args, **kwargs):
        nonlocal tests_passed, tests_failed
        try:
            result = fn(*args, **kwargs)
            print(f"\n--- {label} ---")
            print(_fmt(result))
            tests_passed += 1
            return result
        except Exception as e:
            print(f"\n--- {label} FAILED ---")
            traceback.print_exc()
            tests_failed += 1
            return None

    # 1. Quota attainment — below quota
    r = _test(
        "quota-attainment: 87.3% attainment",
        quota_attainment,
        quota=1_000_000,
        attained=873_000,
    )
    assert r is not None and r["attainment_pct"] == 87.3, "quota attainment pct mismatch"
    assert r["status"] == "below quota"

    # 2. Quota attainment — above quota
    r = _test(
        "quota-attainment: 112% attainment",
        quota_attainment,
        quota=1_000_000,
        attained=1_120_000,
    )
    assert r is not None and r["attainment_pct"] == 112.0

    # 3. Pipeline coverage — with win rate
    r = _test(
        "pipeline-coverage: $4.5M pipeline, $1.5M remaining, 28% win rate",
        pipeline_coverage,
        pipeline=4_500_000,
        quota_remaining=1_500_000,
        win_rate=0.28,
    )
    assert r is not None
    assert r["coverage_ratio"] == 3.0
    assert r["required_coverage_at_this_win_rate"] == round(1 / 0.28, 2)

    # 4. Pipeline coverage — no win rate (heuristic)
    r = _test(
        "pipeline-coverage: heuristic only (no win rate)",
        pipeline_coverage,
        pipeline=2_000_000,
        quota_remaining=1_000_000,
    )
    assert r is not None and r["coverage_ratio"] == 2.0
    assert "below 3x" in r["status"]

    # 5. Weighted forecast
    stages_input = {
        "Discovery": {"acv": 800_000, "prob": 0.15},
        "Technical Validation": {"acv": 600_000, "prob": 0.35},
        "Proposal": {"acv": 500_000, "prob": 0.55},
        "Commit": {"acv": 300_000, "prob": 0.85},
    }
    r = _test(
        "weighted-forecast: four-stage example",
        weighted_forecast,
        stages=stages_input,
    )
    assert r is not None
    assert r["total_pipeline_acv"] == 2_200_000
    expected_weighted = round(800000 * 0.15 + 600000 * 0.35 + 500000 * 0.55 + 300000 * 0.85, 2)
    assert r["total_weighted_forecast"] == expected_weighted, (
        f"Expected {expected_weighted}, got {r['total_weighted_forecast']}"
    )

    # 6. Win rate — closed only
    r = _test(
        "win-rate: 42 won, 118 lost (26% win rate)",
        win_rate,
        won=42,
        lost=118,
    )
    assert r is not None
    assert r["win_rate_closed_pct"] == round(42 / 160 * 100, 2)

    # 7. Win rate — with total cohort
    r = _test(
        "win-rate: 42 won, 118 lost, 200 total cohort",
        win_rate,
        won=42,
        lost=118,
        total=200,
    )
    assert r is not None
    assert r["win_rate_total_cohort_pct"] == round(42 / 200 * 100, 2)

    # 8. Sales velocity
    r = _test(
        "sales-velocity: 80 opps, 25% win rate, $45K ACV, 90-day cycle",
        sales_velocity,
        opps=80,
        win_rate_val=0.25,
        acv=45_000,
        cycle_days=90,
    )
    assert r is not None
    expected_daily = round((80 * 0.25 * 45_000) / 90, 2)
    assert r["daily_velocity"] == expected_daily, f"Expected {expected_daily}, got {r['daily_velocity']}"

    print(f"\n{'=' * 50}")
    print(f"Self-test complete: {tests_passed} passed, {tests_failed} failed.")
    if tests_failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    # If called with no args (or only the script name), run self-tests.
    # If called with args, run the CLI.
    if len(sys.argv) == 1:
        _run_self_tests()
    else:
        main()
