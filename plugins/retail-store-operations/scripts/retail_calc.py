#!/usr/bin/env python3
"""
retail_calc.py — stdlib-only retail store operations calculator.

Modes (pass as first argument):
  gmroi               GMROI = Gross Margin $ / Average Inventory at Cost
  sell_through        Sell-through % = (Units Sold / Units Received) * 100
  shrink_pct          Shrink % = (Shrink $ / Net Sales $) * 100
  weeks_of_supply     WOS = On-Hand Units / Average Weekly Sales
  conversion_rate     Conversion % = (Transactions / Traffic Count) * 100
  sales_per_labor_hour  SPLH = Net Sales $ / Total Labor Hours

All inputs are positional. Run without arguments to see usage.
Run with --self-test to execute the built-in self-test suite.

IMPORTANT: This is a calculator, not a data source. The user supplies every input.
Outputs are decision-support only — not accounting, audit, tax, or investment advice.
"""

import sys
from typing import Callable

# ---------------------------------------------------------------------------
# Core calculation functions
# ---------------------------------------------------------------------------


def gmroi(gross_margin_dollars: float, avg_inventory_at_cost: float) -> float:
    """
    Gross Margin Return on Inventory Investment.

    GMROI = Gross Margin $ / Average Inventory at Cost

    A GMROI < 1.0 means the category returns less in margin than the cost
    of inventory tied up. Use average inventory AT COST — not retail value.

    Args:
        gross_margin_dollars: Total gross margin dollars for the period.
        avg_inventory_at_cost: Average inventory on hand at cost for the period.

    Returns:
        GMROI as a float (e.g. 2.4 = $2.40 returned per $1.00 of inventory cost).

    Raises:
        ValueError: if avg_inventory_at_cost is zero or negative.
    """
    if avg_inventory_at_cost <= 0:
        raise ValueError(
            "avg_inventory_at_cost must be > 0. "
            "Use average inventory at COST, not retail value."
        )
    return gross_margin_dollars / avg_inventory_at_cost


def sell_through(units_sold: float, units_received: float) -> float:
    """
    Sell-through percentage.

    Sell-through % = (Units Sold / Units Received) * 100

    Measures how much of the received inventory has been sold.
    Compare against season-target sell-through at this point in the calendar
    to determine markdown-or-hold.

    Args:
        units_sold: Total units sold in the period.
        units_received: Total units received / opened-to-buy for the period.

    Returns:
        Sell-through as a percentage (0–100+, can exceed 100 if sold from
        prior-period carry-in).

    Raises:
        ValueError: if units_received is zero or negative.
    """
    if units_received <= 0:
        raise ValueError("units_received must be > 0.")
    return (units_sold / units_received) * 100.0


def shrink_pct(shrink_dollars: float, net_sales_dollars: float) -> float:
    """
    Shrink as a percentage of net sales.

    Shrink % = (Shrink $ / Net Sales $) * 100

    Shrink $ = (Beginning Inventory + Purchases - Ending Inventory) - Recorded Sales
    (i.e., the unexplained inventory loss).

    NOTE: A blended shrink % without a root-cause decomposition (operational /
    internal / external) is a symptom, not a diagnosis. Decompose before acting.

    Args:
        shrink_dollars: Dollar value of inventory shrinkage for the period.
        net_sales_dollars: Net sales for the same period.

    Returns:
        Shrink percentage (e.g. 1.8 = 1.8% of net sales).

    Raises:
        ValueError: if net_sales_dollars is zero or negative.
    """
    if net_sales_dollars <= 0:
        raise ValueError("net_sales_dollars must be > 0.")
    return (shrink_dollars / net_sales_dollars) * 100.0


def weeks_of_supply(on_hand_units: float, avg_weekly_sales: float) -> float:
    """
    Weeks of supply on hand.

    WOS = On-Hand Units / Average Weekly Sales

    Pair with sell-through rate and weeks remaining in season to drive
    markdown-or-hold decisions. A WOS below 2 weeks on a fast mover
    is an immediate replenishment trigger.

    Args:
        on_hand_units: Current physical on-hand units (shrink-adjusted if available).
        avg_weekly_sales: Average units sold per week (rolling 4–8 week window).

    Returns:
        Weeks of supply as a float.

    Raises:
        ValueError: if avg_weekly_sales is zero or negative.
    """
    if avg_weekly_sales <= 0:
        raise ValueError("avg_weekly_sales must be > 0.")
    return on_hand_units / avg_weekly_sales


def conversion_rate(transactions: float, traffic_count: float) -> float:
    """
    Store conversion rate.

    Conversion % = (Transactions / Traffic Count) * 100

    Measures the proportion of store visitors who make a purchase.
    A conversion-rate decline without a traffic decline suggests a floor-execution
    or assortment problem, not a demand problem.

    Args:
        transactions: Number of sales transactions in the period.
        traffic_count: Number of customer visits (traffic counter) in the period.

    Returns:
        Conversion rate as a percentage (e.g. 28.5 = 28.5%).

    Raises:
        ValueError: if traffic_count is zero or negative.
    """
    if traffic_count <= 0:
        raise ValueError("traffic_count must be > 0.")
    return (transactions / traffic_count) * 100.0


def sales_per_labor_hour(net_sales_dollars: float, total_labor_hours: float) -> float:
    """
    Sales per labor hour (SPLH).

    SPLH = Net Sales $ / Total Labor Hours

    The primary operating metric for labor efficiency. A declining SPLH while
    labor % holds flat indicates a demand/traffic problem. A rising labor %
    with flat SPLH indicates a rate (wage) problem.

    Args:
        net_sales_dollars: Net sales for the period.
        total_labor_hours: Total labor hours worked (or scheduled) in the period.

    Returns:
        Sales per labor hour as a dollar amount.

    Raises:
        ValueError: if total_labor_hours is zero or negative.
    """
    if total_labor_hours <= 0:
        raise ValueError("total_labor_hours must be > 0.")
    return net_sales_dollars / total_labor_hours


# ---------------------------------------------------------------------------
# CLI dispatch
# ---------------------------------------------------------------------------

_MODES: dict[str, tuple[Callable, list[str], str]] = {
    "gmroi": (
        lambda args: gmroi(float(args[0]), float(args[1])),
        ["gross_margin_dollars", "avg_inventory_at_cost"],
        "GMROI (gross margin return on inventory investment)",
    ),
    "sell_through": (
        lambda args: sell_through(float(args[0]), float(args[1])),
        ["units_sold", "units_received"],
        "Sell-through %",
    ),
    "shrink_pct": (
        lambda args: shrink_pct(float(args[0]), float(args[1])),
        ["shrink_dollars", "net_sales_dollars"],
        "Shrink % of net sales",
    ),
    "weeks_of_supply": (
        lambda args: weeks_of_supply(float(args[0]), float(args[1])),
        ["on_hand_units", "avg_weekly_sales"],
        "Weeks of supply",
    ),
    "conversion_rate": (
        lambda args: conversion_rate(float(args[0]), float(args[1])),
        ["transactions", "traffic_count"],
        "Conversion rate %",
    ),
    "sales_per_labor_hour": (
        lambda args: sales_per_labor_hour(float(args[0]), float(args[1])),
        ["net_sales_dollars", "total_labor_hours"],
        "Sales per labor hour ($)",
    ),
}


def _usage() -> str:
    lines = ["Usage: retail_calc.py <mode> <arg1> <arg2>\n", "Modes:"]
    for mode, (_, params, desc) in _MODES.items():
        lines.append(f"  {mode:<26} {' '.join(params)}")
        lines.append(f"    → {desc}")
    lines.append("\nRun with --self-test to verify the calculator.")
    return "\n".join(lines)


def _cli(argv: list[str]) -> None:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(_usage())
        return

    if argv[1] == "--self-test":
        _run_self_test()
        return

    mode = argv[1]
    if mode not in _MODES:
        print(f"Unknown mode: {mode}\n", file=sys.stderr)
        print(_usage(), file=sys.stderr)
        sys.exit(1)

    fn, params, desc = _MODES[mode]
    if len(argv) < 2 + len(params):
        print(
            f"Mode '{mode}' requires: {' '.join(params)}\n"
            f"Example: retail_calc.py {mode} {' '.join('<' + p + '>' for p in params)}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        result = fn(argv[2:])
        print(f"{desc}: {result:.4f}")
    except ValueError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        print(f"Unexpected error: {exc}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

_EPSILON = 1e-9


def _assert_close(label: str, got: float, expected: float, tol: float = 1e-6) -> None:
    diff = abs(got - expected)
    if diff > tol:
        raise AssertionError(
            f"FAIL [{label}]: expected {expected}, got {got} (diff {diff})"
        )
    print(f"  PASS  {label}: {got:.6f}")


def _run_self_test() -> None:
    print("retail_calc.py self-test\n")

    # --- gmroi ---
    # Gross margin $50,000; avg inventory at cost $25,000 → GMROI 2.0
    _assert_close("gmroi basic", gmroi(50_000, 25_000), 2.0)
    # GMROI < 1.0: capital-destroying scenario
    _assert_close("gmroi < 1.0", gmroi(10_000, 25_000), 0.4)

    # --- sell_through ---
    # 400 sold out of 1,000 received → 40%
    _assert_close("sell_through 40pct", sell_through(400, 1000), 40.0)
    # 100% sell-through
    _assert_close("sell_through 100pct", sell_through(1000, 1000), 100.0)

    # --- shrink_pct ---
    # $18,000 shrink on $900,000 sales → 2.0%
    _assert_close("shrink_pct 2pct", shrink_pct(18_000, 900_000), 2.0)
    # Small shrink
    _assert_close("shrink_pct 0.5pct", shrink_pct(4_500, 900_000), 0.5)

    # --- weeks_of_supply ---
    # 200 units on hand, 40 avg weekly sales → 5.0 weeks
    _assert_close("weeks_of_supply 5wks", weeks_of_supply(200, 40), 5.0)
    # 1 week of supply — near stockout
    _assert_close("weeks_of_supply 1wk", weeks_of_supply(40, 40), 1.0)

    # --- conversion_rate ---
    # 350 transactions out of 1,400 traffic → 25%
    _assert_close("conversion_rate 25pct", conversion_rate(350, 1400), 25.0)

    # --- sales_per_labor_hour ---
    # $42,000 sales / 300 labor hours → $140/hr
    _assert_close("splh $140", sales_per_labor_hour(42_000, 300), 140.0)

    # --- error cases ---
    errors = [
        ("gmroi zero inv", lambda: gmroi(1000, 0)),
        ("sell_through zero recv", lambda: sell_through(100, 0)),
        ("shrink_pct zero sales", lambda: shrink_pct(100, 0)),
        ("wos zero sales", lambda: weeks_of_supply(100, 0)),
        ("conversion zero traffic", lambda: conversion_rate(100, 0)),
        ("splh zero hours", lambda: sales_per_labor_hour(1000, 0)),
    ]
    for label, fn in errors:
        try:
            fn()
            raise AssertionError(f"FAIL [{label}]: expected ValueError, got none")
        except ValueError:
            print(f"  PASS  {label}: correctly raises ValueError")

    print("\nAll tests passed.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _cli(sys.argv)
