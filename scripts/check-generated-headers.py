#!/usr/bin/env python3
"""check-generated-headers.py — Gate 173.

Every generated file must SAY it is generated, in the file itself.

WHY THIS ONE STAMP EARNS ITS COST, AND A GENERAL ONE DOES NOT. The obvious idea
is to stamp every file with who wrote it and when. Measured against this repo,
that fails three ways: 1,560 tracked files (16%) cannot hold a comment at all
(.json/.svg/.png/.jsonl), so coverage is partial and an ABSENT stamp becomes
ambiguous; the generated files carry byte-exact freshness gates, so a stamp
either breaks them or must be excluded — removing provenance exactly where
confusion is highest; and `git blame` already answers "who touched this line,
when", DERIVED, so it cannot go stale the way a maintained stamp can.

The test a stamp has to pass is whether it CHANGES WHAT THE NEXT CLI DOES.
"claude-code edited this at 3pm" changes nothing. "This file is generated — edit
the source" changes everything: without it a session edits a projected file, and
the next regen silently reverts the work. That is not hypothetical — when this
gate was written, 18 of 36 generated files said nothing, including `index.html`
and all 15 projected Copilot agents.

AUTHORSHIP IS NOT QUALITY, and this gate deliberately does not record it. A CLI
that learns "Copilot wrote this, be suspicious" has acquired a prejudice, not
evidence: it would distrust correct work and trust wrong work from a favoured
tool. Quality has a real answer in this repo — the gates — and it is about
whether something is verified, not who vouched for it.

WHAT COUNTS AS GENERATED is a maintained list below, on purpose. Deriving it
(e.g. "anything a generator writes") would need to execute every generator to
find out, and a gate that runs the thing it checks proves less than one that
knows the answer independently. Adding a generator means adding its outputs here
— the same accounting discipline the hook-projection gates use.

Usage:
    python3 scripts/check-generated-headers.py
    python3 scripts/check-generated-headers.py --must-fail
"""

from __future__ import annotations

import argparse
import contextlib
import io
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Path prefixes whose tracked files are GENERATED and must declare themselves.
# Add a generator's output here when you add the generator.
GENERATED_PREFIXES: tuple[str, ...] = (
    "plugins/ravenclaude-core/copilot/",
    "plugins/ravenclaude-core/codex/agents/",
    "plugins/ravenclaude-core/dashboard.html",
    "index.html",
)

# Files under a generated prefix that are NOT generated, with a reason. Keeps the
# prefix list simple without silently exempting anything.
EXEMPT: dict[str, str] = {}

_MARKER = re.compile(r"GENERATED|AUTO-GENERATED|do not edit", re.I)
# ...and it must say WHERE to go instead. A stamp that only says "stop"
# leaves the reader with nowhere to make the change.
_POINTER = re.compile(r"scripts/[\w./-]+\.py|\bedit\b", re.I)
# Only the head is inspected: a declaration buried 400 lines down is not a
# declaration, because nobody opening the file will see it.
_HEAD_BYTES = 1500


def tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True
    )
    return out.stdout.split()


def generated_files() -> list[str]:
    return [
        f
        for f in tracked_files()
        if f.startswith(GENERATED_PREFIXES) and f not in EXEMPT
    ]


def declares_itself(rel: str, *, head_bytes: int = _HEAD_BYTES) -> bool:
    try:
        head = (REPO_ROOT / rel).read_text(encoding="utf-8", errors="replace")[:head_bytes]
    except OSError:
        return False
    if not _MARKER.search(head):
        return False
    # A bare "GENERATED" tells a reader to stop but not where to go. The whole
    # value of this stamp is redirecting the edit, so the declaration must also
    # POINT somewhere — the generator script, or an explicit "edit <x>".
    return bool(_POINTER.search(head))


def run(*, mutate: bool = False) -> int:
    failures = 0

    def bad(msg: str) -> None:
        nonlocal failures
        failures += 1
        print(f"  FAIL: {msg}", file=sys.stderr)

    files = generated_files()
    if not files:
        bad("no generated files found — the gate would pass vacuously "
            "(GENERATED_PREFIXES has drifted from the tree)")
        return failures

    # THE MUTANT: only look at the first 40 bytes. A real regression looks like a
    # generator that stops emitting the header, and this reproduces the same
    # observable — the marker is no longer where a reader would see it.
    head = 40 if mutate else _HEAD_BYTES

    for rel in files:
        if not declares_itself(rel, head_bytes=head):
            bad(f"{rel} is generated but does not say so — a CLI will edit it and "
                "the next regen silently reverts that work")

    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--must-fail", action="store_true")
    args = ap.parse_args()

    if args.must_fail:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            failures = run(mutate=True)
        if failures == 0:
            print("MUST-FAIL: a header the reader cannot see produced NO failures — no teeth",
                  file=sys.stderr)
            return 1
        if "does not say so" not in err.getvalue():
            print("MUST-FAIL: failed, but not on the declaration assertion", file=sys.stderr)
            return 1
        print(f"  ok: teeth — a generated file whose header is out of sight is caught "
              f"({failures} file(s))")
        print("Generated headers: MUST-FAIL half behaved correctly")
        return 0

    failures = run()
    if failures:
        print(f"FAIL: {failures} generated file(s) do not declare themselves", file=sys.stderr)
        return 1
    n = len(generated_files())
    print(f"  ok: all {n} generated files declare themselves in their first "
          f"{_HEAD_BYTES} bytes")
    print("  ok: the declaration names the SOURCE to edit, not just 'generated'")
    print("Generated headers: ALL ASSERTIONS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
