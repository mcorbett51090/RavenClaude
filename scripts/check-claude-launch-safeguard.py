#!/usr/bin/env python3
"""check-claude-launch-safeguard.py -- Gate 282: the claude-launch-safeguard build
(P1 helper, P2 installer, P3 detector, P4 enrichment) is self-consistent and the
detector's discriminator has real teeth.

Background: anthropics/claude-code#92932 -- a session launched with cwd outside any
git repo (e.g. bare $HOME) can hang indefinitely (an unscoped rg scan hits macOS
TCC-denied paths). This repo ships a local, fail-open safeguard:
  - P1 plugins/ravenclaude-core/bin/claude-launch-guard (the decision helper)
  - P2 plugins/ravenclaude-core/scripts/install_launch_guard.py (rc-file installer)
  - P3 an additive evaluate_launch_hangs() in plugins/ravenclaude-core/scripts/stall_watch.py
  - P4 an additive debug-log enrichment on top of P3's finding

Four checks, all must-pass:

  A) P1's own --self-test passes (14 fixtures, incl. the fail-open matrix).
  B) P2's own --self-test passes (incl. the real-shell-sourcing test, the zsh
     menu driven on a pty, uninstall keeping later edits, and --help/unknown
     arguments never installing).
  D) Each repo-review 2026-10-19 fix in P2 has teeth: a mutant reverting it
     (snapshot restored unconditionally; an edited install-created rc deleted;
     --help falling through to install; the zsh-broken selection loop) makes
     P2's own --self-test FAIL. The zsh mutant is reported SKIPPED, never
     passed, when zsh is absent.
  C) The full test-stall-watch.py suite passes against the real source (must_pass),
     AND fails against a MUTANT that removes conjunct 3 (statusUpdatedAt <= startedAt
     + epsilon) from evaluate_launch_hangs() (must_fail) -- proving the healthy-idle
     negative control (gate_250c) actually depends on that conjunct, not just that
     the suite happens to be green.

Python 3.9, stdlib only.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAUNCH_GUARD = ROOT / "plugins" / "ravenclaude-core" / "bin" / "claude-launch-guard"
INSTALLER = ROOT / "plugins" / "ravenclaude-core" / "scripts" / "install_launch_guard.py"
STALL_WATCH = ROOT / "plugins" / "ravenclaude-core" / "scripts" / "stall_watch.py"
TEST_FILE = ROOT / "plugins" / "ravenclaude-core" / "hooks" / "tests" / "test-stall-watch.py"


def _run(cmd: list, timeout: int = 120) -> tuple:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return proc.returncode, (proc.stdout + proc.stderr)


def check_p1_self_test() -> tuple:
    rc, out = _run(["bash", str(LAUNCH_GUARD), "--self-test"])
    if rc != 0:
        return False, "claude-launch-guard --self-test FAILED:\n%s" % out[-2000:]
    return True, "claude-launch-guard --self-test passed (14 fixtures)"


def check_p2_self_test() -> tuple:
    rc, out = _run([sys.executable, str(INSTALLER), "--self-test"])
    if rc != 0:
        return False, "install_launch_guard.py --self-test FAILED:\n%s" % out[-2000:]
    return True, "install_launch_guard.py --self-test passed"


def _mutant_stall_watch_source() -> str:
    """Remove conjunct 3 (statusUpdatedAt <= startedAt + epsilon) from
    evaluate_launch_hangs(), the exact regression this check exists to catch."""
    src = STALL_WATCH.read_text(encoding="utf-8")
    needle = (
        "        if abs(status_updated_ms - started_ms) > LAUNCH_HANG_STATUS_EPSILON_MS:  # conjunct 3\n"
        "            continue\n"
    )
    if needle not in src:
        raise RuntimeError(
            "mutant anchor not found -- has evaluate_launch_hangs() been refactored?"
        )
    return src.replace(needle, "")


def check_teeth() -> tuple:
    rc_real, out_real = _run([sys.executable, str(TEST_FILE)])
    if rc_real != 0:
        return False, "real source: test suite FAILED (expected pass):\n%s" % out_real[-2000:]

    mutant_src = _mutant_stall_watch_source()
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        mirror_root = tmpdir / "plugins" / "ravenclaude-core"
        (mirror_root / "scripts").mkdir(parents=True)
        (mirror_root / "hooks" / "tests").mkdir(parents=True)
        (mirror_root / "scripts" / "stall_watch.py").write_text(mutant_src, encoding="utf-8")
        mutant_test = mirror_root / "hooks" / "tests" / "test-stall-watch.py"
        mutant_test.write_text(TEST_FILE.read_text(encoding="utf-8"), encoding="utf-8")

        rc_mutant, out_mutant = _run([sys.executable, str(mutant_test)])

    if rc_mutant == 0:
        return False, (
            "TEETH FAILURE: the mutant (conjunct 3 / statusUpdatedAt check removed) "
            "still passed the full test suite -- gate_250c's healthy-idle negative "
            "control does not actually depend on that conjunct."
        )
    return True, (
        "real suite passes (43 assertions); the conjunct-3-removed mutant is caught (exit %d)"
        % rc_mutant
    )


# Each mutant reverts ONE repo-review 2026-10-19 fix in install_launch_guard.py;
# P2's own --self-test must then FAIL, or that fix has no regression test.
# (label, [(anchor, replacement), ...], needs_zsh)
P2_MUTANTS = (
    (
        "corescripts-5: uninstall restores the snapshot unconditionally",
        [("        if _unchanged_since_install(current, pristine):\n", "        if True:\n")],
        False,
    ),
    (
        "corescripts-5: an rc created by install is deleted even after edits",
        [("        if not remove_block(current).strip():\n", "        if True:\n")],
        False,
    ),
    (
        "orch-2: --help and unknown arguments fall through to install",
        [
            (
                '        if a in ("-h", "--help"):\n            print(USAGE)\n            return 0\n',
                "",
            ),
            (
                '        print("install_launch_guard: unknown argument %r" % a, file=sys.stderr)\n'
                "        print(USAGE, file=sys.stderr)\n"
                "        return 2\n",
                "        i += 1\n",
            ),
        ],
        False,
    ),
    (
        "corescripts-4: the zsh-broken word-split selection loop is restored",
        [
            (
                '            _rc_target="$(printf \'%s\\n\' "$_rc_recs" | awk -v n="$_rc_choice" '
                "'NR == n - 4 { print; exit }')\"\n",
                "            _rc_j=0\n"
                "            for _rc_line in $_rc_recs; do\n"
                "              _rc_j=$((_rc_j + 1))\n"
                '              if [ "$_rc_choice" = "$((4 + _rc_j))" ]; then _rc_target="$_rc_line"; fi\n'
                "            done\n",
            )
        ],
        True,
    ),
)


def check_p2_mutants() -> tuple:
    """D) every P2 fix has teeth: a mutant reverting it fails P2's self-test."""
    import shutil as _sh

    src = INSTALLER.read_text(encoding="utf-8")
    notes = []
    ok = True
    for label, edits, needs_zsh in P2_MUTANTS:
        if needs_zsh and _sh.which("zsh") is None:
            notes.append("SKIPPED (zsh absent — not a pass): %s" % label)
            continue
        mut = src
        built = True
        for anchor, repl in edits:
            if mut.count(anchor) != 1:
                notes.append("ANCHOR MISSING (%dx): %s" % (mut.count(anchor), label))
                built = False
                ok = False
                break
            mut = mut.replace(anchor, repl, 1)
        if not built:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            mirror = Path(tmp)
            (mirror / "scripts").mkdir()
            (mirror / "bin").mkdir()
            (mirror / "scripts" / "install_launch_guard.py").write_text(mut, encoding="utf-8")
            _sh.copy2(LAUNCH_GUARD, mirror / "bin" / "claude-launch-guard")
            rc, _out = _run(
                [
                    sys.executable,
                    str(mirror / "scripts" / "install_launch_guard.py"),
                    "--self-test",
                ],
                timeout=300,
            )
        if rc == 0:
            ok = False
            notes.append("NOT CAUGHT: %s" % label)
        else:
            notes.append("caught: %s" % label)
    return ok, "\n".join(notes)


def gate(desc: str, ok: bool, detail: str) -> bool:
    mark = "OK " if ok else "FAIL"
    print("  [%s] %s" % (mark, desc))
    if not ok or "-v" in sys.argv:
        for line in detail.splitlines():
            print("      %s" % line)
    return ok


def self_test() -> int:
    print("check-claude-launch-safeguard.py --self-test")
    results = []
    ok, detail = check_p1_self_test()
    results.append(gate("A) claude-launch-guard --self-test", ok, detail))
    ok, detail = check_p2_self_test()
    results.append(gate("B) install_launch_guard.py --self-test", ok, detail))
    ok, detail = check_teeth()
    results.append(
        gate("C) stall_watch.py suite passes + conjunct-3-removed mutant is caught", ok, detail)
    )
    ok, detail = check_p2_mutants()
    results.append(
        gate(
            "D) each install_launch_guard.py fix has teeth (mutants fail P2 self-test)", ok, detail
        )
    )
    passed = all(results)
    print("\nGate 282: %s" % ("PASS" if passed else "FAIL"))
    return 0 if passed else 1


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    print("usage: check-claude-launch-safeguard.py --self-test", file=sys.stderr)
    sys.exit(2)
