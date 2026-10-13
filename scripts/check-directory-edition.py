#!/usr/bin/env python3
"""check-directory-edition.py - Gate 301: the Anthropic-Directory edition of ravenclaude-core.

Builds the edition from the source plugin and refuses it unless every claim in its README and PRIVACY.md
holds. The point of the edition is that a stranger can install it and be told, truthfully, that every hook
is off until they opt in; this gate is what keeps that sentence true as the source plugin changes weekly.

REAL CHECKS (on the freshly built edition)
  1  the builder's and the audit harness's own self-tests pass (their positive controls)
  2  deterministic build; limits (files, per-file bytes, symlinks, non-image binaries); structure (no
     `experimental`, no bin/ monitors/ CLAUDE.md dashboard.html, every hook wrapped in the posture gate
     except the declared setup prompt); README lists exactly the shipped hooks; every network primitive
     in an executable is classified; no secret-shaped string; the committed file list is fresh
  3  every shipped hook, run from the built hooks.json, is INERT with no posture file and SAFE under a
     hostile posture file (scripts/directory-edition-hook-audit.py), writes only under .ravenclaude/, and
     starts only programs on the manifest's allow-list
  4  `claude plugin validate --strict` passes (when the claude CLI is present; otherwise reported as NOT RUN,
     which is not a pass)

MUST-FAIL HALVES (a check that cannot fail proves nothing)
  M1  an always-on hook wrapped in the REAL posture gate is inert; the same hook behind a gate with the
      posture test removed is not - so the property comes from the gate and the harness can see it go
  M2  real hooks that ARE unsafe (guard-destructive.sh always on; dod-gate.sh runs a command read from the
      posture file) are classified unsafe by the same audit, so its payloads and seeds reach real triggers

HONEST LIMIT: the syscall lane (network and exec observation) needs `strace`. Without it the audit still
uses tripwires (curl/wget/nc/ssh/gh/claude stubs and a python socket hook) and says so; set
RC_EDITION_REQUIRE_STRACE=1 (the release check) to make its absence a failure.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent


def _load(name: str, fname: str):
    spec = importlib.util.spec_from_file_location(name, HERE / fname)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


build = _load("rc_build_edition", "build-directory-edition.py")
audit = _load("rc_audit_edition", "directory-edition-hook-audit.py")

PASS = FAIL = 0


def ok(label: str) -> None:
    global PASS
    PASS += 1
    print(f"  \033[32m✓\033[0m {label}")


def bad(label: str, why: str = "") -> None:
    global FAIL
    FAIL += 1
    print(f"  \033[31m✗\033[0m {label}" + (f"\n      {why}" if why else ""))


def check(label: str, cond: bool, why: str = "") -> None:
    ok(label) if cond else bad(label, why)


def run_selftest(script: str) -> tuple[bool, str]:
    cp = subprocess.run(
        [sys.executable, str(HERE / script), "--self-test"],
        capture_output=True,
        text=True,
        timeout=900,
    )
    last = (cp.stdout.strip().splitlines() or [""])[-1]
    m = re.search(r"(\d+) passed, (\d+) failed", last)
    return cp.returncode == 0 and bool(m) and m.group(2) == "0", last


def _wrap(cmd: str) -> str:
    return build.GATE_PREFIX + cmd


def main() -> int:
    manifest = build.load_manifest(build.DEFAULT_MANIFEST)
    pa = manifest.get("hook_audit", {})
    write_dirs = tuple(pa.get("write_dirs", ["ravenclaude"]))
    allowed_out = tuple(pa.get("allowed_output", []))
    allowed_execs = set(pa.get("allowed_execs", []))
    require_strace = os.environ.get("RC_EDITION_REQUIRE_STRACE") == "1"
    quick = "--quick" in sys.argv

    print("── 1. the tools' own positive controls ──")
    for script in ("build-directory-edition.py", "directory-edition-hook-audit.py"):
        passed, last = run_selftest(script)
        check(f"{script} --self-test: {last}", passed)

    print("── 2. the built edition ──")
    try:
        problems, paths, _ = build.check_problems(manifest, REPO)
    except build.BuildError as e:
        bad("build", str(e))
        problems, paths = [], []
    for p in problems:
        bad(p)
    if not problems and paths:
        ok(
            f"{len(paths)} files: deterministic, within limits, structure + README parity + network + secrets + file list all clean"
        )

    if quick:
        print(
            f"directory-edition: {PASS} passed, {FAIL} failed (--quick: hook audit and must-fail halves skipped)"
        )
        return 1 if FAIL else 0

    with tempfile.TemporaryDirectory(prefix="rc-edition-gate-") as td:
        dist = Path(td) / "dist"
        try:
            build.full_build(manifest, dist, REPO)
        except build.BuildError as e:
            bad("build for the hook audit", str(e))
            print(f"directory-edition: {PASS} passed, {FAIL} failed")
            return 1

        print("── 3. every shipped hook, measured ──")
        res = audit.measure(dist, allowed_output=allowed_out, write_dirs=write_dirs)
        if not res["strace"]:
            msg = "strace absent: network and exec observed by tripwires only (set RC_EDITION_REQUIRE_STRACE=1 to require it)"
            if require_strace:
                bad(msg)
            else:
                print(f"  NOT RUN  syscall lane - {msg}")
        shipped = {h["id"] for h in manifest["components"]["hooks"]}
        check(
            "the audit measured exactly the manifest's hooks",
            set(res["hooks"]) == shipped,
            f"measured {sorted(res['hooks'])} vs manifest {sorted(shipped)}",
        )
        shipped_scripts = {Path(p).name for p in paths if p.endswith((".sh", ".py"))}
        for hid, e in sorted(res["hooks"].items()):
            check(
                f"{hid}: inert with no posture file ({e['runs']} payloads)",
                e["inert"],
                "; ".join(e["inert_reasons"][:2]),
            )
            check(
                f"{hid}: safe under a hostile posture file",
                e["hostile_safe"],
                "; ".join(e["hostile_reasons"][:2]),
            )
            if res["strace"]:
                extra = sorted(set(e["hostile_execs"]) - allowed_execs - shipped_scripts)
                check(
                    f"{hid}: starts only allow-listed programs",
                    not extra,
                    f"unexpected programs: {extra}",
                )

        print("── 4. claude plugin validate --strict ──")
        for target, label in (
            (dist, "marketplace manifest"),
            (dist / ".claude-plugin" / "plugin.json", "plugin manifest"),
        ):
            status, out = _validate(target)
            if status == "unavailable":
                print(f"  NOT RUN  {label}: {out} (not a pass)")
            else:
                check(f"{label}: validate --strict", status == "pass", out)

        print("── must-fail halves ──")
        must_fail_gate_shim(dist)
        must_fail_real_hooks()

    print(f"directory-edition: {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


def _validate(target: Path) -> tuple[str, str]:
    exe = shutil.which("claude")
    if not exe:
        return "unavailable", "claude CLI not on PATH"
    cp = subprocess.run(
        [exe, "plugin", "validate", "--strict", str(target)],
        capture_output=True,
        text=True,
        timeout=180,
    )
    return ("pass" if cp.returncode == 0 else "fail"), (cp.stdout + cp.stderr).strip()[-300:]


def _measure_one(plugin: Path, hooks_json: Path | None, only: str, **kw) -> dict:
    return audit.measure(plugin, hooks_json, only={only}, **kw)["hooks"].get(only, {})


def must_fail_gate_shim(dist: Path) -> None:
    """M1: the property comes from the gate. A hook that exits 2 on every call is the stand-in for any
    always-on guard; behind the real shim it is inert, behind a shim without the posture test it is not."""
    with tempfile.TemporaryDirectory(prefix="rc-m1-") as td:
        plug = Path(td) / "p"
        shutil.copytree(dist, plug)
        hook = plug / "hooks" / "zz-always-on.sh"
        hook.write_text('#!/usr/bin/env bash\necho "always on" >&2\nexit 2\n')
        hook.chmod(0o755)
        hj = plug / "hooks" / "hooks.json"
        data = json.loads(hj.read_text())
        data["hooks"].setdefault("UserPromptSubmit", []).append(
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": _wrap('"${CLAUDE_PLUGIN_ROOT}/hooks/zz-always-on.sh"'),
                    }
                ]
            }
        )
        hj.write_text(json.dumps(data))
        real = _measure_one(plug, hj, "zz-always-on.sh")
        check(
            "M1 an always-on hook behind the REAL posture gate is inert",
            bool(real.get("inert")),
            "; ".join(real.get("inert_reasons", [])),
        )
        (plug / "hooks" / "posture-gate.sh").write_text('#!/usr/bin/env bash\nexec "$@"\n')
        mutant = _measure_one(plug, hj, "zz-always-on.sh")
        check(
            "M1 the same hook behind a gate with the posture test removed is NOT inert (the harness can see it)",
            mutant.get("inert") is False,
        )


def must_fail_real_hooks() -> None:
    """M2: real hooks that are unsafe must be classified unsafe, from the SOURCE plugin where they exist."""
    src = REPO / "plugins" / "ravenclaude-core"
    for hid, lane in (("guard-destructive.sh", "inert"), ("dod-gate.sh", "hostile")):
        e = _measure_one(src, None, hid, write_dirs=("ravenclaude",))
        if not e:
            bad(f"M2 {hid} was not found in the source hooks.json (the control has gone stale)")
        elif lane == "inert":
            check(
                "M2 guard-destructive.sh (always on, denies a destructive command) is classified NOT inert",
                e["inert"] is False,
                "the audit's payloads no longer reach this guard",
            )
        else:
            check(
                "M2 dod-gate.sh (runs a command read from the posture file) is classified NOT hostile-safe",
                e["hostile_safe"] is False,
                "the hostile posture/seed no longer reaches the command it runs",
            )


if __name__ == "__main__":
    sys.exit(main())
