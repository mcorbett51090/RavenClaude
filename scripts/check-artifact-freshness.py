#!/usr/bin/env python3
"""check-artifact-freshness.py — Gate 13 / Gate 97: does the COMMITTED generated
artifact still match what its generator emits?

WHY THIS EXISTS (2026-08-18)
────────────────────────────
`plugins/ravenclaude-core/dashboard.html` and `index.html` are GENERATED. Both
carried a "freshness gate" and BOTH gates were structurally blind to the thing
they were named for. Measured on origin/main @ 08237f2e, with a pristine tree:

    $ python3 scripts/generate-dashboards.py --check
    STALE: .../plugins/ravenclaude-core/dashboard.html      → exit 1
    $ python3 scripts/generate-index-dashboard.py --check
    [stale] .../index.html is out of date                   → exit 1
    $ bash scripts/audit-gates.sh
    841 pass, 0 fail

Two independent mechanisms produced that green:

  1. Gate 13's ONLY freshness assertion was a `must_fail`: append a fixture to
     the committed dashboard.html, run `--check`, expect non-zero. `--check` was
     ALREADY non-zero before the fixture was appended, so the assertion was
     satisfied by a pre-existing condition and proved nothing. There was no
     must_pass half at all — a stale committed file was simply never asserted
     against. A must_fail whose expected outcome is already true is not a test.

  2. Gate 97's hermetic rewrite pointed EVERY assertion at `$IDX_HTML` — the
     temp file the audit had just rendered — so it measured generator
     determinism and nothing about the artifact that actually ships. The
     committed-file check survived only on the `audit-gates.sh --check 97`
     per-gate path, which no workflow invokes.

WHAT THIS GATES, AND WHAT IT DELIBERATELY DOES NOT
──────────────────────────────────────────────────
STRUCTURAL freshness: the committed artifact must match the generator's current
output modulo two classes of value that `main` owns rather than the PR author:

  * generated TIMESTAMPS — the same four surfaces generate-index-dashboard.py's
    own `_strip_ts` neutralizes (without this a freshness gate false-fails one
    minute after generation and becomes a paper tiger).
  * VERSION VALUES under a `"…version"` JSON key — `marketplace_version`,
    `plugin_version`, and the per-plugin `version` inside `window.__RC_DATA__`.

The version carve-out is deliberate and measured, not laziness. Over the last 20
commits on main, 7 bumped plugins/ravenclaude-core/.claude-plugin/plugin.json and
only 2 of those also touched dashboard.html. Gating the version EXACTLY at PR time
would therefore redden roughly a quarter of all PRs and force every one of them to
regenerate a 10 MB and a 9 MB file into its own branch — the precise cross-PR
conflict contagion .github/workflows/regenerate-artifacts.yml was built to end.
Version drift stays owned by that post-merge self-heal.

Everything else IS gated, at PR time, against the committed bytes: a plugin row
appearing or disappearing, a stat count, a description, a template or CSS/JS
change, a hand-edit, a reordered or islanded DOM. Those are exactly the drifts
that silently break the downstream render gates and the Gate 132 DOM ratchet,
and none of them self-heal into correctness.

TEETH (`--must-fail`) — planted against the REAL committed artifact
──────────────────────────────────────────────────────────────────
`--must-fail` does NOT use a synthetic fixture file. It reads the actual
committed bytes, asserts they compare CLEAN (the positive control — without it
the teeth are exactly as vacuous as the bug above), then plants a drift into
those same bytes in memory and asserts the comparator reddens. It exits 0 only
when BOTH halves hold, so "already stale" can never be laundered into a pass.

Nothing here writes to a tracked file. Both renders go to memory/temp.

    python3 scripts/check-artifact-freshness.py --check
    python3 scripts/check-artifact-freshness.py --check --surface index.html
    python3 scripts/check-artifact-freshness.py --must-fail --surface index.html
    python3 scripts/check-artifact-freshness.py --report      # human diff shape
"""

from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"

DASHBOARD = REPO_ROOT / "plugins" / "ravenclaude-core" / "dashboard.html"
INDEX = REPO_ROOT / "index.html"
SURFACES = (DASHBOARD, INDEX)

# The drifts planted by --must-fail, each into the REAL committed bytes.
# Two SHAPES, because one shape only proves half of it:
#   append  — content the generator does not emit at all (the classic hand-edit).
#   mutate  — an in-place edit that changes NO byte count and NO version/timestamp
#             field. This is the one that proves the normalizer is not so broad it
#             launders real content drift (a plugin row, a class, a label) away.
def _plant_append(s: str) -> str:
    return s + "\n<!-- PLANTED DRIFT — check-artifact-freshness.py teeth -->\n"


def _plant_mutate(s: str) -> str:
    # Same length, structural, and deliberately NOT under a version/timestamp key.
    return s.replace('class="', 'class="Q', 1)


PLANTS = (("append", _plant_append), ("in-place mutate", _plant_mutate))

# ── Normalization ────────────────────────────────────────────────────────────
# Timestamps: identical to generate-index-dashboard.py's _strip_ts. Kept in sync
# by Gate 13's "normalizer covers every _strip_ts surface" assertion.
_TS_SUBS = (
    (re.compile(r'"generated":"[^"]*"'), '"generated":""'),
    (re.compile(r'"generated_date":"[^"]*"'), '"generated_date":""'),
    (re.compile(r"Updated \d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC"), "Updated"),
    (re.compile(r"(Last updated</span> <code>)[^<]*(</code>)"), r"\1\2"),
)

# Version VALUES under an EXPLICITLY ENUMERATED key — never a `*_version` wildcard.
# A wildcard would also blank `schema_version`, and a schema-version change in a
# generated artifact is real structural drift we must keep catching. Only the
# VALUE is blanked, so the key itself disappearing is still a diff and still red.
_VER_SUB = (
    re.compile(r'("(?:marketplace_version|plugin_version|version)"\s*:\s*)"[^"]*"'),
    r'\1""',
)


def normalize(s: str) -> str:
    """Blank the values `main` owns; leave every structural byte intact."""
    for pat, rep in _TS_SUBS:
        s = pat.sub(rep, s)
    return _VER_SUB[0].sub(_VER_SUB[1], s)


# ── Rendering (never in place) ───────────────────────────────────────────────
def render(surface: Path) -> str:
    """Render the surface's CURRENT generator output without touching the tree."""
    if surface == DASHBOARD:
        out = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "generate-dashboards.py"),
                "--plugin",
                "ravenclaude-core",
                "--stdout",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout
    if surface == INDEX:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "render-index.html"
            subprocess.run(
                [sys.executable, str(SCRIPTS / "generate-index-dashboard.py"), "-o", str(tmp)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            return tmp.read_text(encoding="utf-8")
    raise ValueError(f"unknown surface: {surface}")


def compare(committed: str, fresh: str) -> bool:
    """True iff the committed text is structurally fresh."""
    return normalize(committed) == normalize(fresh)


def rel(p: Path) -> str:
    return str(p.relative_to(REPO_ROOT))


def _resolve(name: str | None) -> list[Path]:
    if not name:
        return list(SURFACES)
    want = (REPO_ROOT / name).resolve()
    for s in SURFACES:
        if s == want:
            return [s]
    raise SystemExit(f"ERROR: --surface must be one of {[rel(s) for s in SURFACES]}, got {name!r}")


# ── Modes ────────────────────────────────────────────────────────────────────
def do_check(surfaces: list[Path]) -> int:
    rc = 0
    for s in surfaces:
        if not s.is_file():
            print(f"FAIL: {rel(s)}: committed artifact is MISSING", file=sys.stderr)
            rc = 1
            continue
        if compare(s.read_text(encoding="utf-8"), render(s)):
            print(f"OK:   {rel(s)}: structurally fresh vs its generator")
        else:
            print(
                f"FAIL: {rel(s)}: STRUCTURALLY STALE — the committed artifact no longer\n"
                f"      matches its generator (timestamps and version values excluded).\n"
                f"      Regenerate it; see --report for the diff shape.",
                file=sys.stderr,
            )
            rc = 1
    return rc


def do_must_fail(surfaces: list[Path]) -> int:
    """Teeth, planted into the REAL committed bytes. Exit 0 only if, for every
    surface, the unmutated bytes compare CLEAN (positive control) AND the
    planted drift is caught."""
    rc = 0
    for s in surfaces:
        fresh = render(s)
        committed = s.read_text(encoding="utf-8")
        if not compare(committed, fresh):
            print(
                f"FAIL: {rel(s)}: no positive control — the committed artifact is ALREADY\n"
                f"      stale, so a 'drift is detected' assertion here would be satisfied by a\n"
                f"      pre-existing condition and would prove nothing. This is the exact bug\n"
                f"      Gate 13 shipped. Regenerate the artifact, then the teeth are provable.",
                file=sys.stderr,
            )
            rc = 1
            continue
        caught = True
        for label, plant in PLANTS:
            planted = plant(committed)
            if planted == committed:
                print(
                    f"FAIL: {rel(s)}: the '{label}' plant was a NO-OP — the teeth would be\n"
                    f"      testing an unmutated file.",
                    file=sys.stderr,
                )
                caught = False
                continue
            if compare(planted, fresh):
                print(
                    f"FAIL: {rel(s)}: a '{label}' drift planted in the REAL committed artifact\n"
                    f"      was NOT detected — the comparator has no teeth for that shape.",
                    file=sys.stderr,
                )
                caught = False
        if not caught:
            rc = 1
            continue
        # And the baseline is still clean after the plants (they were in memory).
        if not compare(s.read_text(encoding="utf-8"), fresh):
            print(f"FAIL: {rel(s)}: teeth run mutated the committed file", file=sys.stderr)
            rc = 1
            continue
        print(
            f"OK:   {rel(s)}: clean baseline -> {len(PLANTS)} planted drift shapes caught"
            f" -> still clean"
        )
    return rc


def do_report(surfaces: list[Path]) -> int:
    for s in surfaces:
        committed = s.read_text(encoding="utf-8") if s.is_file() else ""
        fresh = render(s)
        print(f"── {rel(s)} ──")
        print(f"   exact bytes:  committed={len(committed):,}  fresh={len(fresh):,}")
        print(f"   exact match:  {committed == fresh}")
        print(f"   structural:   {compare(committed, fresh)}")
        diff = list(
            difflib.unified_diff(
                committed.splitlines(), fresh.splitlines(), "committed", "fresh", n=0, lineterm=""
            )
        )
        print(f"   exact diff:   {len(diff)} unified-diff lines")
        for line in diff[:12]:
            print(f"     {line[:160]}")
        if len(diff) > 12:
            print(f"     … {len(diff) - 12} more")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Committed generated-artifact freshness (structural).")
    ap.add_argument("--check", action="store_true", help="committed artifacts are structurally fresh")
    ap.add_argument(
        "--must-fail",
        action="store_true",
        help="teeth: clean baseline + a drift planted in the REAL committed bytes is caught",
    )
    ap.add_argument("--report", action="store_true", help="human-readable diff shape")
    ap.add_argument("--surface", help=f"limit to one of {[rel(s) for s in SURFACES]}")
    args = ap.parse_args()

    surfaces = _resolve(args.surface)
    if args.report:
        return do_report(surfaces)
    if args.must_fail:
        return do_must_fail(surfaces)
    if args.check:
        return do_check(surfaces)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
