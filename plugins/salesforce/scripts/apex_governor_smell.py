#!/usr/bin/env python3
"""apex_governor_smell.py — static "governor-limit smell" detector for Apex.

A heuristic, stdlib-only scanner for the dominant Salesforce defect class: SOQL
or DML inside a loop (the cause of `Too many SOQL queries: 101` /
`Too many DML statements: 151` under a bulk load). It is a *smell* detector, not
a compiler — it reasons about brace depth and `for`/`while`/`do` loop scopes with
regular expressions, so it can over- or under-report. Treat every finding as
"look here," confirm by reading the code, and prove the fix with a 200-record bulk
test (house opinions #1 and #9).

It complements the advisory PreToolUse hook (`hooks/flag-salesforce-anti-patterns.sh`,
which greps a single just-written file) by scanning a whole directory tree of
`.cls` / `.trigger` files on demand — e.g. in CI or before a deploy.

Usage:
    apex_governor_smell.py PATH [PATH ...]      # scan files/dirs (default: cwd)
    apex_governor_smell.py --format json PATH   # machine-readable output

Exit codes: 0 = no smells found; 1 = at least one smell found; 2 = bad usage.

This is decision-support, not a security control or a guarantee of bulk-safety.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

APEX_SUFFIXES = (".cls", ".trigger", ".apex")

# A line that opens a loop scope. We only need the keyword + an opening that leads
# to a block; brace-depth tracking below decides where the loop body ends.
_LOOP_RE = re.compile(r"\b(for|while|do)\b\s*[({]")

# SOQL inside Apex appears as a bracketed query: [ SELECT ... ] or [ FIND ... ].
_SOQL_RE = re.compile(r"\[\s*(SELECT|FIND)\b", re.IGNORECASE)

# DML statements and the Database.* method forms.
_DML_RE = re.compile(
    r"\b(insert|update|delete|undelete|upsert|merge)\b"
    r"|\bDatabase\.\s*(insert|update|delete|undelete|upsert|merge|convertLead)\b",
    re.IGNORECASE,
)

# Comment / string noise we strip before matching so a query mentioned in a
# comment or a string literal does not produce a false finding.
_LINE_COMMENT_RE = re.compile(r"//.*$")
_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_STRING_RE = re.compile(r"'(?:[^'\\]|\\.)*'")


@dataclass
class Finding:
    """One governor-limit smell located in a file."""

    path: str
    line: int
    kind: str  # "soql-in-loop" | "dml-in-loop"
    snippet: str


def _strip_noise(source: str) -> str:
    """Blank out block comments / line comments / string literals.

    Newlines are preserved so line numbers stay accurate; only the *content* is
    replaced, never the line count.
    """
    source = _BLOCK_COMMENT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), source)
    cleaned_lines = []
    for line in source.splitlines():
        line = _STRING_RE.sub("''", line)
        line = _LINE_COMMENT_RE.sub("", line)
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def scan_text(path: str, source: str) -> list[Finding]:
    """Return the SOQL/DML-in-loop findings for one Apex source string."""
    cleaned = _strip_noise(source)
    lines = cleaned.split("\n")
    raw_lines = source.split("\n")

    findings: list[Finding] = []
    # Stack of brace-depths at which an enclosing loop body began. While the stack
    # is non-empty we are inside at least one loop.
    loop_depths: list[int] = []
    depth = 0

    for idx, line in enumerate(lines):
        opens_loop = bool(_LOOP_RE.search(line))

        in_loop = bool(loop_depths)
        if in_loop:
            if _SOQL_RE.search(line):
                findings.append(
                    Finding(path, idx + 1, "soql-in-loop", raw_lines[idx].strip())
                )
            if _DML_RE.search(line):
                findings.append(
                    Finding(path, idx + 1, "dml-in-loop", raw_lines[idx].strip())
                )

        # Update brace depth from this line, recording where a loop body opens.
        for char in line:
            if char == "{":
                if opens_loop:
                    loop_depths.append(depth)
                    opens_loop = False
                depth += 1
            elif char == "}":
                depth -= 1
                if loop_depths and loop_depths[-1] == depth:
                    loop_depths.pop()

    return findings


def iter_apex_files(paths: list[str]) -> list[Path]:
    """Expand the given paths into the set of Apex source files to scan."""
    files: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            for suffix in APEX_SUFFIXES:
                files.extend(sorted(p.rglob(f"*{suffix}")))
        elif p.is_file() and p.suffix in APEX_SUFFIXES:
            files.append(p)
    # De-duplicate while preserving order.
    seen: set[Path] = set()
    unique: list[Path] = []
    for f in files:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    return unique


def scan_paths(paths: list[str]) -> list[Finding]:
    """Scan every Apex file under the given paths and collect findings."""
    findings: list[Finding] = []
    for file in iter_apex_files(paths):
        try:
            source = file.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"warning: could not read {file}: {exc}", file=sys.stderr)
            continue
        findings.extend(scan_text(str(file), source))
    return findings


def _print_text(findings: list[Finding]) -> None:
    if not findings:
        print("No governor-limit smells found. Still prove bulk-safety with a 200-record test.")
        return
    print(f"Found {len(findings)} governor-limit smell(s):\n")
    label = {"soql-in-loop": "SOQL in loop", "dml-in-loop": "DML in loop"}
    for f in findings:
        print(f"  {f.path}:{f.line}  [{label[f.kind]}]")
        print(f"      {f.snippet}")
    print(
        "\nHoist the query/DML out of the loop: collect keys into a Set, query/DML once,"
        "\nbucket into a Map for O(1) lookup. Then add a 200-record bulk test asserting"
        "\noutcomes (house opinions #1 and #9). Heuristic — confirm each by reading the code."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Heuristic SOQL/DML-in-loop detector for Apex (governor-limit smell)."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Files or directories to scan (default: current directory).",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text).",
    )
    args = parser.parse_args(argv)

    findings = scan_paths(args.paths)

    if args.format == "json":
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        _print_text(findings)

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
