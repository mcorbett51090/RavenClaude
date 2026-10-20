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

    print("A-11 — SoD compares MAGNITUDE and fails closed on non-finite amounts")
    for label, amt in (("negative -5,000,000", "-5000000"), ("positive +5,000,000 (control)", "5000000")):
        with tempfile.TemporaryDirectory() as d:
            def cs(*a):
                return py("close_state.py", "--run-dir", d, "--now", "2026-07-06T00:00:00+00:00", *a)
            cs("submit", "--actor", "alice", "--amount", amt)
            cs("review", "--actor", "bob")
            r = cs("approve", "--actor", "alice", "--threshold", "1000")
            check(f"SoD: preparer self-approve of a {label} package REFUSED",
                  r.returncode != 0 and "SoD" in r.stderr)
            check(f"{label}: a different approver still succeeds",
                  cs("approve", "--actor", "carol", "--threshold", "1000").returncode == 0)
    for bad_amt in ("nan", "inf"):
        with tempfile.TemporaryDirectory() as d:
            r = py("close_state.py", "--run-dir", d, "submit", "--actor", "alice", "--amount", bad_amt)
            check(f"submit with a non-finite amount ({bad_amt}) is rejected at submit",
                  r.returncode != 0 and "finite" in r.stderr
                  and not os.path.exists(os.path.join(d, "state.json")))
    sys.path.insert(0, HERE)
    import close_state as cst
    with tempfile.TemporaryDirectory() as d:
        led = cst.CloseLedger(d)
        led.submit("alice", 10.0)
        led.review("bob")
        st = led.load_state()
        st["package_amount"] = float("nan")  # hand-edited / legacy state.json
        led._write_state(st)
        try:
            led.approve("alice", 1000.0)
            refused = False
        except SystemExit as e:
            refused = "SoD" in str(e.code)
        check("a NaN package_amount already in state.json fails CLOSED (self-approve REFUSED)", refused)

    print("A-12 — verify replays the audit stream against state.json")
    import re as _re

    def _approved(d):
        def cs(*a):
            return py("close_state.py", "--run-dir", d, "--now", "2026-07-06T00:00:00+00:00", *a)
        cs("submit", "--actor", "alice", "--amount", "5000")
        cs("review", "--actor", "bob")
        cs("approve", "--actor", "carol", "--threshold", "1000")
        return cs

    def _edit_state(d, **kw):
        sp = os.path.join(d, "state.json")
        st = json.load(open(sp))
        st.update(kw)
        json.dump(st, open(sp, "w"), indent=2)

    with tempfile.TemporaryDirectory() as d:
        cs = _approved(d)
        ok = cs("verify")
        check("untampered approved package: verify OK (rc0)", ok.returncode == 0)
        m = _re.search(r"(\d+) event\(s\), tip ([0-9a-f]{64})", ok.stdout)
        check("verify prints the event count and the FULL chain-tip hash", m is not None and m.group(1) == "3")
        recorded_tip = m.group(2) if m else None
    with tempfile.TemporaryDirectory() as d:
        cs = _approved(d)
        _edit_state(d, state="locked", self_certified=False)
        r = cs("verify")
        check("state.json hand-edited to locked/self_certified:false -> verify FAILS (rc!=0)",
              r.returncode != 0 and r.stdout.startswith("FAIL"))
        check("...and the failure names the mismatched field", "'state'" in r.stdout)
    for field, bad in (("approver", "dave"), ("preparer", "carol"), ("package_amount", 1.0)):
        with tempfile.TemporaryDirectory() as d:
            cs = _approved(d)
            _edit_state(d, **{field: bad})
            r = cs("verify")
            check(f"state.json {field} edited -> verify FAILS naming '{field}'",
                  r.returncode != 0 and f"'{field}'" in r.stdout)
    with tempfile.TemporaryDirectory() as d:
        cs = _approved(d)
        cs("lock", "--actor", "carol", "--approval-token", "human-entered")
        check("lock with a non-agent token (self_certified false): verify OK", cs("verify").returncode == 0)
        _edit_state(d, self_certified=True)
        r = cs("verify")
        check("locked package flipped to self_certified:true -> verify FAILS naming 'self_certified'",
              r.returncode != 0 and "'self_certified'" in r.stdout)
    with tempfile.TemporaryDirectory() as d:
        cs = _approved(d)
        os.remove(os.path.join(d, "state.json"))
        check("state.json deleted after an approved package -> verify FAILS", cs("verify").returncode != 0)
    with tempfile.TemporaryDirectory() as d:
        cs = _approved(d)
        ap = os.path.join(d, "audit.jsonl")
        lines = open(ap).read().splitlines()
        open(ap, "w").write("\n".join(lines[:-1]) + "\n")
        check("last audit line deleted with state.json untouched -> verify FAILS (state disagrees)",
              cs("verify").returncode != 0)
        # The documented residual limit: truncate the tail AND rewind state.json consistently.
        _edit_state(d, state="in_review")
        sp = os.path.join(d, "state.json")
        st = json.load(open(sp))
        st.pop("approver", None)
        json.dump(st, open(sp, "w"), indent=2)
        r = cs("verify")
        m2 = _re.search(r"(\d+) event\(s\), tip ([0-9a-f]{64})", r.stdout)
        check("consistent tail truncation still passes (documented limit) but prints the SHORTER "
              "count and a DIFFERENT tip to compare with a recorded one",
              r.returncode == 0 and m2 is not None and m2.group(1) == "2"
              and m2.group(2) != recorded_tip)
    check("close_state.py docstring states the tail-truncation limit honestly",
          "RESIDUAL LIMIT" in open(os.path.join(HERE, "close_state.py")).read())

    print("A-17 — reconcile_summary sums duplicate account rows (does not overwrite)")
    import reconcile_summary as rs
    with tempfile.TemporaryDirectory() as d:
        dup_tb = os.path.join(d, "dup-tb.csv")
        with open(dup_tb, "w") as fh:
            fh.write("account,description,debit,credit\n"
                     "1000,Cash,500,0\n1000,Cash adjustment,0,200\n2000,AP,0,300\n")
        by = {r["account"]: r for r in rs.reconcile(dup_tb, 1.0)["accounts"]}
        check("1000 dr 500 + 1000 cr 200 -> book_balance 300.0 (not the last row's -200.0)",
              by["1000"]["book_balance"] == 300.0)
        check("the FIRST row's description is kept", by["1000"]["description"] == "Cash")
        check("a single-row account is unchanged (2000 -> -300.0)", by["2000"]["book_balance"] == -300.0)
        sub = os.path.join(d, "dup-sub.csv")
        with open(sub, "w") as fh:
            fh.write("account,subledger_balance\n1000,300\n")
        tied = {r["account"]: r for r in rs.reconcile(dup_tb, 1.0, sub)["accounts"]}["1000"]
        check("tie-out against a 300 sub-ledger PASSes (book 300, diff 0)",
              tied["status"] == "PASS" and tied["difference"] == 0.0)
        prior = os.path.join(d, "dup-prior.csv")
        with open(prior, "w") as fh:
            fh.write("account,description,debit,credit\n1000,Cash,100,0\n2000,AP,0,300\n")
        mv = {m["account"]: m for m in rs.flux(dup_tb, prior, 1.0)["material_movements"]}
        check("flux on the summed account: 300 vs prior 100 -> movement 200.0",
              "1000" in mv and mv["1000"]["movement"] == 200.0)

    print("A-19 — RLS denial script: docker missing is a SKIP (rc3), never a green exit 0")
    import shutil
    rls_sh = os.path.join(HERE, "..", "skills", "warehouse-dashboard", "models", "rls",
                          "run_rls_denial_test.sh")
    bash = shutil.which("bash")
    with tempfile.TemporaryDirectory() as d:
        for tool in ("dirname", "seq"):  # the script's own needs; deliberately NOT docker
            if shutil.which(tool):
                os.symlink(shutil.which(tool), os.path.join(d, tool))
        base_env = {"PATH": d, "HOME": d}
        check("test PATH really has no docker", shutil.which("docker", path=d) is None)

        def rls(**extra):
            return subprocess.run([bash, rls_sh], capture_output=True, text=True,
                                  env={**base_env, **extra})
        r = rls()
        check("PATH without docker -> rc 3", r.returncode == 3)
        check("...with the 'SKIP - THIS IS NOT A PASS' banner", "SKIP - THIS IS NOT A PASS" in r.stdout)
        r = rls(RLS_TEST_ALLOW_SKIP="1")
        check("RLS_TEST_ALLOW_SKIP=1 -> rc 0 with the SAME banner",
              r.returncode == 0 and "SKIP - THIS IS NOT A PASS" in r.stdout)
        check("only the literal value 1 acknowledges a skip (RLS_TEST_ALLOW_SKIP=0 -> rc 3)",
              rls(RLS_TEST_ALLOW_SKIP="0").returncode == 3)
    check("run_rls_denial_test.sh is still executable", os.access(rls_sh, os.X_OK))

    print("A-7 — finance_calc npv-irr survives a long flow stream (no ZeroDivisionError)")

    def _npv_at(rate, initial, flows):
        return -initial + sum(cf / (1 + rate) ** t for t, cf in enumerate(flows, start=1))

    def _is_root(pct, initial, flows):
        """The printed 2dp IRR is the root iff NPV changes sign within +-0.005 pp of it."""
        lo, hi = (pct - 0.005) / 100, (pct + 0.005) / 100
        return _npv_at(lo, initial, flows) * _npv_at(hi, initial, flows) <= 0

    for n in (80, 84, 400):
        r = py("finance_calc.py", "npv-irr", "--rate", "10%", "--initial", "1000",
               "--flows", *(["20"] * n))
        check(f"{n} flows: rc 0, no traceback, NPV printed",
              r.returncode == 0 and "Traceback" not in r.stderr and "-> NPV" in r.stdout)
    r80 = py("finance_calc.py", "npv-irr", "--rate", "10%", "--initial", "1000",
             "--flows", *(["20"] * 80))
    m = re.search(r"-> IRR\s+:\s+(-?[\d.]+)%", r80.stdout)
    check("the 80-flow control still solves the IRR (NPV changes sign at it; re-derived here)",
          m is not None and _is_root(float(m.group(1)), 1000.0, [20.0] * 80))
    r84 = py("finance_calc.py", "npv-irr", "--rate", "10%", "--initial", "1000",
             "--flows", *(["20"] * 84))
    m = re.search(r"-> IRR\s+:\s+(-?[\d.]+)%", r84.stdout)
    check("84 flows now solves a real IRR (NPV changes sign at it), not a crash",
          m is not None and _is_root(float(m.group(1)), 1000.0, [20.0] * 84))
    r = py("finance_calc.py", "npv-irr", "--rate", "10%", "--initial", "0", "--flows", "10", "10")
    check("no root in range -> 'no IRR root in [-99%, 1000%]' (rc 0)",
          r.returncode == 0 and "no IRR root in [-99%, 1000%]" in r.stdout)

    print("A-8 — finance_calc unit-economics range-checks gross margin")
    ue_args = ("unit-economics", "--arpa", "1200", "--churn", "14%", "--cac", "3000")
    r = py("finance_calc.py", *ue_args, "--gross-margin", "78")
    check("--gross-margin 78 (a bare percent) is REJECTED rc 2 with the 'pass 0.78' hint",
          r.returncode == 2 and "pass 0.78 for 78%" in r.stderr and "-> LTV" not in r.stdout)
    for bad in ("0", "-0.2", "1.5", "150%"):
        check(f"--gross-margin {bad} is rejected (rc 2)",
              py("finance_calc.py", *ue_args, "--gross-margin", bad).returncode == 2)
    ok = py("finance_calc.py", *ue_args, "--gross-margin", "0.78")
    # hand-derived: 1200 * 0.78 = 936 gross profit/yr; LTV = 936 / 0.14 = 6,685.71; LTV:CAC 2.23
    check("--gross-margin 0.78 is accepted and unchanged (LTV 6,685.71, 2.23 : 1)",
          ok.returncode == 0 and "6,685.71" in ok.stdout and "2.23 : 1" in ok.stdout)
    check("--gross-margin 78% and 100% (the inclusive upper bound) are accepted",
          py("finance_calc.py", *ue_args, "--gross-margin", "78%").returncode == 0
          and py("finance_calc.py", *ue_args, "--gross-margin", "100%").returncode == 0)

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
