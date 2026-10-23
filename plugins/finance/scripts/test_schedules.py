#!/usr/bin/env python3
"""test_schedules.py - acceptance suite for schedule_engine.py (P12).

Stdlib-only, zero-dependency runner (no pytest). Run:  python3 test_schedules.py
Exits 0 iff every assertion the close-schedules contract pins as load-bearing passes.

The load-bearing claims under test:
  1. Each schedule TIES: beginning + movements == ending, asset-by-asset AND in total.
  2. Depreciation rollforwards (gross cost / accumulated depreciation / NBV) all match
     the HAND-DERIVED goldens, and NBV == gross cost - accumulated depreciation.
  3. A disposal removes cost + accumulated depreciation and books the right gain/loss.
  4. Prepaid amortization and deferred-revenue waterfall match the hand-derived goldens,
     with additions (billings) and drawdowns (amortization/recognition) signed so the
     rollforward closes.
  5. A full-term waterfall drains the balance to exactly 0 and its drawdowns sum to total.
  6. --strict BLOCKS (rc5) a schedule whose portfolio rollforward does not tie.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(HERE, "..", "skills", "close-schedules", "examples")
FA = os.path.join(EX, "fixed-assets-2026-06.csv")
PP = os.path.join(EX, "prepaids-2026-06.csv")
DR = os.path.join(EX, "deferred-revenue-2026-06.csv")
EXP = json.load(open(os.path.join(EX, "expected-schedules-2026-06.json")))
PERIOD = "2026-06"

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(("  PASS " if cond else "  FAIL ") + name)


def approx(a, b):
    return abs(a - b) < 0.01


def py(*args, expect_rc=0):
    return subprocess.run([sys.executable, os.path.join(HERE, "schedule_engine.py"), *args],
                          capture_output=True, text=True)


def rf(schedule, key):
    return schedule["rollforward"][key]


def main():
    sys.path.insert(0, HERE)
    import schedule_engine as se  # noqa

    print("P12 — depreciation (fixed-asset rollforward)")
    dep = se.depreciation(se._read_csv(FA), PERIOD)
    g = EXP["depreciation"]
    check("gross-cost rollforward ties AND == golden",
          rf(dep, "gross_cost")["ties"]
          and all(approx(rf(dep, "gross_cost")[k], g["gross_cost"][k]) for k in g["gross_cost"]))
    check("accumulated-depreciation rollforward ties AND == golden",
          rf(dep, "accumulated_depreciation")["ties"]
          and all(approx(rf(dep, "accumulated_depreciation")[k], g["accumulated_depreciation"][k])
                  for k in g["accumulated_depreciation"]))
    check("NBV rollforward ties AND == golden (beginning + additions - dep - disposals = ending)",
          rf(dep, "net_book_value")["ties"]
          and all(approx(rf(dep, "net_book_value")[k], g["net_book_value"][k]) for k in g["net_book_value"]))
    check("cross-tie: ending NBV == ending gross cost - ending accumulated depreciation",
          dep["rollforward"]["nbv_equals_cost_less_accum"] is True)
    by_id = {a["asset_id"]: a for a in dep["assets"]}
    check("per-asset ending NBV == golden (in-service, mid-life, disposed)",
          all(approx(by_id[k]["ending_nbv"], v) for k, v in g["per_asset_ending_nbv"].items()))
    check("disposal removes cost + accum and books gain/loss on proceeds",
          approx(by_id["FA-050"]["disposal_cost"], 30000.0)
          and approx(by_id["FA-050"]["disposal_accum_depreciation"], 18000.0)
          and approx(by_id["FA-050"]["gain_loss_on_disposal"], g["gain_loss_on_disposal"]["FA-050"]))
    check("addition (van placed in service this period) depreciates its first month",
          approx(by_id["FA-200"]["additions"], 48000.0) and approx(by_id["FA-200"]["depreciation"], 1000.0))
    check("every asset row ties individually", all(a["nbv_tie_ok"] for a in dep["assets"]))
    check("overall depreciation schedule reports ties=True", dep["ties"] is True)

    print("P12 — prepaid amortization schedule")
    pre = se.prepaid(se._read_csv(PP), PERIOD)
    gp = EXP["prepaid"]
    check("prepaid portfolio rollforward ties AND == golden",
          pre["rollforward"]["ties"]
          and approx(pre["rollforward"]["beginning"], gp["opening"])
          and approx(pre["rollforward"]["additions"], gp["additions"])
          and approx(pre["rollforward"]["reductions"], gp["amortization"])
          and approx(pre["rollforward"]["ending"], gp["ending"]))
    pid = {i["prepaid_id"]: i for i in pre["items"]}
    check("per-item ending prepaid balance == golden",
          all(approx(pid[k]["ending_balance"], v) for k, v in gp["per_item_ending"].items()))
    check("full-term waterfall drains to 0 and drawdowns sum to total (PP-INS)",
          approx(pid["PP-INS"]["full_schedule"][-1]["closing"], 0.0)
          and approx(sum(r["drawdown"] for r in pid["PP-INS"]["full_schedule"]), 12000.0))
    check("overall prepaid schedule reports ties=True", pre["ties"] is True)

    print("P12 — deferred-revenue waterfall")
    dr = se.deferred_revenue(se._read_csv(DR), PERIOD)
    gd = EXP["deferred_revenue"]
    check("deferred-revenue portfolio rollforward ties AND == golden",
          dr["rollforward"]["ties"]
          and approx(dr["rollforward"]["beginning"], gd["opening"])
          and approx(dr["rollforward"]["additions"], gd["billings"])
          and approx(dr["rollforward"]["reductions"], gd["recognized"])
          and approx(dr["rollforward"]["ending"], gd["ending"]))
    did = {i["contract_id"]: i for i in dr["items"]}
    check("per-contract ending deferred balance == golden",
          all(approx(did[k]["ending_balance"], v) for k, v in gd["per_item_ending"].items()))
    check("new contract billed this period adds to deferred and recognizes its first month",
          approx(did["DR-B"]["billings"], 36000.0) and approx(did["DR-B"]["recognized"], 3000.0))
    check("overall deferred-revenue schedule reports ties=True", dr["ties"] is True)

    print("P12 — sign symmetry: a credit memo (negative amount) negates the positive schedule (A-10)")
    def _row(kind, total):
        if kind == "prepaid":
            return {"prepaid_id": "X", "description": "d", "total_amount": str(total),
                    "term_months": "12", "start_month": "2026-01"}
        return {"contract_id": "X", "description": "d", "billing_amount": str(total),
                "term_months": "12", "start_month": "2026-01"}

    def _negates(kind, pos_total):
        fn = se.prepaid if kind == "prepaid" else se.deferred_revenue
        keys = ("opening_balance", "ending_balance", "monthly_amount",
                "additions" if kind == "prepaid" else "billings",
                "amortization" if kind == "prepaid" else "recognized")
        ok = True
        for per in ("2025-12", "2026-01", "2026-02", "2026-06", "2026-11", "2026-12", "2027-01"):
            pos = fn([_row(kind, pos_total)], per)["items"][0]
            neg = fn([_row(kind, -pos_total)], per)["items"][0]
            ok = ok and all(approx(neg[k], -pos[k]) for k in keys)
        return ok

    for kind in ("prepaid", "deferred-revenue"):
        check(f"{kind}: -1,200 over 12 months is the row-by-row negation of +1,200 (every period)",
              _negates(kind, 1200.0))
        check(f"{kind}: -1,000.00 over 12 months (rounding remainder) negates +1,000.00",
              _negates(kind, 1000.0))
    neg_pre = se.prepaid([_row("prepaid", -1200.0)], "2026-12")
    neg_item = neg_pre["items"][0]
    pos_full = se.prepaid([_row("prepaid", 1200.0)], "2026-12")["items"][0]["full_schedule"]
    check("negative prepaid: final period ending is 0 and the item ties",
          approx(neg_item["ending_balance"], 0.0) and neg_item["tie_ok"] and neg_pre["ties"])
    check("negative prepaid: first period amortizes ONE month (-100), not the whole total",
          approx(se.prepaid([_row("prepaid", -1200.0)], "2026-01")["items"][0]["amortization"], -100.0))
    check("negative prepaid: full_schedule is the exact negation of the positive one, ends at 0",
          all(approx(n[k], -p[k]) for n, p in zip(neg_item["full_schedule"], pos_full)
              for k in ("opening", "addition", "drawdown", "closing"))
          and approx(neg_item["full_schedule"][-1]["closing"], 0.0)
          and approx(sum(r["drawdown"] for r in neg_item["full_schedule"]), -1200.0))
    mixed = se.deferred_revenue([_row("deferred", 1200.0), _row("deferred", -300.0)], "2026-06")
    check("a credit memo mixed with an invoice still ties as a portfolio (net 900 billed)",
          mixed["ties"] is True and approx(mixed["rollforward"]["ending"], 450.0))

    print("P12 — CLI + --strict blocking")
    r = py("depreciation", "--assets", FA, "--period", PERIOD)
    check("CLI depreciation runs (rc0) and emits ties=true JSON",
          r.returncode == 0 and json.loads(r.stdout)["ties"] is True)
    # The engine ties by construction, so a real CSV cannot produce a non-tie. We
    # exercise the --strict block path directly on a result whose tie flag is forced
    # False (simulating a future rollforward bug), asserting the guard fires (rc5).
    bad = se.deferred_revenue(se._read_csv(DR), PERIOD)
    bad["ties"] = False
    check("--strict blocks a non-tying schedule (rc5)", se._emit(bad, None, strict=True) == 5)
    check("non-strict still emits (rc0) even when it does not tie", se._emit(bad, None, strict=False) == 0)

    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} acceptance tests passed.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
