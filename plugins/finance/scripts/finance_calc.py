#!/usr/bin/env python3
"""finance_calc.py - a zero-dependency corporate-finance / FP&A decision calculator.

Removes arithmetic error from four recurring finance decisions an FP&A analyst,
controller, treasury analyst, or financial modeler runs constantly:

  npv-irr         The NPV and IRR of a cash-flow stream (a capex project, a
                  build-vs-buy / lease-vs-buy comparison, an acquisition).
                  Discounts a year-0 outflow + annual flows at a given rate,
                  and bisection-solves the IRR. Pairs with the build-vs-buy and
                  financing decision trees (knowledge/finance-decision-trees.md).

  variance-bridge The PRICE / VOLUME / MIX decomposition of a revenue (or
                  unit-driven cost) variance that sums EXACTLY to the total.
                  Price = (P1-P0)*Q1 ; Volume = (Q1-Q0)*P0 ; Mix is the residual
                  the two-effect split leaves. Pairs with the variance-
                  decomposition tree and variance-root-cause-triage.md.

  runway          The cash trough and run-out from a DIRECT-METHOD weekly (or
                  monthly) stream: opening cash + each period's receipts -
                  disbursements. Prints the period-by-period balance, the
                  deepest trough, and the first period the balance goes
                  negative. Pairs with the 13-week-cash-forecast skill and the
                  cash-shortfall ladder (knowledge/finance-decision-trees.md).

  unit-economics  SaaS unit economics on DEFENSIBLE definitions: gross-margin
                  LTV (not revenue), CAC payback in months, and the LTV:CAC
                  ratio. Forces the gross-margin and churn inputs that the
                  common revenue-LTV shortcut hides. Pairs with
                  knowledge/fpa-decision-support-and-unit-economics.md.

This is a CALCULATOR, not a data source - it does not fetch benchmarks, market
rates, or live actuals. The user supplies every input; the tool does the
arithmetic and shows the formula. Stdlib only (argparse); runs anywhere Python
3.8+ is present.

IMPORTANT: outputs are decision-support, not accounting, audit, tax, or
investment advice (see ../CLAUDE.md sec.3). Source-cite every input and validate
against the entity's actual data before any deliverable (CLAUDE.md sec.3 #1).

Examples
--------
  # NPV + IRR: $100k upfront, then $30k/$40k/$50k/$50k over 4 years at 10%
  python3 finance_calc.py npv-irr --rate 10% --initial 100000 \\
      --flows 30000 40000 50000 50000

  # Price/volume/mix bridge: prior 1000 units @ $50, actual 1100 units @ $48
  python3 finance_calc.py variance-bridge --q0 1000 --p0 50 --q1 1100 --p1 48

  # 13-week runway: $250k opening, weekly receipts and disbursements
  python3 finance_calc.py runway --opening 250000 \\
      --receipts 40000 40000 90000 40000 \\
      --disbursements 60000 200000 50000 60000

  # SaaS unit economics: $1,200 ARPA/yr, 78% GM, 14% annual churn, $3,000 CAC
  python3 finance_calc.py unit-economics --arpa 1200 --gross-margin 78% \\
      --churn 14% --cac 3000
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '10%' or '0.10' into a fraction (0.10)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '10%' or '0.10', got {s!r}")


def _npv(rate: float, initial: float, flows: list[float]) -> float:
    """NPV of a year-0 outflow (entered positive) plus year 1..n flows."""
    total = -initial
    for t, cf in enumerate(flows, start=1):
        total += cf / (1.0 + rate) ** t
    return total


def _irr(initial: float, flows: list[float]) -> float | None:
    """Bisection IRR on -initial + sum(flows). Returns None if no sign change."""
    lo, hi = -0.9999, 10.0
    f_lo = _npv(lo, initial, flows)
    f_hi = _npv(hi, initial, flows)
    if f_lo * f_hi > 0:
        return None  # no bracketed root in [-99.99%, 1000%]
    for _ in range(200):
        mid = (lo + hi) / 2.0
        f_mid = _npv(mid, initial, flows)
        if abs(f_mid) < 1e-6:
            return mid
        if f_lo * f_mid < 0:
            hi = mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2.0


def cmd_npv_irr(args: argparse.Namespace) -> int:
    if not args.flows:
        print("error: --flows needs at least one value", file=sys.stderr)
        return 2

    npv = _npv(args.rate, args.initial, args.flows)
    irr = _irr(args.initial, args.flows)

    print("NPV / IRR - discounted cash-flow project")
    print(f"  discount rate     : {args.rate * 100:g}%")
    print(f"  initial outflow   : {args.initial:,.0f} (year 0)")
    print(f"  inflows (yr 1..{len(args.flows)}) : "
          + ", ".join(f"{cf:,.0f}" for cf in args.flows))
    print(f"  -> NPV            : {npv:,.0f}")
    if irr is None:
        print("  -> IRR            : undefined (no sign change in the flows)")
    else:
        print(f"  -> IRR            : {irr * 100:.2f}%")
    verdict = "ACCEPT (NPV > 0)" if npv > 0 else "REJECT (NPV <= 0)"
    print(f"  -> decision       : {verdict} at this rate")
    print("  note: an NPV decision is only as good as the discount rate. Build WACC")
    print("        from sourced components; compare lease-vs-buy on AFTER-TAX flows.")
    return 0


def cmd_variance_bridge(args: argparse.Namespace) -> int:
    rev0 = args.q0 * args.p0
    rev1 = args.q1 * args.p1
    total = rev1 - rev0

    # Two-effect price/volume split; the residual is the interaction/mix term.
    price_effect = (args.p1 - args.p0) * args.q1
    volume_effect = (args.q1 - args.q0) * args.p0
    mix_effect = total - price_effect - volume_effect

    print("Variance bridge - price / volume / mix")
    print(f"  prior  : {args.q0:,.0f} units @ {args.p0:,.2f} = {rev0:,.0f}")
    print(f"  actual : {args.q1:,.0f} units @ {args.p1:,.2f} = {rev1:,.0f}")
    print(f"  -> total variance : {total:,.0f}")
    print("  decomposition (sums exactly to total):")
    print(f"    price  effect ((P1-P0)*Q1)        : {price_effect:,.0f}")
    print(f"    volume effect ((Q1-Q0)*P0)        : {volume_effect:,.0f}")
    print(f"    mix/interaction (residual)        : {mix_effect:,.0f}")
    check = price_effect + volume_effect + mix_effect
    print(f"    check (price+volume+mix)          : {check:,.0f}")
    print("  note: this is a single-product two-way bridge with the interaction")
    print("        isolated as 'mix'. For a true MULTI-product mix effect, bridge")
    print("        each product line then aggregate (see the variance-decomposition tree).")
    return 0


def cmd_runway(args: argparse.Namespace) -> int:
    if len(args.receipts) != len(args.disbursements):
        print("error: --receipts and --disbursements must have the same count",
              file=sys.stderr)
        return 2

    label = args.period
    print(f"Cash runway - direct-method {label} forecast")
    print(f"  opening cash : {args.opening:,.0f}")
    print(f"  {label:>6} | receipts | disburse | net | ending balance")
    print("  -------+----------+----------+----------+---------------")

    balance = args.opening
    trough = (0, args.opening)  # (period, balance)
    first_negative = None
    for i, (rcv, dsb) in enumerate(zip(args.receipts, args.disbursements), start=1):
        net = rcv - dsb
        balance += net
        if balance < trough[1]:
            trough = (i, balance)
        if first_negative is None and balance < 0:
            first_negative = i
        print(f"  {i:>6} | {rcv:>8,.0f} | {dsb:>8,.0f} | {net:>8,.0f} | {balance:>13,.0f}")

    print()
    print(f"  -> deepest trough : {trough[1]:,.0f} at {label} {trough[0]}")
    if first_negative is not None:
        print(f"  -> cash goes NEGATIVE at {label} {first_negative}")
    else:
        print(f"  -> stays positive across all {len(args.receipts)} {label}s")
    if args.min_buffer is not None:
        breaches = [i for i, _ in
                    _below_buffer(args.opening, args.receipts,
                                  args.disbursements, args.min_buffer)]
        if breaches:
            print(f"  -> breaches the {args.min_buffer:,.0f} minimum buffer at "
                  f"{label}(s): {', '.join(str(b) for b in breaches)}")
        else:
            print(f"  -> never breaches the {args.min_buffer:,.0f} minimum buffer")
    print("  note: timing gap vs structural burn changes the fix. A timing trough is")
    print("        a treasury-lever problem; ongoing burn > inflow escalates to FP&A.")
    return 0


def _below_buffer(opening: float, receipts: list[float],
                  disbursements: list[float], buffer: float):
    """Yield (period, balance) for each period whose ending balance < buffer."""
    balance = opening
    for i, (rcv, dsb) in enumerate(zip(receipts, disbursements), start=1):
        balance += rcv - dsb
        if balance < buffer:
            yield (i, balance)


def cmd_unit_economics(args: argparse.Namespace) -> int:
    if not 0.0 < args.churn <= 1.0:
        print("error: --churn must be in (0%, 100%]", file=sys.stderr)
        return 2
    if args.cac <= 0:
        print("error: --cac must be > 0", file=sys.stderr)
        return 2

    gm_arpa = args.arpa * args.gross_margin            # annual gross profit per account
    avg_lifetime_years = 1.0 / args.churn
    ltv = gm_arpa * avg_lifetime_years                 # gross-margin LTV
    ratio = ltv / args.cac
    monthly_gross_profit = gm_arpa / 12.0
    payback_months = args.cac / monthly_gross_profit if monthly_gross_profit else float("inf")

    print("SaaS unit economics - defensible definitions")
    print(f"  ARPA (annual)          : {args.arpa:,.2f}")
    print(f"  gross margin           : {args.gross_margin * 100:g}%")
    print(f"  annual churn           : {args.churn * 100:g}% "
          f"(avg lifetime {avg_lifetime_years:.2f} yr)")
    print(f"  fully-loaded CAC       : {args.cac:,.2f}")
    print(f"  gross-margin ARPA/yr   : {gm_arpa:,.2f}")
    print(f"  -> LTV (gross-margin)  : {ltv:,.2f}  (ARPA * GM% / churn)")
    print(f"  -> LTV : CAC ratio     : {ratio:.2f} : 1")
    print(f"  -> CAC payback         : {payback_months:.1f} months "
          "(CAC / monthly gross profit)")
    print("  note: LTV is GROSS-MARGIN based, not revenue; CAC must be FULLY LOADED")
    print("        (all S&M comp + tooling + allocation). Read payback against STAGE")
    print("        benchmarks, not an absolute (verify-at-use). One definition per metric.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="finance_calc.py",
        description="Corporate-finance / FP&A decision calculator (stdlib only). "
        "Decision-support, not accounting/audit/tax/investment advice - "
        "validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    npv = sub.add_parser("npv-irr", help="NPV + IRR of a cash-flow stream")
    npv.add_argument("--rate", type=_parse_rate, required=True,
                     help="discount rate, e.g. 10%% or 0.10")
    npv.add_argument("--initial", type=float, required=True,
                     help="year-0 outflow (enter as a positive number)")
    npv.add_argument("--flows", type=float, nargs="+", required=True,
                     help="year 1..n net cash flows (space-separated)")
    npv.set_defaults(func=cmd_npv_irr)

    vb = sub.add_parser("variance-bridge", help="Price/volume/mix variance bridge")
    vb.add_argument("--q0", type=float, required=True, help="prior-period quantity")
    vb.add_argument("--p0", type=float, required=True, help="prior-period price")
    vb.add_argument("--q1", type=float, required=True, help="actual quantity")
    vb.add_argument("--p1", type=float, required=True, help="actual price")
    vb.set_defaults(func=cmd_variance_bridge)

    rw = sub.add_parser("runway", help="Direct-method cash runway + trough")
    rw.add_argument("--opening", type=float, required=True, help="opening cash balance")
    rw.add_argument("--receipts", type=float, nargs="+", required=True,
                    help="per-period cash receipts (space-separated)")
    rw.add_argument("--disbursements", type=float, nargs="+", required=True,
                    help="per-period cash disbursements (space-separated)")
    rw.add_argument("--min-buffer", type=float, default=None,
                    help="minimum-cash buffer / covenant floor to test against")
    rw.add_argument("--period", default="week",
                    help="period label for output (default 'week')")
    rw.set_defaults(func=cmd_runway)

    ue = sub.add_parser("unit-economics", help="SaaS LTV / CAC payback / ratio")
    ue.add_argument("--arpa", type=float, required=True,
                    help="annual revenue per account")
    ue.add_argument("--gross-margin", type=_parse_rate, required=True,
                    help="gross margin, e.g. 78%% or 0.78")
    ue.add_argument("--churn", type=_parse_rate, required=True,
                    help="annual logo/revenue churn, e.g. 14%% or 0.14")
    ue.add_argument("--cac", type=float, required=True,
                    help="fully-loaded customer acquisition cost")
    ue.set_defaults(func=cmd_unit_economics)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
