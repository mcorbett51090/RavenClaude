#!/usr/bin/env python3
"""Gate 264 -- runtime self-test front door (Phase 8, plan.md's
sessionstart-safeguards-multihost run: "rc hooks selftest: the on-demand
front door"). Drives plugins/ravenclaude-core/scripts/hooks-selftest.py
(and, transitively, its Tier A canary calls into _host-canary.sh) as a
subprocess, exercising A8.1-A8.7 from plan.md Phase 8's acceptance tests.

TIER A ONLY, same M10-honest-limit as check-host-canary.sh (Gate 207):
every subprocess this script drives runs `hooks-selftest.py --tier a`,
which forces Tier A everywhere -- no real host CLI is ever spawned. Tier D
(a real `claude -p`/`copilot -p` process) is NEVER exercised here; it is
owner-run on demand via `rc hooks selftest --tier d` or
hooks/tests/test-tier-d-canary.sh, and it is a hard rule of this repo's
own CI boundary that Tier D never runs in audit-gates.sh's CI-run surface.

Exit codes (this repo's premise-gate.py convention, reused rather than
reinvented -- 1 is COULD NOT RUN, never conflated with a clean 0):
  0  clean
  2  a finding (fail-closed)
  1  could not run at all (e.g. python3/hooks-selftest.py missing)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_SELFTEST = _REPO / "plugins" / "ravenclaude-core" / "scripts" / "hooks-selftest.py"
_RC = _REPO / "plugins" / "ravenclaude-core" / "bin" / "rc"
_COPILOT_ADAPTER = _REPO / "plugins" / "ravenclaude-core" / "hooks" / "copilot-hook-adapter.sh"


def _run(args: list, **kw) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, timeout=60, **kw)


def self_test(must_fail: bool = False) -> int:
    passed = 0
    failed = 0

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  \033[32m✓\033[0m {name}")
        else:
            failed += 1
            print(f"  \033[31m✗\033[0m {name}")

    if not _SELFTEST.exists():
        check("self-test setup: hooks-selftest.py found", False)
        return 1

    # A8.1 -- clean tree -> exit 0, one row per ledgered host + one per
    # unsupported host.
    #
    # HONEST SCOPING NOTE (this is the same CI boundary Gate 264 states
    # everywhere else): `--tier a` FORCES Tier A for every host, but the
    # anti-degradation check (Phase 7 A7.6, plan.md Sec 1.3's own
    # invariant) still compares the ACHIEVED tier against each host's
    # DECLARED tier -- so a host declared runtime_tier="D" (claude-code)
    # correctly, deliberately FAILs under a forced-Tier-A run (declared D,
    # achieved A is exactly the anti-degradation shape A7.6 exists to
    # catch). That is the mechanism working, not a defect to route around.
    # So A8.1 is split into two assertions that are each individually
    # true and CI-safe, rather than one that papers over the distinction:
    #   (a) every host WHOSE DECLARED TIER IS A cleanly exits 0
    #   (b) claude-code (declared D) correctly anti-degrades under a
    #       forced Tier-A run -- exit 2, not a silent pass
    p = _run([sys.executable, str(_SELFTEST), "--tier", "a", "--json"])
    try:
        data = json.loads(p.stdout)
        hosts = data.get("hosts", [])
    except json.JSONDecodeError:
        hosts = []
        check("A8.1: --json output is valid JSON", False)
    else:
        check("A8.1: --json output is valid JSON", True)
    host_names = {h.get("host") for h in hosts}
    check(
        "A8.1: at least one ledgered host (claude-code) and the unsupported "
        "host (grok) both appear as rows",
        "claude-code" in host_names and "grok" in host_names,
    )
    tier_a_hosts = [h.get("host") for h in hosts if h.get("declared_tier") == "A"]
    check(
        "A8.1: at least one Tier-A-declared host present to scope this "
        "assertion against",
        len(tier_a_hosts) > 0,
    )
    for h in tier_a_hosts:
        ph = _run([sys.executable, str(_SELFTEST), "--host", h, "--tier", "a"])
        check(f"A8.1: clean tree, host={h} (declared Tier A) exits 0", ph.returncode == 0)
    check(
        "A8.1 (anti-degradation, positive control): claude-code (declared "
        "Tier D) correctly FAILs (exit 2) under a forced Tier-A run -- "
        "proves the mechanism is live, not silently passing",
        p.returncode == 2,
    )

    # A8.2 -- --host cursor runs only cursor.
    p2 = _run([sys.executable, str(_SELFTEST), "--host", "cursor", "--tier", "a", "--json"])
    try:
        data2 = json.loads(p2.stdout)
        hosts2 = data2.get("hosts", [])
    except json.JSONDecodeError:
        hosts2 = []
    check(
        "A8.2: --host cursor runs only cursor (exactly 1 row, host=cursor)",
        len(hosts2) == 1 and hosts2[0].get("host") == "cursor",
    )

    # A8.3 -- --json emits parseable JSON with the documented row shape.
    required_keys = {"host", "declared_tier", "achieved_tier", "wired_set", "runtime", "verdict"}
    check(
        "A8.3: every row carries {host, declared_tier, achieved_tier, "
        "wired_set, runtime, verdict}",
        bool(hosts) and all(required_keys <= set(h.keys()) for h in hosts),
    )

    # A8.5 -- an unsupported host row is ALWAYS printed with its reason,
    # in HUMAN output (not just --json).
    p5 = _run([sys.executable, str(_SELFTEST), "--tier", "a"])
    check(
        "A8.5: grok's row prints its own reason in human-readable output "
        "(not just --json)",
        "grok" in p5.stdout and "reason:" in p5.stdout,
    )

    # A8.7 -- (closes G5 F2, HIGH) the copilot-cli row's chat annotation is
    # present in BOTH human and --json modes, sourced from host-support.json.
    copilot_annotation_json = any(
        h.get("host") == "copilot-cli" for h in hosts
    ) and "copilot_cli_chat_annotation" in data
    check(
        "A8.7: --json carries copilot_cli_chat_annotation when copilot-cli "
        "is a reported host",
        copilot_annotation_json,
    )
    check(
        "A8.7: human output force-prints 'chat: unverified' for copilot-cli",
        "chat: unverified" in p5.stdout,
    )

    # A8.6 -- `rc hooks` with no subcommand prints usage and exits 1.
    if _RC.exists():
        p6 = _run(["bash", str(_RC), "hooks"])
        check(
            "A8.6: `rc hooks` (no subcommand) exits 1 with a usage hint",
            p6.returncode == 1 and ("subcommand" in p6.stderr or "usage" in p6.stderr.lower()),
        )
    else:
        check("A8.6 setup: bin/rc found", False)

    # A8.4, MUST-FAIL -- a stubbed (misbehaving, not merely absent) adapter
    # -> exit 2, NEVER 1 (the fail-open trap this repo has recorded before).
    # Mutates the REAL copilot-hook-adapter.sh on disk, temporarily, then
    # restores it byte-for-byte -- verified restored before returning.
    if _COPILOT_ADAPTER.exists():
        original = _COPILOT_ADAPTER.read_text(encoding="utf-8")
        anchor = '  sessionstart)\n    out="$(CLAUDE_PROJECT_DIR="$cw" bash "$real" "$@" 2>/dev/null)"\n'
        if anchor not in original:
            check("A8.4 setup: mutation anchor found in copilot-hook-adapter.sh", False)
        else:
            mutant = original.replace(
                anchor,
                '  sessionstart)\n    out=""\n    true "$real" "$@" 2>/dev/null\n',
                1,
            )
            try:
                _COPILOT_ADAPTER.write_text(mutant, encoding="utf-8")
                p4 = _run(
                    [sys.executable, str(_SELFTEST), "--host", "copilot-cli", "--tier", "a"]
                )
                check(
                    "A8.4 MUST-FAIL: a misbehaving (stubbed) adapter makes "
                    "`rc hooks selftest` exit 2, never 1",
                    p4.returncode == 2,
                )
            finally:
                _COPILOT_ADAPTER.write_text(original, encoding="utf-8")
            restored = _COPILOT_ADAPTER.read_text(encoding="utf-8")
            check(
                "A8.4 cleanup verified: copilot-hook-adapter.sh restored "
                "byte-for-byte after the mutant",
                restored == original,
            )
    else:
        check("A8.4 setup: copilot-hook-adapter.sh found", False)

    print(f"\ncheck-hooks-selftest self-test: {passed} pass, {failed} fail")
    return 0 if failed == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Gate 264: runtime self-test front door (Tier A only, plan.md Phase 8/9)"
    )
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    args = ap.parse_args()
    if args.self_test or args.must_fail:
        return self_test(must_fail=args.must_fail)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
