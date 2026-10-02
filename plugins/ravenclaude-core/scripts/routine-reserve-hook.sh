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
#   --event guard    (PreToolUse, guard mode only) before autonomous work — a Workflow,
#                                        ScheduleWakeup, CronCreate, a background Agent,
#                                        or a Remote session/Routine call — ASK when usage
#                                        is past the line in an attended interactive
#                                        session on a live reading; otherwise warn once per
#                                        band. A headless ask is a denial, so nothing asks
#                                        where no person can answer (never stalls a Routine).
#   --event consent  (PostToolUse, guard mode only) the guarded tool ran, so the ask was
#                                        approved: record consent for this session + week.
#
# OPT-IN: no-ops after one grep unless .ravenclaude/comfort-posture.yaml sets
# `routine_reserve: advise` (or `guard`); the guard/consent lanes need `guard` itself.
# FAIL-SAFE: always exits 0 — the only deny is the engine's own JSON verdict.
# State is account-scoped under ~/.ravenclaude/usage/ (see scripts/routine-reserve.py).
# Reference: knowledge/routine-token-reserve.md.
#
# rc-state-key: session_id (sanitized) + the weekly reset_at, in ~/.ravenclaude/usage/guard/<sid>.json
# rc-state-scope: session
# rc-state-rationale: consent is a person's answer in ONE session for ONE week; a new session or a new week asks again, and a sibling session never inherits another's approval
# rc-state-escape: file — ~/.ravenclaude/usage/override.json (written by /routine-reserve override or the dashboard Reserve tab) moves the line; or set routine_reserve: advise in the posture

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
  guard | consent)
    grep -Eq '^[[:space:]]*routine_reserve:[[:space:]]*guard[[:space:]]*(#.*)?$' "$posture" 2>/dev/null || exit 0
    if [ "$event" = "guard" ]; then
      printf '%s' "$payload" | (cd "$proj" && python3 "$engine" hook-guard 2>/dev/null) || true
    else
      printf '%s' "$payload" | (cd "$proj" && python3 "$engine" hook-consent >/dev/null 2>&1) || true
    fi
    ;;
esac
exit 0
