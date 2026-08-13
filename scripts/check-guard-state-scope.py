#!/usr/bin/env python3
"""Every stateful PreToolUse guard must DECLARE what its state is keyed on.

## The defect this closes (P9)

A guard that records a decision and replays it later has a key. If that key is
coarser than the resource the decision is *about*, one agent's negative silently
denies an unrelated sibling. That is not hypothetical: the premise ledger was
keyed on `(project, session_id)`, and a measured 6-agent parallel run put 2,825
entries with 50 unresolved negative families into ONE file spanning 49 distinct
`cwd` values across 15+ worktrees. A negative recorded in worktree A denied a new
module in worktree B, and the agent that hit it lost finished work rather than
tunnel the guard.

The second half is the escape. **A guardrail whose only exit is unreachable does
not get respected — it gets tunnelled.** `RC_PREMISE_CONTROL` was an environment
variable, and a variable exported inside a `Bash` call never reaches the hook
process, so a dispatched subagent that had genuinely run the control had no way
to say so. In the same measured run one agent wrote files through Bash heredocs
purely to dodge the `Write` hook.

## Why a DECLARATION and not an inference

Inferring the right key from the source is not decidable, and guessing produces
exactly the false finding this initiative exists to prevent. The scope is a
design fact only the author knows, so the author states it and the checker
verifies the *key matches the stated scope*. Three of the six live guards turn
out to be correctly session- or globally-keyed — a blanket "must vary per
worktree" rule would have been wrong about half the population.

## The contract

Any hook registered on `PreToolUse` that writes persistent state under
`.ravenclaude/runs/` MUST carry three markers in its header comment:

    # rc-state-key: <the expression the state path is keyed on>
    # rc-state-scope: worktree | project | session | global
    # rc-state-rationale: <why that key is right for what the guard decides>

`rc-state-scope` is checked against `rc-state-key`: a `worktree` scope whose key
never mentions `cwd` (or a cwd-derived digest) is the v0.245.0 collision, caught
statically. `global` is legal but must say why in the rationale — a global key is
correct when the protected resource is itself global (the memory directory is one
directory no matter how many worktrees read it).

A guard that can DENY must also expose a **file-based** escape, or declare
`rc-state-escape: none — <reason>`. An env-var-only escape is unreachable from a
subprocess and is recorded here as a finding, not a style note.

Exit codes:  0 = clean;  2 = a finding, or the contract could not be read.
Exit 1 is never used for a finding — the harness treats exit 1 as a
non-blocking error, which is a silent fail-open.

Usage:
    python3 scripts/check-guard-state-scope.py
    python3 scripts/check-guard-state-scope.py --discover     # report shape only, exit 0
    python3 scripts/check-guard-state-scope.py --self-test
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

HOOKS_JSON = Path("plugins/ravenclaude-core/hooks/hooks.json")

# A hook is "stateful" when it writes under the `.ravenclaude/` substrate. Reading
# it is not enough — a guard that only reads someone else's record has no key of
# its own.
#
# ⛔ THE SCOPE IS `.ravenclaude/`, NOT `.ravenclaude/runs/`. The first draft of
# this checker looked only under `runs/` and reported `worktree-guard.sh` as
# STATELESS — it keys a real per-session registry on sha256(git-toplevel) but
# stores it under `$HOME/.ravenclaude/worktree-guard/`. The narrow probe returned
# a clean-looking answer that was a claim about the probe, not the population.
# Any new substrate root must widen this pattern, not add a special case.
_SUBSTRATE = r"\.ravenclaude/"
STATE_WRITE = re.compile(
    r"""(?x)
    (?: mkdir \s+ -p | >> | > | tee | jq \s+ [^|]* > )  # a write verb
    [^\n]*  """
    + _SUBSTRATE
    + r"""
    |
    """
    + _SUBSTRATE
    + r""" [^\n]* (?: >> | \bmkdir\b )
    """
)
# Some hooks build the root into a variable first and write through the variable.
# Catching that needs TWO passes, not one pattern.
#
# ⛔ A ONE-PASS "assigned a .ravenclaude/ path" RULE IS WRONG, measured: it reported
# 10 of 11 PreToolUse hooks as stateful, up from 5. The extra five were all READS —
# `posture="$proj/.ravenclaude/comfort-posture.yaml"` and
# `task_scope="$root/.ravenclaude/task-scope.json"`. A guard that reads config has
# no state key and nothing to declare, so requiring one of it is a false finding.
# A near-uniform result across a population is a claim about the instrument.
_VAR_ASSIGN = re.compile(
    r"^\s*(?:local\s+|export\s+)?(_?[A-Za-z_][A-Za-z0-9_]*)="
    r"[\"']?[^\"'\n]*\.ravenclaude/",
    re.M,
)
# Every assignment, for the transitive pass below.
_ANY_ASSIGN = re.compile(
    r"^\s*(?:local\s+|export\s+)?(_?[A-Za-z_][A-Za-z0-9_]*)=(.*)$", re.M
)
# The write verbs that turn a path variable into persistent state.
#
# ⛔ EVERY BRANCH MUST PUT THE VARIABLE IN THE WRITE TARGET POSITION. A dropped
# fourth branch matched "$VAR anything >" and fired on
# `"…($mode) auto-resolved this yes/no prompt…"` — a `$var` in an English
# sentence with a `>` later on the line. It classified `route-decision-review.sh`
# (zero write lines) as stateful. A pattern that can match prose is not a
# measurement of behaviour.
_WRITE_THROUGH = (
    r"(?: mkdir \s+ -p \s+ [\"']? \$\{{?{v}\b"
    r"| >{{1,2}} \s* [\"']? \$\{{?{v}\b"
    r"| tee \s+ (?:-a\s+)? [\"']? \$\{{?{v}\b"
    r")"
)

MARK_KEY = re.compile(r"^#\s*rc-state-key:\s*(.+?)\s*$", re.M)
MARK_SCOPE = re.compile(r"^#\s*rc-state-scope:\s*([A-Za-z]+)\s*$", re.M)
MARK_RATIONALE = re.compile(r"^#\s*rc-state-rationale:\s*(.+?)\s*$", re.M)
MARK_ESCAPE = re.compile(r"^#\s*rc-state-escape:\s*(.+?)\s*$", re.M)

# What each declared scope REQUIRES the key expression to vary on. The point of
# the table is that it is checkable: a scope claim that the key cannot deliver is
# the collision, named at author time.
SCOPE_REQUIRES = {
    "worktree": (
        # PATH_KEY / toplevel are named because `worktree-guard.sh` keys on
        # sha256(git toplevel) — a genuine per-checkout component that mentions
        # neither `cwd` nor `worktree`. Omitting them would have forced an honest
        # declaration to be reworded to satisfy the checker, which is gaming.
        re.compile(
            r"\bcwd\b|worktree|PWD|\$\(pwd\)|scope_key|_rc_rel|slug|PATH_KEY|toplevel",
            re.I,
        ),
        "a cwd- or worktree-derived component",
    ),
    "project": (
        re.compile(r"CLAUDE_PROJECT_DIR|\bcwd\b|project"),
        "a project-root component",
    ),
    "session": (
        re.compile(r"session_id|CLAUDE_SESSION_ID|\bsid\b"),
        "a session component",
    ),
    "global": (re.compile(r".*", re.S), "nothing (global is deliberately unkeyed)"),
}

# A guard denies when it can emit a deny verdict or exit 2.
DENIES = re.compile(r"emit\s+deny|\"permissionDecision\"\s*:\s*\"deny\"|\bexit\s+2\b")
# A file-based escape reads a control FILE; an env-only escape reads a variable.
# ⛔ Both orders matter. The first draft required the control word to appear
# AFTER the `[ -f … ]` test, so `if [ -f "$control_md" ]` — the control word
# inside the tested variable's own NAME, which is how these are actually written
# — went unmatched and the good fixture was reported as an unreachable escape.
_CTRL = r"(?: control | override | escape | premise-ok | allow(?:list)? )"
FILE_ESCAPE = re.compile(
    r"""(?x)
      """
    + _CTRL
    + r""" [^\n]{0,80} (?: \.md | \.json | \.txt | -f\s | \[\s*-f | read_text | cat\s )
    | (?: \[\s*-f | -f\s | test\s+-f | read_text | \bcat\s ) [^\n]{0,80} """
    + _CTRL
    + r"""
    """,
    re.I,
)

# Hooks that are exempt from the whole contract, each with a STATED reason. An
# empty reason is a silenced finding, so the value is required and printed.
EXEMPT: dict[str, str] = {
    # (none today — every stateful PreToolUse guard carries its declaration.)
}


class Finding(NamedTuple):
    path: str
    rule: str
    detail: str


def _pretooluse_hooks(repo: Path) -> list[Path]:
    """Every script registered on PreToolUse, resolved to a real path."""
    data = json.loads((repo / HOOKS_JSON).read_text(encoding="utf-8"))
    out: list[Path] = []
    for entry in data.get("hooks", {}).get("PreToolUse", []):
        for hook in entry.get("hooks", []):
            cmd = hook.get("command", "")
            # The command may carry arguments ("worktree-guard.sh check"); the
            # script is the first token that ends in .sh.
            for tok in cmd.replace('"', " ").split():
                if tok.endswith(".sh"):
                    name = tok.split("/")[-1]
                    p = repo / "plugins/ravenclaude-core/hooks" / name
                    if p.is_file() and p not in out:
                        out.append(p)
                    break
    return out


def _strip_comments(src: str) -> str:
    """Blank out whole-line comments before the statefulness scan.

    ⛔ A comment is PROSE, and prose satisfies a source scan. `enforce-git-protocol.sh`
    was classified stateful purely because a header line reads "…comfort-posture.yaml
    (read with the same minimal-scalar…" — the `>`-free sentence still matched a write
    pattern through an adjacent construct. The hook writes nothing. This repo has been
    bitten by source-scan-matches-prose twice; strip first, then match.

    Marker comments are parsed from the RAW source, so blanking here cannot hide a
    declaration.
    """
    return "\n".join("" if ln.lstrip().startswith("#") else ln for ln in src.splitlines())


_READ_CONSTRUCTS = (
    r"(?: \[\s*-f\s+[\"']?\$\{{?{v}\b"
    r"| test\s+-f\s+[\"']?\$\{{?{v}\b"
    r"| <\s*[\"']?\$\{{?{v}\b"
    r"| (?: sed|grep|awk|cat|head|jq ) \s+ [^\n]*\$\{{?{v}\b"
    r")"
)


def _reads_control_file(src: str) -> bool:
    """True iff the hook READS a `.ravenclaude/`-rooted file it could be steered by.

    This is what corroborates a declared escape. It reuses the same substrate-variable
    resolution as the statefulness pass, so the two cannot disagree about what counts
    as a substrate path.
    """
    src = _strip_comments(src)
    for var in _substrate_vars(src):
        if re.search(_READ_CONSTRUCTS.format(v=re.escape(var)), src, re.X):
            return True
    return False


def _substrate_vars(src: str) -> set[str]:
    """Variables holding a `.ravenclaude/` path, resolved to a fixpoint."""
    substrate = set(_VAR_ASSIGN.findall(src))
    changed = True
    while changed:
        changed = False
        for m in _ANY_ASSIGN.finditer(src):
            name, value = m.group(1), m.group(2)
            if name in substrate or "/" not in value:
                continue
            if any(re.search(r"\$\{?" + re.escape(v) + r"\b", value) for v in substrate):
                substrate.add(name)
                changed = True
    return substrate


def _is_stateful(src: str) -> bool:
    """True iff the hook WRITES persistent state under `.ravenclaude/`.

    Reading config from that tree is not state — see the note on `_VAR_ASSIGN`.

    ⚑ SCOPE LIMIT, named rather than silently dropped: a guard that READS a record
    some other component writes (`guard-web-access.sh` reads `runs/<sess>/web-allow.txt`
    but never writes it) is correctly out of scope here — the key belongs to whoever
    writes it. If that writer is not itself a PreToolUse hook, no gate currently asks
    it to declare one. Widening discovery past PreToolUse is follow-up work.
    """
    src = _strip_comments(src)
    if STATE_WRITE.search(src):
        return True

    # Substrate variables, resolved to a FIXPOINT. One level is not enough:
    # `worktree-guard.sh` assigns GUARD_HOME=…/.ravenclaude/worktree-guard, then
    # SESS_DIR="$GUARD_HOME/sessions/$PATH_KEY", and writes through SESS_DIR. A
    # one-level check saw a literal-path variable that is never written and a
    # written variable with no literal path, and concluded "stateless" — for the
    # one hook whose keying this gate most wants to see.
    for var in _substrate_vars(src):
        if re.search(_WRITE_THROUGH.format(v=re.escape(var)), src, re.X):
            return True
    return False


def _check_one(path: Path, src: str) -> list[Finding]:
    rel = path.as_posix()
    name = path.name
    if name in EXEMPT:
        return []
    if not _is_stateful(src):
        return []

    found: list[Finding] = []
    m_key = MARK_KEY.search(src)
    m_scope = MARK_SCOPE.search(src)
    m_rat = MARK_RATIONALE.search(src)

    if not m_key or not m_scope or not m_rat:
        missing = [
            n
            for n, m in (
                ("rc-state-key", m_key),
                ("rc-state-scope", m_scope),
                ("rc-state-rationale", m_rat),
            )
            if not m
        ]
        found.append(
            Finding(
                rel,
                "undeclared-state",
                f"writes persistent state but declares no {', '.join(missing)}. "
                f"A guard whose key nobody stated is a guard nobody can check.",
            )
        )
        return found  # the rest of the checks need the declaration

    scope = m_scope.group(1).strip().lower()
    key = m_key.group(1)
    if scope not in SCOPE_REQUIRES:
        found.append(
            Finding(
                rel,
                "unknown-scope",
                f"rc-state-scope: {scope!r} is not one of "
                f"{sorted(SCOPE_REQUIRES)} — an unrecognised scope cannot be checked.",
            )
        )
        return found

    pattern, human = SCOPE_REQUIRES[scope]
    if scope != "global" and not pattern.search(key):
        found.append(
            Finding(
                rel,
                "key-coarser-than-scope",
                f"declares scope {scope!r} but its key ({key.strip()!r}) carries no "
                f"{human}. This is the v0.245.0 shape: one agent's record gates another.",
            )
        )

    if scope == "global" and len(m_rat.group(1).strip()) < 20:
        found.append(
            Finding(
                rel,
                "unjustified-global",
                "declares the global scope without a substantive rationale. A global "
                "key is correct only when the protected resource is itself global.",
            )
        )

    if DENIES.search(src):
        m_esc = MARK_ESCAPE.search(src)
        declared = m_esc.group(1).strip() if m_esc else ""
        declared_none = declared.lower().startswith("none")
        corroborated = _reads_control_file(src) or bool(FILE_ESCAPE.search(src))

        if declared_none:
            pass  # an explicit, reasoned "no exit by design" is a legitimate answer
        elif declared and not corroborated:
            # ⛔ A DECLARATION IS NOT EVIDENCE. Honouring the marker alone would let
            # any guard claim a file escape it does not implement — the same shape as
            # a comment quoting a config key and flipping a tracker item to DONE with
            # nothing actually bound.
            found.append(
                Finding(
                    rel,
                    "uncorroborated-escape",
                    f"declares the escape {declared!r} but nothing in the source reads "
                    f"a control file. Either implement the read or correct the marker.",
                )
            )
        elif not declared and not corroborated:
            found.append(
                Finding(
                    rel,
                    "unreachable-escape",
                    "can DENY but exposes no file-based escape. An env-var-only exit "
                    "never reaches the hook process from a subprocess, so it gets "
                    "tunnelled rather than used. Add a control file or declare "
                    "'# rc-state-escape: none — <reason>'.",
                )
            )
    return found


def scan(repo: Path) -> tuple[list[Finding], list[tuple[str, bool]]]:
    findings: list[Finding] = []
    shape: list[tuple[str, bool]] = []
    for p in _pretooluse_hooks(repo):
        src = p.read_text(encoding="utf-8", errors="replace")
        stateful = _is_stateful(src)
        shape.append((p.name, stateful))
        findings.extend(_check_one(p, src))
    return findings, shape


# --------------------------------------------------------------------------
# Self-test. Fixtures are assembled with printf-style concatenation so this
# file does not itself contain a literal undeclared-state hook — a source-scan
# gate matches its own fixtures, and that has bitten this repo twice.
# --------------------------------------------------------------------------

_RUNS = ".ravenclaude/" + "runs"
_W = "mkdir -p " + '"$cwd/' + _RUNS + '/thing"'


def _fixture(body: str) -> str:
    return "#!/usr/bin/env bash\nset -euo pipefail\n" + body + "\n"


def _self_test() -> int:
    cases: list[tuple[str, str, str | None]] = [
        (
            "good-worktree",
            _fixture(
                "# rc-state-key: cwd + scope digest\n"
                "# rc-state-scope: worktree\n"
                "# rc-state-rationale: the decision is about files in ONE worktree\n"
                + _W
                + '\nif [ -f "$control_md" ]; then :; fi\nemit deny "no"\n'
            ),
            None,
        ),
        (
            "missing-declaration",
            _fixture(_W),
            "undeclared-state",
        ),
        (
            "session-key-for-worktree-scope",
            _fixture(
                "# rc-state-key: session_id only\n"
                "# rc-state-scope: worktree\n"
                "# rc-state-rationale: stated but wrong\n" + _W
            ),
            "key-coarser-than-scope",
        ),
        (
            "env-only-escape",
            _fixture(
                "# rc-state-key: cwd\n"
                "# rc-state-scope: worktree\n"
                "# rc-state-rationale: per-worktree files\n"
                + _W
                + '\nemit deny "set RC_THING_OVERRIDE=1"\n'
            ),
            "unreachable-escape",
        ),
        (
            "declared-escape-none",
            _fixture(
                "# rc-state-key: cwd\n"
                "# rc-state-scope: worktree\n"
                "# rc-state-rationale: per-worktree files\n"
                "# rc-state-escape: none - a security deny has no user-side exit by design\n"
                + _W
                + '\nemit deny "no"\n'
            ),
            None,
        ),
        (
            # A marker is a claim, not an implementation. This is the fixture that
            # keeps the escape check from degrading into "did the author type a line".
            "uncorroborated-escape",
            _fixture(
                "# rc-state-key: cwd\n"
                "# rc-state-scope: worktree\n"
                "# rc-state-rationale: per-worktree files\n"
                "# rc-state-escape: a control file under the run dir\n"
                + _W
                + '\nemit deny "no"\n'
            ),
            "uncorroborated-escape",
        ),
        (
            "unjustified-global",
            _fixture(
                "# rc-state-key: HOME\n"
                "# rc-state-scope: global\n"
                "# rc-state-rationale: global\n" + _W
            ),
            "unjustified-global",
        ),
        (
            "stateless-hook-is-silent",
            _fixture('echo "no state here"'),
            None,
        ),
    ]

    failures = 0
    with tempfile.TemporaryDirectory() as td:
        for name, src, expect in cases:
            p = Path(td) / f"{name}.sh"
            p.write_text(src, encoding="utf-8")
            got = _check_one(p, src)
            rules = {f.rule for f in got}
            if expect is None:
                ok = not got
            else:
                ok = expect in rules
            print(f"  [{'ok' if ok else 'FAIL'}] {name}: expected={expect} got={sorted(rules)}")
            if not ok:
                failures += 1

    print(f"\nself-test: {len(cases) - failures} passed, {failures} failed")
    return 2 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--discover", action="store_true", help="report shape only; exit 0")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    repo = Path.cwd()
    if not (repo / HOOKS_JSON).is_file():
        print(f"ERROR: {HOOKS_JSON} not found (run from the repo root).", file=sys.stderr)
        return 2

    findings, shape = scan(repo)

    if args.discover:
        print("PreToolUse hooks — persistent-state shape:")
        for name, stateful in shape:
            print(f"  {'STATEFUL' if stateful else '  ---   '}  {name}")
        print(f"\n{sum(1 for _, s in shape if s)} stateful of {len(shape)} PreToolUse hooks.")
        if findings:
            print("\n(would report:)")
            for f in findings:
                print(f"  {f.path}: [{f.rule}] {f.detail}")
        return 0

    if EXEMPT:
        print("Declared exemptions (each carries a stated reason):")
        for k, v in EXEMPT.items():
            print(f"  {k}: {v}")

    if not findings:
        n = sum(1 for _, s in shape if s)
        print(f"OK: {n} stateful PreToolUse guard(s) declare a checked state contract.")
        return 0

    print(f"{len(findings)} guard-state finding(s):\n", file=sys.stderr)
    for f in findings:
        print(f"  {f.path}\n    [{f.rule}] {f.detail}\n", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
