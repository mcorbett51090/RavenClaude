#!/usr/bin/env bash
# codex-hook-env.sh — the Codex ENV shim. NOT an envelope adapter.
#
# READ THIS BEFORE EXTENDING IT, because the obvious wrong move is to grow this
# into a second copilot-hook-adapter.sh.
#
# Codex speaks the Claude Code hook contract natively `[docs-verified 2026-07-28,
# https://learn.chatgpt.com/docs/hooks]`: identical PascalCase event names,
# identical stdin field names (tool_name / tool_input / cwd / session_id),
# identical `exit 2` + stderr blocking, identical hookSpecificOutput envelope, and
# identical PascalCase tool-name VALUES ("Bash", not Copilot's "bash"). So there is
# NOTHING to translate. Copilot needed ~300 lines of envelope translation plus a
# tool-name normalisation map; Codex needs none of it, and adding one would be the
# expensive wrong answer. See knowledge/codex-cli-customization.md.
#
# What Codex genuinely does NOT provide is two environment variables:
#
#   CLAUDE_PROJECT_DIR — 25 hook files read it. _emit-event.sh no-ops without it,
#                        so NO hook event is ever written and the Guardrails
#                        dashboard (Heimdall / Vidarr) stays dark — the exact
#                        "unwatched, not clean" state audit MH-05 made honest.
#   CLAUDE_SESSION_ID  — 14 hook files read it; events would land in runs/unknown/.
#
# Codex's documented environment is ONLY: PLUGIN_ROOT, PLUGIN_DATA, and
# CLAUDE_PLUGIN_ROOT / CLAUDE_PLUGIN_DATA (supplied as legacy-compatibility names,
# which is why helper-path resolution already works unaided).
#
# THE LOAD-BEARING POINT: `hooks/_portable.sh`'s _rc_host_env falls back to
# CODEX_PROJECT_ROOT / CODEX_SESSION_ID / PROJECT_DIR / SESSION_ID. Those names are
# NOT in Codex's documented environment — they are speculative, so under a real
# Codex session they resolve to nothing and the two variables stay blank. The shim
# is harmless (it fills blanks only) but it does not close this gap.
#
# The documented, reliable source is STDIN: every Codex hook payload carries `cwd`
# and `session_id`. This wrapper reads the payload, lifts those two values into the
# CLAUDE_* names the hooks already read, and re-emits the payload UNCHANGED on the
# real hook's stdin. That is the whole job.
#
# Usage (from a generated .codex/hooks.json entry):
#   codex-hook-env.sh /abs/path/to/real-hook.sh [args...]
#
# INVARIANTS (each has a Gate 155 assertion):
#   1. stdin is passed through BYTE-IDENTICAL. A hook that re-parses the payload
#      must see exactly what Codex sent — this shim adds no field and drops none.
#   2. It fills BLANKS ONLY. If Codex (or a wrapping host) already set
#      CLAUDE_PROJECT_DIR / CLAUDE_SESSION_ID, that value wins untouched. Claude
#      Code is authoritative about its own vocabulary.
#   3. The real hook's EXIT CODE propagates verbatim — especially exit 2, which is
#      how every guardrail here blocks. Swallowing it would silently disarm the
#      whole enforcement layer, which is the failure class this audit exists to fix.
#   4. It NEVER fails the hook. A missing jq, a malformed payload, an absent python3
#      — all degrade to "export nothing and run the hook anyway". A telemetry
#      convenience must never become a new way for a guardrail to die.
set -uo pipefail

_hook="${1:-}"
if [ -z "$_hook" ]; then
  printf 'codex-hook-env.sh: no hook path given\n' >&2
  exit 1
fi
shift

# Read the payload once. `cat` with no redirect consumes stdin whole; if stdin is
# closed/empty this is an empty string and everything below no-ops safely.
_payload="$(cat 2>/dev/null || true)"

# Extract cwd + session_id. jq first (already a dependency of the hook layer),
# python3 second, then give up. Both readers are total: any parse failure yields an
# empty string, never an error and never a non-zero exit out of this block.
_rc_field() {
  _name="$1"
  [ -z "$_payload" ] && return 0
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$_payload" | jq -r --arg k "$_name" '.[$k] // empty' 2>/dev/null && return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    printf '%s' "$_payload" | python3 -c '
import json, sys
try:
    v = json.load(sys.stdin).get(sys.argv[1])
    if isinstance(v, str):
        sys.stdout.write(v)
except Exception:
    pass
' "$_name" 2>/dev/null && return 0
  fi
  return 0
}

# INVARIANT 2 — blanks only. Never overwrite a value the host already set.
if [ -z "${CLAUDE_PROJECT_DIR:-}" ]; then
  _cwd="$(_rc_field cwd)"
  [ -n "$_cwd" ] && export CLAUDE_PROJECT_DIR="$_cwd"
fi
if [ -z "${CLAUDE_SESSION_ID:-}" ]; then
  _sid="$(_rc_field session_id)"
  [ -n "$_sid" ] && export CLAUDE_SESSION_ID="$_sid"
fi

# Positive host assertion, mirroring what copilot-hook-adapter.sh does for Copilot.
# _rc_host() in _portable.sh trusts THING_HOST because it is an assertion made by a
# wrapper that KNOWS the host, never an inference from ambient environment — an
# in-session probe found COPILOT_* vars set inside a Claude Code session, so
# guessing from the environment mislabels live sessions.
export THING_HOST="${THING_HOST:-codex}"

# INVARIANTS 1 + 3 — byte-identical stdin, verbatim exit code.
printf '%s' "$_payload" | "$_hook" "$@"
exit $?
