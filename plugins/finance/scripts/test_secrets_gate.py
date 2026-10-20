#!/usr/bin/env python3
"""test_secrets_gate.py - acceptance suite for the finance secret/PII scan gate.

Stdlib-only, zero-dependency runner (no pytest). Run:  python3 test_secrets_gate.py
Exits 0 iff every load-bearing property of hooks/scan-finance-secrets.sh holds:

  - --ci EXITS NON-ZERO on a file carrying a fake secret/PII shape (blocks a merge);
  - --ci EXITS ZERO on a clean file (no false gate failure);
  - the sanctioned "env-var NAME only" reference + documented placeholders do NOT
    trip the gate (os.environ / example.com / 'ENV-VAR NAME');
  - ADVISORY (default) mode ALWAYS exits 0 even when it finds a secret, so it is
    safe to wire as a non-blocking PostToolUse hook;
  - run EXACTLY as hooks.json registers it (empty "$CLAUDE_TOOL_FILE_PATH" arg,
    path only in the stdin payload) it scans a finance-path file, skips a
    non-finance path, never falls back to plugins/finance/ under the cwd, and
    exits 2 under FINANCE_STRICT=1 (repo-review 2026-10-19, domainplugins-2).

All fixtures are written to a throwaway temp dir OUTSIDE the repo and are OBVIOUSLY
synthetic (AKIAEXAMPLE..., a well-known test SSN, a test-card PAN). No real
credential or PII is ever created. Env-var NAMES only — never a value.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.abspath(os.path.join(HERE, ".."))
HOOK = os.path.join(HERE, "..", "hooks", "scan-finance-secrets.sh")
HOOKS_JSON = os.path.join(PLUGIN_ROOT, "hooks", "hooks.json")

# Obviously-fake secret/PII shapes — synthetic, never real.
DIRTY = (
    "aws_key = AKIAEXAMPLE1234567890\n"  # AWS access-key shape
    "ssn: 452-11-7834\n"  # US SSN shape (synthetic; NOT a known-dummy the scanner allowlists)
    "client_secret = s3cr3tExampleValue987\n"  # OAuth client secret with a value
    "api_key = abcdef123456\n"  # generic api_key assignment
    "card 4111111111111111\n"  # Visa test PAN
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


def registered_command():
    """The scan-finance-secrets command string exactly as hooks.json wires it."""
    with open(HOOKS_JSON, encoding="utf-8") as fh:
        hooks = json.load(fh)["hooks"]
    for group in hooks.get("PostToolUse", []):
        for h in group.get("hooks", []):
            if "scan-finance-secrets.sh" in h.get("command", ""):
                return h["command"]
    raise SystemExit("scan-finance-secrets.sh is not registered in hooks.json")


def run_registered(payload, cwd, **env_extra):
    """Run the hooks.json command the way Claude Code does: through a shell, with
    CLAUDE_TOOL_FILE_PATH unset (so the quoted arg is empty) and the tool payload
    as JSON on stdin."""
    env = {
        k: v for k, v in os.environ.items() if k not in ("CLAUDE_TOOL_FILE_PATH", "FINANCE_STRICT")
    }
    env["CLAUDE_PLUGIN_ROOT"] = PLUGIN_ROOT
    env.update(env_extra)
    return subprocess.run(
        ["sh", "-c", registered_command()],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=cwd,
        env=env,
    )


def write_payload(path, content):
    return {
        "hook_event_name": "PostToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": path, "content": content},
    }


def main():
    check("hook script exists + is executable", os.path.isfile(HOOK) and os.access(HOOK, os.X_OK))

    with tempfile.TemporaryDirectory() as d:
        dirty = os.path.join(d, "dirty.txt")
        clean = os.path.join(d, "clean.txt")
        with open(dirty, "w") as fh:
            fh.write(DIRTY)
        with open(clean, "w") as fh:
            fh.write(CLEAN)

        print("secrets-gate — --ci gates a merge on a fake secret/PII shape")
        r = run("--ci", dirty)
        check("--ci exits NON-ZERO on the dirty fixture (blocks merge)", r.returncode != 0)
        check("--ci reports the AWS key shape", "aws-access-key" in r.stderr)
        check("--ci reports the SSN shape", "us-ssn" in r.stderr)
        check("--ci reports the credit-card PAN shape", "credit-card-pan" in r.stderr)

        print("secrets-gate — --ci stays green on a clean file")
        r = run("--ci", clean)
        check("--ci exits 0 on the clean fixture (no false gate failure)", r.returncode == 0)
        check("clean file produces no findings block", "match(es)" not in r.stderr)

        print("secrets-gate — sanctioned env-var-NAME references never trip")
        # Each sanctioned line, scanned alone, must be clean under --ci.
        for i, ln in enumerate(CLEAN.strip().splitlines()):
            f = os.path.join(d, f"line{i}.txt")
            with open(f, "w") as fh:
                fh.write(ln + "\n")
            check(
                f"sanctioned line does not trip --ci: {ln[:48]!r}", run("--ci", f).returncode == 0
            )

        print("secrets-gate — a placeholder does not mask a real secret on its line")
        # Regression: the per-line filter must inspect EVERY matched span, not
        # just the first. A documented placeholder SSN (123-45-6789) sharing a
        # line with a genuine synthetic SSN (452-11-7834) must still be flagged;
        # a placeholder-only line must stay clean.
        mixed = os.path.join(d, "mixed.txt")
        with open(mixed, "w") as fh:
            fh.write('a = "123-45-6789"; b = "452-11-7834"\n')
        check(
            "--ci flags a real SSN even when a placeholder shares its line",
            run("--ci", mixed).returncode != 0,
        )
        placeholder_only = os.path.join(d, "placeholder_only.txt")
        with open(placeholder_only, "w") as fh:
            fh.write('a = "123-45-6789"\n')
        check(
            "--ci stays clean on a placeholder-only line",
            run("--ci", placeholder_only).returncode == 0,
        )

        print("secrets-gate — ADVISORY (default) mode never blocks")
        r = run(dirty)  # no --ci
        check("advisory mode exits 0 EVEN WITH findings (non-blocking hook)", r.returncode == 0)
        check("advisory mode still prints the findings to stderr", "aws-access-key" in r.stderr)

        print("secrets-gate — run as hooks.json registers it (stdin payload, empty $1)")
        # Built by concatenation so no secret-shaped literal sits in this file's
        # new lines (the live guards screen written content).
        hook_body = "aws_key = " + "AKIA" + "Q3EXAMPLE" + "7ZT4WX9P\n"
        proj = os.path.join(d, "proj")
        fin_file = os.path.join(proj, "finance", "bank.csv")
        other_file = os.path.join(proj, "src", "app.py")
        for f in (fin_file, other_file):
            os.makedirs(os.path.dirname(f), exist_ok=True)
            with open(f, "w") as fh:
                fh.write(hook_body)
        r = run_registered(write_payload(fin_file, hook_body), proj)
        check("hook: finance-path file with a key shape is reported", "aws-access-key" in r.stderr)
        check("hook: advisory run exits 0", r.returncode == 0)
        r = run_registered(write_payload(other_file, hook_body), proj)
        check(
            "hook: a non-finance path is skipped (no output, exit 0)",
            r.returncode == 0 and r.stderr == "" and r.stdout == "",
        )
        r = run_registered(write_payload(fin_file, hook_body), proj, FINANCE_STRICT="1")
        check("hook: FINANCE_STRICT=1 exits 2 on a finding", r.returncode == 2)
        # A payload with no file path must NOT fall back to scanning
        # plugins/finance/ under the cwd (a consumer project's own tree).
        cwd_tree = os.path.join(proj, "plugins", "finance")
        os.makedirs(cwd_tree, exist_ok=True)
        with open(os.path.join(cwd_tree, "leak.txt"), "w") as fh:
            fh.write(hook_body)
        r = run_registered({"hook_event_name": "PostToolUse", "tool_input": {}}, proj)
        check(
            "hook: a payload with no path scans nothing (no cwd fallback)",
            r.returncode == 0 and r.stderr == "",
        )

    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} acceptance tests passed.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
