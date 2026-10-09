#!/usr/bin/env bash
# spectate-steer.sh — v0.3 pause-as-deny + capped note injection
#
# Reads .ravenclaude/runs/<session>/spectate-steer.json written by
# POST /__spectate/steer. Only active when comfort-posture has
# `spectate_steer: on` (absent => off).
#
# PreToolUse: if paused -> deny (permissionDecision) — pause-as-deny MVP.
# UserPromptSubmit / PreToolUse: if note_pending -> additionalContext (capped),
# then clear the note. Fail-open on any error.

set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd)" || here="."
payload="$(cat 2>/dev/null || true)"
event_hint="${1:-}"

if [ -f "$here/_portable.sh" ]; then
  # shellcheck source=/dev/null
  . "$here/_portable.sh" 2>/dev/null || true
fi

project_dir="${CLAUDE_PROJECT_DIR:-}"
[ -n "$project_dir" ] && [ -d "$project_dir" ] || exit 0

posture="$project_dir/.ravenclaude/comfort-posture.yaml"
[ -f "$posture" ] || exit 0
grep -Eqi '^[[:space:]]*spectate_steer:[[:space:]]*on[[:space:]]*$' "$posture" 2>/dev/null || exit 0

command -v python3 >/dev/null 2>&1 || exit 0

export CLAUDE_PROJECT_DIR="$project_dir"
export CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID:-}"
export CLAUDE_HOOK_EVENT="${CLAUDE_HOOK_EVENT:-${HOOK_EVENT:-}}"
export SPECTATE_EVENT_HINT="$event_hint"
export SPECTATE_PAYLOAD="$payload"
export SPECTATE_HOOK_DIR="$here"

python3 - <<'PY2' || exit 0
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

hook_dir = Path(os.environ.get("SPECTATE_HOOK_DIR") or ".")
candidates = [
    hook_dir.parent / "scripts",
]
plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
if plugin_root:
    candidates.insert(0, Path(plugin_root) / "scripts")
proj = Path(os.environ["CLAUDE_PROJECT_DIR"])
candidates.append(proj / "plugins" / "ravenclaude-core" / "scripts")

store = None
for d in candidates:
    if (d / "spectate_store.py").is_file():
        sys.path.insert(0, str(d))
        import spectate_store as store  # noqa: E402
        break
if store is None:
    raise SystemExit(0)

project = Path(os.environ["CLAUDE_PROJECT_DIR"])
sid = (os.environ.get("CLAUDE_SESSION_ID") or "").strip()
if not store.validate_session_id(sid):
    try:
        raw = os.environ.get("SPECTATE_PAYLOAD") or ""
        obj = json.loads(raw) if raw.strip() else {}
        sid = str(obj.get("session_id") or obj.get("sessionId") or "")
    except Exception:
        sid = ""
if not store.validate_session_id(sid):
    raise SystemExit(0)

pending = store.read_steer_pending(project, sid) or {}
event = (os.environ.get("CLAUDE_HOOK_EVENT") or os.environ.get("SPECTATE_EVENT_HINT") or "").lower()
event_key = event.replace("_", "").replace("-", "")

paused = bool(pending.get("paused"))
note_pending = bool(pending.get("note_pending"))

if paused and "pretooluse" in event_key:
    reason = "Spectate steer: paused from /spectate (POST /__spectate/steer)."
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    raise SystemExit(0)

if note_pending and (
    "userpromptsubmit" in event_key
    or "pretooluse" in event_key
    or "sessionstart" in event_key
):
    note = store.consume_steer_note(project, sid)
    if note:
        ctx = "[Spectate steer note] " + note
        print(json.dumps({"hookSpecificOutput": {"additionalContext": ctx}}))
raise SystemExit(0)
PY2
exit 0
