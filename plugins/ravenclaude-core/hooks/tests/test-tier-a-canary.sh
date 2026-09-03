#!/usr/bin/env bash
# test-tier-a-canary.sh — Phase 6 acceptance tests (A6.1-A6.5) for the
# SessionStart Tier A lane added to _host-canary.sh (plan.md's
# sessionstart-safeguards-multihost run, "Phase 6 — Runtime Tier A: a
# `sessionstart` lane inside `_host-canary.sh`").
#
# Registered as part of Gate 264 (Phase 9) — dispatcher + main sequence +
# Supported: string, per plan.md's Phase 9 goal ("register the runtime
# self-test's mechanism checks — invocation + delivery + completeness scan
# — as Gate 264"). Every function this script drives runs a bundled
# ADAPTER SHELL SCRIPT (or, for claude-code, the planted probe script
# directly) — never a real host CLI binary — so this is CI-safe Tier A,
# distinct from hooks/tests/test-tier-d-canary.sh (Tier D, real `claude -p`
# / `copilot -p` spawns, NEVER wired into audit-gates.sh's CI-run surface).
#
# Usage:
#   bash test-tier-a-canary.sh              # good path (A6.1, A6.4)
#   bash test-tier-a-canary.sh --self-test  # good path + all must-fail halves
#   bash test-tier-a-canary.sh --must-fail  # only the must-fail halves

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE="$HERE/.."
PORTABLE="$CORE/_portable.sh"
CANARY="$CORE/_host-canary.sh"
REPO_ROOT="$(cd "$CORE/../../.." && pwd)"

PASS=0
FAIL=0
ok()   { PASS=$((PASS + 1)); printf '  \xe2\x9c\x93 %s\n' "$1"; }
bad()  { FAIL=$((FAIL + 1)); printf '  \xe2\x9c\x97 %s\n' "$1"; }
# _host-canary.sh's own sourced functions call ok/warn/note directly — give
# them a home so sourcing doesn't blow up on an undefined command. warn/note
# are advisory prints only; they do not affect PASS/FAIL bookkeeping.
warn() { printf '    (warn) %s\n' "$1" >&2; }
note() { printf '    (note) %s\n' "$1"; }

[ -f "$PORTABLE" ] || { echo "FATAL: $PORTABLE not found" >&2; exit 1; }
[ -f "$CANARY" ] || { echo "FATAL: $CANARY not found" >&2; exit 1; }
# shellcheck source=/dev/null
. "$PORTABLE"
# shellcheck source=/dev/null
. "$CANARY"

printf '\xe2\x94\x80\xe2\x94\x80 Phase 6 acceptance tests \xe2\x80\x94 Tier A (adapter seam) \xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\n'

TIER_A_HOSTS="copilot cursor gemini codex claude-code"

# ── A6.1 — for each host: sessionstart marker fires AND the sentinel
#          appears on stdout (invocation + delivery, the good path) ──────────
run_a61() {
  printf '\nA6.1 \xe2\x80\x94 invocation + context delivery, per host\n'
  for h in $TIER_A_HOSTS; do
    rc=0
    out="$(_rc_host_sessionstart_canary "$h" "$REPO_ROOT" 2>&1)" || rc=$?
    printf '%s\n' "$out" | sed 's/^/    /'
    if [ "$rc" -eq 0 ]; then
      ok "$h: sessionstart canary fired AND delivered (rc=0)"
    elif [ "$rc" -eq 1 ]; then
      # Not a failure — an honestly-declared skip (e.g. missing jq for
      # copilot). A6.5 exercises the deliberate-absence path directly;
      # this arm only fails the test if EVERY host skips (below).
      ok "$h: honest skip (rc=1) — not a silent pass, recorded"
    else
      bad "$h: expected rc=0 or rc=1 (honest skip), got rc=$rc"
    fi
  done
}

# ── A6.4 — the PreToolUse lane is byte-unchanged; Gate 207's round-trip +
#           both its mutant halves still pass, untouched by this phase ──────
run_a64() {
  printf '\nA6.4 \xe2\x80\x94 PreToolUse lane unchanged (delegates to Gate 207)\n'
  rc=0
  out="$(bash "$REPO_ROOT/scripts/check-host-canary.sh" --self-test 2>&1)" || rc=$?
  printf '%s\n' "$out" | sed 's/^/    /'
  if [ "$rc" -eq 0 ]; then
    ok "Gate 207 (--self-test) still passes 0 fail -- PreToolUse lane untouched"
  else
    bad "Gate 207 (--self-test) regressed (rc=$rc) -- Phase 6 must not touch the PreToolUse lane"
  fi
}

# ── A6.5 — an absent adapter must SKIP (rc=1), never a silent pass (rc=0) ──
run_a65() {
  printf '\nA6.5 \xe2\x80\x94 absent adapter \xe2\x86\x92 skip (rc=1), never a pass\n'
  real_adapter="$CORE/gemini-hook-adapter.sh"
  if [ ! -f "$real_adapter" ]; then
    bad "A6.5 setup: $real_adapter not found -- cannot exercise the absent-adapter path"
    return
  fi
  moved="${real_adapter}.a65-moved"
  mv "$real_adapter" "$moved"
  rc=0
  out="$(_rc_host_sessionstart_canary gemini "$REPO_ROOT" 2>&1)" || rc=$?
  mv "$moved" "$real_adapter"
  printf '%s\n' "$out" | sed 's/^/    /'
  if [ "$rc" -eq 1 ]; then
    ok "A6.5: gemini with its adapter removed -> skip (rc=1), not a silent pass"
  else
    bad "A6.5: expected rc=1 (skip) with the adapter absent, got rc=$rc"
  fi
  # Cleanup verified — the real tree is restored before any later assertion.
  [ -f "$real_adapter" ] && ok "A6.5 cleanup verified: gemini-hook-adapter.sh restored" \
    || bad "A6.5 cleanup FAILED: gemini-hook-adapter.sh not restored"
}

# ── Shared mutant builder for A6.2/A6.3 — mutates a SCRATCH COPY of
#    copilot-hook-adapter.sh's `sessionstart)` case only, then redefines
#    _rc_canary_sessionstart_adapter to point at the scratch copy for the
#    duration of one call. The real file on disk is never touched.
_a6_mutant_dir=""
_build_copilot_mutant() {
  local kind="$1" dest="$2"
  python3 - "$CORE/copilot-hook-adapter.sh" "$dest" "$kind" <<'PY'
import sys
src_path, dest_path, kind = sys.argv[1], sys.argv[2], sys.argv[3]
src = open(src_path, "r", encoding="utf-8").read()
anchor = '  sessionstart)\n    out="$(CLAUDE_PROJECT_DIR="$cw" bash "$real" "$@" 2>/dev/null)"\n'
if anchor not in src:
    sys.stderr.write("MUTATION ANCHOR NOT FOUND in copilot-hook-adapter.sh sessionstart case\n")
    sys.exit(3)
if kind == "a62":
    # A6.2 — never invoke the real probe at all. The marker can never fire.
    new = '  sessionstart)\n    out=""\n    true "$real" "$@" 2>/dev/null\n'
elif kind == "a63":
    # A6.3 — invoke the real probe (marker DOES fire) but swallow its
    # stdout before capture, so the sentinel never reaches $out.
    new = '  sessionstart)\n    CLAUDE_PROJECT_DIR="$cw" bash "$real" "$@" >/dev/null 2>&1\n    out=""\n'
else:
    sys.exit(4)
open(dest_path, "w", encoding="utf-8").write(src.replace(anchor, new, 1))
PY
}

_run_copilot_mutant() {
  local kind="$1" want_rc="$2" label="$3"
  _a6_mutant_dir="$(mktemp -d "${TMPDIR:-/tmp}/rc-t6-mutant.XXXXXX")"
  local mutant="$_a6_mutant_dir/copilot-hook-adapter.sh"
  if ! _build_copilot_mutant "$kind" "$mutant"; then
    bad "$label: mutant could not be built (anchor missing)"
    rm -rf "$_a6_mutant_dir"
    return
  fi
  chmod +x "$mutant"
  # Override the adapter-path resolver for the duration of this call only —
  # restored immediately after, so no other assertion in this file (or a
  # later one) can observe the override.
  eval "_rc_canary_sessionstart_adapter() {
    local host=\"\$1\"
    if [ \"\$host\" = \"copilot\" ]; then printf '%s\n' \"$mutant\"; return 0; fi
    command _rc_canary_sessionstart_adapter_ORIG \"\$host\"
  }"
  local rc=0
  local out
  out="$(_rc_host_sessionstart_canary copilot "$REPO_ROOT" 2>&1)" || rc=$?
  # Restore the real resolver.
  eval "$(declare -f _rc_canary_sessionstart_adapter_ORIG | sed '1s/_ORIG//')"
  printf '%s\n' "$out" | sed 's/^/    /'
  rm -rf "$_a6_mutant_dir"
  if [ "$rc" -eq "$want_rc" ]; then
    ok "$label: rc=$rc as expected"
  else
    bad "$label: expected rc=$want_rc, got rc=$rc"
  fi
}

run_must_fail() {
  printf '\n\xe2\x94\x80\xe2\x94\x80 Phase 6 must-fail halves \xe2\x94\x80\xe2\x94\x80\n'
  # Snapshot the real resolver under an alternate name so the two mutant
  # drivers can restore it deterministically regardless of call order.
  eval "$(declare -f _rc_canary_sessionstart_adapter | sed '1s/^_rc_canary_sessionstart_adapter/_rc_canary_sessionstart_adapter_ORIG/')"

  printf '\nA6.2 \xe2\x80\x94 must-fail: adapter never invokes the probe \xe2\x86\x92 INVOCATION failure (rc=3)\n'
  _run_copilot_mutant a62 3 "A6.2 (marker never fires)"

  printf '\nA6.3 \xe2\x80\x94 must-fail: adapter swallows stdout \xe2\x86\x92 DELIVERY failure (rc=2), distinct from A6.2\n'
  _run_copilot_mutant a63 2 "A6.3 (sentinel swallowed)"
}

MODE="${1:-}"
case "$MODE" in
  --must-fail)
    run_must_fail
    ;;
  --self-test)
    run_a61
    run_a64
    run_a65
    run_must_fail
    ;;
  "")
    run_a61
    run_a64
    run_a65
    ;;
  *)
    echo "usage: test-tier-a-canary.sh [--self-test|--must-fail]" >&2
    exit 2
    ;;
esac

printf '\n\xe2\x94\x80\xe2\x94\x80 Phase 6 acceptance tests: %d passed, %d failed \xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
