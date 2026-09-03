#!/usr/bin/env python3
"""hooks-selftest.py -- `rc hooks selftest`, Phase 8 of the
sessionstart-safeguards-multihost FORGE plan: the on-demand front door
(plan.md Sec 1.4).

One command, per-host pass/fail, with the runtime TIER printed on every row so
a green run can never be silently read as more coverage than it actually has
(the anti-silent-degradation clause, plan.md Sec 1.3/Sec 4 -- "PASS (tier A)"
and "PASS (tier D)" are different claims and must never collapse into one
summary).

This is a MARKETPLACE-DEV tool, not a shipped-plugin runtime component, and
that is deliberate, not an oversight: it audits THIS repo's own
plugins/ravenclaude-core/hooks/hooks.json wiring across the declared hosts, by
importing the ledger (`_WIRED_SET_LEDGER` / `_UNSUPPORTED_HOSTS` /
`check_c_wired_set`'s extractors / `_copilot_cli_chat_annotation`) straight out
of the marketplace-root `scripts/check-sessionstart-matcher-regression.py`
(Phase 1-5's Gate 259 engine) -- the same "lives at the MARKETPLACE root, not
the plugin's" pattern `rc artifacts` already uses for `rc-artifacts.py` (see
that case in plugins/ravenclaude-core/bin/rc). A plugin CONSUMER who has no
such file will see a clear "cannot find ..." error, not a crash -- exactly
`rc artifacts`'s own failure shape.

It sources plugins/ravenclaude-core/hooks/_host-canary.sh's Tier A
(`_rc_host_sessionstart_canary`) and Tier D (`_rc_host_tier_d_canary`) canary
functions, plus `_rc_canary_declared_tier` and `_rc_canary_anti_degradation`,
rather than reimplementing any canary logic -- every runtime assertion in this
file is a subprocess call into that shell file, read only for its documented
exit-code contract.

Two distinct notions of "declared tier" are deliberately kept apart, because
they answer different questions and collapsing them was the exact failure
plan.md's anti-degradation clause exists to prevent:

  - `_rc_canary_declared_tier` (bash, Phase 6/7, unchanged by this phase) is
    the GENERIC ASPIRATIONAL classification from plan.md Sec 1.3's per-host
    table ("Copilot-CLI -> D-if-present, else A").
  - `_WIRED_SET_LEDGER[host]["runtime_tier"]` (Python, this phase's own
    addition to check-sessionstart-matcher-regression.py) is the SETTLED,
    REPORTABLE tier -- for copilot-cli specifically, Phase 7 measured (twice,
    with a positive control on the spawn mechanism) that SessionStart does
    NOT fire under `copilot -p`, so the settled value is "A" even though the
    aspirational classification still says "D" for the un-measured general
    case. When the two disagree, this tool prints the settled tier in the
    "tier" column (never silently upgraded to the aspirational one) plus an
    explicit "D unverified" caveat on the verdict -- see `_evaluate_host`.

Exit codes (never conflated -- this repo's own recorded fail-open trap; see
AGENTS.md's "the cause selects the fix" + this repo's Gate-184/Gate-259
must-fail-half discipline):
  0  every selected host PASSED its declared tier, or SKIPped with a stated
     reason (grok, an absent host CLI, a harness error -- never silent)
  2  at least one selected host FAILED its declared tier -- a finding
  1  could not run at all (missing _host-canary.sh/_portable.sh, the ledger
     script itself missing/unimportable, or an unknown --host) -- NEVER used
     for a finding, so a CI consumer can always tell "ran and found a
     problem" apart from "never ran"
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType

_PLUGIN_ROOT = Path(__file__).resolve().parent.parent  # plugins/ravenclaude-core
_HOOKS_DIR = _PLUGIN_ROOT / "hooks"
_CANARY_SH = _HOOKS_DIR / "_host-canary.sh"
_PORTABLE_SH = _HOOKS_DIR / "_portable.sh"
_MARKET_ROOT = _PLUGIN_ROOT.parent.parent  # the marketplace repo root (RavenClaude/)
_REGRESSION_PY = _MARKET_ROOT / "scripts" / "check-sessionstart-matcher-regression.py"

# _host-canary.sh's own `case "$host" in ...)` dispatch (adapter lookup,
# host-support.json lookup, payload shaping) still keys on the bare "copilot"
# token -- it predates, and was never re-keyed for, plan.md Sec 1.1's mandated
# ledger rename to "copilot-cli" (G4b correction #3 / G5 Finding F2). The
# regression module's own `_HOST_ALIASES` performs the OPPOSITE direction
# (raw filesystem/host-support.json "copilot" -> ledger "copilot-cli"); this
# is the mirror, applied only at the boundary where THIS tool calls into the
# shell canary functions -- every reported row, JSON field and table column
# keeps the mandated "copilot-cli" spelling throughout.
_CANARY_HOST_ALIAS = {"copilot-cli": "copilot"}


def _canary_host(host: str) -> str:
    return _CANARY_HOST_ALIAS.get(host, host)


def _load_regression_module() -> ModuleType:
    if not _REGRESSION_PY.exists():
        raise FileNotFoundError(str(_REGRESSION_PY))
    spec = importlib.util.spec_from_file_location(
        "check_sessionstart_matcher_regression", _REGRESSION_PY
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"could not build an import spec for {_REGRESSION_PY}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_canary_shell(body: str) -> subprocess.CompletedProcess:
    """Run BODY after sourcing _portable.sh + _host-canary.sh -- the one place
    this file touches a shell, so every canary invocation goes through the
    same sourcing + error handling.
    """
    script = f'set -uo pipefail\n. "{_PORTABLE_SH}"\n. "{_CANARY_SH}"\n{body}\n'
    return subprocess.run(["bash", "-c", script], capture_output=True, text=True)


def _canary_call(func: str, host: str, project: str) -> int:
    """Call a _host-canary.sh function by name and return ONLY its exit code
    -- every function this tool calls has a documented return-code contract
    (see _host-canary.sh's own comments above each), so exit code is all a
    caller needs; stdout/stderr are the human-facing ok/warn/note lines that
    function already prints for a human running it directly. HOST is always
    the LEDGER spelling ("copilot-cli"); translated to the shell layer's own
    "copilot" via `_canary_host` before it ever reaches _host-canary.sh.
    """
    proc = _run_canary_shell(f'{func} "{_canary_host(host)}" "{project}" >/dev/null 2>&1')
    return proc.returncode


def _aspirational_tier(host: str) -> str:
    proc = _run_canary_shell(f'_rc_canary_declared_tier "{_canary_host(host)}"')
    out = (proc.stdout or "").strip()
    return out or "A"


def _tier_d_cli_available(host: str) -> bool:
    proc = _run_canary_shell(f'_rc_canary_tier_d_cli_for "{_canary_host(host)}" >/dev/null 2>&1')
    return proc.returncode == 0


def _anti_degradation(declared: str, achieved: str) -> str:
    proc = _run_canary_shell(f'_rc_canary_anti_degradation "{declared}" "{achieved}"')
    return (proc.stdout or "").strip() or "FAIL"


def _wired_set_check(mod: ModuleType, host: str) -> tuple[bool, list]:
    """Reuses the module's own `_EXTRACTORS`/`_WIRED_SET_LEDGER["required"]`
    -- the same primitives `check_c_wired_set` iterates over -- scoped to ONE
    host instead of the whole ledger, so `--host <h>` never has to touch
    another host's extractor.
    """
    entry = mod._WIRED_SET_LEDGER[host]
    required = entry["required"]
    extractor = mod._EXTRACTORS.get(host)
    if extractor is None:
        return False, ["no extractor registered for this host"]
    try:
        actual = extractor(_MARKET_ROOT)
    except NotImplementedError as exc:
        return False, [f"extractor not implemented: {exc}"]
    wired_names = set(actual)
    if required and not wired_names:
        return False, ["EMPTY-EXTRACTION -- extractor returned zero wired hooks"]
    missing = sorted(required - wired_names)
    if missing:
        return False, missing
    return True, []


def _evaluate_host(mod: ModuleType, host: str, tier_flag: str, project: str) -> dict:
    entry = mod._WIRED_SET_LEDGER[host]
    declared_tier = entry.get("runtime_tier", "A")
    aspirational = _aspirational_tier(host)
    wired_ok, missing = _wired_set_check(mod, host)

    if tier_flag == "a":
        attempt = "A"
    elif tier_flag == "d":
        attempt = "D" if _tier_d_cli_available(host) else "A"
    else:  # auto -- attempt this host's own SETTLED declared tier, never more
        attempt = "D" if declared_tier == "D" else "A"

    achieved: str | None = None
    runtime_label = "n/a"
    note = ""
    skip_reason: str | None = None

    if attempt == "D":
        rc = _canary_call("_rc_host_tier_d_canary", host, project)
        if rc == 0:
            achieved = "D"
            runtime_label = "fired"
        elif rc == 3:
            # HARNESS error -- explicitly NOT a dispatch verdict per
            # _host-canary.sh's own contract; must not be conflated with rc=2.
            runtime_label = "harness-error"
            skip_reason = (
                "Tier D harness error (scratch provisioning/config write "
                "failed) -- not a dispatch verdict, see _host-canary.sh"
            )
        else:
            # rc == 1 (unavailable -- CLI absent or RC_SELFTEST_TIER=a) or
            # rc == 2 (candidate regression -- spawn ran, marker did not
            # fire). Either way, fall back to Tier A so a caller gets an
            # honest achieved-tier reading instead of nothing at all.
            ta_rc = _canary_call("_rc_host_sessionstart_canary", host, project)
            if ta_rc == 0:
                achieved = "A"
                runtime_label = "fired+ctx"
            else:
                runtime_label = "did-not-fire"
            note = (
                "tier D unavailable this run (CLI absent or RC_SELFTEST_TIER=a)"
                if rc == 1
                else "candidate regression: tier D spawn ran but the marker did not fire"
            )
    else:  # attempt == "A"
        rc = _canary_call("_rc_host_sessionstart_canary", host, project)
        if rc == 0:
            achieved = "A"
            runtime_label = "fired+ctx"
        elif rc == 1:
            runtime_label = "skip"
            skip_reason = (
                "host has no verified hook path on this machine, or its "
                "adapter file is not present -- not a files-exist check "
                "(see _host-canary.sh's own M10 honest-limit note)"
            )
        elif rc == 2:
            runtime_label = "delivery-failure"
        else:  # rc == 3
            runtime_label = "invocation-failure"

    if skip_reason is not None:
        return {
            "host": host,
            "declared_tier": declared_tier,
            "achieved_tier": None,
            "wired_set": "ok" if wired_ok else "fail",
            "runtime": runtime_label,
            "verdict": f"SKIP -- {skip_reason}",
            "verdict_kind": "skip",
            "note": note,
        }

    degradation = _anti_degradation(declared_tier, achieved or "none")
    runtime_broken = achieved is None
    passed = wired_ok and not runtime_broken and degradation == "PASS"

    if passed:
        if aspirational == "D" and declared_tier != "D":
            verdict = (
                f"PASS (tier {declared_tier} -- D unverified, see "
                f"check-sessionstart-matcher-regression.py's {host} ledger entry)"
            )
        else:
            verdict = "PASS"
        kind = "pass"
    else:
        reasons = []
        if not wired_ok:
            reasons.append(f"wired-set missing: {missing}")
        if runtime_broken:
            reasons.append(f"runtime: {runtime_label}")
        if degradation != "PASS":
            reasons.append(
                f"anti-degradation: declared {declared_tier}, achieved {achieved or 'none'}"
            )
        if note:
            reasons.append(note)
        verdict = "FAIL (" + "; ".join(reasons) + ")"
        kind = "fail"

    return {
        "host": host,
        "declared_tier": declared_tier,
        "achieved_tier": achieved,
        "wired_set": "ok" if wired_ok else "fail",
        "runtime": runtime_label,
        "verdict": verdict,
        "verdict_kind": kind,
        "note": note,
    }


def _evaluate_unsupported(mod: ModuleType, host: str) -> dict:
    entry = mod._UNSUPPORTED_HOSTS[host]
    reason = entry.get("reason", "") or ""
    return {
        "host": host,
        "declared_tier": "S",
        "achieved_tier": None,
        "wired_set": "n/a",
        "runtime": "n/a",
        "verdict": "SKIP -- no hook adapter (see _UNSUPPORTED_HOSTS)",
        "verdict_kind": "skip",
        "note": "",
        "reason": reason,
    }


def _print_table(rows: list, copilot_annotation: str | None) -> None:
    print(f"{'host':<12} {'tier':<5} {'wired-set':<10} {'runtime':<12} verdict")
    for row in rows:
        print(
            f"{row['host']:<12} {row['declared_tier']:<5} {row['wired_set']:<10} "
            f"{row['runtime']:<12} {row['verdict']}"
        )
        if row["host"] == "copilot-cli" and copilot_annotation:
            print(f"{'':<12} {'':<5} {'':<10} {'':<12} {copilot_annotation}")
        if row.get("reason"):
            print(f"    reason: {row['reason']}")


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="rc hooks selftest",
        description=(
            "Per-host SessionStart wiring + runtime-tier self-test "
            "(sessionstart-safeguards-multihost Phase 8)."
        ),
    )
    ap.add_argument("--host", default=None, help="run only this one host")
    ap.add_argument(
        "--tier",
        choices=["a", "d", "auto"],
        default="auto",
        help=(
            "a: force Tier A everywhere (never spawns a real host CLI). "
            "d: force-attempt Tier D wherever a Tier-D CLI mapping exists "
            "(claude-code, copilot-cli), Tier A elsewhere. "
            "auto (default): attempt each host's own SETTLED declared tier "
            "-- Tier D only where the ledger's runtime_tier says D."
        ),
    )
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON instead of a table")
    args = ap.parse_args()

    if not _CANARY_SH.exists() or not _PORTABLE_SH.exists():
        print(
            f"rc hooks selftest: cannot find _host-canary.sh/_portable.sh under {_HOOKS_DIR}",
            file=sys.stderr,
        )
        return 1

    try:
        mod = _load_regression_module()
    except Exception as exc:  # noqa: BLE001 -- any load failure is "could not run"
        print(
            f"rc hooks selftest: could not load the SessionStart ledger "
            f"({_REGRESSION_PY}): {exc}",
            file=sys.stderr,
        )
        return 1

    ledgered_hosts = sorted(mod._WIRED_SET_LEDGER)
    unsupported_hosts = sorted(mod._UNSUPPORTED_HOSTS)
    all_hosts = ledgered_hosts + unsupported_hosts

    if args.host is not None:
        if args.host not in all_hosts:
            print(
                f"rc hooks selftest: unknown --host '{args.host}' "
                f"(known: {', '.join(all_hosts)})",
                file=sys.stderr,
            )
            return 1
        selected = [args.host]
    else:
        selected = all_hosts

    project = str(_MARKET_ROOT)
    rows: list = []
    exit_code = 0
    for host in selected:
        if host in mod._WIRED_SET_LEDGER:
            row = _evaluate_host(mod, host, args.tier, project)
        else:
            row = _evaluate_unsupported(mod, host)
        rows.append(row)
        if row["verdict_kind"] == "fail":
            exit_code = 2

    # G5 Finding F2 (HIGH, mandatory): force-printed on EVERY invocation that
    # reports on copilot-cli, in BOTH human and --json output, regardless of
    # pass/fail -- sourced verbatim from host-support.json via the module's
    # own function (never hardcoded, never reimplemented).
    copilot_annotation = None
    if any(r["host"] == "copilot-cli" for r in rows):
        try:
            copilot_annotation = mod._copilot_cli_chat_annotation()
        except Exception as exc:  # noqa: BLE001 -- a stale-claim guard firing
            copilot_annotation = (
                f"chat: UNVERIFIABLE -- could not read host-support.json's "
                f"copilot chat note ({exc})"
            )
            if exit_code == 0:
                exit_code = 1

    if args.json:
        payload = {"hosts": rows}
        if copilot_annotation is not None:
            payload["copilot_cli_chat_annotation"] = copilot_annotation
        print(json.dumps(payload, indent=2))
    else:
        _print_table(rows, copilot_annotation)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
