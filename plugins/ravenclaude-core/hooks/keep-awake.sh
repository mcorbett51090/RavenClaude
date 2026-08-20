#!/usr/bin/env bash
# keep-awake.sh — SessionStart: hold the strongest sleep assertion available WITHOUT a
# password, and say so honestly when it cannot hold one at all.
#
# ⛔ WHY THIS EXISTS — MEASURED 2026-08-20, not assumed.
# Claude Code already spawns `caffeinate -i -t 300` per session (verified: ps PPID resolves
# to `claude`). `-i` is PreventUserIdleSystemSleep — IDLE sleep only. It does not stop a lid
# close. Measured on this machine the same day:
#
#   09:00:51  Sleep  Entering Sleep state due to 'Clamshell Sleep' ... Using Batt
#   10:36:48  Wake   Wake from Deep Idle ... DriverReason:lid
#
# ~96 minutes suspended, with the `-i` assertion held the whole time. The failure is SILENT:
# the process is suspended, not killed, so the terminal resumes mid-scrollback and only
# wall-clock reveals the gap. That silence is the bug this hook exists to break.
#
# CONTRACT
#   OPT-IN; absent means OFF — the same contract as every other comfort-posture knob:
#     # .ravenclaude/comfort-posture.yaml
#     keep_awake: on     # off is the default, and the behavior when the key is absent
#   AC   + on -> hold `caffeinate -s` (PreventSystemSleep) bound to the session's lifetime.
#   Batt + on -> hold NOTHING and warn. No software-only method prevents Clamshell Sleep on
#                battery, and forcing it via a persistent pmset override cooks a closed laptop.
#   Never blocks. Always exits 0. SessionStart has nothing to fail closed to.
#
# ⛔ HONEST LIMIT, STATED NOT GLOSSED. Whether `caffeinate -s` defeats *Clamshell* sleep on
# Apple Silicon is UNVERIFIED [training knowledge]: caffeinate(8) documents `-s` as AC-only
# but is silent on the lid switch, and clamshell sleep is powerd/SMC-driven. It cannot be
# tested without physically closing a lid. The banner says so rather than implying a safety
# it has not earned — an assertion that silently fails is the exact defect above.
#
# PORTABILITY. bash 3.2-safe (stock macOS): no declare -A / mapfile / globstar, and no
# GNU-only timeout / grep -P / sed -i.

set -euo pipefail

# ── Cheapest possible no-op for everyone who has not opted in ────────────────
[ "$(uname -s 2>/dev/null || echo unknown)" = "Darwin" ] || exit 0

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
CFG="$PROJECT_DIR/.ravenclaude/comfort-posture.yaml"
[ -f "$CFG" ] || exit 0
grep -q 'keep_awake' "$CFG" 2>/dev/null || exit 0

# Minimal scalar parse (no PyYAML in a consumer env). BRE only — portable to BSD sed.
# Anything unrecognised falls through to the `*)` no-op, so a typo can never accidentally
# hold a system assertion.
MODE="$(sed -n 's/^[[:space:]]*keep_awake:[[:space:]]*\([a-z]*\).*/\1/p' "$CFG" 2>/dev/null | head -1)"
case "$MODE" in
  on) ;;
  *) exit 0 ;;
esac

command -v pmset >/dev/null 2>&1 || exit 0
command -v caffeinate >/dev/null 2>&1 || exit 0

# ── Advisory channel ────────────────────────────────────────────────────────
# MEASURED 2026-08-19: stderr-at-exit-0 reaches the MODEL on no event; additionalContext
# does. Without this the warning would talk only to the terminal — which is how five
# advisory hooks in this repo spent their whole service life. Forced exit 0.
_rc_hd="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$_rc_hd/_advise.sh" ]; then . "$_rc_hd/_advise.sh"; rc_advise_init SessionStart 0; fi

# ── Bind the assertion to the SESSION, not to this hook ─────────────────────
# `caffeinate -w <pid>` dies with that pid. $PPID may be a transient shell, so walk up for
# the real `claude`; fall back to $PPID rather than guessing.
_find_session_pid() {
  _p="${PPID:-0}"; _i=0
  while [ "$_p" -gt 1 ] && [ "$_i" -lt 8 ]; do
    _n="$(ps -o comm= -p "$_p" 2>/dev/null | sed 's#.*/##')"
    case "$_n" in claude) printf '%s' "$_p"; return 0 ;; esac
    _p="$(ps -o ppid= -p "$_p" 2>/dev/null | tr -d ' ')"
    [ -n "$_p" ] || return 1
    _i=$((_i + 1))
  done
  return 1
}
SESSION_PID="$(_find_session_pid || true)"
[ -n "$SESSION_PID" ] || SESSION_PID="${PPID:-$$}"

# ── Battery: hold nothing, warn loudly ──────────────────────────────────────
if ! pmset -g batt 2>/dev/null | grep -q "AC Power"; then
  printf '%s\n' "RavenClaude keep-awake: on BATTERY — nothing software-only prevents Clamshell Sleep, so closing the lid WILL freeze this session (suspended, not killed; it resumes on wake and only wall-clock shows the gap). Plug into AC to have this hook hold an assertion, or accept the freeze." >&2
  exit 0
fi

# ── AC: one assertion per session, idempotent across SessionStart re-fires ──
if pgrep -f "caffeinate -s -w $SESSION_PID" >/dev/null 2>&1; then
  exit 0
fi
nohup caffeinate -s -w "$SESSION_PID" >/dev/null 2>&1 &

printf '%s\n' "RavenClaude keep-awake: holding PreventSystemSleep (caffeinate -s, bound to pid $SESSION_PID) on AC power. UNVERIFIED on this machine: whether -s defeats Clamshell Sleep on Apple Silicon is not confirmed — run the lid probe to settle it, and do not assume a closed lid is safe until you have." >&2
exit 0
