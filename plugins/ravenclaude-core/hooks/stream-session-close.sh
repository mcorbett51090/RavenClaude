#!/usr/bin/env bash
# stream-session-close.sh
# Stop hook (P1, Agentic Work-Streams). When a session ends AND a work-stream is
# active, append ONE derived "session_closed" event to that stream's history and
# refresh its state.md resume snapshot — the crash-resilience anchor (a resumed
# session reads state.md to know where to pick up).
#
# DERIVED-ONLY (no-egress invariant): the event carries only the session id (a FK
# back to runs/<id>/, not prompt content), an event-kind, and a count of events
# already recorded on the stream this session. It NEVER reads or writes prompt
# text — stream-ops.append_event refuses a raw-content field by construction, and
# this hook passes only session_id + a derived summary string.
#
# FAIL-SAFE: no python3 / no active stream / no streams store / any error -> silent
# no-op, exit 0. A Stop hook must never block the stop on its own failure.
#
# Wired in hooks.json (Stop) + the dev-mirror .claude/settings.json.

set -euo pipefail

# Read the Stop payload from stdin (so _emit-event-style session-id resolution
# could work later); we only need it to find the session id, best-effort.
payload="$(cat 2>/dev/null || true)"

project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -d "$project_dir" ] || exit 0

# python3 is required to touch the store fail-safely. Absent -> no-op.
command -v python3 >/dev/null 2>&1 || exit 0

# Resolve the ops library: ${CLAUDE_PLUGIN_ROOT} when installed, else in-repo.
ops="${CLAUDE_PLUGIN_ROOT:-}/scripts/stream-ops.py"
if [ ! -f "$ops" ]; then
  scripts_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../scripts" 2>/dev/null && pwd || true)"
  ops="${scripts_dir:-}/stream-ops.py"
fi
[ -f "$ops" ] || exit 0

# Resolve the session id: $CLAUDE_SESSION_ID, else the payload's .session_id, else "".
session_id="${CLAUDE_SESSION_ID:-}"
if [ -z "$session_id" ] && [ -n "$payload" ]; then
  if command -v jq >/dev/null 2>&1; then
    session_id="$(printf '%s' "$payload" | jq -r '.session_id // empty' 2>/dev/null || true)"
  fi
fi

# Everything else is done in python (fail-safe by contract): if no stream is
# active, it no-ops; otherwise it appends a derived session_closed event + state.md.
python3 - "$ops" "$project_dir" "$session_id" <<'PY' 2>/dev/null || true
import importlib.util
import sys

ops_path, root, session_id = sys.argv[1], sys.argv[2], (sys.argv[3] or None)
try:
    spec = importlib.util.spec_from_file_location("stream_ops", ops_path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
except Exception:
    sys.exit(0)

try:
    active = m.read_active(root)
    if not active:
        sys.exit(0)
    # How many events does this stream already carry? (a derived count only)
    events = m.read_history(root, active)
    count = len(events)
    # Append a derived session-close marker (no prompt text anywhere).
    m.append_event(
        root,
        active,
        kind="session_closed",
        session_id=session_id,
        summary=f"session ended; {count} event(s) recorded on this stream",
    )
    # Refresh the resume snapshot so a crash/resume can pick up here.
    m.write_state(
        root,
        active,
        summary=(
            f"Stream '{active}' had {count + 1} recorded event(s) as of the last "
            "session close. Resume by re-activating it: rc streams set-active "
            f"{active}. (This snapshot carries derived labels only — see history.jsonl.)"
        ),
        session_id=session_id,
    )
except Exception:
    sys.exit(0)
PY

exit 0
