#!/usr/bin/env python3
"""test_consolidate.py - acceptance suite for consolidate.py (P9).

Stdlib-only, zero-dependency runner (no pytest). Run:  python3 test_consolidate.py
Exits 0 iff every assertion the consolidation contract pins as load-bearing passes.

The load-bearing claims under test:
  1. A naive sum DOUBLE-COUNTS the intercompany balances (both sides present).
  2. After elimination the intercompany lines NET TO ZERO in the consolidated column.
  3. The consolidated balance sheet still BALANCES to 0.00.
  4. Consolidated subtotals equal the HAND-DERIVED goldens (external-only revenue/COGS;
     gross profit and net income unchanged by a revenue-neutral IC sale elimination).
  5. The elimination journal must balance; an unbalanced one is BLOCKED.
  6. A non-functional-currency entity is FLAGGED for CTA (not silently rolled up).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(HERE, "..", "skills", "consolidate-entities", "examples")
CONFIG = os.path.join(EX, "atlas-group-2026-06.json")
EXP = json.load(open(os.path.join(EX, "expected-consolidated-2026-06.json")))

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(("  PASS " if cond else "  FAIL ") + name)


def main():
    sys.path.insert(0, HERE)
    import consolidate as con  # noqa

    print("P9 — consolidation + intercompany elimination")
    out = con.consolidate(CONFIG, strict=True)

    # --- 1. Pre-elimination sum double-counts the intercompany amounts ---
    ic = out["eliminations"]["intercompany_lines"]
    exp_pre = EXP["pre_elimination_intercompany"]
    check("pre-elim sum double-counts IC receivable/payable (100k each, both sides present)",
          abs(ic["Intercompany receivable"]["pre_elimination"]
              - exp_pre["Intercompany receivable"]) < 0.01
          and abs(ic["Intercompany payable"]["pre_elimination"]
                  - exp_pre["Intercompany payable"]) < 0.01)
    check("pre-elim sum double-counts IC revenue/COGS (200k each)",
          abs(ic["Intercompany revenue"]["pre_elimination"]
              - exp_pre["Intercompany revenue"]) < 0.01
          and abs(ic["Intercompany cost of goods sold"]["pre_elimination"]
                  - exp_pre["Intercompany cost of goods sold"]) < 0.01)
    pre = out["pre_elimination_subtotals"]
    check("pre-elim consolidated revenue is grossed up by the 200k IC sale (1,600,000)",
          abs(pre["income_statement"]["revenue"] - 1600000.0) < 0.01)

    # --- 2. Post-elimination the intercompany lines net to zero ---
    check("post-elim IC receivable nets to 0.00",
          abs(ic["Intercompany receivable"]["consolidated"]) < 0.01)
    check("post-elim IC payable nets to 0.00",
          abs(ic["Intercompany payable"]["consolidated"]) < 0.01)
    check("post-elim IC revenue nets to 0.00",
          abs(ic["Intercompany revenue"]["consolidated"]) < 0.01)
    check("post-elim IC COGS nets to 0.00",
          abs(ic["Intercompany cost of goods sold"]["consolidated"]) < 0.01)

    # --- 3 & 4. Consolidated subtotals == hand-derived goldens; BS balances ---
    cis = out["consolidated_subtotals"]["income_statement"]
    cbs = out["consolidated_subtotals"]["balance_sheet"]
    check("consolidated IS subtotals == hand-derived golden (external-only rev/COGS)",
          all(abs(cis[k] - v) < 0.01
              for k, v in EXP["consolidated_income_statement"].items()))
    check("consolidated BS subtotals == hand-derived golden",
          all(abs(cbs[k] - v) < 0.01
              for k, v in EXP["consolidated_balance_sheet"].items()))
    check("consolidated balance sheet balances to 0.00 (delta)",
          abs(cbs["balance_delta"]) < 0.01)
    check("elimination is revenue-neutral: gross profit UNCHANGED vs pre-elim (800,000)",
          abs(cis["gross_profit"] - pre["income_statement"]["gross_profit"]) < 0.01
          and abs(cis["gross_profit"] - 800000.0) < 0.01)
    check("elimination is income-neutral: net income UNCHANGED vs pre-elim (490,000)",
          abs(cis["net_income"] - pre["income_statement"]["net_income"]) < 0.01
          and abs(cis["net_income"] - 490000.0) < 0.01)
    check("consolidated revenue is external-only (1,400,000 = grossed 1.6M less 200k IC)",
          abs(cis["revenue"] - 1400000.0) < 0.01)

    # --- worksheet shape: entity columns + eliminations + consolidated ---
    row = next(r for r in out["worksheet"]["balance_sheet"]
               if r["line"] == "Intercompany receivable")
    check("worksheet row carries per-entity columns + eliminations + consolidated",
          set(row["entities"]) == {e["name"] for e in out["entities"]}
          and "eliminations" in row and "consolidated" in row)

    # --- 5. An unbalanced elimination journal is BLOCKED ---
    with tempfile.TemporaryDirectory() as d:
        bad_elim = os.path.join(d, "bad-elim.csv")
        with open(bad_elim, "w") as w:
            w.write("ic_id,description,statement,section,line,debit,credit\n")
            # Only one side of the loan -> debits != credits.
            w.write("IC-LOAN,broken,BS,CurrentLiabilities,Intercompany payable,100000,0\n")
        bad_cfg = os.path.join(d, "bad-config.json")
        cfg = json.load(open(CONFIG))
        cfg["eliminations"] = bad_elim
        # Point entity paths back at the real examples dir (absolute).
        for ent in cfg["entities"]:
            for k in ("profile", "coa", "tb"):
                ent[k] = os.path.join(EX, ent[k])
        with open(bad_cfg, "w") as w:
            json.dump(cfg, w)
        r = subprocess.run(
            [sys.executable, os.path.join(HERE, "consolidate.py"), "--config", bad_cfg],
            capture_output=True, text=True)
        check("unbalanced elimination journal is BLOCKED (rc4)", r.returncode == 4)

    # --- 6. Non-functional-currency entity flagged for CTA ---
    flagged = out["currency_translation_note"]["flagged_entities"]
    check("EUR subsidiary flagged for CTA (functional != presentation currency)",
          any(f["functional_currency"] == "EUR" for f in flagged))
    check("USD parent NOT flagged for CTA",
          all(f["functional_currency"] != "USD" for f in flagged))

    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} acceptance tests passed.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
