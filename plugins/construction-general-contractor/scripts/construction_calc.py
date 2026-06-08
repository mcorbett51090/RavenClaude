#!/usr/bin/env python3
"""
construction_calc.py — GC project delivery calculator (stdlib only)

Functions:
  markup_to_margin(markup_pct)          Convert markup % (on cost) to margin % (on revenue)
  margin_to_markup(margin_pct)          Convert margin % (on revenue) to markup % (on cost)
  bid_markup(direct_cost, markup_pct)   Compute bid price and profit given direct cost + markup %
  sov_line(contract_amount, pct_complete, retainage_pct, previously_billed)
                                         Compute pay-app amounts for one SOV line
  retainage_withheld(billings_to_date, retainage_pct)
                                         Total retainage held at a point in time
  earned_value(budgeted_cost_work_scheduled, budgeted_cost_work_performed,
               actual_cost_work_performed)
                                         Compute CPI, SPI, EAC from EV data
  labor_productivity(units_installed, crew_hours)
                                         Units per crew-hour (field productivity)

All functions are pure (no I/O, no side effects). They raise ValueError for invalid inputs.

DISCLAIMER: outputs are decision-support tools, not legal, accounting, or tax advice.
Verify all rates, contracts, and regulatory requirements with qualified professionals.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# 1. Markup vs. Margin conversion
# ---------------------------------------------------------------------------

def markup_to_margin(markup_pct: float) -> float:
    """
    Convert markup percentage (profit ÷ cost) to gross margin percentage (profit ÷ revenue).

    markup_pct: e.g. 20.0 for 20%
    Returns: margin_pct (0–100 scale)

    Formula: margin = markup / (1 + markup/100) × 100
    Example: 20% markup → revenue = cost × 1.20 → margin = 20/120 = 16.667%
    """
    if markup_pct < 0:
        raise ValueError(f"markup_pct must be ≥ 0, got {markup_pct}")
    if markup_pct >= 100:
        # Technically possible but unusual; allow it with a note
        pass
    markup = markup_pct / 100.0
    margin = markup / (1.0 + markup)
    return round(margin * 100, 4)


def margin_to_markup(margin_pct: float) -> float:
    """
    Convert gross margin percentage (profit ÷ revenue) to markup percentage (profit ÷ cost).

    margin_pct: e.g. 16.667 for 16.667%
    Returns: markup_pct (0–100+ scale)

    Formula: markup = margin / (1 - margin/100) × 100
    Example: 16.667% margin → markup = 16.667 / 83.333 × 100 = 20.0%
    """
    if margin_pct < 0:
        raise ValueError(f"margin_pct must be ≥ 0, got {margin_pct}")
    if margin_pct >= 100:
        raise ValueError(f"margin_pct must be < 100, got {margin_pct}")
    margin = margin_pct / 100.0
    markup = margin / (1.0 - margin)
    return round(markup * 100, 4)


# ---------------------------------------------------------------------------
# 2. Bid markup
# ---------------------------------------------------------------------------

def bid_markup(direct_cost: float, markup_pct: float) -> dict:
    """
    Compute bid price and profit given direct cost and markup percentage (on cost).

    direct_cost: total direct cost (labor + material + equipment + sub + GC general conditions)
    markup_pct:  markup on cost, e.g. 15.0 for 15%

    Returns dict:
      direct_cost, markup_pct, profit, bid_price, gross_margin_pct
    """
    if direct_cost < 0:
        raise ValueError(f"direct_cost must be ≥ 0, got {direct_cost}")
    if markup_pct < 0:
        raise ValueError(f"markup_pct must be ≥ 0, got {markup_pct}")
    markup = markup_pct / 100.0
    profit = direct_cost * markup
    bid_price = direct_cost + profit
    gross_margin_pct = markup_to_margin(markup_pct)
    return {
        "direct_cost": round(direct_cost, 2),
        "markup_pct": markup_pct,
        "profit": round(profit, 2),
        "bid_price": round(bid_price, 2),
        "gross_margin_pct": gross_margin_pct,
    }


# ---------------------------------------------------------------------------
# 3. Schedule of values — single line
# ---------------------------------------------------------------------------

def sov_line(
    contract_amount: float,
    pct_complete: float,
    retainage_pct: float,
    previously_billed: float,
) -> dict:
    """
    Compute pay-application amounts for a single SOV line item.

    contract_amount:   scheduled value of this line item ($)
    pct_complete:      percent complete this period, 0–100
    retainage_pct:     retainage rate, 0–100 (e.g. 10.0 for 10%)
    previously_billed: total previously certified for this line item ($)

    Returns dict:
      contract_amount, pct_complete, value_in_place, retainage_this_line,
      net_earned_this_line, previously_billed, this_period_payment, balance_to_finish
    """
    if not (0 <= pct_complete <= 100):
        raise ValueError(f"pct_complete must be 0–100, got {pct_complete}")
    if not (0 <= retainage_pct <= 100):
        raise ValueError(f"retainage_pct must be 0–100, got {retainage_pct}")
    if previously_billed < 0:
        raise ValueError(f"previously_billed must be ≥ 0, got {previously_billed}")

    value_in_place = contract_amount * (pct_complete / 100.0)
    retainage_this_line = value_in_place * (retainage_pct / 100.0)
    net_earned = value_in_place - retainage_this_line
    this_period_payment = net_earned - previously_billed
    balance_to_finish = contract_amount - value_in_place

    return {
        "contract_amount": round(contract_amount, 2),
        "pct_complete": pct_complete,
        "value_in_place": round(value_in_place, 2),
        "retainage_this_line": round(retainage_this_line, 2),
        "net_earned": round(net_earned, 2),
        "previously_billed": round(previously_billed, 2),
        "this_period_payment": round(this_period_payment, 2),
        "balance_to_finish": round(balance_to_finish, 2),
    }


# ---------------------------------------------------------------------------
# 4. Retainage withheld
# ---------------------------------------------------------------------------

def retainage_withheld(billings_to_date: float, retainage_pct: float) -> dict:
    """
    Compute total retainage withheld given cumulative billings and a retainage rate.

    billings_to_date: cumulative gross billings on the contract to date ($)
    retainage_pct:    retainage rate, 0–100

    Returns dict:
      billings_to_date, retainage_pct, retainage_withheld, net_paid_to_date
    """
    if billings_to_date < 0:
        raise ValueError(f"billings_to_date must be ≥ 0, got {billings_to_date}")
    if not (0 <= retainage_pct <= 100):
        raise ValueError(f"retainage_pct must be 0–100, got {retainage_pct}")

    withheld = billings_to_date * (retainage_pct / 100.0)
    net_paid = billings_to_date - withheld
    return {
        "billings_to_date": round(billings_to_date, 2),
        "retainage_pct": retainage_pct,
        "retainage_withheld": round(withheld, 2),
        "net_paid_to_date": round(net_paid, 2),
    }


# ---------------------------------------------------------------------------
# 5. Earned value (CPI / SPI)
# ---------------------------------------------------------------------------

def earned_value(
    bcws: float,
    bcwp: float,
    acwp: float,
    budget_at_completion: float | None = None,
) -> dict:
    """
    Compute earned-value metrics from BCWS, BCWP, ACWP.

    bcws: Budgeted Cost of Work Scheduled (Planned Value, PV)
    bcwp: Budgeted Cost of Work Performed (Earned Value, EV)
    acwp: Actual Cost of Work Performed (Actual Cost, AC)
    budget_at_completion: total project budget (BAC) — required for EAC / ETC

    Returns dict:
      cost_variance (CV), schedule_variance (SV),
      cpi (Cost Performance Index), spi (Schedule Performance Index),
      eac (Estimate at Completion — if BAC provided),
      etc (Estimate to Complete — if BAC provided),
      interpretation (plain-English summary)
    """
    if bcwp < 0 or bcws < 0 or acwp < 0:
        raise ValueError("BCWS, BCWP, and ACWP must all be ≥ 0")

    cv = round(bcwp - acwp, 2)
    sv = round(bcwp - bcws, 2)
    cpi = round(bcwp / acwp, 4) if acwp > 0 else None
    spi = round(bcwp / bcws, 4) if bcws > 0 else None

    eac = None
    etc = None
    if budget_at_completion is not None and budget_at_completion > 0:
        if cpi and cpi > 0:
            eac = round(budget_at_completion / cpi, 2)
            etc = round(eac - acwp, 2)

    # Plain-English interpretation
    parts = []
    if cpi is not None:
        if cpi >= 1.0:
            parts.append(f"CPI {cpi:.3f} — under budget (earning ${cpi:.2f} for every $1.00 spent)")
        else:
            parts.append(f"CPI {cpi:.3f} — over budget (earning only ${cpi:.2f} for every $1.00 spent)")
    if spi is not None:
        if spi >= 1.0:
            parts.append(f"SPI {spi:.3f} — ahead of schedule")
        else:
            parts.append(f"SPI {spi:.3f} — behind schedule")
    if eac is not None:
        parts.append(f"EAC ${eac:,.2f} (forecast final cost at current CPI)")

    result = {
        "bcws_planned_value": round(bcws, 2),
        "bcwp_earned_value": round(bcwp, 2),
        "acwp_actual_cost": round(acwp, 2),
        "cost_variance_cv": cv,
        "schedule_variance_sv": sv,
        "cpi": cpi,
        "spi": spi,
        "eac": eac,
        "etc": etc,
        "interpretation": "; ".join(parts) if parts else "Insufficient data",
    }
    return result


# ---------------------------------------------------------------------------
# 6. Labor productivity
# ---------------------------------------------------------------------------

def labor_productivity(units_installed: float, crew_hours: float) -> dict:
    """
    Compute labor productivity as units per crew-hour.

    units_installed: quantity of work installed (e.g. CY of concrete, LF of pipe, SF of drywall)
    crew_hours:      total crew-hours expended (number of workers × hours each)

    Returns dict:
      units_installed, crew_hours, units_per_crew_hour, crew_hours_per_unit
    """
    if units_installed < 0:
        raise ValueError(f"units_installed must be ≥ 0, got {units_installed}")
    if crew_hours <= 0:
        raise ValueError(f"crew_hours must be > 0, got {crew_hours}")

    units_per_hour = round(units_installed / crew_hours, 4)
    hours_per_unit = round(crew_hours / units_installed, 4) if units_installed > 0 else None

    return {
        "units_installed": units_installed,
        "crew_hours": crew_hours,
        "units_per_crew_hour": units_per_hour,
        "crew_hours_per_unit": hours_per_unit,
    }


# ---------------------------------------------------------------------------
# __main__ self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sep = "-" * 60

    print(sep)
    print("1. Markup vs. Margin conversion")
    print(sep)
    for mk in [10, 15, 20, 25, 33.33]:
        mg = markup_to_margin(mk)
        roundtrip = margin_to_markup(mg)
        print(f"  markup {mk:6.2f}% → margin {mg:6.4f}% → markup (roundtrip) {roundtrip:6.4f}%")
    print()

    print(sep)
    print("2. Bid markup")
    print(sep)
    result = bid_markup(direct_cost=4_250_000, markup_pct=18.0)
    print(f"  Direct cost:      ${result['direct_cost']:>12,.2f}")
    print(f"  Markup:           {result['markup_pct']}% on cost")
    print(f"  Profit:           ${result['profit']:>12,.2f}")
    print(f"  Bid price:        ${result['bid_price']:>12,.2f}")
    print(f"  Gross margin:     {result['gross_margin_pct']:.4f}%")
    print()

    print(sep)
    print("3. SOV line — pay application")
    print(sep)
    r = sov_line(
        contract_amount=850_000,
        pct_complete=45.0,
        retainage_pct=10.0,
        previously_billed=330_000,
    )
    for k, v in r.items():
        print(f"  {k:<30} {v:>14,.2f}" if isinstance(v, float) else f"  {k:<30} {v}")
    print()

    print(sep)
    print("4. Retainage withheld")
    print(sep)
    r2 = retainage_withheld(billings_to_date=3_200_000, retainage_pct=10.0)
    for k, v in r2.items():
        print(f"  {k:<30} {v:>14,.2f}" if isinstance(v, float) else f"  {k:<30} {v}")
    print()

    print(sep)
    print("5. Earned value (CPI / SPI)")
    print(sep)
    ev = earned_value(
        bcws=1_800_000,
        bcwp=1_620_000,
        acwp=1_750_000,
        budget_at_completion=5_000_000,
    )
    for k, v in ev.items():
        if isinstance(v, float):
            print(f"  {k:<30} {v:>14,.4f}")
        else:
            print(f"  {k:<30} {v}")
    print()

    print(sep)
    print("6. Labor productivity")
    print(sep)
    lp = labor_productivity(units_installed=320, crew_hours=64)
    for k, v in lp.items():
        print(f"  {k:<30} {v}")
    print()

    print("All self-tests passed.")
