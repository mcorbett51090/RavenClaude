#!/usr/bin/env python3
"""Fail if a plugin file-hook reads only `$1` for its target path with no stdin fallback.

Root-cause gate for the 2026-07 class of *inert* file hooks: `hooks.json` wires a
PostToolUse/PreToolUse file hook as `script.sh "$CLAUDE_TOOL_FILE_PATH"`, but
`$CLAUDE_TOOL_FILE_PATH` is **not** a real Claude Code hook variable — under Claude
Code the tool call arrives as JSON on stdin (`{"tool_input":{"file_path":…}}`). A
hook that reads only `file="${1:-}"` therefore gets an empty path and silently
exits 0 without ever running its check. The whole in-editor enforcement/advisory
surface goes dark with no signal. See plugins/ravenclaude-core/skills/set-posture/
SKILL.md for the canonical stdin-JSON hook contract, and guard-destructive.sh /
regen-on-manifest-change.sh for the correct dual-source pattern.

A hook is OFFENDING when it reads `file="${1:-}"` (or `path="${1:-}"`) but does NOT
also resolve `.tool_input.file_path` from stdin. Scans `<root>/plugins/*/hooks/*.sh`,
skipping `test-*.sh` fixtures. Exit 0 = clean, 1 = at least one offending hook
(printed as file:line).
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys

# Reads the target path straight from the positional arg with the ${var:-} idiom.
# Case-insensitive (2026-07-09): the uppercase `FILE="${1:-}"` idiom is used by
# dozens of advisory hooks and was silently missed by a case-sensitive match, so
# the gate passed while those hooks were inert. Also tolerate a leading
# local/declare/readonly/export prefix so a scoped assignment still matches.
_ARG_PATH = re.compile(
    r'^\s*(?:local\s+|declare\s+|readonly\s+|export\s+)?(?:file|path|target)="\$\{1:-\}"',
    re.IGNORECASE,
)
# The stdin-JSON fallback any correct file hook carries.
_STDIN_FALLBACK = re.compile(r"tool_input\.file_path")


def offending(path: str) -> int | None:
    """Return the 1-indexed line of the arg-only read if the hook is offending, else None."""
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return None
    # Scope the fallback search to NON-COMMENT code lines (Finding 6): a bare textual
    # mention of `tool_input.file_path` in a comment or diagnostic string must not
    # exonerate an inert hook whose code only reads `file="${1:-}"`. Mirrors the
    # comment handling in check-grep-ere-pcre.py (lines starting with `#` skipped).
    code = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
    if _STDIN_FALLBACK.search(code):
        return None  # has the fallback in real code — fine
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("#"):
            continue
        if _ARG_PATH.match(line):
            return n
    return None  # doesn't read a positional path at all — not a file hook we gate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repo root to scan (default: cwd).")
    args = parser.parse_args(argv)

    pattern = os.path.join(args.root, "plugins", "*", "hooks", "*.sh")
    violations: list[str] = []
    for path in sorted(glob.glob(pattern)):
        if os.path.basename(path).startswith("test-"):
            continue
        lineno = offending(path)
        if lineno is not None:
            rel = os.path.relpath(path, args.root)
            violations.append(
                f"  {rel}:{lineno}: reads $1 only, no stdin .tool_input.file_path fallback"
            )

    if violations:
        print(
            "Plugin file-hooks read only $1 (empty under Claude Code — the hook "
            "silently no-ops). Add the stdin-JSON fallback (see guard-destructive.sh):",
            file=sys.stderr,
        )
        for v in violations:
            print(v, file=sys.stderr)
        return 1

    print("hook-stdin-fallback check passed: every plugin file-hook resolves the path from stdin.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
