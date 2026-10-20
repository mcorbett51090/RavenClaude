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
#   tool.fail, session.*, subagent.*, *.truncated, and turn.end ONLY when its
#   asserted_status is failed — a StopFailure, v0.16). tool.pre/post,
#   prompt.submit and ordinary turn.end are skipped to avoid notification spam.
#
# READ-ONLY / FAIL-SAFE
#   Same contract as watch-run-state.sh: resolve newest spectate-events.jsonl,
#   never `tail -F <glob>`, re-resolve on rotation, portable stat, sourced-guard
#   for tests. Also the same log choice: with $CLAUDE_SESSION_ID set, follow
#   only runs/<that id>/ (no cross-session flapping); a log present at startup
#   is joined at its end, a log first seen later is read from line 1 (so its
#   session.start, the event that created it, is not lost).
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
    permission.request | permission.resolve | steer.applied | tool.fail | turn.end | \
      session.start | session.end | subagent.start | subagent.stop | \
      stream.truncated | emitter.truncated)
      return 0
      ;;
    *) return 1 ;;
  esac
}

# The run-dir name the spectate emitter uses for $CLAUDE_SESSION_ID (same rule
# as sanitize_session in hooks/spectate-emit.sh). Empty when the id is unset.
session_run_name() {
  [ -n "${CLAUDE_SESSION_ID:-}" ] || return 0
  local s
  s="$(printf '%s' "$CLAUDE_SESSION_ID" | tr -dc 'A-Za-z0-9._-' | cut -c1-128)"
  case "$s" in . | .. | "") s="unknown" ;; esac
  printf '%s\n' "$s"
}

newest_spectate_log() {
  # Re-resolve each call so CLAUDE_PROJECT_DIR changes (tests / resume) bind.
  local runs_dir="${CLAUDE_PROJECT_DIR:-$PWD}/.ravenclaude/runs"
  [ -d "$runs_dir" ] || return 0
  # This session's own log only, when the id is known (never another session's).
  local _sess
  _sess="$(session_run_name)"
  if [ -n "$_sess" ]; then
    [ -f "$runs_dir/$_sess/spectate-events.jsonl" ] && printf '%s\n' "$runs_dir/$_sess/spectate-events.jsonl"
    return 0
  fi
  # ONE `stat` over every candidate (xargs batches the list), not a fork per run
  # dir (~6 s per call at 1,500 run dirs); same GNU/BSD split as watch-run-state.sh.
  local _flag="-f" _fmt="%m %N"
  if stat -c '%Y' "$runs_dir" >/dev/null 2>&1; then _flag="-c" _fmt="%Y %n"; fi
  find "$runs_dir" -maxdepth 2 -name 'spectate-events.jsonl' -type f -print0 2>/dev/null |
    xargs -0 stat "$_flag" "$_fmt" 2>/dev/null |
    awk '{ mt = $1 + 0; if (mt > best) { best = mt; line = $0 } }
      END { if (line != "") { sub(/^[0-9]+ /, "", line); print line } }'
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
  # A clean Stop is a turn.end every turn — only the failed ones are signal.
  if [ "$kind" = "turn.end" ] && [ "$status" != "failed" ]; then
    return 0
  fi

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
    tool.fail | turn.end | stream.truncated | emitter.truncated) glyph="⚠" ;;
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

# True when $1 is one of the newline-separated lines of $2 (no pipe, so no
# SIGPIPE-under-pipefail false negative on a long list).
_line_in() {
  local _l
  while IFS= read -r _l; do
    [ "$_l" = "$1" ] && return 0
  done <<<"$2"
  return 1
}

_run_spectate_monitor_loop() {
  local current="" first_pass=1 followed="" tail_from
  while true; do
    local log
    log="$(newest_spectate_log || true)"

    if [ -z "$log" ] || [ ! -f "$log" ]; then
      current=""
      first_pass=0
      sleep "$POLL_SECONDS"
      continue
    fi

    if [ "$log" != "$current" ]; then
      # Joined at its end only if it existed at startup or was followed before;
      # a log first seen later is read from line 1 (its first event created it).
      if _line_in "$log" "$followed"; then
        tail_from="0"
      else
        if [ "$first_pass" -eq 1 ]; then tail_from="0"; else tail_from="+1"; fi
        followed="$followed
$log"
      fi
      first_pass=0
      current="$log"
      local tail_pid newer
      ( tail -n "$tail_from" -F "$log" 2>/dev/null | while IFS= read -r jsonl_line; do
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
