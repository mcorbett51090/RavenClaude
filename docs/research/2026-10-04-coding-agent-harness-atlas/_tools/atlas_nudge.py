#!/usr/bin/env python3
"""Session-start nudge: tell the session when the atlas is behind the coding agent it runs on.

It reads the Claude Code version from the local session registry (~/.claude/sessions/*.json, the
way the plugin's own session-start banner does), reads the version the atlas was written against
from data/snapshot.json, and prints one line only when they differ. Equal versions, a missing
file or any error print nothing. It starts no process, makes no network call and always exits 0,
so it can never slow or block a session.

Marketplace-only: register it in this repository's .claude/settings.json, never in a plugin's
hooks.json (consumers have no atlas). The entry is in the atlas README.
"""

import json
import os
import re
import sys
from pathlib import Path

HOST = "claude-code"
VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+")
SESSION_CAP = 20
WATCH = "docs/research/2026-10-04-coding-agent-harness-atlas/_tools/watch.py"


def live_version(home):
    """The Claude Code version of the newest session on this machine, or None."""
    sessions = Path(home) / ".claude" / "sessions"
    if not sessions.is_dir():
        return None
    files = sorted(sessions.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in files[:SESSION_CAP]:
        try:
            version = json.loads(path.read_text(encoding="utf-8")).get("version")
        except (OSError, ValueError, AttributeError):
            continue
        if isinstance(version, str) and VERSION.match(version):
            return version
    return None


def atlas_dirs(project_dir):
    return sorted(Path(project_dir).glob("docs/research/*-coding-agent-harness-atlas"))


def nudge(project_dir, home):
    """The one line to show, or None when there is nothing to say."""
    live = live_version(home)
    dirs = atlas_dirs(project_dir)
    if not live or not dirs:
        return None
    data = dirs[-1] / "data"
    try:
        snapshot = json.loads((data / "snapshot.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    column = next(
        (
            c
            for c in snapshot.get("columns", [])
            if isinstance(c, dict) and c.get("surface") == HOST
        ),
        {},
    )
    written = column.get("version")
    if not isinstance(written, str) or written == live:
        return None
    checked = "no watch baseline yet"
    try:
        accepted = json.loads((data / "watch-baseline.json").read_text(encoding="utf-8")).get(
            "accepted"
        )
        if isinstance(accepted, str):
            checked = f"docs last checked {accepted}"
    except (OSError, ValueError):
        pass
    return (
        f"Atlas drift: the harness atlas was written against Claude Code {written}; this machine "
        f"runs {live}. Lever, permission and hook facts may have moved ({checked}). Run "
        f"`python3 {WATCH} check --out /tmp/atlas-watch` to see what changed."
    )


def main(project_dir=None, home=None):
    try:
        project = project_dir or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
        line = nudge(project, home or Path.home())
    except Exception:  # noqa: BLE001 - a nudge must never fail a session
        return 0
    if line:
        sys.stdout.write(
            json.dumps(
                {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": line}}
            )
            + "\n"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
