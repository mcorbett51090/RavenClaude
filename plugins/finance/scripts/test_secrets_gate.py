#!/usr/bin/env python3
"""test_secrets_gate.py - acceptance suite for the finance secret/PII scan gate.

Stdlib-only, zero-dependency runner (no pytest). Run:  python3 test_secrets_gate.py
Exits 0 iff every load-bearing property of hooks/scan-finance-secrets.sh holds:

  - --ci EXITS NON-ZERO on a file carrying a fake secret/PII shape (blocks a merge);
  - --ci EXITS ZERO on a clean file (no false gate failure);
  - the sanctioned "env-var NAME only" reference + documented placeholders do NOT
    trip the gate (os.environ / example.com / 'ENV-VAR NAME');
  - ADVISORY (default) mode ALWAYS exits 0 even when it finds a secret, so it is
    safe to wire as a non-blocking PostToolUse hook.

All fixtures are written to a throwaway temp dir OUTSIDE the repo and are OBVIOUSLY
synthetic (AKIAEXAMPLE..., a well-known test SSN, a test-card PAN). No real
credential or PII is ever created. Env-var NAMES only — never a value.
"""
from __future__ import annotations

import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "..", "hooks", "scan-finance-secrets.sh")

# Obviously-fake secret/PII shapes — synthetic, never real.
DIRTY = (
    "aws_key = AKIAEXAMPLE1234567890\n"       # AWS access-key shape
    "ssn: 452-11-7834\n"                        # US SSN shape (synthetic; NOT a known-dummy the scanner allowlists)
    "client_secret = s3cr3tExampleValue987\n"  # OAuth client secret with a value
    "api_key = abcdef123456\n"                  # generic api_key assignment
    "card 4111111111111111\n"                   # Visa test PAN
)

# Clean file: no secrets, plus the SANCTIONED patterns that must NOT trip.
CLEAN = (
    "This workpaper has no secrets in it.\n"
    'token = os.environ["FINANCE_API_TOKEN"]  # env-var NAME only, never a value\n'
    "client_secret_env points at an ENV-VAR NAME, not a value\n"
    "questions -> support@example.com\n"
)

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(("  PASS " if cond else "  FAIL ") + name)


def run(*args):
    return subprocess.run(["bash", HOOK, *args], capture_output=True, text=True)


def main():
    check("hook script exists + is executable",
          os.path.isfile(HOOK) and os.access(HOOK, os.X_OK))

    with tempfile.TemporaryDirectory() as d:
        dirty = os.path.join(d, "dirty.txt")
        clean = os.path.join(d, "clean.txt")
        with open(dirty, "w") as fh:
            fh.write(DIRTY)
        with open(clean, "w") as fh:
            fh.write(CLEAN)

        print("secrets-gate — --ci gates a merge on a fake secret/PII shape")
        r = run("--ci", dirty)
        check("--ci exits NON-ZERO on the dirty fixture (blocks merge)",
              r.returncode != 0)
        check("--ci reports the AWS key shape", "aws-access-key" in r.stderr)
        check("--ci reports the SSN shape", "us-ssn" in r.stderr)
        check("--ci reports the credit-card PAN shape", "credit-card-pan" in r.stderr)

        print("secrets-gate — --ci stays green on a clean file")
        r = run("--ci", clean)
        check("--ci exits 0 on the clean fixture (no false gate failure)",
              r.returncode == 0)
        check("clean file produces no findings block", "match(es)" not in r.stderr)

        print("secrets-gate — sanctioned env-var-NAME references never trip")
        # Each sanctioned line, scanned alone, must be clean under --ci.
        for i, ln in enumerate(CLEAN.strip().splitlines()):
            f = os.path.join(d, f"line{i}.txt")
            with open(f, "w") as fh:
                fh.write(ln + "\n")
            check(f"sanctioned line does not trip --ci: {ln[:48]!r}",
                  run("--ci", f).returncode == 0)

        print("secrets-gate — ADVISORY (default) mode never blocks")
        r = run(dirty)  # no --ci
        check("advisory mode exits 0 EVEN WITH findings (non-blocking hook)",
              r.returncode == 0)
        check("advisory mode still prints the findings to stderr",
              "aws-access-key" in r.stderr)

    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} acceptance tests passed.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
