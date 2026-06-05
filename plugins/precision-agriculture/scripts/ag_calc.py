#!/usr/bin/env python3
"""ag_calc.py — a zero-dependency precision-agriculture decision calculator.

Removes arithmetic error from three recurring farm-economics decisions a grower /
farm manager / ag-retail agronomist runs constantly. It is anchored on the
team's house opinions: per-acre-by-field economics (not whole-farm averages),
and managing to the ECONOMIC optimum (not maximum yield).

  breakeven    The per-field BREAKEVEN squeeze. Given total cost/acre and a
               realistic yield, prints the breakeven PRICE (cost/acre / yield)
               and, given a cash bid, the breakeven YIELD (cost/acre / price)
               and the margin/acre at that bid. Flags an underwater field.
               Pairs with knowledge/ag-economics.md and the
               build-per-acre-economics skill. (CLAUDE.md §3 #4)

  vrt-roi      The VARIABLE-RATE-vs-UNIFORM return-to-seed delta. Compares
               return-to-seed (yield x price - seed cost) of a VR prescription
               against a uniform check, net of the per-acre prescription +
               technology cost, and prints the verdict + the breakeven yield
               lift VR must clear to pay for itself. VR is an economic-optimum
               tool, NOT a yield-maximizer. Pairs with
               knowledge/ag-decision-trees.md. (CLAUDE.md §3 #1, #2)

  input-cost   The per-acre INPUT-COST stack + economic-optimum trim check.
               Sums seed + fertilizer + chemical + other per-acre costs, prints
               the total and each share, and — given the price of the last
               input unit's marginal yield — flags whether the last unit clears
               the economic optimum (marginal return >= marginal cost). Pairs
               with the optimize-input-economics skill. (CLAUDE.md §3 #1)

This is a CALCULATOR, not a data source — it does not fetch prices, yields, or
costs. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not agronomic, legal, or licensed
financial advice (see ../CLAUDE.md §2). It does not set application rates or
guarantee label compliance. Validate every figure against the operation's actual
data and current cash bid before any deliverable (CLAUDE.md §3 #8).

Examples
--------
  # Breakeven on a field at $897/acre cost, 230 bu/acre realistic yield,
  # against a $3.90/bu cash bid
  python3 ag_calc.py breakeven --cost-per-acre 897 --yield 230 --price 3.90

  # VR vs uniform: VR avg 208 bu/ac vs uniform 205 bu/ac, $4.10/bu, VR seed
  # $128/ac vs uniform $122/ac, $4/ac prescription+tech cost
  python3 ag_calc.py vrt-roi --vr-yield 208 --uniform-yield 205 --price 4.10 \\
      --vr-seed-cost 128 --uniform-seed-cost 122 --prescription-cost 4

  # Input-cost stack: $120 seed + $190 fertilizer + $85 chemical + $40 other,
  # last N unit returns 0.3 bu/ac at $4/bu vs $0.55/lb marginal cost
  python3 ag_calc.py input-cost --seed 120 --fertilizer 190 --chemical 85 \\
      --other 40 --marginal-yield 0.3 --price 4.00 --marginal-cost 0.55
"""

from __future__ import annotations

import argparse
import sys


def cmd_breakeven(args: argparse.Namespace) -> int:
    if args.yield_ <= 0:
        print("error: --yield must be > 0", file=sys.stderr)
        return 2
    if args.cost_per_acre < 0:
        print("error: --cost-per-acre must be >= 0", file=sys.stderr)
        return 2

    breakeven_price = args.cost_per_acre / args.yield_
    print("Per-field breakeven (cost/acre / realistic yield)")
    print(f"  total cost/acre        : {args.cost_per_acre:,.2f}")
    print(f"  realistic yield/acre   : {args.yield_:,.1f}")
    print(f"  -> BREAKEVEN PRICE     : {breakeven_price:,.2f} /unit")

    if args.price is not None:
        if args.price <= 0:
            print("error: --price must be > 0", file=sys.stderr)
            return 2
        breakeven_yield = args.cost_per_acre / args.price
        revenue = args.yield_ * args.price
        margin = revenue - args.cost_per_acre
        print(f"  cash bid               : {args.price:,.2f} /unit")
        print(f"  -> BREAKEVEN YIELD     : {breakeven_yield:,.1f} units/acre "
              "(to cover cost at this bid)")
        print(f"  revenue/acre           : {revenue:,.2f}")
        print(f"  -> MARGIN/acre         : {margin:,.2f}")
        if margin < 0:
            print("  *** UNDERWATER at this bid — this field needs a plan "
                  "(rotation switch / input-cost trim), not a prayer (§3 #4).")
        elif breakeven_price > args.price:
            print("  *** breakeven price is ABOVE the cash bid — margin only "
                  "holds if realized yield beats the realistic figure.")
        else:
            print("  field clears breakeven at this bid — confirm against your "
                  "own budget and current cash bid before acting.")
    print("  note: run this PER FIELD on THIS year's cost stack — a whole-farm "
          "average on last year's costs hides the money-losing field (§3 #4).")
    return 0


def cmd_vrt_roi(args: argparse.Namespace) -> int:
    if args.price <= 0:
        print("error: --price must be > 0", file=sys.stderr)
        return 2
    if args.prescription_cost < 0:
        print("error: --prescription-cost must be >= 0", file=sys.stderr)
        return 2

    vr_rts = args.vr_yield * args.price - args.vr_seed_cost
    uniform_rts = args.uniform_yield * args.price - args.uniform_seed_cost
    gross_gain = vr_rts - uniform_rts
    net_gain = gross_gain - args.prescription_cost

    print("Variable-rate vs uniform — return-to-seed (RTS)")
    print(f"  price/unit               : {args.price:,.2f}")
    print(f"  VR:      yield {args.vr_yield:,.1f} x price - seed {args.vr_seed_cost:,.2f} "
          f"= RTS {vr_rts:,.2f}/acre")
    print(f"  uniform: yield {args.uniform_yield:,.1f} x price - seed {args.uniform_seed_cost:,.2f} "
          f"= RTS {uniform_rts:,.2f}/acre")
    print(f"  gross RTS gain (VR - uniform) : {gross_gain:,.2f}/acre")
    print(f"  prescription + tech cost      : {args.prescription_cost:,.2f}/acre")
    print(f"  -> NET RTS gain from VR       : {net_gain:,.2f}/acre")

    # Breakeven yield lift VR must clear vs uniform (holding seed cost delta),
    # to cover the prescription cost: lift * price = prescription_cost + seed_delta
    seed_delta = args.vr_seed_cost - args.uniform_seed_cost
    breakeven_lift = (args.prescription_cost + seed_delta) / args.price
    print(f"  -> breakeven yield lift VR must clear : {breakeven_lift:,.2f} units/acre")

    verdict = "VR PAYS" if net_gain > 0 else "VR does NOT pay on cost"
    print(f"  -> verdict               : {verdict}")
    print("  reminder: VR is an ECONOMIC-OPTIMUM tool (pull seed from low-response")
    print("            zones), NOT a yield-maximizer; validate zones first and measure")
    print("            against a UNIFORM CHECK STRIP — don't assume the lift (§3 #1, #2).")
    return 0


def cmd_input_cost(args: argparse.Namespace) -> int:
    components = {
        "seed": args.seed,
        "fertilizer": args.fertilizer,
        "chemical": args.chemical,
        "other": args.other,
    }
    if any(v < 0 for v in components.values()):
        print("error: cost components must be >= 0", file=sys.stderr)
        return 2
    total = sum(components.values())

    print("Per-acre input-cost stack")
    for name, value in components.items():
        share = (value / total * 100.0) if total else 0.0
        print(f"  {name:<11} : {value:>10,.2f}  ({share:4.1f}%)")
    print(f"  {'TOTAL':<11} : {total:>10,.2f}/acre")

    # Economic-optimum check on the last input unit, if supplied.
    if args.marginal_yield is not None:
        if args.price is None or args.marginal_cost is None:
            print("error: --marginal-yield needs --price and --marginal-cost",
                  file=sys.stderr)
            return 2
        marginal_return = args.marginal_yield * args.price
        print()
        print("  economic-optimum check on the LAST input unit (§3 #1):")
        print(f"    marginal yield of last unit : {args.marginal_yield:,.3f} units/acre")
        print(f"    marginal return (x price)   : {marginal_return:,.3f}/acre")
        print(f"    marginal cost of last unit  : {args.marginal_cost:,.3f}/acre")
        if marginal_return < args.marginal_cost:
            print("    *** PAST the economic optimum — the last unit costs more than")
            print("        it returns; trim it. Manage to economic optimum, not max yield.")
        elif marginal_return == args.marginal_cost:
            print("    at the economic optimum — marginal return == marginal cost.")
        else:
            print("    below the economic optimum — the last unit still pays; more may.")
    print("  note: per-acre BY FIELD, never whole-farm only (§3 #4); recompute against")
    print("        the operation's own costs and current prices before any deliverable.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ag_calc.py",
        description="Precision-agriculture decision calculator (stdlib only). "
        "Decision-support, not agronomic/legal/financial advice — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    be = sub.add_parser("breakeven", help="Per-field breakeven price + yield + margin")
    be.add_argument("--cost-per-acre", type=float, required=True,
                    help="total cost per acre for this field this season")
    be.add_argument("--yield", dest="yield_", type=float, required=True,
                    help="realistic yield per acre (units, e.g. bu/acre)")
    be.add_argument("--price", type=float, default=None,
                    help="current cash bid per unit (optional; enables yield + margin)")
    be.set_defaults(func=cmd_breakeven)

    vr = sub.add_parser("vrt-roi", help="Variable-rate vs uniform return-to-seed delta")
    vr.add_argument("--vr-yield", type=float, required=True, help="VR avg yield/acre")
    vr.add_argument("--uniform-yield", type=float, required=True,
                    help="uniform-rate (check-strip) yield/acre")
    vr.add_argument("--price", type=float, required=True, help="price per unit")
    vr.add_argument("--vr-seed-cost", type=float, required=True, help="VR seed cost/acre")
    vr.add_argument("--uniform-seed-cost", type=float, required=True,
                    help="uniform seed cost/acre")
    vr.add_argument("--prescription-cost", type=float, default=0.0,
                    help="per-acre prescription + VR technology cost (default 0)")
    vr.set_defaults(func=cmd_vrt_roi)

    ic = sub.add_parser("input-cost", help="Per-acre input-cost stack + econ-optimum check")
    ic.add_argument("--seed", type=float, default=0.0, help="seed cost/acre")
    ic.add_argument("--fertilizer", type=float, default=0.0, help="fertilizer cost/acre")
    ic.add_argument("--chemical", type=float, default=0.0, help="crop-protection cost/acre")
    ic.add_argument("--other", type=float, default=0.0, help="other input cost/acre")
    ic.add_argument("--marginal-yield", type=float, default=None,
                    help="yield/acre from the LAST input unit (optional; enables optimum check)")
    ic.add_argument("--price", type=float, default=None, help="price per unit (for optimum check)")
    ic.add_argument("--marginal-cost", type=float, default=None,
                    help="cost of the last input unit (for optimum check)")
    ic.set_defaults(func=cmd_input_cost)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
