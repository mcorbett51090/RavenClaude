#!/usr/bin/env python3
"""embedded_iot_calc.py — a zero-dependency Embedded & IoT Engineering decision calculator.

Removes arithmetic error from 3 recurring embedded & iot engineering decisions:

  power-budget  Average current and battery life from a duty-cycled profile.

  memory-budget Flash and RAM used vs available with headroom.

  bom-cost      Per-unit BOM at a volume tier and target-margin sell price.

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the
client's actual data; route every professional determination to the qualified
authority. No device/telemetry PII belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No device/telemetry PII."
)


def _pct(x):
    return f"{x * 100:.1f}%"


def _money(x):
    return f"${x:,.0f}"


def cmd_power_budget(a):
    if not (0 <= a.active_fraction <= 1):
        print("error: 0 <= --active-fraction <= 1", file=sys.stderr)
        return 2
    if a.active_ma < 0 or a.sleep_ma < 0 or a.battery_mah <= 0 or not (0 < a.derate <= 1):
        print("error: currents >= 0, --battery-mah > 0, 0 < --derate <= 1", file=sys.stderr)
        return 2
    sleep_fraction = 1 - a.active_fraction
    active_contrib = a.active_ma * a.active_fraction
    sleep_contrib = a.sleep_ma * sleep_fraction
    avg_current = active_contrib + sleep_contrib
    if avg_current <= 0:
        print("error: average current must be > 0", file=sys.stderr)
        return 2
    usable_mah = a.battery_mah * a.derate
    life_hours = usable_mah / avg_current
    life_days = life_hours / 24.0
    print("=== Power budget (CLAUDE.md S3 #1) ===")
    print(f"  Active current      : {a.active_ma:g} mA @ {_pct(a.active_fraction)} duty  -> {active_contrib:.4f} mA")
    print(f"  Sleep current       : {a.sleep_ma:g} mA @ {_pct(sleep_fraction)} duty  -> {sleep_contrib:.4f} mA")
    print(f"  >> Average current  : {avg_current:.4f} mA")
    print(f"  Battery (derated)   : {a.battery_mah:g} mAh x {_pct(a.derate)} = {usable_mah:g} mAh usable")
    print(f"  >> Battery life     : {life_hours:,.0f} h  =  {life_days:,.1f} days  =  {life_days/365.0:,.2f} yr")
    dominant = "sleep floor" if sleep_contrib >= active_contrib else "active duty"
    print(f"  >> Dominant sink    : {dominant} — attack it first (S3 #1)")
    print("  NOTE: datasheet currents are starting estimates — date+source and bench-measure (S3 #8).")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_memory_budget(a):
    if a.flash_avail <= 0 or a.ram_avail <= 0:
        print("error: --flash-avail and --ram-avail must be > 0", file=sys.stderr)
        return 2
    if a.flash_used < 0 or a.ram_used < 0:
        print("error: used values must be >= 0", file=sys.stderr)
        return 2
    flash_head = (a.flash_avail - a.flash_used) / a.flash_avail
    ram_head = (a.ram_avail - a.ram_used) / a.ram_avail
    print("=== Memory budget (CLAUDE.md S3 #3) ===")
    print(f"  Flash used / avail  : {a.flash_used:g} / {a.flash_avail:g}  -> headroom {_pct(flash_head)}")
    print(f"  RAM   used / avail  : {a.ram_used:g} / {a.ram_avail:g}  -> headroom {_pct(ram_head)}  (static + worst-case stack/heap)")
    over = []
    if flash_head < 0:
        over.append("FLASH")
    if ram_head < 0:
        over.append("RAM")
    if over:
        print(f"  >> OVER BUDGET: {', '.join(over)} exceeds the part — re-fit or change part (S3 #3)")
    elif flash_head < 0.15 or ram_head < 0.15:
        print("  >> TIGHT: <15% headroom — leave margin for stack peaks + OTA dual-bank (S3 #3 #5)")
    else:
        print("  >> Within budget with headroom")
    print("  NOTE: RAM exhaustion in the field is a brick — budget worst-case stack/heap (S3 #3).")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_bom_cost(a):
    if a.component_cost < 0 or a.assembly_cost < 0:
        print("error: costs must be >= 0", file=sys.stderr)
        return 2
    if not (0 <= a.target_margin < 1):
        print("error: 0 <= --target-margin < 1", file=sys.stderr)
        return 2
    bom_unit = a.component_cost + a.assembly_cost
    print("=== BOM cost (CLAUDE.md S3 #6) ===")
    if a.volume > 0:
        print(f"  Volume tier         : {a.volume:,.0f} units")
    print(f"  Component cost      : {_money(a.component_cost)}")
    print(f"  Assembly/test       : {_money(a.assembly_cost)}")
    print(f"  >> Per-unit BOM     : {_money(bom_unit)}")
    if a.target_margin > 0:
        sell = bom_unit / (1 - a.target_margin)
        print(f"  Target margin       : {_pct(a.target_margin)}")
        print(f"  >> Target sell price: {_money(sell)}  (BOM / (1 - margin))")
    print("  NOTE: the radio module + its certification are part of the BOM — protocol is a cost too (S3 #6).")
    print("        Component prices are volume- and date-specific — date+source them (S3 #8).")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='embedded_iot_calc.py',
        description="Embedded & IoT Engineering decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('power-budget', help='avg current = active x frac + sleep x frac; battery life from mAh')
    sp.add_argument('--active-ma', type=float, required=True, help='active-mode current (mA)')
    sp.add_argument('--active-fraction', type=float, required=True, help='fraction of time active (0-1)')
    sp.add_argument('--sleep-ma', type=float, required=True, help='sleep-mode current (mA)')
    sp.add_argument('--battery-mah', type=float, required=True, help='battery capacity (mAh)')
    sp.add_argument('--derate', type=float, default=0.85, help='usable-capacity derate (0-1, e.g. 0.85)')
    sp.set_defaults(func=cmd_power_budget)

    sp = sub.add_parser('memory-budget', help='per-region flash/RAM headroom % + over-budget flag')
    sp.add_argument('--flash-used', type=float, required=True, help='flash/image used (bytes or KB)')
    sp.add_argument('--flash-avail', type=float, required=True, help='flash available on the part')
    sp.add_argument('--ram-used', type=float, required=True, help='RAM used: static + worst-case stack/heap')
    sp.add_argument('--ram-avail', type=float, required=True, help='RAM available on the part')
    sp.set_defaults(func=cmd_memory_budget)

    sp = sub.add_parser('bom-cost', help='per-unit BOM + sell price at a target margin')
    sp.add_argument('--component-cost', type=float, required=True, help='summed component cost at the volume tier')
    sp.add_argument('--assembly-cost', type=float, default=0.0, help='per-unit assembly/test cost')
    sp.add_argument('--target-margin', type=float, default=0.0, help='target gross margin (0-1)')
    sp.add_argument('--volume', type=float, default=0.0, help='volume tier (units, for context)')
    sp.set_defaults(func=cmd_bom_cost)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
