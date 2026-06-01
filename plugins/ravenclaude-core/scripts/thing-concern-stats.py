#!/usr/bin/env python3
"""thing-concern-stats.py — compute per-concern reliability signals from the
Sága log.

Reads every `.ravenclaude/runs/thing/thing-*.json` verdict in the project, and
for each concern id reports the signals that surface false-positive-prone
concerns over time:

  - cited_total           seats voted while citing this concern
  - stripped              orchestrator deterministically resolved-false (a
                          confirmed false-positive caught by Phase A's strip
                          logic — these are the BEST signal because they're
                          mechanical, not heuristic)
  - heimdall_disagreed    citing seat said deny while heimdall said allow on
                          the same review (a proxy false-positive signal:
                          heimdall is injection-only, so a heimdall ALLOW is a
                          vote of confidence that the content is benign — when
                          another seat denies citing this concern, the seat is
                          plausibly hallucinating)
  - final_deny            reviews where this concern was in the final cited
                          list AND the final verdict was deny

The output ratio is `(stripped + heimdall_disagreed) / cited_total` — what
fraction of times this concern was cited, it was either a mechanically-
confirmed false positive or a behaviorally-suspected one. A high ratio is the
queue of concerns worth tuning.

Usage:
    thing-concern-stats.py                  # JSON to stdout, default
                                            # project = $CLAUDE_PROJECT_DIR
    thing-concern-stats.py --project DIR    # scan a different project
    thing-concern-stats.py --pretty         # pretty-printed JSON
"""

import argparse
import json
import os
import sys
from pathlib import Path


def _saga_dir(project: Path) -> Path:
    return project / ".ravenclaude" / "runs" / "thing"


def _iter_verdicts(saga_dir: Path):
    """Yield each parsed Sága JSON. Skips silently on a malformed entry (the
    Sága is best-effort; one bad line never poisons the report)."""
    if not saga_dir.is_dir():
        return
    for fp in sorted(saga_dir.glob("thing-*.json")):
        try:
            yield json.loads(fp.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue


def compute(project: Path) -> dict:
    """Aggregate per-concern signals across every Sága entry in `project`.
    Returns {concerns: [{id, cited_total, stripped, heimdall_disagreed,
    final_deny, fp_ratio}, ...], total_reviews: N, generated_at: ts}."""
    saga_dir = _saga_dir(project)
    per_concern: dict[str, dict] = {}
    total_reviews = 0

    for entry in _iter_verdicts(saga_dir):
        total_reviews += 1
        seats = entry.get("seats") or []
        final_verdict = entry.get("final_verdict") or ""
        final_cited = entry.get("concerns_cited") or []
        strips = entry.get("resolved_false_strips") or []

        # heimdall's verdict on this review (None if absent — older entries)
        heimdall_v = None
        for s in seats:
            if (s or {}).get("name") == "heimdall":
                heimdall_v = (s or {}).get("verdict")
                break

        # seat-level citations
        for s in seats:
            s = s or {}
            cited = s.get("concerns_cited") or []
            verdict = s.get("verdict") or ""
            for cid in cited:
                if not isinstance(cid, str):
                    continue
                row = per_concern.setdefault(
                    cid,
                    {
                        "id": cid,
                        "cited_total": 0,
                        "stripped": 0,
                        "heimdall_disagreed": 0,
                        "final_deny": 0,
                    },
                )
                row["cited_total"] += 1
                if (
                    s.get("name") != "heimdall"
                    and verdict == "deny"
                    and heimdall_v == "allow"
                ):
                    row["heimdall_disagreed"] += 1

        # orchestrator-level strips (Phase A's resolved-false bookkeeping)
        for strip in strips:
            for cid in (strip or {}).get("removed") or []:
                if not isinstance(cid, str):
                    continue
                row = per_concern.setdefault(
                    cid,
                    {
                        "id": cid,
                        "cited_total": 0,
                        "stripped": 0,
                        "heimdall_disagreed": 0,
                        "final_deny": 0,
                    },
                )
                row["stripped"] += 1
                # A strip implies the seat originally cited it; the seat's
                # cited list was updated before the Sága was written, so the
                # seat-loop above didn't double-count it.  Add to cited_total
                # so the ratio reflects every time this concern was raised.
                row["cited_total"] += 1

        # final-verdict denies attributable to this concern
        if final_verdict == "deny":
            for cid in final_cited:
                if not isinstance(cid, str):
                    continue
                row = per_concern.setdefault(
                    cid,
                    {
                        "id": cid,
                        "cited_total": 0,
                        "stripped": 0,
                        "heimdall_disagreed": 0,
                        "final_deny": 0,
                    },
                )
                row["final_deny"] += 1

    rows = []
    for cid, row in per_concern.items():
        total = max(row["cited_total"], 1)
        row["fp_ratio"] = round(
            (row["stripped"] + row["heimdall_disagreed"]) / total, 4
        )
        rows.append(row)
    rows.sort(key=lambda r: (-r["fp_ratio"], -r["cited_total"], r["id"]))
    return {
        "schema_version": 1,
        "total_reviews": total_reviews,
        "concerns": rows,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--project",
        default=os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd(),
        help="Project root (default: $CLAUDE_PROJECT_DIR or $PWD)",
    )
    ap.add_argument("--pretty", action="store_true", help="pretty-print JSON")
    args = ap.parse_args(argv)

    project = Path(args.project)
    if not project.is_dir():
        print(
            json.dumps({"error": f"not a directory: {project}"}),
            file=sys.stderr,
        )
        return 1

    report = compute(project)
    json.dump(report, sys.stdout, indent=2 if args.pretty else None)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
