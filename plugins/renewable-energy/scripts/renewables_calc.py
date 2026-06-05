#!/usr/bin/env python3
"""renewables_calc.py — a zero-dependency renewable-energy decision calculator.

Removes arithmetic error from four recurring solar/storage project decisions a
developer / finance analyst / asset manager runs constantly:

  lcoe            Levelized cost of energy. Discounts lifetime cost (capital +
                  PV of annual O&M) over discounted, degrading lifetime energy.
                  Prints $/MWh. Pairs with knowledge/renewables-economics.md and
                  the model-lcoe-and-irr skill. (LCOE prices the ENERGY; it is
                  NOT project IRR — show both, CLAUDE.md §3 #1.)

  capacity-factor Converts measured/expected annual energy to a capacity factor
                  (and back). CF = annual_MWh / (nameplate_MW x 8760). Pairs with
                  knowledge/renewables-kpi-glossary.md and the capacity-factor
                  underperformance scenario. (CF and availability are DIFFERENT
                  metrics — report both, CLAUDE.md §3.)

  itc-vs-ptc      The mutually-exclusive tax-credit election. ITC = rate x
                  eligible basis (one-time); PTC = PV of per-kWh credit over 10
                  years on degrading production. Prints both + the verdict and
                  margin. Pairs with knowledge/renewables-itc-vs-ptc-decision-tree.md.

  simple-payback  Simple payback (years) on net cost after incentives:
                  net_cost / annual_net_savings, with an undiscounted breakeven
                  year. Pairs with knowledge/renewables-policy-cost-2026.md.

This is a CALCULATOR, not a data source — it does not fetch costs, credits,
prices, or resource data. The user supplies every input; the tool does the
arithmetic and shows the formula. Stdlib only (argparse); runs anywhere Python
3.8+ is present.

IMPORTANT: outputs are decision-support, not tax, legal, engineering (PE), or
licensed financial advice (see ../CLAUDE.md §2). Tax-credit rates, the ITC/PTC
window, and policy figures are jurisdiction- and year-specific and were
reshaped by OBBBA (2025) — confirm every input with current IRS guidance and
tax counsel before any deliverable (CLAUDE.md §3 #3, #8).

Examples
--------
  # LCOE: $1,000,000/MW capital on a 50 MW project, $15,000/MW-yr O&M, 25-yr
  # life, 24% capacity factor, 0.6%/yr degradation, 7% discount rate
  python3 renewables_calc.py lcoe --capital-per-mw 1000000 --mw 50 \\
      --om-per-mw-year 15000 --life-years 25 --capacity-factor 24% \\
      --degradation 0.6% --discount-rate 7%

  # Capacity factor from measured energy: 105,000 MWh/yr on a 50 MW plant
  python3 renewables_calc.py capacity-factor --mw 50 --annual-mwh 105000

  # ITC vs PTC: 30% ITC on $50M eligible basis vs $27.50/MWh PTC over 10 yrs
  # on 105,000 MWh/yr, 0.6%/yr degradation, 7% discount
  python3 renewables_calc.py itc-vs-ptc --itc-rate 30% --eligible-basis 50000000 \\
      --ptc-per-mwh 27.50 --annual-mwh 105000 --degradation 0.6% --discount-rate 7%

  # Simple payback: $1.50/W net on an 8.5 kW system saving $2,200/yr
  python3 renewables_calc.py simple-payback --net-cost 12750 --annual-savings 2200
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '24%' or '0.24' into a fraction (0.24)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"must be like '24%' or '0.24', got {s!r}"
        ) from None


def _annual_energy_mwh(mw: float, capacity_factor: float) -> float:
    """Annual energy (MWh) from nameplate MW and capacity factor over 8760 h."""
    return mw * capacity_factor * 8760.0


def cmd_lcoe(args: argparse.Namespace) -> int:
    if args.life_years < 1:
        print("error: --life-years must be >= 1", file=sys.stderr)
        return 2
    if not 0.0 < args.capacity_factor <= 1.0:
        print("error: --capacity-factor must be in (0%, 100%]", file=sys.stderr)
        return 2
    if args.discount_rate <= -1.0:
        print("error: --discount-rate must be > -100%", file=sys.stderr)
        return 2

    capital = args.capital_per_mw * args.mw
    om_per_year = args.om_per_mw_year * args.mw
    year1_mwh = _annual_energy_mwh(args.mw, args.capacity_factor)

    pv_cost = capital  # capital incurred at t0
    pv_energy = 0.0
    for y in range(1, args.life_years + 1):
        disc = (1.0 + args.discount_rate) ** y
        pv_cost += om_per_year / disc
        energy_y = year1_mwh * (1.0 - args.degradation) ** (y - 1)
        pv_energy += energy_y / disc

    lcoe = pv_cost / pv_energy if pv_energy else float("inf")

    print("LCOE — levelized cost of energy")
    print(f"  nameplate              : {args.mw:g} MW")
    print(f"  capital                : {capital:,.0f} ({args.capital_per_mw:,.0f}/MW)")
    print(f"  O&M                    : {om_per_year:,.0f}/yr ({args.om_per_mw_year:,.0f}/MW-yr)")
    print(f"  capacity factor        : {args.capacity_factor * 100:g}%")
    print(f"  year-1 energy          : {year1_mwh:,.0f} MWh")
    print(f"  degradation            : {args.degradation * 100:g}%/yr")
    print(f"  life / discount rate   : {args.life_years} yr / {args.discount_rate * 100:g}%")
    print(f"  PV of lifetime cost    : {pv_cost:,.0f}")
    print(f"  PV of lifetime energy  : {pv_energy:,.0f} MWh")
    print(f"  -> LCOE                : {lcoe:,.2f} /MWh  ({lcoe / 10.0:,.2f} cents/kWh)")
    print("  note: LCOE prices the ENERGY; it is NOT project IRR (which prices the")
    print("        equity over the hold). Show both (CLAUDE.md S3 #1).")
    return 0


def cmd_capacity_factor(args: argparse.Namespace) -> int:
    if args.mw <= 0:
        print("error: --mw must be > 0", file=sys.stderr)
        return 2
    nameplate_mwh = args.mw * 8760.0
    cf = args.annual_mwh / nameplate_mwh if nameplate_mwh else 0.0

    print("Capacity factor")
    print(f"  nameplate              : {args.mw:g} MW")
    print("  hours/year             : 8760")
    print(f"  max possible energy    : {nameplate_mwh:,.0f} MWh/yr (at 100% CF)")
    print(f"  measured/expected      : {args.annual_mwh:,.0f} MWh/yr")
    print(f"  -> CAPACITY FACTOR     : {cf * 100:.1f}%")
    if args.expected_cf is not None:
        delta = (cf - args.expected_cf) * 100.0
        verdict = "ABOVE" if delta >= 0 else "BELOW"
        print(f"  expected CF            : {args.expected_cf * 100:g}%")
        print(f"  -> vs expected         : {verdict} by {abs(delta):.1f} pts")
        print("    reminder: a CF shortfall can be availability (recoverable),")
        print("    degradation (permanent), OR a low-resource year (P50 vs P90) —")
        print("    decompose before naming a cause. CF != availability.")
    return 0


def cmd_itc_vs_ptc(args: argparse.Namespace) -> int:
    if not 0.0 < args.itc_rate <= 1.0:
        print("error: --itc-rate must be in (0%, 100%]", file=sys.stderr)
        return 2
    if args.discount_rate <= -1.0:
        print("error: --discount-rate must be > -100%", file=sys.stderr)
        return 2

    itc_value = args.itc_rate * args.eligible_basis

    ptc_pv = 0.0
    for y in range(1, args.ptc_years + 1):
        energy_y = args.annual_mwh * (1.0 - args.degradation) ** (y - 1)
        credit_y = args.ptc_per_mwh * energy_y
        ptc_pv += credit_y / (1.0 + args.discount_rate) ** y

    winner = "PTC" if ptc_pv > itc_value else "ITC"
    margin = abs(ptc_pv - itc_value)

    print("ITC vs PTC — tax-credit election (mutually exclusive)")
    print(f"  ITC rate / basis       : {args.itc_rate * 100:g}% of {args.eligible_basis:,.0f}")
    print(f"  -> ITC value (one-time): {itc_value:,.0f}")
    print(f"  PTC rate               : {args.ptc_per_mwh:,.2f}/MWh over {args.ptc_years} yrs")
    print(f"  year-1 production      : {args.annual_mwh:,.0f} MWh")
    print(f"  degradation / discount : {args.degradation * 100:g}%/yr / {args.discount_rate * 100:g}%")
    print(f"  -> PTC value (PV)      : {ptc_pv:,.0f}")
    print(f"  -> WINNER              : {winner} by {margin:,.0f}")
    print("  note: high capacity factor + low CapEx favors PTC; high CapEx or")
    print("        modest resource favors ITC. Layer bonus adders before the call.")
    print("        Decision-support only — the binding election is tax counsel's,")
    print("        and the OBBBA (2025) begin-construction / placed-in-service")
    print("        window gates eligibility (CLAUDE.md S2, S3 #3).")
    return 0


def cmd_simple_payback(args: argparse.Namespace) -> int:
    if args.annual_savings <= 0:
        print("error: --annual-savings must be > 0", file=sys.stderr)
        return 2
    payback = args.net_cost / args.annual_savings
    breakeven_year = -(-args.net_cost // args.annual_savings)  # ceil division

    print("Simple payback (undiscounted)")
    print(f"  net cost after incentives : {args.net_cost:,.0f}")
    print(f"  annual net savings        : {args.annual_savings:,.0f}/yr")
    print(f"  -> SIMPLE PAYBACK         : {payback:,.1f} years")
    print(f"  -> breakeven by year      : {int(breakeven_year)}")
    print("  note: SIMPLE payback ignores the time value of money, escalation,")
    print("        and degradation — use it as a screen, not the investment case.")
    print("        Net cost after incentives is the REAL cost (CLAUDE.md S3 #4).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="renewables_calc.py",
        description="Renewable-energy decision calculator (stdlib only). "
        "Decision-support, not tax/legal/engineering/financial advice — "
        "validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    lcoe = sub.add_parser("lcoe", help="Levelized cost of energy ($/MWh)")
    lcoe.add_argument("--capital-per-mw", type=float, required=True,
                      help="installed capital cost per MW")
    lcoe.add_argument("--mw", type=float, required=True, help="nameplate capacity (MW)")
    lcoe.add_argument("--om-per-mw-year", type=float, default=0.0,
                      help="annual O&M cost per MW (default 0)")
    lcoe.add_argument("--life-years", type=int, default=25,
                      help="economic life in years (default 25)")
    lcoe.add_argument("--capacity-factor", type=_parse_rate, required=True,
                      help="capacity factor (e.g. 24%%)")
    lcoe.add_argument("--degradation", type=_parse_rate, default=0.006,
                      help="annual energy degradation (default 0.6%%)")
    lcoe.add_argument("--discount-rate", type=_parse_rate, default=0.07,
                      help="real discount rate (default 7%%)")
    lcoe.set_defaults(func=cmd_lcoe)

    cf = sub.add_parser("capacity-factor", help="Capacity factor from annual energy")
    cf.add_argument("--mw", type=float, required=True, help="nameplate capacity (MW)")
    cf.add_argument("--annual-mwh", type=float, required=True,
                    help="measured/expected annual energy (MWh)")
    cf.add_argument("--expected-cf", type=_parse_rate, default=None,
                    help="expected CF to compare against (optional, e.g. 25%%)")
    cf.set_defaults(func=cmd_capacity_factor)

    e = sub.add_parser("itc-vs-ptc", help="ITC vs PTC tax-credit election")
    e.add_argument("--itc-rate", type=_parse_rate, required=True,
                   help="ITC rate (e.g. 30%%)")
    e.add_argument("--eligible-basis", type=float, required=True,
                   help="ITC-eligible cost basis")
    e.add_argument("--ptc-per-mwh", type=float, required=True,
                   help="PTC rate per MWh")
    e.add_argument("--annual-mwh", type=float, required=True,
                   help="year-1 annual production (MWh)")
    e.add_argument("--ptc-years", type=int, default=10,
                   help="PTC production-credit years (default 10)")
    e.add_argument("--degradation", type=_parse_rate, default=0.006,
                   help="annual energy degradation (default 0.6%%)")
    e.add_argument("--discount-rate", type=_parse_rate, default=0.07,
                   help="discount rate for PTC PV (default 7%%)")
    e.set_defaults(func=cmd_itc_vs_ptc)

    sp = sub.add_parser("simple-payback", help="Simple payback on net cost")
    sp.add_argument("--net-cost", type=float, required=True,
                    help="net cost after incentives")
    sp.add_argument("--annual-savings", type=float, required=True,
                    help="annual net savings (or net revenue)")
    sp.set_defaults(func=cmd_simple_payback)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
