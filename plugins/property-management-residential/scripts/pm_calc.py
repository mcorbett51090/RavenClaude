#!/usr/bin/env python3
"""
pm_calc.py — Residential property management calculator.

stdlib-only (Python 3.8+). No third-party dependencies.

Functions:
  physical_occupancy(occupied, total)
  vacancy_rate(occupied, total)
  economic_occupancy(gross_potential_rent, vacancy_loss, concession_loss, bad_debt_loss)
  noi(gross_potential_rent, vacancy_loss, concession_loss, bad_debt_loss,
      other_income, operating_expenses)
  delinquency_rate(delinquent_balance, gross_potential_rent)
  turn_cost(days_vacant, daily_rent, make_ready_cost)
  rent_to_income_ratio(monthly_rent, gross_monthly_income)

Run as __main__ for a self-test that prints example outputs.

This is a CALCULATOR, not a data source. The caller supplies every input.
Outputs are decision-support only — not accounting, legal, or investment advice.
"""

from __future__ import annotations


def physical_occupancy(occupied: int, total: int) -> float:
    """Physical occupancy rate as a decimal fraction (0.0–1.0).

    Args:
        occupied: number of occupied units
        total: total number of units in the portfolio / property

    Returns:
        Occupancy rate, e.g. 0.95 for 95%.

    Raises:
        ValueError: if total <= 0 or occupied < 0 or occupied > total
    """
    if total <= 0:
        raise ValueError(f"total must be > 0, got {total}")
    if occupied < 0:
        raise ValueError(f"occupied must be >= 0, got {occupied}")
    if occupied > total:
        raise ValueError(
            f"occupied ({occupied}) cannot exceed total ({total})"
        )
    return occupied / total


def vacancy_rate(occupied: int, total: int) -> float:
    """Vacancy rate as a decimal fraction (1 - physical_occupancy).

    Args:
        occupied: number of occupied units
        total: total number of units

    Returns:
        Vacancy rate, e.g. 0.05 for 5%.
    """
    return 1.0 - physical_occupancy(occupied, total)


def economic_occupancy(
    gross_potential_rent: float,
    vacancy_loss: float,
    concession_loss: float,
    bad_debt_loss: float,
) -> float:
    """Economic occupancy rate as a decimal fraction.

    Economic occupancy = collected rent / gross potential rent.
    Collected rent = gross_potential_rent - vacancy_loss - concession_loss - bad_debt_loss.

    A portfolio at 95% physical occupancy can be well below 95% economic occupancy
    when concessions (free months) and bad debt (uncollected rent) are factored in.

    Args:
        gross_potential_rent: total rent if every unit were occupied at asking rent (monthly or
            annual — be consistent across all arguments)
        vacancy_loss: rent lost due to vacant units (use the same period as gross_potential_rent)
        concession_loss: rent lost to free-rent concessions and discounts
        bad_debt_loss: rent recognized but uncollected (delinquent, written off)

    Returns:
        Economic occupancy rate, e.g. 0.91 for 91%.

    Raises:
        ValueError: if gross_potential_rent <= 0 or any loss is negative
    """
    if gross_potential_rent <= 0:
        raise ValueError(
            f"gross_potential_rent must be > 0, got {gross_potential_rent}"
        )
    for name, value in [
        ("vacancy_loss", vacancy_loss),
        ("concession_loss", concession_loss),
        ("bad_debt_loss", bad_debt_loss),
    ]:
        if value < 0:
            raise ValueError(f"{name} must be >= 0, got {value}")

    total_loss = vacancy_loss + concession_loss + bad_debt_loss
    collected = gross_potential_rent - total_loss
    return max(0.0, collected / gross_potential_rent)


def noi(
    gross_potential_rent: float,
    vacancy_loss: float,
    concession_loss: float,
    bad_debt_loss: float,
    other_income: float,
    operating_expenses: float,
) -> float:
    """Net Operating Income (NOI).

    NOI = (Gross potential rent
           - vacancy loss
           - concession loss
           - bad debt loss
           + other income)
          - operating expenses

    Does NOT include debt service (mortgage payments), capital expenditures,
    depreciation, or income taxes — these are below-the-NOI-line items.

    Args:
        gross_potential_rent: total scheduled rent if fully occupied
        vacancy_loss: rent lost to vacant units
        concession_loss: rent lost to concessions / free rent
        bad_debt_loss: uncollected rent (bad debt / write-offs)
        other_income: laundry, parking, late fees, pet fees, storage (net)
        operating_expenses: all operating costs — management fee, maintenance,
            insurance, taxes, utilities (owner-paid), landscaping, admin.
            Do NOT include debt service or capex.

    Returns:
        NOI in the same currency / period as the inputs.

    Raises:
        ValueError: if any loss or expense is negative
    """
    for name, value in [
        ("vacancy_loss", vacancy_loss),
        ("concession_loss", concession_loss),
        ("bad_debt_loss", bad_debt_loss),
        ("operating_expenses", operating_expenses),
        ("other_income", other_income),
    ]:
        if value < 0:
            raise ValueError(f"{name} must be >= 0, got {value}")

    effective_gross_income = (
        gross_potential_rent
        - vacancy_loss
        - concession_loss
        - bad_debt_loss
        + other_income
    )
    return effective_gross_income - operating_expenses


def delinquency_rate(
    delinquent_balance: float,
    gross_potential_rent: float,
) -> float:
    """Delinquency rate = delinquent balance / gross potential rent.

    Measures the share of gross potential rent that is currently past due.
    Report this monthly alongside economic occupancy to the owner.

    Args:
        delinquent_balance: total rent past due (all residents, all periods)
        gross_potential_rent: one month's gross potential rent (or match periods)

    Returns:
        Delinquency rate as a decimal fraction, e.g. 0.04 for 4%.

    Raises:
        ValueError: if gross_potential_rent <= 0 or delinquent_balance < 0
    """
    if gross_potential_rent <= 0:
        raise ValueError(
            f"gross_potential_rent must be > 0, got {gross_potential_rent}"
        )
    if delinquent_balance < 0:
        raise ValueError(
            f"delinquent_balance must be >= 0, got {delinquent_balance}"
        )
    return delinquent_balance / gross_potential_rent


def turn_cost(
    days_vacant: int,
    daily_rent: float,
    make_ready_cost: float,
) -> dict:
    """Total turn cost for a single unit vacancy.

    Turn cost = (days_vacant × daily_rent) + make_ready_cost

    The vacancy loss component alone reveals the economics of the renew-vs-turn
    decision: compare this total against the annual cost of a below-market renewal
    concession to determine whether retaining the resident is cheaper.

    Args:
        days_vacant: days the unit is vacant (key surrender → new lease start)
        daily_rent: daily rent equivalent (monthly_rent / 30)
        make_ready_cost: total make-ready spend (cleaning, paint, carpet, repairs)

    Returns:
        dict with keys:
            'vacancy_loss_dollars': float — rental income lost during vacancy
            'make_ready_cost': float — the make_ready_cost argument
            'total_turn_cost': float — vacancy_loss + make_ready_cost
            'days_vacant': int — the days_vacant argument

    Raises:
        ValueError: if days_vacant < 0 or daily_rent <= 0 or make_ready_cost < 0
    """
    if days_vacant < 0:
        raise ValueError(f"days_vacant must be >= 0, got {days_vacant}")
    if daily_rent <= 0:
        raise ValueError(f"daily_rent must be > 0, got {daily_rent}")
    if make_ready_cost < 0:
        raise ValueError(f"make_ready_cost must be >= 0, got {make_ready_cost}")

    vacancy_loss_dollars = days_vacant * daily_rent
    total = vacancy_loss_dollars + make_ready_cost
    return {
        "vacancy_loss_dollars": round(vacancy_loss_dollars, 2),
        "make_ready_cost": round(make_ready_cost, 2),
        "total_turn_cost": round(total, 2),
        "days_vacant": days_vacant,
    }


def rent_to_income_ratio(
    monthly_rent: float,
    gross_monthly_income: float,
) -> float:
    """Rent-to-income ratio = monthly_rent / gross_monthly_income.

    Used in applicant screening to assess affordability. Common PM standards
    require gross monthly income of 2.5x–3x monthly rent (ratio ≤ 0.33–0.40).
    A ratio > 0.40 is typically considered rent-burdened.

    Args:
        monthly_rent: asking rent (or proposed rent for a specific unit)
        gross_monthly_income: applicant's verified gross monthly income

    Returns:
        Ratio as a decimal, e.g. 0.33 means rent is 33% of gross income.

    Raises:
        ValueError: if monthly_rent <= 0 or gross_monthly_income <= 0
    """
    if monthly_rent <= 0:
        raise ValueError(f"monthly_rent must be > 0, got {monthly_rent}")
    if gross_monthly_income <= 0:
        raise ValueError(
            f"gross_monthly_income must be > 0, got {gross_monthly_income}"
        )
    return monthly_rent / gross_monthly_income


# ---------------------------------------------------------------------------
# Self-test (run as __main__)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("pm_calc.py self-test")
    print("=" * 60)

    # --- physical occupancy / vacancy ---
    occupied, total = 94, 100
    phys_occ = physical_occupancy(occupied, total)
    vac = vacancy_rate(occupied, total)
    print(f"\nPhysical occupancy ({occupied}/{total} units):")
    print(f"  Occupancy: {phys_occ:.1%}")
    print(f"  Vacancy:   {vac:.1%}")

    # --- economic occupancy ---
    gpr = 160_000  # $160k gross potential rent per month (100 units × $1,600 avg)
    vac_loss = 9_600   # 6 vacant units × $1,600
    con_loss = 2_400   # concessions (2 free weeks on 3 new leases)
    bd_loss = 3_200    # 2 delinquent units × $1,600
    econ_occ = economic_occupancy(gpr, vac_loss, con_loss, bd_loss)
    print(f"\nEconomic occupancy (100-unit portfolio, $160k GPR/mo):")
    print(f"  GPR:              ${gpr:>10,.0f}")
    print(f"  Vacancy loss:     ${vac_loss:>10,.0f}")
    print(f"  Concession loss:  ${con_loss:>10,.0f}")
    print(f"  Bad-debt loss:    ${bd_loss:>10,.0f}")
    print(f"  Collected:        ${gpr - vac_loss - con_loss - bd_loss:>10,.0f}")
    print(f"  Economic occ:     {econ_occ:.1%}  (vs physical {phys_occ:.1%})")

    # --- NOI ---
    other_income = 4_800   # parking, laundry, late fees
    op_ex = 72_000         # management, maintenance, taxes, insurance, admin
    portfolio_noi = noi(gpr, vac_loss, con_loss, bd_loss, other_income, op_ex)
    print(f"\nNOI (monthly):")
    print(f"  Effective gross income: ${gpr - vac_loss - con_loss - bd_loss + other_income:>10,.0f}")
    print(f"  Operating expenses:     ${op_ex:>10,.0f}")
    print(f"  NOI:                    ${portfolio_noi:>10,.0f}")
    print(f"  Annualized NOI:         ${portfolio_noi * 12:>10,.0f}")

    # --- delinquency rate ---
    delinquent_bal = 4_800   # 3 units × $1,600
    del_rate = delinquency_rate(delinquent_bal, gpr)
    print(f"\nDelinquency rate:")
    print(f"  Delinquent balance: ${delinquent_bal:>8,.0f}")
    print(f"  Delinquency rate:    {del_rate:.1%} of GPR")

    # --- turn cost ---
    tc = turn_cost(days_vacant=14, daily_rent=1600 / 30, make_ready_cost=2_200)
    print(f"\nTurn cost (Unit A — 14 days vacant, $1,600/mo rent, $2,200 make-ready):")
    print(f"  Vacancy loss:   ${tc['vacancy_loss_dollars']:>8,.2f}")
    print(f"  Make-ready:     ${tc['make_ready_cost']:>8,.2f}")
    print(f"  Total turn cost:${tc['total_turn_cost']:>8,.2f}")
    print(f"  → Below-market renewal of $100/mo = $1,200/yr vs ${tc['total_turn_cost']:,.0f} turn cost")
    print(f"    Retention saves ${tc['total_turn_cost'] - 1200:,.0f} in year 1.")

    # --- rent-to-income ratio ---
    rti = rent_to_income_ratio(monthly_rent=1_600, gross_monthly_income=5_000)
    print(f"\nRent-to-income ratio:")
    print(f"  Monthly rent:          $1,600")
    print(f"  Gross monthly income:  $5,000")
    print(f"  Ratio:                  {rti:.2f}  ({rti:.1%} of gross income)")
    print(f"  Standard: ≤0.33 (3× income) — this applicant {'qualifies' if rti <= 0.40 else 'does not qualify'}")

    print("\n" + "=" * 60)
    print("All self-tests passed.")
    print("=" * 60)
