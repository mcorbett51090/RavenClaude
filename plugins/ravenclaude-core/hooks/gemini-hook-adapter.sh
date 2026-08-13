#!/usr/bin/env bash
# gemini-hook-adapter.sh — run the unmodified RavenClaude guardrails under Gemini CLI.
#
# Multi-host audit MH-30. Gemini was "name-checked 17 times, supported zero times".
# It turns out to be the CHEAPEST lane in the marketplace, because its hook contract
# is nearly Claude Code's `[docs-verified 2026-07-29 — geminicli.com/docs/hooks/reference/]`:
#
#   stdin fields   session_id / cwd / tool_name / tool_input / transcript_path — IDENTICAL names
#   blocking       exit 2 + stderr as the reason — IDENTICAL mechanism
#   matcher        supported, with regex
#
# So this is a SHIM, not an adapter. Compare:
#   Copilot  — ~300 lines translating envelopes AND normalising tool names.
#   Cursor   — a fixed-literal deny, because Cursor FAILS OPEN on malformed JSON.
#   Codex    — an env shim only; the contract already matched.
#   Gemini   — an env shim PLUS tool-name normalisation. Nothing else.
#
# ── THE ONE REAL TRANSLATION, AND WHY IT IS THE WHOLE POINT ─────────────────
# Gemini's tool names are snake_case: `run_shell_command`, `read_file`,
# `write_file`, `replace`. RavenClaude's guardrails dispatch on Claude's
# PascalCase `Bash | Read | Write | Edit | …` and fall through to `*) exit 0` —
# "no decision, proceed" — on anything unrecognised.
#
# That exact mismatch is MH-01: under Copilot the command-review tribunal and the
# web guard were fully wired and reviewed NOTHING, silently, because `bash` is not
# `Bash`. Shipping this lane without normalising would reproduce that defect on a
# third host, and it would look wired the entire time.
#
# ── WHAT IS DELIBERATELY *NOT* TRANSLATED ───────────────────────────────────
# Blocking. `exit 2` is already Gemini's contract, so the guard's own exit code
# passes straight through untouched. We emit no JSON verdict at all: every byte of
# translation on the deny path is a byte that can be wrong, and here none is needed.
#
# Usage (from a generated .gemini/settings.json entry):
#   gemini-hook-adapter.sh <mode> /abs/path/to/real-hook.sh [args...]
# Modes: pretool | posttool | sessionstart
set -uo pipefail

mode="${1:-}"
real="${2:-}"
# A missing/misconfigured shim must not brick every tool call in the editor. The
# installer verifies the paths it writes; runtime stays permissive here.
[ -z "$mode" ] || [ -z "$real" ] || [ ! -f "$real" ] && exit 0
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

cw="$(_field cwd)"; [ -z "$cw" ] && cw="$PWD"
sid="$(_field session_id)"
export CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$cw}"
[ -n "$sid" ] && export CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID:-$sid}"
# Positive host assertion, as the Copilot/Codex/Cursor shims do. _rc_host() trusts
# THING_HOST because it is asserted by a wrapper that KNOWS the host, never inferred
# from ambient environment.
export THING_HOST="${THING_HOST:-gemini}"

# Rewrite the payload's tool_name into Claude's vocabulary, leaving every other
# field untouched. Unmapped names pass through VERBATIM rather than defaulting to
# anything: a wrong default is how MH-01 reviewed an absent name as `Bash` while
# skipping a present one.
_normalise() {
  if command -v python3 >/dev/null 2>&1; then
    printf '%s' "$payload" | python3 -c '
import json, sys
MAP = {
    "run_shell_command": "Bash",
    "read_file": "Read",
    "read_many_files": "Read",
    "write_file": "Write",
    "replace": "Edit",
    "edit_file": "Edit",
    "web_fetch": "WebFetch",
    "google_web_search": "WebSearch",
    "web_search": "WebSearch",
}
try:
    d = json.load(sys.stdin)
except Exception:
    sys.stdout.write(sys.argv[1] if len(sys.argv) > 1 else "")
    sys.exit(0)
if isinstance(d, dict):
    raw = d.get("tool_name")
    if isinstance(raw, str):
        # MCP tools arrive as mcp_<server>_<tool>; Claude expects mcp__<server>__<tool>.
        if raw.startswith("mcp_") and not raw.startswith("mcp__"):
            d["tool_name"] = "mcp__" + raw[4:]
        else:
            d["tool_name"] = MAP.get(raw, raw)
    if "session_id" not in d and sys.argv[2:]:
        d["session_id"] = sys.argv[2]
sys.stdout.write(json.dumps(d))
' "$payload" "$sid" 2>/dev/null && return 0
  fi
  # No python3: pass the payload through unchanged rather than guessing. The guard
  # then sees a snake_case name and declines to act — the same as today's
  # unsupported state, not a new hole.
  printf '%s' "$payload"
}

case "$mode" in
  pretool)
    # ⛔ stdout is suppressed; stderr is NOT. The comment below has always said
    # "stderr already carries the reason" — and until 2026-08-12 the very same
    # line ended `2>&1`, which sent that reason to /dev/null. Measured: the guard
    # emitted 233 bytes of deny reason directly and 0 bytes through this adapter,
    # so a Gemini user saw a bare exit-2 block with no explanation. That is the
    # diagnostic-blindness class the Copilot adapter fixed in v0.111.0, reproduced
    # here by one redirect. A comment is not a control: the claim and the code
    # disagreed for the adapter's whole life and no gate could see it.
    #
    # Only `>/dev/null` is correct — a guard may print a JSON verdict on stdout
    # that Gemini does not expect, but stderr IS Gemini's documented reason
    # channel, so it must flow through untouched. Do not "tidy" this back to 2>&1.
    _normalise | bash "$real" "$@" >/dev/null
    rc=$?
    # exit 2 IS Gemini's block. Pass the guard's own code through untouched —
    # there is nothing to translate, and stderr now genuinely carries the reason.
    exit "$rc"
    ;;
  posttool)
    fp="$(_field file_path)"
    bash "$real" "$fp" >/dev/null 2>&1 || true
    exit 0
    ;;
  sessionstart)
    out="$(bash "$real" "$@" 2>/dev/null || true)"
    if [ -n "$out" ] && command -v jq >/dev/null 2>&1; then
      ctx="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null)"
      [ -n "$ctx" ] && printf '%s\n' "$ctx"
    fi
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
