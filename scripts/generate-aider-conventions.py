#!/usr/bin/env python3
"""Project AGENTS.md onto Aider's CONVENTIONS.md.

Multi-host audit MH-26. The audit's P0 half — this repo *claiming* Aider read
`AGENTS.md` natively — was corrected in prose earlier. This is the half that makes
the corrected claim actionable instead of merely honest.

--------------------------------------------------------------------------------
WHY A PROJECTION AND NOT A POINTER
--------------------------------------------------------------------------------
`[docs-verified 2026-07-28 — aider.chat/docs/usage/conventions.html]` Aider's
documented mechanism is **`CONVENTIONS.md`**, and it is loaded **only on explicit
opt-in** — `aider --read CONVENTIONS.md`, or a `read:` entry in `.aider.conf.yml`.
`AGENTS.md` is not mentioned on that page at all.

So an Aider user gets **nothing** from this repo's guidance unless two things are
true: the file exists under the name Aider looks for, AND the opt-in is authored.
A pointer file saying "read AGENTS.md" fails the first condition; documentation
alone fails the second. Hence: generate the file, and ship the config that opts in.

Every other host lane here bridges *enforcement*. This one cannot — **Aider has no
hooks API**, so nothing in this repo can gate an Aider session in-loop and CI is
the only backstop. The generated file says that plainly rather than implying a
protection that is not there.

--------------------------------------------------------------------------------
FAIL LOUDLY ON A MOVED HEADER
--------------------------------------------------------------------------------
Sections are extracted by exact `## ` header match and a missing header RAISES.
That is deliberate and copied from the Copilot projector: a rename upstream should
fail the build, not silently ship a CONVENTIONS.md with a hole in it. A projection
that degrades quietly is how a host lane rots — which is the failure this audit
spent itself documenting.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_AGENTS = _REPO / "AGENTS.md"

# The sections an Aider session actually needs to behave correctly here. Chosen for
# what changes an agent's ACTIONS, not for completeness: style, how to verify, where
# files may go, how to land work, and the honesty discipline.
_SECTIONS = [
    "## Code style",
    "## Layout & boundary rules",
    "## Where work files go — the cross-CLI storage contract (READ THIS BEFORE WRITING ANY FILE)",
    "## Testing instructions",
    "## PR conventions",
    "## House rules",
    "## Accuracy discipline (cross-tool pointer)",
]

_PREAMBLE = """# CONVENTIONS.md

> **GENERATED — do not hand-edit.** Projected from `AGENTS.md` by
> `scripts/generate-aider-conventions.py`. Re-run the installer to refresh.
> `AGENTS.md` is the canonical source; if this file and it ever disagree, it wins.

This file exists because **Aider does not read `AGENTS.md`**. Aider's documented
mechanism is `CONVENTIONS.md`, loaded **only on explicit opt-in** — either
`aider --read CONVENTIONS.md` or a `read:` entry in `.aider.conf.yml`
(`[docs-verified — aider.chat/docs/usage/conventions.html]`). The installer writes
that opt-in for you; if you cloned this repo without running it, add it yourself or
Aider will never load this file.

## ⚠️ What does NOT protect you here

**Aider has no hooks API, so none of this repository's guardrails run in your
session** — not the layout gate, not the destructive-command guard, not the
command-review tribunal, not the runaway brake. Under Claude Code, Copilot CLI,
Codex and Cursor those fire in-loop and can block a bad command before it runs.
Under Aider **nothing does**, and CI is the only backstop — which means a mistake
is caught after it is committed, not before it executes.

Treat every rule below as something **you** must uphold rather than something the
tooling will catch. That is not a nice-to-have framing; it is the actual
difference between this host and the others.

---
"""


def extract_section(text: str, header: str) -> str:
    """Return a `## ` section, header line through the line before the next `## `.

    Raises on a missing header so an upstream rename fails the build loudly rather
    than silently shipping a file with a hole in it.
    """
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.rstrip() == header:
            start = i
            break
    if start is None:
        raise ValueError(
            f"AGENTS.md has no section {header!r}. It was renamed or removed — update "
            "_SECTIONS in this projector rather than letting the projection ship "
            "incomplete."
        )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "\n".join(lines[start:end]).rstrip()


def build() -> str:
    text = _AGENTS.read_text(encoding="utf-8")
    parts = [_PREAMBLE.rstrip()]
    for header in _SECTIONS:
        parts.append(extract_section(text, header))
    return "\n\n".join(parts) + "\n"


AIDER_CONF = """# Aider configuration — written by `ravenclaude install --host aider`.
#
# `read:` is the opt-in that makes Aider load the projected conventions. Without
# it Aider reads NOTHING from this repository's guidance
# (docs-verified: aider.chat/docs/usage/conventions.html).
#
# NOTE: Aider has no hooks API, so no RavenClaude guardrail runs in an Aider
# session. CI is the only backstop on this host.
read:
  - CONVENTIONS.md
"""


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description="Project AGENTS.md onto CONVENTIONS.md.")
    ap.add_argument("--out")
    ap.add_argument("--conf-out")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv[1:])

    try:
        body = build()
    except (ValueError, OSError) as exc:
        print(f"aider-conventions: {exc}", file=sys.stderr)
        return 1

    if args.check:
        missing = [h for h in _SECTIONS if h not in body]
        if missing:
            print(f"aider-conventions: sections missing from output: {missing}", file=sys.stderr)
            return 1
        if "no hooks API" not in body:
            print(
                "aider-conventions: the no-enforcement warning is absent — the file "
                "would imply guardrail coverage Aider does not have.",
                file=sys.stderr,
            )
            return 1
        print(
            f"Aider conventions OK — {len(_SECTIONS)} sections projected, "
            "no-enforcement warning present."
        )
        return 0

    if args.out:
        Path(args.out).write_text(body, encoding="utf-8")
    else:
        sys.stdout.write(body)
    if args.conf_out:
        Path(args.conf_out).write_text(AIDER_CONF, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
