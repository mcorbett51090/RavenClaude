#!/usr/bin/env bash
# copilot-hook-adapter.sh — run a RavenClaude (Claude Code) hook under GitHub Copilot CLI.
#
# Claude Code and Copilot CLI both have lifecycle hooks with the same EVENTS
# (SessionStart, PreToolUse, PostToolUse, …) but DIFFERENT I/O envelopes:
#
#                      Claude Code                         Copilot CLI
#   PreToolUse stdin   {tool_name, tool_input:{...}, cwd}  {toolName, toolArgs:"<json string>", cwd}
#   PreToolUse stdout  {hookSpecificOutput:{permission     {permissionDecision, permissionDecisionReason}
#                        Decision, permissionDecisionReason, (top-level — no hookSpecificOutput wrapper)
#                        updatedInput}}  OR  exit 2 = block
#   SessionStart out   {hookSpecificOutput:{additionalContext}}  plain stdout is added to context
#
# This adapter translates Copilot's envelope <-> the Claude envelope so the EXISTING
# hook scripts (thing-orchestrator.sh, guard-destructive.sh, enforce-layout.sh,
# capability-orientation.sh) run unmodified under Copilot. The generated Copilot
# hooks.json invokes hooks through this adapter.
#
# Usage (from a Copilot hooks.json `bash` entry):
#   copilot-hook-adapter.sh <mode> <real-hook> [real-hook-args...]
#     mode = bash-pretool | file-pretool | sessionstart | posttool | stop
#
# Fail-open is Copilot's default on hook error; for the PreToolUse command hooks
# we translate a Claude `exit 2` (block) into a Copilot `deny` so the block still
# holds. Always exits 0 after emitting (so a translation hiccup never wedges the
# tool); the decision is carried in the emitted JSON, not the exit code.
#
# VERIFY-IN-COPILOT (could not be tested without a live Copilot CLI):
#   - the exact SessionStart context-injection shape (we emit BOTH a structured
#     {additionalContext} and the plain banner text, which covers both documented
#     behaviors);
#   - the "modify tool call" (updatedInput) shape — we pass the revised command
#     through as `updatedInput` best-effort and fall back to surfacing it in the
#     reason if Copilot ignores it.

set -uo pipefail

mode="${1:-}"; real="${2:-}"
shift 2 2>/dev/null || true
[ -z "$mode" ] || [ -z "$real" ] && exit 0          # misconfigured -> no-op (fail open)
command -v jq >/dev/null 2>&1 || exit 0
[ -f "$real" ] || exit 0

payload=""
[ ! -t 0 ] && payload="$(cat)"

cw="$(printf '%s' "$payload" | jq -r '.cwd // .workspaceRoot // empty' 2>/dev/null)"
[ -z "$cw" ] && cw="$PWD"
sid="$(printf '%s' "$payload" | jq -r '.sessionId // .session_id // empty' 2>/dev/null)"

case "$mode" in
  bash-pretool)
    # Copilot toolArgs is a JSON STRING; parse it, then re-shape to Claude stdin.
    claude_stdin="$(printf '%s' "$payload" | jq -c \
      '{tool_name: (.toolName // .tool_name // "Bash"),
        tool_input: ((.toolArgs // "{}") | (try fromjson catch {command: .})),
        cwd: (.cwd // .workspaceRoot // "."),
        session_id: (.sessionId // .session_id // "")}' 2>/dev/null)"
    out="$(printf '%s' "$claude_stdin" | THING_SEAT_ACTIVE="${THING_SEAT_ACTIVE:-}" bash "$real" "$@" 2>/dev/null)"; rc=$?
    if [ "$rc" -eq 2 ]; then
      jq -cn '{permissionDecision:"deny",permissionDecisionReason:"Blocked by RavenClaude guard (translated from a Claude exit-2 block)."}'
      exit 0
    fi
    # Claude verdict JSON -> Copilot top-level shape.
    dec="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.permissionDecision // empty' 2>/dev/null)"
    if [ -n "$dec" ]; then
      reason="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.permissionDecisionReason // ""' 2>/dev/null)"
      revised="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.updatedInput.command // empty' 2>/dev/null)"
      if [ -n "$revised" ]; then
        jq -cn --arg d "$dec" --arg r "$reason" --arg c "$revised" \
          '{permissionDecision:$d,permissionDecisionReason:($r + " [revised command: " + $c + "]"),updatedInput:{command:$c}}'
      else
        jq -cn --arg d "$dec" --arg r "$reason" '{permissionDecision:$d,permissionDecisionReason:$r}'
      fi
    fi
    exit 0
    ;;
  file-pretool)
    # Claude path hooks (enforce-layout) take the file path as argv, not stdin.
    fp="$(printf '%s' "$payload" | jq -r \
      '(.toolArgs // "{}") | (try fromjson catch {}) | (.file_path // .path // .filePath // empty)' 2>/dev/null)"
    [ -z "$fp" ] && exit 0
    CLAUDE_PROJECT_DIR="$cw" bash "$real" "$fp" >/dev/null 2>&1; rc=$?
    if [ "$rc" -eq 2 ]; then
      jq -cn --arg p "$fp" '{permissionDecision:"deny",permissionDecisionReason:("RavenClaude layout guard: " + $p + " is off the allow-list (.repo-layout.json).")}'
    fi
    exit 0
    ;;
  sessionstart)
    out="$(CLAUDE_PROJECT_DIR="$cw" bash "$real" "$@" 2>/dev/null)"
    ctx="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null)"
    if [ -n "$ctx" ]; then
      # Emit a structured additionalContext AND the plain text, covering both the
      # documented Copilot context-injection behaviors (structured field + stdout).
      jq -cn --arg c "$ctx" '{additionalContext:$c}'
      printf '%s\n' "$ctx"
    fi
    exit 0
    ;;
  posttool)
    # Side-effecting hooks (format-on-write, remind-tests): run, ignore output.
    fp="$(printf '%s' "$payload" | jq -r \
      '(.toolArgs // "{}") | (try fromjson catch {}) | (.file_path // .path // .filePath // empty)' 2>/dev/null)"
    CLAUDE_PROJECT_DIR="$cw" bash "$real" "$fp" >/dev/null 2>&1 || true
    exit 0
    ;;
  stop)
    # Stop hooks (dod-gate, remind-tests). Re-shape Copilot's stop payload to the
    # Claude stdin {cwd, session_id} and translate a Claude Stop block back.
    claude_stdin="$(printf '%s' "$payload" | jq -c \
      '{cwd: (.cwd // .workspaceRoot // "."),
        session_id: (.sessionId // .session_id // "")}' 2>/dev/null)"
    out="$(printf '%s' "$claude_stdin" | CLAUDE_PROJECT_DIR="$cw" bash "$real" "$@" 2>/dev/null)"; rc=$?
    # A Claude Stop block is either {"decision":"block","reason":...} on stdout or exit 2.
    dec="$(printf '%s' "$out" | jq -r '.decision // empty' 2>/dev/null)"
    reason="$(printf '%s' "$out" | jq -r '.reason // empty' 2>/dev/null)"
    if [ "$dec" = "block" ] || [ "$rc" -eq 2 ]; then
      [ -z "$reason" ] && reason="RavenClaude definition-of-done gate: work is not yet verified done."
      # Best-effort: emit BOTH a structured decision and the plain reason, mirroring
      # the sessionstart dual-emit, since Copilot's exact stop-block shape is
      # unverified (VERIFY-IN-COPILOT). Fail-open if Copilot ignores it.
      jq -cn --arg r "$reason" '{decision:"block",reason:$r}'
      printf '%s\n' "$reason" >&2
    fi
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
