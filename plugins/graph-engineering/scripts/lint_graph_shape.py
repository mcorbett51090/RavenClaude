#!/usr/bin/env python3
"""lint_graph_shape.py — shape-check graph query snippets (stdlib only).

A *shape linter*, not a parser and not a query engine. It flags three ERROR-class
smells the graph-engineering constitution treats as bugs, plus one WARNING:

  ERROR
    - unbounded variable-length path (Cypher `-[*]->` / `-[*..]->` / `-[*1..]->`;
      GQL `{1,}` / `{,}` with no upper bound)
    - missing relationship type (`-[]-`, `-[]->`, `<-[]-`)
    - anonymous expansion `MATCH ()-` / `MATCH ()<-` (supernode scan heuristic)

  WARNING
    - Cypher `*` quantified path used in a `.gql` file (pre-GQL syntax)

False positives: prose that mentions `-[*]->` in markdown will flag — that is
intentional for knowledge files (put intentional-bad examples in fixtures/).
False negatives: a full Cypher/GQL/SPARQL parser would catch more; this does not
claim to. SPARQL/Gremlin get thinner "unbounded + untyped" heuristics.

No network. Stdlib only (argparse, re, sys, pathlib).

Usage:
    lint_graph_shape.py [--strict] PATH [PATH ...]
    lint_graph_shape.py [--strict] --stdin
    lint_graph_shape.py --self-test

Default exit 0 even on ERROR (advisory). --strict → exit 1 if any ERROR.
`.graphql` files print a "wrong plugin" note and exit 0.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ERROR = "ERROR"
WARNING = "WARNING"

# Cypher unbounded: [*]  [*..]  [*1..]  [*..]  [*..]  not [*1..3] or [*..5] or [*5]
_CYPHER_UNBOUNDED = re.compile(
    r"-\[(?:[A-Za-z_][\w]*\s*)?\*(?:\s*\d+\s*)?\.\.(?:\s*)?\]->|"
    r"-\[(?:[A-Za-z_][\w]*\s*)?\*\]->|"
    r"<-\[(?:[A-Za-z_][\w]*\s*)?\*(?:\s*\d+\s*)?\.\.(?:\s*)?\]-|"
    r"<-\[(?:[A-Za-z_][\w]*\s*)?\*\]-"
)
_CYPHER_UNBOUNDED_SIMPLE = re.compile(
    r"\[\s*(?:[A-Za-z_][\w]*)?\s*\*(?:\s*\d+\s*)?\.\.\s*\]|"
    r"\[\s*(?:[A-Za-z_][\w]*)?\s*\*\s*\]"
)

# GQL {1,} or {,} without an upper bound. {1,5} is fine.
_GQL_UNBOUNDED = re.compile(r"\{\s*\d*\s*,\s*\}")

# Untyped relationship: -[]-  -[]->  <-[]-
_UNTYPED_REL = re.compile(r"<\s*-\s*\[\s*\]\s*-|-\s*\[\s*\]\s*-")

# Anonymous MATCH ()- or MATCH ()<-
_ANON_MATCH = re.compile(r"\bMATCH\s+\(\s*\)\s*<?-", re.IGNORECASE)

_GRAPHQL_SUFFIXES = {".graphql", ".gqls"}
_SCAN_SUFFIXES = {
    ".cypher",
    ".cyp",
    ".gql",
    ".sparql",
    ".rq",
    ".groovy",
    ".py",
    ".js",
    ".ts",
    ".md",
}


def _findings_for_line(line: str, lineno: int, suffix: str) -> list[tuple[int, str, str]]:
    out: list[tuple[int, str, str]] = []
    if _CYPHER_UNBOUNDED.search(line) or _CYPHER_UNBOUNDED_SIMPLE.search(line):
        out.append(
            (
                lineno,
                ERROR,
                "unbounded variable-length path — give an upper bound "
                "(Cypher [*1..5], not [*] / [*..] / [*1..])",
            )
        )
    if _GQL_UNBOUNDED.search(line):
        out.append(
            (
                lineno,
                ERROR,
                "unbounded GQL quantifier {n,} / {,} — give an upper bound ({1,5})",
            )
        )
    if _UNTYPED_REL.search(line):
        out.append(
            (
                lineno,
                ERROR,
                "missing relationship type — type and direct every edge "
                "((a)-[:KNOWS]->(b), not (a)-[]-(b))",
            )
        )
    if _ANON_MATCH.search(line):
        out.append(
            (
                lineno,
                ERROR,
                "anonymous MATCH ()- expansion — name the start node and type the edge "
                "(supernode scan heuristic)",
            )
        )
    if suffix == ".gql" and re.search(r"\[\s*\*", line):
        out.append(
            (
                lineno,
                WARNING,
                "Cypher * quantified-path syntax is not ISO GQL — use {1, n}",
            )
        )
    return out


def lint_text(text: str, filename: str = "<stdin>") -> list[tuple[str, int, str, str]]:
    suffix = Path(filename).suffix.lower()
    if suffix in _GRAPHQL_SUFFIXES:
        return []
    findings: list[tuple[str, int, str, str]] = []
    for i, line in enumerate(text.splitlines(), 1):
        for lineno, level, msg in _findings_for_line(line, i, suffix):
            findings.append((filename, lineno, level, msg))
    return findings


def lint_path(path: Path) -> list[tuple[str, int, str, str]]:
    suffix = path.suffix.lower()
    if suffix in _GRAPHQL_SUFFIXES:
        print(f"{path}: wrong plugin — GraphQL belongs to graphql-engineering; skipped")
        return []
    if suffix not in _SCAN_SUFFIXES and suffix != "":
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"{path}: ERROR: cannot read: {exc}", file=sys.stderr)
        return [(str(path), 0, ERROR, f"cannot read: {exc}")]
    return lint_text(text, str(path))


def _print(findings: list[tuple[str, int, str, str]]) -> None:
    for filename, lineno, level, msg in findings:
        where = f"{filename}:{lineno}" if lineno else filename
        print(f"{where}: {level}: {msg}")


def self_test() -> int:
    """Embedded canary — does not depend on fixtures/ remaining on disk."""
    cases = [
        (
            "good",
            "MATCH (a:Person)-[:KNOWS*1..3]->(b:Person) RETURN b\n",
            ".cypher",
            [],
        ),
        (
            "unbounded",
            "MATCH (a)-[*]->(b) RETURN a\n",
            ".cypher",
            [ERROR],
        ),
        (
            "untyped",
            "MATCH (a)-[]->(b) RETURN a\n",
            ".cypher",
            [ERROR],
        ),
        (
            "anonymous",
            "MATCH ()-[:KNOWS]->(b) RETURN b\n",
            ".cypher",
            [ERROR],
        ),
        (
            "gql-star-warn",
            "MATCH (a)-[*1..3]->(b) RETURN b\n",
            ".gql",
            [WARNING],
        ),
    ]
    failed = 0
    for name, text, suffix, want_levels in cases:
        findings = lint_text(text, f"{name}{suffix}")
        got = [f[2] for f in findings]
        if want_levels:
            if not any(level in got for level in want_levels):
                print(f"SELF-TEST FAIL {name}: expected {want_levels}, got {got}")
                failed += 1
            else:
                print(f"SELF-TEST OK   {name}")
        else:
            if findings:
                print(f"SELF-TEST FAIL {name}: expected clean, got {findings}")
                failed += 1
            else:
                print(f"SELF-TEST OK   {name}")
    if failed:
        print(f"SELF-TEST: {failed} failed")
        return 1
    print("SELF-TEST: all passed")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--stdin", action="store_true", help="lint text from stdin")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 if any ERROR finding (default: advisory, always 0)",
    )
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    findings: list[tuple[str, int, str, str]] = []
    if args.stdin:
        findings.extend(lint_text(sys.stdin.read(), "<stdin>"))
    for path in args.paths:
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file():
                    findings.extend(lint_path(child))
        else:
            findings.extend(lint_path(path))

    _print(findings)
    if args.strict and any(level == ERROR for _, _, level, _ in findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
