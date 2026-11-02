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

# A loop keyword. Whether it really starts a loop is decided by what FOLLOWS it, which may
# be on a later line: for/while need a '(' (so a lower-case SOQL `for update` is not a
# loop), and the body is then a '{' block or, when no '{' follows, the next statement.
_LOOP_KW_RE = re.compile(r"\b(for|while|do)\b")

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


def _record_segment(
    findings: list[Finding],
    matched: set[str],
    path: str,
    idx: int,
    raw_line: str,
    text: str,
) -> None:
    """Flag SOQL/DML found in an in-loop segment (once per kind per physical line)."""
    if _SOQL_RE.search(text) and "soql-in-loop" not in matched:
        findings.append(Finding(path, idx + 1, "soql-in-loop", raw_line.strip()))
        matched.add("soql-in-loop")
    if _DML_RE.search(text) and "dml-in-loop" not in matched:
        findings.append(Finding(path, idx + 1, "dml-in-loop", raw_line.strip()))
        matched.add("dml-in-loop")


def _flush(
    findings: list[Finding],
    matched: set[str],
    path: str,
    idx: int,
    raw_line: str,
    seg: list[str],
    seg_in_loop: bool,
) -> None:
    """Score the finished segment under the state it was collected in, then clear it."""
    if seg_in_loop:
        _record_segment(findings, matched, path, idx, raw_line, "".join(seg))
    seg.clear()


class _PendingLoop:
    """A loop keyword whose body has not been fully seen yet (it may span lines).

    phase: "paren"  for/while, waiting for the '(' that opens the header
           "header" inside the header parens (SOQL here is NOT in the loop)
           "body"   header closed (or `do`): a '{' opens the body, a ';' means no body, any
                    other character starts a brace-less single-statement body
           "stmt"   inside that brace-less statement, up to its terminating ';'
    """

    __slots__ = ("phase", "parens", "start_depth")

    def __init__(self, keyword: str) -> None:
        self.phase = "body" if keyword == "do" else "paren"
        self.parens = 0
        self.start_depth = 0


def scan_text(path: str, source: str) -> list[Finding]:
    """Return the SOQL/DML-in-loop findings for one Apex source string.

    We walk the source character by character, tracking brace depth and loop scopes, and
    cut each line into segments at every point where the in-loop state changes. Content
    before a body-open is matched under the *pre-brace* loop state (so a loop HEADER's own
    SOQL -- the bulk-safe `for (a : [SELECT ...])` single-query pattern -- is NOT flagged),
    while content after the body-open is matched under the now-active scope (so a
    single-line body like `for (x : xs) { insert x; }` IS flagged).

    A loop keyword stays pending across lines until its body is known: an Allman-style
    '{' on the next line, a multi-line header, and a brace-less single-statement body
    (`for (...) insert x;`) are all in-loop; a `do { } while (c);` terminator and a
    lower-case SOQL `for update` are not loops.
    """
    cleaned = _strip_noise(source)
    lines = cleaned.split("\n")
    raw_lines = source.split("\n")

    findings: list[Finding] = []
    # Stack of brace-depths at which an enclosing loop body began.
    loop_depths: list[int] = []
    pending: list[_PendingLoop] = []  # innermost last
    depth = 0

    def in_loop() -> bool:
        return bool(loop_depths) or any(pl.phase == "stmt" for pl in pending)

    for idx, line in enumerate(lines):
        keywords = {m.start(): m.group(1) for m in _LOOP_KW_RE.finditer(line)}
        matched: set[str] = set()
        ctx = (findings, matched, path, idx, raw_lines[idx])
        seg: list[str] = []
        seg_in_loop = in_loop()
        i = 0
        while i < len(line):
            char = line[i]
            top = pending[-1] if pending else None

            if i in keywords and (top is None or top.phase in ("body", "stmt")):
                if top is not None and top.phase == "body":
                    # The keyword starts the brace-less body statement of the loop above.
                    _flush(*ctx, seg, seg_in_loop)
                    top.phase = "stmt"
                    top.start_depth = depth
                    seg_in_loop = in_loop()
                keyword = keywords[i]
                pending.append(_PendingLoop(keyword))
                seg.append(keyword)
                i += len(keyword)
                continue

            if top is not None and top.phase == "paren":
                if char == "(":
                    top.phase, top.parens = "header", 1
                elif not char.isspace():
                    pending.pop()  # not a loop after all (e.g. SOQL `for update`)
                    continue
                seg.append(char)
                i += 1
                continue

            if top is not None and top.phase == "header":
                if char == "(":
                    top.parens += 1
                elif char == ")":
                    top.parens -= 1
                    if top.parens == 0:
                        top.phase = "body"
                elif char == "{":
                    depth += 1  # e.g. `new Set<Id>{...}` literal inside the header
                elif char == "}":
                    depth -= 1
                seg.append(char)
                i += 1
                continue

            if top is not None and top.phase == "body":
                if char == "{":
                    # This brace opens the loop body. The segment before it (which includes
                    # any loop-header SOQL) is scored under the pre-brace state; the body
                    # after it is in-loop.
                    _flush(*ctx, seg, seg_in_loop)
                    pending.pop()
                    loop_depths.append(depth)
                    depth += 1
                    seg_in_loop = in_loop()
                    i += 1
                    continue
                if char == ";":
                    pending.pop()  # `do {...} while (c);` terminator, or an empty loop
                    seg.append(char)
                    i += 1
                    continue
                if char == "}":
                    pending.pop()  # malformed: no body before the enclosing block closed
                    continue
                if char.isspace():
                    seg.append(char)
                    i += 1
                    continue
                # First character of a brace-less single-statement body.
                _flush(*ctx, seg, seg_in_loop)
                top.phase = "stmt"
                top.start_depth = depth
                seg_in_loop = in_loop()

            if char == "{":
                depth += 1
                seg.append(char)
            elif char == "}":
                depth -= 1
                if loop_depths and loop_depths[-1] == depth:
                    _flush(*ctx, seg, seg_in_loop)
                    loop_depths.pop()
                    seg_in_loop = in_loop()
                seg.append(char)
            else:
                seg.append(char)

            # A brace-less body statement ends at its ';' (or when its block closes).
            if char in ";}":
                while pending and pending[-1].phase == "stmt" and depth <= pending[-1].start_depth:
                    _flush(*ctx, seg, seg_in_loop)
                    pending.pop()
                    seg_in_loop = in_loop()
            i += 1

        # Flush the trailing segment.
        if seg_in_loop:
            _record_segment(findings, matched, path, idx, raw_lines[idx], "".join(seg))

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
