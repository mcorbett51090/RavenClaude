#!/usr/bin/env python3
"""Gate-introspection meta-gate: audit `scripts/audit-gates.sh` itself.

The audit suite is the instrument every other gate is measured with, and nothing
measured the instrument. Three defect classes shipped green because of that:

  * REACHABILITY - a gate registered only inside the `--check <n>` dispatcher arm
    never runs in the full suite. Gate 184 was unreachable for an entire release
    while the suite printed "all gates audited and verified bidirectional".
  * NUMBER COLLISION - two gates hand-assigned the same number (the two-Gate-104
    collision). Numbers are assigned by reading the current max, so a stale read
    silently overwrites a neighbour's identity.
  * EXIT-2 SPECIFICITY - a gate that drives a PreToolUse hook and asserts only
    `must_fail` (any nonzero) passes on a hook that exits 1. Claude Code treats
    exit 1 as a NON-BLOCKING error and runs the command anyway, so such a gate
    reports green over a guard that does not actually guard.

This checker is a static reader. It executes nothing and mutates nothing, so it
has no deny surface of its own (self-non-recursion is structural, not asserted).

Exit codes:  0 = clean;  2 = a finding OR a parse ambiguity (fail-closed).
Exit 1 is never used for a finding - a non-blocking exit is the very defect this
file exists to catch.

Usage:
    python3 scripts/check-gate-registration.py [path/to/audit-gates.sh]
    python3 scripts/check-gate-registration.py --self-test
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

# ── Syntax of the surfaces we parse ──────────────────────────────────────────
# Headers are box-drawing rules: "── Gate 42: description ──".  Two forms exist
# in the live suite and BOTH are legitimate registrations (measured, not assumed):
#   singular  "── Gate 126: ..."      - one gate
#   grouped   "── Gates 120–125: ..." - a contiguous run sharing one header
# Letter-suffixed sub-gates ("── Gate 3b:") are deliberately NOT gate numbers;
# they are sub-sections of their parent and carry no independent registration.
HEADER_RE = re.compile(r"─{2,}\s*Gate\s+(\d+)\s*:")
GROUP_HEADER_RE = re.compile(r"─{2,}\s*Gates\s+(\d+)\s*[–—-]\s*(\d+)\s*:")
ANY_HEADER_RE = re.compile(r"─{2,}\s*Gates?\s+\d+")

# An assertion. `gate <name> <direction> <observed>` is the suite's only verdict
# primitive; `_skip_or_fail` is its loud-skip counterpart (also a real outcome).
GATE_CALL_RE = re.compile(r"^\s*gate\s+\"")
SKIP_CALL_RE = re.compile(r"^\s*_skip_or_fail\s+")
GATE_CALL_TEXT_RE = re.compile(r"^\s*gate\s+\"(.*?)\"")
NAMED_GATE_RE = re.compile(r"\bGate\s+(\d+)\b")

# The dispatcher: `case` arms are bare `<n>)` lines; the `*)` arm prints the
# canonical `Supported:` list.  These two are independently hand-maintained and
# MUST agree - each is the other's oracle (never a constant).
CASE_ARM_RE = re.compile(r"^\s+(\d+)\)\s*$")
SUPPORTED_RE = re.compile(r"Supported:\s*\d")

# Hook-invocation detection. The question is behavioural - "is this hook
# EXECUTED here?" - not "does a hook path appear here?". Matching the path alone
# produced two false positives in calibration (`bash -n <hookpath>` syntax-checks
# it, `test -x <hookpath>` stats it; neither runs it), so command position is
# what we test.
HOOK_PATH_ANYWHERE_RE = re.compile(r"hooks/[A-Za-z0-9_.-]+\.sh")
HOOK_IN_CMD_POS_RE = re.compile(r"^\S*hooks/[A-Za-z0-9_.-]+\.sh\b")
ENV_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=(?:\"[^\"]*\"|'[^']*'|\S*)\s+")
INTERPRETER_RE = re.compile(r"^(?:sh|bash|zsh)\s+(?!-)")
# `name() {` at the start of a stripped line. Used to close assertion-reachability
# over helper functions (Gate 30's assert_hook_fires / assert_hook_silent).
FUNC_DEF_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\(\)\s*\{")
FUNC_NAME_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\b")
RC_CAPTURE_RE = re.compile(r"\|\|\s*([A-Za-z_][A-Za-z0-9_]*)=\$\?")
MUST_FAIL_RE = re.compile(r"^\s*gate\s+\".*?\"\s+must_fail\s+\"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?\"")
EXIT_TWO_RE = re.compile(r"-eq\s+2\b")


class Ambiguity(Exception):
    """The file could not be parsed with confidence. Always fail-closed."""


class Finding(NamedTuple):
    kind: str
    gate: str
    line: int
    detail: str

    def render(self) -> str:
        return f"  [{self.kind}] Gate {self.gate} (line {self.line}): {self.detail}"


class Suite(NamedTuple):
    lines: list[str]
    close: int  # 0-based index of the `fi` that closes the --check dispatcher
    case_arms: dict[int, int]  # gate number -> 1-based line
    supported: list[int]


def _strip_to_command(segment: str) -> str:
    """Reduce one pipeline/sequencer segment to whatever sits in command position."""
    s = segment.strip()
    while True:
        m = ENV_ASSIGN_RE.match(s)
        if not m:
            break
        s = s[m.end():]
    m = INTERPRETER_RE.match(s)
    if m:
        s = s[m.end():]
    return s.lstrip("\"'")


def is_hook_invocation(line: str) -> bool:
    """True iff a `hooks/*.sh` script is EXECUTED on this line.

    A hook path handed to another program as an argument (`bash -n`, `test -x`,
    `chmod`, `cp`, `backup`) is not an invocation; asserting exit 2 there would
    be meaningless and would flood the suite.
    """
    if not HOOK_PATH_ANYWHERE_RE.search(line):
        return False
    for segment in re.split(r"\|\||&&|[;|]", line):
        cmd = _strip_to_command(segment)
        if cmd and HOOK_IN_CMD_POS_RE.search(cmd):
            return True
    return False


def _parse_functions(lines: list[str]) -> dict[str, tuple[int, int]]:
    """name -> [start, end) line indices of each `name() { ... }` body."""
    out: dict[str, tuple[int, int]] = {}
    i = 0
    n = len(lines)
    while i < n:
        m = FUNC_DEF_RE.match(lines[i].lstrip())
        if not m:
            i += 1
            continue
        name = m.group(1)
        depth = lines[i].count("{") - lines[i].count("}")
        start = i
        i += 1
        while i < n and depth > 0:
            depth += lines[i].count("{") - lines[i].count("}")
            i += 1
        out[name] = (start, i)
    return out


def _cmd_pos_func_calls(line: str, func_names: set[str]) -> set[str]:
    """Functions invoked in command position on this line — never a definition
    and never a name mentioned in a comment or string-only occurrence.

    A naive name match would re-green a block that DEFINES an assertion-bearing
    helper and never calls it (the same accident-of-layout Gate 30 is green
    today). Call-site, not mention. Same doctrine as is_hook_invocation.
    """
    stripped = line.lstrip()
    if not stripped or stripped.startswith("#") or FUNC_DEF_RE.match(stripped):
        return set()
    found: set[str] = set()
    for segment in re.split(r"\|\||&&|[;|]", line):
        cmd = _strip_to_command(segment)
        m = FUNC_NAME_RE.match(cmd)
        if m and m.group(1) in func_names:
            found.add(m.group(1))
    return found


def _line_is_assertion(line: str) -> bool:
    return bool(GATE_CALL_RE.match(line) or SKIP_CALL_RE.match(line))


def _asserting_functions(lines: list[str], funcs: dict[str, tuple[int, int]]) -> set[str]:
    """Fixpoint: a function asserts if its body contains a gate/_skip_or_fail
    call, or a command-position call to a function that asserts."""
    names = set(funcs)
    asserting = {
        name
        for name, (start, end) in funcs.items()
        if any(_line_is_assertion(lines[j]) for j in range(start, end))
    }
    changed = True
    while changed:
        changed = False
        for name, (start, end) in funcs.items():
            if name in asserting:
                continue
            for j in range(start, end):
                if _cmd_pos_func_calls(lines[j], names) & asserting:
                    asserting.add(name)
                    changed = True
                    break
    return asserting


def _block_asserts(
    lines: list[str],
    start: int,
    end: int,
    funcs: dict[str, tuple[int, int]],
    asserting: set[str],
) -> bool:
    """True iff this header block actually fires an assertion.

    Direct `gate` / `_skip_or_fail` OR a command-position call to a function
    whose body (transitively) contains one. Defining such a helper without
    calling it does not count — that is the false-green a name match would
    restore. Measured: Gate 30's 28 assertions all arrive via assert_hook_fires
    / assert_hook_silent; those two defs sitting inside the block is an
    accident of layout, not a detection (hoisting them currently false-REDs).
    """
    names = set(funcs)
    for j in range(start, end):
        # A `gate` call inside a helper body is the helper asserting, not the
        # block. Counting it here is what made Gate 30 look reachable by
        # accident-of-layout, and what would false-green a define-but-never-call
        # block.
        if any(s <= j < e for s, e in funcs.values()):
            continue
        if _line_is_assertion(lines[j]):
            return True
        if _cmd_pos_func_calls(lines[j], names) & asserting:
            return True
    return False


def parse(path: Path) -> Suite:
    """Split the suite into its dispatcher and full-suite regions.

    Every landmark is required. A missing one means the file's shape changed and
    this checker can no longer reason about it - which is a hard failure, never a
    silent pass.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise Ambiguity(f"cannot read {path}: {exc}") from exc
    lines = text.splitlines()

    supported_idx = next((i for i, ln in enumerate(lines) if SUPPORTED_RE.search(ln)), None)
    if supported_idx is None:
        raise Ambiguity("no `Supported:` line found - cannot locate the --check dispatcher")
    esac = next((i for i in range(supported_idx, len(lines)) if lines[i].strip() == "esac"), None)
    if esac is None:
        raise Ambiguity("no `esac` after the `Supported:` line - dispatcher never closes")
    close = next((i for i in range(esac, len(lines)) if lines[i].strip() == "fi"), None)
    if close is None:
        raise Ambiguity("no `fi` after the dispatcher `esac` - cannot split the regions")

    case_arms: dict[int, int] = {}
    for i in range(0, esac):
        m = CASE_ARM_RE.match(lines[i])
        if m:
            case_arms[int(m.group(1))] = i + 1

    # The list runs from "Supported:" to the first sentence break. Stopping there
    # matters: the line ends `... full suite." >&2`, and a naive digit sweep reads
    # the `>&2` redirect as gate number 2.
    tail = lines[supported_idx].split("Supported:", 1)[1].split(". ", 1)[0]
    supported = [int(n) for n in re.findall(r"\d+", tail)]
    if not supported:
        raise Ambiguity("the `Supported:` line lists no gate numbers")

    return Suite(lines=lines, close=close, case_arms=case_arms, supported=supported)


def _full_suite_blocks(suite: Suite) -> list[tuple[str, list[int], int, int]]:
    """Every header block after the dispatcher: (label, covered numbers, start, end)."""
    starts: list[tuple[int, str, list[int]]] = []
    for i in range(suite.close + 1, len(suite.lines)):
        line = suite.lines[i]
        grouped = GROUP_HEADER_RE.search(line)
        if grouped:
            lo, hi = int(grouped.group(1)), int(grouped.group(2))
            if lo <= hi:
                starts.append((i, f"{lo}-{hi}", list(range(lo, hi + 1))))
                continue
        single = HEADER_RE.search(line)
        if single:
            starts.append((i, single.group(1), [int(single.group(1))]))
            continue
        # A header-shaped line we could not classify is an ambiguity, not a skip.
        if ANY_HEADER_RE.search(line) and not re.search(r"Gate\s+\d+[a-z]", line):
            if not HEADER_RE.search(line) and not GROUP_HEADER_RE.search(line):
                # Tolerated annotated forms ("── Gate 190 teeth:") always carry a
                # plain header elsewhere; they open no new block.
                continue

    blocks = []
    for idx, (start, label, nums) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(suite.lines)
        blocks.append((label, nums, start, end))
    return blocks


def audit(path: Path) -> list[Finding]:
    suite = parse(path)
    lines = suite.lines
    findings: list[Finding] = []
    blocks = _full_suite_blocks(suite)

    # ── Surface parity: dispatcher case arms vs the `Supported:` string ───────
    # Two hand-maintained surfaces that must describe the same set. Each is the
    # other's oracle; neither is compared against a constant.
    arms = set(suite.case_arms)
    listed = set(suite.supported)
    for n in sorted(arms - listed):
        findings.append(
            Finding(
                "supported-parity",
                str(n),
                suite.case_arms[n],
                "has a --check dispatcher arm but is absent from the `Supported:` list",
            )
        )
    for n in sorted(listed - arms):
        findings.append(
            Finding(
                "supported-parity",
                str(n),
                0,
                "is advertised in the `Supported:` list but has no --check dispatcher arm",
            )
        )

    # ── Reachability (P2) ────────────────────────────────────────────────────
    # A number is reachable when the full-suite region actually asserts it. Three
    # registration shapes are legitimate and all three are honoured, because the
    # live suite uses all three (calibrated against the real file, not assumed).
    funcs = _parse_functions(lines)
    asserting_funcs = _asserting_functions(lines, funcs)
    reachable: set[int] = set()
    for _label, nums, start, end in blocks:
        asserts = _block_asserts(lines, start, end, funcs, asserting_funcs)
        if asserts:
            reachable.update(nums)
        for j in range(start, end):
            m = GATE_CALL_TEXT_RE.match(lines[j])
            if m:
                # A gate call naming "Gate 127" registers 127 even under a
                # neighbouring header (the live shape for the pseudonymize gate).
                reachable.update(int(g) for g in NAMED_GATE_RE.findall(m.group(1)))

    declared: set[int] = set(arms) | listed
    for line in lines:
        m = HEADER_RE.search(line)
        if m:
            declared.add(int(m.group(1)))
        g = GROUP_HEADER_RE.search(line)
        if g and int(g.group(1)) <= int(g.group(2)):
            declared.update(range(int(g.group(1)), int(g.group(2)) + 1))

    for n in sorted(declared - reachable):
        where = suite.case_arms.get(n, 0)
        findings.append(
            Finding(
                "unreachable",
                str(n),
                where,
                "is declared but never asserted in the full-suite region - it runs "
                "only under `--check`, so the full suite reports green without it",
            )
        )

    # ── Number uniqueness (P3), keyed on REGION ──────────────────────────────
    # 94 of the 150 numbers legitimately echo their header in BOTH the dispatcher
    # and the full-suite region, so a naive "same number twice" rule floods on
    # day one. Only a repeat WITHIN the full-suite region is a collision.
    seen: dict[int, int] = {}
    for i in range(suite.close + 1, len(lines)):
        m = HEADER_RE.search(lines[i])
        if not m:
            continue
        n = int(m.group(1))
        if n in seen:
            findings.append(
                Finding(
                    "number-collision",
                    str(n),
                    i + 1,
                    f"a second full-suite header for this number (first at line {seen[n]}) - "
                    "two gates share one identity",
                )
            )
        else:
            seen[n] = i + 1

    # ── Exit-2 specificity (P5) ──────────────────────────────────────────────
    # Scoped to the hook-INVOCATION signature, never to a gate NAME containing
    # "blocks"/"deny": most such gates assert an internal decision string, where
    # "exit 2" is meaningless. Only a real hook execution whose result is asserted
    # `must_fail` needs the exit-2 companion.
    for label, _nums, start, end in blocks:
        pending: list[list] = []
        for j in range(start, end):
            line = lines[j]
            if is_hook_invocation(line):
                capture = RC_CAPTURE_RE.search(line)
                if capture:
                    pending.append([capture.group(1), j, False, False])
                continue
            mf = MUST_FAIL_RE.match(line)
            if mf and pending and pending[-1][0] == mf.group(1):
                pending[-1][2] = True
            if pending and EXIT_TWO_RE.search(line) and pending[-1][0] in line:
                pending[-1][3] = True
        for var, j, saw_must_fail, saw_exit_two in pending:
            if saw_must_fail and not saw_exit_two:
                findings.append(
                    Finding(
                        "exit-2-unasserted",
                        label,
                        j + 1,
                        f"drives a PreToolUse hook and asserts `must_fail \"${var}\"` (any "
                        "nonzero) without asserting the deny is exit 2 - a hook that exits 1 "
                        "is non-blocking and would pass this gate",
                    )
                )

    return findings


# ── Teeth ────────────────────────────────────────────────────────────────────
# Each mutant must be CAUGHT; each companion must stay CLEAN. The companions are
# the half that matters most here: a checker that flags everything is as useless
# as one that flags nothing, and would get this keystone switched off.


def _hoist_gate30_helpers(lines: list[str]) -> list[str]:
    """Move assert_hook_fires + assert_hook_silent above the Gate 30 header.

    Behaviour-preserving: the two helpers still exist, the 28 call sites still
    sit under the header. Only the accident-of-layout (defs inside the block)
    is removed.
    """
    funcs = _parse_functions(lines)
    if "assert_hook_fires" not in funcs or "assert_hook_silent" not in funcs:
        raise Ambiguity("Gate 30 helpers missing - hoist fixture cannot be built")
    s1, e1 = funcs["assert_hook_fires"]
    s2, e2 = funcs["assert_hook_silent"]
    lo, hi = (s1, e2) if s1 < s2 else (s2, e1)
    header_i = next(
        (
            i
            for i, ln in enumerate(lines)
            if (m := HEADER_RE.search(ln)) and m.group(1) == "30"
        ),
        None,
    )
    if header_i is None:
        raise Ambiguity("no Gate 30 header - hoist fixture cannot be built")
    if lo <= header_i:
        raise Ambiguity("Gate 30 helpers are already above the header")
    chunk = lines[lo:hi]
    without = lines[:lo] + lines[hi:]
    return without[:header_i] + chunk + [""] + without[header_i:]


def _extend_supported(lines: list[str], extra: str) -> list[str]:
    """Append gate numbers to the `Supported:` list.

    Derived, never hardcoded: the fixture must not encode today's highest gate
    number, or it silently stops patching the moment a gate is added - which is
    the build-to-a-guessed-contract defect this checker exists to catch. (It bit
    this very fixture when Gates 195/196 were registered.)
    """
    return [re.sub(r"(\d+)\.(\s+Run without)", rf"\1, {extra}.\2", ln) for ln in lines]


def _mutants(src: Path, work: Path) -> list[tuple[str, Path, str]]:
    """(name, path, expected finding kind) - each must be caught."""
    base = src.read_text(encoding="utf-8")
    lines = base.splitlines()
    out = []

    esac = max(i for i, ln in enumerate(lines) if ln.strip() == "esac" and i < len(lines) // 2)
    star = next(i for i in range(esac, 0, -1) if lines[i].strip() == "*)")

    # M1 - a gate pasted INSIDE the dispatcher only (the Gate 184 shape).
    m1 = lines[:star] + [
        "    901)",
        '      echo "── Gate 901: pasted inside the dispatcher ──"',
        '      gate "orphan" must_pass "0"',
        "      exit $?",
        "      ;;",
    ] + lines[star:]
    m1 = _extend_supported(m1, "901")
    p1 = work / "m1-unreachable.sh"
    p1.write_text("\n".join(m1) + "\n", encoding="utf-8")
    out.append(("gate reachable only from the dispatcher", p1, "unreachable"))

    # M2 - two full-suite headers sharing one number (the two-Gate-104 collision).
    dup_target = None
    for i in range(len(lines) - 1, 0, -1):
        m = HEADER_RE.search(lines[i])
        if m:
            dup_target = (i, m.group(1))
            break
    assert dup_target is not None
    di, dnum = dup_target
    m2 = lines[:di] + [
        f'echo "── Gate {dnum}: a colliding second registration ──"',
        'gate "collides" must_pass "0"',
    ] + lines[di:]
    p2 = work / "m2-collision.sh"
    p2.write_text("\n".join(m2) + "\n", encoding="utf-8")
    out.append(("two full-suite headers on one number", p2, "number-collision"))

    # M3 - a hook driven and asserted must_fail with no exit-2 companion.
    m3 = base + (
        '\necho "── Gate 902: synthetic hook deny ──"\n'
        "rc=0; printf '%s' '{}' | plugins/ravenclaude-core/hooks/guard-destructive.sh || rc=$?\n"
        'gate "synthetic deny" must_fail "$rc"\n'
    )
    p3 = work / "m3-exit2.sh"
    p3.write_text(m3, encoding="utf-8")
    out.append(("hook deny asserted without exit 2", p3, "exit-2-unasserted"))

    # M4 - a dispatcher arm that never made it into the Supported: list.
    m4 = lines[:star] + ["    903)", '      echo "x"', "      exit $?", "      ;;"] + lines[star:]
    p4 = work / "m4-parity.sh"
    p4.write_text("\n".join(m4) + "\n", encoding="utf-8")
    out.append(("dispatcher arm missing from Supported:", p4, "supported-parity"))

    # M5 - a block that DEFINES an assertion-bearing helper and never calls it.
    # A name-match closure would mark this reachable (false green). Call-site
    # closure must still say unreachable.
    m5 = base + (
        '\necho "── Gate 908: defines an assertion helper and never calls it ──"\n'
        "never_called_assert() {\n"
        '  gate "inside helper" must_pass "0"\n'
        "}\n"
    )
    p5 = work / "m5-define-only.sh"
    p5.write_text(m5, encoding="utf-8")
    out.append(("block defines assertion helper and never calls it", p5, "unreachable"))

    return out


def _companions(src: Path, work: Path) -> list[tuple[str, Path]]:
    """(name, path) - each must produce NO findings (anti-flood)."""
    base = src.read_text(encoding="utf-8")
    out = [("the live, unmodified suite", src)]

    # C1 - a hook path handed to another program as an ARGUMENT. This is the
    # Gate 3 / Gate 4 shape; demanding exit 2 of a syntax check is nonsense.
    c1 = base + (
        '\necho "── Gate 904: hook path as an argument ──"\n'
        "rc=0; bash -n plugins/ravenclaude-core/hooks/guard-destructive.sh || rc=$?\n"
        'gate "syntax" must_fail "$rc"\n'
        "rc=0; test -x plugins/ravenclaude-core/hooks/guard-destructive.sh || rc=$?\n"
        'gate "exec bit" must_fail "$rc"\n'
    )
    p1 = work / "c1-path-as-arg.sh"
    p1.write_text(c1, encoding="utf-8")
    out.append(("hook path as an argument, not an invocation", p1))

    # C2 - a gate whose name says "blocks" but which asserts an internal decision
    # string, not a hook exit. 49 live gates have this shape.
    c2 = base + (
        '\necho "── Gate 905: internal decision engine ──"\n'
        'rc=0; python3 scripts/nonexistent.py --verdict deny | grep -q "deny" || rc=$?\n'
        'gate "tribunal blocks a high-blast command" must_fail "$rc"\n'
    )
    p2 = work / "c2-internal-decision.sh"
    p2.write_text(c2, encoding="utf-8")
    out.append(('a "blocks"-named gate asserting a decision string', p2))

    # C3 - a contiguous run sharing one grouped header (the live 120-125 shape).
    lines = base.splitlines()
    esac = max(i for i, ln in enumerate(lines) if ln.strip() == "esac" and i < len(lines) // 2)
    star = next(i for i in range(esac, 0, -1) if lines[i].strip() == "*)")
    c3 = lines[:star]
    for n in (906, 907):
        c3 += [
            f"    {n})",
            f'      echo "── Gate {n}: grouped member (per-gate run) ──"',
            "      exit $?",
            "      ;;",
        ]
    c3 += lines[star:]
    c3 = _extend_supported(c3, "906, 907")
    c3 += [
        'echo "── Gates 906–907: a contiguous run under one header ──"',
        'gate "grouped member a" must_pass "0"',
        'gate "grouped member b" must_pass "0"',
    ]
    p3 = work / "c3-grouped.sh"
    p3.write_text("\n".join(c3) + "\n", encoding="utf-8")
    out.append(("a grouped-range header covering several numbers", p3))

    # C4 - Gate 30 helpers hoisted ABOVE the header. Pre-closure this is a
    # false RED (28 live assertions via assert_hook_fires/silent, defs no
    # longer inside the block). Post-closure it must stay clean.
    c4_lines = _hoist_gate30_helpers(base.splitlines())
    p4 = work / "c4-hoist-gate30.sh"
    p4.write_text("\n".join(c4_lines) + "\n", encoding="utf-8")
    out.append(("Gate 30 helpers hoisted above the header (still 28 calls)", p4))

    return out


def self_test(src: Path) -> int:
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)

        for name, path, expected in _mutants(src, work):
            found = audit(path)
            kinds = {f.kind for f in found}
            if expected in kinds:
                print(f"  ✓ caught: {name}")
            else:
                ok = False
                print(f"  ✗ MISSED: {name} (expected '{expected}', got {sorted(kinds)})")

        for name, path in _companions(src, work):
            found = audit(path)
            if not found:
                print(f"  ✓ clean:  {name}")
            else:
                ok = False
                print(f"  ✗ FLOODED on: {name}")
                for f in found:
                    print(f.render())

        # A file this checker cannot parse must fail CLOSED, never pass silently.
        broken = work / "unparseable.sh"
        broken.write_text("#!/usr/bin/env bash\necho hello\n", encoding="utf-8")
        try:
            audit(broken)
            ok = False
            print("  ✗ MISSED: an unparseable suite was accepted instead of failing closed")
        except Ambiguity:
            print("  ✓ caught: an unparseable suite fails closed")

    print("\nteeth verified" if ok else "\nTEETH BROKEN")
    return 0 if ok else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?", default="scripts/audit-gates.sh")
    ap.add_argument(
        "--self-test",
        action="store_true",
        help="prove the checker's teeth: every mutant caught, every companion clean",
    )
    args = ap.parse_args()

    src = Path(args.path)
    if args.self_test:
        return self_test(src)

    try:
        findings = audit(src)
    except Ambiguity as exc:
        print(f"check-gate-registration: FAIL-CLOSED - {exc}", file=sys.stderr)
        return 2

    if findings:
        print(f"check-gate-registration: {len(findings)} finding(s) in {src}", file=sys.stderr)
        for f in findings:
            print(f.render(), file=sys.stderr)
        return 2

    print(f"check-gate-registration: {src} clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
