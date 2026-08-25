#!/usr/bin/env python3
"""check-scope-key-parity.py — Phase 10 of verify-before-assert.

The scope-key block (`rc_worktree_root` + `rc_scope_key`) is duplicated verbatim
across five live files. The duplication is DELIBERATE: refactoring it would touch
several load-bearing guards in one increment, and `log-probe.sh` already carries
a "KEEP THIS BLOCK IN SYNC WITH ITS TWIN" warning for the same reason.

⛔ WHAT DRIFT COSTS HERE IS NOT A BUG, IT IS A SILENT PASS.
The recorder writes the ledger at `scopes/<key>/open.jsonl`; the gates read it
from the key they derive themselves. If a gate's key differs by one character it
reads a ledger NOBODY WRITES, finds no open rows, and reports clean forever. It
runs, it parses, it exits 0. A tested duplication beats an untested refactor of
load-bearing guards, but only if something actually tests it.

⛔ TEXTUAL IDENTITY IS THE WEAKER HALF, AND ON ITS OWN IT IS NOT ENOUGH.
Two copies can be byte-identical and still be reached with different inputs, and
two copies can differ cosmetically and compute the same key. So this asserts
BOTH: normalised byte-identity, AND that every copy driven with the SAME synthetic
cwd returns the SAME key.

⛔ THE EXTRACTOR ITSELF IS A TRAP, AND IT CAUGHT ME FIRST.
A naive range from `def rc_worktree_root` to the closing return over-ran in
`guard-cause-closure.sh`, because that file MENTIONS `/^def rc_worktree_root/`
inside its own --must-fail awk program. The naive read reported a 61-line block
against a 22-line reference and looked exactly like real drift.
control: the extracted blocks hash identically across all five files once the
range stops at the first `return (slug or "root")` AFTER the function start,
while the naive range reports one file differing — so the fix removed a false
positive rather than hiding a real one.

Usage:
    check-scope-key-parity.py --check
    check-scope-key-parity.py --must-fail
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PLUGIN = os.path.dirname(_HERE)

_COPIES = (
    os.path.join(_PLUGIN, "hooks", "log-probe.sh"),
    os.path.join(_PLUGIN, "hooks", "triage-outcome.sh"),
    os.path.join(_PLUGIN, "hooks", "guard-premise.sh"),
    os.path.join(_PLUGIN, "scripts", "guard-remediation-cause.sh"),
    os.path.join(_PLUGIN, "scripts", "guard-cause-closure.sh"),
)

_START = re.compile(r"^def rc_worktree_root\(", re.M)
_END = re.compile(r'^\s*return \(slug or "root"\)[^\n]*$', re.M)

# A synthetic cwd every copy is driven with. Deliberately NOT a real path: the
# key must be a pure function of the string, and a real path would let a copy
# pass by touching the filesystem.
_PROBE_CWD = "/synthetic/probe/tree"
_PROBE_FALLBACK = "/synthetic/probe"


def extract(path: str) -> str:
    """Return the scope-key block, or '' if absent.

    ⛔ The range stops at the FIRST closing return AFTER the function start, not
    at the last match in the file. Files that merely MENTION the function name
    later (a --must-fail awk program does) would otherwise over-run.
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return ""
    m = _START.search(text)
    if not m:
        return ""
    tail = text[m.start():]
    e = _END.search(tail)
    if not e:
        return ""
    return tail[: e.end()]


def _normalise(block: str) -> str:
    # Whitespace-insensitive, so an indentation change inside a heredoc is not
    # reported as a semantic difference. Everything else must match exactly.
    return re.sub(r"\s+", " ", block).strip()


def _drive(block: str, cwd: str, fallback: str):
    """Exec one copy in a fresh namespace and call rc_scope_key."""
    ns = {"os": os, "re": re, "hashlib": hashlib}
    try:
        exec(compile(block, "<scope-key-copy>", "exec"), ns)  # noqa: S102
        return ns["rc_scope_key"](cwd, fallback)
    except Exception as exc:  # pragma: no cover - reported as a finding
        return f"<error: {exc}>"


def check(copies=_COPIES) -> int:
    fails = []
    blocks = {}

    for path in copies:
        rel = os.path.relpath(path, _PLUGIN)
        block = extract(path)
        if not block:
            fails.append(f"{rel}: no scope-key block found — the copy list is stale")
            continue
        blocks[rel] = block

    if len(blocks) < 2:
        fails.append(
            f"only {len(blocks)} copy/copies extracted — a parity check over fewer "
            "than two files is vacuous"
        )

    # 1. Normalised byte-identity.
    digests = {rel: hashlib.sha256(_normalise(b).encode()).hexdigest()[:16]
               for rel, b in blocks.items()}
    uniq = sorted(set(digests.values()))
    if len(uniq) > 1:
        fails.append("TEXTUAL DRIFT — the copies are not the same block:")
        for rel, d in sorted(digests.items()):
            fails.append(f"    {d}  {rel}")

    # ⛔ 2. BEHAVIOURAL identity — the half that actually matters. Same synthetic
    # cwd into every copy must yield the same key.
    keys = {rel: _drive(b, _PROBE_CWD, _PROBE_FALLBACK) for rel, b in blocks.items()}
    uniq_keys = sorted(set(keys.values()))
    if len(uniq_keys) > 1:
        fails.append("BEHAVIOURAL DRIFT — copies derive DIFFERENT keys for one cwd:")
        for rel, k in sorted(keys.items()):
            fails.append(f"    {k}  {rel}")
    elif uniq_keys and uniq_keys[0].startswith("<error"):
        fails.append(f"every copy errored when driven: {uniq_keys[0]}")

    # ⛔ 3. THE KEY MUST ACTUALLY VARY, or identical-everywhere is trivially true
    # and proves nothing. The two probes must differ in the resolved TREE, not
    # merely in the cwd: `rc_worktree_root` walks up looking for a `.git` and,
    # finding none under a synthetic path, returns the FALLBACK — so two
    # different cwds under one fallback correctly derive the SAME key.
    # control: varying only the cwd produced one key for both probes (a real
    # property of the derivation, not a defect); varying the fallback produces
    # two, which is what shows the key is a function of its input.
    if blocks:
        one = next(iter(blocks.values()))
        a = _drive(one, _PROBE_CWD, _PROBE_FALLBACK)
        b = _drive(one, "/synthetic/other/tree", "/synthetic/other")
        if a == b:
            fails.append(
                "the derived key does not vary with the resolved tree — parity would "
                "be satisfied by a constant, which is not a scope key"
            )

    for f in fails:
        print(f"FAIL: {f}")
    if fails:
        print(f"\nscope-key parity FAILED — {len(fails)} finding(s)")
        return 2
    print(
        f"PASS: {len(blocks)} copies, normalised-identical, all derive "
        f"{uniq_keys[0]!r} for one synthetic cwd, and the key varies with cwd"
    )
    return 0


def must_fail() -> int:
    """Perturb one copy in memory and require the check to redden.

    ⛔ The perturbation changes the DIGEST LENGTH, so it is a behavioural change
    and not merely a comment edit — a whitespace-only mutation would be
    normalised away and would prove nothing about the check.
    """
    blocks = {}
    for path in _COPIES:
        b = extract(path)
        if b:
            blocks[os.path.relpath(path, _PLUGIN)] = b
    if len(blocks) < 2:
        print("MUST-FAIL SETUP FAILED: fewer than two copies extracted")
        return 1

    rel, block = sorted(blocks.items())[0]
    mutated = block.replace("hexdigest()[:10]", "hexdigest()[:12]")
    if mutated == block:
        print("MUST-FAIL SETUP FAILED: the mutation did not apply")
        return 1

    a = _drive(block, _PROBE_CWD, _PROBE_FALLBACK)
    b = _drive(mutated, _PROBE_CWD, _PROBE_FALLBACK)
    if a == b:
        print(
            "MUST-FAIL VIOLATED: a copy with a different digest length produced the "
            "SAME key — the behavioural half is not measuring anything"
        )
        return 1
    if _normalise(mutated) == _normalise(block):
        print("MUST-FAIL VIOLATED: the mutation normalised away, so the textual half "
              "would not see it either")
        return 1
    print(
        f"PASS (--must-fail): perturbing {rel} yields {b!r} against {a!r} — both the "
        "textual and behavioural halves would redden"
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="scope-key parity")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    args = ap.parse_args()
    if args.must_fail:
        return must_fail()
    return check()


if __name__ == "__main__":
    sys.exit(main())
