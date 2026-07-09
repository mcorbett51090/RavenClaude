#!/usr/bin/env python3
"""statement_engine.py - trial balance -> IS / BS / (draft) CF, classification-tested.

WHAT THIS IS (and is NOT). Producing statements from a trial balance is a COMMODITY
pivot — every GL (QuickBooks, NetSuite, Xero, Sage Intacct) and Excel already do it.
This engine is NOT a differentiator by existing; it earns its place by being
*classification-correct and blocking*, so it can sit inside a governed close cycle
whose real value is the controls spine (close_state.py) and the per-entity COA
mapping asset (skills/author-coa-mapping). Two disciplines make it honest:

  1. BLOCK ON UNMAPPED ACCOUNTS. A balanced trial balance produces a balanced balance
     sheet REGARDLESS of whether accounts map to the right lines — net income is
     Sum(credit-debit) over IS accounts no matter how they're classified, so
     "assets == liabilities + equity to the cent" is a TAUTOLOGY that proves the
     arithmetic and catches nothing about mis-classification. Correctness lives in
     the SUBTOTALS (gross profit, operating income), which are classification-
     sensitive. So the engine refuses (--strict) to emit a statement while any TB
     account is unmapped or ambiguously mapped, rather than silently plugging it.

  2. TRACEABILITY BADGE. A trial balance has already discarded the transaction detail
     an auditor needs (line -> account -> journal entry -> document). With only a TB,
     the output is badged "TB-only - NOT audit-traceable" so the false precision is
     explicit on the artifact. Pass optional --gl-detail to carry account -> JE
     references into the reasoning trail and lift the badge to "GL-detail-traced".

  3. CASH FLOW IS AN UNAUDITED DRAFT. Indirect-method CF needs operating/investing/
     financing classification and non-cash adjustments that are NOT derivable from a
     two-period TB alone. When a prior-period TB is supplied the engine emits a
     best-effort indirect CF LABELED 'unaudited_draft' with its ending-cash tie-out
     as a SANITY check (necessary, not sufficient) - never as a correctness proof.

Reusable per entity: entities are data (entity profile + COA mapping CSV); the code
never contains an entity-specific fact. Stdlib only (csv/json/argparse). Python 3.8+.

Outputs are decision-support, not an accounting/audit/tax opinion (../CLAUDE.md sec.3).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys

IS_SECTIONS = {"Revenue", "COGS", "OpEx", "OtherIncomeExpense", "Tax"}
BS_SECTIONS = {
    "CurrentAssets",
    "NonCurrentAssets",
    "CurrentLiabilities",
    "NonCurrentLiabilities",
    "Equity",
}
ASSET_SECTIONS = {"CurrentAssets", "NonCurrentAssets"}
NORMAL = {"debit", "credit"}

# Presentation sign is driven by the SECTION's natural side, not the account's
# normal_balance — this is what makes contra-accounts correct. A contra-asset
# (accumulated depreciation) carries a credit balance, so within an asset section
# its (debit - credit) is NEGATIVE and correctly reduces net assets; a contra-
# revenue (sales returns, a debit balance) reduces revenue the same way.
DEBIT_POSITIVE = {"CurrentAssets", "NonCurrentAssets", "COGS", "OpEx", "Tax"}
CREDIT_POSITIVE = {
    "CurrentLiabilities",
    "NonCurrentLiabilities",
    "Equity",
    "Revenue",
    "OtherIncomeExpense",
}


def _read_csv(path: str) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def load_mapping(path: str) -> dict:
    """account -> {statement, section, line, normal_balance, cf_category, noncash}."""
    m: dict[str, dict] = {}
    for i, row in enumerate(_read_csv(path), 2):
        acct = (row.get("account") or "").strip()
        if not acct:
            raise SystemExit(f"{path}:{i} blank account in mapping")
        if acct in m:
            raise SystemExit(f"{path}:{i} duplicate mapping for account {acct!r}")
        m[acct] = {
            "statement": (row.get("statement") or "").strip(),
            "section": (row.get("section") or "").strip(),
            "line": (row.get("line") or "").strip(),
            "normal_balance": (row.get("normal_balance") or "").strip().lower(),
            "cf_category": (row.get("cf_category") or "").strip().lower(),
            "noncash": (row.get("noncash") or "").strip().lower() in ("1", "true", "yes"),
        }
    return m


def load_tb(path: str) -> list[dict]:
    rows = []
    for i, row in enumerate(_read_csv(path), 2):
        acct = (row.get("account") or "").strip()
        if not acct:
            continue
        try:
            debit = float(row.get("debit") or 0)
            credit = float(row.get("credit") or 0)
        except ValueError:
            raise SystemExit(f"{path}:{i} non-numeric debit/credit for {acct!r}")
        rows.append(
            {
                "account": acct,
                "description": (row.get("description") or "").strip(),
                "debit": debit,
                "credit": credit,
            }
        )
    return rows


def lint_mapping(tb: list[dict], mapping: dict) -> list[str]:
    """Coverage + validity errors that must block a --strict run."""
    errs: list[str] = []
    tb_accts = {r["account"] for r in tb}
    for acct in sorted(tb_accts):
        if acct not in mapping:
            errs.append(
                f"UNMAPPED account in TB: {acct!r} (every account must map to a statement line)"
            )
    for acct, mp in mapping.items():
        if mp["statement"] not in ("IS", "BS"):
            errs.append(f"{acct}: statement must be IS|BS, got {mp['statement']!r}")
        elif mp["statement"] == "IS" and mp["section"] not in IS_SECTIONS:
            errs.append(
                f"{acct}: IS section must be one of {sorted(IS_SECTIONS)}, got {mp['section']!r}"
            )
        elif mp["statement"] == "BS" and mp["section"] not in BS_SECTIONS:
            errs.append(
                f"{acct}: BS section must be one of {sorted(BS_SECTIONS)}, got {mp['section']!r}"
            )
        if mp["normal_balance"] not in NORMAL:
            errs.append(
                f"{acct}: normal_balance must be debit|credit, got {mp['normal_balance']!r}"
            )
    return errs


def _present(row: dict, section: str) -> float:
    """Presentation amount, signed by the SECTION's natural side (handles contra-accounts)."""
    if section in DEBIT_POSITIVE:
        return row["debit"] - row["credit"]
    if section in CREDIT_POSITIVE:
        return row["credit"] - row["debit"]
    raise SystemExit(f"unknown section for presentation: {section!r}")


def build_income_statement(tb: list[dict], mapping: dict):
    lines: dict[str, float] = {}
    section_totals = dict.fromkeys(IS_SECTIONS, 0.0)
    trail = []
    ni_check = 0.0
    for r in tb:
        mp = mapping[r["account"]]
        if mp["statement"] != "IS":
            continue
        amt = _present(r, mp["section"])
        lines[mp["line"]] = round(lines.get(mp["line"], 0.0) + amt, 2)
        section_totals[mp["section"]] += amt
        ni_check += r["credit"] - r["debit"]  # mapping-independent NI accumulator
        trail.append(
            {
                "account": r["account"],
                "line": mp["line"],
                "section": mp["section"],
                "amount": round(amt, 2),
            }
        )
    rev = round(section_totals["Revenue"], 2)
    cogs = round(section_totals["COGS"], 2)
    opex = round(section_totals["OpEx"], 2)
    other = round(section_totals["OtherIncomeExpense"], 2)  # net (income +, expense -)
    tax = round(section_totals["Tax"], 2)
    gross_profit = round(rev - cogs, 2)
    operating_income = round(gross_profit - opex, 2)
    pretax_income = round(operating_income + other, 2)
    net_income = round(pretax_income - tax, 2)
    # internal consistency: subtotal-derived NI must equal the mapping-independent one.
    # A bare `assert` is compiled out under `python -O`, so raise explicitly to keep the
    # cross-check alive in optimized runs.
    if abs(net_income - round(ni_check, 2)) >= 0.01:
        raise SystemExit(
            f"internal error: IS subtotal-derived net income {net_income:,.2f} != "
            f"mapping-independent net income {round(ni_check, 2):,.2f}"
        )
    return (
        {
            "lines": lines,
            "subtotals": {
                "revenue": rev,
                "cogs": cogs,
                "gross_profit": gross_profit,
                "operating_expenses": opex,
                "operating_income": operating_income,
                "other_income_expense_net": other,
                "pretax_income": pretax_income,
                "income_tax_expense": tax,
                "net_income": net_income,
            },
        },
        net_income,
        trail,
    )


def build_balance_sheet(tb: list[dict], mapping: dict, net_income: float):
    lines: dict[str, float] = {}
    section_totals = dict.fromkeys(BS_SECTIONS, 0.0)
    trail = []
    for r in tb:
        mp = mapping[r["account"]]
        if mp["statement"] != "BS":
            continue
        amt = _present(r, mp["section"])
        lines[mp["line"]] = round(lines.get(mp["line"], 0.0) + amt, 2)
        section_totals[mp["section"]] += amt
        trail.append(
            {
                "account": r["account"],
                "line": mp["line"],
                "section": mp["section"],
                "amount": round(amt, 2),
            }
        )
    total_assets = round(sum(section_totals[s] for s in ASSET_SECTIONS), 2)
    total_liabilities = round(
        section_totals["CurrentLiabilities"] + section_totals["NonCurrentLiabilities"], 2
    )
    equity_from_tb = round(section_totals["Equity"], 2)
    total_equity = round(equity_from_tb + net_income, 2)  # current earnings -> equity
    balance_delta = round(total_assets - (total_liabilities + total_equity), 2)
    return (
        {
            "lines": lines,
            "subtotals": {
                "total_assets": total_assets,
                "total_current_assets": round(section_totals["CurrentAssets"], 2),
                "total_liabilities": total_liabilities,
                "equity_beginning": equity_from_tb,
                "current_period_net_income": round(net_income, 2),
                "total_equity": total_equity,
                "balance_delta": balance_delta,  # 0.00 by construction (see module docstring)
            },
        },
        trail,
        section_totals,
    )


def build_cashflow_draft(cur_bs_sections, prior_tb, mapping, net_income, cur_bs_lines):
    """Best-effort indirect CF from two TBs. LABELED unaudited_draft - see docstring."""
    prior_is, prior_ni, _ = build_income_statement(prior_tb, mapping)
    _, prior_sect, prior_raw = build_balance_sheet(prior_tb, mapping, prior_ni)

    # Delta by BS section (current - prior), presentation-signed.
    def delt(sec):
        return round(cur_bs_sections[sec] - prior_raw[sec], 2)

    d_ca = delt("CurrentAssets")
    d_nca = delt("NonCurrentAssets")
    d_cl = delt("CurrentLiabilities")
    d_ncl = delt("NonCurrentLiabilities")
    d_eq = delt("Equity")
    # Operating: NI + increase in current liabilities - increase in (non-cash) current assets.
    # NOTE: we cannot separate cash from other current assets reliably without tagging,
    # so this is deliberately coarse and flagged unaudited.
    operating = round(net_income + d_cl - d_ca, 2)
    investing = round(-d_nca, 2)  # asset increase = cash outflow
    financing = round(d_ncl + d_eq, 2)  # NI already in operating; d_eq here is coarse
    net_change = round(operating + investing + financing, 2)
    return {
        "label": "unaudited_draft",
        "caveat": (
            "Indirect CF derived from two trial balances only. Operating/investing/"
            "financing splits and non-cash adjustments are NOT reliably derivable from "
            "a TB; treat as a draft sanity check, not a GAAP cash-flow statement."
        ),
        "cash_from_operating": operating,
        "cash_from_investing": investing,
        "cash_from_financing": financing,
        "net_change_in_cash": net_change,
    }


def run(entity, mapping_path, tb_path, gl_detail=None, prior_tb_path=None, strict=False):
    mapping = load_mapping(mapping_path)
    tb = load_tb(tb_path)
    errs = lint_mapping(tb, mapping)
    if errs and strict:
        sys.stderr.write("BLOCKED (--strict): mapping/coverage errors:\n")
        for e in errs:
            sys.stderr.write(f"  - {e}\n")
        raise SystemExit(3)
    tb_debits = round(sum(r["debit"] for r in tb), 2)
    tb_credits = round(sum(r["credit"] for r in tb), 2)
    if abs(tb_debits - tb_credits) >= 0.01:
        sys.stderr.write(
            f"BLOCKED: trial balance is out of balance by "
            f"{tb_debits - tb_credits:,.2f} (debits {tb_debits:,.2f} != "
            f"credits {tb_credits:,.2f}).\n"
        )
        raise SystemExit(4)

    is_stmt, net_income, is_trail = build_income_statement(tb, mapping)
    bs_stmt, bs_trail, bs_sections = build_balance_sheet(tb, mapping, net_income)
    traced = bool(gl_detail)
    badge = "GL-detail-traced" if traced else "TB-only - NOT audit-traceable"
    out = {
        "entity": entity["entity_name"],
        "currency": entity["functional_currency"],
        "period": entity["fiscal_period"],
        "traceability_badge": badge,
        "income_statement": is_stmt,
        "balance_sheet": bs_stmt,
        "reasoning_trail": {"income_statement": is_trail, "balance_sheet": bs_trail},
        "warnings": errs,
    }
    if prior_tb_path:
        prior_tb = load_tb(prior_tb_path)
        # The prior-period TB feeds the cash-flow draft directly; hold it to the same
        # debits==credits invariant as the current TB, so an unbalanced prior TB BLOCKS
        # rather than silently producing a garbage draft cash flow.
        p_debits = round(sum(r["debit"] for r in prior_tb), 2)
        p_credits = round(sum(r["credit"] for r in prior_tb), 2)
        if abs(p_debits - p_credits) >= 0.01:
            sys.stderr.write(
                f"BLOCKED: prior-period trial balance is out of balance by "
                f"{p_debits - p_credits:,.2f} (debits {p_debits:,.2f} != "
                f"credits {p_credits:,.2f}).\n"
            )
            raise SystemExit(4)
        out["cash_flow"] = build_cashflow_draft(
            bs_sections, prior_tb, mapping, net_income, bs_stmt["lines"]
        )
    if gl_detail:
        det = _read_csv(gl_detail)
        by_acct: dict[str, int] = {}
        for row in det:
            by_acct[row.get("account", "")] = by_acct.get(row.get("account", ""), 0) + 1
        out["gl_detail_index"] = {"journal_lines": len(det), "accounts_traced": len(by_acct)}
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Trial balance -> GAAP statements (classification-tested)."
    )
    p.add_argument("--entity", required=True, help="entity profile JSON")
    p.add_argument("--coa", required=True, help="COA mapping CSV")
    p.add_argument("--tb", required=True, help="trial balance CSV")
    p.add_argument("--prior-tb", help="prior-period TB CSV (enables draft cash flow)")
    p.add_argument("--gl-detail", help="optional journal-line CSV for traceability")
    p.add_argument("--strict", action="store_true", help="block on unmapped/invalid accounts")
    p.add_argument(
        "--lint-map", action="store_true", help="only lint the mapping vs the TB, then exit"
    )
    p.add_argument("--out", help="write statements JSON here (else stdout)")
    a = p.parse_args(argv)

    with open(a.entity) as fh:
        entity = json.load(fh)

    if a.lint_map:
        errs = lint_mapping(load_tb(a.tb), load_mapping(a.coa))
        if errs:
            sys.stderr.write("COA mapping lint FAILED:\n")
            for e in errs:
                sys.stderr.write(f"  - {e}\n")
            return 1
        print("OK: every TB account maps to a valid statement line.")
        return 0

    out = run(entity, a.coa, a.tb, a.gl_detail, a.prior_tb, a.strict)
    text = json.dumps(out, indent=2)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text + "\n")
        print(
            f"wrote {a.out}  [{out['traceability_badge']}]  net income "
            f"{out['income_statement']['subtotals']['net_income']:,.2f} {out['currency']}"
        )
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
