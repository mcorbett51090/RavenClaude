#!/usr/bin/env python3
"""
fsm_calc.py — Field-Service Management calculator (stdlib only).

Six functions covering the core FSM decision metrics:
  - technician_utilization    : billable ÷ available hours
  - first_time_fix_rate       : jobs resolved on first visit ÷ total jobs
  - mttr                      : mean time to repair
  - route_density             : jobs ÷ drive-hours (productivity of territory)
  - sla_attainment            : jobs responded within SLA window ÷ total jobs in tier
  - truck_stock_fill_rate     : parts-on-hand requests satisfied ÷ total requests

All functions are pure (no I/O) and return a dict with the result plus the
input assumptions so callers can audit the calculation.

DISCLAIMER: outputs are decision-support only, not operational/accounting/audit
advice. The caller supplies every input; this script does not source data.
"""

from __future__ import annotations

import math
from typing import Sequence


# ---------------------------------------------------------------------------
# 1. Technician utilization
# ---------------------------------------------------------------------------


def technician_utilization(
    billable_hours: float,
    available_hours: float,
) -> dict:
    """
    Calculate technician utilization as billable ÷ available hours.

    Parameters
    ----------
    billable_hours : float
        Hours spent on productive billable work (on-site, billable travel if applicable).
    available_hours : float
        Total paid/clocked hours (scheduled shift hours).

    Returns
    -------
    dict with keys: utilization_rate, billable_hours, available_hours,
                    non_billable_hours, interpretation.
    """
    if available_hours <= 0:
        raise ValueError("available_hours must be > 0")
    if billable_hours < 0:
        raise ValueError("billable_hours must be >= 0")
    if billable_hours > available_hours:
        raise ValueError("billable_hours cannot exceed available_hours")

    rate = billable_hours / available_hours
    non_billable = available_hours - billable_hours

    if rate >= 0.80:
        interp = "High utilization (≥80%) — monitor for burnout/quality risk; little buffer for emergencies."
    elif rate >= 0.70:
        interp = "Healthy utilization (70–79%) — typical field-service target range."
    elif rate >= 0.60:
        interp = "Below target (60–69%) — investigate: excessive travel, scheduling gaps, or admin time?"
    else:
        interp = "Low utilization (<60%) — significant drag; root-cause the utilization waterfall."

    return {
        "utilization_rate": round(rate, 4),
        "utilization_pct": f"{rate * 100:.1f}%",
        "billable_hours": billable_hours,
        "available_hours": available_hours,
        "non_billable_hours": round(non_billable, 2),
        "interpretation": interp,
    }


# ---------------------------------------------------------------------------
# 2. First-time-fix rate
# ---------------------------------------------------------------------------


def first_time_fix_rate(
    jobs_resolved_first_visit: int,
    total_jobs: int,
) -> dict:
    """
    Calculate first-time-fix (FTF) rate.

    Parameters
    ----------
    jobs_resolved_first_visit : int
        Jobs fully resolved on the first technician visit (no return trip required).
    total_jobs : int
        Total jobs in the period.

    Returns
    -------
    dict with keys: ftf_rate, jobs_resolved_first_visit, total_jobs,
                    jobs_requiring_return, interpretation.
    """
    if total_jobs <= 0:
        raise ValueError("total_jobs must be > 0")
    if jobs_resolved_first_visit < 0:
        raise ValueError("jobs_resolved_first_visit must be >= 0")
    if jobs_resolved_first_visit > total_jobs:
        raise ValueError("jobs_resolved_first_visit cannot exceed total_jobs")

    rate = jobs_resolved_first_visit / total_jobs
    returns = total_jobs - jobs_resolved_first_visit

    if rate >= 0.85:
        interp = "Strong FTF (≥85%) — industry benchmark for well-run field-service operations."
    elif rate >= 0.75:
        interp = "Acceptable FTF (75–84%) — improvement opportunity; segment root causes."
    elif rate >= 0.65:
        interp = "Below target (65–74%) — significant first-visit failure rate; root-cause analysis needed."
    else:
        interp = "Low FTF (<65%) — systemic issue; investigate parts, skill-match, and job-information gaps."

    return {
        "ftf_rate": round(rate, 4),
        "ftf_pct": f"{rate * 100:.1f}%",
        "jobs_resolved_first_visit": jobs_resolved_first_visit,
        "total_jobs": total_jobs,
        "jobs_requiring_return": returns,
        "return_rate_pct": f"{(returns / total_jobs) * 100:.1f}%",
        "interpretation": interp,
    }


# ---------------------------------------------------------------------------
# 3. Mean time to repair (MTTR)
# ---------------------------------------------------------------------------


def mttr(resolution_times_hours: Sequence[float]) -> dict:
    """
    Calculate mean time to repair from a list of individual job resolution times.

    Parameters
    ----------
    resolution_times_hours : sequence of float
        Per-job resolution time in hours (time from job-open to job-closed).

    Returns
    -------
    dict with keys: mttr_hours, job_count, min_hours, max_hours,
                    median_hours, std_dev_hours.
    """
    times = list(resolution_times_hours)
    if not times:
        raise ValueError("resolution_times_hours must not be empty")
    if any(t < 0 for t in times):
        raise ValueError("All resolution times must be >= 0")

    n = len(times)
    mean = sum(times) / n
    sorted_t = sorted(times)
    mid = n // 2
    median = sorted_t[mid] if n % 2 == 1 else (sorted_t[mid - 1] + sorted_t[mid]) / 2
    variance = sum((t - mean) ** 2 for t in times) / n
    std_dev = math.sqrt(variance)

    return {
        "mttr_hours": round(mean, 2),
        "job_count": n,
        "min_hours": round(min(times), 2),
        "max_hours": round(max(times), 2),
        "median_hours": round(median, 2),
        "std_dev_hours": round(std_dev, 2),
        "note": "High std_dev relative to mean suggests a mix of quick fixes and complex jobs — consider segmenting by equipment type or failure mode.",
    }


# ---------------------------------------------------------------------------
# 4. Route density
# ---------------------------------------------------------------------------


def route_density(total_jobs: int, total_drive_hours: float) -> dict:
    """
    Calculate route density: jobs completed per drive-hour.

    Higher density = less time driving per job = more productive territory design.

    Parameters
    ----------
    total_jobs : int
        Number of jobs completed in the period.
    total_drive_hours : float
        Total hours spent driving between jobs (not including on-site time).

    Returns
    -------
    dict with keys: jobs_per_drive_hour, total_jobs, total_drive_hours,
                    avg_drive_time_per_job_min, interpretation.
    """
    if total_drive_hours <= 0:
        raise ValueError("total_drive_hours must be > 0")
    if total_jobs <= 0:
        raise ValueError("total_jobs must be > 0")

    density = total_jobs / total_drive_hours
    avg_drive_min = (total_drive_hours / total_jobs) * 60

    if avg_drive_min <= 20:
        interp = "Dense territory (≤20 min avg drive/job) — well-clustered; high route efficiency."
    elif avg_drive_min <= 30:
        interp = "Acceptable density (20–30 min avg) — consider geo-clustering PM batches further."
    elif avg_drive_min <= 40:
        interp = "Below target (30–40 min avg) — territory may be too large or poorly clustered; review zone boundaries."
    else:
        interp = "Low density (>40 min avg) — significant drive-time waste; rebalance territory or investigate scheduling gaps."

    return {
        "jobs_per_drive_hour": round(density, 2),
        "total_jobs": total_jobs,
        "total_drive_hours": round(total_drive_hours, 2),
        "avg_drive_time_per_job_min": round(avg_drive_min, 1),
        "interpretation": interp,
    }


# ---------------------------------------------------------------------------
# 5. SLA attainment
# ---------------------------------------------------------------------------


def sla_attainment(
    jobs_within_window: int,
    total_jobs_in_tier: int,
    sla_tier_label: str = "",
) -> dict:
    """
    Calculate SLA attainment rate for a given SLA tier.

    Parameters
    ----------
    jobs_within_window : int
        Number of jobs responded to (first tech on-site) within the SLA response window.
    total_jobs_in_tier : int
        Total jobs in this SLA tier for the period.
    sla_tier_label : str, optional
        Human-readable tier name for output labeling (e.g., "Premium 4h").

    Returns
    -------
    dict with keys: sla_tier, attainment_rate, jobs_within_window,
                    total_jobs, misses, interpretation.
    """
    if total_jobs_in_tier <= 0:
        raise ValueError("total_jobs_in_tier must be > 0")
    if jobs_within_window < 0:
        raise ValueError("jobs_within_window must be >= 0")
    if jobs_within_window > total_jobs_in_tier:
        raise ValueError("jobs_within_window cannot exceed total_jobs_in_tier")

    rate = jobs_within_window / total_jobs_in_tier
    misses = total_jobs_in_tier - jobs_within_window

    if rate >= 0.95:
        interp = "Strong SLA attainment (≥95%) — target for premium-tier contracts."
    elif rate >= 0.90:
        interp = "Acceptable attainment (90–94%) — monitor for trend; investigate miss causes."
    elif rate >= 0.80:
        interp = "Below target (80–89%) — SLA misses are recurring; review dispatch priority enforcement and emergency-buffer sizing."
    else:
        interp = "Poor attainment (<80%) — systemic SLA failure; dispatch logic, skill coverage, or capacity is misaligned with commitment."

    return {
        "sla_tier": sla_tier_label or "unspecified",
        "attainment_rate": round(rate, 4),
        "attainment_pct": f"{rate * 100:.1f}%",
        "jobs_within_window": jobs_within_window,
        "total_jobs_in_tier": total_jobs_in_tier,
        "misses": misses,
        "miss_rate_pct": f"{(misses / total_jobs_in_tier) * 100:.1f}%",
        "interpretation": interp,
    }


# ---------------------------------------------------------------------------
# 6. Truck-stock fill rate
# ---------------------------------------------------------------------------


def truck_stock_fill_rate(
    requests_filled_from_stock: int,
    total_parts_requests: int,
    service_level_target: float = 0.95,
) -> dict:
    """
    Calculate truck-stock fill rate: parts requests satisfied from on-truck stock
    ÷ total parts requests.

    A "parts request" is a job that required a specific part; "filled from stock" means
    the technician had the part on the truck when the job was dispatched.

    Parameters
    ----------
    requests_filled_from_stock : int
        Jobs where the required part was already on the technician's truck.
    total_parts_requests : int
        Total jobs that required a specific part (universal-carry or specialty).
    service_level_target : float
        The fill-rate target set by the SLA tier design (default 0.95 for premium tier).

    Returns
    -------
    dict with keys: fill_rate, target, gap_to_target, stockout_count,
                    total_requests, meets_target, interpretation.
    """
    if total_parts_requests <= 0:
        raise ValueError("total_parts_requests must be > 0")
    if requests_filled_from_stock < 0:
        raise ValueError("requests_filled_from_stock must be >= 0")
    if requests_filled_from_stock > total_parts_requests:
        raise ValueError("requests_filled_from_stock cannot exceed total_parts_requests")
    if not (0 < service_level_target <= 1.0):
        raise ValueError("service_level_target must be between 0 and 1")

    fill_rate = requests_filled_from_stock / total_parts_requests
    stockouts = total_parts_requests - requests_filled_from_stock
    gap = service_level_target - fill_rate
    meets = fill_rate >= service_level_target

    if meets:
        interp = f"Fill rate {fill_rate * 100:.1f}% meets the {service_level_target * 100:.0f}% service-level target."
    else:
        interp = (
            f"Fill rate {fill_rate * 100:.1f}% is {gap * 100:.1f}pp below the "
            f"{service_level_target * 100:.0f}% target — {stockouts} stockout event(s) in period. "
            "Identify top-miss parts and evaluate adding to universal-carry using the payback framework."
        )

    return {
        "fill_rate": round(fill_rate, 4),
        "fill_rate_pct": f"{fill_rate * 100:.1f}%",
        "service_level_target_pct": f"{service_level_target * 100:.0f}%",
        "gap_to_target_pp": round(gap * 100, 1),
        "meets_target": meets,
        "requests_filled_from_stock": requests_filled_from_stock,
        "total_parts_requests": total_parts_requests,
        "stockout_count": stockouts,
        "interpretation": interp,
    }


# ---------------------------------------------------------------------------
# Self-test (__main__)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    print("=" * 60)
    print("fsm_calc.py — self-test")
    print("=" * 60)

    # 1. Technician utilization
    print("\n--- 1. technician_utilization ---")
    result = technician_utilization(billable_hours=6.2, available_hours=9.0)
    print(json.dumps(result, indent=2))
    assert result["utilization_pct"] == "68.9%", f"Unexpected: {result['utilization_pct']}"

    # 2. First-time-fix rate
    print("\n--- 2. first_time_fix_rate ---")
    result = first_time_fix_rate(jobs_resolved_first_visit=78, total_jobs=100)
    print(json.dumps(result, indent=2))
    assert result["ftf_pct"] == "78.0%", f"Unexpected: {result['ftf_pct']}"

    # 3. MTTR
    print("\n--- 3. mttr ---")
    times = [1.5, 2.0, 0.75, 3.5, 1.0, 2.5, 1.25, 4.0, 1.75, 2.0]
    result = mttr(times)
    print(json.dumps(result, indent=2))
    expected_mean = round(sum(times) / len(times), 2)
    assert result["mttr_hours"] == expected_mean, f"Unexpected mean: {result['mttr_hours']}"

    # 4. Route density
    print("\n--- 4. route_density ---")
    result = route_density(total_jobs=24, total_drive_hours=8.0)
    print(json.dumps(result, indent=2))
    assert result["jobs_per_drive_hour"] == 3.0, f"Unexpected: {result['jobs_per_drive_hour']}"

    # 5. SLA attainment
    print("\n--- 5. sla_attainment ---")
    result = sla_attainment(
        jobs_within_window=92,
        total_jobs_in_tier=100,
        sla_tier_label="Premium 4h",
    )
    print(json.dumps(result, indent=2))
    assert result["attainment_pct"] == "92.0%", f"Unexpected: {result['attainment_pct']}"

    # 6. Truck-stock fill rate
    print("\n--- 6. truck_stock_fill_rate ---")
    result = truck_stock_fill_rate(
        requests_filled_from_stock=88,
        total_parts_requests=100,
        service_level_target=0.95,
    )
    print(json.dumps(result, indent=2))
    assert result["fill_rate_pct"] == "88.0%", f"Unexpected: {result['fill_rate_pct']}"
    assert result["meets_target"] is False

    print("\n" + "=" * 60)
    print("All self-tests passed.")
    print("=" * 60)
