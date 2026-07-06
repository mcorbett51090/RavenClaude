#!/usr/bin/env python3
"""test_recon_match.py - acceptance suite for the reconciliation auto-match engine.

Stdlib-only, zero-dependency runner (no pytest). Run:  python3 test_recon_match.py
Exits 0 iff every assertion the P8 brief pinned as load-bearing passes:
  - exact + tolerance + grouped matches ALL land (per the hand-derived golden);
  - the genuine break above materiality is FLAGGED, not auto-certified;
  - a within-materiality residual AUTO-CERTIFIES (materiality-bounded, not zero-break).
The expected golden is hand-derived by independent arithmetic in
skills/reconciliation-automatch/examples/expected-recon-2026-06.json — NOT frozen
from an engine run, so a bug cannot ship inside its own golden.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(HERE, "..", "skills", "reconciliation-automatch", "examples")
ENT = os.path.join(EX, "nimbus-widgets.json")
GL = os.path.join(EX, "gl-lines-2026-06.csv")
SUB = os.path.join(EX, "subledger-lines-2026-06.csv")
EXP = json.load(open(os.path.join(EX, "expected-recon-2026-06.json")))

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(("  PASS " if cond else "  FAIL ") + name)


def py(mod, *args):
    return subprocess.run([sys.executable, os.path.join(HERE, mod), *args],
                          capture_output=True, text=True)


def main():
    import recon_match as rm  # noqa

    entity = json.load(open(ENT))
    out = rm.run(entity, GL, SUB, tolerance=1.00)
    by_acct = {a["account"]: a for a in out["accounts"]}

    print("P8 — match ladder (exact / tolerance / grouped all land)")
    check("summary match tallies == hand-derived golden",
          out["summary"]["matches"] == EXP["summary"]["matches"])
    check("exact matches present (INV-501/INV-502/PP-01/BILL-900 = 4)",
          out["summary"]["matches"]["exact"] == 4)
    check("tolerance match present (WIRE-88, 0.50 within tolerance = 1)",
          out["summary"]["matches"]["tolerance"] == 1)
    check("grouped match present (DEP-777 two GL -> one subledger = 1)",
          out["summary"]["matches"]["grouped"] == 1)

    # per-account structural + numeric parity with the golden
    for acct, exp in EXP["accounts"].items():
        got = by_acct[acct]
        mt = {"exact": 0, "tolerance": 0, "grouped": 0}
        for m in got["matches"]:
            mt[m["type"]] += 1
        ok = (got["status"] == exp["status"]
              and abs(got["gl_total"] - exp["gl_total"]) < 0.01
              and abs(got["subledger_total"] - exp["subledger_total"]) < 0.01
              and abs(got["matched_delta"] - exp["matched_delta"]) < 0.01
              and abs(got["residual"] - exp["residual"]) < 0.01
              and len(got["breaks"]) == exp["n_breaks"]
              and mt == exp["match_types"])
        check(f"account {acct}: status/totals/residual/matches == golden", ok)

    print("P8 — grouped match ties the many-to-one deposit exactly")
    grp = [m for m in by_acct["1100"]["matches"] if m["type"] == "grouped"][0]
    check("grouped DEP-777 matched 2 GL lines to 1 subledger line",
          len(grp["gl"]) == 2 and len(grp["subledger"]) == 1)
    check("grouped DEP-777 net delta is 0 (12000+8000 == 20000)",
          abs(grp["delta"]) < 0.01)

    print("P8 — the genuine break is FLAGGED, not auto-certified")
    check("account 2000 (BILL-999 missing from subledger) is FLAGGED",
          by_acct["2000"]["status"] == "FLAGGED")
    check("account 2000 residual 30000 >= materiality 25000",
          by_acct["2000"]["residual"] >= entity["materiality_threshold"])
    check("account 2000 has exactly one break (BILL-999)",
          len(by_acct["2000"]["breaks"]) == 1
          and by_acct["2000"]["breaks"][0]["reference"] == "BILL-999")

    print("P8 — within-materiality residual AUTO-CERTIFIES (materiality-bounded)")
    check("account 1200 AUTO-CERTIFIED despite a nonzero residual (500 < 25000)",
          by_acct["1200"]["status"] == "AUTO-CERTIFIED"
          and 0 < by_acct["1200"]["residual"] < entity["materiality_threshold"])
    check("account 1200 still DISCLOSES its immaterial unmatched item in the trail",
          len(by_acct["1200"]["breaks"]) == 1
          and by_acct["1200"]["breaks"][0]["reference"] == "PP-MISC")
    check("tolerance-explained residual auto-certifies (1000 residual 0.00)",
          by_acct["1000"]["status"] == "AUTO-CERTIFIED"
          and abs(by_acct["1000"]["residual"]) < 0.01)

    print("P8 — summary rollup + --strict gate")
    check("3 auto-certified, 1 flagged, 2 breaks (golden)",
          out["summary"]["auto_certified"] == 3
          and out["summary"]["flagged"] == 1
          and out["summary"]["breaks"] == 2)
    r_strict = py("recon_match.py", "--entity", ENT, "--gl", GL,
                  "--subledger", SUB, "--strict")
    check("--strict exits rc3 while an account is FLAGGED (blocks the close)",
          r_strict.returncode == 3)
    r_open = py("recon_match.py", "--entity", ENT, "--gl", GL, "--subledger", SUB)
    check("without --strict the run reports and exits rc0", r_open.returncode == 0)

    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} acceptance tests passed.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
