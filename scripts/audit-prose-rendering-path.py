#!/usr/bin/env python3
"""audit-prose-rendering-path.py — P1 / S4, and the standing gate it becomes.

⛔ WHY THIS EXISTS. Authored concept prose (`body_md`, `summary`, `nuance`,
`refresh_when`) travels from a concept markdown file through concepts.py into
render-concepts.py, generate-dashboards.py, generate-concepts-doc.py and a CI
annotation. If ANY leg of that path interpolates the prose into a SHELL command,
one apostrophe in an authored sentence changes what runs. This repo has paid for
that class twice, and the plan calls the remaining exposure "plausibly safe,
unverified" — a standard this repo's own discipline rejects.

Two checks, both mechanical:

  A. SHELL-INTERPOLATION. Every prose consumer must handle the text with Python
     string operations only. A consumer that also calls subprocess with
     shell=True, os.system, os.popen, or commands.getoutput is REPORTED — the
     prose and the shell live in one process and the separation is no longer
     structural.

  B. APOSTROPHE-IN-SINGLE-QUOTED-BLOCK. A `.sh` file that embeds a python/awk
     program inside a single-quoted bash block dies on the first apostrophe —
     including one in a COMMENT — with a non-blocking error, so the gate fails
     OPEN and silently stops gating. Detected by re-parsing each shell file and
     asserting `bash -n` is clean, then extracting embedded single-quoted
     interpreter blocks and asserting each one compiles.

⛔ THE TEETH-BIT EXIT IS 1. Declared, never assumed — premise-gate.py uses 0 and
sync-plugin-versions.py uses 2, so a shared constant is wrong by construction.

Usage:
    audit-prose-rendering-path.py                     # report
    audit-prose-rendering-path.py --check             # gate (exit 1 on violation)
    audit-prose-rendering-path.py --must-fail         # teeth: plant, expect a catch
    audit-prose-rendering-path.py --must-fail-convention
"""

from __future__ import annotations

import argparse
import ast
import glob
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# The authored-prose fields. A file mentioning any of these is a prose consumer.
PROSE_FIELDS = ("body_md", "summary", "nuance", "refresh_when", "nuance_evidence")

# Shell-interpolation shapes. Presence in a prose consumer is the finding.
# ⛔ The strings below are DETECTOR PATTERNS and the planted --must-fail fixture,
# never calls this tool makes. The only subprocess here is a list-form
# `bash -n` with no shell. A source-scanning security check flags this file on
# the pattern text itself — the recorded "a grep is satisfied by the thing being
# described" class. Do not "fix" it by weakening the patterns; that disarms the
# detector while making the scanner quiet.
SHELL_SHAPES = (
    (re.compile(r"\bshell\s*=\s*True\b"), "subprocess(..., shell=True)"),
    (re.compile(r"\bos\.system\s*\("), "os.system()"),
    (re.compile(r"\bos\.popen\s*\("), "os.popen()"),
    (re.compile(r"\bcommands\.getoutput\s*\("), "commands.getoutput()"),
)

# A single-quoted bash block that opens an embedded interpreter program.
_EMBEDDED = re.compile(
    r"(?:python3?|awk|perl)\s+(?:-\s|-c\s|)'(?P<body>(?:[^']|\n)*?)'",
    re.MULTILINE,
)


def _root() -> Path:
    return Path(__file__).resolve().parent.parent


def find_prose_consumers(root: Path) -> list[Path]:
    """Every .py under scripts/ that reads an authored-prose field."""
    out = []
    for f in sorted(glob.glob(str(root / "scripts" / "*.py"))):
        p = Path(f)
        if p.name == Path(__file__).name:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if any(field in text for field in PROSE_FIELDS):
            out.append(p)
    return out


def check_shell_interpolation(files: list[Path], root: Path | None = None) -> list[str]:
    # ⛔ root is a PARAMETER, not _root(). The first version hard-coded the repo
    # root, so --must-fail crashed on a temp-dir fixture and exited 1 — which is
    # exactly this tool's declared teeth exit. A crash that returns the success
    # code of a teeth run is a false pass, and it is the shape this whole audit
    # exists to catch.
    root = root or _root()
    findings = []
    for p in files:
        text = p.read_text(encoding="utf-8", errors="replace")
        for rx, label in SHELL_SHAPES:
            for m in rx.finditer(text):
                line = text[: m.start()].count("\n") + 1
                findings.append(
                    f"{p.relative_to(root)}:{line}: prose consumer also uses {label} "
                    "— authored text and a shell share this process"
                )
    return findings


def _bash_syntax_clean(p: Path) -> str | None:
    try:
        r = subprocess.run(
            ["bash", "-n", str(p)], capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.SubprocessError) as exc:  # bash absent / hung
        return f"bash -n could not run ({type(exc).__name__}) — this is UNKNOWN, not clean"
    if r.returncode != 0:
        return (r.stderr or "").strip().splitlines()[0] if r.stderr else "bash -n failed"
    return None


def check_apostrophe_blocks(root: Path) -> tuple[list[str], int]:
    """bash -n every shell file, then compile embedded single-quoted python."""
    findings: list[str] = []
    shells = sorted(
        glob.glob(str(root / "scripts" / "*.sh"))
        + glob.glob(str(root / "plugins" / "*" / "hooks" / "*.sh"))
        + glob.glob(str(root / "plugins" / "*" / "scripts" / "*.sh"))
    )
    for f in shells:
        p = Path(f)
        err = _bash_syntax_clean(p)
        if err:
            findings.append(f"{p.relative_to(root)}: shell syntax — {err}")
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for m in _EMBEDDED.finditer(text):
            body = m.group("body")
            # An apostrophe cannot survive inside a single-quoted block; if the
            # extracted program looks like python and does not compile, the block
            # was truncated by one. Only python is compile-checkable here.
            head = text[max(0, m.start() - 40) : m.start()]
            if "python" not in head:
                continue
            if len(body.strip()) < 20:
                continue
            try:
                ast.parse(body)
            except SyntaxError as exc:
                line = text[: m.start()].count("\n") + 1
                findings.append(
                    f"{p.relative_to(root)}:{line}: embedded python block does not parse "
                    f"({exc.msg}) — an apostrophe may have closed the bash string early"
                )
    return findings, len(shells)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    ap.add_argument("--must-fail-convention", action="store_true")
    args = ap.parse_args()

    if args.must_fail_convention:
        print("must-fail-teeth-exit: 1")
        return 0

    root = _root()

    if args.must_fail:
        # TEETH. Plant both shapes and require the detectors to bite. A detector
        # that reports nothing on a pristine tree and was never proven to fire is
        # indistinguishable from one that never ran.
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td)
            (fake / "scripts").mkdir()
            (fake / "scripts" / "bad-consumer.py").write_text(
                "import os, subprocess\n"
                "def render(body_md):\n"
                "    subprocess.run('echo ' + body_md, shell=True)\n"
                "    os.system('echo ' + body_md)\n",
                encoding="utf-8",
            )
            shell_findings = check_shell_interpolation(
                [fake / "scripts" / "bad-consumer.py"], root=fake
            )
            # ⛔ INVERTED EXIT ON PURPOSE — see the note in
            # check-covers-completeness.py. --must-fail exits with the DECLARED
            # teeth code when the canary bites, so audit-gates can compare the
            # declaration against the observed exit instead of hard-coding one.
            if len(shell_findings) < 2:
                print("✗ must-fail: shell-interpolation detector did not bite on a")
                print("  planted consumer. The clean report on the real tree is not evidence.")
                return 0
            # Planted broken shell: an unterminated quote must trip bash -n.
            (fake / "scripts" / "bad-shell.sh").write_text(
                "#!/usr/bin/env bash\necho 'unterminated\n", encoding="utf-8"
            )
            errs, _ = check_apostrophe_blocks(fake)
            if not errs:
                print("✗ must-fail: shell-syntax detector did not bite on a planted")
                print("  unterminated single-quoted block.")
                return 0
        print("✓ must-fail: both detectors bit on planted defects.")
        print("  exiting 1, the DECLARED teeth code, so the auditor can compare.")
        return 1

    consumers = find_prose_consumers(root)
    shell_findings = check_shell_interpolation(consumers)
    apos_findings, n_shell = check_apostrophe_blocks(root)

    print("── P1/S4: authored-prose rendering path ──")
    print(f"  prose consumers traced : {len(consumers)}")
    for p in consumers:
        print(f"    · {p.relative_to(root)}")
    print(f"  shell files parsed     : {n_shell}")
    print()

    if not consumers:
        print("  ✗ zero prose consumers found. That is a broken tracer, not a clean")
        print("    path — the fields are known to be read. Refusing to report green.")
        return 2

    findings = shell_findings + apos_findings
    if findings:
        print(f"  ⛔ {len(findings)} finding(s):")
        for f in findings:
            print(f"    ✗ {f}")
    else:
        print("  ✓ every prose consumer handles authored text with Python string")
        print("    operations only; no shell interpolation on the path.")
        print("  ✓ every shell file parses, and every embedded single-quoted python")
        print("    block compiles — no apostrophe has closed a block early.")

    if args.check:
        return 1 if findings else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
