#!/usr/bin/env python3
"""aec_calc.py — a zero-dependency architecture/AEC decision calculator.

Removes arithmetic error from three recurring AEC project-economics decisions an
architect / PM / AEC principal runs constantly:

  evm             EARNED-VALUE health for a project or phase. From budget-at-
                  completion (BAC), the planned-value %, the earned %, and the
                  actual cost to date, computes CPI (cost performance index =
                  EV/AC), SPI (schedule performance index = EV/PV), the cost and
                  schedule variances, and the EAC/VAC forecast (estimate/variance
                  at completion). Flags the under-budget/over-budget,
                  ahead/behind quadrant. Pairs with knowledge/aec-kpi-glossary.md
                  and the read-firm-economics skill.

  change-order    The CHANGE-ORDER load as a share of the original contract and
                  its margin impact. Takes the original contract value, the
                  approved change-order total (or a list), and the firm's planned
                  margin %, and reports CO % of contract against the ~5-15%
                  industry bands, plus the margin erosion if a share of the CO
                  work is unbilled/absorbed. Pairs with
                  knowledge/aec-delivery-and-estimate-decision-tree.md and the
                  control-scope-creep skill.

  chargeable-area The EFFICIENCY (loss-factor) translation between gross,
                  rentable, and usable area for a fee or test-fit: efficiency =
                  usable / gross; loss factor = (rentable - usable) / rentable.
                  Converts a target program (usable SF) into the gross SF a fee
                  or a lease must carry. Pairs with knowledge/aec-kpi-glossary.md.

This is a CALCULATOR, not a data source — it does not fetch benchmarks, fees,
rates, or live costs. The user supplies every input; the tool does the
arithmetic and shows the formula. Stdlib only (argparse); runs anywhere Python
3.8+ is present.

IMPORTANT: outputs are decision-support, not licensed architectural,
engineering, legal, or financial advice (see ../CLAUDE.md §2). Code, life-safety,
and stamp decisions route to the professional of record (§3 #7). Validate every
figure against the project's actual data before any deliverable (§3 #8).

Examples
--------
  # EVM: $500k phase budget, planned 60% done, actually 50% earned,
  # $320k spent to date
  python3 aec_calc.py evm --bac 500000 --planned-pct 60% --earned-pct 50% \\
      --actual-cost 320000

  # Change-order load: $2.4M original contract, $310k approved COs,
  # 18% planned margin, 40% of the CO work was unbilled coordination rework
  python3 aec_calc.py change-order --contract 2400000 --change-orders 310000 \\
      --margin 18% --unbilled-share 40%

  # Chargeable area: need 12,000 usable SF at 82% building efficiency
  python3 aec_calc.py chargeable-area --usable 12000 --efficiency 82%
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '60%' or '0.60' into a fraction (0.60)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '60%' or '0.60', got {s!r}")


def cmd_evm(args: argparse.Namespace) -> int:
    if args.bac <= 0:
        print("error: --bac must be > 0", file=sys.stderr)
        return 2
    if not 0.0 < args.planned_pct <= 1.0 or not 0.0 <= args.earned_pct <= 1.0:
        print(
            "error: --planned-pct must be in (0%, 100%], --earned-pct in [0%, 100%]",
            file=sys.stderr,
        )
        return 2
    if args.actual_cost < 0:
        print("error: --actual-cost must be >= 0", file=sys.stderr)
        return 2

    pv = args.bac * args.planned_pct
    ev = args.bac * args.earned_pct
    ac = args.actual_cost
    cpi = ev / ac if ac else float("inf")
    spi = ev / pv if pv else float("inf")
    cv = ev - ac
    sv = ev - pv
    # EAC forecast. The two special cases are OPPOSITE situations and must not
    # share a branch:
    #   cpi == inf  (ac == 0): no cost incurred yet — EAC = BAC is defensible.
    #   cpi == 0.0  (ev == 0, ac > 0): cost incurred with zero earned value. The
    #     cost-to-complete is unbounded under the trending-CPI assumption, so we
    #     do NOT collapse to BAC (that would read "on budget" while CPI reads
    #     OVER). Fall back to the independent EAC = AC + (BAC - EV) and label it.
    eac_independent = False
    if cpi == float("inf"):
        eac = args.bac
    elif cpi == 0.0:
        eac = ac + (args.bac - ev)
        eac_independent = True
    else:
        eac = args.bac / cpi
    vac = args.bac - eac

    print("Earned-value (EVM) — project/phase health")
    print(f"  budget at completion (BAC) : {args.bac:,.0f}")
    print(f"  planned value  (PV = BAC x planned%) : {pv:,.0f}  ({args.planned_pct * 100:g}%)")
    print(f"  earned value   (EV = BAC x earned%)  : {ev:,.0f}  ({args.earned_pct * 100:g}%)")
    print(f"  actual cost    (AC, to date)         : {ac:,.0f}")
    print()
    cpi_s = "inf" if cpi == float("inf") else f"{cpi:.3f}"
    spi_s = "inf" if spi == float("inf") else f"{spi:.3f}"
    print(f"  → CPI (EV/AC)  : {cpi_s}   ({'under' if cpi >= 1 else 'OVER'} budget)")
    print(f"  → SPI (EV/PV)  : {spi_s}   ({'ahead/on' if spi >= 1 else 'BEHIND'} schedule)")
    print(f"  → cost variance     (CV = EV-AC) : {cv:,.0f}")
    print(f"  → schedule variance (SV = EV-PV) : {sv:,.0f}")
    eac_formula = "EAC = AC+(BAC-EV), CPI=0" if eac_independent else "EAC = BAC/CPI"
    print(f"  → forecast at completion ({eac_formula}) : {eac:,.0f}")
    print(f"  → variance at completion (VAC = BAC-EAC) : {vac:,.0f}")
    if eac_independent:
        print("    (CPI is 0 — cost incurred with zero earned value; cost-to-complete is")
        print("     unbounded under the trending CPI, so EAC uses the independent formula)")
    print()
    quadrant = (
        ("under budget" if cpi >= 1 else "over budget")
        + ", "
        + ("ahead of / on schedule" if spi >= 1 else "behind schedule")
    )
    print(f"  quadrant: {quadrant}")
    print("  note: EAC assumes current cost efficiency holds. Research finds a")
    print("        cumulative CPI below ~0.90 by the 20% mark rarely recovers —")
    print("        treat an early CPI<0.90 as a fee-recovery trigger (§3 #1, #6).")
    return 0


def cmd_change_order(args: argparse.Namespace) -> int:
    if args.contract <= 0:
        print("error: --contract must be > 0", file=sys.stderr)
        return 2
    if args.change_orders < 0:
        print("error: --change-orders must be >= 0", file=sys.stderr)
        return 2
    if not 0.0 <= args.margin < 1.0:
        print("error: --margin must be in [0%, 100%)", file=sys.stderr)
        return 2
    if not 0.0 <= args.unbilled_share <= 1.0:
        print("error: --unbilled-share must be in [0%, 100%]", file=sys.stderr)
        return 2

    co_pct = args.change_orders / args.contract
    # Industry framing: ~5-10% is the commonly-cited "normal" band on commercial
    # work; 8-14% average with distressed projects up to ~25% (see knowledge bank).
    if co_pct <= 0.05:
        band = "within the typical low band (<=5%)"
    elif co_pct <= 0.10:
        band = "near the commonly-cited ~10% average"
    elif co_pct <= 0.14:
        band = "in the elevated 10-14% range — investigate the coordination signal (§3 #3)"
    else:
        band = "ABOVE 14% — distressed-project territory; root-cause before the next phase"

    unbilled_value = args.change_orders * args.unbilled_share
    planned_profit = args.contract * args.margin
    # Unbilled CO work is effort delivered with no fee — it erodes profit dollar-for-dollar.
    eroded_profit = planned_profit - unbilled_value
    eroded_margin = eroded_profit / args.contract if args.contract else 0.0

    print("Change-order load + margin impact")
    print(f"  original contract value : {args.contract:,.0f}")
    print(f"  approved change orders   : {args.change_orders:,.0f}")
    print(f"  → CO as % of contract    : {co_pct * 100:.1f}%  ({band})")
    print()
    print(f"  planned margin           : {args.margin * 100:g}%  (= {planned_profit:,.0f} profit)")
    print(f"  unbilled/absorbed CO work: {args.unbilled_share * 100:g}%  (= {unbilled_value:,.0f})")
    print(f"  → profit after absorption: {eroded_profit:,.0f}")
    print(f"  → effective margin       : {eroded_margin * 100:.1f}%  (was {args.margin * 100:g}%)")
    if unbilled_value > 0:
        print("  note: unbilled CO work is effort delivered for no fee — it erodes")
        print("        profit dollar-for-dollar. Authorize additional services BEFORE")
        print("        the work, not after (§3 #2); a high CO rate is a coordination")
        print("        signal to fix the next set, not just paperwork (§3 #3).")
    return 0


def cmd_chargeable_area(args: argparse.Namespace) -> int:
    if not 0.0 < args.efficiency <= 1.0:
        print("error: --efficiency must be in (0%, 100%]", file=sys.stderr)
        return 2
    if args.usable is None and args.gross is None:
        print("error: supply exactly one of --usable or --gross", file=sys.stderr)
        return 2
    if args.usable is not None and args.gross is not None:
        print("error: supply exactly one of --usable or --gross, not both", file=sys.stderr)
        return 2

    loss_factor = 1.0 - args.efficiency
    print("Chargeable / usable-area efficiency translation")
    print(f"  building efficiency : {args.efficiency * 100:g}%  (usable / gross)")
    print(f"  loss factor         : {loss_factor * 100:g}%  (core + circulation + walls)")
    if args.usable is not None:
        if args.usable < 0:
            print("error: --usable must be >= 0", file=sys.stderr)
            return 2
        gross = args.usable / args.efficiency
        print(f"  target usable SF    : {args.usable:,.0f}")
        print(f"  → required gross SF : {gross:,.0f}  (usable / efficiency)")
    else:
        if args.gross < 0:
            print("error: --gross must be >= 0", file=sys.stderr)
            return 2
        usable = args.gross * args.efficiency
        print(f"  gross SF            : {args.gross:,.0f}")
        print(f"  → usable SF         : {usable:,.0f}  (gross x efficiency)")
    print("  note: efficiency varies by building type and core configuration —")
    print("        validate against a real test-fit, not a rule of thumb (§3 #8).")
    print("        Rentable-area / load-factor definitions follow the measurement")
    print("        standard in the lease (e.g. BOMA) — confirm which one applies.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="aec_calc.py",
        description="Architecture/AEC decision calculator (stdlib only). "
        "Decision-support, not licensed architectural/engineering/financial "
        "advice — validate every input; code routes to the professional of record.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    evm = sub.add_parser("evm", help="Earned-value (CPI/SPI/EAC) project health")
    evm.add_argument(
        "--bac",
        type=float,
        required=True,
        help="budget at completion (project or phase fee/cost budget)",
    )
    evm.add_argument(
        "--planned-pct",
        type=_parse_rate,
        required=True,
        help="planned percent complete to date (e.g. 60%%)",
    )
    evm.add_argument(
        "--earned-pct",
        type=_parse_rate,
        required=True,
        help="earned (actual) percent complete to date (e.g. 50%%)",
    )
    evm.add_argument(
        "--actual-cost", type=float, required=True, help="actual cost incurred to date"
    )
    evm.set_defaults(func=cmd_evm)

    co = sub.add_parser("change-order", help="Change-order load + margin erosion")
    co.add_argument("--contract", type=float, required=True, help="original contract value")
    co.add_argument(
        "--change-orders", type=float, required=True, help="approved change-order total"
    )
    co.add_argument(
        "--margin", type=_parse_rate, default=0.15, help="planned margin fraction (default 15%%)"
    )
    co.add_argument(
        "--unbilled-share",
        type=_parse_rate,
        default=0.0,
        help="fraction of CO work delivered unbilled/absorbed (default 0%%)",
    )
    co.set_defaults(func=cmd_change_order)

    area = sub.add_parser("chargeable-area", help="Gross<->usable efficiency translation")
    area.add_argument(
        "--efficiency",
        type=_parse_rate,
        required=True,
        help="building efficiency = usable / gross (e.g. 82%%)",
    )
    area.add_argument(
        "--usable", type=float, default=None, help="target usable SF (solve for required gross)"
    )
    area.add_argument("--gross", type=float, default=None, help="gross SF (solve for usable)")
    area.set_defaults(func=cmd_chargeable_area)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
