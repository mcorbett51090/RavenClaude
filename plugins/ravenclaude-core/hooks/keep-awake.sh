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
# ✅ MEASURED 2026-08-24 — this was the last unverified premise in the hook, and it HOLDS.
# Two physical lid closes on AC, `PreventSystemSleep 1` verified held before and after. A 1 s
# user-space ticker recorded 98 ticks inside a 99 s closed-lid window (99.0% coverage), max
# gap 2 s — identical to the lid-open baseline. So `caffeinate -s` DOES keep a session
# executing through a closed lid, and the AC path earns what it claims.
#
# ⛔ AND THE OBVIOUS PROBE SAYS THE OPPOSITE. A `'Clamshell Sleep'` entry STILL appears on AC:
#
#     12:00:56  Sleep  Entering DarkWake state due to 'Clamshell Sleep' ... Using AC
#
# That line records the DarkWake TRANSITION, not a suspension. So "grep pmset -g log for a new
# Clamshell Sleep entry; a new one means it failed" returns FAILED on a setup that works — it
# was run first here and produced exactly that wrong verdict, and the planned response was to
# make this AC path warning-only. That would have removed a protection that measurably works.
#
# ⛔ THE DISCRIMINATOR IS THE SECOND TRANSITION, so grep for `Entering Sleep state`, never for
# `Clamshell Sleep`. Unprotected 2026-08-22: DarkWake 14:58:38, then `Entering Sleep state due
# to 'Clamshell Sleep'` 34 s later. Protected 2026-08-24: DarkWake only, no full-Sleep entry
# from a clamshell cause all day.
#
# ⛔ Daemon log activity during the window is NOT evidence the session survived — cloudd and
# dasd run in DarkWake regardless. That is a different process class. Instrument a user-space
# ticker, and take a positive control that the lid ACTUALLY closed (Clamshell count increments
# + `powerd ... lidopen` TurnedOn on reopen), or "no gap" cannot be told apart from "the lid
# never closed". Probes: `.ravenclaude/runs/guard-gate-correctness/lid-{probe,ticker}.sh`.
#
# ⛔ STILL TRUE, AND THE REASON THIS HOOK EXISTS: `-i` LOSES. The original 96-minute silent
# suspension was under `caffeinate -i -t 300` (PreventUserIdleSystemSleep), which Claude Code
# spawns per session — idle-only, and a lid close is not idle. `-i` losing says nothing about
# `-s`; conflating them is what made this an open question for four days.
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
# ⛔ NO PIPE, NO `grep -q`, ON PURPOSE. This file runs under `set -o pipefail` (above), and
# `grep -q` exits the instant it matches; if the producer still has a write pending it takes
# SIGPIPE and the PIPELINE reports 141, not 0. Under the old `if ! pmset … | grep -q "AC
# Power"` that inverted to TRUE, so a machine ON AC would take the BATTERY branch: warn "on
# BATTERY" and hold NO assertion. That is the silent no-op this hook exists to prevent, and
# it would have looked like correct behaviour.
#
# An intermittent RACE, not a certainty: measured 2026-08-24 at 141 once on a larger `pmset`
# producer, then 0/460 on re-probe with a detector proven live by a positive control
# (`yes | grep -q y` -> 20/20 exit 141). ⛔ 460 passes do NOT show a race is gone.
#
# `case` on a captured string removes the failure mode outright rather than narrowing it —
# no subprocess, no pipe, no exit status to misread. Capturing and then piping into `grep -q`
# would only have made the window smaller, which is not the same as closing it. bash 3.2-safe.
_batt="$(pmset -g batt 2>/dev/null || printf '')"
case "$_batt" in
  *"AC Power"*)
    : # on AC — fall through and hold the assertion
    ;;
  *)
    printf '%s\n' "RavenClaude keep-awake: on BATTERY — nothing software-only prevents Clamshell Sleep, so closing the lid WILL freeze this session (suspended, not killed; it resumes on wake and only wall-clock shows the gap). Plug into AC to have this hook hold an assertion, or accept the freeze." >&2
    exit 0
    ;;
esac

# ── AC: one assertion per session, idempotent across SessionStart re-fires ──
if pgrep -f "caffeinate -s -w $SESSION_PID" >/dev/null 2>&1; then
  exit 0
fi
nohup caffeinate -s -w "$SESSION_PID" >/dev/null 2>&1 &

printf '%s\n' "RavenClaude keep-awake: holding PreventSystemSleep (caffeinate -s, bound to pid $SESSION_PID) on AC power. VERIFIED 2026-08-24 by two physical lid closes — a user-space ticker logged 98 of 99 seconds inside a closed-lid window (max gap 2s, same as lid-open), so the session keeps running. ⛔ A 'Clamshell Sleep' line WILL still appear in pmset -g log; it is only the DarkWake transition, NOT a stall — grep for 'Entering Sleep state' if you want the real thing." >&2
exit 0
