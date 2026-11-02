#!/usr/bin/env python3
"""test_entity_dashboard.py - acceptance suite for the per-entity dashboard (P10).

Stdlib-only, zero-dependency runner (no pytest). Run: python3 test_entity_dashboard.py
Exits 0 iff every check passes. Covers: KPI derivation correctness against a hand-
derived synthetic package, graceful 'n/a' when a KPI's inputs are absent (never a
plugged value), self-containment (no external http/https resource refs), and the
committed sample dashboard's content. The synthetic entity is obviously fake.
"""
from __future__ import annotations

import copy
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import controller_cycle as cc  # noqa: E402
import entity_dashboard as ed  # noqa: E402
import statement_engine as se  # noqa: E402

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(("  PASS " if cond else "  FAIL ") + name)


# A fully synthetic, obviously-fake close package matching controller_cycle --out-json.
# Numbers are hand-picked so every derived KPI has a clean golden.
SYNTH = {
    "entity": "Nimbus Widgets LLC (FICTITIOUS)",
    "period": "2026-06",  # 30 days
    "currency": "USD",
    "sod_threshold": 100000.0,
    "package_amount": 900000.0,
    "statements": {
        "traceability_badge": "TB-only - NOT audit-traceable",
        "income_statement": {
            "subtotals": {
                "revenue": 1000000.0, "cogs": 400000.0, "gross_profit": 600000.0,
                "operating_expenses": 380000.0, "operating_income": 220000.0,
                "other_income_expense_net": -20000.0, "pretax_income": 200000.0,
                "income_tax_expense": 50000.0, "net_income": 150000.0,
            },
        },
        "balance_sheet": {
            "lines": {
                "Cash and cash equivalents": 180000.0,
                "Accounts receivable, net": 120000.0,
                "Inventory": 200000.0,
            },
            "subtotals": {
                "total_assets": 900000.0, "total_current_assets": 500000.0,
                "total_liabilities": 400000.0, "equity_beginning": 350000.0,
                "current_period_net_income": 150000.0, "total_equity": 500000.0,
                "balance_delta": 0.0,
            },
        },
        "reasoning_trail": {
            "balance_sheet": [
                {"account": "2000", "line": "Accounts payable",
                 "section": "CurrentLiabilities", "amount": 200000.0},
                {"account": "2100", "line": "Accrued liabilities",
                 "section": "CurrentLiabilities", "amount": 50000.0},
                {"account": "2500", "line": "Long-term debt",
                 "section": "NonCurrentLiabilities", "amount": 150000.0},
            ],
        },
        "cash_flow": {
            "label": "unaudited_draft",
            "caveat": "Draft sanity check only.",
            "cash_from_operating": 40000.0, "cash_from_investing": -10000.0,
            "cash_from_financing": -5000.0, "net_change_in_cash": 25000.0,
        },
    },
    "reconciliation": {
        "materiality_threshold": 20000.0, "flagged_count": 1,
        "accounts": [
            {"account": "1000", "description": "Cash", "book_balance": 180000.0,
             "subledger_balance": 180000.0, "difference": 0.0, "status": "PASS"},
            {"account": "1200", "description": "Inventory", "book_balance": 200000.0,
             "subledger_balance": 165000.0, "difference": 35000.0, "status": "FLAG"},
            {"account": "1500", "description": "PP&E", "book_balance": 250000.0,
             "subledger_balance": None, "difference": None, "status": "self-supported"},
        ],
    },
    "flux": {
        "materiality_threshold": 20000.0, "suppressed_below": 20000.0,
        "material_movements": [
            {"account": "4000", "description": "Product Revenue", "current": -1000000.0,
             "prior": -800000.0, "movement": -200000.0, "pct_change": 25.0},
            {"account": "1000", "description": "Cash", "current": 180000.0,
             "prior": 155000.0, "movement": 25000.0, "pct_change": 16.1},
        ],
    },
    "workflow_state": {
        "schema_version": 1, "state": "submitted", "preparer": "autopilot",
        "package_amount": 900000.0, "self_certified": None,
    },
}


_CF_ENT = {"entity_name": "Cashflow Co (FICTITIOUS)", "functional_currency": "USD",
           "fiscal_period": "2026-06"}
_TB_HDR = "account,description,debit,credit,entity,period,currency\n"


def _cf_book(d, cash_line="Cash and cash equivalents", cash_col=None, cash_is_receivable=False):
    """A tiny hand-checked pair of TBs: cash 120 -> 180, prior NI 40, current NI 90, AP +10.

    cash_col  None -> the COA has no `cash` column; "true"/"" -> a `cash` column tagging 1000.
    cash_is_receivable  map 1000 to a non-cash line (so NO cash account is identifiable)."""
    line = "Accounts receivable" if cash_is_receivable else cash_line
    head = "account,description,statement,section,line,normal_balance"
    tag = "" if cash_col is None else ("," + cash_col)
    rows = [head + (",cash" if cash_col is not None else ""),
            f"1000,Bank,BS,CurrentAssets,{line},debit{tag}",
            "2000,AP,BS,CurrentLiabilities,Accounts payable,credit" + ("," if tag else ""),
            "3000,Equity,BS,Equity,Common stock,credit" + ("," if tag else ""),
            "4000,Revenue,IS,Revenue,Revenue,credit" + ("," if tag else "")]
    coa = os.path.join(d, "coa.csv")
    with open(coa, "w") as fh:
        fh.write("\n".join(rows) + "\n")
    prior = os.path.join(d, "prior.csv")
    with open(prior, "w") as fh:
        fh.write(_TB_HDR + "1000,Bank,120,0,X,2026-05,USD\n3000,Equity,0,80,X,2026-05,USD\n"
                 "4000,Revenue,0,40,X,2026-05,USD\n")
    cur = os.path.join(d, "cur.csv")
    with open(cur, "w") as fh:
        fh.write(_TB_HDR + "1000,Bank,180,0,X,2026-06,USD\n2000,AP,0,10,X,2026-06,USD\n"
                 "3000,Equity,0,80,X,2026-06,USD\n4000,Revenue,0,90,X,2026-06,USD\n")
    return coa, cur, prior


def main():
    print("A-9 — draft cash flow: net_change_in_cash is the cash MOVEMENT, not prior-period NI")
    with tempfile.TemporaryDirectory() as d:
        coa, cur, prior = _cf_book(d)
        cf = se.run(_CF_ENT, coa, cur, None, prior, strict=True)["cash_flow"]
        check("cash 120 -> 180 (prior NI 40, current NI 90): net_change_in_cash == 60.0, "
              "NOT the prior NI 40.0", cf["net_change_in_cash"] == 60.0)
        check("unreconciled_difference = cash movement - (operating+investing+financing) "
              "= 60 - 100 = -40.0 (shown, not plugged)",
              cf["cash_from_operating"] == 100.0 and cf["unreconciled_difference"] == -40.0)
        check("cash is excluded from the operating working-capital change (operating = 90 + 10)",
              cf["cash_from_operating"] == 100.0)
    with tempfile.TemporaryDirectory() as d:
        coa, cur, prior = _cf_book(d, cash_line="Operating account", cash_col="true")
        cf = se.run(_CF_ENT, coa, cur, None, prior, strict=True)["cash_flow"]
        check("a mapping entry tagged cash=true is identified as cash (any line name)",
              cf["net_change_in_cash"] == 60.0)
    with tempfile.TemporaryDirectory() as d:
        coa, cur, prior = _cf_book(d, cash_is_receivable=True)
        cf = se.run(_CF_ENT, coa, cur, None, prior, strict=True)["cash_flow"]
        check("no cash account identifiable -> net_change_in_cash is None (not prior NI)",
              cf["net_change_in_cash"] is None and cf["unreconciled_difference"] is None)
        check("...with a caveat telling the user to tag a cash account",
              "Tag a cash account" in cf["caveat"])
    pkg_none = copy.deepcopy(SYNTH)
    pkg_none["statements"]["cash_flow"]["net_change_in_cash"] = None
    row = r"Net change in cash</td><td class='num'>([^<]*)"
    got_ed = re.findall(row, ed.render_dashboard(pkg_none))
    got_cc = re.findall(row, cc.render_html(pkg_none))
    check("entity_dashboard renders a None net change as 'n/a'", got_ed == ["n/a"])
    check("controller_cycle renders a None net change as 'n/a'", got_cc == ["n/a"])
    check("a real net change still renders as a number (25,000.00) in both",
          re.findall(row, ed.render_dashboard(SYNTH)) == ["25,000.00"]
          and re.findall(row, cc.render_html(SYNTH)) == ["25,000.00"])
    pkg_unrec = copy.deepcopy(SYNTH)
    pkg_unrec["statements"]["cash_flow"]["unreconciled_difference"] = -40.0
    check("an unreconciled_difference, when present, is rendered by both",
          "Unreconciled difference" in ed.render_dashboard(pkg_unrec)
          and "Unreconciled difference" in cc.render_html(pkg_unrec))

    print("P10 — KPI derivation (hand-derived goldens)")
    kpi = ed.derive_kpis(SYNTH)
    check("revenue passes through from IS subtotals", kpi["revenue"] == 1000000.0)
    check("net income passes through from IS subtotals", kpi["net_income"] == 150000.0)
    check("gross margin % = gross_profit/revenue (60.0)", kpi["gross_margin_pct"] == 60.0)
    check("net margin % = net_income/revenue (15.0)", kpi["net_margin_pct"] == 15.0)
    check("current ratio uses trail CurrentLiabilities (500000/250000 = 2.0)",
          kpi["current_ratio"] == 2.0)
    check("current liabilities recovered from trail = 250000", kpi["current_liabilities"] == 250000.0)
    check("DSO = AR/revenue*days (120000/1000000*30 = 3.6)", kpi["dso_days"] == 3.6)

    print("P10 — graceful n/a (no plugged values when inputs absent)")
    no_trail = {**SYNTH, "statements": {**SYNTH["statements"]}}
    no_trail["statements"] = dict(SYNTH["statements"])
    no_trail["statements"].pop("reasoning_trail", None)
    k2 = ed.derive_kpis(no_trail)
    check("current ratio is None (n/a) with no reasoning trail", k2["current_ratio"] is None)
    zero_rev = {**SYNTH}
    zr_st = dict(SYNTH["statements"])
    zr_is = {"subtotals": dict(SYNTH["statements"]["income_statement"]["subtotals"], revenue=0.0)}
    zr_st["income_statement"] = zr_is
    zero_rev["statements"] = zr_st
    k3 = ed.derive_kpis(zero_rev)
    check("gross margin is None (n/a) when revenue is 0 (no div-by-zero)",
          k3["gross_margin_pct"] is None)

    print("P10 — rendered HTML")
    doc = ed.render_dashboard(SYNTH)
    check("HTML contains the entity name", "Nimbus Widgets LLC (FICTITIOUS)" in doc)
    check("HTML contains net income value (150,000.00)", "150,000.00" in doc)
    check("HTML contains a KPI value (60.0% gross margin)", "60.0%" in doc)
    check("HTML surfaces the reconciliation FLAG exception", "s-flag" in doc and "35,000.00" in doc)
    check("HTML carries the traceability badge verbatim", "TB-only - NOT audit-traceable" in doc)
    check("HTML shows the self-certified governance banner", "SELF-CERTIFIED" in doc)
    check("HTML references the RLS / JWT multi-tenant reuse note (auth not reimplemented here)",
          "rls-policy-authoring" in doc and "jwt-embed-issuance" in doc)
    urls = re.findall(r"https?://", doc)
    check("HTML is self-contained (no http:// or https:// resource references)", len(urls) == 0)

    print("P10 — committed sample dashboard")
    sample = os.path.join(HERE, "..", "skills", "per-entity-dashboard", "examples",
                          "sample-entity-dashboard.html")
    check("committed sample dashboard exists", os.path.exists(sample))
    if os.path.exists(sample):
        html_text = open(sample, encoding="utf-8").read()
        check("sample contains the (synthetic) entity name 'Meridian Robotics'",
              "Meridian Robotics" in html_text)
        check("sample contains net income (202,500.00)", "202,500.00" in html_text)
        check("sample contains a KPI value (60.0% gross margin)", "60.0%" in html_text)
        check("sample is self-contained (no http/https references)",
              len(re.findall(r"https?://", html_text)) == 0)

    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} checks passed.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
