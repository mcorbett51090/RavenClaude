#!/usr/bin/env bash
#
# routine-reserve-hook.sh — the routine token reserve's session hooks (advise mode).
#
#   --event session  (SessionStart)     refresh in the BACKGROUND: pull the meter's data
#                                        branch + recompute. Never makes a session wait on
#                                        the network.
#   --event prompt   (UserPromptSubmit) once per state band per session, tell the user
#                                        (systemMessage) and the model (additionalContext)
#                                        that interactive use is nearing or inside the
#                                        reserve held for their claude.ai Routines.
#
# OPT-IN: no-ops after one grep unless .ravenclaude/comfort-posture.yaml sets
# `routine_reserve: advise` (or `guard`). FAIL-SAFE: always exits 0, never blocks.
# State is account-scoped under ~/.ravenclaude/usage/ (see scripts/routine-reserve.py).
# Reference: knowledge/routine-token-reserve.md.

set -uo pipefail

event=""
[ "${1:-}" = "--event" ] && event="${2:-}"
payload=""
[ ! -t 0 ] && payload="$(cat)"

proj="${CLAUDE_PROJECT_DIR:-$PWD}"
posture="${proj}/.ravenclaude/comfort-posture.yaml"
[ -f "$posture" ] || exit 0
grep -Eq '^[[:space:]]*routine_reserve:[[:space:]]*(advise|guard)[[:space:]]*(#.*)?$' "$posture" 2>/dev/null || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

engine="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/routine-reserve.py"
[ -f "$engine" ] || exit 0

case "$event" in
  session)
    (cd "$proj" && nohup python3 "$engine" refresh >/dev/null 2>&1 &)
    ;;
  prompt)
    printf '%s' "$payload" | (cd "$proj" && python3 "$engine" hook-warn 2>/dev/null) || true
    ;;
esac
exit 0
