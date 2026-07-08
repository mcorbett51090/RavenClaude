#!/usr/bin/env python3
"""netsuite_coa_draft.py - draft a per-entity COA-mapping CSV from NetSuite's chart of
accounts, so onboarding a new entity starts from a reviewable draft instead of a blank CSV.

WHAT THIS IS (and is NOT). `skills/author-coa-mapping` is explicit that the COA->statement-
line mapping is the genuinely bespoke, judgment-laden asset — authoring 100-200 accounts by
hand from a blank CSV is the day-one killer for onboarding a new NetSuite entity. This module
pulls NetSuite's chart of accounts (via SuiteQL, replayed offline — see suiteql.py) and RULES-
CLASSIFIES each account's `accttype` to the SAME mapping contract
`skills/author-coa-mapping/SKILL.md` documents and `statement_engine.py --lint-map` validates:

    account,description,statement,section,line,normal_balance,cf_category,noncash

It reuses suiteql.py's BALANCE_SHEET_TYPES / INCOME_STATEMENT_TYPES sets (NetSuite's
documented `accttype` enum) as the single source of truth for the statement split, so this
module can never drift from the SuiteQL TB query's own classification.

THE HONEST BOUNDARY. This is DECISION SUPPORT, not a certified mapping. An `accttype` this
module doesn't recognize is NEVER silently guessed — the row is written with
`line = "REVIEW REQUIRED — unknown accttype '<type>'"` and blank statement/section, which
means `--lint-map` will (correctly) refuse to build statements until a human classifies it.
Every classification of a KNOWN accttype is still a rule, not a judgment call about THIS
entity's specific chart — a controller must review the draft before it feeds a close
(../../CLAUDE.md sec.3).

Coverage is reported dollar-weighted by an optional staged trial balance (canonical columns
from tb_stage.py), so review time goes to the accounts that actually move the statements
first; absent a TB, the review queue falls back to account-number order.

Stdlib only (csv/json/argparse/os/sys). Python 3.8+.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from replay_transport import ReplayTransport  # noqa: E402
from suiteql import BALANCE_SHEET_TYPES, INCOME_STATEMENT_TYPES  # noqa: E402

# The SuiteQL text used to pull the chart of accounts. `query` is recorded for the audit
# trail; ReplayTransport.suiteql() selects the fixture by NAME (offline replay can't execute
# SQL), so the fixture IS the recorded result. [Query SHAPE is settling-gated — verify
# column names against a sandbox before go-live, same discipline as suiteql.py.]
COA_QUERY = "SELECT acctnumber, fullname, accttype, subsidiary FROM account"
COA_FIXTURE = "netsuite_m2m/coa"

MAPPING_HEADER = [
    "account", "description", "statement", "section", "line",
    "normal_balance", "cf_category", "noncash",
]

# NetSuite documented accttype -> (section, line, normal_balance, cf_category). Kept in the
# SAME statement/section vocabulary statement_engine.py --lint-map validates
# (IS_SECTIONS/BS_SECTIONS). `cf_category` is left "" for IS types the same way the worked
# example (skills/produce-gaap-statements/examples/coa-mapping.csv) leaves revenue/COGS/opex
# blank — cf classification of an IS account is a judgment call this rules pass does not make.
ACCTTYPE_CLASSIFICATION = {
    # -- balance-sheet types --------------------------------------------------------------
    "Bank":         ("CurrentAssets", "Cash and cash equivalents", "debit", "operating"),
    "AcctRec":      ("CurrentAssets", "Accounts receivable, net", "debit", "operating"),
    "OthCurrAsset": ("CurrentAssets", "Other current assets", "debit", "operating"),
    "DeferExpense": ("CurrentAssets", "Prepaid & deferred expenses", "debit", "operating"),
    "FixedAsset":   ("NonCurrentAssets", "Property, plant & equipment, net", "debit", "investing"),
    "OthAsset":     ("NonCurrentAssets", "Other non-current assets", "debit", "investing"),
    "AcctPay":      ("CurrentLiabilities", "Accounts payable", "credit", "operating"),
    "CredCard":     ("CurrentLiabilities", "Credit card payable", "credit", "operating"),
    "OthCurrLiab":  ("CurrentLiabilities", "Other current liabilities", "credit", "operating"),
    "DeferRevenue": ("CurrentLiabilities", "Deferred revenue", "credit", "operating"),
    "LongTermLiab": ("NonCurrentLiabilities", "Long-term liabilities", "credit", "financing"),
    "Equity":       ("Equity", "Equity", "credit", "financing"),
    # -- income-statement types ------------------------------------------------------------
    "Income":       ("Revenue", "Revenue", "credit", ""),
    "COGS":         ("COGS", "Cost of goods sold", "debit", ""),
    "Expense":      ("OpEx", "Operating expenses", "debit", ""),
    "OthIncome":    ("OtherIncomeExpense", "Other income", "credit", ""),
    "OthExpense":   ("OtherIncomeExpense", "Other expense", "debit", ""),
}
assert set(ACCTTYPE_CLASSIFICATION) == (BALANCE_SHEET_TYPES | INCOME_STATEMENT_TYPES)


def pull_coa(transport, *, fixture_name: str = COA_FIXTURE, limit: int = 1000) -> list:
    """Page the chart-of-accounts SuiteQL result via transport.suiteql(). Simple serial
    paging (no retry/backoff) — this is a draft-support pull, not the governed, retried
    trial-balance pager in suiteql.pull(); a controller re-runs this on demand, it does not
    gate a close."""
    rows: list = []
    offset = 0
    while True:
        page = transport.suiteql(COA_QUERY, limit=limit, offset=offset, name=fixture_name)
        items = page.get("items", []) if isinstance(page, dict) else getattr(page, "items", [])
        rows.extend(items or [])
        has_more = page.get("hasMore", False) if isinstance(page, dict) else getattr(page, "hasMore", False)
        if not has_more:
            break
        offset += limit
    return rows


def classify_account(row: dict) -> dict:
    """One NetSuite account row -> one mapping-contract row + a `flagged` bookkeeping field
    (stripped before the CSV is written; used only for the coverage report)."""
    acct = str(row.get("acctnumber", "")).strip()
    name = str(row.get("fullname", "")).strip()
    accttype = str(row.get("accttype", "")).strip()
    spec = ACCTTYPE_CLASSIFICATION.get(accttype)
    if spec is None:
        return {
            "account": acct, "description": name, "statement": "", "section": "",
            "line": f"REVIEW REQUIRED — unknown accttype {accttype!r}",
            "normal_balance": "", "cf_category": "", "noncash": "",
            "flagged": True, "accttype": accttype,
        }
    section, line, normal_balance, cf_category = spec
    statement = "BS" if accttype in BALANCE_SHEET_TYPES else "IS"
    return {
        "account": acct, "description": name, "statement": statement, "section": section,
        "line": line, "normal_balance": normal_balance, "cf_category": cf_category,
        "noncash": "", "flagged": False, "accttype": accttype,
    }


def classify_rows(rows: list) -> list:
    return [classify_account(r) for r in rows]


def write_mapping_csv(path: str, mapping_rows: list) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(MAPPING_HEADER)
        for r in mapping_rows:
            w.writerow([r[c] for c in MAPPING_HEADER])
    return path


def load_tb_weights(tb_path: str) -> dict:
    """account -> abs(debit - credit) from a canonical staged TB (tb_stage.py's columns:
    account,description,debit,credit,entity,period,currency). Tolerant of a missing
    debit/credit cell (treated as 0); a non-numeric cell is a hard error (a weighting input
    must be trustworthy, not silently zeroed)."""
    weights: dict = {}
    with open(tb_path, newline="") as fh:
        for i, row in enumerate(csv.DictReader(fh), 2):
            acct = (row.get("account") or "").strip()
            if not acct:
                continue
            try:
                debit = float(row.get("debit") or 0)
                credit = float(row.get("credit") or 0)
            except ValueError:
                raise SystemExit(f"{tb_path}:{i}: non-numeric debit/credit for account {acct!r}")
            weights[acct] = weights.get(acct, 0.0) + abs(debit - credit)
    return weights


def _sort_key(row: dict, weights: dict) -> tuple:
    if weights is not None:
        # Largest dollar-weighted balance first; unweighted accounts (not in the TB) sink
        # to the bottom of their tier instead of being silently interleaved.
        w = weights.get(row["account"], 0.0)
        return (0, -w, row["account"])
    # No TB supplied: fall back to account-number order (numeric where possible).
    acct = row["account"]
    try:
        return (0, float(acct), acct)
    except ValueError:
        return (1, 0.0, acct)


def sort_rows_for_review(mapping_rows: list, weights: dict | None = None) -> list:
    return sorted(mapping_rows, key=lambda r: _sort_key(r, weights))


def write_coverage_md(path: str, mapping_rows: list, weights: dict | None = None) -> str:
    ordered = sort_rows_for_review(mapping_rows, weights)
    flagged = [r for r in ordered if r["flagged"]]
    auto = [r for r in ordered if not r["flagged"]]
    sort_note = (
        "dollar-weighted by the supplied staged trial balance (largest balance first)"
        if weights is not None else
        "account-number order (no trial balance supplied to weight by dollar impact)"
    )
    lines = [
        "# NetSuite Chart-of-Accounts Draft — Coverage Report",
        "",
        "**This is decision-support, not a certified mapping.** Every row below was "
        "RULES-classified from NetSuite's `accttype` field; a controller must review every "
        "`REVIEW REQUIRED` row (and spot-check the auto-classified ones) before this mapping "
        "feeds a close cycle.",
        "",
        f"- Accounts pulled: **{len(ordered)}**",
        f"- Auto-classified: **{len(auto)}**",
        f"- Flagged REVIEW REQUIRED: **{len(flagged)}**",
        f"- Review order: {sort_note}",
        "",
    ]
    lines.append("## Review queue (flagged — classify these first)")
    lines.append("")
    if flagged:
        lines.append("| account | description | accttype | issue |")
        lines.append("|---|---|---|---|")
        for r in flagged:
            w = f" (${weights.get(r['account'], 0.0):,.2f})" if weights is not None else ""
            lines.append(f"| {r['account']}{w} | {r['description']} | {r['accttype']} | {r['line']} |")
    else:
        lines.append("_None — every pulled account matched a known accttype._")
    lines.append("")
    lines.append("## Auto-classified accounts (spot-check before relying on these)")
    lines.append("")
    lines.append("| account | description | accttype | statement | section | line |")
    lines.append("|---|---|---|---|---|---|")
    for r in auto:
        lines.append(
            f"| {r['account']} | {r['description']} | {r['accttype']} | {r['statement']} | "
            f"{r['section']} | {r['line']} |"
        )
    lines.append("")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Draft a NetSuite COA-mapping CSV (skills/author-coa-mapping contract) "
                    "from a SuiteQL chart-of-accounts pull, plain-English coverage report."
    )
    ap.add_argument("--fixture-dir", default=os.path.join(HERE, "fixtures"),
                    help="ReplayTransport fixture directory (offline, zero-cred)")
    ap.add_argument("--out-map", required=True, help="draft coa-mapping.csv to write")
    ap.add_argument("--out-coverage", required=True, help="coverage.md to write")
    ap.add_argument("--tb", help="optional staged TB CSV (tb_stage.py canonical columns) "
                                 "to dollar-weight the review queue")
    a = ap.parse_args(argv)

    transport = ReplayTransport(a.fixture_dir)
    rows = pull_coa(transport)
    mapping_rows = classify_rows(rows)
    weights = load_tb_weights(a.tb) if a.tb else None
    write_mapping_csv(a.out_map, mapping_rows)
    write_coverage_md(a.out_coverage, mapping_rows, weights)
    n_flag = sum(1 for r in mapping_rows if r["flagged"])
    print(
        f"wrote {a.out_map} ({len(mapping_rows)} accounts, {n_flag} flagged REVIEW REQUIRED) "
        f"and {a.out_coverage} — decision-support only, review before it feeds a close."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
