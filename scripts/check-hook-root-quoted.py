#!/usr/bin/env python3
"""Fail if a hook command leaves ${CLAUDE_PLUGIN_ROOT|PROJECT_DIR}/… unquoted.

SH-F11 (2026-10-06 repo-review): an unquoted
`${CLAUDE_PLUGIN_ROOT}/hooks/foo.sh` (or the marketplace-dev mirror
`${CLAUDE_PROJECT_DIR}/plugins/…/foo.sh`) splits on spaces when the root
path contains one. The shell then looks up a truncated path, gets exit 127,
and every fail-open guard silently no-ops.

Scans (SH-F11 — ravenclaude-core + marketplace-dev settings mirror):
  - <root>/plugins/ravenclaude-core/hooks/hooks.json → ${CLAUDE_PLUGIN_ROOT}/…
  - <root>/.claude/settings.json                     → ${CLAUDE_PROJECT_DIR}/…

Domain-plugin hooks.json files share the same shape; quoting them is a
follow-up (version-bump blast radius across ~115 plugins). Pass --all-plugins
to include every plugins/*/hooks/hooks.json.

Exit 0 = every root-path token in a `command` string is double-quoted.
Exit 1 = at least one unquoted token (printed as file → command snippet).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _iter_commands(obj):
    if isinstance(obj, dict):
        cmd = obj.get("command")
        if isinstance(cmd, str):
            yield cmd
        for v in obj.values():
            yield from _iter_commands(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _iter_commands(v)


def unquoted_tokens(cmd: str, var: str) -> list[str]:
    """Return every ${VAR}/path token in cmd that is not already double-quoted."""
    needle = "${" + var + "}"
    found: list[str] = []
    i = 0
    while True:
        idx = cmd.find(needle, i)
        if idx < 0:
            break
        before = cmd[idx - 1] if idx > 0 else ""
        j = idx + len(needle)
        if j < len(cmd) and cmd[j] == "/":
            j += 1
            while j < len(cmd) and cmd[j] not in " \t\n;\"'|&<>()":
                j += 1
        token = cmd[idx:j]
        if before != '"':
            found.append(token)
        i = j
    return found


def scan_file(path: Path, var: str) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"  {path}: cannot parse JSON ({exc})"]
    violations: list[str] = []
    for cmd in _iter_commands(data):
        for tok in unquoted_tokens(cmd, var):
            snippet = cmd if len(cmd) <= 100 else cmd[:97] + "…"
            violations.append(f"  {path}: unquoted {tok} in: {snippet}")
    return violations


def collect(root: Path, *, all_plugins: bool = False) -> list[str]:
    violations: list[str] = []
    if all_plugins:
        paths = sorted(root.glob("plugins/*/hooks/hooks.json"))
    else:
        core = root / "plugins" / "ravenclaude-core" / "hooks" / "hooks.json"
        paths = [core] if core.is_file() else []
    for path in paths:
        violations.extend(scan_file(path, "CLAUDE_PLUGIN_ROOT"))
    settings = root / ".claude" / "settings.json"
    if settings.is_file():
        violations.extend(scan_file(settings, "CLAUDE_PROJECT_DIR"))
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repo root to scan (default: cwd).")
    parser.add_argument(
        "--all-plugins",
        action="store_true",
        help="Also scan every plugins/*/hooks/hooks.json (domain follow-up).",
    )
    parser.add_argument(
        "--must-fail",
        action="store_true",
        help="Plant an unquoted canary under a temp tree and require exit 1.",
    )
    parser.add_argument(
        "--must-fail-convention",
        action="store_true",
        help="Print the declared --must-fail teeth exit code.",
    )
    args = parser.parse_args(argv)

    if args.must_fail_convention:
        # 3 — distinct from success(0)/crash(1)/argparse(2); see audit-gates rc_mustfail.
        print("must-fail-teeth-exit: 3")
        return 0

    if args.must_fail:
        import tempfile

        with tempfile.TemporaryDirectory(prefix="hook-root-quoted-") as tmp:
            root = Path(tmp)
            # Plant under ravenclaude-core so the default scan sees it.
            hooks_dir = root / "plugins" / "ravenclaude-core" / "hooks"
            hooks_dir.mkdir(parents=True)
            (hooks_dir / "hooks.json").write_text(
                json.dumps(
                    {
                        "hooks": {
                            "PreToolUse": [
                                {
                                    "matcher": "Bash",
                                    "hooks": [
                                        {
                                            "type": "command",
                                            "command": (
                                                "${CLAUDE_PLUGIN_ROOT}/hooks/guard-destructive.sh"
                                            ),
                                        }
                                    ],
                                }
                            ]
                        }
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            settings_dir = root / ".claude"
            settings_dir.mkdir(parents=True)
            (settings_dir / "settings.json").write_text(
                json.dumps(
                    {
                        "hooks": {
                            "PreToolUse": [
                                {
                                    "matcher": "Bash",
                                    "hooks": [
                                        {
                                            "type": "command",
                                            "command": (
                                                "${CLAUDE_PROJECT_DIR}/plugins/"
                                                "ravenclaude-core/hooks/"
                                                "guard-destructive.sh"
                                            ),
                                        }
                                    ],
                                }
                            ]
                        }
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            violations = collect(root)
            if not violations:
                print(
                    "check-hook-root-quoted --must-fail: planted unquoted canaries "
                    "were NOT detected — gate has no teeth",
                    file=sys.stderr,
                )
                return 0  # declared teeth exit is 3; returning 0 fails rc_mustfail
            print(
                "Unquoted ${CLAUDE_PLUGIN_ROOT|PROJECT_DIR}/… in hook commands "
                "(space in root → exit 127 → fail-open). Quote every root path:",
                file=sys.stderr,
            )
            for v in violations:
                print(v, file=sys.stderr)
            return 3

    root = Path(args.root)
    violations = collect(root, all_plugins=args.all_plugins)
    if violations:
        print(
            "Unquoted ${CLAUDE_PLUGIN_ROOT|PROJECT_DIR}/… in hook commands "
            "(space in root → exit 127 → fail-open). Quote every root path:",
            file=sys.stderr,
        )
        for v in violations:
            print(v, file=sys.stderr)
        return 1

    print(
        "hook-root-quoted check passed: every CLAUDE_PLUGIN_ROOT / "
        "CLAUDE_PROJECT_DIR path token in hook commands is double-quoted."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
