#!/usr/bin/env python3
"""check-lineup-citations.py — enforce inline grounding on volatile model-lineup facts.

The `ai-coding-model-guidance` plugin ships a deliberately-volatile knowledge
bank: third-party model names, prices, and context windows for GitHub Copilot,
OpenAI Codex, and xAI Grok that churn weekly and sit past the author's training
cutoff. The plugin's whole reason to exist is to NOT confidently assert a stale
or invented number — so a table row that quotes a price or a context window must
carry a grounding signal (a citation link, a retrieval date, or an explicit
verify-at-use / unverified marker) right on the row. This gate makes that
discipline mechanical instead of trusting the prose to stay honest.

CONSERVATIVE + OPT-IN by design (the marketplace-gate house style): it only
scans a markdown file that explicitly opts in with the marker

    <!-- lineup-citations: enforce ... -->

so it can never false-positive on an unrelated doc that happens to mention a
dollar sign. Within an opted-in file it inspects only Markdown TABLE ROWS
(lines beginning with `|`) that contain a money amount (`$<digit>`) or a
token-context magnitude (`<n>M` / `<n>K tokens`). Each such row must contain at
least one grounding signal:

  * a markdown/inline link to a source            `](https?://...`
  * an ISO retrieval/launch date                  `20YY-MM-DD`
  * an explicit deferral marker                   `verify` / `unverified`

A row that quotes a number with none of these is the exact failure mode the
plugin exists to prevent (a bare, uncited, undated price), and the gate fails.

Exit 0 if every quoted number on every opted-in row is grounded; exit 1 with a
per-offender report otherwise. Runs in CI (validate-marketplace.yml) and is
exercised bidirectionally by audit-gates.sh.

Usage:
    check-lineup-citations.py [--root <dir>]
"""

from __future__ import annotations

import argparse
import glob
import re
import sys
from pathlib import Path

# Opt-in marker — a file is only scanned if it carries this HTML comment.
_OPT_IN = re.compile(r"<!--\s*lineup-citations:\s*enforce", re.IGNORECASE)

# A quoted number that demands grounding: a money amount or a token-context magnitude.
_MONEY = re.compile(r"\$\s?\d")
_CONTEXT = re.compile(r"\b\d+\s?M\b|\b\d+\s?[Kk]\s*(?:tok|token)")

# Grounding signals — any one of these on the same row satisfies the gate.
_LINK = re.compile(r"\]\(https?://")
_DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")
_DEFER = re.compile(r"verify|unverified", re.IGNORECASE)


def _needs_citation(row: str) -> bool:
    return bool(_MONEY.search(row) or _CONTEXT.search(row))


def _is_grounded(row: str) -> bool:
    return bool(_LINK.search(row) or _DATE.search(row) or _DEFER.search(row))


def check_file(path: Path) -> list[str]:
    """Return a list of human-readable failures for one file (empty == clean)."""
    text = path.read_text(encoding="utf-8")
    if not _OPT_IN.search(text):
        return []  # not opted in — silently skipped
    failures: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if not stripped.startswith("|"):
            continue  # only table rows are in scope
        if _needs_citation(line) and not _is_grounded(line):
            failures.append(
                f"{path}:{lineno}: quotes a price/context number with no "
                f"citation, date, or verify-at-use marker on the row:\n"
                f"      {stripped.strip()}"
            )
    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parent.parent),
        help="repo root to scan (default: the repo this script lives in)",
    )
    args = ap.parse_args()
    root = Path(args.root)

    # Scan every plugin knowledge/doc markdown; the opt-in marker gates the rest.
    candidates = sorted(
        glob.glob(str(root / "plugins" / "*" / "knowledge" / "**" / "*.md"), recursive=True)
        + glob.glob(str(root / "plugins" / "*" / "knowledge" / "*.md"))
    )
    seen: set[str] = set()
    failures: list[str] = []
    scanned = 0
    for c in candidates:
        if c in seen:
            continue
        seen.add(c)
        p = Path(c)
        text = p.read_text(encoding="utf-8")
        if not _OPT_IN.search(text):
            continue
        scanned += 1
        failures.extend(check_file(p))

    if failures:
        print("Lineup-citation gate FAILED — uncited volatile numbers:\n")
        for f in failures:
            print(f"  ✗ {f}")
        print(
            "\nEvery price/context-window row in a lineup-citations-enforced file "
            "must carry a citation link, an ISO date, or a verify-at-use marker."
        )
        return 1

    print(
        f"Lineup-citation gate OK — {scanned} opted-in file(s); "
        "every quoted price/context number is grounded."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
