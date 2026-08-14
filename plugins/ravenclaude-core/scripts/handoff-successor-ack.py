#!/usr/bin/env python3
"""handoff-successor-ack.py — SessionStart startup handshake.

Reads .ravenclaude/handoff-pending.json (written by handoff-spawn.sh).
If it is fresh and matches this cwd, writes
.ravenclaude/runs/<task-id>/successor-ack.json and clears the pending file.

Derived values only: task_id from pending, session_id from hook env/payload,
ISO timestamp. Never echoes stdin transcript or lastAssistantMessage.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

MAX_PENDING_AGE_SEC = 300


def _payload() -> dict:
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    if not raw.strip():
        return {}
    try:
        obj = json.loads(raw)
    except ValueError:
        return {}
    return obj if isinstance(obj, dict) else {}


def _root(payload: dict) -> Path:
    cwd = (
        payload.get("workspaceRoot")
        or payload.get("cwd")
        or os.environ.get("GROK_WORKSPACE_ROOT")
        or os.environ.get("CLAUDE_PROJECT_DIR")
        or os.getcwd()
    )
    return Path(str(cwd)).resolve()


def _session_id(payload: dict) -> str:
    sid = (
        os.environ.get("GROK_SESSION_ID")
        or payload.get("sessionId")
        or payload.get("session_id")
        or ""
    )
    return sid if isinstance(sid, str) else ""


def _source(payload: dict) -> str:
    src = payload.get("source") or payload.get("matcher") or ""
    return src if isinstance(src, str) else ""


def main() -> int:
    payload = _payload()
    # Compact / resume / fork are not a successor start.
    src = _source(payload).lower()
    if src in ("compact", "resume", "fork", "clear"):
        return 0

    root = _root(payload)
    pending_path = root / ".ravenclaude" / "handoff-pending.json"
    if not pending_path.is_file():
        return 0
    try:
        pending = json.loads(pending_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0
    if not isinstance(pending, dict):
        return 0
    task = pending.get("task_id")
    if not isinstance(task, str) or "/" in task or task in (".", ".."):
        return 0
    created = pending.get("created_at")
    if isinstance(created, str):
        try:
            ts = datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=timezone.utc
            )
            age = (datetime.now(timezone.utc) - ts).total_seconds()
            if age > MAX_PENDING_AGE_SEC:
                pending_path.unlink(missing_ok=True)
                return 0
        except ValueError:
            pass

    dest = root / ".ravenclaude" / "runs" / task
    try:
        dest.mkdir(parents=True, exist_ok=True)
        ack = {
            "task_id": task,
            "session_id": _session_id(payload),
            "started_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": "started",
        }
        (dest / "successor-ack.json").write_text(
            json.dumps(ack, separators=(",", ":")) + "\n", encoding="utf-8"
        )
    except OSError:
        return 0
    try:
        pending_path.unlink(missing_ok=True)
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
