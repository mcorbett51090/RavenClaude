#!/usr/bin/env python3
"""Platform-engineering arithmetic — platform-engineering plugin.

Stdlib only (Python 3.8+). Removes arithmetic error from three recurring
platform-as-product decisions: classifying delivery throughput against the DORA
four keys, measuring paved-road coverage (the share of work that takes the
golden path), and sizing a platform SLO's error budget so the platform team can
spend it on change velocity. It is a *calculator, not a data source* — the user
supplies every input; outputs are decision-support, not a maturity verdict.

Subcommands:
  dora             deployment frequency / lead time / change-failure rate /
                   time-to-restore -> per-key Elite/High/Medium/Low band
  paved-road       on-road vs total work -> paved-road coverage %, plus the gap
                   to a target and how many units must move onto the road
  error-budget     platform SLO target + window -> allowed downtime / bad-event
                   budget, optionally consumed-to-date and remaining

DORA bands follow the published "Accelerate State of DevOps" four-key thresholds
(deployment frequency, lead time for changes, change-failure rate, time to
restore service). Bands drift year to year — verify against the current report
before quoting a band to a consumer.

Examples:
  platform_calc.py dora --deploys-per-day 5 --lead-time-hours 4 \\
      --change-fail-pct 8 --restore-hours 0.5
  platform_calc.py paved-road --on-road 140 --total 200 --target-pct 90
  platform_calc.py error-budget --slo 99.9 --window-days 30 --consumed-min 18
"""
from __future__ import annotations

import argparse
import sys

MINUTES_PER_DAY = 24 * 60


def _fmt_duration(minutes: float) -> str:
    """Human-readable duration from a minute count."""
    if minutes < 1:
        return f"{minutes * 60:.1f} s"
    if minutes < 60:
        return f"{minutes:.1f} min"
    hours = minutes / 60
    if hours < 24:
        return f"{hours:.2f} h"
    return f"{hours / 24:.2f} d"


def _band_deploy_freq(deploys_per_day: float) -> str:
    """Deployment-frequency band from deploys/day."""
    if deploys_per_day >= 1:
        return "Elite (on-demand, multiple per day)"
    if deploys_per_day >= 1 / 7:
        return "High (between once per day and once per week)"
    if deploys_per_day >= 1 / 30:
        return "Medium (between once per week and once per month)"
    return "Low (fewer than once per month)"


def _band_lead_time(hours: float) -> str:
    """Lead-time-for-changes band from hours."""
    if hours < 24:
        return "Elite (less than one day)"
    if hours < 7 * 24:
        return "High (between one day and one week)"
    if hours < 30 * 24:
        return "Medium (between one week and one month)"
    return "Low (more than one month)"


def _band_change_fail(pct: float) -> str:
    """Change-failure-rate band from a percentage."""
    if pct <= 5:
        return "Elite (0-5%)"
    if pct <= 10:
        return "High (5-10%)"
    if pct <= 15:
        return "Medium (10-15%)"
    return "Low (above 15%)"


def _band_restore(hours: float) -> str:
    """Time-to-restore-service band from hours."""
    if hours < 1:
        return "Elite (less than one hour)"
    if hours < 24:
        return "High (less than one day)"
    if hours < 7 * 24:
        return "Medium (less than one week)"
    return "Low (more than one week)"


def dora(
    deploys_per_day: float,
    lead_time_hours: float,
    change_fail_pct: float,
    restore_hours: float,
) -> dict:
    """Classify the four DORA keys into Elite/High/Medium/Low bands."""
    if deploys_per_day < 0:
        raise ValueError("--deploys-per-day must be non-negative")
    if lead_time_hours < 0:
        raise ValueError("--lead-time-hours must be non-negative")
    if not 0 <= change_fail_pct <= 100:
        raise ValueError("--change-fail-pct must be a percentage in [0, 100]")
    if restore_hours < 0:
        raise ValueError("--restore-hours must be non-negative")
    return {
        "deployment_frequency_per_day": deploys_per_day,
        "deployment_frequency_band": _band_deploy_freq(deploys_per_day),
        "lead_time_hours": lead_time_hours,
        "lead_time_band": _band_lead_time(lead_time_hours),
        "change_failure_percent": change_fail_pct,
        "change_failure_band": _band_change_fail(change_fail_pct),
        "time_to_restore_hours": restore_hours,
        "time_to_restore_band": _band_restore(restore_hours),
        "note": (
            "Throughput (frequency, lead time) and stability (change-failure, "
            "restore) move together for elite teams; a throughput gain bought "
            "by a stability loss is not progress. Pair with a DevEx signal."
        ),
    }


def paved_road(on_road: float, total: float, target_pct: float) -> dict:
    """Paved-road coverage and the gap to a coverage target."""
    if total <= 0:
        raise ValueError("--total must be positive")
    if on_road < 0 or on_road > total:
        raise ValueError("--on-road must be between 0 and --total")
    if not 0 <= target_pct <= 100:
        raise ValueError("--target-pct must be a percentage in [0, 100]")

    coverage_pct = on_road / total * 100
    target_units = target_pct / 100 * total
    units_to_move = max(0.0, target_units - on_road)
    gap_pct = max(0.0, target_pct - coverage_pct)
    return {
        "on_road_units": on_road,
        "total_units": total,
        "off_road_units": total - on_road,
        "paved_road_coverage_percent": coverage_pct,
        "target_percent": target_pct,
        "gap_to_target_percent": gap_pct,
        "units_to_move_onto_road": units_to_move,
        "verdict": _coverage_verdict(coverage_pct, target_pct),
    }


def _coverage_verdict(coverage_pct: float, target_pct: float) -> str:
    if coverage_pct >= target_pct:
        return "at or above target — pull demand is real; widen the road, don't mandate it"
    if coverage_pct >= target_pct * 0.75:
        return "approaching target — close the last gap with ergonomics, not policy"
    if coverage_pct >= 25:
        return "partial adoption — find why off-road work avoids the path before adding capability"
    return "low adoption — the paved road is not yet the easy default; treat as a product problem"


def error_budget(
    slo: float,
    window_days: float,
    consumed_min: float,
) -> dict:
    """Platform-SLO error budget over a window, with optional spend-to-date."""
    if not 0 < slo < 100:
        raise ValueError("--slo must be a percentage in (0, 100)")
    if window_days <= 0:
        raise ValueError("--window-days must be positive")
    if consumed_min < 0:
        raise ValueError("--consumed-min must be non-negative")

    budget_fraction = (100 - slo) / 100
    window_minutes = window_days * MINUTES_PER_DAY
    allowed_minutes = window_minutes * budget_fraction
    remaining_minutes = allowed_minutes - consumed_min
    consumed_pct = consumed_min / allowed_minutes * 100 if allowed_minutes else float("inf")
    return {
        "slo_percent": slo,
        "window_days": window_days,
        "allowed_downtime_minutes": allowed_minutes,
        "allowed_downtime_human": _fmt_duration(allowed_minutes),
        "bad_events_per_million": budget_fraction * 1_000_000,
        "consumed_minutes": consumed_min,
        "consumed_percent": consumed_pct,
        "remaining_minutes": remaining_minutes,
        "remaining_human": _fmt_duration(remaining_minutes) if remaining_minutes > 0 else "exhausted",
        "verdict": _budget_verdict(consumed_pct),
    }


def _budget_verdict(consumed_pct: float) -> str:
    if consumed_pct >= 100:
        return "exhausted — freeze risky platform changes; reliability work only"
    if consumed_pct >= 75:
        return "low — slow down; reserve the remainder for the unexpected"
    if consumed_pct >= 25:
        return "healthy — spend the slack on change velocity"
    return "ample — the platform is over-delivering; consider a tighter SLO or faster shipping"


def _print(d: dict, indent: int = 0) -> None:
    pad = "  " * indent
    for k, v in d.items():
        if isinstance(v, list):
            print(f"{pad}{k}:")
            for item in v:
                if isinstance(item, dict):
                    print(f"{pad}  -")
                    _print(item, indent + 2)
                else:
                    print(f"{pad}  - {item}")
        elif isinstance(v, dict):
            print(f"{pad}{k}:")
            _print(v, indent + 1)
        elif isinstance(v, float):
            print(f"{pad}{k}: {v:.4g}")
        else:
            print(f"{pad}{k}: {v}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="platform_calc.py",
        description="Platform-engineering calculator: DORA bands, paved-road coverage, platform SLO budget (decision-support only).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    dr = sub.add_parser("dora", help="four-key inputs -> Elite/High/Medium/Low bands")
    dr.add_argument("--deploys-per-day", type=float, required=True, help="deployment frequency, deploys/day")
    dr.add_argument("--lead-time-hours", type=float, required=True, help="lead time for changes, hours")
    dr.add_argument("--change-fail-pct", type=float, required=True, help="change-failure rate, percent")
    dr.add_argument("--restore-hours", type=float, required=True, help="time to restore service, hours")

    pr = sub.add_parser("paved-road", help="on-road vs total -> coverage % + gap to target")
    pr.add_argument("--on-road", type=float, required=True, help="units of work that took the golden path")
    pr.add_argument("--total", type=float, required=True, help="total units of comparable work")
    pr.add_argument("--target-pct", type=float, default=80, help="coverage target percent (default 80)")

    eb = sub.add_parser("error-budget", help="platform SLO + window -> allowed downtime/budget")
    eb.add_argument("--slo", type=float, required=True, help="platform SLO target percent, e.g. 99.9")
    eb.add_argument("--window-days", type=float, default=30, help="rolling window in days (default 30)")
    eb.add_argument("--consumed-min", type=float, default=0, help="budget already spent this window, minutes")

    return parser


def main(argv: list = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "dora":
            result = dora(args.deploys_per_day, args.lead_time_hours, args.change_fail_pct, args.restore_hours)
        elif args.command == "paved-road":
            result = paved_road(args.on_road, args.total, args.target_pct)
        elif args.command == "error-budget":
            result = error_budget(args.slo, args.window_days, args.consumed_min)
        else:  # pragma: no cover - argparse enforces choices
            parser.error(f"unknown command {args.command}")
            return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
