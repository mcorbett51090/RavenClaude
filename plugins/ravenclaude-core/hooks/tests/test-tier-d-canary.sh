#!/usr/bin/env bash
# test-tier-d-canary.sh — Phase 7 acceptance tests (A7.1–A7.7) for the Tier D
# lane added to _host-canary.sh (plan.md's sessionstart-safeguards-multihost
# run, "Phase 7 — Runtime Tier D: a real short-lived host session").
#
# NOT yet a numbered audit-gate. Registering this as Gate 264 (dispatcher +
# main sequence + Supported: string, with mutant teeth wired in) is Phase 9's
# explicit job per plan.md ("Register the runtime self-test's mechanism
# checks as Gate 264 ... Pre-build gate: Phases 1-8 green"). Running this
# script directly is how Phase 7 proves its own acceptance tests pass without
# pre-empting that later registration.
#
# ⛔ THIS SCRIPT SPAWNS REAL `claude -p` / `copilot -p` PROCESSES. It must
# NEVER be wired into scripts/audit-gates.sh's main sequence (which runs in
# CI, with no host CLI available) — see plan.md Phase 7's reversibility note
# and Phase 9's CI boundary ("Tier D is never run in CI").
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CANARY="$HERE/../_host-canary.sh"
PORTABLE="$HERE/../_portable.sh"
REPO_ROOT="$(cd "$HERE/../../../.." && pwd)"

PASS=0
FAIL=0
ok()  { PASS=$((PASS + 1)); printf '  ✓ %s\n' "$1"; }
bad() { FAIL=$((FAIL + 1)); printf '  ✗ %s\n' "$1"; }

[ -f "$CANARY" ] || { printf 'FATAL: %s not found\n' "$CANARY" >&2; exit 1; }
[ -f "$PORTABLE" ] || { printf 'FATAL: %s not found\n' "$PORTABLE" >&2; exit 1; }

# shellcheck source=/dev/null
. "$PORTABLE"
# shellcheck source=/dev/null
. "$CANARY"

printf '── Phase 7 acceptance tests — Tier D (real host session) ──────────────────\n'

CLAUDE_PRESENT=0
COPILOT_PRESENT=0
command -v claude >/dev/null 2>&1 && CLAUDE_PRESENT=1
command -v copilot >/dev/null 2>&1 && COPILOT_PRESENT=1

# ── A7.7 — zero heredoc hits in the Tier D implementation, checked FIRST ────
# (run first so a heredoc regression is caught before anything else is even
# attempted — this is a static property, independent of host CLI presence)
printf '\nA7.7 — no heredoc in the Tier D scratch-config-writing code path\n'
TIER_D_SECTION="$(awk '/# ── TIER D LANE/,0' "$CANARY")"
HEREDOC_HITS="$(printf '%s\n' "$TIER_D_SECTION" | grep -cE '<<[A-Za-z"'"'"']')"
if [ "$HEREDOC_HITS" -eq 0 ]; then
  ok "zero heredoc-pattern hits (<<[A-Z\"']) in the Tier D section"
else
  bad "heredoc pattern found in the Tier D section — property 4 violated"
  printf '%s\n' "$TIER_D_SECTION" | grep -nE '<<[A-Za-z"'"'"']'
fi

# ── A7.1 — Claude Code: Tier-D marker fires; this IS the positive control ──
printf '\nA7.1 — Claude Code: Tier-D marker fires against a scratch project (positive control)\n'
if [ "$CLAUDE_PRESENT" -eq 1 ]; then
  A71_OUT="$(_rc_host_tier_d_canary claude-code 2>&1)"
  A71_RC=$?
  printf '%s\n' "$A71_OUT" | sed 's/^/    /'
  if [ "$A71_RC" -eq 0 ]; then
    ok "claude-code Tier D fired for real (rc=0) — spawn mechanism proven capable of firing"
  else
    bad "claude-code Tier D did NOT fire (rc=$A71_RC) — see output above"
  fi
else
  # premise-control on file (this machine's claude presence was verified
  # command -v claude -> /Users/matthewcorbett/.local/bin/claude, rc=0);
  # this else-arm is a defensive fallback for a machine where it is absent —
  # A7.4 below independently exercises that exact code path with its own
  # PATH-stripped positive/negative check.
  bad "claude CLI not present on this machine — A7.1 cannot run (see A7.4 for the absent-CLI path instead)"
fi

# ── A7.2 — must-fail: a NON-EXISTENT probe path must NOT fire ──────────────
# Drives the REAL _rc_canary_tier_d_write_config / _rc_canary_tier_d_spawn
# functions with a deliberately-broken probe path, for BOTH Tier-D-capable
# hosts (a bonus over the plan's single-host ask: it gives copilot its own
# negative control too, at near-zero extra cost since it's the same shape).
run_a72() {
  local host="$1" cli
  cli="$(_rc_canary_tier_d_cli_for "$host" 2>/dev/null)" || return 2
  command -v "$cli" >/dev/null 2>&1 || return 2
  local scratch outdir marker bogus_probe
  scratch="$(mktemp -d "${TMPDIR:-/tmp}/rc-tier-d-a72.XXXXXX")" || return 3
  outdir="$scratch/.rc-tier-d-out"
  mkdir -p "$outdir"
  marker="$outdir/marker"
  bogus_probe="$outdir/does-not-exist-probe.sh"   # deliberately never created
  _rc_canary_tier_d_write_config "$host" "$scratch" "$bogus_probe" >/dev/null 2>&1
  _rc_canary_tier_d_spawn "$host" "$scratch" >/dev/null 2>&1
  local fired=1
  [ -f "$marker" ] && fired=0
  rm -rf "$scratch"
  return "$fired"   # 0 = marker somehow appeared (BAD), 1 = did not fire (GOOD)
}
printf '\nA7.2 — must-fail: a scratch settings.json pointing at a NON-EXISTENT probe path must NOT fire\n'
for h in claude-code copilot; do
  cli="$(_rc_canary_tier_d_cli_for "$h" 2>/dev/null)"
  if [ -n "$cli" ] && command -v "$cli" >/dev/null 2>&1; then
    run_a72 "$h"
    rc=$?
    if [ "$rc" -eq 1 ]; then
      ok "$h: nonexistent probe path correctly did NOT fire (proves the assertion reads real dispatch)"
    else
      bad "$h: A7.2 assertion broken — rc=$rc (0 = marker appeared with no real probe, which must never happen)"
    fi
  else
    printf '    (skip: %s CLI not present on this machine)\n' "$h"
  fi
done

# ── A7.3 — scratch containment: real project tree unmodified after a run ───
printf '\nA7.3 — scratch containment: git status --porcelain on the REAL project tree is unchanged\n'
BEFORE_PRIMARY="$(git -C "$REPO_ROOT" status --porcelain 2>/dev/null)"
BEFORE_HERE="$(git -C "$HERE" status --porcelain 2>/dev/null)"
if [ "$CLAUDE_PRESENT" -eq 1 ]; then
  _rc_host_tier_d_canary claude-code >/dev/null 2>&1
fi
AFTER_PRIMARY="$(git -C "$REPO_ROOT" status --porcelain 2>/dev/null)"
AFTER_HERE="$(git -C "$HERE" status --porcelain 2>/dev/null)"
if [ "$BEFORE_PRIMARY" = "$AFTER_PRIMARY" ]; then
  ok "primary/worktree checkout ($REPO_ROOT) git status --porcelain unchanged after a Tier D run"
else
  bad "primary checkout ($REPO_ROOT) git status --porcelain CHANGED after a Tier D run — containment violated"
  diff <(printf '%s' "$BEFORE_PRIMARY") <(printf '%s' "$AFTER_PRIMARY")
fi
if [ "$BEFORE_HERE" = "$AFTER_HERE" ]; then
  ok "this checkout's own tree ($HERE/../../..) git status --porcelain unchanged after a Tier D run"
else
  bad "this checkout's tree CHANGED after a Tier D run — containment violated"
  diff <(printf '%s' "$BEFORE_HERE") <(printf '%s' "$AFTER_HERE")
fi

# ── A7.4 — claude absent -> explicit skip + tier-A-fallback, never silent ──
printf '\nA7.4 — claude absent: explicit skip + tier-A-fallback message, never silent\n'
A74_OUT="$(PATH="/usr/bin:/bin" bash -c '
  ok()  { printf "  OK %s\n" "$*"; }
  warn(){ printf "  WARN %s\n" "$*" >&2; }
  note(){ printf "  NOTE %s\n" "$*"; }
  . "'"$PORTABLE"'"
  . "'"$CANARY"'"
  _rc_host_tier_d_canary claude-code
  echo "RC=$?"
' 2>&1)"
printf '%s\n' "$A74_OUT" | sed 's/^/    /'
A74_RC="$(printf '%s\n' "$A74_OUT" | grep -o 'RC=[0-9]*' | tail -1 | cut -d= -f2)"
if [ "$A74_RC" = "1" ] && printf '%s' "$A74_OUT" | grep -q 'tier D unavailable' && printf '%s' "$A74_OUT" | grep -q 'falls back to tier A'; then
  ok "absent-claude path returns skip (rc=1) with an explicit, non-silent tier-A-fallback message"
else
  bad "absent-claude path did not produce the expected skip+message shape (rc='$A74_RC')"
fi

# ── A7.5 — Copilot-CLI probe outcome, with its own positive control ────────
printf '\nA7.5 — Copilot-CLI probe outcome, recorded with a positive control either way\n'
if [ "$COPILOT_PRESENT" -eq 1 ]; then
  # Positive control on the copilot spawn mechanism itself: prove `copilot -p`
  # against a scratch project actually runs to completion and returns text —
  # i.e. the spawn mechanism is demonstrably capable of doing SOMETHING,
  # independent of whether SessionStart hooks fire. This is what keeps a
  # spawn failure and a genuine "SessionStart never fires under -p" finding
  # from becoming indistinguishable (property 2).
  PC_SCRATCH="$(mktemp -d "${TMPDIR:-/tmp}/rc-tier-d-a75pc.XXXXXX")"
  command -v git >/dev/null 2>&1 && git init -q "$PC_SCRATCH" >/dev/null 2>&1
  PC_OUT="$( ( cd "$PC_SCRATCH" 2>/dev/null && _rc_timeout 25 copilot -C "$PC_SCRATCH" -p "reply with just the word OK" --model auto --allow-all-tools --deny-tool write --deny-tool shell --silent --output-format text ) 2>&1 )"
  rm -rf "$PC_SCRATCH"
  if [ -n "$PC_OUT" ]; then
    ok "positive control: copilot -p spawns and returns real output against a scratch project"
    COPILOT_SPAWN_OK=1
  else
    bad "positive control FAILED: copilot -p produced no output at all — treat any 'did not fire' below as inconclusive, not a finding"
    COPILOT_SPAWN_OK=0
  fi

  A75_OUT="$(_rc_host_tier_d_canary copilot 2>&1)"
  A75_RC=$?
  printf '%s\n' "$A75_OUT" | sed 's/^/    /'
  if [ "$A75_RC" -eq 0 ]; then
    MEASURED_TIER_COPILOT="D"
    ok "copilot-cli: measured runtime_tier = D (SessionStart fired for real under copilot -p)"
  elif [ "$COPILOT_SPAWN_OK" -eq 1 ]; then
    MEASURED_TIER_COPILOT="A"
    ok "copilot-cli: measured runtime_tier = A (spawn mechanism proven working via positive control, but SessionStart did not fire under -p — pinned to Tier A per plan.md §1.3, recorded as a finding, not treated as a bug)"
  else
    MEASURED_TIER_COPILOT="inconclusive"
    bad "copilot-cli: outcome inconclusive — the positive control itself failed, so rc=$A75_RC cannot be trusted as a finding"
  fi
else
  MEASURED_TIER_COPILOT="A (copilot CLI absent on this machine)"
  ok "copilot CLI not present — recorded as the measured state, not silently skipped (A0.2-style honesty)"
fi
printf '    MEASURED runtime_tier for copilot-cli THIS RUN: %s\n' "$MEASURED_TIER_COPILOT"

# ── A7.6 — anti-degradation: declared D + achieved only A -> FAIL ──────────
printf '\nA7.6 — anti-degradation: a declared-D host that only achieves A this run must be FAIL, not a quiet pass\n'
# Case 1: genuine D achieved (from A7.1's real run) -> must be PASS.
if [ "$CLAUDE_PRESENT" -eq 1 ]; then
  DECLARED="$(_rc_canary_declared_tier claude-code)"
  ACHIEVED_D="D"
  V1="$(_rc_canary_anti_degradation "$DECLARED" "$ACHIEVED_D")"
  if [ "$V1" = "PASS" ]; then
    ok "declared=D, achieved=D -> PASS (correct; not over-triggering on a genuine success)"
  else
    bad "declared=D, achieved=D incorrectly reported '$V1' (expected PASS)"
  fi
fi
# Case 2: force a real fallback-to-A via the kill switch, then feed the
# REAL observed achieved-tier into the REAL anti-degradation function.
A76_KILL_OUT="$(RC_SELFTEST_TIER=a bash -c '
  . "'"$PORTABLE"'"
  . "'"$CANARY"'"
  _rc_host_tier_d_canary claude-code >/dev/null 2>&1
  echo "RC=$?"
')"
A76_KILL_RC="$(printf '%s\n' "$A76_KILL_OUT" | grep -o 'RC=[0-9]*' | cut -d= -f2)"
if [ "$A76_KILL_RC" = "1" ]; then
  DECLARED2="$(_rc_canary_declared_tier claude-code)"
  ACHIEVED2="A"   # rc=1 (skip) means the caller falls back to tier A — this is the achieved tier
  V2="$(_rc_canary_anti_degradation "$DECLARED2" "$ACHIEVED2")"
  V2_STATUS=$?
  if [ "$V2" = "FAIL" ] && [ "$V2_STATUS" -eq 1 ]; then
    ok "declared=D, achieved=A (kill-switch forced fallback) -> FAIL correctly flagged, not a quiet pass"
  else
    bad "declared=D, achieved=A did not flag FAIL (_rc_canary_anti_degradation returned '$V2', exit $V2_STATUS)"
  fi
else
  bad "could not force the fallback scenario to set up A7.6 case 2 (kill-switch rc=$A76_KILL_RC, expected 1)"
fi

printf '\n── Phase 7 acceptance tests: %d passed, %d failed ─────────────────────────\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
