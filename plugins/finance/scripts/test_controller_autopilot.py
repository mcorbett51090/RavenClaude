#!/usr/bin/env python3
"""test_controller_autopilot.py - acceptance/regression suite for the close autopilot.

Stdlib-only, zero-dependency test runner (no pytest). Run:  python3 test_controller_autopilot.py
Exits 0 iff every acceptance test the FORGE plan pinned as load-bearing passes. Each
test maps to a plan.md phase gate or a G5 red-team mitigation, so a regression that
erodes a control (e.g. the submit-only orchestrator boundary) fails CI loudly.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(HERE, "..", "skills", "produce-gaap-statements", "examples")
ENT = os.path.join(EX, "meridian-robotics.json")
COA = os.path.join(EX, "coa-mapping.csv")
COA_BAD = os.path.join(EX, "coa-mapping-misclassified.csv")
TB = os.path.join(EX, "trial-balance-2026-06.csv")
PRIOR = os.path.join(EX, "trial-balance-2026-05.csv")
SUB = os.path.join(EX, "subledger-2026-06.csv")
GLD = os.path.join(EX, "gl-detail-2026-06.csv")
EXP = json.load(open(os.path.join(EX, "expected-subtotals-2026-06.json")))

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(("  PASS " if cond else "  FAIL ") + name)


def py(mod, *args, expect_rc=0):
    r = subprocess.run([sys.executable, os.path.join(HERE, mod), *args],
                       capture_output=True, text=True)
    return r


def main():
    import statement_engine as se  # noqa
    print("P1 — entity + COA mapping")
    check("valid entity validates (rc0)", py("entity_config.py", "--validate", ENT).returncode == 0)
    check("COA lint passes on the correct map",
          py("statement_engine.py", "--entity", ENT, "--coa", COA, "--tb", TB, "--lint-map").returncode == 0)

    print("P2 — statement engine (classification correctness)")
    out = se.run(json.load(open(ENT)), COA, TB, GLD, PRIOR, strict=True)
    iss, bss = out["income_statement"]["subtotals"], out["balance_sheet"]["subtotals"]
    check("IS subtotals == hand-derived golden",
          all(abs(iss[k] - v) < 0.01 for k, v in EXP["income_statement"].items()))
    check("BS subtotals == hand-derived golden",
          all(abs(bss[k] - v) < 0.01 for k, v in EXP["balance_sheet"].items()))
    check("traceability badge lifts to GL-detail-traced with --gl-detail",
          out["traceability_badge"] == "GL-detail-traced")
    tb_only = se.run(json.load(open(ENT)), COA, TB, None, None, strict=True)
    check("badge is 'TB-only - NOT audit-traceable' without GL detail",
          "TB-only" in tb_only["traceability_badge"])
    check("cash flow is labeled unaudited_draft", out["cash_flow"]["label"] == "unaudited_draft")
    bad = se.run(json.load(open(ENT)), COA_BAD, TB, None, None, strict=False)
    bads = bad["income_statement"]["subtotals"]
    check("MISCLASSIFICATION caught via gross_profit (subtotal test, not tautological balance)",
          abs(bads["gross_profit"] - EXP["income_statement"]["gross_profit"]) >= 0.01)
    check("...while net_income is UNCHANGED (proves a balance-check cannot catch it)",
          abs(bads["net_income"] - EXP["income_statement"]["net_income"]) < 0.01)
    with tempfile.TemporaryDirectory() as d:
        partial = os.path.join(d, "partial.csv")
        with open(COA) as fh, open(partial, "w") as w:
            w.writelines(fh.readlines()[:-2])  # drop last two accounts
        check("--strict BLOCKS on unmapped accounts (rc3)",
              py("statement_engine.py", "--entity", ENT, "--coa", partial, "--tb", TB, "--strict").returncode == 3)

    print("P0 — controls spine (state machine + audit ledger)")
    with tempfile.TemporaryDirectory() as d:
        def cs(*a):
            return py("close_state.py", "--run-dir", d, "--now", "2026-07-06T00:00:00+00:00", *a)
        cs("submit", "--actor", "alice", "--amount", "500000")
        check("illegal transition submitted->locked refused (rc!=0)",
              cs("lock", "--actor", "bob").returncode != 0)
        cs("review", "--actor", "bob")
        check("SoD: preparer self-approve above threshold REFUSED (Ramp anti-pattern)",
              cs("approve", "--actor", "alice", "--threshold", "100000").returncode != 0)
        check("approve by a different actor succeeds", cs("approve", "--actor", "carol", "--threshold", "100000").returncode == 0)
        check("verify: clean hash chain OK", cs("verify").returncode == 0)
        # tamper
        ap = os.path.join(d, "audit.jsonl")
        lines = open(ap).read().splitlines()
        ev = json.loads(lines[0]); ev["detail"]["amount"] = 1; lines[0] = json.dumps(ev)
        open(ap, "w").write("\n".join(lines) + "\n")
        check("verify: tampered audit line detected (rc!=0)", cs("verify").returncode != 0)

    print("P4 — orchestrator submit-only invariant")
    src = open(os.path.join(HERE, "controller_cycle.py")).read()
    # strip comments/strings-ish: just assert no .approve(/.lock(/.reopen( call on a ledger
    calls = re.findall(r"\.(approve|lock|reopen|auto_cert|autocert)\s*\(", src)
    check("controller_cycle.py never calls approve/lock/reopen (submit-only boundary)", len(calls) == 0)
    with tempfile.TemporaryDirectory() as d:
        r = py("controller_cycle.py", "--entity", ENT, "--coa", COA, "--tb", TB,
               "--prior-tb", PRIOR, "--subledger", SUB, "--run-dir", d,
               "--now", "2026-07-06T00:00:00+00:00")
        check("full cycle runs and lands state=submitted", r.returncode == 0 and "submitted" in r.stdout)
        st = json.load(open(os.path.join(d, "state.json")))
        check("orchestrator left the package at 'submitted' (never advanced)", st["state"] == "submitted")

    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} acceptance tests passed.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
