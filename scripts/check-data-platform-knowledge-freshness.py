#!/usr/bin/env python3
"""check-data-platform-knowledge-freshness.py — sweep data-platform's knowledge bank for staleness.

FORGE dashboard-top1pct P1-12 (2026-09-03): ~30 of ~37 `knowledge/*.md` files were past the
plugin's own self-declared 90-day re-verification trigger (retrieval dates clustering at
2026-05-21/2026-06-03/04, 90-105 days old as of this run). This is a SWEEP, not a purge —
spot-checking one aged claim (Cube Cloud pricing) found it still accurate 105 days past its
retrieval date, so "aged" does not mean "wrong." Three files had no discoverable date at all
(`charting-library-selection-2026.md`, `dashboard-productization-multi-tenant-2026.md`,
`data-platform-decision-trees.md`) — corrected this same session; two of the three already
carried a `last_reviewed:` field in YAML frontmatter this script's earlier grep-based
detection had simply missed (a real false-positive in the *investigation*, caught and named
here rather than silently repeated in the tooling).

Two date formats coexist by design, not oversight: some knowledge files carry a proper YAML
frontmatter `last_reviewed:` field (the more machine-readable shape); most carry a prose
`> **Last reviewed:** YYYY-MM-DD` blockquote line. Forcing all ~37 files into one identical
format would be a large, low-value mechanical rewrite for no functional gain — this script
accepts either, deliberately.

Severity split (per plan.md's own acceptance test): a file with NO discoverable date at all is
a hard FAIL — an undated claim is worse than a stale one, because nothing can flag it for
re-check. A file whose date is simply past the 90-day trigger is a WARN, not a FAIL — the
knowledge bank is a research substrate consulted by agents, not a build input; treating every
aging claim as a blocking failure would either force a constant re-verification treadmill or
train everyone to ignore the gate. Wired into the scheduled routine lane, not a PR gate.

Usage:
    check-data-platform-knowledge-freshness.py [--root <path-to-data-platform-plugin-dir>]
                                                [--as-of YYYY-MM-DD] [--trigger-days N]

Exit 0 unless a file has no discoverable date at all (exit 1). Staleness past the trigger is
printed as a WARN and does not affect the exit code.
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

_FM_DATE = re.compile(r"^last_reviewed:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
# Prose forms: "> **Last reviewed:** 2026-05-21." / "**Last reviewed:** 2026-05-21 — the OLDEST..."
_PROSE_DATE = re.compile(r"\*\*Last reviewed[^*]*\*\*[^0-9]*?(\d{4}-\d{2}-\d{2})")

DEFAULT_TRIGGER_DAYS = 90


def _extract_date(text: str) -> str | None:
    m = _FM_DATE.search(text)
    if m:
        return m.group(1)
    m = _PROSE_DATE.search(text)
    if m:
        return m.group(1)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="plugins/data-platform")
    ap.add_argument("--as-of", default=None, help="YYYY-MM-DD; defaults to today")
    ap.add_argument("--trigger-days", type=int, default=DEFAULT_TRIGGER_DAYS)
    args = ap.parse_args()

    root = Path(args.root)
    knowledge_dir = root / "knowledge"
    if not knowledge_dir.is_dir():
        print(f"check-data-platform-knowledge-freshness: no knowledge/ dir under {root}", file=sys.stderr)
        return 2

    as_of = (
        datetime.date.fromisoformat(args.as_of)
        if args.as_of
        else datetime.date.today()
    )

    missing: list[str] = []
    stale: list[tuple[str, str, int]] = []
    fresh_count = 0

    for md in sorted(knowledge_dir.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        date_str = _extract_date(text)
        if date_str is None:
            missing.append(md.name)
            continue
        reviewed = datetime.date.fromisoformat(date_str)
        age_days = (as_of - reviewed).days
        if age_days > args.trigger_days:
            stale.append((md.name, date_str, age_days))
        else:
            fresh_count += 1

    if missing:
        print("check-data-platform-knowledge-freshness: FAILED", file=sys.stderr)
        for name in missing:
            print(f"  - {name}: no discoverable last_reviewed date (neither YAML frontmatter nor prose)", file=sys.stderr)

    if stale:
        print(f"⚠ {len(stale)} file(s) past the {args.trigger_days}-day trigger (WARN, not a failure):")
        for name, date_str, age in sorted(stale, key=lambda t: -t[2]):
            print(f"  - {name}: last reviewed {date_str} ({age} days ago)")

    print(
        f"check-data-platform-knowledge-freshness: {fresh_count} fresh, {len(stale)} stale (WARN), "
        f"{len(missing)} missing date (FAIL) — as of {as_of.isoformat()}"
    )

    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
