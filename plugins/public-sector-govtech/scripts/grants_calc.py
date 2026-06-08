#!/usr/bin/env python3
"""grants_calc.py — a zero-dependency public-grants arithmetic calculator.

Removes guesswork from three recurring quantitative calls a grants budget runs
constantly. It implements the team's house doctrine — see ../CLAUDE.md §4 and
../knowledge/public-sector-grants-decision-trees.md:

  indirect  Apply a negotiated (or de-minimis) indirect-cost rate to a Modified
            Total Direct Cost (MTDC) base. Excludes the items 2 CFR 200 carves
            out of MTDC (equipment, capital expenditures, the portion of each
            sub-award over the threshold, participant support, etc.) BEFORE
            applying the rate, so the recovery traces to a defensible base — not
            a rate slapped on the whole budget (budget-is-a-narrative-in-numbers,
            cite-the-authority-not-a-memory).

  match     Given a total project cost (or a federal share) and a required
            cost-share %, compute the match obligation and the shortfall against
            what's been sourced. Surfaces a match gap as a go/no-go input, not a
            quarter-end scramble (compliance-starts-at-the-proposal). Federal
            funds cannot match federal funds — the tool computes, it does not
            vouch for the source.

  budget    Roll a list of category line items (category=amount) into a total,
            each line's % of total, and (optionally) a personnel line built from
            FTE x salary x effort%. Makes every line's share explicit so the
            budget narrative can justify it line by line.

This is a CALCULATOR, not a data source — it does not read a grants system, an
award document, or a negotiated indirect-cost-rate agreement (NICRA). The user
supplies every input; the tool does the arithmetic and shows the rule it applied.
Stdlib only (argparse); runs anywhere Python 3.9+ is present.

IMPORTANT: outputs are decision-support, not an allowability determination. The
rate, the MTDC exclusions, the match-source eligibility, and the final budget
sign-off route to grants-compliance-analyst + the org's authorized official (see
../CLAUDE.md §3, §4 #12). Re-verify every rate/threshold against the CURRENT
2 CFR 200 and the specific award terms — the de-minimis rate and the sub-award
MTDC threshold change [verify-at-build]. A number is only as honest as its base.

Examples
--------
  # 10% de-minimis indirect on a $200,000 base, excluding $25,000 equipment
  python3 grants_calc.py indirect --base 200000 --rate 10 --exclude 25000

  # A program needs a 25% non-federal match on a $400,000 total; $60k sourced
  python3 grants_calc.py match --total 400000 --rate 25 --sourced 60000

  # Roll up a budget; one line is personnel built from FTE x salary x effort
  python3 grants_calc.py budget --line travel=12000 --line supplies=8000 \
      --personnel "PM:1x95000x50" --personnel "Analyst:1x70000x25"
"""

from __future__ import annotations

import argparse
import sys

_RULE = "-" * 60


def _money(x: float) -> str:
    """Format a number as a dollar amount with thousands separators."""
    return f"${x:,.2f}"


# --- indirect: indirect-cost recovery on an MTDC base -----------------------
def cmd_indirect(a: argparse.Namespace) -> int:
    if a.base < 0:
        print("error: --base must be >= 0", file=sys.stderr)
        return 2
    if not 0.0 <= a.rate <= 100.0:
        print("error: --rate must be 0..100", file=sys.stderr)
        return 2
    excluded = sum(a.exclude) if a.exclude else 0.0
    if excluded < 0:
        print("error: --exclude amounts must be >= 0", file=sys.stderr)
        return 2
    if excluded > a.base:
        print("error: total --exclude exceeds --base", file=sys.stderr)
        return 2

    mtdc = a.base - excluded
    indirect = round(mtdc * a.rate / 100.0, 2)
    total = round(mtdc + excluded + indirect, 2)

    print("Indirect-cost recovery on an MTDC base")
    print(_RULE)
    print(f"  Direct-cost base       : {_money(a.base)}")
    print(f"  Excluded from MTDC      : {_money(excluded)}  ({len(a.exclude or [])} item(s))")
    print(f"  MTDC base (rate applies): {_money(mtdc)}")
    print(f"  Indirect rate           : {a.rate:g}%")
    print(_RULE)
    print(f"  INDIRECT recovered      : {_money(indirect)}")
    print(f"  Total (direct + indirect): {_money(total)}")
    print(_RULE)
    print("  Note: MTDC excludes equipment, capital expenditures, the portion of")
    print("  each sub-award over the 2 CFR threshold, participant support, and")
    print("  pass-through items — exclude them BEFORE applying the rate. The rate")
    print("  must be a negotiated (NICRA) or de-minimis rate, cited — not a norm.")
    print("  The rate/threshold change [verify-at-build]; sign-off is the analyst's.")
    return 0


# --- match: required cost-share and the shortfall ---------------------------
def cmd_match(a: argparse.Namespace) -> int:
    if a.total <= 0:
        print("error: --total must be > 0", file=sys.stderr)
        return 2
    if not 0.0 <= a.rate <= 100.0:
        print("error: --rate must be 0..100", file=sys.stderr)
        return 2
    if a.sourced < 0:
        print("error: --sourced must be >= 0", file=sys.stderr)
        return 2

    if a.of_federal:
        # --total is the federal share; gross up to the project total first.
        if a.rate >= 100.0:
            print("error: --rate must be < 100 when --of-federal is set", file=sys.stderr)
            return 2
        project_total = round(a.total / (1.0 - a.rate / 100.0), 2)
        basis = "federal share"
    else:
        project_total = float(a.total)
        basis = "total project cost"

    required = round(project_total * a.rate / 100.0, 2)
    shortfall = round(required - a.sourced, 2)
    federal_share = round(project_total - required, 2)

    if shortfall > 0:
        verdict = "SHORTFALL — a match gap is a go/no-go input, not a writing problem"
    elif shortfall == 0:
        verdict = "MET — exactly sourced; document the source and valuation now"
    else:
        verdict = f"OVER — {_money(-shortfall)} above the requirement (sourced > required)"

    print("Required match / cost-share")
    print(_RULE)
    print(f"  Basis                  : {basis}")
    print(f"  Total project cost      : {_money(project_total)}")
    print(f"  Federal share           : {_money(federal_share)}")
    print(f"  Required match           : {_money(required)}  ({a.rate:g}% of total)")
    print(f"  Sourced so far           : {_money(a.sourced)}")
    print(_RULE)
    print(f"  SHORTFALL                : {_money(shortfall)}")
    print(f"  Verdict                  : {verdict}")
    print(_RULE)
    print("  Note: federal funds cannot match federal funds; value third-party")
    print("  in-kind with a documented method (hours x a defensible rate). Each")
    print("  match item must itself be allowable/allocable/reasonable and verifiable.")
    print("  Source the match BEFORE pledging it — the source eligibility is the")
    print("  analyst's call, not this tool's.")
    return 0


# --- budget: category roll-up + % of total + personnel build ----------------
def _parse_line(spec: str) -> tuple[str, float]:
    if "=" not in spec:
        raise ValueError(f"--line must be category=amount, got: {spec!r}")
    name, _, amount = spec.partition("=")
    name = name.strip()
    if not name:
        raise ValueError(f"--line needs a category name, got: {spec!r}")
    try:
        value = float(amount)
    except ValueError as exc:
        raise ValueError(f"--line amount must be a number, got: {amount!r}") from exc
    if value < 0:
        raise ValueError(f"--line amount must be >= 0, got: {value}")
    return name, round(value, 2)


def _parse_personnel(spec: str) -> tuple[str, float]:
    # Format: name:FTExSALARYxEFFORT  e.g. "PM:1x95000x50"
    if ":" not in spec:
        raise ValueError(f"--personnel must be name:FTExSALARYxEFFORT, got: {spec!r}")
    name, _, rest = spec.partition(":")
    name = name.strip()
    parts = rest.split("x")
    if not name or len(parts) != 3:
        raise ValueError(f"--personnel must be name:FTExSALARYxEFFORT, got: {spec!r}")
    try:
        fte, salary, effort = (float(p) for p in parts)
    except ValueError as exc:
        raise ValueError(f"--personnel FTE/SALARY/EFFORT must be numbers, got: {rest!r}") from exc
    if fte < 0 or salary < 0:
        raise ValueError("--personnel FTE and SALARY must be >= 0")
    if not 0.0 <= effort <= 100.0:
        raise ValueError("--personnel EFFORT must be 0..100 (percent)")
    return name, round(fte * salary * effort / 100.0, 2)


def cmd_budget(a: argparse.Namespace) -> int:
    items: list[tuple[str, float]] = []
    try:
        for spec in a.line or []:
            items.append(_parse_line(spec))
        for spec in a.personnel or []:
            items.append(_parse_personnel(spec))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not items:
        print("error: provide at least one --line or --personnel", file=sys.stderr)
        return 2

    total = round(sum(amount for _, amount in items), 2)
    name_width = max(len(name) for name, _ in items)

    print("Budget roll-up — category share of total")
    print(_RULE)
    for name, amount in items:
        pct = (100.0 * amount / total) if total else 0.0
        print(f"  {name.ljust(name_width)} : {_money(amount).rjust(15)}  {pct:5.1f}%")
    print(_RULE)
    print(f"  {'TOTAL'.ljust(name_width)} : {_money(total).rjust(15)}  100.0%")
    print(_RULE)
    print("  Note: a personnel line is FTE x salary x effort%; every line needs a")
    print("  budget narrative that shows its math and ties to a logic-model")
    print("  activity. A number with no narrative is a finding waiting to happen.")
    print("  Indirect is computed separately (see the `indirect` subcommand).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="grants_calc.py",
        description="Public-grants arithmetic calculator (decision-support, not an allowability determination).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="command", required=True)

    ind = sub.add_parser("indirect", help="indirect-cost recovery on an MTDC base")
    ind.add_argument("--base", type=float, required=True, help="total direct-cost base before MTDC exclusions")
    ind.add_argument("--rate", type=float, required=True, help="indirect rate 0..100 (negotiated or de-minimis)")
    ind.add_argument(
        "--exclude",
        type=float,
        action="append",
        metavar="AMOUNT",
        help="an item excluded from MTDC (equipment, sub-award over threshold, etc.); repeatable",
    )
    ind.set_defaults(func=cmd_indirect)

    mat = sub.add_parser("match", help="required cost-share and the shortfall")
    mat.add_argument("--total", type=float, required=True, help="total project cost (or federal share with --of-federal)")
    mat.add_argument("--rate", type=float, required=True, help="required match/cost-share rate 0..100 (% of total)")
    mat.add_argument("--sourced", type=float, default=0.0, help="non-federal match already sourced (default 0)")
    mat.add_argument(
        "--of-federal",
        action="store_true",
        help="treat --total as the federal share and gross up to the project total first",
    )
    mat.set_defaults(func=cmd_match)

    bud = sub.add_parser("budget", help="category roll-up + % of total + personnel build")
    bud.add_argument(
        "--line",
        action="append",
        metavar="CATEGORY=AMOUNT",
        help="a budget line, e.g. travel=12000; repeatable",
    )
    bud.add_argument(
        "--personnel",
        action="append",
        metavar="NAME:FTExSALARYxEFFORT",
        help="a personnel line built from FTE x salary x effort%%, e.g. PM:1x95000x50; repeatable",
    )
    bud.set_defaults(func=cmd_budget)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
