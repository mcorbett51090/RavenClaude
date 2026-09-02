#!/usr/bin/env python3
"""handoff-successor-ack.py — SessionStart startup handshake.

Reads every .ravenclaude/handoff-pending*.json marker (written by
handoff-spawn.sh). The glob matches both the legacy unscoped
handoff-pending.json name and the task_id-scoped handoff-pending-<slug>.json
form handoff-spawn.sh now writes (concurrent invocations for different tasks
each get their own marker, so one never clobbers or deletes another's). For
each marker that is fresh and well-formed, writes
.ravenclaude/runs/<task-id>/successor-ack.json and clears that marker.

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


def _pending_candidates(root: Path) -> list[Path]:
    # Matches both the legacy exact "handoff-pending.json" (zero-width glob
    # match on the "*") and the task_id-scoped "handoff-pending-<slug>.json"
    # form. Sorted for deterministic processing order across a run.
    try:
        return sorted((root / ".ravenclaude").glob("handoff-pending*.json"))
    except OSError:
        return []


def _process_one(pending_path: Path, root: Path, payload: dict) -> None:
    if not pending_path.is_file():
        return
    try:
        pending = json.loads(pending_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    if not isinstance(pending, dict):
        return
    task = pending.get("task_id")
    if not isinstance(task, str) or "/" in task or task in (".", ".."):
        return
    created = pending.get("created_at")
    if isinstance(created, str):
        try:
            ts = datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=timezone.utc
            )
            age = (datetime.now(timezone.utc) - ts).total_seconds()
            if age > MAX_PENDING_AGE_SEC:
                pending_path.unlink(missing_ok=True)
                return
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
        return
    try:
        pending_path.unlink(missing_ok=True)
    except OSError:
        pass


def main() -> int:
    payload = _payload()
    # Compact / resume / fork are not a successor start.
    src = _source(payload).lower()
    if src in ("compact", "resume", "fork", "clear"):
        return 0

    root = _root(payload)
    for pending_path in _pending_candidates(root):
        _process_one(pending_path, root, payload)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
