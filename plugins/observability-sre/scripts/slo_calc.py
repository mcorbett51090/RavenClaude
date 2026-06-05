#!/usr/bin/env python3
"""SLO / error-budget calculator — observability-sre plugin.

Stdlib only (Python 3.8+). Removes arithmetic error from the recurring
reliability decisions: how much budget an SLO buys, how fast the budget is
burning, and what burn-rate alert thresholds to set for a target detection
time. It is a *calculator, not a data source* — the user supplies every
input; outputs are decision-support, not a reliability guarantee.

Subcommands:
  error-budget   SLO target + window -> allowed downtime / bad-event budget
  burn-rate      good/bad events (or error rate) over a window -> burn rate,
                 budget consumed, time-to-exhaustion at the current rate
  alert-windows  SLO target + acceptable budget-spend -> the multi-window
                 multi-burn-rate alert thresholds (Google SRE Workbook shape)

All math is grounded in the Google SRE Workbook "Implementing SLOs" and
"Alerting on SLOs" chapters. Verify the conventions at use.

Examples:
  slo_calc.py error-budget --slo 99.9 --window-days 30
  slo_calc.py burn-rate --slo 99.9 --window-days 30 --bad 1200 --total 1000000 --elapsed-hours 48
  slo_calc.py alert-windows --slo 99.9 --window-days 30
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


def _validate_slo(slo: float) -> float:
    """SLO target as a percentage in (0, 100)."""
    if not 0 < slo < 100:
        raise ValueError(f"--slo must be a percentage in (0, 100), got {slo}")
    return slo


def error_budget(slo: float, window_days: float) -> dict:
    """Allowed unreliability for an SLO over a rolling window."""
    _validate_slo(slo)
    if window_days <= 0:
        raise ValueError("--window-days must be positive")
    budget_fraction = (100 - slo) / 100
    window_minutes = window_days * MINUTES_PER_DAY
    allowed_minutes = window_minutes * budget_fraction
    return {
        "slo_percent": slo,
        "window_days": window_days,
        "budget_fraction": budget_fraction,
        "allowed_downtime_minutes": allowed_minutes,
        "allowed_downtime_human": _fmt_duration(allowed_minutes),
        "bad_events_per_million": budget_fraction * 1_000_000,
    }


def burn_rate(
    slo: float,
    window_days: float,
    bad: float,
    total: float,
    elapsed_hours: float,
) -> dict:
    """Current burn rate and projected time-to-exhaustion.

    Burn rate = (observed error fraction) / (budget fraction). A burn rate of
    1.0 spends the whole budget exactly over the SLO window; 14.4 spends it in
    ~1/14.4 of the window.
    """
    _validate_slo(slo)
    if total <= 0:
        raise ValueError("--total must be positive")
    if bad < 0 or bad > total:
        raise ValueError("--bad must be between 0 and --total")
    if elapsed_hours <= 0:
        raise ValueError("--elapsed-hours must be positive")

    budget_fraction = (100 - slo) / 100
    observed_error_fraction = bad / total
    rate = observed_error_fraction / budget_fraction if budget_fraction else float("inf")

    # Fraction of the whole-window budget consumed during the elapsed slice.
    window_hours = window_days * 24
    budget_consumed_fraction = rate * (elapsed_hours / window_hours)

    if rate > 0:
        hours_to_exhaust = window_hours / rate
        remaining_budget_fraction = max(0.0, 1 - budget_consumed_fraction)
        hours_remaining = remaining_budget_fraction * window_hours / rate
    else:
        hours_to_exhaust = float("inf")
        hours_remaining = float("inf")

    return {
        "slo_percent": slo,
        "window_days": window_days,
        "observed_error_percent": observed_error_fraction * 100,
        "budget_error_percent": budget_fraction * 100,
        "burn_rate": rate,
        "budget_consumed_percent": budget_consumed_fraction * 100,
        "time_to_full_exhaustion_from_start": _fmt_duration(hours_to_exhaust * 60)
        if rate > 0
        else "never (no errors)",
        "time_remaining_at_this_rate": _fmt_duration(hours_remaining * 60)
        if rate > 0
        else "unbounded (no errors)",
        "verdict": _burn_verdict(rate),
    }


def _burn_verdict(rate: float) -> str:
    if rate == 0:
        return "no burn — budget untouched this window slice"
    if rate < 1:
        return "sustainable — at this rate the budget lasts beyond the window"
    if rate < 2:
        return "watch — burning slightly faster than budget allows"
    if rate < 10:
        return "elevated — slow-burn alert territory; investigate"
    return "critical — fast-burn; this is a page"


def alert_windows(slo: float, window_days: float) -> dict:
    """Multi-window multi-burn-rate alert thresholds (SRE Workbook shape).

    The Workbook's canonical pairs for a 30-day SLO: a fast page that spends a
    given % of the budget over a short window, and a slow page over a longer
    one. Burn factor = (budget_spent_fraction * window_total) / alert_window.
    """
    _validate_slo(slo)
    if window_days <= 0:
        raise ValueError("--window-days must be positive")
    window_hours = window_days * 24

    # (label, budget % spent that should trigger, long window h, short confirm h)
    presets = [
        ("fast-burn (page)", 0.02, 1.0, 5 / 60),
        ("medium-burn (page)", 0.05, 6.0, 30 / 60),
        ("slow-burn (ticket)", 0.10, 24.0, 2.0),
    ]
    rows = []
    for label, budget_spent, long_h, short_h in presets:
        burn_factor = (budget_spent * window_hours) / long_h
        rows.append(
            {
                "alert": label,
                "budget_spent_to_fire_percent": budget_spent * 100,
                "long_window_hours": long_h,
                "short_confirm_window_hours": round(short_h, 4),
                "burn_rate_factor": round(burn_factor, 2),
            }
        )
    return {
        "slo_percent": slo,
        "window_days": window_days,
        "alerts": rows,
        "note": (
            "Long window AND short confirmation window must both exceed the burn "
            "factor to fire. Recompute factors if your window != 30d."
        ),
    }


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
        prog="slo_calc.py",
        description="SLO / error-budget / burn-rate calculator (decision-support only).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    eb = sub.add_parser("error-budget", help="SLO target + window -> allowed downtime/budget")
    eb.add_argument("--slo", type=float, required=True, help="SLO target percent, e.g. 99.9")
    eb.add_argument("--window-days", type=float, default=30, help="rolling window in days (default 30)")

    br = sub.add_parser("burn-rate", help="events over a window -> burn rate + time-to-exhaustion")
    br.add_argument("--slo", type=float, required=True, help="SLO target percent")
    br.add_argument("--window-days", type=float, default=30, help="SLO rolling window in days")
    br.add_argument("--bad", type=float, required=True, help="bad (failed) event count in the elapsed slice")
    br.add_argument("--total", type=float, required=True, help="total valid event count in the elapsed slice")
    br.add_argument("--elapsed-hours", type=float, required=True, help="hours the slice covers")

    aw = sub.add_parser("alert-windows", help="SLO target -> multi-window burn-rate alert thresholds")
    aw.add_argument("--slo", type=float, required=True, help="SLO target percent")
    aw.add_argument("--window-days", type=float, default=30, help="SLO rolling window in days")

    return parser


def main(argv: list = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "error-budget":
            result = error_budget(args.slo, args.window_days)
        elif args.command == "burn-rate":
            result = burn_rate(args.slo, args.window_days, args.bad, args.total, args.elapsed_hours)
        elif args.command == "alert-windows":
            result = alert_windows(args.slo, args.window_days)
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
