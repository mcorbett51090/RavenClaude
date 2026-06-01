#!/usr/bin/env python3
"""
knowledge-health.py — sweep all `plugins/*/knowledge/**.md` files for stale
verification dates and emit a JSON remediation queue.

Reads each file's first ~30 lines looking for a date marker — accepts several
common forms used across the marketplace:

    Last reviewed: 2026-05-21
    Last verified: 2026-05-21
    last-verified: 2026-05-21
    retrieved: 2026-05-21
    last_verified: 2026-05-21

(Case-insensitive on the key; ISO-8601 date on the value.)

Categorizes by age:
    untracked  — no date marker at all
    fresh      — < 90 days
    due_soon   — 60-90 days
    stale      — > 90 days

Output (stdout): a JSON document with three lists + counts. Used by:
- the release checklist (run before tagging a marketplace release)
- the `ravenclaude doctor` subcommand (one of the health checks)
- the `knowledge-health` skill (wraps this script for dashboard surfaces)

Exit code: 0 always (the script's job is to REPORT staleness, not enforce it —
the release-checklist step is what gates).

Usage:
    python3 plugins/ravenclaude-core/scripts/knowledge-health.py
    python3 plugins/ravenclaude-core/scripts/knowledge-health.py --json
    python3 plugins/ravenclaude-core/scripts/knowledge-health.py --threshold-days 180
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

DATE_KEYS = ("last reviewed", "last verified", "last-verified", "last_verified", "retrieved")
ISO_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
DEFAULT_THRESHOLD_DAYS = 90
DUE_SOON_WINDOW_DAYS = 30  # files within 30 days of the threshold


@dataclass
class FileVerdict:
    path: str
    plugin: str
    last_verified: str | None
    age_days: int | None
    bucket: str  # "fresh" | "due_soon" | "stale" | "untracked"
    excerpt: str = ""


@dataclass
class Report:
    threshold_days: int
    today: str
    counts: dict[str, int] = field(default_factory=dict)
    stale: list[FileVerdict] = field(default_factory=list)
    due_soon: list[FileVerdict] = field(default_factory=list)
    untracked: list[FileVerdict] = field(default_factory=list)
    fresh: list[FileVerdict] = field(default_factory=list)


def _today() -> date:
    return date.today()


def _extract_date(text: str) -> tuple[str | None, str]:
    """
    Return (iso_date_str, excerpt_line) or (None, "") if no date found.

    Only inspects the first ~30 lines so we don't accidentally pick up a
    historical-narrative date deep in the file.
    """
    head = "\n".join(text.splitlines()[:30])
    lower = head.lower()
    for key in DATE_KEYS:
        idx = lower.find(key)
        if idx < 0:
            continue
        line_start = head.rfind("\n", 0, idx) + 1
        line_end = head.find("\n", idx)
        line = head[line_start : line_end if line_end >= 0 else len(head)]
        match = ISO_DATE_RE.search(line)
        if match:
            return match.group(1), line.strip()
    return None, ""


def _bucket(age_days: int | None, threshold_days: int) -> str:
    if age_days is None:
        return "untracked"
    if age_days > threshold_days:
        return "stale"
    if age_days > threshold_days - DUE_SOON_WINDOW_DAYS:
        return "due_soon"
    return "fresh"


def _walk(threshold_days: int) -> Report:
    plugins_root = REPO_ROOT / "plugins"
    report = Report(threshold_days=threshold_days, today=_today().isoformat())
    today = _today()

    if not plugins_root.is_dir():
        return report

    for md_path in sorted(plugins_root.glob("*/knowledge/**/*.md")):
        try:
            text = md_path.read_text(errors="replace")
        except OSError:
            continue
        date_str, excerpt = _extract_date(text)
        age_days: int | None = None
        if date_str:
            try:
                age_days = (today - datetime.strptime(date_str, "%Y-%m-%d").date()).days
            except ValueError:
                date_str = None

        plugin = md_path.relative_to(plugins_root).parts[0]
        rel = md_path.relative_to(REPO_ROOT).as_posix()
        verdict = FileVerdict(
            path=rel,
            plugin=plugin,
            last_verified=date_str,
            age_days=age_days,
            bucket=_bucket(age_days, threshold_days),
            excerpt=excerpt,
        )
        if verdict.bucket == "stale":
            report.stale.append(verdict)
        elif verdict.bucket == "due_soon":
            report.due_soon.append(verdict)
        elif verdict.bucket == "untracked":
            report.untracked.append(verdict)
        else:
            report.fresh.append(verdict)

    report.stale.sort(key=lambda v: -(v.age_days or 0))
    report.due_soon.sort(key=lambda v: -(v.age_days or 0))

    report.counts = {
        "stale": len(report.stale),
        "due_soon": len(report.due_soon),
        "untracked": len(report.untracked),
        "fresh": len(report.fresh),
        "total": len(report.stale) + len(report.due_soon) + len(report.untracked) + len(report.fresh),
    }
    return report


def _render_text(report: Report) -> str:
    lines = []
    counts = report.counts
    lines.append(
        f"Knowledge health — {counts.get('total', 0)} files in plugins/*/knowledge/ "
        f"(threshold: {report.threshold_days} days; today: {report.today})"
    )
    lines.append(
        f"  stale: {counts.get('stale', 0)}    "
        f"due_soon: {counts.get('due_soon', 0)}    "
        f"untracked: {counts.get('untracked', 0)}    "
        f"fresh: {counts.get('fresh', 0)}"
    )
    if report.stale:
        lines.append("")
        lines.append("STALE (re-verify):")
        for v in report.stale:
            lines.append(f"  [{v.age_days} days] {v.path} — {v.excerpt or '(no excerpt)'}")
    if report.due_soon:
        lines.append("")
        lines.append("DUE SOON (within 30 days of threshold):")
        for v in report.due_soon:
            lines.append(f"  [{v.age_days} days] {v.path}")
    if report.untracked:
        lines.append("")
        lines.append("UNTRACKED (no date marker — add one):")
        for v in report.untracked:
            lines.append(f"  {v.path}")
    if not (report.stale or report.due_soon or report.untracked):
        lines.append("")
        lines.append("All tracked. Nothing to do.")
    return "\n".join(lines) + "\n"


def _to_json(report: Report) -> str:
    payload = {
        "schema_version": 1,
        "today": report.today,
        "threshold_days": report.threshold_days,
        "counts": report.counts,
        "stale": [v.__dict__ for v in report.stale],
        "due_soon": [v.__dict__ for v in report.due_soon],
        "untracked": [v.__dict__ for v in report.untracked],
        "fresh_paths": [v.path for v in report.fresh],
    }
    return json.dumps(payload, indent=2) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Sweep plugins/*/knowledge/ for stale verification dates.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    parser.add_argument(
        "--threshold-days",
        type=int,
        default=DEFAULT_THRESHOLD_DAYS,
        help=f"Days-since-verification at which a file becomes stale (default: {DEFAULT_THRESHOLD_DAYS}).",
    )
    args = parser.parse_args(argv)

    report = _walk(args.threshold_days)
    sys.stdout.write(_to_json(report) if args.json else _render_text(report))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
