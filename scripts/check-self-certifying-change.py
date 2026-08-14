#!/usr/bin/env python3
"""A gate re-authored in the same commit as the thing it gates certifies itself.

## The defect this closes (P10)

`plugins/ravenclaude-core/CLAUDE.md` (the v0.208.0 P3 milestone) records the real
instance in this repo's own words:

    "Gate 51 was re-authored in the same commit -- the self-certifying-change trap
     -- proven not-weaker by the unchanged external `check-shell-router.selftest.mjs`
     still tripping all three mutations."

That entry is the whole shape. When the diff that changes an artifact ALSO
re-authors the checker that asserts over that artifact, the checker's green tells
you nothing: the same author, in the same edit, moved both the claim and the
evidence. The remedy is already known and already shipped here -- an **external
oracle that the commit leaves UNCHANGED** and that still trips the re-authored
checker. `scripts/check-shell-router.selftest.mjs` exists for exactly that reason
and says so in its own header.

Nothing gated any of it. The trap was recognised, remedied by hand once, written
down -- and the next re-authoring would have had to be caught by a reviewer
noticing two paths in one diff.

## THE HONEST BOUND -- read this before trusting the flag

**This is a co-change detector, not a proof of weakening.** It answers "did a
checker and something it asserts over move together?", never "is the checker now
weaker?". Only a mutation test answers that, and only an oracle the commit did not
touch makes the mutation test credible.

Concretely, it cannot see:

  * a checker weakened in one commit and its target changed in the next
  * a target reached through a path the checker computes at runtime
  * a co-change that is entirely legitimate (most of them are)

The last bullet is why the diff-scanning mode is wired into CI as an **advisory
comment, not a blocking step**: hard-blocking every legitimate co-change would
train reviewers to bypass it, and a bypassed guard protects nothing. The half that
*does* block is this file's default mode -- the oracle-manifest integrity check --
because a declared oracle that has rotted is a silent, unbounded fail-open.

## The two suppressions, both of which must be DECLARED

  1. **An unchanged external oracle** (`docs/gate-oracle-manifest.json` ->
     `oracles`). The Gate 51 remedy, generalised: if a declared oracle for the
     re-authored checker is present in the tree and absent from the diff, the
     co-change carries independent evidence and is not flagged. An oracle that is
     ITSELF in the diff suppresses nothing -- that is the whole point.
  2. **A reasoned waiver** (`waivers`). Every waiver carries a non-empty `reason`.
     A waiver with an empty reason is a silenced finding, so the manifest check
     rejects it.

There is no third, undeclared carve-out. The manifest lives OUTSIDE this file on
purpose: adding a waiver must not require editing the checker that reads it --
that would be this very defect, committed while closing it.

## Precision decisions, each made because the naive form was measured and failed

  * **Both sides must be MODIFIED, never ADDED.** Every "add a new gate" commit in
     this repo touches `scripts/audit-gates.sh` and a new `scripts/check-*.py` in
     one diff. Treating an added file as a target made the detector flag ~every
     gate PR in the repo's history -- a detector that fires on the normal case is
     a detector nobody keeps. A gate can only be *re-authored* if it already
     existed.
  * **`scripts/audit-gates.sh` is scoped to its own diff hunks.** It names on the
     order of two hundred paths, so deriving its targets from the whole file makes
     it co-change with essentially anything. Its targets are the paths named in the
     lines this diff added or removed.
  * **Targets are path literals that EXIST in the tree.** A checker's source names
     the paths it reads. A literal that resolves to nothing is a comment, a
     fixture, or a temp path -- never a live target.

Exit codes:  0 = clean;  2 = a finding, a rotted manifest, or nothing to read.
Exit 1 is never used for a finding -- the harness treats exit 1 as a non-blocking
error, which is a silent fail-open.

Usage:
    python3 scripts/check-self-certifying-change.py                  # manifest integrity
    python3 scripts/check-self-certifying-change.py --self-test
    python3 scripts/check-self-certifying-change.py --must-fail       # planted rot; exit 2
    python3 scripts/check-self-certifying-change.py --commit <sha>
    python3 scripts/check-self-certifying-change.py --range <base>..<head>
    python3 scripts/check-self-certifying-change.py --staged
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

MANIFEST_PATH = Path("docs/gate-oracle-manifest.json")

# The one checker whose target set is derived from its diff hunks rather than its
# whole source. See the header: it names ~200 paths, so whole-file derivation
# makes it co-change with the entire repo.
HUNK_SCOPED = "scripts/audit-gates.sh"

# ── What counts as a gate/checker file ───────────────────────────────────────
# Matched on the repo-relative POSIX path. Kept to the shapes this repo actually
# uses for enforcement, so an ordinary source edit is never mistaken for a gate
# re-authoring.
CHECKER_RES = (
    re.compile(r"^scripts/audit-gates\.sh$"),
    re.compile(r"^scripts/check-[A-Za-z0-9_.-]+\.(?:py|sh|mjs|js)$"),
    re.compile(r"^scripts/[A-Za-z0-9_.-]+\.selftest\.mjs$"),
    re.compile(r"^plugins/[^/]+/hooks/tests/[A-Za-z0-9_.-]+\.sh$"),
)

# ── Path literals inside a checker's source ──────────────────────────────────
# Anchored on the repo's real top-level directories so that prose fragments like
# "and/or" or a URL path cannot masquerade as a repo path.
_ROOTS = (
    "scripts",
    "plugins",
    "docs",
    "schemas",
    "checklists",
    "examples",
    "evals",
    "tests",
    "logo-export",
    ".github",
    ".claude-plugin",
    ".ravenclaude",
    ".claude",
)
PATH_LITERAL_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])(" + "|".join(re.escape(r) for r in _ROOTS) + r")/[A-Za-z0-9_*?./-]*[A-Za-z0-9_*?]"
)
# Committed top-level artifacts that gates assert over by bare name.
TOP_LEVEL_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])(index\.html|pitch\.html|feedback-report\.html|pitch-data\.json|\.repo-layout\.json)\b"
)


class Change(NamedTuple):
    """One path in a diff: its status letter and (for hunk-scoped files) its hunks."""

    status: str  # "A" added, "M" modified, "D" deleted, "R"/"C" renamed/copied
    path: str
    hunks: str  # added/removed line text; "" when not collected


class Finding(NamedTuple):
    checker: str
    target: str
    why: str


class Ambiguity(Exception):
    """The input could not be read with confidence. Always fail-closed."""


def is_checker(path: str) -> bool:
    return any(rx.match(path) for rx in CHECKER_RES)


# ── Target derivation ────────────────────────────────────────────────────────


_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
_TRIPLE_RE = re.compile(r'"""(?:.|\n)*?"""|\'\'\'(?:.|\n)*?\'\'\'')


def strip_commentary(text: str) -> str:
    """Remove comments and docstrings before looking for path literals.

    ⛔ A PATH NAMED IN PROSE IS NOT A TARGET — the source-scan-matches-prose trap
    this repo has shipped repeatedly, and the 150-commit dry run reproduced it
    here: `check-shipped-references-resolve.py` came out "asserting over"
    `scripts/audit-gates.sh` purely because a header comment says its teeth are
    audited there. Every checker in this repo documents itself heavily, so
    scanning raw source makes every explained cross-reference look like a
    dependency.
    """
    text = _BLOCK_COMMENT_RE.sub(" ", text)
    text = _TRIPLE_RE.sub(" ", text)
    out: list[str] = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue
        out.append(_truncate_at_comment(line))
    return "\n".join(out)


def _truncate_at_comment(line: str) -> str:
    """Cut a trailing `#` / `//` comment, respecting quotes (a `#` inside a string stays)."""
    quote = ""
    i = 0
    while i < len(line):
        ch = line[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = ""
        elif ch in "\"'`":
            quote = ch
        elif ch == "#":
            return line[:i]
        elif ch == "/" and line[i : i + 2] == "//":
            return line[:i]
        i += 1
    return line


_TOKEN_TRIM = "()[]{}<>,;:|&`\"'$*+!?=\\ \t"


def _split_strings(line: str) -> tuple[list[str], list[str]]:
    """Split one line into (quoted-string contents, everything outside quotes)."""
    inside: list[str] = []
    outside: list[str] = []
    buf: list[str] = []
    quote = ""
    i = 0
    while i < len(line):
        ch = line[i]
        if quote:
            if ch == "\\" and i + 1 < len(line):
                buf.append(line[i : i + 2])
                i += 2
                continue
            if ch == quote:
                inside.append("".join(buf))
                buf = []
                quote = ""
            else:
                buf.append(ch)
        elif ch in "\"'`":
            outside.append("".join(buf))
            buf = []
            quote = ch
        else:
            buf.append(ch)
        i += 1
    (inside if quote else outside).append("".join(buf))
    return inside, outside


def _whole(text: str) -> str | None:
    """The text, if the WHOLE of it is one path literal; otherwise None."""
    s = text.strip()
    if not s:
        return None
    m = PATH_LITERAL_RE.fullmatch(s) or TOP_LEVEL_RE.fullmatch(s)
    return s if m else None


def _literals(text: str) -> set[str]:
    """Path literals a checker uses AS PATHS, not ones it merely mentions.

    ⛔ A PATH INSIDE A MESSAGE IS STILL PROSE — the dry run's third false-positive
    class, and the nastiest, because stripping comments does not catch it. Line
    348 of `check-shipped-references-resolve.py` is a user-facing *string*:
    "Dev tooling is fine: `bash scripts/audit-gates.sh` (ignore-listed)." So is
    an argparse `help=` text. Both read as a dependency to any scanner that just
    greps for a path.

    The discriminator is structural, not lexical: a path a program USES is either
    the ENTIRE contents of a quoted string (`Path("scripts/ravenclaude")`,
    `const ROOT = "scripts/serve-dashboards.py"`) or a standalone unquoted token
    in shell. A path a program TALKS ABOUT is one word inside a sentence.
    """
    text = strip_commentary(text)
    out: set[str] = set()
    for line in text.splitlines():
        inside, outside = _split_strings(line)
        for s in inside:
            whole = _whole(s)
            if whole:
                out.add(whole)
        for chunk in outside:
            for raw in chunk.split():
                tok = raw.strip(_TOKEN_TRIM)
                whole = _whole(tok)
                if whole:
                    out.add(whole)
    return out


class Tree:
    """The file set a diff is judged against.

    ⛔ A historical commit must be judged against ITS OWN tree, never today's. The
    first draft read every checker's source from the working copy, so a commit
    from twenty merges ago was scored with path literals that did not exist yet
    (and missed ones that had since been deleted). `GitTree` fixes that; `DiskTree`
    is the working-copy case the self-test and the manifest check use.
    """

    def paths(self) -> set[str]:
        raise NotImplementedError

    def read(self, path: str) -> str:
        raise NotImplementedError

    def is_file(self, path: str) -> bool:
        return path in self.paths()

    def is_dir(self, path: str) -> bool:
        pre = path.rstrip("/") + "/"
        return any(p.startswith(pre) for p in self.paths())


class DiskTree(Tree):
    def __init__(self, root: Path) -> None:
        self.root = root
        self._paths: set[str] | None = None

    def paths(self) -> set[str]:
        if self._paths is None:
            self._paths = {
                p.relative_to(self.root).as_posix()
                for p in self.root.rglob("*")
                if p.is_file() and ".git/" not in p.relative_to(self.root).as_posix() + "/"
            }
        return self._paths

    def is_file(self, path: str) -> bool:
        return (self.root / path).is_file()

    def is_dir(self, path: str) -> bool:
        return (self.root / path).is_dir()

    def read(self, path: str) -> str:
        return (self.root / path).read_text(encoding="utf-8", errors="replace")


class GitTree(Tree):
    def __init__(self, root: Path, rev: str) -> None:
        self.root = root
        self.rev = rev
        self._paths: set[str] | None = None

    def paths(self) -> set[str]:
        if self._paths is None:
            self._paths = set(_git(["ls-tree", "-r", "--name-only", self.rev], self.root).splitlines())
        return self._paths

    def read(self, path: str) -> str:
        proc = subprocess.run(
            ["git", "-C", str(self.root), "show", f"{self.rev}:{path}"],
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            raise Ambiguity(f"cannot read {path} at {self.rev}")
        return proc.stdout.decode("utf-8", errors="replace")


def _resolve(literal: str, tree: Tree) -> set[str]:
    """Expand one source literal to the real tree paths it names, or nothing.

    ⛔ A DIRECTORY LITERAL IS A SCAN ROOT, NOT A TARGET — measured, not assumed.
    The first draft let a directory stand for everything beneath it, and the
    150-commit dry run turned that into the dominant false-positive class:
    `check-frontmatter.py` names `plugins/` because it WALKS it, so it "asserted
    over" all ~4,000 files in the tree and flagged eleven unrelated paths in one
    commit; `check-shipped-references-resolve.py` did the same and ended up
    flagged against `scripts/audit-gates.sh` and its own fixture. A whole-tree
    walker co-changing with one of the thousands of files it happens to walk is
    not the P10 trap. The trap needs a checker that names a SPECIFIC artifact, so
    only a literal path to an existing FILE resolves.

    ⛔ A GLOB IS A CORPUS, AND SO IS ALSO NOT A TARGET. Same measurement: with
    globs resolved, `check-frontmatter.py`'s `plugins/*/agents/**` gave it 9,083
    "targets" and `check-md-links.py`'s `plugins/**/*.md` gave it 9,326. A checker
    that lints a whole population is not certifying any one member of it.
    """
    if "*" in literal or "?" in literal:
        return set()
    if tree.is_file(literal):
        return {literal}
    return set()


def targets_of(checker: str, source: str, tree: Tree) -> set[str]:
    """The tree paths `checker`'s source claims to read, minus the checker itself."""
    resolved: set[str] = set()
    for lit in _literals(source):
        resolved |= _resolve(lit, tree)
    resolved.discard(checker)
    return resolved


def _covers(target: str, changed_path: str) -> bool:
    if target.endswith("/"):
        return changed_path.startswith(target)
    return target == changed_path


# ── Manifest ─────────────────────────────────────────────────────────────────


def load_manifest(root: Path) -> dict:
    p = root / MANIFEST_PATH
    if not p.is_file():
        raise Ambiguity(f"oracle manifest missing: {MANIFEST_PATH}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise Ambiguity(f"oracle manifest unreadable: {exc}") from exc
    if not isinstance(data, dict):
        raise Ambiguity("oracle manifest is not an object")
    return data


def verify_manifest(root: Path) -> list[str]:
    """Every declared oracle and waiver must still be real. Returns problem lines.

    This is the blocking half. A declared oracle whose file was renamed away, or a
    waiver whose reason was blanked, silently widens the suppression surface --
    the exact rot class this initiative exists to close.
    """
    problems: list[str] = []
    data = load_manifest(root)

    if data.get("schema_version") != 1:
        problems.append("schema_version must be 1")

    oracles = data.get("oracles")
    if not isinstance(oracles, dict):
        problems.append("`oracles` must be an object")
        oracles = {}
    for checker, entry in sorted(oracles.items()):
        where = f"oracles[{checker}]"
        if not is_checker(checker):
            problems.append(f"{where}: key is not a recognised gate/checker path")
        if not (root / checker).is_file():
            problems.append(f"{where}: checker does not exist in the tree")
        if not isinstance(entry, dict):
            problems.append(f"{where}: entry must be an object")
            continue
        reason = entry.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            problems.append(f"{where}: empty reason — an undeclared suppression")
        paths = entry.get("oracles")
        if not isinstance(paths, list) or not paths:
            problems.append(f"{where}: `oracles` must be a non-empty list")
            continue
        base = Path(checker).name
        for op in paths:
            if not isinstance(op, str) or not op:
                problems.append(f"{where}: oracle path must be a non-empty string")
                continue
            if op == checker:
                problems.append(f"{where}: {op} is the checker itself, not an external oracle")
                continue
            of = root / op
            if not of.is_file():
                problems.append(f"{where}: oracle {op} does not exist in the tree")
                continue
            # An oracle that never names the checker it certifies is not its
            # oracle. This is what stops a plausible-looking but inert file from
            # suppressing findings forever.
            try:
                otext = of.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                problems.append(f"{where}: oracle {op} unreadable: {exc}")
                continue
            if base not in otext:
                problems.append(f"{where}: oracle {op} never references {base} — it is not an oracle for it")

    waivers = data.get("waivers")
    if not isinstance(waivers, list):
        problems.append("`waivers` must be a list")
        waivers = []
    for i, w in enumerate(waivers):
        where = f"waivers[{i}]"
        if not isinstance(w, dict):
            problems.append(f"{where}: must be an object")
            continue
        for key in ("checker", "target", "reason"):
            v = w.get(key)
            if not isinstance(v, str) or not v.strip():
                problems.append(f"{where}: `{key}` must be a non-empty string")
        reason = w.get("reason") or ""
        if isinstance(reason, str) and reason.strip() and len(reason.strip()) < 30:
            problems.append(f"{where}: reason is too short to be a reason ({len(reason.strip())} chars)")
        checker = w.get("checker")
        if isinstance(checker, str) and checker and not (root / checker).is_file():
            problems.append(f"{where}: checker {checker} does not exist in the tree")
    return problems


# ── The detector ─────────────────────────────────────────────────────────────


def analyze(changes: list[Change], tree: Tree, manifest: dict) -> list[Finding]:
    if not changes:
        raise Ambiguity("the diff contains no paths — the detector had nothing to read (UNWIRED, not clean)")

    by_path = {c.path: c for c in changes}
    changed_paths = set(by_path)
    oracles = manifest.get("oracles") or {}
    waivers = manifest.get("waivers") or []

    findings: list[Finding] = []
    for change in sorted(changes):
        if change.status != "M" or not is_checker(change.path):
            continue
        if change.path == HUNK_SCOPED:
            source = change.hunks
            scope = "hunks"
        else:
            if not tree.is_file(change.path):
                raise Ambiguity(f"changed checker {change.path} is not readable in the tree")
            source = tree.read(change.path)
            scope = "source"

        # An unchanged declared oracle is the Gate 51 remedy; it clears the whole
        # checker. An oracle that is itself in the diff clears nothing.
        entry = oracles.get(change.path)
        if isinstance(entry, dict):
            declared = [o for o in (entry.get("oracles") or []) if isinstance(o, str)]
            intact = [o for o in declared if tree.is_file(o) and o not in changed_paths]
            if intact:
                continue

        for target in sorted(targets_of(change.path, source, tree)):
            hits = sorted(p for p in changed_paths if _covers(target, p) and p != change.path)
            for hit in hits:
                if by_path[hit].status != "M":
                    continue  # a newly added target cannot have been re-authored around
                if _waived(waivers, change.path, hit):
                    continue
                findings.append(
                    Finding(
                        change.path,
                        hit,
                        f"both modified in one diff; target named in the checker's {scope}",
                    )
                )
    # De-duplicate while keeping order.
    seen: set[tuple[str, str]] = set()
    out: list[Finding] = []
    for f in findings:
        key = (f.checker, f.target)
        if key in seen:
            continue
        seen.add(key)
        out.append(f)
    return out


def _waived(waivers: list, checker: str, target: str) -> bool:
    for w in waivers:
        if not isinstance(w, dict):
            continue
        if w.get("checker") != checker:
            continue
        reason = w.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            continue  # an empty reason waives nothing
        pat = w.get("target")
        if not isinstance(pat, str) or not pat:
            continue
        if pat == target or (pat.endswith("/") and target.startswith(pat)):
            return True
        if ("*" in pat or "?" in pat) and Path(target).match(pat):
            return True
    return False


# ── git plumbing ─────────────────────────────────────────────────────────────


def _git(args: list[str], root: Path) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root)] + args,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise Ambiguity(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def collect_changes(root: Path, *, commit: str | None, rng: str | None, staged: bool) -> list[Change]:
    if commit:
        name_status = ["show", "--name-status", "--format=", "-m", "--first-parent", commit]
        hunk_args = ["show", "-U0", "--format=", "--first-parent", commit, "--", HUNK_SCOPED]
    elif rng:
        name_status = ["diff", "--name-status", rng]
        hunk_args = ["diff", "-U0", rng, "--", HUNK_SCOPED]
    elif staged:
        name_status = ["diff", "--name-status", "--cached"]
        hunk_args = ["diff", "-U0", "--cached", "--", HUNK_SCOPED]
    else:
        raise Ambiguity("no diff selector given")

    raw = _git(name_status, root)
    hunks = ""
    parsed: list[Change] = []
    seen: set[str] = set()
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0][:1]
        path = parts[-1]
        if path in seen:
            continue
        seen.add(path)
        parsed.append(Change(status, path, ""))

    if any(c.path == HUNK_SCOPED for c in parsed):
        hunk_lines = []
        for line in _git(hunk_args, root).splitlines():
            if line.startswith(("+++", "---")):
                continue
            if line.startswith(("+", "-")):
                hunk_lines.append(line[1:])
        hunks = "\n".join(hunk_lines)
        parsed = [c._replace(hunks=hunks) if c.path == HUNK_SCOPED else c for c in parsed]
    return parsed


# ── self-test ────────────────────────────────────────────────────────────────
#
# ⛔ SELF-NON-RECURSION. Every fixture below is ASSEMBLED from fragments at
# runtime, never written as a literal path or a literal manifest. A source-scan
# gate that spells its own bad input out loud matches itself the moment anything
# scans this file -- this repo has shipped that bug repeatedly. `_seg` exists for
# exactly that reason and the fixtures are unreadable-as-literals on purpose.


def _seg(*parts: str) -> str:
    return "/".join(parts)


def _mk_tree(root: Path, files: dict[str, str]) -> None:
    for rel, body in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")


def _fixture_names() -> tuple[str, str, str, str]:
    """checker, target, oracle, unrelated — assembled, never literal."""
    checker = _seg("scripts", "check-" + "widget" + "-shape.py")
    target = _seg("plugins", "demo", "hooks", "widget.sh")
    oracle = _seg("scripts", "widget-shape" + ".selftest" + ".mjs")
    unrelated = _seg("docs", "notes.md")
    return checker, target, oracle, unrelated


def _fixture_manifest(checker: str, oracle: str, *, with_oracle: bool, waiver: str | None, reason: str) -> dict:
    m: dict = {"schema_version": 1, "oracles": {}, "waivers": []}
    if with_oracle:
        m["oracles"][checker] = {"oracles": [oracle], "reason": "fixture oracle, " + "declared for the self-test"}
    if waiver:
        m["waivers"].append({"checker": checker, "target": waiver, "reason": reason})
    return m


def _run_self_test() -> int:
    failures: list[str] = []

    def check(label: str, ok: bool) -> None:
        mark = "✓" if ok else "✗"
        print(f"  {mark} {label}")
        if not ok:
            failures.append(label)

    checker, target, oracle, unrelated = _fixture_names()
    # A path the checker USES (the whole of a quoted string), not one it mentions
    # in a comment — strip_commentary would drop a `# reads <path>` line, and the
    # three must-fail fixtures would go silent for the wrong reason.
    checker_body = "p = " + '"' + target + '"' + "\nimport sys\n"
    oracle_body = "// external oracle for " + Path(checker).name + "\n"

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        tree = DiskTree(root)
        _mk_tree(
            root,
            {
                checker: checker_body,
                target: "#!/bin/sh\necho widget\n",
                oracle: oracle_body,
                unrelated: "# notes\n",
                HUNK_SCOPED: "# suite\n",
            },
        )

        bare = _fixture_manifest(checker, oracle, with_oracle=False, waiver=None, reason="")

        # 1. MUST FAIL — the checker and the artifact it names, both modified.
        co_change = [Change("M", checker, ""), Change("M", target, "")]
        check("must-fail: checker + its named target modified together is flagged", len(analyze(co_change, tree, bare)) == 1)

        # 2. SILENT-ON-GOOD — the target moves alone.
        check("silent-on-good: the target alone is not a finding", analyze([Change("M", target, "")], tree, bare) == [])

        # 3. SILENT-ON-GOOD — the checker moves alone.
        check("silent-on-good: the checker alone is not a finding", analyze([Change("M", checker, "")], tree, bare) == [])

        # 4. SILENT-ON-GOOD — an unchanged declared oracle clears it (the Gate 51 remedy).
        with_oracle = _fixture_manifest(checker, oracle, with_oracle=True, waiver=None, reason="")
        check("silent-on-good: an UNCHANGED declared external oracle clears the co-change", analyze(co_change, tree, with_oracle) == [])

        # 5. MUST FAIL — the same oracle, itself in the diff, suppresses nothing.
        touched = co_change + [Change("M", oracle, "")]
        check("must-fail: an oracle that is ITSELF in the diff suppresses nothing", len(analyze(touched, tree, with_oracle)) == 1)

        # 6. SILENT-ON-GOOD — a newly ADDED checker (every new-gate PR) is not a re-authoring.
        added = [Change("A", checker, ""), Change("M", target, "")]
        check("silent-on-good: a newly ADDED checker is not a re-authoring", analyze(added, tree, bare) == [])

        # 7. SILENT-ON-GOOD — a newly ADDED target cannot have been certified around.
        added_target = [Change("M", checker, ""), Change("A", target, "")]
        check("silent-on-good: a newly ADDED target is not a re-authoring", analyze(added_target, tree, bare) == [])

        # 8. SILENT-ON-GOOD — a reasoned waiver clears exactly its own pair.
        reason = "a fixture waiver whose reason is long enough to be a real reason"
        waived = _fixture_manifest(checker, oracle, with_oracle=False, waiver=target, reason=reason)
        check("silent-on-good: a reasoned waiver clears its own pair", analyze(co_change, tree, waived) == [])

        # 9. MUST FAIL — a waiver with an EMPTY reason is a silenced finding, not a waiver.
        silent = _fixture_manifest(checker, oracle, with_oracle=False, waiver=target, reason="")
        check("must-fail: an EMPTY-reason waiver suppresses nothing", len(analyze(co_change, tree, silent)) == 1)

        # 10. MUST FAIL — a path the checker does NOT name is not its target.
        pair = [Change("M", checker, ""), Change("M", unrelated, "")]
        check("silent-on-good: a co-changed path the checker never names is not a target", analyze(pair, tree, bare) == [])

        # 11. UNWIRED — an empty diff must be loud, never green.
        unwired = False
        try:
            analyze([], tree, bare)
        except Ambiguity:
            unwired = True
        check("unwired: an empty diff fails closed instead of reporting clean", unwired)

        # 12. HUNK SCOPING — the suite file is judged on its hunks, not its whole source.
        suite_all = root / HUNK_SCOPED
        suite_all.write_text("# names " + target + "\n# and " + unrelated + "\n", encoding="utf-8")
        hunk_naming_target = "+run " + target
        only_target = [
            Change("M", HUNK_SCOPED, hunk_naming_target),
            Change("M", target, ""),
            Change("M", unrelated, ""),
        ]
        got = analyze(only_target, tree, bare)
        check(
            "hunk-scoped: the suite is judged on its DIFF HUNKS, not its whole source",
            len(got) == 1 and got[0].target == target,
        )

        # 13. MANIFEST INTEGRITY — a rotted oracle path is caught.
        _mk_tree(root, {MANIFEST_PATH.as_posix(): json.dumps(_fixture_manifest(checker, oracle, with_oracle=True, waiver=None, reason=""))})
        check("manifest: a live, well-formed manifest verifies clean", verify_manifest(root) == [])
        gone = _fixture_manifest(checker, _seg("scripts", "does-not-exist" + ".selftest" + ".mjs"), with_oracle=True, waiver=None, reason="")
        _mk_tree(root, {MANIFEST_PATH.as_posix(): json.dumps(gone)})
        check("manifest must-fail: an oracle path that no longer exists is caught", verify_manifest(root) != [])

        # 14. MANIFEST INTEGRITY — an oracle that never names its checker is inert.
        _mk_tree(root, {oracle: "// unrelated file that names nothing\n"})
        _mk_tree(root, {MANIFEST_PATH.as_posix(): json.dumps(_fixture_manifest(checker, oracle, with_oracle=True, waiver=None, reason=""))})
        check("manifest must-fail: an oracle that never references its checker is caught", verify_manifest(root) != [])

        # 15. MANIFEST INTEGRITY — an empty waiver reason is caught.
        _mk_tree(root, {oracle: oracle_body})
        blank = _fixture_manifest(checker, oracle, with_oracle=False, waiver=target, reason="   ")
        _mk_tree(root, {MANIFEST_PATH.as_posix(): json.dumps(blank)})
        check("manifest must-fail: a blank waiver reason is caught", verify_manifest(root) != [])

        # 16. RANGE HEAD — three-dot `A...B` is not two-dot `A..B` with a leading dot.
        check("range-head: three-dot range resolves to the right-hand rev", _range_head("origin/main...HEAD") == "HEAD")
        check("range-head: two-dot range resolves to the right-hand rev", _range_head("abc..def") == "def")

    if failures:
        print(f"\nself-test FAILED — {len(failures)} fixture(s) did not behave as specified:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 2
    print("\nself-test passed — teeth on both halves, and the suppressions are declared-only.")
    return 0


def _range_head(rng: str) -> str:
    """Right-hand revision of a two- or three-dot git range.

    `str.split("..")` on `origin/main...HEAD` yields `.HEAD`, which is not a
    revision. Three-dot must be split first.
    """
    if "..." in rng:
        return rng.rsplit("...", 1)[-1] or "HEAD"
    if ".." in rng:
        return rng.rsplit("..", 1)[-1] or "HEAD"
    return rng or "HEAD"


def _run_must_fail() -> int:
    """Plant a rotted oracle and run the integrity check. Exit 2 if teeth work.

    This is the finding path, not a wrapper that converts 2→0. The harness
    asserts the exit is literally 2 — exit 1 is a silent fail-open (Gate 6).
    If the planted rot produces no findings the teeth are gone: exit 0 so
    `must_fail` in audit-gates.sh goes red.
    """
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        checker, _target, _oracle, _unrelated = _fixture_names()
        gone = _seg("scripts", "does-not-exist" + ".selftest" + ".mjs")
        _mk_tree(
            root,
            {
                checker: "import sys\n",
                MANIFEST_PATH.as_posix(): json.dumps(
                    _fixture_manifest(checker, gone, with_oracle=True, waiver=None, reason="")
                ),
            },
        )
        try:
            problems = verify_manifest(root)
        except Ambiguity as exc:
            print(f"self-certifying-change --must-fail: FAIL-CLOSED — {exc}", file=sys.stderr)
            return 2
        if not problems:
            print(
                "self-certifying-change --must-fail: planted rot produced NO findings — no teeth",
                file=sys.stderr,
            )
            return 0
        print("self-certifying-change --must-fail: planted rot was caught\n", file=sys.stderr)
        for p in problems:
            print(f"  ✗ {p}", file=sys.stderr)
        return 2


# ── entry point ──────────────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true", help="run the fixture pairs and exit")
    ap.add_argument(
        "--must-fail",
        action="store_true",
        help="plant a rotted oracle and exit 2 if the integrity check catches it",
    )
    ap.add_argument("--commit", help="analyze a single commit")
    ap.add_argument("--range", dest="rng", help="analyze a diff range, e.g. origin/main...HEAD")
    ap.add_argument("--staged", action="store_true", help="analyze the staged diff")
    ap.add_argument("--root", default=".", help="repo root (default: cwd)")
    args = ap.parse_args()

    if args.self_test:
        return _run_self_test()
    if args.must_fail:
        return _run_must_fail()

    root = Path(args.root).resolve()

    try:
        if not (args.commit or args.rng or args.staged):
            problems = verify_manifest(root)
            if problems:
                print("self-certifying-change: the oracle manifest has ROTTED\n", file=sys.stderr)
                for p in problems:
                    print(f"  ✗ {p}", file=sys.stderr)
                print(
                    "\nA declared oracle or waiver that no longer resolves silently widens the\n"
                    "suppression surface. Repair the entry or delete it.",
                    file=sys.stderr,
                )
                return 2
            print(f"self-certifying-change: {MANIFEST_PATH} is intact (every declared oracle and waiver resolves).")
            return 0

        manifest = load_manifest(root)
        changes = collect_changes(root, commit=args.commit, rng=args.rng, staged=args.staged)
        # ⛔ Judge a commit against ITS OWN tree. Reading the working copy would
        # score a historical diff with path literals that did not exist yet.
        if args.commit:
            tree: Tree = GitTree(root, args.commit)
        elif args.rng:
            tree = GitTree(root, _range_head(args.rng))
        else:
            tree = DiskTree(root)
        findings = analyze(changes, tree, manifest)
    except Ambiguity as exc:
        print(f"self-certifying-change: FAIL-CLOSED — {exc}", file=sys.stderr)
        return 2

    if not findings:
        print(f"self-certifying-change: no gate was re-authored alongside its own target ({len(changes)} path(s) scanned).")
        return 0

    print("self-certifying-change: a gate moved in the same diff as the thing it gates\n", file=sys.stderr)
    for f in findings:
        print(f"  ✗ {f.checker}\n      asserts over  {f.target}\n      {f.why}", file=sys.stderr)
    print(
        "\nThe checker's green proves nothing here: the same diff moved both the claim\n"
        "and the evidence. Either (a) point an EXTERNAL oracle that this diff leaves\n"
        f"UNCHANGED at the checker and declare it in {MANIFEST_PATH}, or (b) record a\n"
        "reasoned waiver there. An empty reason is a silenced finding, not a waiver.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
