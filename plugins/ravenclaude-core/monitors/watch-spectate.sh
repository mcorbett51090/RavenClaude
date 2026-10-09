#!/usr/bin/env bash
# watch-spectate.sh
# Reactive Spectate push mirror for ravenclaude-core (BUILD-PLAN v0.6).
#
# WHAT IT IS
#   The *push* complement to the loopback /spectate page. That page is a pull
#   surface — you open it and watch the loop. This monitor streams a *derived*
#   subset of spectate-events.jsonl to Claude Code as native notifications so
#   the agent hears permission waits, steer actions, and failures as they land
#   without being asked to open the UI.
#
#   Declared in monitors/monitors.json with
#   `when: "on-skill-invoke:spectate"` (NOT `when: always`). Starts the first
#   time the `spectate` skill is dispatched and stays up for the session.
#   Cost bound: ordinary sessions that never invoke the skill never start it.
#
# WHAT IT EMITS  (injection surface — read before changing)
#   Every stdout line becomes a Claude notification. Emit DERIVED labels only
#   from the whitelist: kind, asserted_status, tool.name, tool.family,
#   steer.action. NEVER echo session_id, ts, tool.target (may hold a path),
#   note text, args, prompts, or free-form detail.
#
#   Only high-signal kinds are mirrored (permission.*, steer.applied,
#   tool.fail, session.*, subagent.*, *.truncated). tool.pre/post and
#   prompt.submit are skipped to avoid notification spam.
#
# READ-ONLY / FAIL-SAFE
#   Same contract as watch-run-state.sh: resolve newest spectate-events.jsonl,
#   never `tail -F <glob>`, re-resolve on rotation, portable stat, sourced-guard
#   for tests.
#
# CLAUDE-CODE-ONLY
#   Plugin monitors are Claude Code v2.1.105+. No Copilot equivalent — the
#   /spectate page remains the pull surface there.

set -euo pipefail

POLL_SECONDS="${RC_SPECTATE_MONITOR_POLL_SECONDS:-${RC_MONITOR_POLL_SECONDS:-5}}"
case "$POLL_SECONDS" in
  '' | *[!0-9]*) POLL_SECONDS=5 ;;
esac
[ "$POLL_SECONDS" -lt 1 ] && POLL_SECONDS=5

# Kinds worth a notification (fixed vocabulary — edit with care).
_interesting_kind() {
  case "$1" in
    permission.request | permission.resolve | steer.applied | tool.fail | \
      session.start | session.end | subagent.start | subagent.stop | \
      stream.truncated | emitter.truncated)
      return 0
      ;;
    *) return 1 ;;
  esac
}

newest_spectate_log() {
  # Re-resolve each call so CLAUDE_PROJECT_DIR changes (tests / resume) bind.
  local runs_dir="${CLAUDE_PROJECT_DIR:-$PWD}/.ravenclaude/runs"
  [ -d "$runs_dir" ] || return 0
  local newest="" newest_mt=0 _f _mt
  while IFS= read -r -d '' _f; do
    _mt="$(stat -c '%Y' "$_f" 2>/dev/null || stat -f '%m' "$_f" 2>/dev/null)" || continue
    [ -n "$_mt" ] || continue
    if [ "$_mt" -gt "$newest_mt" ] 2>/dev/null; then
      newest_mt="$_mt"
      newest="$_f"
    fi
  done < <(find "$runs_dir" -maxdepth 2 -name 'spectate-events.jsonl' -type f -print0 2>/dev/null)
  [ -n "$newest" ] && printf '%s\n' "$newest"
}

# Derive and print ONE notification line from ONE spectate JSONL line.
emit_spectate_derived() {
  local json_line="$1"
  [ -n "$json_line" ] || return 0

  local kind status tool_name tool_family steer_action
  if command -v jq >/dev/null 2>&1; then
    kind="$(printf '%s' "$json_line" | jq -r '.kind // empty' 2>/dev/null || true)"
    status="$(printf '%s' "$json_line" | jq -r '.asserted_status // empty' 2>/dev/null || true)"
    tool_name="$(printf '%s' "$json_line" | jq -r '.tool.name // empty' 2>/dev/null || true)"
    tool_family="$(printf '%s' "$json_line" | jq -r '.tool.family // empty' 2>/dev/null || true)"
    steer_action="$(printf '%s' "$json_line" | jq -r '.steer.action // empty' 2>/dev/null || true)"
  else
    kind="$(printf '%s' "$json_line" | grep -oE '"kind"[[:space:]]*:[[:space:]]*"[^"]*"' | head -n1 | sed -E 's/.*:[[:space:]]*"([^"]*)".*/\1/' || true)"
    status="$(printf '%s' "$json_line" | grep -oE '"asserted_status"[[:space:]]*:[[:space:]]*"[^"]*"' | head -n1 | sed -E 's/.*:[[:space:]]*"([^"]*)".*/\1/' || true)"
    tool_name="$(printf '%s' "$json_line" | grep -oE '"name"[[:space:]]*:[[:space:]]*"[^"]*"' | head -n1 | sed -E 's/.*:[[:space:]]*"([^"]*)".*/\1/' || true)"
    tool_family="$(printf '%s' "$json_line" | grep -oE '"family"[[:space:]]*:[[:space:]]*"[^"]*"' | head -n1 | sed -E 's/.*:[[:space:]]*"([^"]*)".*/\1/' || true)"
    steer_action="$(printf '%s' "$json_line" | grep -oE '"action"[[:space:]]*:[[:space:]]*"[^"]*"' | head -n1 | sed -E 's/.*:[[:space:]]*"([^"]*)".*/\1/' || true)"
  fi

  kind="$(printf '%s' "$kind" | tr -d '\r\n')"
  status="$(printf '%s' "$status" | tr -d '\r\n')"
  tool_name="$(printf '%s' "$tool_name" | tr -d '\r\n')"
  tool_family="$(printf '%s' "$tool_family" | tr -d '\r\n')"
  steer_action="$(printf '%s' "$steer_action" | tr -d '\r\n')"

  [ -n "$kind" ] || return 0
  _interesting_kind "$kind" || return 0

  local glyph="•"
  case "$kind" in
    permission.request) glyph="⏸" ;;
    permission.resolve)
      case "$status" in
        succeeded) glyph="✓" ;;
        failed) glyph="⚠" ;;
        *) glyph="•" ;;
      esac
      ;;
    steer.applied)
      case "$steer_action" in
        interrupt | deny | pause) glyph="⚠" ;;
        approve | resume) glyph="✓" ;;
        *) glyph="•" ;;
      esac
      ;;
    tool.fail | stream.truncated | emitter.truncated) glyph="⚠" ;;
    session.start | subagent.start) glyph="→" ;;
    session.end | subagent.stop) glyph="■" ;;
  esac

  local line="$glyph spectate $kind"
  [ -n "$tool_name" ] && line="$line ${tool_name}"
  [ -n "$tool_family" ] && [ -z "$tool_name" ] && line="$line (${tool_family})"
  [ -n "$status" ] && line="$line [$status]"
  [ -n "$steer_action" ] && line="$line (steer: $steer_action)"
  printf '%s\n' "$line"
}

_run_spectate_monitor_loop() {
  local current=""
  while true; do
    local log
    log="$(newest_spectate_log || true)"

    if [ -z "$log" ] || [ ! -f "$log" ]; then
      current=""
      sleep "$POLL_SECONDS"
      continue
    fi

    if [ "$log" != "$current" ]; then
      current="$log"
      local tail_pid newer
      ( tail -n0 -F "$log" 2>/dev/null | while IFS= read -r jsonl_line; do
          emit_spectate_derived "$jsonl_line" || true
        done ) &
      tail_pid=$!

      while kill -0 "$tail_pid" 2>/dev/null; do
        sleep "$POLL_SECONDS"
        newer="$(newest_spectate_log || true)"
        if [ "$newer" != "$current" ] || [ ! -f "$current" ]; then
          pkill -P "$tail_pid" 2>/dev/null || true
          kill "$tail_pid" 2>/dev/null || true
          wait "$tail_pid" 2>/dev/null || true
          break
        fi
      done
    else
      sleep "$POLL_SECONDS"
    fi
  done
}

if [ "${BASH_SOURCE[0]:-$0}" = "${0}" ]; then
  _run_spectate_monitor_loop
fi
