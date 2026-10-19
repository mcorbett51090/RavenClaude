#!/usr/bin/env python3
"""check-secret-pattern-parity.py — the secret-pattern copies cannot drift apart.

The secret-shape list in plugins/ravenclaude-core/hooks/_scrub.sh is copied by
hand into about a dozen files: Python ports, inline bash fallbacks, and two deny
sets. On 2026-10-19 the copies had already drifted (two used gh[pousr]_, the rest
only ghp_), and the shared `sk-` shape had no left boundary, so ordinary
kebab-case names such as a docs path built from "ri" + "sk-assessment-..." were
refused as secrets by four egress backstops.

This checker reads the COPIES table (the secret_spec copy list) and asserts:

  R copies (redaction / egress backstops)
    R1  the file exists and is readable;
    R2  it carries the sk- shape, and EVERY sk- regex in it has a left boundary;
    R3  it carries the full GitHub class gh[pousr]_[A-Za-z0-9]{30,} and no
        ghp_-only class.
  D copies (deny / refusal gates)
    D1  the file exists and is readable;
    D2  every sk- regex in it has a left boundary;
    D3  it carries each D-set form verbatim (secret_spec D_set_deny), and no
        ghp_-only class.
  Unlisted copies
    U1  no other tracked code file carries an UNANCHORED sk- regex or a
        ghp_-only class. A new copy must be added to COPIES (and anchored), so
        the next copy cannot drift silently. tests/ paths are skipped: mutation
        tests legitimately hold the old form as data.

Exit codes (premise-gate.py's contract):
  0  every copy is in parity
  2  drift found (each finding names the file and the rule)
  1  could not run (unreadable file, bad --root) — never reported as clean

Usage:
  python3 scripts/check-secret-pattern-parity.py            # check this repo
  python3 scripts/check-secret-pattern-parity.py --root DIR
  python3 scripts/check-secret-pattern-parity.py --self-test
  python3 scripts/check-secret-pattern-parity.py --must-fail

Registration in scripts/audit-gates.sh happens at integration, after every
package that owns a copy has merged (the copies live in five packages).
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# The copy list. Keep it in sync with secret_spec (R_set_redaction.copies and
# D_set_deny.copies). Paths are repo-relative.
# ---------------------------------------------------------------------------
COPIES: list[tuple[str, str]] = [
    ("plugins/ravenclaude-core/hooks/_scrub.sh", "R"),
    ("plugins/ravenclaude-core/scripts/claude-orchestrate.sh", "R"),
    ("plugins/ravenclaude-core/skills/refine-to-rubric/scripts/judge.sh", "R"),
    ("plugins/ravenclaude-core/hooks/triage-outcome.sh", "R"),
    ("plugins/ravenclaude-core/scripts/capability-orientation.py", "R"),
    ("plugins/ravenclaude-core/scripts/precompact-digest.py", "R"),
    ("plugins/ravenclaude-core/scripts/thing-denial-kb.py", "R"),
    ("plugins/ravenclaude-core/scripts/thing-seat.sh", "R"),
    ("plugins/ravenclaude-core/scripts/serve-dashboards.py", "R"),
    ("scripts/serve-dashboards.py", "R"),
    ("plugins/ravenclaude-core/scripts/spectate_store.py", "R"),
    ("plugins/ravenclaude-core/scripts/context-handoff.py", "R"),
    ("plugins/ravenclaude-core/knowledge/concerns-catalog.md", "D"),
    ("scripts/process-scenario-submission.py", "D"),
]

# The full GitHub token class, as it must appear in an R copy.
GH_FULL = "gh[pousr]_[A-Za-z0-9]{30,}"
# The ghp_-only class that must not survive anywhere in a copy.
GH_ONLY_RE = re.compile(r"ghp_\[A-Za-z0-9\]")

# D-set forms (secret_spec D_set_deny.changes), verbatim.
D_FORMS: list[str] = [
    r"(?<![A-Za-z0-9])(?-i:sk-)(?:ant-|proj-)?[A-Za-z0-9_-]{20,}",
    r"(?-i:gh[pousr]_)[A-Za-z0-9]{30,}",
    r"(?-i:npm_)[A-Za-z0-9]{30,}",
    r"(?-i:[sr]k_live_)[A-Za-z0-9]{24,}",
    r"(?-i:hf_)[A-Za-z0-9]{30,}",
    r"(https?|postgres(ql)?|mysql|mongodb|redis|amqp|smtp)s?://[A-Za-z0-9._-]{2,}:[A-Za-z0-9._%+-]{4,}@",
]

# A regex occurrence of the sk- shape: `sk-` followed by a group or a class,
# optionally after a closing paren (the D form `(?-i:sk-)` then `(?:ant-...`).
SK_OCC_RE = re.compile(r"sk-\)?[\[(]")
# What may sit immediately before `sk-` (after stripping one group opener).
BOUNDARIES: tuple[str, ...] = (
    "(^|[^A-Za-z0-9])",
    "(?<![A-Za-z0-9])",
    "\\b",
)
GROUP_OPENERS: tuple[str, ...] = ("(?-i:", "(?:", "(")

CODE_SUFFIXES = (".sh", ".bash", ".py", ".js", ".mjs", ".cjs", ".ts")
SELF_NAME = "check-secret-pattern-parity.py"


class CouldNotRun(Exception):
    """The checker could not look; never reported as clean."""


def _anchored(text: str, sk_index: int) -> bool:
    """True when the sk- regex starting at sk_index has a left boundary."""
    before = text[max(0, sk_index - 64) : sk_index]
    for opener in GROUP_OPENERS:
        if before.endswith(opener):
            before = before[: -len(opener)]
            break
    return any(before.endswith(b) for b in BOUNDARIES)


def sk_occurrences(text: str) -> list[tuple[int, bool]]:
    """Every sk- regex occurrence as (line number, anchored?)."""
    out = []
    for m in SK_OCC_RE.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        out.append((line, _anchored(text, m.start())))
    return out


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise CouldNotRun(f"cannot read {path}: {exc}") from exc


def check_copy(root: Path, rel: str, kind: str) -> list[str]:
    path = root / rel
    if not path.is_file():
        return [f"{rel}: listed {kind} copy not found — renamed or deleted? update COPIES"]
    text = _read(path)
    findings: list[str] = []
    occ = sk_occurrences(text)
    if kind == "R" and not occ:
        findings.append(f"{rel}: R2 no sk- pattern found — the copy lost the shape")
    for line, ok in occ:
        if not ok:
            findings.append(f"{rel}:{line}: {kind}2 sk- regex has no left boundary")
    for m in GH_ONLY_RE.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        findings.append(f"{rel}:{line}: {kind}3 ghp_-only class — use gh[pousr]_")
    if kind == "R" and GH_FULL not in text:
        findings.append(f"{rel}: R3 missing {GH_FULL}")
    if kind == "D":
        for form in D_FORMS:
            if form not in text:
                findings.append(f"{rel}: D3 missing D-set form {form}")
    return findings


def _tracked_files(root: Path) -> list[str]:
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            capture_output=True,
            check=True,
        )
        return [p for p in res.stdout.decode("utf-8", "replace").split("\0") if p]
    except (OSError, subprocess.CalledProcessError):
        files = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d != ".git"]
            for name in filenames:
                files.append(os.path.relpath(os.path.join(dirpath, name), root))
        return files


def check_unlisted(root: Path, listed: set[str]) -> list[str]:
    findings: list[str] = []
    for rel in sorted(_tracked_files(root)):
        rel = rel.replace(os.sep, "/")
        if rel in listed or not rel.endswith(CODE_SUFFIXES):
            continue
        if "/tests/" in "/" + rel or rel.startswith("tests/") or rel.endswith(SELF_NAME):
            continue
        path = root / rel
        if not path.is_file():
            continue
        text = _read(path)
        for line, ok in sk_occurrences(text):
            if not ok:
                findings.append(
                    f"{rel}:{line}: U1 unlisted copy with an unanchored sk- regex — "
                    "anchor it and add it to COPIES"
                )
        for m in GH_ONLY_RE.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            findings.append(
                f"{rel}:{line}: U1 unlisted copy with a ghp_-only class — add it to COPIES"
            )
    return findings


def run(root: Path, copies: list[tuple[str, str]]) -> list[str]:
    if not root.is_dir():
        raise CouldNotRun(f"--root {root} is not a directory")
    findings: list[str] = []
    for rel, kind in copies:
        findings.extend(check_copy(root, rel, kind))
    findings.extend(check_unlisted(root, {rel for rel, _ in copies}))
    return findings


# ---------------------------------------------------------------------------
# Self-test. Every stale form is assembled at runtime so this file never holds
# the literal it hunts for.
# ---------------------------------------------------------------------------
SK = "s" + "k-"
STALE_ERE = "'" + SK + "(ant-)?[A-Za-z0-9-]{20,}'"
GOOD_ERE = "'(^|[^A-Za-z0-9])" + SK + "(ant-)?[A-Za-z0-9-]{20,}'"
STALE_PY = 'r"' + SK + '(?:ant-)?[A-Za-z0-9-]{20,}"'
GOOD_PY = 'r"(?<![A-Za-z0-9])' + SK + '(?:ant-)?[A-Za-z0-9-]{20,}"'
GHP_ONLY = "'gh" + "p_[A-Za-z0-9]{30,}'"
GOOD_GH = "'" + GH_FULL + "'"
BOUNDED_B = 'r"\\b(' + SK + '[A-Za-z0-9]{16,})\\b"'


def _write(root: Path, rel: str, body: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")


def _good_tree(root: Path) -> list[tuple[str, str]]:
    _write(root, "r/ere.sh", "_secret_patterns=(\n  " + GOOD_ERE + "\n  " + GOOD_GH + "\n)\n")
    _write(root, "r/port.py", "P = [\n    " + GOOD_PY + ',\n    r"' + GH_FULL + '",\n]\n')
    _write(root, "d/deny.md", "triggers:\n" + "".join(f"  - '{f}'\n" for f in D_FORMS))
    _write(root, "other/anchored.py", "X = " + BOUNDED_B + "\n")
    _write(root, "other/tests/mutant.sh", "OLD=" + STALE_ERE + "\n")
    return [("r/ere.sh", "R"), ("r/port.py", "R"), ("d/deny.md", "D")]


def self_test(anchored_fn=None) -> int:
    """Return 0 when every fixture is classified correctly."""
    global _anchored
    saved = _anchored
    if anchored_fn is not None:
        _anchored = anchored_fn
    checks: list[tuple[str, bool]] = []
    try:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copies = _good_tree(root)
            clean = run(root, copies)
            checks.append(("clean tree: zero findings", clean == []))

            def mutate(rel: str, old: str, new: str) -> list[str]:
                p = root / rel
                orig = p.read_text()
                p.write_text(orig.replace(old, new))
                try:
                    return run(root, copies)
                finally:
                    p.write_text(orig)

            f = mutate("r/ere.sh", GOOD_ERE, STALE_ERE)
            checks.append(("R2: unanchored ERE sk- is a finding", any("R2 sk-" in x for x in f)))
            f = mutate("r/port.py", GOOD_PY, STALE_PY)
            checks.append(("R2: unanchored Python sk- is a finding", any("R2 sk-" in x for x in f)))
            f = mutate("r/ere.sh", GOOD_ERE, "'AKIA[0-9A-Z]{12,}'")
            checks.append(
                (
                    "R2: a copy that lost the sk- shape is a finding",
                    any("no sk- pattern" in x for x in f),
                )
            )
            f = mutate("r/ere.sh", GOOD_GH, GHP_ONLY)
            checks.append(("R3: ghp_-only class is a finding", any("R3 ghp_-only" in x for x in f)))
            checks.append(
                ("R3: missing gh[pousr]_ is a finding", any("R3 missing" in x for x in f))
            )
            f = mutate("d/deny.md", "(?-i:npm_)", "(?-i:np_)")
            checks.append(
                ("D3: a missing D-set form is a finding", any("D3 missing" in x for x in f))
            )
            stale_d = "  - '" + SK + "(ant-)?[A-Za-z0-9-]{20,}'\n"
            f = mutate("d/deny.md", "triggers:\n", "triggers:\n" + stale_d)
            checks.append(
                ("D2: unanchored sk- in a deny copy is a finding", any("D2 sk-" in x for x in f))
            )

            _write(root, "new/copy.py", "P = [" + STALE_PY + "]\n")
            f = run(root, copies)
            checks.append(
                (
                    "U1: an unlisted unanchored copy is a finding",
                    any(x.startswith("new/copy.py") and "U1" in x for x in f),
                )
            )
            (root / "new/copy.py").unlink()
            _write(root, "new/gh.sh", "P=(" + GHP_ONLY + ")\n")
            f = run(root, copies)
            checks.append(
                (
                    "U1: an unlisted ghp_-only copy is a finding",
                    any(x.startswith("new/gh.sh") for x in f),
                )
            )
            (root / "new/gh.sh").unlink()
            f = run(root, copies)
            checks.append(
                (
                    "U1: a \\b-anchored unlisted copy is not a finding",
                    not any("anchored.py" in x for x in f),
                )
            )
            checks.append(
                ("U1: a tests/ mutation file is skipped", not any("mutant.sh" in x for x in f))
            )

            (root / "r/port.py").unlink()
            f = run(root, copies)
            checks.append(
                ("R1: a missing listed copy is a finding", any("not found" in x for x in f))
            )
            _write(root, "r/port.py", "P = [" + GOOD_PY + ', r"' + GH_FULL + '"]\n')

            try:
                run(root / "absent", copies)
                checks.append(("bad --root raises CouldNotRun", False))
            except CouldNotRun:
                checks.append(("bad --root raises CouldNotRun", True))

            # Boundary unit cases on the real accept rule.
            checks.append(("boundary: ERE form accepted", _anchored(GOOD_ERE, GOOD_ERE.index(SK))))
            checks.append(("boundary: lookbehind accepted", _anchored(GOOD_PY, GOOD_PY.index(SK))))
            dform = D_FORMS[0]
            checks.append(("boundary: D form (?-i: accepted", _anchored(dform, dform.index(SK))))
            checks.append(
                ("boundary: bare form rejected", not _anchored(STALE_ERE, STALE_ERE.index(SK)))
            )
    finally:
        _anchored = saved
    failed = 0
    for name, ok in checks:
        print(("  ok   " if ok else "  FAIL ") + name)
        failed += 0 if ok else 1
    print(f"check-secret-pattern-parity --self-test: {len(checks) - failed}/{len(checks)} passed")
    return 0 if failed == 0 else 1


def must_fail() -> int:
    """Teeth: with the boundary rule neutered, the self-test must go red."""
    print("must-fail: running the self-test with _anchored() always True")
    rc = self_test(anchored_fn=lambda text, i: True)
    if rc == 0:
        print("must-fail: FAIL — the self-test passed with the boundary check disabled")
        return 1
    print("must-fail: OK — the self-test fails when the boundary check is disabled")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.must_fail:
        return must_fail()
    try:
        findings = run(Path(args.root), COPIES)
    except CouldNotRun as exc:
        print(f"check-secret-pattern-parity: COULD NOT RUN — {exc}", file=sys.stderr)
        return 1
    if findings:
        for f in findings:
            print("  " + f)
        print(
            f"check-secret-pattern-parity: {len(findings)} drift finding(s) across "
            f"{len(COPIES)} listed copies"
        )
        return 2
    print(f"check-secret-pattern-parity: OK — {len(COPIES)} copies in parity, no unlisted copy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
