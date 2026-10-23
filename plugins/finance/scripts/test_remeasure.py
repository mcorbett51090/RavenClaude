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


# Seeds for the generated wide-TB regression (A-1). Per-line 2dp rounding accumulates, so a
# 40-account TB drifts past 0.01 on most inputs; with the pre-fix self-check (which compared
# the analytical CTA with the ROUNDED imbalance) seeds 1, 2, 4, 6, 7, 8, 10 and 11 below all
# exited rc5 on a correct translation. Do not shrink this list without re-proving the teeth.
WIDE_SEEDS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)


def gen_wide_book(seed: int, d: str, n: int = 40, with_synthetic: bool = False):
    """Write a deterministic n-account EUR COA + balanced TB (cents-level amounts) into d.

    The COA carries NO synthetic __CTA__/__REMEAS_GL__ rows unless with_synthetic. Returns
    (coa_path, tb_path). The TB is balanced exactly by adjusting the first Equity row.
    """
    import random
    rng = random.Random(seed)
    kinds = [("CurrentAssets", "BS", "debit", "MONETARY"),
             ("NonCurrentAssets", "BS", "debit", "NONMONETARY"),
             ("CurrentLiabilities", "BS", "credit", "MONETARY"),
             ("Equity", "BS", "credit", "EQUITY_CONTRIB"),
             ("Revenue", "IS", "credit", "REV_EXP"),
             ("OpEx", "IS", "debit", "REV_EXP")]
    coa, tb = [], []
    for i in range(n):
        sec, st, nb, rc = kinds[i % len(kinds)]
        acct = str(1000 + i)
        coa.append([acct, f"Acct {acct}", st, sec, f"Line {sec} {acct}", nb, rc])
        cents = rng.randint(100_00, 90_000_00) + rng.randint(1, 99)
        tb.append([acct, f"Acct {acct}", cents if nb == "debit" else 0,
                   cents if nb == "credit" else 0])
    diff = sum(r[2] for r in tb) - sum(r[3] for r in tb)
    eq = next(r for r, c in zip(tb, coa) if c[3] == "Equity")
    if diff >= 0:
        eq[3] += diff
    else:
        eq[2] += -diff
    if with_synthetic:
        coa.append(["__CTA__", "CTA", "BS", "Equity", "Cumulative translation adjustment (CTA)",
                    "credit", "EQUITY_RE"])
        coa.append(["__REMEAS_GL__", "Remeasurement", "IS", "OtherIncomeExpense",
                    "Remeasurement gain/(loss)", "credit", "REV_EXP"])
    coa_path, tb_path = os.path.join(d, f"coa-{seed}.csv"), os.path.join(d, f"tb-{seed}.csv")
    with open(coa_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["account", "description", "statement", "section", "line",
                    "normal_balance", "rate_class"])
        w.writerows(coa)
    with open(tb_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["account", "description", "debit", "credit", "entity", "period", "currency"])
        for r in tb:
            w.writerow([r[0], r[1], f"{r[2] / 100:.2f}", f"{r[3] / 100:.2f}",
                        "EURSUB", "2026-06", "EUR"])
    return coa_path, tb_path


def consolidate_rc(d: str, coa: str, tb: str):
    """Run consolidate.py (strict) over ONE USD entity built from (coa, tb); return the result."""
    cfg = os.path.join(d, "consol-cfg.json")
    with open(cfg, "w") as fh:
        json.dump({"schema_version": 1, "group_name": "G", "presentation_currency": "USD",
                   "fiscal_period": "2026-06",
                   "entities": [{"profile": USD_ENT, "coa": coa, "tb": tb, "role": "parent"}]}, fh)
    return subprocess.run([sys.executable, os.path.join(HERE, "consolidate.py"), "--config", cfg],
                          capture_output=True, text=True)


def run_rc(fn, *a, **k):
    """Call fn; return (result, exit_code) with SystemExit mapped to its code."""
    try:
        return fn(*a, **k), 0
    except SystemExit as e:
        return None, e.code


def main():
    import remeasure as rm  # noqa
    from statement_engine import load_mapping as se_load_mapping  # noqa

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

    print("W1.10 — wide generated TB: per-line rounding must NOT trip the CTA self-check (A-1)")
    with tempfile.TemporaryDirectory() as d:
        rates_wide = os.path.join(d, "rates-wide.json")
        with open(rates_wide, "w") as fh:
            json.dump({"method": "current_rate", "closing": 1.0837, "average": 1.0592,
                       "historical": {"default": 1.0123}}, fh)
        codes, all_pass, drift = [], True, 0.0
        for seed in WIDE_SEEDS:
            coa_w, tb_w = gen_wide_book(seed, d)
            res, rc = run_rc(rm.run, ENT, coa_w, tb_w, rates_wide)
            codes.append(rc)
            if res is not None:
                all_pass = all_pass and res["cta_self_check"]["passes"]
                sc = res["cta_self_check"]
                drift = max(drift, abs(sc["plug"] - sc.get("plug_unrounded", sc["plug"])))
        check("every generated 40-account EUR TB translates (rc0, never rc5): " + str(codes),
              all(c == 0 for c in codes))
        check("cta_self_check.passes true on every generated TB", all_pass)
        check("rounded plug is kept on the TB while plug_unrounded is reported "
              "(max |plug - plug_unrounded| %.4f)" % drift, 0 < drift < 1.0)
        coa_w, tb_w = gen_wide_book(WIDE_SEEDS[0], d)
        res, _ = run_rc(rm.run, ENT, coa_w, tb_w, rates_wide)
        check("emitted translated TB still balances to the cent on rounded lines",
              res is not None
              and abs(sum(r["debit"] for r in res["translated_tb"])
                      - sum(r["credit"] for r in res["translated_tb"])) < 0.01)
        # Must-fail control: a genuinely WRONG translation (equity at the CLOSING rate instead
        # of historical) must still BLOCK rc5 on the wide book AND on the golden example.
        real_rate_for = rm.rate_for

        def wrong_rate_for(method, rate_class, account, rates):
            if rate_class in rm.EQUITY_CLASSES:
                return float(rates["closing"])
            return real_rate_for(method, rate_class, account, rates)

        rm.rate_for = wrong_rate_for
        try:
            _, rc_wide = run_rc(rm.run, ENT, coa_w, tb_w, rates_wide)
            _, rc_gold = run_rc(rm.run, ENT, COA, TB, RATES_CUR)
        finally:
            rm.rate_for = real_rate_for
        check("equity-at-closing (wrong) still BLOCKS rc5 on the wide TB", rc_wide == 5)
        check("equity-at-closing (wrong) still BLOCKS rc5 on the golden example", rc_gold == 5)

    print("W1.11 — --out-coa: the translated TB's plug rows must be mappable by consolidate (A-15)")
    with tempfile.TemporaryDirectory() as d:
        coa_w, tb_w = gen_wide_book(7, d)  # 40 accounts, NO __CTA__/__REMEAS_GL__ rows
        for method, plug_acct, other_acct in (("current_rate", "__CTA__", "__REMEAS_GL__"),
                                              ("temporal", "__REMEAS_GL__", "__CTA__")):
            rates_m = os.path.join(d, f"rates-{method}.json")
            with open(rates_m, "w") as fh:
                json.dump({"method": method, "closing": 1.0837, "average": 1.0592,
                           "historical": {"default": 1.0123}}, fh)
            out_tb = os.path.join(d, f"usd-{method}.csv")
            out_coa = os.path.join(d, f"coa-{method}.csv")
            bare = py("--entity", ENT, "--coa", coa_w, "--tb", tb_w, "--rates", rates_m,
                      "--out-tb", out_tb)
            check(f"{method}: --out-tb without --out-coa prints a stderr NOTE naming {plug_acct} "
                  "and --out-coa",
                  bare.returncode == 0 and "NOTE" in bare.stderr and plug_acct in bare.stderr
                  and "--out-coa" in bare.stderr)
            before = consolidate_rc(d, coa_w, out_tb)
            check(f"{method}: consolidate with the ORIGINAL COA is BLOCKED (rc3, unmapped {plug_acct})",
                  before.returncode == 3 and plug_acct in before.stderr)
            full = py("--entity", ENT, "--coa", coa_w, "--tb", tb_w, "--rates", rates_m,
                      "--out-tb", out_tb, "--out-coa", out_coa)
            check(f"{method}: --out-tb + --out-coa runs (rc0) with no NOTE",
                  full.returncode == 0 and "NOTE" not in full.stderr)
            after = consolidate_rc(d, out_coa, out_tb)
            check(f"{method}: consolidate with the --out-coa file succeeds (rc0)",
                  after.returncode == 0)
            if after.returncode == 0:
                cbs = json.loads(after.stdout)["consolidated_subtotals"]["balance_sheet"]
                check(f"{method}: consolidated balance sheet balances to 0.00 on the 40-account book",
                      abs(cbs["balance_delta"]) < 0.01)
            mapped = se_load_mapping(out_coa) if os.path.exists(out_coa) else {}
            want = {"__CTA__": ("BS", "Equity"),
                    "__REMEAS_GL__": ("IS", "OtherIncomeExpense")}[plug_acct]
            check(f"{method}: {plug_acct} appended with the work_map mapping "
                  f"({want[0]}/{want[1]}); {other_acct} NOT added",
                  plug_acct in mapped and other_acct not in mapped
                  and (mapped[plug_acct]["statement"], mapped[plug_acct]["section"]) == want)
            with open(coa_w, encoding="utf-8") as f1:
                src_text = f1.read()
            out_text = open(out_coa, encoding="utf-8").read() if os.path.exists(out_coa) else ""
            check(f"{method}: every original COA row is preserved verbatim (only appended)",
                  out_text.startswith(src_text)
                  and len(out_text.splitlines()) == len(src_text.splitlines()) + 1)
        # A COA that ALREADY maps the plug rows (the shipped example) is not duplicated or NOTEd.
        again = os.path.join(d, "coa-example-out.csv")
        r = py("--entity", ENT, "--coa", COA, "--tb", TB, "--rates", RATES_CUR,
               "--out-tb", os.path.join(d, "ex.csv"), "--out-coa", again)
        accts = []
        if os.path.exists(again):
            with open(again, encoding="utf-8") as fh:
                accts = [row["account"] for row in csv.DictReader(fh)]
        check("a COA that already maps __CTA__ gets no duplicate row", r.returncode == 0
              and accts.count("__CTA__") == 1)
        r = py("--entity", ENT, "--coa", COA, "--tb", TB, "--rates", RATES_CUR,
               "--out-tb", os.path.join(d, "ex2.csv"))
        check("no NOTE when the input COA already maps the plug rows", "NOTE" not in r.stderr)
        # Zero-drift no-op: --out-coa is a byte-identical copy.
        noop = os.path.join(d, "coa-noop.csv")
        py("--entity", USD_ENT, "--coa", COA, "--tb", USD_TB,
           "--out-tb", os.path.join(d, "noop-tb.csv"), "--out-coa", noop)
        with open(COA, "rb") as f1:
            check("all-USD no-op: --out-coa is a BYTE-IDENTICAL copy of the input COA",
                  os.path.exists(noop) and f1.read() == open(noop, "rb").read())

    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} acceptance tests passed.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
