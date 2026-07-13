#!/usr/bin/env python3
"""evm_calc.py — a zero-dependency project-delivery decision calculator.

Removes arithmetic error from three recurring delivery-management decisions a
project / delivery manager runs constantly across the predictive and agile
tracks:

  evm             EARNED VALUE status + forecast from the three base measures
                  (PV, EV, AC) and the budget (BAC). Prints CV/SV, CPI/SPI, the
                  four standard EAC variants (BAC/CPI; AC+BAC-EV;
                  AC+(BAC-EV)/(CPI*SPI); AC+bottom-up ETC), ETC, VAC, and TCPI,
                  plus a RAG read keyed off CPI/SPI thresholds. Pairs with
                  knowledge/pm-decision-trees.md (the Status-RAG and
                  recover-vs-escalate trees) and best-practices/earned-value-
                  tells-two-stories.md.

  pert            THREE-POINT (PERT/beta) estimate from optimistic / most-likely
                  / pessimistic. Prints the PERT mean (O+4M+P)/6, the standard
                  deviation (P-O)/6, and the +/-1sigma and +/-2sigma confidence
                  bands — the spread that sizes a contingency reserve. Pairs with
                  the estimate-confidence decision tree.

  forecast        AGILE completion FORECAST from remaining backlog size and a
                  sample of recent per-sprint throughput (or velocity). Prints
                  the mean, the conservative (mean-1sigma) and optimistic
                  (mean+1sigma) per-sprint rates, and the sprint count each
                  implies — turning a single velocity number into a range.
                  Pairs with best-practices/velocity-is-descriptive-not-a-
                  target.md.

This is a CALCULATOR, not a data source — it does not fetch baselines, rates, or
benchmarks. The user supplies every input; the tool does the arithmetic and
shows the formula. Stdlib only (argparse + statistics); runs anywhere Python
3.8+ is present.

IMPORTANT: outputs are decision-support, not a governance decision. The numbers
feed the change-control / escalation / RAG decisions the specialists own; they
do not make them. Validate every figure against the project's actual baseline
and the engagement's governance before any deliverable.

Examples
--------
  # Earned value: $100k budget, planned $50k of work by now, $40k earned, $48k spent
  python3 evm_calc.py evm --bac 100000 --pv 50000 --ev 40000 --ac 48000

  # PERT estimate of a work package: 5 / 8 / 17 days
  python3 evm_calc.py pert --optimistic 5 --most-likely 8 --pessimistic 17

  # Agile forecast: 80 items left, last 6 sprints completed 9 11 7 13 10 8
  python3 evm_calc.py forecast --remaining 80 --throughput 9 11 7 13 10 8
"""

from __future__ import annotations

import argparse
import statistics
import sys


def cmd_evm(args: argparse.Namespace) -> int:
    if args.bac <= 0:
        print("error: --bac must be > 0", file=sys.stderr)
        return 2
    if args.ac <= 0 or args.ev <= 0:
        print("error: --ac and --ev must be > 0 to compute indices", file=sys.stderr)
        return 2

    cv = args.ev - args.ac
    sv = args.ev - args.pv
    cpi = args.ev / args.ac
    spi = (args.ev / args.pv) if args.pv > 0 else float("inf")

    eac_trend = args.bac / cpi  # variant 1: current cost trend continues
    eac_budget = args.ac + (args.bac - args.ev)  # variant 2: remainder at budgeted rate
    eac_both = (
        args.ac + (args.bac - args.ev) / (cpi * spi)
        if spi not in (0, float("inf"))
        else float("inf")
    )  # variant 3: cost AND schedule drag remaining work

    etc_trend = (args.bac - args.ev) / cpi
    vac = args.bac - eac_trend
    # TCPI to the original budget: work remaining / funds remaining
    # Guard the denominator against NON-POSITIVE remaining budget, not just exact zero:
    # when AC >= BAC (the over-budget distress case this tool forecasts) the funds are
    # exhausted and TCPI-to-BAC is undefined/unachievable, so route it into the inf
    # branch instead of printing a meaningless negative "efficiency needed" (2026-07-13
    # review).
    tcpi = (args.bac - args.ev) / (args.bac - args.ac) if (args.bac - args.ac) > 0 else float("inf")

    print("Earned Value status + forecast")
    print(f"  BAC (budget at completion) : {args.bac:,.0f}")
    print(f"  PV  (planned value)        : {args.pv:,.0f}")
    print(f"  EV  (earned value)         : {args.ev:,.0f}")
    print(f"  AC  (actual cost)          : {args.ac:,.0f}")
    print("  ---- variances ----")
    print(f"  CV  = EV - AC              : {cv:,.0f}  ({'over' if cv < 0 else 'under'} budget)")
    print(
        f"  SV  = EV - PV              : {sv:,.0f}  ({'behind' if sv < 0 else 'ahead of'} schedule)"
    )
    print("  ---- indices ----")
    print(
        f"  CPI = EV / AC              : {cpi:.3f}  ({'<1 over budget' if cpi < 1 else '>=1 on/under'})"
    )
    if spi == float("inf"):
        print("  SPI = EV / PV              : n/a  (PV is 0 — no schedule baseline yet)")
    else:
        print(
            f"  SPI = EV / PV              : {spi:.3f}  ({'<1 behind' if spi < 1 else '>=1 on/ahead'})"
        )
    print("  ---- forecasts ----")
    print(f"  EAC1 = BAC / CPI           : {eac_trend:,.0f}  (cost trend continues — start here)")
    print(f"  EAC2 = AC + (BAC - EV)     : {eac_budget:,.0f}  (remainder at budgeted rate)")
    if eac_both == float("inf"):
        print("  EAC3 = AC + (BAC-EV)/(CPI*SPI): n/a")
    else:
        print(
            f"  EAC3 = AC + (BAC-EV)/(CPI*SPI): {eac_both:,.0f}  (cost AND schedule drag remainder)"
        )
    print("  EAC4 = AC + bottom-up ETC  : (re-estimate the remainder when the model breaks)")
    print(f"  ETC  = (BAC - EV) / CPI    : {etc_trend:,.0f}  (cost to finish at current CPI)")
    print(
        f"  VAC  = BAC - EAC1          : {vac:,.0f}  ({'overrun' if vac < 0 else 'underrun'} vs budget)"
    )
    if tcpi == float("inf"):
        print(
            "  TCPI = (BAC-EV)/(BAC-AC)   : n/a  (AC >= BAC: funds exhausted with work "
            "remaining — the original budget is unrecoverable; re-baseline to EAC)"
        )
    else:
        warn = ""
        if tcpi > 1.20:
            warn = "  >1.20: budget effectively unrecoverable"
        elif tcpi > 1.10:
            warn = "  >1.10: very challenging to recover"
        print(f"  TCPI = (BAC-EV)/(BAC-AC)   : {tcpi:.3f}  (efficiency needed to hit BAC){warn}")

    # RAG read keyed off the Status-RAG decision tree thresholds.
    worst = min(cpi, spi if spi != float("inf") else cpi)
    if worst < 0.80:
        rag = "RED — distress; an EAC/escalation decision is required, not a green report"
    elif worst < 0.95:
        rag = "AMBER — under pressure; the status narrative must name the cause + a recovery plan"
    else:
        rag = "GREEN — on track; confirm in the narrative and note any watches"
    print("  ---- RAG (from CPI/SPI; the RAG never contradicts the numbers) ----")
    print(f"  → {rag}")
    print("  note: CPI tends to stabilize after ~20-25% complete — EAC1 is the honest")
    print("        default once past that point. Route the recovery call through the")
    print("        recover-vs-escalate tree; do not absorb the variance silently.")
    return 0


def cmd_pert(args: argparse.Namespace) -> int:
    o, m, p = args.optimistic, args.most_likely, args.pessimistic
    if not (o <= m <= p):
        print("error: require optimistic <= most-likely <= pessimistic", file=sys.stderr)
        return 2

    mean = (o + 4 * m + p) / 6.0
    sd = (p - o) / 6.0

    print("Three-point (PERT / beta) estimate")
    print(f"  optimistic (O)   : {o:,.2f}")
    print(f"  most likely (M)  : {m:,.2f}")
    print(f"  pessimistic (P)  : {p:,.2f}")
    print(f"  → PERT mean = (O + 4M + P) / 6 : {mean:,.2f}")
    print(f"  → std dev   = (P - O) / 6      : {sd:,.2f}")
    print("  ---- confidence bands (assuming roughly normal about the mean) ----")
    print(f"  ~68% (+/-1 sigma): {mean - sd:,.2f}  to  {mean + sd:,.2f}")
    print(f"  ~95% (+/-2 sigma): {mean - 2 * sd:,.2f}  to  {mean + 2 * sd:,.2f}")
    if mean:
        print(
            f"  spread ratio (2 sigma / mean): {(2 * sd / mean):.0%}  "
            "(wider => more uncertainty => more contingency)"
        )
    print("  note: size the contingency reserve off the spread, not off the single")
    print("        most-likely figure. A wide band is a signal to decompose further")
    print("        or commit a range, not a false-precision point date.")
    return 0


def cmd_forecast(args: argparse.Namespace) -> int:
    if args.remaining <= 0:
        print("error: --remaining must be > 0", file=sys.stderr)
        return 2
    sample = args.throughput
    if len(sample) < 2:
        print("error: need at least 2 throughput samples for a spread", file=sys.stderr)
        return 2
    if any(x < 0 for x in sample):
        print("error: throughput samples must be >= 0", file=sys.stderr)
        return 2

    mean = statistics.mean(sample)
    sd = statistics.pstdev(sample)
    if mean <= 0:
        print("error: mean throughput is 0 — cannot forecast completion", file=sys.stderr)
        return 2

    conservative = max(mean - sd, 0.1)  # mean - 1 sigma, floored so we don't divide by ~0
    optimistic = mean + sd

    def sprints(rate: float) -> float:
        return args.remaining / rate

    print("Agile completion forecast (throughput range)")
    print(f"  remaining items     : {args.remaining:g}")
    print(f"  throughput samples  : {', '.join(f'{x:g}' for x in sample)}  (n={len(sample)})")
    print(f"  mean / sprint       : {mean:.2f}")
    print(f"  std dev / sprint    : {sd:.2f}")
    print("  ---- sprints to finish the remaining backlog ----")
    print(f"  optimistic (mean+1 sigma = {optimistic:.2f}/spr): {sprints(optimistic):.1f} sprints")
    print(f"  expected   (mean      = {mean:.2f}/spr): {sprints(mean):.1f} sprints")
    print(
        f"  conservative (mean-1 sigma = {conservative:.2f}/spr): {sprints(conservative):.1f} sprints"
    )
    print("  note: commit the conservative end externally; velocity is DESCRIPTIVE of")
    print("        past sprints, not a target to load the next one to. Use >=8-15 stable")
    print("        sprints; for a real probability distribution run a Monte Carlo, not")
    print("        this +/-1 sigma approximation.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="evm_calc.py",
        description="Project-delivery decision calculator (stdlib only). "
        "Decision-support, not a governance decision — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    evm = sub.add_parser("evm", help="Earned value status + EAC/ETC/VAC/TCPI forecast")
    evm.add_argument("--bac", type=float, required=True, help="budget at completion")
    evm.add_argument("--pv", type=float, required=True, help="planned value to date")
    evm.add_argument(
        "--ev", type=float, required=True, help="earned value to date (BAC * %% complete)"
    )
    evm.add_argument("--ac", type=float, required=True, help="actual cost to date")
    evm.set_defaults(func=cmd_evm)

    pert = sub.add_parser("pert", help="Three-point (PERT) estimate + confidence bands")
    pert.add_argument(
        "--optimistic", "-o", type=float, required=True, help="optimistic estimate (O)"
    )
    pert.add_argument(
        "--most-likely", "-m", type=float, required=True, help="most-likely estimate (M)"
    )
    pert.add_argument(
        "--pessimistic", "-p", type=float, required=True, help="pessimistic estimate (P)"
    )
    pert.set_defaults(func=cmd_pert)

    fc = sub.add_parser("forecast", help="Agile completion forecast from throughput range")
    fc.add_argument(
        "--remaining", type=float, required=True, help="remaining backlog size (items or points)"
    )
    fc.add_argument(
        "--throughput",
        type=float,
        nargs="+",
        required=True,
        help="recent per-sprint throughput (or velocity) sample, space-separated",
    )
    fc.set_defaults(func=cmd_forecast)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
