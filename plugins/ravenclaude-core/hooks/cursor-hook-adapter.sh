#!/usr/bin/env bash
# cursor-hook-adapter.sh — run the unmodified RavenClaude guardrails under Cursor.
#
# Multi-host audit MH-13. Before this, Cursor had ZERO in-loop enforcement: not the
# layout gate, not guard-destructive, not the command-review tribunal, not the
# runaway brake, not the web guard. CI was the only backstop, and CI runs after the
# damage. Cursor has had a real hooks API since 1.7 and this repo had never touched it.
#
# ============================================================================
# THE ONE FACT THAT SHAPES EVERY LINE BELOW: CURSOR FAILS **OPEN**.
# ============================================================================
# "malformed JSON response silently allows command instead of blocking"
# `[docs-verified 2026-07-28 — Cursor's own bug tracker, forum.cursor.com/t/…/152669]`
#
# Every other host this marketplace supports fails CLOSED on a broken hook — Claude
# Code and Codex treat a non-zero exit as a block; Copilot's preToolUse "fails closed
# … an error/crash/timeout denies the tool". Cursor is the exception. Here, a
# guardrail that emits slightly-wrong JSON does not fail loudly; it VANISHES, and the
# command it was supposed to stop runs.
#
# So the deny path is built to be unbreakable rather than expressive:
#
#   1. DENY IS A FIXED LITERAL. No interpolation, no jq dependency, no command text
#      echoed back. A hostile command cannot make it malformed because nothing from
#      the payload reaches it. We give up a detailed reason to guarantee the block.
#   2. BOTH FIELD SPELLINGS. The docs specify `user_message`/`agent_message`; multiple
#      community reports show `userMessage`/`agentMessage`. Unknown keys are ignored,
#      so emitting both removes a coin-flip from the safety path. `permission` itself
#      is not in dispute and is the only field that binds.
#   3. SILENCE MEANS ALLOW — so silence is emitted ONLY on a genuine allow. Any
#      internal failure AFTER the real hook decided to block still prints the literal.
#   4. `deny` is the only verdict translated. Cursor reportedly ignores `allow`/`ask`
#      when a command is already allow-listed, so pretending to emit them would be
#      theatre; anything not denied falls through to Cursor's own permission system.
#
# Usage (from a generated .cursor/hooks.json entry):
#   cursor-hook-adapter.sh <mode> /abs/path/to/real-hook.sh [args...]
# Modes: shell-pretool | file-posttool | sessionstart | stop | promptsubmit
#
# NOT wired: Cursor's `preToolUse`/`postToolUse`. Those events exist, but their
# per-event payload fields are not published on the page verified, and guessing a
# payload shape on a host that fails open is precisely the trade this repo refuses.
# See knowledge/cursor-customization.md.
set -uo pipefail

# The literal deny. Kept as ONE constant so there is exactly one thing to get right,
# and so a reader can see at a glance that nothing interpolates into it.
_RC_DENY='{"permission":"deny","user_message":"Blocked by a RavenClaude guardrail. Run the same command under Claude Code or check .ravenclaude/runs/ for the recorded reason.","agent_message":"Blocked by a RavenClaude guardrail. Do not retry verbatim; adjust the command to satisfy the guard, or ask the user.","userMessage":"Blocked by a RavenClaude guardrail. Run the same command under Claude Code or check .ravenclaude/runs/ for the recorded reason.","agentMessage":"Blocked by a RavenClaude guardrail. Do not retry verbatim; adjust the command to satisfy the guard, or ask the user."}'

_rc_deny() { printf '%s\n' "$_RC_DENY"; exit 0; }

mode="${1:-}"
real="${2:-}"
if [ -z "$mode" ] || [ -z "$real" ] || [ ! -f "$real" ]; then
  # Cannot run the guard. We do NOT deny here: a missing/misconfigured adapter must
  # not brick every shell command in the user's editor. This is the one place the
  # fail-open default is deliberate, and it is why the installer verifies the paths
  # it writes rather than trusting them at runtime.
  exit 0
fi
shift 2

payload="$(cat 2>/dev/null || true)"

_field() {
  _n="$1"
  [ -z "$payload" ] && return 0
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$payload" | jq -r --arg k "$_n" '.[$k] // empty' 2>/dev/null && return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    printf '%s' "$payload" | python3 -c '
import json, sys
try:
    v = json.load(sys.stdin).get(sys.argv[1])
    if isinstance(v, str):
        sys.stdout.write(v)
except Exception:
    pass
' "$_n" 2>/dev/null && return 0
  fi
  return 0
}

# Cursor gives workspace_roots[] rather than a single project dir.
_root() {
  [ -z "$payload" ] && return 0
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$payload" | jq -r '.workspace_roots[0] // empty' 2>/dev/null && return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    printf '%s' "$payload" | python3 -c '
import json, sys
try:
    r = json.load(sys.stdin).get("workspace_roots") or []
    if r and isinstance(r[0], str):
        sys.stdout.write(r[0])
except Exception:
    pass
' 2>/dev/null && return 0
  fi
  return 0
}

cw="$(_root)"; [ -z "$cw" ] && cw="$(_field cwd)"; [ -z "$cw" ] && cw="$PWD"
sid="$(_field conversation_id)"
export CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$cw}"
[ -n "$sid" ] && export CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID:-$sid}"
# Positive host assertion, mirroring the Copilot and Codex adapters. _rc_host()
# trusts THING_HOST because it is an assertion by a wrapper that KNOWS the host,
# never an inference from ambient environment.
export THING_HOST="${THING_HOST:-cursor}"

# Build the Claude-shaped stdin a guardrail expects. Cursor's beforeShellExecution
# carries {command, cwd, sandbox}; Claude's hooks read {tool_name, tool_input, ...}.
_claude_stdin() {
  _tool="$1"; _cmd="$2"
  if command -v jq >/dev/null 2>&1; then
    jq -cn --arg t "$_tool" --arg c "$_cmd" --arg d "$cw" --arg s "$sid" \
      '{tool_name:$t,tool_input:{command:$c},cwd:$d,session_id:$s}' 2>/dev/null && return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    python3 -c '
import json, sys
print(json.dumps({"tool_name": sys.argv[1], "tool_input": {"command": sys.argv[2]},
                  "cwd": sys.argv[3], "session_id": sys.argv[4]}))
' "$_tool" "$_cmd" "$cw" "$sid" 2>/dev/null && return 0
  fi
  return 1
}

case "$mode" in
  shell-pretool)
    cmd="$(_field command)"
    [ -z "$cmd" ] && exit 0
    stdin_json="$(_claude_stdin Bash "$cmd")" || exit 0
    # ⛔ stdout suppressed, stderr preserved (was `2>&1` until 2026-08-12, which
    # discarded the guard's deny reason entirely — same defect as the Gemini
    # adapter, found the same way). The JSON verdict below stays a FIXED literal:
    # Cursor fails OPEN on malformed JSON, so interpolating guard stderr into the
    # verdict would turn a noisy reason into a silently-allowed command. Sending
    # it to the adapter's own stderr keeps the reason visible in logs while the
    # deny path stays byte-fixed. Do not merge the two.
    printf '%s' "$stdin_json" | bash "$real" "$@" >/dev/null
    rc=$?
    # exit 2 is how every guardrail here blocks. Translate it, and ONLY it.
    [ "$rc" -eq 2 ] && _rc_deny
    exit 0
    ;;
  file-posttool)
    # afterFileEdit: side-effecting hooks (formatters, lints). Path as argv, output
    # ignored — a PostToolUse hook has no verdict to translate.
    fp="$(_field file_path)"; [ -z "$fp" ] && fp="$(_field path)"
    bash "$real" "$fp" >/dev/null 2>&1 || true
    exit 0
    ;;
  sessionstart)
    # Cursor does not document a structured context-injection field, so the hook's
    # additionalContext is emitted as plain stdout, which the docs' own examples use.
    out="$(bash "$real" "$@" 2>/dev/null || true)"
    if [ -n "$out" ] && command -v jq >/dev/null 2>&1; then
      ctx="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null)"
      [ -n "$ctx" ] && printf '%s\n' "$ctx"
    fi
    exit 0
    ;;
  stop|promptsubmit)
    # Fail-open by contract: these never block on any host.
    bash "$real" "$@" >/dev/null 2>&1 || true
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
