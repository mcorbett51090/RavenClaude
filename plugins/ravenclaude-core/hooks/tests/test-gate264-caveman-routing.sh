#!/usr/bin/env bash
#
# Gate 264 -- caveman auto-routing: P6 CI registration (plan.md P6).
#
# This gate does NOT reimplement any component's own must-fail teeth. The
# dedupe-mutant (P1), the snapshot-abort-removed mutant + readback-mismatch
# fixture (P2), and the shadow-gate/source-branching/no-egress mutants (P3)
# already live inside each component's own --self-test, proven at 11/11,
# 8/8 and 21/21 respectively before this gate existed. Re-deriving them here
# would be duplicated fixture logic that can drift from the real one -- this
# gate instead WIRES those self-tests in and proves this file's own harness
# is load-bearing (--must-fail-a): a self-test that regresses to nonzero
# exit, or that silently stops asserting anything (an N/N pass-count of 0/0
# would still be exit 0), must be caught here, not waved through.
#
# The ONE genuinely new check this gate adds (check 4) is that all three
# host projectors still carry the caveman-route-hook.sh _SKIP registration
# and that the copilot generator's own stale-map check stays clean -- a
# future accidental removal of any of the three would otherwise ship
# silently, because nothing calls caveman-route-hook.sh in a way any other
# gate would notice. Check 4 gets its own teeth (--must-fail-b).
#
# Read-back verification (P6 item 7) is exercised by construction: the same
# caveman-apply-mode.sh --self-test invoked at check 2 includes the
# readback-mismatch fixture (confirmed this build: its own self-test output
# names the fixture explicitly -- "readback-mismatch: broken fixture
# detected, warn event emitted", with a same-shaped control fixture proving
# the emit is conditional, not unconditional). No separate check is added
# for it here; a separate one would be the duplicated-fixture-logic mistake
# this file's header opens by naming.
#
# ⛔ NO APOSTROPHES (spike-tprose-canary.sh convention, matched here for
# consistency even though this file is not itself scanned by that canary).

set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
cd "$ROOT" || exit 1

PASS=0
FAIL=0
ok() {
  PASS=$((PASS + 1))
  printf '  OK    %s\n' "$1"
}
bad() {
  FAIL=$((FAIL + 1))
  printf '  FAIL  %s (%s)\n' "$1" "$2"
}

mode="${1:-}"

ROUTE_PY="$ROOT/plugins/ravenclaude-core/scripts/caveman-route.py"
APPLY_SH="$ROOT/plugins/ravenclaude-core/scripts/caveman-apply-mode.sh"
HOOK_SH="$ROOT/plugins/ravenclaude-core/scripts/caveman-route-hook.sh"
COPILOT_GEN="$ROOT/scripts/generate-copilot-hooks.py"
CURSOR_GEN="$ROOT/scripts/generate-cursor-hooks.py"
GEMINI_GEN="$ROOT/scripts/generate-gemini-hooks.py"

# ── run_selftest <label> <min_assertions> <cmd...> ───────────────────────────
# Runs a component's --self-test, requires exit 0 AND a computed N/N
# pass-count (never a hardcoded literal -- the Gate 260 lesson) with N==D
# and N at least min_assertions, so an exit-0-but-zero-assertions run cannot
# read as a pass. Returns 0 (recorded ok) or 1 (recorded bad).
run_selftest() {
  local label="$1" min="$2"
  shift 2
  local out rc=0
  out="$("$@" 2>&1)" || rc=$?
  if [ "$rc" -ne 0 ]; then
    bad "$label" "exit=$rc: $(printf '%s' "$out" | tail -1)"
    return 1
  fi
  local pair
  pair="$(printf '%s\n' "$out" | grep -oE '[0-9]+/[0-9]+' | tail -1)"
  if [ -z "$pair" ]; then
    bad "$label" "no N/N pass-count found in self-test output"
    return 1
  fi
  local n d
  n="${pair%%/*}"
  d="${pair##*/}"
  if [ "$n" != "$d" ] || [ "$n" -lt "$min" ]; then
    bad "$label" "pass-count $pair (want equal halves, >= $min)"
    return 1
  fi
  ok "$label ($pair)"
  return 0
}

# ── projector_check <copilot_skip_src> <cursor_skip_src> <gemini_skip_src> <copilot_gen_or_empty> ──
# Check 4: the _SKIP registration itself, plus (when copilot_gen is
# non-empty) the real copilot generator's stale-map self-check.
projector_check() {
  local cop="$1" cur="$2" gem="$3" cop_gen="$4"
  local miss=""
  grep -qF '"caveman-route-hook.sh":' "$cop" || miss="$miss copilot"
  grep -qF '"caveman-route-hook.sh":' "$cur" || miss="$miss cursor"
  grep -qF '"caveman-route-hook.sh":' "$gem" || miss="$miss gemini"
  if [ -n "$miss" ]; then
    bad "projector _SKIP registration (caveman-route-hook.sh)" "missing in:$miss"
    return 1
  fi
  if [ -n "$cop_gen" ]; then
    local gen_out gen_rc
    gen_out="$(python3 "$cop_gen" 2>&1 1>/dev/null)"
    gen_rc=$?
    if [ "$gen_rc" -ne 0 ] || printf '%s' "$gen_out" | grep -q 'skip map names hooks that no longer exist'; then
      bad "copilot stale-map check (stale = set(_SKIP) - canonical)" "generator rc=$gen_rc: $gen_out"
      return 1
    fi
  fi
  ok "projector _SKIP registration (copilot+cursor+gemini) + copilot stale-map check clean"
  return 0
}

case "$mode" in
--must-fail-a)
  echo "── Gate 264 teeth (a): a regressed component self-test must redden this gate's harness ──"
  if run_selftest "PLANTED regressed self-test (exit 1, stands in for any of the three)" 1 \
    python3 -c 'import sys; sys.exit(1)'; then
    echo "  the harness did NOT detect the planted regression -- toothless" >&2
    exit 0
  else
    echo "  the harness correctly detected the planted regression"
    exit 1
  fi
  ;;
--must-fail-b)
  echo "── Gate 264 teeth (b): stripping a projector's _SKIP entry must redden check 4 ──"
  T="$(mktemp -d)"
  trap 'rm -rf "$T"' EXIT
  # Mutant: drop the caveman-route-hook.sh block from a copy of the gemini
  # projector. One mutant is sufficient -- the grep logic in projector_check
  # is identical for all three files, so this proves the check is
  # load-bearing rather than decoration, without needing three near-identical
  # mutants.
  python3 - "$GEMINI_GEN" "$T/gemini-mutant.py" <<'PY'
import sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src, encoding="utf-8").read()
marker = '"caveman-route-hook.sh": ('
start = text.index(marker)
end = text.index("),\n", start) + len("),\n")
mutated = text[:start] + text[end:]
open(dst, "w", encoding="utf-8").write(mutated)
PY
  if grep -qF '"caveman-route-hook.sh":' "$T/gemini-mutant.py"; then
    echo "  the mutant fixture itself still carries the entry -- fixture is broken, not a real test" >&2
    exit 0
  fi
  if projector_check "$COPILOT_GEN" "$CURSOR_GEN" "$T/gemini-mutant.py" ""; then
    echo "  check 4 did NOT detect the stripped _SKIP entry -- toothless" >&2
    exit 0
  else
    echo "  check 4 correctly detected the stripped _SKIP entry"
    exit 1
  fi
  ;;
"")
  echo "── Gate 264: caveman auto-routing -- P1-P5 self-tests wired + P6 projector-registration check ──"
  run_selftest "caveman-route.py --self-test (classifier: dedupe/mid-window-pivot/torn-line/empty-transcript mutants inside)" 8 \
    python3 "$ROUTE_PY" --self-test
  run_selftest "caveman-apply-mode.sh --self-test (applier: snapshot-abort + readback-mismatch + restore mutants inside)" 6 \
    bash "$APPLY_SH" --self-test
  run_selftest "caveman-route-hook.sh --self-test (hook body: short-circuit/shadow/source-branching/no-egress mutants inside)" 15 \
    bash "$HOOK_SH" --self-test
  projector_check "$COPILOT_GEN" "$CURSOR_GEN" "$GEMINI_GEN" "$COPILOT_GEN"
  echo
  printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
  [ "$FAIL" -eq 0 ] || exit 1
  ;;
*)
  echo "usage: $0 [--must-fail-a|--must-fail-b]" >&2
  exit 2
  ;;
esac
