#!/usr/bin/env bash
# _emit-event.sh — shared structured hook-event logger (P0.2, event substrate).
#
# Source this from a hook and call `_emit_hook_event`. It appends one JSON line
# per call to:
#   ${CLAUDE_PROJECT_DIR:-$PWD}/.ravenclaude/runs/${CLAUDE_SESSION_ID:-unknown}/hook-events.jsonl
#
# Why: the four PreToolUse/PostToolUse guard hooks below emit human-readable
# stderr/banner output, but that output vanishes after the turn — the dashboard
# (Heimdall perimeter-alarm, Víðarr event log) cannot read it after the fact.
# This gives the same verdicts a machine-readable trail: what fired, when, why,
# on what. The stderr/banner output of each hook is UNCHANGED.
#
# CONTRACT — telemetry must never break the hook it instruments:
#   * Every failure path returns 0 silently (the calling hooks run under
#     `set -euo pipefail`; a logging failure must not abort the guard).
#   * No-op (return 0) when jq is absent — the line is best-effort, not required.
#   * The jsonl lives under .ravenclaude/runs/ which is gitignored, and is written
#     with shell `>>` (not the Write tool), so neither the layout hook nor the
#     CI layout gate ever sees it.
#
# Usage: _emit_hook_event <hook> <verdict> <tool> <path> <rule> <exit_code>
#   hook       e.g. "enforce-layout.sh"
#   verdict    deny | warn | allow
#   tool       the tool being gated (Bash | Edit | Write | MultiEdit | …; "" ok)
#   path       the target path or command the verdict was about ("" ok)
#   rule       the rule/pattern that fired ("" ok)
#   exit_code  numeric exit the hook is about to take (non-numeric → 0)

_emit_hook_event() {
  # Wrap the whole body so nothing inside can trip the caller's `set -e`.
  {
    command -v jq >/dev/null 2>&1 || return 0

    local hook="${1:-unknown}"
    local verdict="${2:-allow}"
    local tool="${3:-}"
    local path="${4:-}"
    local rule="${5:-}"
    local exit_code="${6:-0}"

    # exit_code must be a JSON number; coerce anything else to 0.
    case "$exit_code" in
      ''|*[!0-9]*) exit_code=0 ;;
    esac

    local proj="${CLAUDE_PROJECT_DIR:-$PWD}"
    local sid="${CLAUDE_SESSION_ID:-unknown}"
    local dir="$proj/.ravenclaude/runs/$sid"
    mkdir -p "$dir" 2>/dev/null || return 0

    local ts
    ts="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null)" || return 0

    # jq -n with --arg quotes every value safely (paths/commands may contain
    # quotes, backslashes, newlines). -c keeps it one line per event.
    jq -cn \
      --arg ts "$ts" \
      --arg hook "$hook" \
      --arg verdict "$verdict" \
      --arg tool "$tool" \
      --arg path "$path" \
      --arg rule "$rule" \
      --arg sid "$sid" \
      --argjson ec "$exit_code" \
      '{schema_version: 1, ts: $ts, hook: $hook, verdict: $verdict, tool: $tool, path: $path, rule: $rule, session_id: $sid, exit_code: $ec}' \
      >> "$dir/hook-events.jsonl" 2>/dev/null || return 0
  } 2>/dev/null || true
  return 0
}
