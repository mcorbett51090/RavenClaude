#!/usr/bin/env bash
# _emit-event.sh
# Shared, sourced helper for the structured hook-event substrate (P0.2).
#
# Provides ONE function — `_emit_hook_event` — that appends a single machine-
# readable JSON line to the current session's hook-event log:
#
#   ${CLAUDE_PROJECT_DIR}/.ravenclaude/runs/${CLAUDE_SESSION_ID:-unknown}/hook-events.jsonl
#
# This is the read-side substrate for the Heimdall perimeter-alarm panel and any
# other surface that wants to know "what hook fired, when, why, on what" AFTER
# the fact (today the verdicts go only to stderr and vanish). The hooks keep
# their existing stderr/banner output unchanged; this is purely additive.
#
# Contract (intentionally minimal so callers can't get it wrong):
#
#   _emit_hook_event <hook> <verdict> <tool> <path> <rule> <exit_code>
#
#     hook       basename of the firing hook, e.g. "enforce-layout.sh"
#     verdict    one of: deny | warn | allow
#     tool       the tool that triggered the hook, e.g. "Edit" / "Bash"
#     path       the file path or command the verdict applies to ("" if n/a)
#     rule       short machine token naming WHY, e.g. "off-allow-list"
#     exit_code  the exit code the hook is about to use (0 / 2 / ...)
#
# Design invariants:
#   * SOURCED, not executed — defines a function and returns. It carries NO
#     top-level `set -euo pipefail` so it can never change the sourcing hook's
#     shell options or abort it. (It is still chmod +x to satisfy the repo's
#     "every hooks/*.sh is executable" gate, and `bash -n`-clean.)
#   * FAIL-SAFE — emission is best-effort. Any failure (no project dir, no jq,
#     unwritable path) is swallowed; the hook's own verdict is never affected.
#     A telemetry write must never be able to break a guardrail.
#   * ATOMIC-APPEND — exactly one `>>` of one newline-terminated line per call.
#     Lines are individually small (< PIPE_BUF), so concurrent appends from
#     parallel hook invocations interleave at line granularity, never mid-line.
#   * SCHEMA-VERSIONED — every line carries "schema_version": 1 so readers can
#     evolve. See plugins/ravenclaude-core/CLAUDE.md → "Hook event log".
#   * SECRET-SCRUBBED — the `rule` (reason) argument is scrubbed via
#     _scrub_reason() before writing, so secret-shaped tokens never appear in
#     the JSONL substrate. Scrubbing is provided by _scrub.sh (sourced once,
#     fail-safe: absent helper -> no-op scrub).

# Source the shared scrub helper (fail-safe: if absent, define a no-op).
_ee_scrub_helper="$(dirname "${BASH_SOURCE[0]:-$0}")/_scrub.sh"
if [ -f "$_ee_scrub_helper" ]; then
  # shellcheck source=/dev/null
  . "$_ee_scrub_helper" 2>/dev/null || true
fi
# If _scrub.sh was not sourced successfully, define a safe passthrough.
command -v _scrub_reason >/dev/null 2>&1 || _scrub_reason() { printf '%s' "${1:-}"; }

# Append one structured hook event. Never fails the caller.
_emit_hook_event() {
  # Wrap the whole body so a failure of any single step is contained.
  {
    local hook="${1:-unknown}"
    local verdict="${2:-unknown}"
    local tool="${3:-}"
    local path="${4:-}"
    local rule="${5:-}"
    local exit_code="${6:-}"

    # Substrate-wide invariant (Phase 0): scrub secret-shaped tokens from the
    # reason/rule field before it is written to the JSONL log. This is done
    # here — inside _emit_hook_event — so EVERY caller gets safe-by-construction
    # output without any per-call scrub responsibility.
    rule="$(_scrub_reason "$rule" 2>/dev/null || printf '%s' "$rule")"

    local project_dir="${CLAUDE_PROJECT_DIR:-}"
    # No project dir → nowhere canonical to write. Stay silent (fail-safe).
    [ -z "$project_dir" ] && return 0
    [ -d "$project_dir" ] || return 0

    local session="${CLAUDE_SESSION_ID:-unknown}"
    local run_dir="$project_dir/.ravenclaude/runs/$session"
    local log="$run_dir/hook-events.jsonl"

    mkdir -p "$run_dir" 2>/dev/null || return 0

    # RFC3339 UTC timestamp; fall back to empty string if `date` is odd.
    local ts
    ts="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || true)"

    local line=""
    if command -v jq >/dev/null 2>&1; then
      # jq does the JSON escaping correctly for arbitrary path/command content.
      line="$(jq -cn \
        --arg ts "$ts" \
        --arg hook "$hook" \
        --arg verdict "$verdict" \
        --arg tool "$tool" \
        --arg path "$path" \
        --arg rule "$rule" \
        --arg session "$session" \
        --argjson exit_code "${exit_code:-null}" \
        '{schema_version: 1, ts: $ts, hook: $hook, verdict: $verdict, tool: $tool, path: $path, rule: $rule, session_id: $session, exit_code: $exit_code}' \
        2>/dev/null || true)"
    fi

    # Fallback if jq is missing or failed: hand-escape the fields we control.
    if [ -z "$line" ]; then
      local ec="${exit_code:-null}"
      case "$ec" in
        ''|*[!0-9-]*) ec="null" ;;
      esac
      line="{\"schema_version\":1,\"ts\":\"$(_ee_json_escape "$ts")\",\"hook\":\"$(_ee_json_escape "$hook")\",\"verdict\":\"$(_ee_json_escape "$verdict")\",\"tool\":\"$(_ee_json_escape "$tool")\",\"path\":\"$(_ee_json_escape "$path")\",\"rule\":\"$(_ee_json_escape "$rule")\",\"session_id\":\"$(_ee_json_escape "$session")\",\"exit_code\":$ec}"
    fi

    [ -z "$line" ] && return 0
    printf '%s\n' "$line" >> "$log" 2>/dev/null || return 0
  } 2>/dev/null || return 0
  return 0
}

# Minimal JSON string escaper for the no-jq fallback path. Handles the
# characters that would break a JSON string: backslash, double-quote, and the
# common control chars (tab, CR, LF). Control bytes are rare in our fields
# (paths/commands); anything exotic is left as-is, which is acceptable for a
# best-effort fallback that only runs when jq is absent.
_ee_json_escape() {
  local s="${1:-}"
  s="${s//\\/\\\\}"   # backslash first
  s="${s//\"/\\\"}"   # double quote
  s="${s//	/\\t}"    # literal tab
  s="${s//$'\r'/\\r}"
  s="${s//$'\n'/\\n}"
  printf '%s' "$s"
}
