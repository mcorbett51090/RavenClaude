#!/usr/bin/env python3
"""cre_calc.py — a zero-dependency commercial-real-estate underwriting calculator.

Removes arithmetic error from four recurring CRE decisions an analyst,
acquisitions underwriter, or asset manager runs constantly:

  noi-cap         The income stack and what it implies. Builds NOI bottom-up
                  (gross potential rent − vacancy/credit loss + expense
                  recoveries − operating expenses), then prints the going-in
                  cap rate, the price implied by a target cap rate, and the
                  cap-rate-vs-Treasury SPREAD (the risk premium — CLAUDE.md
                  §3 #3). Pairs with knowledge/cre-underwriting-economics.md.

  debt-size       The loan the deal can carry, sized by the BINDING of three
                  lender constraints — max LTV, min DSCR, and min debt yield —
                  not just LTV. Prints each constraint's max proceeds, the
                  binding one, the resulting DSCR/debt-yield/LTV, and annual
                  cash flow after debt service. Pairs with the debt-stress
                  skill and knowledge/cre-decision-trees.md.

  cash-on-cash    The levered first-year cash return on equity: (NOI − annual
                  debt service) ÷ equity invested, with the equity stack
                  (price + closing + capex reserve − loan). Pairs with the
                  hold-vs-sell tree.

  hold-vs-sell    The hold-vs-sell-vs-refi comparison at an exit-cap shift.
                  Computes net sale proceeds today (at an exit cap on forward
                  NOI, net of selling costs + loan payoff) vs the equity left
                  in the deal, and the simple equity multiple + a rough
                  annualized return on a held year. Pairs with the
                  hold-sell-refi decision tree.

This is a CALCULATOR, not a data source — it does not fetch cap rates,
Treasury yields, rents, or live costs. The user supplies every input; the tool
does the arithmetic and shows the formula. Stdlib only (argparse); runs
anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not investment, legal, or tax advice
(see ../CLAUDE.md §2). Validate every figure against the deal's actual rent
roll, lease abstracts, and a current term sheet before any IC deliverable
(CLAUDE.md §3 #8 — cite the source and date for every market number).

Examples
--------
  # NOI + cap rate + spread: $1.2M GPR, 7% vacancy, $180k recoveries,
  # $520k opex, $14.5M price, target 6.5% cap, 4.15% 10-yr Treasury
  python3 cre_calc.py noi-cap --gpr 1200000 --vacancy 7% --recoveries 180000 \\
      --opex 520000 --price 14500000 --target-cap 6.5% --treasury 4.15%

  # Debt sizing by the binding constraint: $14.5M price, $820k NOI,
  # 6.25% rate, 30-yr amort, 75% max LTV, 1.25x min DSCR, 10% min debt yield
  python3 cre_calc.py debt-size --price 14500000 --noi 820000 --rate 6.25% \\
      --amort-years 30 --max-ltv 75% --min-dscr 1.25 --min-debt-yield 10%

  # Cash-on-cash: $820k NOI, $660k annual debt service, on a $4.2M equity check
  python3 cre_calc.py cash-on-cash --noi 820000 --annual-debt-service 660000 \\
      --equity 4200000

  # Hold vs sell at a cap shift: $850k forward NOI, exit cap 6.75%, 2% selling
  # cost, $9.8M loan payoff, $4.2M equity in, held one year of $820k cash flow
  python3 cre_calc.py hold-vs-sell --forward-noi 850000 --exit-cap 6.75% \\
      --selling-cost 2% --loan-payoff 9800000 --equity 4200000 \\
      --annual-cash-flow 820000
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '6.5%' or '0.065' into a fraction (0.065)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '6.5%' or '0.065', got {s!r}")


def _annual_debt_service(principal: float, annual_rate: float, amort_years: float) -> float:
    """Annual debt service for a fully-amortizing fixed-rate loan.

    Standard mortgage constant: 12 * level monthly payment. If the rate is
    zero, it degenerates to straight principal amortization.
    """
    n = amort_years * 12
    if n <= 0:
        return principal
    r = annual_rate / 12.0
    if r == 0:
        return (principal / n) * 12.0
    payment = principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    return payment * 12.0


def cmd_noi_cap(args: argparse.Namespace) -> int:
    if not 0.0 <= args.vacancy < 1.0:
        print("error: --vacancy must be in [0%, 100%)", file=sys.stderr)
        return 2
    effective_rent = args.gpr * (1.0 - args.vacancy)
    egi = effective_rent + args.recoveries
    noi = egi - args.opex

    print("NOI build-up + cap rate + spread")
    print(f"  gross potential rent (GPR)    : {args.gpr:,.0f}")
    print(f"  less vacancy/credit loss      : -{args.gpr * args.vacancy:,.0f} ({args.vacancy * 100:g}%)")
    print(f"  plus expense recoveries       : +{args.recoveries:,.0f}")
    print(f"  effective gross income (EGI)  : {egi:,.0f}")
    print(f"  less operating expenses       : -{args.opex:,.0f}")
    print(f"  = NET OPERATING INCOME (NOI)  : {noi:,.0f}")

    if noi <= 0:
        print()
        print("  → NOI is zero or negative — no positive cap rate. Re-check opex/vacancy.")
        return 0

    if args.price:
        going_in_cap = noi / args.price
        print(f"  going-in cap (NOI ÷ price)    : {going_in_cap * 100:.2f}% on {args.price:,.0f}")
    if args.target_cap:
        implied_price = noi / args.target_cap
        print(f"  price at {args.target_cap * 100:g}% target cap     : {implied_price:,.0f}")
    if args.treasury is not None and args.price:
        going_in_cap = noi / args.price
        spread_bps = (going_in_cap - args.treasury) * 10000.0
        print(f"  cap-rate-vs-Treasury spread   : {spread_bps:,.0f} bps "
              f"(cap {going_in_cap * 100:.2f}% − 10yr {args.treasury * 100:.2f}%)")
        print("    note: the spread IS the risk premium (§3 #3). A thin spread means")
        print("    you are paid little for risk — say so in the memo, don't bury it.")
    return 0


def cmd_debt_size(args: argparse.Namespace) -> int:
    if not 0.0 < args.max_ltv <= 1.0:
        print("error: --max-ltv must be in (0%, 100%]", file=sys.stderr)
        return 2
    if args.min_dscr <= 0 or args.min_debt_yield <= 0:
        print("error: --min-dscr and --min-debt-yield must be > 0", file=sys.stderr)
        return 2
    if args.amort_years <= 0:
        print("error: --amort-years must be > 0", file=sys.stderr)
        return 2

    # 1) LTV constraint — proceeds capped by loan-to-value.
    ltv_proceeds = args.price * args.max_ltv

    # 2) DSCR constraint — max annual debt service the NOI supports, back into
    #    a principal via the mortgage constant for the given rate/amort.
    max_ads = args.noi / args.min_dscr
    constant = _annual_debt_service(1.0, args.rate, args.amort_years)  # ADS per $1 of loan
    dscr_proceeds = max_ads / constant if constant > 0 else float("inf")

    # 3) Debt-yield constraint — proceeds capped so NOI/loan >= min debt yield.
    dy_proceeds = args.noi / args.min_debt_yield

    binding_value = min(ltv_proceeds, dscr_proceeds, dy_proceeds)
    if binding_value == ltv_proceeds:
        binding = "LTV"
    elif binding_value == dscr_proceeds:
        binding = "DSCR"
    else:
        binding = "debt yield"

    loan = binding_value
    ads = _annual_debt_service(loan, args.rate, args.amort_years)
    actual_dscr = args.noi / ads if ads > 0 else float("inf")
    actual_dy = args.noi / loan if loan > 0 else float("inf")
    actual_ltv = loan / args.price if args.price > 0 else float("inf")
    cash_after_debt = args.noi - ads

    print("Debt sizing — binding of LTV / DSCR / debt yield")
    print(f"  price                         : {args.price:,.0f}")
    print(f"  NOI                           : {args.noi:,.0f}")
    print(f"  rate / amort                  : {args.rate * 100:g}% / {args.amort_years:g}yr")
    print(f"  max proceeds @ {args.max_ltv * 100:g}% LTV      : {ltv_proceeds:,.0f}")
    print(f"  max proceeds @ {args.min_dscr:g}x DSCR      : {dscr_proceeds:,.0f}")
    print(f"  max proceeds @ {args.min_debt_yield * 100:g}% debt yld  : {dy_proceeds:,.0f}")
    print(f"  → BINDING CONSTRAINT          : {binding}")
    print(f"  → loan proceeds               : {loan:,.0f}")
    print(f"    resulting DSCR              : {actual_dscr:.2f}x")
    print(f"    resulting debt yield        : {actual_dy * 100:.2f}%")
    print(f"    resulting LTV               : {actual_ltv * 100:.1f}%")
    print(f"    annual debt service         : {ads:,.0f}")
    print(f"    cash flow after debt        : {cash_after_debt:,.0f}")
    print("  note: in a high-rate market debt yield often binds before LTV — proceeds")
    print("        are capped regardless of how the loan is structured (§3 #6).")
    return 0


def cmd_cash_on_cash(args: argparse.Namespace) -> int:
    if args.equity <= 0:
        print("error: --equity must be > 0", file=sys.stderr)
        return 2
    pre_tax_cash = args.noi - args.annual_debt_service
    coc = pre_tax_cash / args.equity

    print("Cash-on-cash (levered first-year)")
    print(f"  NOI                           : {args.noi:,.0f}")
    print(f"  less annual debt service      : -{args.annual_debt_service:,.0f}")
    print(f"  = pre-tax cash flow           : {pre_tax_cash:,.0f}")
    print(f"  equity invested               : {args.equity:,.0f}")
    print(f"  → CASH-ON-CASH                : {coc * 100:.2f}%")
    if pre_tax_cash < 0:
        print("    → NEGATIVE leverage this year — debt service exceeds NOI; the deal")
        print("      needs reserves to carry, or the basis/rate is wrong.")
    print("  note: cash-on-cash is a single-year snapshot, NOT a return on the whole")
    print("        hold — it ignores amortization, appreciation, and exit (§3 #2).")
    return 0


def cmd_hold_vs_sell(args: argparse.Namespace) -> int:
    if not 0.0 < args.exit_cap < 1.0:
        print("error: --exit-cap must be in (0%, 100%)", file=sys.stderr)
        return 2
    if not 0.0 <= args.selling_cost < 1.0:
        print("error: --selling-cost must be in [0%, 100%)", file=sys.stderr)
        return 2
    if args.equity <= 0:
        print("error: --equity must be > 0", file=sys.stderr)
        return 2

    gross_value = args.forward_noi / args.exit_cap
    selling_costs = gross_value * args.selling_cost
    net_sale_proceeds = gross_value - selling_costs - args.loan_payoff

    print("Hold vs sell — at the exit-cap shift")
    print(f"  forward NOI                   : {args.forward_noi:,.0f}")
    print(f"  exit cap                      : {args.exit_cap * 100:g}%")
    print(f"  gross value (NOI ÷ exit cap)  : {gross_value:,.0f}")
    print(f"  less selling costs            : -{selling_costs:,.0f} ({args.selling_cost * 100:g}%)")
    print(f"  less loan payoff              : -{args.loan_payoff:,.0f}")
    print(f"  = NET SALE PROCEEDS today     : {net_sale_proceeds:,.0f}")
    print(f"  equity invested               : {args.equity:,.0f}")

    equity_multiple = net_sale_proceeds / args.equity if args.equity > 0 else float("inf")
    print(f"  → equity multiple on a sale   : {equity_multiple:.2f}x")

    if args.annual_cash_flow is not None:
        held_total = net_sale_proceeds + args.annual_cash_flow
        held_return = (held_total - args.equity) / args.equity
        print(f"  if held one more year (+{args.annual_cash_flow:,.0f} cash):")
        print(f"    rough one-year total return : {held_return * 100:.1f}% "
              "(cash flow + change in equity value)")
        print("    compare that to your cost of capital / next-best use of the equity.")
    print("  note: the exit cap is the swing assumption — SENSITIZE it, never assume it")
    print("        flat to going-in (§3 — exit cap must be sensitized, not assumed).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cre_calc.py",
        description="Commercial-real-estate underwriting calculator (stdlib only). "
        "Decision-support, not investment/legal/tax advice — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    nc = sub.add_parser("noi-cap", help="NOI build-up + cap rate + Treasury spread")
    nc.add_argument("--gpr", type=float, required=True, help="gross potential rent (annual)")
    nc.add_argument("--vacancy", type=_parse_rate, default=0.0,
                    help="vacancy + credit loss rate (e.g. 7%%)")
    nc.add_argument("--recoveries", type=float, default=0.0, help="expense recoveries (annual)")
    nc.add_argument("--opex", type=float, required=True, help="operating expenses (annual)")
    nc.add_argument("--price", type=float, default=None, help="purchase price (for going-in cap + spread)")
    nc.add_argument("--target-cap", type=_parse_rate, default=None,
                    help="target cap rate to imply a price (e.g. 6.5%%)")
    nc.add_argument("--treasury", type=_parse_rate, default=None,
                    help="10-yr Treasury yield for the spread (e.g. 4.15%%; needs --price)")
    nc.set_defaults(func=cmd_noi_cap)

    ds = sub.add_parser("debt-size", help="Loan sized by the binding of LTV/DSCR/debt-yield")
    ds.add_argument("--price", type=float, required=True, help="purchase price")
    ds.add_argument("--noi", type=float, required=True, help="net operating income (annual)")
    ds.add_argument("--rate", type=_parse_rate, required=True, help="loan interest rate (e.g. 6.25%%)")
    ds.add_argument("--amort-years", type=float, default=30.0, help="amortization period (default 30)")
    ds.add_argument("--max-ltv", type=_parse_rate, default=0.75, help="max loan-to-value (default 75%%)")
    ds.add_argument("--min-dscr", type=float, default=1.25, help="min debt-service coverage (default 1.25)")
    ds.add_argument("--min-debt-yield", type=_parse_rate, default=0.10,
                    help="min debt yield = NOI/loan (default 10%%)")
    ds.set_defaults(func=cmd_debt_size)

    cc = sub.add_parser("cash-on-cash", help="Levered first-year cash-on-cash return")
    cc.add_argument("--noi", type=float, required=True, help="net operating income (annual)")
    cc.add_argument("--annual-debt-service", type=float, required=True, help="annual debt service")
    cc.add_argument("--equity", type=float, required=True, help="equity invested")
    cc.set_defaults(func=cmd_cash_on_cash)

    hs = sub.add_parser("hold-vs-sell", help="Hold vs sell at an exit-cap shift")
    hs.add_argument("--forward-noi", type=float, required=True, help="forward (next-year) NOI")
    hs.add_argument("--exit-cap", type=_parse_rate, required=True, help="exit cap rate (e.g. 6.75%%)")
    hs.add_argument("--selling-cost", type=_parse_rate, default=0.02,
                    help="selling cost as fraction of value (default 2%%)")
    hs.add_argument("--loan-payoff", type=float, default=0.0, help="outstanding loan balance to repay")
    hs.add_argument("--equity", type=float, required=True, help="equity invested")
    hs.add_argument("--annual-cash-flow", type=float, default=None,
                    help="annual cash flow if held one more year (optional)")
    hs.set_defaults(func=cmd_hold_vs_sell)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
