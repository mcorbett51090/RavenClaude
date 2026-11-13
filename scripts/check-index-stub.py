#!/usr/bin/env python3
"""check-index-stub.py — Gate 51 Phase 3b: committed index.html is a thin redirect.

Phase 3b retires the fat portal from the committed tree. Pages `/` must be a
stub that redirects to `plugins/ravenclaude-core/dashboard.html` (meta refresh
and/or `location.replace`), must NOT reintroduce the fat portal markers
(`id="dt-store"`, `const DASH_SECTIONS`), and must stay under 8 KiB.

Usage:
    python3 scripts/check-index-stub.py                 # assert committed index.html
    python3 scripts/check-index-stub.py path/to.html    # assert that file
    python3 scripts/check-index-stub.py --must-fail     # plant a bad stub; expect fail

Exit codes: 0 clean, 2 violation / cannot-run (fail-closed). Exit 1 is never
used for a finding — a non-blocking exit code is itself a silent fail-open.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INDEX = REPO_ROOT / "index.html"
DASH_PATH = "plugins/ravenclaude-core/dashboard.html"
MAX_BYTES = 8 * 1024  # 8 KiB

# Fat-portal markers that must stay out of the stub.
FORBIDDEN = (
    'id="dt-store"',
    "const DASH_SECTIONS",
)


def check_stub(path: Path) -> list[str]:
    """Return a list of failure messages (empty == pass)."""
    failures: list[str] = []
    try:
        raw = path.read_bytes()
    except OSError as e:
        return [f"cannot read {path}: {e}"]

    if len(raw) >= MAX_BYTES:
        failures.append(
            f"{path}: {len(raw)} bytes >= {MAX_BYTES} (stub must stay under 8 KiB)"
        )

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        return failures + [f"{path}: not utf-8: {e}"]

    has_meta = DASH_PATH in text and (
        "http-equiv" in text.lower() and "refresh" in text.lower()
    )
    has_js = DASH_PATH in text and "location.replace" in text
    if DASH_PATH not in text:
        failures.append(
            f"{path}: missing redirect target `{DASH_PATH}` "
            "(meta refresh or location.replace required)"
        )
    elif not (has_meta or has_js):
        failures.append(
            f"{path}: mentions `{DASH_PATH}` but has neither meta refresh "
            "nor location.replace"
        )

    for marker in FORBIDDEN:
        if marker in text:
            failures.append(
                f"{path}: fat-portal marker present: {marker!r} "
                "(Phase 3b stub must not bake the portal back in)"
            )

    return failures


def report(failures: list[str], label: str) -> int:
    if failures:
        print(f"FAIL: index stub contract ({label}) — {len(failures)}:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 2
    print(f"OK: index stub satisfies Phase 3b contract ({label})")
    return 0


def must_fail() -> int:
    """Plant a stub that omits the dashboard path; the check MUST exit 2."""
    # Positive control first: the real committed stub must be clean. Without
    # this, an already-broken tree would make --must-fail vacuously green.
    live = check_stub(DEFAULT_INDEX)
    if live:
        print(
            "FAIL: --must-fail positive control — committed index.html already "
            "violates the stub contract; teeth cannot be proven:",
            file=sys.stderr,
        )
        for f in live:
            print(f"  - {f}", file=sys.stderr)
        return 2

    bad = (
        "<!DOCTYPE html><html><head><title>bad</title>"
        '<meta http-equiv="refresh" content="0; url=/somewhere-else.html" />'
        "</head><body>no dashboard redirect</body></html>\n"
    )
    with tempfile.TemporaryDirectory(prefix="index-stub-mustfail-") as tmp:
        bad_path = Path(tmp) / "index-bad.html"
        bad_path.write_text(bad, encoding="utf-8")
        failures = check_stub(bad_path)
        if not failures:
            print(
                "FAIL: --must-fail teeth broken — stub missing dashboard path "
                "did not fail",
                file=sys.stderr,
            )
            return 2
        # Confirm the discriminating failure is the missing dashboard path.
        if not any(DASH_PATH in f or "redirect" in f.lower() for f in failures):
            print(
                "FAIL: --must-fail reddened for the wrong reason:",
                file=sys.stderr,
            )
            for f in failures:
                print(f"  - {f}", file=sys.stderr)
            return 2
        print(
            "OK: --must-fail teeth — stub missing dashboard path exits 2 "
            f"({len(failures)} finding(s))"
        )
        return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "path",
        nargs="?",
        default=str(DEFAULT_INDEX),
        help="HTML file to check (default: committed index.html)",
    )
    ap.add_argument(
        "--must-fail",
        action="store_true",
        help="plant a temp stub missing the dashboard path; exit 0 only if "
        "that check fails (and the live stub is clean)",
    )
    args = ap.parse_args()

    if args.must_fail:
        return must_fail()

    path = Path(args.path)
    return report(check_stub(path), str(path))


if __name__ == "__main__":
    sys.exit(main())
