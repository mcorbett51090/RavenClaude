#!/usr/bin/env python3
"""Gate 210 — generated shipping-state / gate-state prose is not a typed lie.

MH-40: a dashboard JS comment claimed the Settings autostart control
did not ship, after `_render_dashboard_autostart()` landed. An audit
lens read the stale sentence and reported closed work as open.
CLAUDE.md was corrected; the generator kept emitting the lie into
dashboard.html and index.html.

This gate is a denylist over the generator and the two shipped HTML
surfaces. It does not wrap the generator and it does not re-count the
DOM (Gate 132 already owns the numbers).

Exit 0 = clean. Exit 2 = a finding or a failed plant.
Exit 1 is never used for a finding.

Usage:
    python3 scripts/check-generated-gate-state.py
    python3 scripts/check-generated-gate-state.py --self-test
    python3 scripts/check-generated-gate-state.py --must-fail
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

# Assembled so this file is not itself a finding.
_PHRASE = "No DOM " + "control ships"

SURFACES = (
    Path("scripts/generate-dashboards.py"),
    Path("plugins/ravenclaude-core/dashboard.html"),
    Path("index.html"),
)


def scan(paths: tuple[Path, ...] = SURFACES) -> list[str]:
    hits = []
    for path in paths:
        if not path.is_file():
            hits.append(f"missing {path}")
            continue
        text = path.read_text(encoding="utf-8")
        if _PHRASE in text:
            hits.append(f"{path}: stale shipping-state phrase still present")
    return hits


def _self_test() -> int:
    failures = 0
    src = Path(__file__).read_text(encoding="utf-8")
    if _PHRASE in src:
        print("  [FAIL] checker source contains the contiguous forbidden phrase")
        failures += 1
    else:
        print("  [ok] checker source has no contiguous forbidden phrase")

    live = scan()
    if live:
        print("  [FAIL] live tree:")
        for h in live:
            print(f"    - {h}")
        failures += 1
    else:
        print("  [ok] generator + dashboard.html + index.html are clean")

    print(f"\nself-test: {'FAIL' if failures else 'PASS'}")
    return 2 if failures else 0


def _must_fail() -> int:
    missing = [str(p) for p in SURFACES if not p.is_file()]
    if missing:
        print("ERROR: " + "; ".join(missing), file=sys.stderr)
        return 2
    tmp = Path(tempfile.mkdtemp(prefix="g210-"))
    try:
        plant = tmp / "dashboard.html"
        shutil.copy2(SURFACES[1], plant)
        plant.write_text(
            plant.read_text(encoding="utf-8") + "\n/* " + _PHRASE + " */\n",
            encoding="utf-8",
        )
        hits = scan((plant,))
        live = scan()
        if hits and not live:
            print("  [ok] planted stale phrase is caught")
            print("  [ok] unmutated live tree is clean (the red is the plant)")
            print("\nmust-fail: plant caught")
            return 2
        print(f"  [FAIL] plant hits={hits!r} live={live!r}", file=sys.stderr)
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if args.must_fail:
        return _must_fail()
    findings = scan()
    if findings:
        print(f"{len(findings)} generated-gate-state finding(s):", file=sys.stderr)
        for f in findings:
            print(f"  {f}", file=sys.stderr)
        return 2
    print("OK: no stale shipping-state lie in generator or shipped HTML.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
