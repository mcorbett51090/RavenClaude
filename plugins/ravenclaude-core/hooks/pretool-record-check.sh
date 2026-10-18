#!/usr/bin/env bash
# pretool-record-check.sh — PostToolUse: warn loudly when the pre-tool review did
# not run for a tool call (AppSec hook-env, 2026-10-18).
#
# thing-orchestrator.sh writes a record keyed by tool_use_id the moment it starts
# (before any short-circuit), under ${XDG_RUNTIME_DIR:-/tmp}/ravenclaude-$UID/pretool/.
# If that hook could not even start — a planted PATH with no bash, a broken
# interpreter, a timeout before our first line — Claude Code treats it as a
# NON-blocking error and the tool runs anyway. Afterwards, this hook finds no record
# and says so: a systemMessage for the user, additionalContext for the model, a
# stderr line, and a line in <runtime>/review-gap.log reading
# 'pre-tool review did not run'. It cannot undo the call; it makes the gap visible.
#
# Registered with the SAME matcher as thing-orchestrator.sh. Never blocks (exit 0).
set -uo pipefail
. "$(dirname "$0")/_rc-runtime.sh" 2>/dev/null || exit 0
command -v jq >/dev/null 2>&1 || exit 0
# A tribunal seat's own `claude -p` (valid seat-child lock) skips the orchestrator
# by design, so there is no record to find; stay quiet there only.
if [ -n "${THING_SEAT_ACTIVE:-}" ] && _rc_seat_child_ok "${THING_SEAT_CHILD_NONCE:-}"; then exit 0; fi

payload="$(cat 2>/dev/null || true)"
id="$(_rc_safe_id "$(printf '%s' "$payload" | jq -r '.tool_use_id // empty' 2>/dev/null)")"
[ -n "$id" ] || exit 0
tool="$(printf '%s' "$payload" | jq -r '.tool_name // "?"' 2>/dev/null)"
sid="$(_rc_safe_id "$(printf '%s' "$payload" | jq -r '.session_id // empty' 2>/dev/null)")"

d="$(_rc_runtime_subdir pretool)" || exit 0
if [ -f "$d/$id" ]; then
  rm -f "$d/$id" 2>/dev/null || true
  find "$d" -maxdepth 1 -type f -mmin +120 -exec rm -f {} + 2>/dev/null || true
  exit 0
fi

line="$(date -u +%Y-%m-%dT%H:%M:%SZ) pre-tool review did not run tool=${tool} tool_use_id=${id} session=${sid:-?}"
printf '%s\n' "$line" >>"$(dirname "$d")/review-gap.log" 2>/dev/null || true
echo "[RavenClaude] WARNING: pre-tool review did not run for ${tool} (${id})" >&2
msg="⚠ RavenClaude: pre-tool review did not run for ${tool} (tool_use_id ${id}). The command-review hook never started, so this call was NOT reviewed. Check for a planted PATH/BASH_ENV in project settings or a broken hook launch before continuing."
jq -cn --arg m "$msg" '{systemMessage:$m,hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$m}}'
exit 0
