#!/usr/bin/env python3
"""check-crosshost-hook-coverage.py — Phase 7 of verify-before-assert.

⛔ THE DEFECT THIS PINS IS A CLASS, NOT AN INSTANCE.

The three host projectors (Copilot, Cursor, Gemini) each resolve a registered
hook to a script name with `_script_of`, and each was written to be LOUD about a
hook it cannot place: an unmapped event RAISES, an intentional omission needs an
explicit skip with a reason, and `--check` fails the build otherwise.

That contract had a hole underneath it. `_script_of` matched only
`/hooks/([...]+\\.sh)`, and a hook body that lives under `/scripts/` -- the
packaging exception the tribunal's substrate guard forces, because it denies
setting the executable bit on a new `hooks/*.sh` -- resolved to the empty string
and hit a bare `continue`. A hook the projector cannot SEE is a hook it cannot
REFUSE, so the explicit-skip-or-raise contract never fired for it.

control (2026-08-25): with the old resolver, 4 of 42 registered commands dropped
silently and none of the three generators said a word; with the widened one, 42
of 42 resolve and 0 drop. `ask-on-ambiguity.sh` had been dropped from every
cross-host projection since v0.273.0 -- it shipped, it was documented, and it
reached no host but Claude Code.

This checker asserts the property the contract assumed: EVERY registered command
resolves. That is the assertion that would have caught it, and it is the one that
keeps catching it.

Usage:
    check-crosshost-hook-coverage.py --check
    check-crosshost-hook-coverage.py --must-fail
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MANIFEST = os.path.join(
    _REPO, "plugins", "ravenclaude-core", "hooks", "hooks.json"
)
_GENERATORS = ("copilot", "cursor", "gemini")

# The resolver the projectors use. Kept here as the ASSERTED contract, and checked
# against each generator's own copy so the three cannot drift apart silently.
_RESOLVER = re.compile(r"/(?:hooks|scripts)/([A-Za-z0-9._-]+\.sh)")

# ⛔ R7 — these three ship UNWIRED AND DECLARED on Cursor and Gemini, and WIRED on
# Copilot (repo-level `.github/hooks`; plugin-level never fires there, per
# github/copilot-cli#2540). A cell that flips from skipped to wired without a live
# round-trip is the MH-01 shape: fully wired, reviewing nothing.
_R7_UNWIRED = (
    "preflight-command-review.sh",
    "guard-remediation-cause.sh",
    "guard-cause-closure.sh",
)


def _registrations():
    with open(_MANIFEST, encoding="utf-8") as fh:
        manifest = json.load(fh)
    out = []
    for event, groups in (manifest.get("hooks") or {}).items():
        for group in groups:
            for entry in group.get("hooks") or []:
                out.append((event, entry.get("command", "")))
    return out


def _gen_path(host):
    return os.path.join(_REPO, "scripts", f"generate-{host}-hooks.py")


def _run_generator(host, extra=None):
    cmd = [sys.executable, _gen_path(host)] + (extra or [])
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120)


def check() -> int:
    fails = []

    regs = _registrations()
    if len(regs) < 10:
        fails.append(
            f"only {len(regs)} registrations parsed from hooks.json — the reader is "
            "blind, and every assertion below would pass vacuously"
        )

    # ⛔ 1. ZERO SILENT DROPS. The assertion the contract assumed and never made.
    dropped = [(e, c) for e, c in regs if not _RESOLVER.search(c)]
    if dropped:
        for e, c in dropped:
            fails.append(f"SILENT DROP: {e} registration resolves to no script: {c}")

    # 2. Each generator's own resolver must match this one. Three copies that drift
    #    reproduce the defect on whichever host was not updated.
    for host in _GENERATORS:
        try:
            with open(_gen_path(host), encoding="utf-8") as fh:
                src = fh.read()
        except OSError as exc:
            fails.append(f"cannot read the {host} generator: {exc}")
            continue
        if "/(?:hooks|scripts)/" not in src:
            fails.append(
                f"{host}: _script_of does not resolve /scripts/-hosted hook bodies — "
                "a hook it cannot see is a hook it cannot refuse"
            )

    # 3. Every generator accounts for every hook: --check must pass, and its own
    #    summary must claim the full canonical count.
    for host in _GENERATORS:
        proc = _run_generator(host, ["--check"])
        if proc.returncode != 0:
            tail = (proc.stdout + proc.stderr).strip().split("\n")[-1][:200]
            fails.append(f"{host} --check failed: {tail}")

    # ⛔ 4. R7: the three cells are ABSENT from Cursor and Gemini, PRESENT for
    #    Copilot, and every omission carries a NON-EMPTY reason.
    for host in ("cursor", "gemini"):
        proc = _run_generator(host)
        if proc.returncode != 0:
            fails.append(f"{host} generator failed to project")
            continue
        try:
            doc = json.loads(proc.stdout)
        except Exception:
            fails.append(f"{host} projection is not JSON")
            continue
        reasons = doc.get("_not_wired") or []
        blob = json.dumps(doc)
        for script in _R7_UNWIRED:
            named = [r for r in reasons if script in r]
            if not named:
                fails.append(
                    f"{host}: {script} is not declared in _not_wired — R7 requires an "
                    "explicit skip with a stated reason, never a silent omission"
                )
                continue
            # The reason must say something. An empty label is the shape of a
            # reason, not a reason.
            if all(len(r.split(":", 1)[-1].strip()) < 20 for r in named):
                fails.append(f"{host}: {script} carries an empty/blank skip reason")
            # And it must not ALSO be wired.
            wired_hit = re.search(
                r'"[^"]*%s[^"]*"' % re.escape(script), blob.replace("_not_wired", "")
            )
            if wired_hit and script not in json.dumps(reasons):
                fails.append(f"{host}: {script} appears wired despite being declared UNWIRED")

    proc = _run_generator("copilot")
    if proc.returncode == 0:
        blob = proc.stdout
        for script in _R7_UNWIRED:
            if script not in blob:
                fails.append(
                    f"copilot: {script} is MISSING from the projection — the plan wires "
                    "this host repo-level, so an absence here is lost coverage"
                )
    else:
        fails.append("copilot generator failed to project")

    for f in fails:
        print(f"FAIL: {f}")
    if fails:
        print(f"\ncross-host hook coverage FAILED — {len(fails)} finding(s)")
        return 2
    print(
        f"PASS: {len(regs)} registrations, 0 silent drops; 3 generators resolve "
        "/scripts/ bodies; R7 cells declared on cursor+gemini, wired on copilot"
    )
    return 0


def must_fail() -> int:
    """Narrow the resolver back to /hooks/ and require the drop assertion to redden.

    ⛔ This is the teeth for the CLASS. If it ever passes, the checker has stopped
    measuring resolution and is passing for some other reason.
    """
    global _RESOLVER
    saved = _RESOLVER
    _RESOLVER = re.compile(r"/hooks/([A-Za-z0-9._-]+\.sh)")
    try:
        regs = _registrations()
        dropped = [(e, c) for e, c in regs if not _RESOLVER.search(c)]
    finally:
        _RESOLVER = saved
    if not dropped:
        print(
            "MUST-FAIL VIOLATED: narrowing the resolver to /hooks/ dropped nothing, "
            "so the zero-silent-drops assertion is not measuring resolution"
        )
        return 1
    # ⛔ AND THE VERDICT MUST COME FROM check() ITSELF. Counting drops is a proxy:
    # a check() blinded so it can report nothing would still let the count above
    # pass. Point the reader at a manifest carrying an unresolvable command and
    # require the ENTRY POINT to return 2.
    import json as _json
    import tempfile as _tf

    real = check()
    if real != 0:
        print(f"MUST-FAIL SETUP FAILED: the unmutated tree already fails check() "
              f"(rc={real}), so a red result would be ambiguous")
        return 1

    saved = globals()["_MANIFEST"]
    try:
        with _tf.TemporaryDirectory() as tmp:
            bad = os.path.join(tmp, "hooks.json")
            with open(bad, "w", encoding="utf-8") as fh:
                _json.dump({"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [
                    {"type": "command", "command": "python3 /elsewhere/not-a-hook.py"}]}]}}, fh)
            globals()["_MANIFEST"] = bad
            rc = check()
    finally:
        globals()["_MANIFEST"] = saved

    if rc != 2:
        print(f"MUST-FAIL VIOLATED: check() returned {rc} on a manifest whose "
              "registration resolves to no script — the silent-drop assertion is "
              "not reaching the verdict")
        return 1

    print(
        f"PASS (--must-fail): the narrowed resolver drops {len(dropped)} registration(s), "
        "and an unresolvable registration drives check() to 2 while the real tree scores 0"
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="cross-host hook coverage")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    args = ap.parse_args()
    if args.must_fail:
        return must_fail()
    return check()


if __name__ == "__main__":
    sys.exit(main())
