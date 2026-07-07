#!/usr/bin/env python3
"""test_remeasure.py - acceptance suite for remeasure.py (currency translation + CTA).

Stdlib-only, zero-dependency runner (no pytest). Run:  python3 test_remeasure.py
Exits 0 iff every load-bearing claim of the W1 multi-currency stage holds. Each check
maps to a spec requirement: current-rate golden, temporal golden, the CTA self-check,
a rate_class-missing BLOCK, the hyperinflation REFUSE, and the all-USD zero-drift no-op.

The goldens are HAND-DERIVED (examples/expected-remeasured-*.json), NOT frozen from a
remeasure.py run, so a sign/rate regression fails here loudly.
"""
from __future__ import annotations

import csv
import io
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(HERE, "..", "skills", "multi-currency-translation", "examples")
ENT = os.path.join(EX, "eur-sub.json")
COA = os.path.join(EX, "coa-mapping-fx.csv")
TB = os.path.join(EX, "tb-eur-sub-2026-06.csv")
RATES_CUR = os.path.join(EX, "rates-current.json")
RATES_TEMP = os.path.join(EX, "rates-temporal.json")
RATES_HYPER = os.path.join(EX, "rates-hyperinflation.json")
USD_ENT = os.path.join(EX, "usd-sub.json")
USD_TB = os.path.join(EX, "tb-usd-sub-2026-06.csv")
EXP_CUR = json.load(open(os.path.join(EX, "expected-remeasured-current.json")))
EXP_TEMP = json.load(open(os.path.join(EX, "expected-remeasured-temporal.json")))

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(("  PASS " if cond else "  FAIL ") + name)


def py(*args):
    return subprocess.run([sys.executable, os.path.join(HERE, "remeasure.py"), *args],
                          capture_output=True, text=True)


def subtotals_match(got: dict, want: dict) -> bool:
    return all(k in got and abs(got[k] - v) < 0.01 for k, v in want.items())


def main():
    import remeasure as rm  # noqa

    print("W1.1 — current-rate translation golden")
    cur = rm.run(ENT, COA, TB, RATES_CUR)
    check("current-rate IS subtotals == hand-derived golden",
          subtotals_match(cur["translated_income_statement"],
                          EXP_CUR["translated_income_statement"]))
    check("current-rate BS subtotals == hand-derived golden",
          subtotals_match(cur["translated_balance_sheet"],
                          EXP_CUR["translated_balance_sheet"]))
    check("current-rate consolidated BS balances (delta 0.00)",
          abs(cur["translated_balance_sheet"]["balance_delta"]) < 0.01)
    check("current-rate plug is a CTA (equity/OCI, not net income)",
          cur["plug"]["type"] == "CTA" and cur["plug"]["section"] == "Equity")
    check("current-rate CTA == 200.00", abs(cur["plug"]["presentation_amount"] - 200.0) < 0.01)
    check("current-rate net income == 1050.00 (unaffected by CTA)",
          abs(cur["translated_income_statement"]["net_income"] - 1050.0) < 0.01)
    check("Inventory (asset) translated @ closing 1.10 under current-rate, not @ hist",
          any(t["account"] == "1200" and abs(t["rate"] - 1.10) < 1e-9
              for t in cur["translation_trail"]))

    print("W1.2 — temporal remeasurement golden")
    temp = rm.run(ENT, COA, TB, RATES_TEMP)
    check("temporal IS subtotals == hand-derived golden",
          subtotals_match(temp["translated_income_statement"],
                          EXP_TEMP["translated_income_statement"]))
    check("temporal BS subtotals == hand-derived golden",
          subtotals_match(temp["translated_balance_sheet"],
                          EXP_TEMP["translated_balance_sheet"]))
    check("temporal consolidated BS balances (delta 0.00)",
          abs(temp["translated_balance_sheet"]["balance_delta"]) < 0.01)
    check("temporal plug is a remeasurement G/L flowing to NET INCOME (IS)",
          temp["plug"]["type"] == "remeasurement_gain_loss"
          and temp["plug"]["statement"] == "IS")
    check("temporal remeasurement loss == -80.00",
          abs(temp["plug"]["presentation_amount"] - (-80.0)) < 0.01)
    check("temporal net income == 970.00 (1050 before, -80 remeasurement)",
          abs(temp["translated_income_statement"]["net_income"] - 970.0) < 0.01)
    check("Inventory (non-monetary) translated @ historical 1.02 under temporal",
          any(t["account"] == "1200" and abs(t["rate"] - 1.02) < 1e-9
              for t in temp["translation_trail"]))
    check("Cash (monetary) translated @ closing 1.10 under temporal",
          any(t["account"] == "1000" and abs(t["rate"] - 1.10) < 1e-9
              for t in temp["translation_trail"]))

    print("W1.3 — CTA self-check")
    check("current-rate CTA self-check present + passes (analytical == plug == 200)",
          cur["cta_self_check"]["passes"]
          and abs(cur["cta_self_check"]["analytical"] - 200.0) < 0.01
          and abs(cur["cta_self_check"]["plug"] - 200.0) < 0.01)
    # Force a self-check failure by feeding a rates.json whose average makes the
    # analytical figure diverge from the plug ONLY if the plug were wrong — instead we
    # prove the guard fires when the analytical figure is corrupted. We do this by
    # monkeypatching analytical_cta to return a wrong number and asserting SystemExit 5.
    orig = rm.analytical_cta
    try:
        rm.analytical_cta = lambda *a, **k: 999.99
        raised = 0
        try:
            rm.run(ENT, COA, TB, RATES_CUR)
        except SystemExit as e:
            raised = e.code
        check("CTA self-check BLOCKS (rc5) when analytical != balancing plug", raised == 5)
    finally:
        rm.analytical_cta = orig

    print("W1.4 — rate_class-missing BLOCK")
    with tempfile.TemporaryDirectory() as d:
        bad = os.path.join(d, "coa-bad.csv")
        with open(COA) as fh:
            rows = list(csv.DictReader(fh))
            fields = list(rows[0].keys())
        with open(bad, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            for r in rows:
                if r["account"] == "1200":
                    r["rate_class"] = ""  # blank -> must block like an unmapped account
                w.writerow(r)
        rc = py("--entity", ENT, "--coa", bad, "--tb", TB, "--rates", RATES_CUR).returncode
        check("blank rate_class BLOCKS (rc3)", rc == 3)
        # An out-of-vocabulary rate_class also blocks.
        bad2 = os.path.join(d, "coa-bad2.csv")
        with open(bad2, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            for r in rows:
                if r["account"] == "1500":
                    r["rate_class"] = "WOBBLE"
                w.writerow(r)
        rc2 = py("--entity", ENT, "--coa", bad2, "--tb", TB, "--rates", RATES_CUR).returncode
        check("invalid rate_class value BLOCKS (rc3)", rc2 == 3)

    print("W1.5 — hyperinflation REFUSE (current_rate)")
    r = py("--entity", ENT, "--coa", COA, "--tb", TB, "--rates", RATES_HYPER)
    check("highly_inflationary + current_rate REFUSED (rc7)", r.returncode == 7)
    check("refusal cites ASC 830 vs IAS 29",
          "ASC 830" in r.stderr and "IAS 29" in r.stderr)

    print("W1.6 — zero-drift no-op (functional == presentation == USD)")
    with tempfile.TemporaryDirectory() as d:
        out_tb = os.path.join(d, "usd-out.csv")
        r = py("--entity", USD_ENT, "--coa", COA, "--tb", USD_TB, "--out-tb", out_tb)
        check("all-USD entity runs as a no-op (rc0)", r.returncode == 0)
        with open(USD_TB, "rb") as f:
            src_bytes = f.read()
        with open(out_tb, "rb") as f:
            out_bytes = f.read()
        check("presentation TB is a BYTE-IDENTICAL copy of the source TB",
              src_bytes == out_bytes)
        no_op = rm.run(USD_ENT, COA, USD_TB)
        check("no-op result carries no_op flag and method=None",
              no_op.get("no_op") is True and no_op.get("method") is None)

    print("W1.7 — translated TB is emitted balanced (feeds consolidate's rc6 guardrail)")
    with tempfile.TemporaryDirectory() as d:
        out_tb = os.path.join(d, "eur-usd.csv")
        py("--entity", ENT, "--coa", COA, "--tb", TB, "--rates", RATES_TEMP,
           "--out-tb", out_tb)
        rows = list(csv.DictReader(io.StringIO(open(out_tb).read())))
        dsum = round(sum(float(x["debit"]) for x in rows), 2)
        csum = round(sum(float(x["credit"]) for x in rows), 2)
        check("emitted presentation TB has debits == credits (balanced)",
              abs(dsum - csum) < 0.01)
        check("emitted TB currency column stamped USD",
              all(x["currency"] == "USD" for x in rows))

    print("W1.8 — emitted TB is consumable by the per-entity consolidate path")
    # consolidate.py runs statement_engine.run per entity and relies on build_balance_
    # sheet's balance_delta (its rc6 guardrail). Prove the emitted USD TB, fed back
    # through statement_engine with the SAME COA (which maps the injected plug lines),
    # produces a balanced BS whose subtotals equal the hand-derived temporal golden.
    import statement_engine as se
    with tempfile.TemporaryDirectory() as d:
        out_tb = os.path.join(d, "eur-usd.csv")
        py("--entity", ENT, "--coa", COA, "--tb", TB, "--rates", RATES_TEMP,
           "--out-tb", out_tb)
        stmt = se.run(json.load(open(USD_ENT)), COA, out_tb, strict=True)
        bss = stmt["balance_sheet"]["subtotals"]
        check("statement_engine.run on the emitted TB balances (delta 0.00 -> no rc6)",
              abs(bss["balance_delta"]) < 0.01)
        check("re-run BS subtotals still match the temporal golden",
              subtotals_match(bss, EXP_TEMP["translated_balance_sheet"]))

    print("W1.9 — REV_EXP_HIST temporal branch: COGS/deprec/prepaid-amort @ HISTORICAL")
    # The goldens' expenses are all at the average rate, so the distinct
    # temporal branch — non-monetary-linked P&L (COGS, depreciation, prepaid
    # amortization; rate_class REV_EXP_HIST) at the HISTORICAL rate, ordinary P&L
    # (REV_EXP) at the AVERAGE rate — is otherwise untested. Exercise rate_for directly.
    branch_rates = {"closing": 1.10, "average": 1.05, "historical": {"default": 1.00}}
    temporal_hist = rm.rate_for("temporal", "REV_EXP_HIST", "6000", branch_rates)
    temporal_avg = rm.rate_for("temporal", "REV_EXP", "6000", branch_rates)
    check("temporal: REV_EXP_HIST resolves to the HISTORICAL rate (1.00)",
          abs(temporal_hist - 1.00) < 1e-9)
    check("temporal: REV_EXP resolves to the AVERAGE rate (1.05)",
          abs(temporal_avg - 1.05) < 1e-9)
    check("temporal: the two P&L rate classes DIFFER (the branch is distinct, not dead)",
          abs(temporal_hist - temporal_avg) > 1e-9)
    # Under current_rate the historical/ordinary P&L split is IGNORED — all P&L @ average.
    current_hist = rm.rate_for("current_rate", "REV_EXP_HIST", "6000", branch_rates)
    current_ord = rm.rate_for("current_rate", "REV_EXP", "6000", branch_rates)
    check("current_rate: BOTH REV_EXP_HIST and REV_EXP resolve to AVERAGE (split ignored)",
          abs(current_hist - 1.05) < 1e-9 and abs(current_ord - 1.05) < 1e-9)

    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} acceptance tests passed.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
