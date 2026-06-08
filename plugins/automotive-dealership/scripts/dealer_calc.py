#!/usr/bin/env python3
"""
dealer_calc.py — Automotive Dealership Calculator (stdlib only, Python 3.8+)

Modes
-----
front_back_gross   Front-end and back-end gross on a single deal
pvr                F&I per-vehicle retailed (PVR) across a period
days_supply        Days-supply for a vehicle segment
absorption         Fixed-ops absorption rate
elr                Effective labor rate (ELR) with dilution summary
recon_holding_cost Reconditioning and holding cost break-even analysis

Usage
-----
  python3 dealer_calc.py <mode> [args ...]
  python3 dealer_calc.py --help

All inputs are numbers. Rates are decimal percentages (e.g., 7.0 = 7%).

This is a decision-support calculator, not accounting, legal, or investment advice.
Outputs should be verified by a qualified professional before use in financial decisions.
"""

from __future__ import annotations

import sys
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# front_back_gross
# ---------------------------------------------------------------------------

def front_back_gross(
    selling_price: float,
    vehicle_cost: float,
    trade_allowance: float,
    trade_acv: float,
    fi_gross: float,
) -> Dict[str, float]:
    """
    Calculate front-end gross, trade spread, back-end (F&I) gross, and total deal gross.

    Parameters
    ----------
    selling_price   : Vehicle selling price agreed with customer ($)
    vehicle_cost    : Dealer's total investment in the vehicle (invoice/purchase + pack + recon)
    trade_allowance : Allowance given to customer for trade-in ($)
    trade_acv       : Actual cash value (ACV) of the trade-in ($, market wholesale)
    fi_gross        : Total F&I gross on this deal ($, reserve + product)

    Returns
    -------
    dict with front_gross, trade_spread, net_front_gross, fi_gross, total_deal_gross
    """
    front_gross = selling_price - vehicle_cost
    trade_spread = trade_acv - trade_allowance  # negative = over-allowance
    net_front_gross = front_gross + trade_spread  # trade_spread is negative when over-allowed
    total_deal_gross = net_front_gross + fi_gross
    return {
        "selling_price": selling_price,
        "vehicle_cost": vehicle_cost,
        "front_gross": front_gross,
        "trade_allowance": trade_allowance,
        "trade_acv": trade_acv,
        "trade_spread": trade_spread,
        "net_front_gross": net_front_gross,
        "fi_gross": fi_gross,
        "total_deal_gross": total_deal_gross,
    }


def _print_front_back_gross(r: Dict[str, float]) -> None:
    sep = "-" * 44
    print(sep)
    print("FRONT / BACK-END GROSS ANALYSIS")
    print(sep)
    print(f"  Selling price:          ${r['selling_price']:>10,.2f}")
    print(f"  Vehicle cost:           ${r['vehicle_cost']:>10,.2f}")
    print(f"  Front-end gross:        ${r['front_gross']:>10,.2f}")
    print()
    print(f"  Trade allowance given:  ${r['trade_allowance']:>10,.2f}")
    print(f"  Trade ACV:              ${r['trade_acv']:>10,.2f}")
    trade_label = "over-allowance" if r["trade_spread"] < 0 else "trade profit"
    print(f"  Trade spread ({trade_label}): ${r['trade_spread']:>10,.2f}")
    print()
    print(f"  Net front-end gross:    ${r['net_front_gross']:>10,.2f}")
    print(f"  F&I gross (back-end):   ${r['fi_gross']:>10,.2f}")
    print(f"  TOTAL DEAL GROSS:       ${r['total_deal_gross']:>10,.2f}")
    print(sep)
    if r["trade_spread"] < 0:
        print(f"  NOTE: Trade is over-allowed by ${abs(r['trade_spread']):,.2f}")


# ---------------------------------------------------------------------------
# pvr
# ---------------------------------------------------------------------------

def pvr(
    total_fi_gross: float,
    units_retailed: int,
    reserve_gross: float = 0.0,
) -> Dict[str, float]:
    """
    Calculate F&I per-vehicle retailed (PVR) and decompose reserve vs product.

    Parameters
    ----------
    total_fi_gross  : Total F&I gross for the period ($)
    units_retailed  : Total retail units for the period
    reserve_gross   : Finance reserve gross for the period ($, optional)

    Returns
    -------
    dict with total_pvr, reserve_pvr, product_pvr
    """
    if units_retailed <= 0:
        raise ValueError("units_retailed must be a positive integer")
    total_pvr = total_fi_gross / units_retailed
    reserve_pvr = reserve_gross / units_retailed
    product_pvr = total_pvr - reserve_pvr
    return {
        "total_fi_gross": total_fi_gross,
        "units_retailed": units_retailed,
        "reserve_gross": reserve_gross,
        "total_pvr": total_pvr,
        "reserve_pvr": reserve_pvr,
        "product_pvr": product_pvr,
    }


def _print_pvr(r: Dict[str, float]) -> None:
    sep = "-" * 44
    print(sep)
    print("F&I PER-VEHICLE RETAILED (PVR)")
    print(sep)
    print(f"  Total F&I gross:        ${r['total_fi_gross']:>10,.2f}")
    print(f"  Units retailed:         {int(r['units_retailed']):>11,}")
    print(f"  Total PVR:              ${r['total_pvr']:>10,.2f}")
    print()
    print(f"  Finance reserve gross:  ${r['reserve_gross']:>10,.2f}")
    print(f"  Reserve PVR:            ${r['reserve_pvr']:>10,.2f}")
    print(f"  Product PVR:            ${r['product_pvr']:>10,.2f}")
    print(sep)
    print("  [verify-at-use: compare against current 20-group benchmarks]")


# ---------------------------------------------------------------------------
# days_supply
# ---------------------------------------------------------------------------

def days_supply(
    units_on_hand: float,
    monthly_retail_rate: float,
    floor_plan_balance: float = 0.0,
    annual_floor_plan_rate_pct: float = 0.0,
) -> Dict[str, float]:
    """
    Calculate days-supply and optional daily floor-plan cost.

    Parameters
    ----------
    units_on_hand            : Units currently on hand (lot + in-transit; exclude recon)
    monthly_retail_rate      : Average units retailed per month
    floor_plan_balance       : Total floor-plan balance on these units ($, optional)
    annual_floor_plan_rate_pct: Annual floor-plan rate as a percentage (e.g., 7.0), optional

    Returns
    -------
    dict with days_supply, daily_fp_cost_total, daily_fp_cost_per_unit
    """
    if monthly_retail_rate <= 0:
        raise ValueError("monthly_retail_rate must be positive")
    ds = (units_on_hand / monthly_retail_rate) * 30
    daily_rate = annual_floor_plan_rate_pct / 100 / 365
    daily_fp_total = floor_plan_balance * daily_rate
    daily_fp_per_unit = daily_fp_total / units_on_hand if units_on_hand > 0 else 0.0
    return {
        "units_on_hand": units_on_hand,
        "monthly_retail_rate": monthly_retail_rate,
        "days_supply": ds,
        "floor_plan_balance": floor_plan_balance,
        "annual_floor_plan_rate_pct": annual_floor_plan_rate_pct,
        "daily_fp_cost_total": daily_fp_total,
        "daily_fp_cost_per_unit": daily_fp_per_unit,
    }


def _print_days_supply(r: Dict[str, float]) -> None:
    sep = "-" * 44
    print(sep)
    print("DAYS-SUPPLY ANALYSIS")
    print(sep)
    print(f"  Units on hand:          {r['units_on_hand']:>11,.0f}")
    print(f"  Monthly retail rate:    {r['monthly_retail_rate']:>11,.1f}")
    print(f"  Days-supply:            {r['days_supply']:>11.1f} days")
    print()
    if r["floor_plan_balance"] > 0:
        print(f"  Floor-plan balance:     ${r['floor_plan_balance']:>10,.0f}")
        print(f"  Annual rate:            {r['annual_floor_plan_rate_pct']:>10.2f}%")
        print(f"  Daily FP cost (total):  ${r['daily_fp_cost_total']:>10,.2f}/day")
        print(f"  Daily FP cost/unit:     ${r['daily_fp_cost_per_unit']:>10,.2f}/unit/day")
    print(sep)
    print("  [verify-at-use: compare days-supply target against current 20-group/OEM data]")


# ---------------------------------------------------------------------------
# absorption
# ---------------------------------------------------------------------------

def absorption(
    service_labor_gross: float,
    service_parts_gross: float,
    body_shop_gross: float,
    total_dealership_overhead: float,
) -> Dict[str, float]:
    """
    Calculate fixed-ops absorption rate.

    Parameters
    ----------
    service_labor_gross       : Service department labor gross ($)
    service_parts_gross       : Service department parts gross ($)
    body_shop_gross           : Body shop gross ($; use 0 if not applicable)
    total_dealership_overhead : Total dealership overhead (fixed + variable) ($)

    Returns
    -------
    dict with fixed_gross, absorption_pct, dollar_gap_to_100pct
    """
    if total_dealership_overhead <= 0:
        raise ValueError("total_dealership_overhead must be positive")
    fixed_gross = service_labor_gross + service_parts_gross + body_shop_gross
    absorption_pct = (fixed_gross / total_dealership_overhead) * 100
    dollar_gap = total_dealership_overhead - fixed_gross  # positive = under-absorbed
    return {
        "service_labor_gross": service_labor_gross,
        "service_parts_gross": service_parts_gross,
        "body_shop_gross": body_shop_gross,
        "fixed_gross": fixed_gross,
        "total_dealership_overhead": total_dealership_overhead,
        "absorption_pct": absorption_pct,
        "dollar_gap_to_100pct": dollar_gap,
    }


def _print_absorption(r: Dict[str, float]) -> None:
    sep = "-" * 44
    print(sep)
    print("FIXED-OPS ABSORPTION RATE")
    print(sep)
    print(f"  Service labor gross:    ${r['service_labor_gross']:>10,.2f}")
    print(f"  Service parts gross:    ${r['service_parts_gross']:>10,.2f}")
    print(f"  Body shop gross:        ${r['body_shop_gross']:>10,.2f}")
    print(f"  TOTAL FIXED GROSS:      ${r['fixed_gross']:>10,.2f}")
    print()
    print(f"  Total overhead:         ${r['total_dealership_overhead']:>10,.2f}")
    print(f"  ABSORPTION RATE:        {r['absorption_pct']:>10.1f}%")
    print()
    if r["dollar_gap_to_100pct"] > 0:
        print(f"  Gap to 100% absorption: ${r['dollar_gap_to_100pct']:>10,.2f}")
    else:
        print(f"  Overhead surplus:       ${abs(r['dollar_gap_to_100pct']):>10,.2f}  (over 100%)")
    print(sep)
    pct = r["absorption_pct"]
    if pct < 70:
        status = "CRITICAL (<70%) — significant structural gap"
    elif pct < 85:
        status = "Below average (70–84%)"
    elif pct < 100:
        status = "Average-good (85–99%)"
    else:
        status = "Excellent (100%+) — overhead fully covered"
    print(f"  Status: {status}")
    print("  [verify-at-use: benchmark ranges from current 20-group data]")


# ---------------------------------------------------------------------------
# elr
# ---------------------------------------------------------------------------

def elr(
    total_labor_sales: float,
    total_hours_sold: float,
    posted_rate: float,
    warranty_dilution: float = 0.0,
    internal_dilution: float = 0.0,
    advisor_discounting: float = 0.0,
    comeback_credits: float = 0.0,
    other_adjustments: float = 0.0,
) -> Dict[str, float]:
    """
    Calculate effective labor rate (ELR) and build a dilution waterfall.

    Parameters
    ----------
    total_labor_sales   : Total labor sales for the period ($)
    total_hours_sold    : Total hours sold (flagged and billed)
    posted_rate         : Posted (door) labor rate ($/hr)
    warranty_dilution   : Average ELR reduction from warranty caps ($/hr)
    internal_dilution   : Average ELR reduction from internal RO pricing ($/hr)
    advisor_discounting : Average ELR reduction from advisor discounts ($/hr)
    comeback_credits    : Average ELR reduction from come-back credits ($/hr)
    other_adjustments   : Other ELR reductions (goodwill, etc.) ($/hr)

    Returns
    -------
    dict with actual_elr, elr_gap, waterfall layers, monthly_impact
    """
    if total_hours_sold <= 0:
        raise ValueError("total_hours_sold must be positive")
    actual_elr = total_labor_sales / total_hours_sold
    elr_gap = posted_rate - actual_elr
    # Monthly impact = gap × hours sold (total lost dollars)
    monthly_gap_dollars = elr_gap * total_hours_sold
    # Waterfall: decompose the gap into its layers (in $/hr)
    waterfall: List[Tuple[str, float]] = [
        ("Warranty dilution", warranty_dilution),
        ("Internal dilution", internal_dilution),
        ("Advisor discounting", advisor_discounting),
        ("Come-back credits", comeback_credits),
        ("Other adjustments", other_adjustments),
    ]
    explained = sum(v for _, v in waterfall)
    unexplained = elr_gap - explained
    return {
        "total_labor_sales": total_labor_sales,
        "total_hours_sold": total_hours_sold,
        "posted_rate": posted_rate,
        "actual_elr": actual_elr,
        "elr_gap": elr_gap,
        "monthly_gap_dollars": monthly_gap_dollars,
        "waterfall": waterfall,
        "unexplained_gap": unexplained,
    }


def _print_elr(r: Dict[str, float]) -> None:
    sep = "-" * 44
    print(sep)
    print("EFFECTIVE LABOR RATE (ELR) WATERFALL")
    print(sep)
    print(f"  Total labor sales:      ${r['total_labor_sales']:>10,.2f}")
    print(f"  Total hours sold:       {r['total_hours_sold']:>11,.1f}")
    print(f"  Posted (door) rate:     ${r['posted_rate']:>10,.2f}/hr")
    print(f"  ACTUAL ELR:             ${r['actual_elr']:>10,.2f}/hr")
    print(f"  ELR gap (posted−actual): ${r['elr_gap']:>9,.2f}/hr")
    print()
    print("  Dilution waterfall ($/hr):")
    for label, val in r["waterfall"]:
        if val != 0:
            print(f"    {label:<28} −${val:>6,.2f}")
    if r["unexplained_gap"] != 0:
        print(f"    {'Unexplained gap':<28} −${r['unexplained_gap']:>6,.2f}")
    print()
    print(f"  Monthly revenue impact: ${r['monthly_gap_dollars']:>10,.2f}")
    print(f"  (ELR gap × hours sold = lost labor revenue vs posted rate)")
    print(sep)


# ---------------------------------------------------------------------------
# recon_holding_cost
# ---------------------------------------------------------------------------

def recon_holding_cost(
    acv: float,
    recon_estimate: float,
    estimated_retail_price: float,
    days_remaining_to_sale: int,
    annual_floor_plan_rate_pct: float,
    other_daily_holding_cost: float = 0.0,
    days_already_held: int = 0,
) -> Dict[str, float]:
    """
    Calculate recon + holding cost and the hold-vs-wholesale break-even threshold.

    Parameters
    ----------
    acv                      : Actual cash value of the unit (market wholesale $)
    recon_estimate           : Estimated total recon cost ($)
    estimated_retail_price   : Expected retail selling price after recon ($)
    days_remaining_to_sale   : Estimated days from today until retail sale
    annual_floor_plan_rate_pct: Annual floor-plan rate as % (e.g., 7.0)
    other_daily_holding_cost : Other daily holding costs (lot, insurance, opportunity, $/day)
    days_already_held        : Days the unit has already been on lot/in recon

    Returns
    -------
    dict with total_investment, expected_retail_gross, daily_fp_cost, total_remaining_holding,
    cumulative_holding_to_date, break_even_recon_threshold, recommendation
    """
    daily_fp_rate = annual_floor_plan_rate_pct / 100 / 365
    # Daily floor-plan cost is on the total investment (acv + recon), approximated on acv
    daily_fp_cost = acv * daily_fp_rate + other_daily_holding_cost
    remaining_holding_cost = daily_fp_cost * days_remaining_to_sale
    holding_to_date = daily_fp_cost * days_already_held
    total_investment = acv + recon_estimate + remaining_holding_cost
    expected_retail_gross = estimated_retail_price - total_investment
    # Break-even: max recon where retail still beats wholesale net
    # wholesale_net ≈ 0 (no additional cost): retail_net must cover acv + recon + remaining holding
    # break_even_recon = (retail_price - acv - remaining_holding) - minimum acceptable gross
    # We set minimum acceptable gross = 0 for the pure break-even
    break_even_recon = estimated_retail_price - acv - remaining_holding_cost
    recommendation = "HOLD" if expected_retail_gross > 0 else "WHOLESALE"
    return {
        "acv": acv,
        "recon_estimate": recon_estimate,
        "estimated_retail_price": estimated_retail_price,
        "days_remaining_to_sale": days_remaining_to_sale,
        "annual_floor_plan_rate_pct": annual_floor_plan_rate_pct,
        "daily_fp_cost": daily_fp_cost,
        "remaining_holding_cost": remaining_holding_cost,
        "holding_cost_to_date": holding_to_date,
        "total_investment": total_investment,
        "expected_retail_gross": expected_retail_gross,
        "break_even_recon_threshold": break_even_recon,
        "recommendation": recommendation,
    }


def _print_recon_holding_cost(r: Dict[str, float]) -> None:
    sep = "-" * 44
    print(sep)
    print("RECON + HOLDING COST — HOLD VS WHOLESALE")
    print(sep)
    print(f"  ACV (market wholesale): ${r['acv']:>10,.2f}")
    print(f"  Recon estimate:         ${r['recon_estimate']:>10,.2f}")
    print(f"  Floor-plan rate:        {r['annual_floor_plan_rate_pct']:>10.2f}% annual")
    print(f"  Daily holding cost:     ${r['daily_fp_cost']:>10,.2f}/day")
    print()
    print(f"  Days held to date:      {r.get('days_already_held', 0):>11,}")
    print(f"  Holding cost to date:   ${r['holding_cost_to_date']:>10,.2f}")
    print()
    print(f"  Days remaining to sale: {r['days_remaining_to_sale']:>11,}")
    print(f"  Remaining holding cost: ${r['remaining_holding_cost']:>10,.2f}")
    print()
    print(f"  Total investment:       ${r['total_investment']:>10,.2f}")
    print(f"  Estimated retail price: ${r['estimated_retail_price']:>10,.2f}")
    print(f"  Expected retail gross:  ${r['expected_retail_gross']:>10,.2f}")
    print()
    print(f"  Break-even recon limit: ${r['break_even_recon_threshold']:>10,.2f}")
    print(f"  (Recon above this threshold = wholesale is better)")
    print()
    arrow = ">>>" if r["recommendation"] == "WHOLESALE" else "   "
    print(f"  {arrow} RECOMMENDATION: {r['recommendation']}")
    print(sep)
    print("  NOTE: Decision-support only. Verify with current market data [verify-at-use].")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

USAGE = """
Usage: python3 dealer_calc.py <mode> [args...]

Modes and required args:
  front_back_gross  selling_price vehicle_cost trade_allowance trade_acv fi_gross
  pvr               total_fi_gross units_retailed [reserve_gross]
  days_supply       units_on_hand monthly_retail_rate [floor_plan_balance annual_rate_pct]
  absorption        service_labor_gross service_parts_gross body_shop_gross total_overhead
  elr               total_labor_sales total_hours_sold posted_rate \\
                    [warranty_dilution internal_dilution advisor_discounting \\
                     comeback_credits other_adjustments]
  recon_holding_cost acv recon_estimate retail_price days_to_sale annual_rate_pct \\
                    [other_daily_holding_cost days_already_held]

All dollar values in $. Rates as percentages (e.g., 7.0 = 7%).
"""


def main(argv: List[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(USAGE)
        return 0
    mode = argv[1]
    args = [float(a) for a in argv[2:]]

    try:
        if mode == "front_back_gross":
            if len(args) < 5:
                print("front_back_gross requires 5 args: selling_price vehicle_cost "
                      "trade_allowance trade_acv fi_gross")
                return 1
            r = front_back_gross(*args[:5])
            _print_front_back_gross(r)

        elif mode == "pvr":
            if len(args) < 2:
                print("pvr requires at least 2 args: total_fi_gross units_retailed [reserve_gross]")
                return 1
            reserve = args[2] if len(args) > 2 else 0.0
            r = pvr(args[0], int(args[1]), reserve)
            _print_pvr(r)

        elif mode == "days_supply":
            if len(args) < 2:
                print("days_supply requires at least 2 args: units_on_hand monthly_retail_rate "
                      "[floor_plan_balance annual_rate_pct]")
                return 1
            fp_bal = args[2] if len(args) > 2 else 0.0
            fp_rate = args[3] if len(args) > 3 else 0.0
            r = days_supply(args[0], args[1], fp_bal, fp_rate)
            _print_days_supply(r)

        elif mode == "absorption":
            if len(args) < 4:
                print("absorption requires 4 args: service_labor_gross service_parts_gross "
                      "body_shop_gross total_overhead")
                return 1
            r = absorption(*args[:4])
            _print_absorption(r)

        elif mode == "elr":
            if len(args) < 3:
                print("elr requires at least 3 args: total_labor_sales total_hours_sold "
                      "posted_rate [warranty_dil internal_dil advisor_dil comeback_dil other]")
                return 1
            optional = list(args[3:8]) + [0.0] * (5 - len(args[3:8]))
            r = elr(args[0], args[1], args[2], *optional[:5])
            _print_elr(r)

        elif mode == "recon_holding_cost":
            if len(args) < 5:
                print("recon_holding_cost requires at least 5 args: acv recon_estimate "
                      "retail_price days_to_sale annual_rate_pct "
                      "[other_daily_holding_cost days_already_held]")
                return 1
            other_daily = args[5] if len(args) > 5 else 0.0
            days_held = int(args[6]) if len(args) > 6 else 0
            r = recon_holding_cost(
                args[0], args[1], args[2], int(args[3]), args[4], other_daily, days_held
            )
            r["days_already_held"] = days_held
            _print_recon_holding_cost(r)

        else:
            print(f"Unknown mode: {mode}")
            print(USAGE)
            return 1

    except (ValueError, ZeroDivisionError) as exc:
        print(f"Error: {exc}")
        return 1

    return 0


# ---------------------------------------------------------------------------
# Self-test (__main__)
# ---------------------------------------------------------------------------

def _self_test() -> None:
    """Print example outputs for every mode to verify the calculator is working."""
    print("=" * 60)
    print("dealer_calc.py — SELF-TEST")
    print("=" * 60)

    # front_back_gross
    print("\n--- Mode: front_back_gross ---")
    r1 = front_back_gross(
        selling_price=32000,
        vehicle_cost=28500,
        trade_allowance=18000,
        trade_acv=16000,
        fi_gross=1400,
    )
    _print_front_back_gross(r1)
    assert r1["front_gross"] == 3500.0, f"Expected 3500, got {r1['front_gross']}"
    assert r1["trade_spread"] == -2000.0, f"Expected -2000, got {r1['trade_spread']}"
    assert r1["net_front_gross"] == 1500.0
    assert r1["total_deal_gross"] == 2900.0

    # pvr
    print("\n--- Mode: pvr ---")
    r2 = pvr(total_fi_gross=198000, units_retailed=150, reserve_gross=75000)
    _print_pvr(r2)
    assert abs(r2["total_pvr"] - 1320.0) < 0.01
    assert abs(r2["reserve_pvr"] - 500.0) < 0.01
    assert abs(r2["product_pvr"] - 820.0) < 0.01

    # days_supply
    print("\n--- Mode: days_supply ---")
    r3 = days_supply(
        units_on_hand=90,
        monthly_retail_rate=60,
        floor_plan_balance=2_250_000,
        annual_floor_plan_rate_pct=7.0,
    )
    _print_days_supply(r3)
    assert abs(r3["days_supply"] - 45.0) < 0.01
    assert r3["daily_fp_cost_total"] > 0

    # absorption
    print("\n--- Mode: absorption ---")
    r4 = absorption(
        service_labor_gross=210_000,
        service_parts_gross=120_000,
        body_shop_gross=20_000,
        total_dealership_overhead=450_000,
    )
    _print_absorption(r4)
    assert abs(r4["absorption_pct"] - 77.78) < 0.01
    assert abs(r4["dollar_gap_to_100pct"] - 100_000) < 0.01

    # elr
    print("\n--- Mode: elr ---")
    r5 = elr(
        total_labor_sales=56_640,
        total_hours_sold=480,
        posted_rate=145.0,
        warranty_dilution=12.0,
        internal_dilution=8.0,
        advisor_discounting=6.0,
        comeback_credits=1.0,
        other_adjustments=0.0,
    )
    _print_elr(r5)
    assert abs(r5["actual_elr"] - 118.0) < 0.01
    assert abs(r5["elr_gap"] - 27.0) < 0.01
    assert abs(r5["monthly_gap_dollars"] - 12_960.0) < 0.01

    # recon_holding_cost
    print("\n--- Mode: recon_holding_cost ---")
    r6 = recon_holding_cost(
        acv=18_000,
        recon_estimate=2_200,
        estimated_retail_price=23_500,
        days_remaining_to_sale=30,
        annual_floor_plan_rate_pct=7.0,
        other_daily_holding_cost=5.0,
        days_already_held=15,
    )
    r6["days_already_held"] = 15
    _print_recon_holding_cost(r6)
    assert r6["daily_fp_cost"] > 0
    assert r6["break_even_recon_threshold"] > 0

    print("\n" + "=" * 60)
    print("All self-tests passed.")
    print("=" * 60)


if __name__ == "__main__":
    # If called with no arguments (or only the script name), run the self-test.
    if len(sys.argv) == 1:
        _self_test()
        sys.exit(0)
    sys.exit(main(sys.argv))
