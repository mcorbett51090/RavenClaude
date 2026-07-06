#!/usr/bin/env python3
"""test_elt_stage.py - acceptance/regression suite for the finance-shaped ELT staging seam.

Stdlib-only, zero-dependency (no pytest). Run:  python3 test_elt_stage.py
Exits 0 iff every load-bearing property of tb_stage.py holds:
  - a NetSuite-style signed-amount export normalizes to the canonical staging schema,
    byte-identical to the hand-derived golden;
  - a QBO-style separate-debit/credit export normalizes to the SAME canonical target
    (one adapter, two source shapes);
  - a bad (out-of-balance) export is REJECTED with a non-zero exit, not silently staged;
  - the canonical header contract and the debits==credits invariant are enforced by
    `validate`.

The golden `examples/expected-staging-2026-06.csv` is hand-derived from the raw export
by independent arithmetic (each signed amount split into debit/credit by sign), NOT
frozen from a tb_stage.py run — so a staging bug cannot ship inside its own golden.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(HERE, "..", "skills", "finance-elt-staging", "examples")
RAW_NS = os.path.join(EX, "raw-export-netsuite.csv")
MAP_NS = os.path.join(EX, "column-map-netsuite.json")
RAW_QBO = os.path.join(EX, "raw-export-qbo.csv")
MAP_QBO = os.path.join(EX, "column-map-qbo.json")
RAW_BAD = os.path.join(EX, "raw-export-bad.csv")
GOLDEN = os.path.join(EX, "expected-staging-2026-06.csv")

CANONICAL = "account,description,debit,credit,entity,period,currency"

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(("  PASS " if cond else "  FAIL ") + name)


def run(*args):
    return subprocess.run([sys.executable, os.path.join(HERE, "tb_stage.py"), *args],
                          capture_output=True, text=True)


def main():
    import tb_stage as ts  # noqa: F401  (import-cleanliness check + direct-API access)

    print("P7 — ELT staging (raw export -> canonical staging schema)")
    golden = open(GOLDEN).read()
    check("golden header is EXACTLY the canonical staging contract",
          golden.splitlines()[0] == CANONICAL)

    with tempfile.TemporaryDirectory() as d:
        out_ns = os.path.join(d, "staging-ns.csv")
        r = run("stage", "--raw", RAW_NS, "--column-map", MAP_NS, "--out", out_ns)
        check("NetSuite signed-amount export stages (rc0)", r.returncode == 0)
        check("staged NetSuite output is byte-identical to the hand-derived golden",
              os.path.exists(out_ns) and open(out_ns).read() == golden)

        out_qbo = os.path.join(d, "staging-qbo.csv")
        r = run("stage", "--raw", RAW_QBO, "--column-map", MAP_QBO, "--out", out_qbo)
        check("QBO separate-debit/credit export stages (rc0)", r.returncode == 0)
        check("QBO export normalizes to the SAME canonical target (one adapter, two shapes)",
              os.path.exists(out_qbo) and open(out_qbo).read() == golden)

        check("staged output validates clean", run("validate", "--staging", out_ns).returncode == 0)

        # CLI override supplies/overrides the close-period watermark + entity dimension.
        out_ovr = os.path.join(d, "staging-ovr.csv")
        run("stage", "--raw", RAW_NS, "--column-map", MAP_NS, "--out", out_ovr,
            "--period", "2026-07", "--entity", "MRI-UK")
        with open(out_ovr) as fh:
            body = fh.read()
        check("--period / --entity overrides land in the watermark + dimension",
              ",MRI-UK,2026-07,USD" in body and "2026-06" not in body)

        # A bad (out-of-balance) export must be REJECTED, and no file left behind.
        out_bad = os.path.join(d, "staging-bad.csv")
        r = run("stage", "--raw", RAW_BAD, "--column-map", MAP_NS, "--out", out_bad)
        check("out-of-balance export REJECTED (rc!=0)", r.returncode != 0)
        check("...with an OUT OF BALANCE reason on stderr", "OUT OF BALANCE" in r.stderr)
        check("...and no staging file is published on rejection", not os.path.exists(out_bad))

    # validate detects a hand-corrupted (out-of-balance) staging file directly.
    with tempfile.TemporaryDirectory() as d:
        corrupt = os.path.join(d, "corrupt.csv")
        lines = golden.splitlines()
        lines[1] = "1000,Cash,999999,0,MRI,2026-06,USD"  # inflate a debit -> unbalanced
        open(corrupt, "w").write("\n".join(lines) + "\n")
        check("validate flags a tampered/unbalanced staging file (rc1)",
              run("validate", "--staging", corrupt).returncode == 1)

    # validate rejects a wrong/reordered header (byte-identity to the dbt model).
    with tempfile.TemporaryDirectory() as d:
        wrong = os.path.join(d, "wrong-header.csv")
        open(wrong, "w").write("account,debit,credit,description,entity,period,currency\n"
                               "1000,502500,0,Cash,MRI,2026-06,USD\n")
        check("validate rejects a reordered/non-canonical header (rc1)",
              run("validate", "--staging", wrong).returncode == 1)

    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} acceptance tests passed.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
