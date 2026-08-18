#!/usr/bin/env python3
"""form_metrics.py — form session metrics, with the denominator printed.

Reads a per-session CSV and reports starts, submits, completion and abandonment
(as exact complements on ONE named denominator), time-to-complete for
completers, per-field error rate, and per-field last-touch drop-off carrying its
proxy label. `--emit-imr` emits the individuals series that
`plugins/process-improvement/scripts/lss_calc.py imr` consumes.

⛔ NOVEL SYNTHESIS. Applying statistical process control to web-form telemetry is
this plugin's synthesis, not received practice. The marker below is printed on
STDERR in EVERY mode, from the public entry point, so a user who never opens a
document still sees it. A caller who imports this module and suppresses stderr
owns the omission.

⛔ STREAM CONTRACT — binding, and a gate asserts all three halves:
  1. `--emit-imr` writes ONLY whitespace-separated numbers to stdout. No header,
     no banner, no units. `lss_calc.py imr` requires `--values` and has no stdin
     path, so the round-trip is COMMAND SUBSTITUTION, not a pipe:
         lss_calc.py imr --values "$(form_metrics.py --emit-imr sessions.csv)"
     A marker on stdout would make `_parse_values` raise and the round-trip exit
     non-zero. That is why the marker goes to stderr.
  2. The marker reaches stderr in every mode, including `--emit-imr`.
  3. `--emit-imr` REFUSES below 20 individual observations. `lss_calc.py imr`
     accepts n >= 2 and will happily print control limits for a two-point
     series — exactly what this plugin's own best-practice rule forbids. The
     floor is enforced here so a gate cannot bless what the plugin prohibits.

Input schema (header row required):

    session_id,form_id,started_at,submitted_at,last_field,errors

  started_at / submitted_at  integer epoch seconds; submitted_at empty = abandoned
  last_field                 the last field interacted with (proxy; see below)
  errors                     semicolon-separated field names that errored (may be empty)

Exit codes: 0 = clean; 2 = a malformed input, an impossible input (a submission
with no start), or a series below the charting floor. Exit 1 is never used.

Usage:
    python3 form_metrics.py sessions.csv
    python3 form_metrics.py --emit-imr sessions.csv
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from pathlib import Path

NOVEL_SYNTHESIS_MARKER = (
    "[NOVEL SYNTHESIS — applying SPC to form telemetry is our synthesis, not "
    "established practice. We found no published work joining web-form telemetry to "
    "SPC/DMAIC (open-web search, 2026-08-17); the negative finding is bounded by that "
    "method and is not proof of universal absence.]"
)

# The denominator, named once and printed with every rate derived from it.
DENOMINATOR_LABEL = (
    "form starts = sessions in which any field received a FIRST INTERACTION "
    "(not page views, not sessions that merely saw the form)"
)

PROXY_CAVEAT = (
    "PROXY — last field touched is NOT the field that caused the exit; "
    "unvalidated, treat as a hypothesis generator"
)

REQUIRED_COLUMNS = ("session_id", "started_at", "submitted_at", "last_field", "errors")

# ⛔ Stated here, in best-practices/do-not-put-three-sigma-limits-on-a-low-volume-form-series.md,
# and asserted by the gate that runs this script. One number, three surfaces, no drift.
MIN_INDIVIDUAL_OBSERVATIONS = 20


class InputError(Exception):
    """The input cannot be trusted. Always fail closed."""


class Session:
    __slots__ = ("session_id", "started", "submitted", "last_field", "errors")

    def __init__(
        self,
        session_id: str,
        started: int | None,
        submitted: int | None,
        last_field: str,
        errors: list[str],
    ) -> None:
        self.session_id = session_id
        self.started = started
        self.submitted = submitted
        self.last_field = last_field
        self.errors = errors

    @property
    def completed(self) -> bool:
        return self.submitted is not None

    @property
    def duration(self) -> int:
        if self.started is None or self.submitted is None:
            raise InputError(f"session {self.session_id}: duration of an incomplete session")
        return self.submitted - self.started


def _int_or_none(raw: str, field: str, row_no: int) -> int | None:
    value = (raw or "").strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise InputError(f"row {row_no}: {field}={value!r} is not an integer epoch second") from exc


def load(path: Path) -> list[Session]:
    try:
        handle = path.open(newline="", encoding="utf-8")
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc
    with handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise InputError(f"{path}: no header row")
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise InputError(f"{path}: missing required column(s): {', '.join(missing)}")
        sessions: list[Session] = []
        for row_no, row in enumerate(reader, start=2):
            started = _int_or_none(row.get("started_at", ""), "started_at", row_no)
            submitted = _int_or_none(row.get("submitted_at", ""), "submitted_at", row_no)
            if submitted is not None and started is None:
                # A completion with no start. Left unchecked this makes completions
                # exceed starts and the completion rate exceed 100% — a number that
                # gets explained away rather than investigated.
                raise InputError(
                    f"row {row_no}: submitted_at is set but started_at is empty — "
                    "a completion cannot outnumber its own denominator"
                )
            if submitted is not None and started is not None and submitted < started:
                raise InputError(f"row {row_no}: submitted_at precedes started_at")
            errors = [e.strip() for e in (row.get("errors") or "").split(";") if e.strip()]
            sessions.append(
                Session(
                    session_id=(row.get("session_id") or "").strip(),
                    started=started,
                    submitted=submitted,
                    last_field=(row.get("last_field") or "").strip(),
                    errors=errors,
                )
            )
    if not sessions:
        raise InputError(f"{path}: no data rows — an empty scope is a failure, not a clean report")
    return sessions


def imr_series(sessions: list[Session]) -> list[int]:
    """One observation per completed submission: seconds to complete, in file order."""
    return [s.duration for s in sessions if s.completed]


def _rate(numerator: int, denominator: int) -> float:
    return 0.0 if denominator == 0 else 100.0 * numerator / denominator


def report(sessions: list[Session], out) -> None:
    starts = sum(1 for s in sessions if s.started is not None)
    submits = sum(1 for s in sessions if s.completed)
    completion = _rate(submits, starts)

    print("form metrics", file=out)
    print(f"denominator: {DENOMINATOR_LABEL}", file=out)
    print(f"starts: {starts}", file=out)
    print(f"submits: {submits}", file=out)
    print(f"completion rate: {completion:.2f}%", file=out)
    print(f"abandonment rate: {100.0 - completion:.2f}%", file=out)
    print("  (completion and abandonment are exact complements on the denominator above)", file=out)

    durations = imr_series(sessions)
    print("", file=out)
    print(f"time-to-complete, completers only (n={len(durations)}):", file=out)
    if durations:
        print(f"  median: {statistics.median(durations):.2f} s", file=out)
        print(f"  mean: {statistics.fmean(durations):.2f} s", file=out)
        print(f"  min: {min(durations)} s   max: {max(durations)} s", file=out)
    else:
        print("  no completed sessions", file=out)

    print("", file=out)
    print(f"per-field error rate (denominator: {starts} starts):", file=out)
    error_counts: dict[str, int] = {}
    for session in sessions:
        for field in set(session.errors):
            error_counts[field] = error_counts.get(field, 0) + 1
    if error_counts:
        for field in sorted(error_counts):
            print(f"  {field}: {_rate(error_counts[field], starts):.2f}%", file=out)
    else:
        print("  none recorded", file=out)

    abandoned = [s for s in sessions if s.started is not None and not s.completed]
    print("", file=out)
    print(f"per-field last-touch drop-off [{PROXY_CAVEAT}]", file=out)
    print(f"  (denominator: {len(abandoned)} abandoned sessions)", file=out)
    drop_counts: dict[str, int] = {}
    for session in abandoned:
        key = session.last_field or "(unrecorded)"
        drop_counts[key] = drop_counts.get(key, 0) + 1
    if drop_counts:
        for field in sorted(drop_counts):
            print(f"  {field}: {_rate(drop_counts[field], len(abandoned)):.2f}%", file=out)
    else:
        print("  no abandoned sessions", file=out)


def emit_imr(sessions: list[Session], out) -> None:
    """Numbers only. Nothing else may reach stdout in this mode."""
    series = imr_series(sessions)
    if len(series) < MIN_INDIVIDUAL_OBSERVATIONS:
        raise InputError(
            f"only {len(series)} completed observation(s); the charting floor is "
            f"{MIN_INDIVIDUAL_OBSERVATIONS} individual observations. Form series are "
            "low-volume and autocorrelated by weekday and campaign — three-sigma limits "
            "below this floor manufacture false special-cause signals. Refusing to emit."
        )
    for value in series:
        print(value, file=out)


def run(argv: list[str] | None = None, stdout=None, stderr=None) -> int:
    """Public entry point. Emits the synthesis marker to stderr in EVERY mode.

    Emitted here rather than inside `main()` so an importing caller also gets it;
    a caller who suppresses stderr owns the omission.
    """
    out = sys.stdout if stdout is None else stdout
    err = sys.stderr if stderr is None else stderr

    ap = argparse.ArgumentParser(description="Form session metrics with the denominator printed.")
    ap.add_argument("csv_path", type=Path, help="per-session CSV (see the module docstring)")
    ap.add_argument(
        "--emit-imr",
        action="store_true",
        help="emit the individuals series (numbers only, stdout) for lss_calc.py imr",
    )
    args = ap.parse_args(argv)

    print(NOVEL_SYNTHESIS_MARKER, file=err)

    try:
        sessions = load(args.csv_path)
        if args.emit_imr:
            emit_imr(sessions, out)
        else:
            report(sessions, out)
    except InputError as exc:
        print(f"form_metrics: {exc}", file=err)
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    return run(argv)


if __name__ == "__main__":
    sys.exit(main())
