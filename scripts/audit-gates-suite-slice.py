#!/usr/bin/env python3
"""Slice `scripts/audit-gates.sh`'s full-suite region down to the blocks a
named `--suite` needs, for `audit-gates.sh --suite <name>` (PR-C).

WHY A SEPARATE SCRIPT, NOT A REWRITE OF audit-gates.sh ITSELF: the full-suite
region is ~225 sequential gate blocks with no per-gate function boundary —
wrapping every block in a conditional would touch nearly the whole file and
invite exactly the drift this initiative exists to prevent (a --suite path
that quietly runs different code than the default path). Slicing the file's
OWN TEXT and `source`-ing only the selected blocks means every gate's fixture
is executed from the SAME lines the default (no-args) run executes — there is
no second copy to drift.

WHAT COUNTS AS A HEADER (deliberately stricter than Gate 195's reachability
parser in scripts/check-gate-registration.py): a real gate header is a line
that ACTUALLY PRINTS the banner (`echo "── Gate N: …"` at statement position),
never a line that merely mentions the shape in a comment (one such comment
exists at the time of writing, describing a HISTORICAL grouped-header bug —
confirmed by control probe: `grep -n '── Gates [0-9]' scripts/audit-gates.sh`
returns exactly that one comment line, and re-deriving the full token set with
this stricter regex matches the looser extraction byte-for-byte, 0 additions/
removals). Gate 195 treats a letter-suffixed sub-gate (3b/5b/9b) as a
sub-section of its numeric parent and folds it in for reachability purposes;
this slicer treats 3b/5b/9b as INDEPENDENT tokens, because the PR-C brief
requires each to land in >=1 suite on its own
(docs/best-practices/ci-gate-audit.md § "Suite dispatcher"). The two parsers
answering different questions is intentional, not a drift risk — neither
reads the other's output.

DEPENDENCY CLOSURE: a handful of gate blocks share a bash function or an
ALL-CAPS variable with a *different* gate's block (measured on the live file,
2026-09: DASH_HTML/IDX_HTML from Gate 13 feed several later portal/streams
render-test gates; ORCH14 from Gate 14 feeds Gate 15 and Gate 28; DECP from
Gate 24 feeds Gate 25; WFDIR from Gate 146 feeds Gates 147-149). A suite
request that includes the consumer but not the definer would `source` a block
that references an unset function/variable. So selection is a FIXPOINT
closure: any block defining a function or a single-def-block ALL-CAPS
variable referenced by an already-selected block is pulled in too — even if
that block's own gate number is not nominally part of the requested suite.
This is a runtime-correctness mechanism, distinct from (and never a
substitute for) the suite MEMBERSHIP table in audit-gates.sh, which is what
the union-completeness meta-test (Gate 267) reads.

Usage:
    python3 scripts/audit-gates-suite-slice.py <path-to-audit-gates.sh> <token> [<token> ...]

Prints, to stdout: the selected (+ closure) blocks in ORIGINAL FILE ORDER,
verbatim, followed by the closing summary block, verbatim. Prints nothing
else — the caller is expected to `source` the result directly. Exits 2 on any
parse ambiguity (fail-closed: never emit a partial or guessed slice).
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

SUPPORTED_RE = re.compile(r"Supported:\s*\d")
# A real header PRINTS the banner; a comment merely mentioning one does not.
# (One such comment exists today, describing a historical grouped-header bug
# — matching it as a live header would silently over-select.)
HEADER_SINGLE_RE = re.compile(r'^\s*echo\s+"─{2,}\s*Gate\s+(\d+[a-z]?)\s*:')
HEADER_RANGE_RE = re.compile(r'^\s*echo\s+"─{2,}\s*Gates\s+(\d+)\s*[–—-]\s*(\d+)\s*:')
FUNC_DEF_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\(\)\s*\{")
# Real cross-cutting vars in this file are ALL-CAPS by convention; scratch/loop
# vars (rc, status, i, tmp, ...) are lowercase and are exactly what this
# uppercase-only filter is designed to exclude — see the module docstring.
VAR_ASSIGN_RE = re.compile(r"(?:^|[;{(]|\blocal\s+|\bexport\s+)\s*([A-Z_][A-Z0-9_]*)=")


class Ambiguity(Exception):
    """The file could not be parsed with confidence. Always fail-closed."""


def _find_regions(lines: list[str]) -> tuple[int, int]:
    """Return (gate_region_start, summary_start) as 0-based line indices.

    gate_region_start is the line right after the --check dispatcher's
    closing `fi`. summary_start is the line where the closing "N pass, N
    fail, N skipped" banner begins (identified by the double-line box-drawing
    char U+2550, "═", which the gate HEADERS never use — they use U+2500,
    "─" — so the two can never be confused).
    """
    supported_idx = next((i for i, ln in enumerate(lines) if SUPPORTED_RE.search(ln)), None)
    if supported_idx is None:
        raise Ambiguity("no `Supported:` line — cannot locate the --check dispatcher")
    esac = next((i for i in range(supported_idx, len(lines)) if lines[i].strip() == "esac"), None)
    if esac is None:
        raise Ambiguity("no `esac` after `Supported:` — dispatcher never closes")
    close = next((i for i in range(esac, len(lines)) if lines[i].strip() == "fi"), None)
    if close is None:
        raise Ambiguity("no `fi` after the dispatcher `esac` — cannot split the regions")

    gate_region_start = close + 1
    box_idx = next((i for i in range(gate_region_start, len(lines)) if "═" in lines[i]), None)
    if box_idx is None:
        raise Ambiguity("no closing summary banner (no line containing '═') found")
    summary_start = box_idx
    if lines[box_idx - 1].strip() == "echo":
        summary_start = box_idx - 1
    if summary_start <= gate_region_start:
        raise Ambiguity("summary banner appears before the gate region even starts")
    return gate_region_start, summary_start


class Block:
    __slots__ = ("tokens", "start", "end")

    def __init__(self, tokens: list[str], start: int, end: int) -> None:
        self.tokens = tokens
        self.start = start
        self.end = end


def _parse_blocks(lines: list[str], region_start: int, region_end: int) -> list[Block]:
    header_lines: list[tuple[int, list[str]]] = []
    for i in range(region_start, region_end):
        line = lines[i]
        mr = HEADER_RANGE_RE.match(line)
        if mr:
            lo, hi = int(mr.group(1)), int(mr.group(2))
            if lo > hi:
                raise Ambiguity(f"line {i + 1}: grouped header has lo > hi ({lo}-{hi})")
            header_lines.append((i, [str(n) for n in range(lo, hi + 1)]))
            continue
        ms = HEADER_SINGLE_RE.match(line)
        if ms:
            header_lines.append((i, [ms.group(1)]))
    if not header_lines:
        raise Ambiguity("no gate headers found in the gate region")

    blocks: list[Block] = []
    for idx, (start, tokens) in enumerate(header_lines):
        end = header_lines[idx + 1][0] if idx + 1 < len(header_lines) else region_end
        blocks.append(Block(tokens, start, end))
    return blocks


def _closure(
    lines: list[str],
    blocks: list[Block],
    selected: set[int],
) -> set[int]:
    """Fixpoint: pull in any block that DEFINES a function/var referenced by
    an already-selected block, even if that block's own tokens are not in the
    requested set. See the module docstring's "DEPENDENCY CLOSURE" section.
    """
    func_def_block: dict[str, int] = {}
    var_def_blocks: dict[str, set[int]] = {}
    for bi, block in enumerate(blocks):
        for i in range(block.start, block.end):
            line = lines[i]
            fm = FUNC_DEF_RE.match(line)
            if fm:
                func_def_block[fm.group(1)] = bi
            if line.lstrip().startswith("#"):
                continue
            for vm in VAR_ASSIGN_RE.finditer(line):
                var_def_blocks.setdefault(vm.group(1), set()).add(bi)
    single_def_vars = {
        name: next(iter(bset)) for name, bset in var_def_blocks.items() if len(bset) == 1
    }

    func_pattern = {
        name: re.compile(r"(?<![A-Za-z0-9_])" + re.escape(name) + r"(?![A-Za-z0-9_])")
        for name in func_def_block
    }
    var_pattern = {name: re.compile(r"\$\{?" + re.escape(name) + r"\b") for name in single_def_vars}

    selected = set(selected)
    changed = True
    while changed:
        changed = False
        for bi in list(selected):
            block = blocks[bi]
            for i in range(block.start, block.end):
                line = lines[i]
                for name, def_bi in func_def_block.items():
                    if def_bi not in selected and func_pattern[name].search(line):
                        selected.add(def_bi)
                        changed = True
                for name, def_bi in single_def_vars.items():
                    if def_bi not in selected and var_pattern[name].search(line):
                        selected.add(def_bi)
                        changed = True
    return selected


def slice_suite(path: Path, tokens: set[str]) -> str:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    region_start, summary_start = _find_regions(lines)
    blocks = _parse_blocks(lines, region_start, summary_start)

    selected = {bi for bi, b in enumerate(blocks) if set(b.tokens) & tokens}
    if not selected:
        raise Ambiguity(f"no gate block matches any requested token: {sorted(tokens)}")
    selected = _closure(lines, blocks, selected)

    out: list[str] = []
    for bi in sorted(selected):
        block = blocks[bi]
        out.extend(lines[block.start : block.end])
    out.extend(lines[summary_start : len(lines)])
    sliced = "\n".join(out) + "\n"

    # Defense in depth: a gate block can, in principle, open a bash control
    # structure (`if`/`for`/`while`/`case`) that a DIFFERENT block closes (this
    # happened once for real — Gate 49/50, fixed by removing the spanning
    # wrapper at its source — see the module docstring). The function/variable
    # closure above cannot see that class of dependency at all (it is not a
    # name reference), so rather than trying to enumerate every way two blocks
    # could be control-flow-coupled, verify the ACTUAL OUTPUT parses as valid
    # bash before handing it back. A silently-broken slice is strictly worse
    # than a loud one: `bash -n` catches it here, in the specific tool that
    # produced it, instead of as an opaque "unexpected end of file" several
    # layers away inside `source`.
    with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False, encoding="utf-8") as tmp:
        tmp.write(sliced)
        tmp_path = tmp.name
    try:
        proc = subprocess.run(["bash", "-n", tmp_path], capture_output=True, text=True)
    finally:
        Path(tmp_path).unlink(missing_ok=True)
    if proc.returncode != 0:
        raise Ambiguity(
            "the sliced output is not syntactically valid bash — a selected block "
            "likely opens or closes a control structure that spans a block "
            f"boundary this slicer's closure cannot see. `bash -n` said: {proc.stderr.strip()}"
        )
    return sliced


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(
            "usage: audit-gates-suite-slice.py <path-to-audit-gates.sh> <token> [<token> ...]",
            file=sys.stderr,
        )
        return 2
    path = Path(argv[1])
    tokens = set(argv[2:])
    try:
        sys.stdout.write(slice_suite(path, tokens))
    except Ambiguity as exc:
        print(f"audit-gates-suite-slice: FAIL-CLOSED - {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"audit-gates-suite-slice: cannot read {path}: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
