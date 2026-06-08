#!/usr/bin/env python3
"""
people_calc.py — stdlib-only People Operations calculator for the people-operations-hr plugin.

Functions
---------
comp_ratio(salary, band_midpoint)
    Salary ÷ band midpoint. A comp ratio of 1.0 = exactly at midpoint.

time_to_fill(req_open_date, offer_accept_date)
    Calendar days from requisition open to offer acceptance.

annualized_attrition(separations, avg_headcount)
    (Separations / Average headcount) × 100, expressed as a percentage.

span_of_control(total_individual_contributors, total_managers)
    Total ICs / Total managers — the average number of direct reports per manager.

offer_accept_rate(offers_extended, offers_accepted)
    (Offers accepted / Offers extended) × 100, expressed as a percentage.

All functions raise ValueError for invalid inputs. All outputs are decision-support only —
not legal, tax, or compensation advice.

Usage
-----
    python3 people_calc.py                    # run self-test
    python3 -c "from people_calc import *; print(comp_ratio(115000, 120000))"
"""

from __future__ import annotations

import datetime


# ---------------------------------------------------------------------------
# Core calculations
# ---------------------------------------------------------------------------


def comp_ratio(salary: float, band_midpoint: float) -> float:
    """Return salary / band_midpoint rounded to 4 decimal places.

    A comp ratio of 1.0 means the employee is paid exactly at the band midpoint.
    < 0.90 is typically under-band; > 1.15 is typically above-band.

    Parameters
    ----------
    salary : float
        The employee's total base salary (annualized, in any consistent currency).
    band_midpoint : float
        The midpoint of the compensation band for the employee's level and job family.

    Returns
    -------
    float
        The comp ratio as a decimal (e.g., 0.9583 means 95.83% of midpoint).

    Raises
    ------
    ValueError
        If salary or band_midpoint is not positive.
    """
    if salary <= 0:
        raise ValueError(f"salary must be positive, got {salary}")
    if band_midpoint <= 0:
        raise ValueError(f"band_midpoint must be positive, got {band_midpoint}")
    return round(salary / band_midpoint, 4)


def time_to_fill(req_open_date: str, offer_accept_date: str) -> int:
    """Return calendar days from requisition open to offer acceptance.

    Parameters
    ----------
    req_open_date : str
        The date the requisition was opened, in ISO 8601 format (YYYY-MM-DD).
    offer_accept_date : str
        The date the candidate accepted the offer, in ISO 8601 format (YYYY-MM-DD).

    Returns
    -------
    int
        Number of calendar days (inclusive of start date, exclusive of end date).

    Raises
    ------
    ValueError
        If dates cannot be parsed or if offer_accept_date is before req_open_date.
    """
    try:
        open_dt = datetime.date.fromisoformat(req_open_date)
        accept_dt = datetime.date.fromisoformat(offer_accept_date)
    except ValueError as exc:
        raise ValueError(
            f"Dates must be ISO 8601 (YYYY-MM-DD). Got: '{req_open_date}', '{offer_accept_date}'"
        ) from exc
    delta = (accept_dt - open_dt).days
    if delta < 0:
        raise ValueError(
            f"offer_accept_date ({offer_accept_date}) must be on or after "
            f"req_open_date ({req_open_date})"
        )
    return delta


def annualized_attrition(
    separations: float,
    avg_headcount: float,
    period_months: float = 12.0,
) -> float:
    """Return annualized attrition as a percentage.

    Formula: (separations / avg_headcount) × (12 / period_months) × 100

    If period_months is 12 (the default), this is simply (separations / avg_headcount) × 100.
    Pass a smaller period_months to annualize data from a shorter window (e.g., 3 for a quarter).

    Parameters
    ----------
    separations : float
        Number of employee departures (voluntary + involuntary, unless measuring voluntary only).
    avg_headcount : float
        Average headcount over the period — use (opening headcount + closing headcount) / 2.
    period_months : float
        Length of the measurement period in months. Default is 12 (a full year).

    Returns
    -------
    float
        Annualized attrition rate as a percentage, rounded to 2 decimal places.

    Raises
    ------
    ValueError
        If inputs are invalid.
    """
    if separations < 0:
        raise ValueError(f"separations must be >= 0, got {separations}")
    if avg_headcount <= 0:
        raise ValueError(f"avg_headcount must be positive, got {avg_headcount}")
    if period_months <= 0:
        raise ValueError(f"period_months must be positive, got {period_months}")
    raw_rate = separations / avg_headcount
    annualized_rate = raw_rate * (12.0 / period_months) * 100.0
    return round(annualized_rate, 2)


def span_of_control(
    total_individual_contributors: float,
    total_managers: float,
) -> float:
    """Return average span of control (ICs per manager).

    This is a simple ratio. Typical healthy spans: 5–9 for IC managers; 4–6 for
    managers-of-managers. Spans below 4 suggest over-management; spans above 12 suggest
    under-management (context-dependent — fast-moving consumer teams often run wider spans).

    Parameters
    ----------
    total_individual_contributors : float
        Total number of individual contributors in scope.
    total_managers : float
        Total number of people managers in scope.

    Returns
    -------
    float
        Average number of direct reports per manager, rounded to 2 decimal places.

    Raises
    ------
    ValueError
        If inputs are invalid.
    """
    if total_individual_contributors < 0:
        raise ValueError(
            f"total_individual_contributors must be >= 0, got {total_individual_contributors}"
        )
    if total_managers <= 0:
        raise ValueError(f"total_managers must be positive, got {total_managers}")
    return round(total_individual_contributors / total_managers, 2)


def offer_accept_rate(offers_extended: float, offers_accepted: float) -> float:
    """Return offer acceptance rate as a percentage.

    Industry benchmark: healthy offer-accept rates vary by function and market.
    A rate below 80% typically signals a candidate experience, comp, or competitor problem
    worth investigating.

    Parameters
    ----------
    offers_extended : float
        Total number of formal written offers extended to candidates.
    offers_accepted : float
        Total number of those offers accepted by candidates.

    Returns
    -------
    float
        Offer acceptance rate as a percentage, rounded to 2 decimal places.

    Raises
    ------
    ValueError
        If inputs are invalid or if offers_accepted exceeds offers_extended.
    """
    if offers_extended <= 0:
        raise ValueError(f"offers_extended must be positive, got {offers_extended}")
    if offers_accepted < 0:
        raise ValueError(f"offers_accepted must be >= 0, got {offers_accepted}")
    if offers_accepted > offers_extended:
        raise ValueError(
            f"offers_accepted ({offers_accepted}) cannot exceed "
            f"offers_extended ({offers_extended})"
        )
    return round((offers_accepted / offers_extended) * 100.0, 2)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


def _self_test() -> None:
    """Print example outputs for each function to verify correct behavior."""
    print("=" * 60)
    print("people_calc.py — self-test")
    print("=" * 60)

    # comp_ratio
    cr = comp_ratio(salary=115_000, band_midpoint=120_000)
    print(f"\ncomp_ratio(salary=115000, band_midpoint=120000)")
    print(f"  → {cr}  (employee is at {cr * 100:.2f}% of midpoint)")
    assert 0.9583 == cr, f"Expected 0.9583, got {cr}"

    cr2 = comp_ratio(salary=140_000, band_midpoint=120_000)
    print(f"\ncomp_ratio(salary=140000, band_midpoint=120000)")
    print(f"  → {cr2}  (employee is above midpoint — above-band signal)")
    assert 1.1667 == cr2, f"Expected 1.1667, got {cr2}"

    # time_to_fill
    ttf = time_to_fill("2026-01-15", "2026-03-15")
    print(f"\ntime_to_fill('2026-01-15', '2026-03-15')")
    print(f"  → {ttf} calendar days")
    assert ttf == 59, f"Expected 59, got {ttf}"

    ttf2 = time_to_fill("2026-01-01", "2026-04-01")
    print(f"\ntime_to_fill('2026-01-01', '2026-04-01')")
    print(f"  → {ttf2} calendar days")
    assert ttf2 == 90, f"Expected 90, got {ttf2}"

    # annualized_attrition — full year
    aa = annualized_attrition(separations=22, avg_headcount=100)
    print(f"\nannualized_attrition(separations=22, avg_headcount=100)")
    print(f"  → {aa}%  (full-year; benchmark: SaaS/tech ~15-20%)")
    assert aa == 22.0, f"Expected 22.0, got {aa}"

    # annualized_attrition — annualize from a quarter
    aa_q = annualized_attrition(separations=6, avg_headcount=100, period_months=3)
    print(f"\nannualized_attrition(separations=6, avg_headcount=100, period_months=3)")
    print(f"  → {aa_q}%  (Q1 data annualized — 6/100 × (12/3) × 100)")
    assert aa_q == 24.0, f"Expected 24.0, got {aa_q}"

    # span_of_control
    soc = span_of_control(total_individual_contributors=60, total_managers=8)
    print(f"\nspan_of_control(total_individual_contributors=60, total_managers=8)")
    print(f"  → {soc}  (avg direct reports per manager; healthy: 5–9)")
    assert soc == 7.5, f"Expected 7.5, got {soc}"

    # offer_accept_rate
    oar = offer_accept_rate(offers_extended=40, offers_accepted=34)
    print(f"\noffer_accept_rate(offers_extended=40, offers_accepted=34)")
    print(f"  → {oar}%  (benchmark: healthy = >80%)")
    assert oar == 85.0, f"Expected 85.0, got {oar}"

    oar2 = offer_accept_rate(offers_extended=25, offers_accepted=18)
    print(f"\noffer_accept_rate(offers_extended=25, offers_accepted=18)")
    print(f"  → {oar2}%  (below 80% — investigate comp, experience, or competition)")
    assert oar2 == 72.0, f"Expected 72.0, got {oar2}"

    # Error path — ValueError on bad input
    try:
        comp_ratio(salary=0, band_midpoint=100_000)
        raise AssertionError("Expected ValueError for salary=0")
    except ValueError:
        pass  # expected

    try:
        annualized_attrition(separations=5, avg_headcount=-10)
        raise AssertionError("Expected ValueError for negative avg_headcount")
    except ValueError:
        pass  # expected

    print("\n" + "=" * 60)
    print("All self-tests passed.")
    print("=" * 60)
    print(
        "\nNote: outputs are decision-support only — not legal, tax, "
        "or compensation advice."
    )


if __name__ == "__main__":
    _self_test()
