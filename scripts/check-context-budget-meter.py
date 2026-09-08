#!/usr/bin/env python3
"""check-context-budget-meter.py — Gate 280: the context-usage meter is model-aware,
and a regression back to a hardcoded window is caught.

Before 2026-09-08, scripts/context-usage-meter.py assumed every Claude Code session
had a 200,000-token context window, regardless of which model was actually running.
Every current Claude model except the haiku tier is really 1,000,000 tokens (per the
claude-api skill's live table), so the meter — the single source of truth
conserve-tokens.py / handoff-nudge.py / the SessionStart banner all read — was wrong
by 5x for most sessions. See CLAUDE.md milestone "Context-usage meter becomes
model-aware".

Two checks, both must-pass + must-fail (teeth):

  A) knowledge/model-catalog.json's `context_windows` map covers every alias in
     `current`, each a positive integer. A missing/malformed entry here would make
     resolve_context_window_for_model() silently fall through to the heuristic
     for a GOVERNED model, which defeats the point of having a catalog at all.

  B) The full test-context-usage-meter.py suite passes against the real source
     (must_pass), AND fails against a MUTANT that reverts the model-aware
     resolution to the old hardcoded-200000 behavior (must_fail) — proving the
     test suite actually catches the regression this gate exists to prevent,
     not just that the tests currently happen to be green.

Python 3.9, stdlib only.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
METER = ROOT / "plugins" / "ravenclaude-core" / "scripts" / "context-usage-meter.py"
CATALOG = ROOT / "plugins" / "ravenclaude-core" / "knowledge" / "model-catalog.json"
TEST_FILE = ROOT / "plugins" / "ravenclaude-core" / "hooks" / "tests" / "test-context-usage-meter.py"


def _load_meter(path: Path):
    spec = importlib.util.spec_from_file_location("check_ctx_meter", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def check_catalog_context_windows() -> tuple[bool, str]:
    try:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return False, "cannot read/parse %s: %s" % (CATALOG, exc)
    current = data.get("current")
    windows = data.get("context_windows")
    if not isinstance(current, dict) or not isinstance(windows, dict):
        return False, "model-catalog.json missing `current` or `context_windows` object"
    missing = [alias for alias in current if alias not in windows]
    if missing:
        return False, "context_windows missing aliases: %s" % missing
    bad = [
        alias
        for alias, win in windows.items()
        if alias in current
        and (not isinstance(win, int) or isinstance(win, bool) or win <= 0)
    ]
    if bad:
        return False, "context_windows has non-positive-int entries for: %s" % bad
    return True, "context_windows covers every current alias with a positive int"


def _run_test_file(path: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(path), "-v"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    return proc.returncode, (proc.stdout + proc.stderr)


def _mutant_source() -> str:
    """Revert the model-aware resolution to the pre-fix hardcoded-200000 behavior,
    the exact regression this gate exists to catch."""
    src = METER.read_text(encoding="utf-8")
    needle = (
        "    if window is None and source == \"claude-code\":\n"
        "        # Rank 4 (model-aware) before rank 5 (hardcoded default) — see the\n"
        "        # module docstring's window-ranking table.\n"
        "        window, window_source = resolve_context_window_for_model(model_id)\n"
        "        if window is None:\n"
        "            window = DEFAULT_CLAUDE_WINDOW\n"
        "            window_source = \"default\"\n"
    )
    replacement = (
        "    if window is None and source == \"claude-code\":\n"
        "        window = DEFAULT_CLAUDE_WINDOW\n"
        "        window_source = \"default\"\n"
    )
    if needle not in src:
        raise RuntimeError("mutant anchor not found — has measure() been refactored?")
    return src.replace(needle, replacement)


def check_teeth() -> tuple[bool, str]:
    rc_real, out_real = _run_test_file(TEST_FILE)
    if rc_real != 0:
        return False, "real source: test suite FAILED (expected pass):\n%s" % out_real[-2000:]

    mutant_src = _mutant_source()
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        # Mirror the real plugin's directory shape so the test file's HERE-relative
        # import (parents[2] / "scripts" / "context-usage-meter.py") resolves.
        mirror_root = tmpdir / "plugins" / "ravenclaude-core"
        (mirror_root / "scripts").mkdir(parents=True)
        (mirror_root / "hooks" / "tests").mkdir(parents=True)
        (mirror_root / "knowledge").mkdir(parents=True)
        (mirror_root / "scripts" / "context-usage-meter.py").write_text(mutant_src, encoding="utf-8")
        (mirror_root / "knowledge" / "model-catalog.json").write_text(
            CATALOG.read_text(encoding="utf-8"), encoding="utf-8"
        )
        mutant_test = mirror_root / "hooks" / "tests" / "test-context-usage-meter.py"
        mutant_test.write_text(TEST_FILE.read_text(encoding="utf-8"), encoding="utf-8")

        rc_mutant, out_mutant = _run_test_file(mutant_test)

    if rc_mutant == 0:
        return False, (
            "TEETH FAILURE: the mutant (hardcoded-200000 window, no model resolution) "
            "still passed the full test suite — the tests do not actually catch this "
            "regression."
        )
    return True, "real suite passes; the hardcoded-window mutant is caught (exit %d)" % rc_mutant


def gate(desc: str, ok: bool, detail: str) -> bool:
    mark = "✓" if ok else "✗"
    print("  %s %s" % (mark, desc))
    if not ok or "-v" in sys.argv:
        for line in detail.splitlines():
            print("      %s" % line)
    return ok


def self_test() -> int:
    print("check-context-budget-meter.py --self-test")
    results = []
    ok, detail = check_catalog_context_windows()
    results.append(gate("A) model-catalog.json context_windows completeness", ok, detail))
    ok, detail = check_teeth()
    results.append(gate("B) real suite passes + hardcoded-window mutant is caught", ok, detail))
    passed = all(results)
    print("\nGate 280: %s" % ("PASS" if passed else "FAIL"))
    return 0 if passed else 1


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    print("usage: check-context-budget-meter.py --self-test", file=sys.stderr)
    sys.exit(2)
