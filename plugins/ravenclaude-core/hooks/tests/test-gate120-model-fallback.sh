#!/usr/bin/env bash
# Gate 120 — model-fallback helper (_model-fallback.sh).
# Drives the ladder with a MOCK runner (never calls real `claude`). Asserts:
#   1 disabled path is byte-identical (primary only, one call)
#   2 primary overloaded ⇒ falls to next rung, succeeds
#   3 primary auth-error ⇒ STOP, no retry (the masking-a-real-bug guard)
#   4 all overloaded ⇒ exhausts at max_retries (the cost cap), fail-safe non-zero
#   5 --exclude model is skipped (diversity / anti-self-grade guard)
#   6 MUST-FAIL HALF: stripping the classifier makes the auth error retry — proving
#     the real `stop` classification has teeth.
#
# Call order is tracked in a FILE, not a var: the helper captures the runner via
# command substitution (a subshell), so a var the runner sets would be lost. The
# resolved model escapes the same way, via _MF_RESOLVED_FILE.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
HELPER="$HERE/../_model-fallback.sh"
fails=0
pass() { echo "  ✓ $1"; }
fail() {
  echo "  ✗ $1"
  fails=$((fails + 1))
}

# shellcheck source=/dev/null
. "$HELPER"

OUT="$(mktemp)"
RESF="$(mktemp)"
CALLSF="$(mktemp)"
export _MF_RESOLVED_FILE="$RESF"

# ── Mock runner ────────────────────────────────────────────────────────────────
# _MOCK[<model>]="<exit>|<stderr-text>|<stdout>" ; each call appends the model to $CALLSF.
declare -A _MOCK
export _CALLSF="$CALLSF"
_mock_run() {
  local m="$1" spec="${_MOCK[$1]:-1|unknown|}"
  local rc="${spec%%|*}" rest="${spec#*|}"
  local err="${rest%%|*}" out="${rest#*|}"
  printf '%s\n' "$m" >>"$_CALLSF"
  printf '%s' "$err" >"$_MF_ERRFILE"
  printf '%s' "$out"
  return "${rc:-1}"
}
reset() {
  : >"$OUT"
  : >"$RESF"
  : >"$CALLSF"
}
calls() { paste -sd, "$CALLSF" 2>/dev/null; }
resolved() { cat "$RESF" 2>/dev/null; }
outval() { cat "$OUT" 2>/dev/null; }

# ── 1. disabled ⇒ primary only, byte-identical ─────────────────────────────────
reset
_MOCK=([haiku]='0||{"result":"ok"}')
MODEL_FALLBACK_ENABLED=0 MODEL_FALLBACK_PRIMARY=haiku MODEL_FALLBACK_LADDER="sonnet,opus" \
  _model_call_with_fallback --runner _mock_run >"$OUT"
rc=$?
if [ "$rc" -eq 0 ] && [ "$(outval)" = '{"result":"ok"}' ] && [ "$(calls)" = "haiku" ] && [ "$(resolved)" = "haiku" ]; then
  pass "disabled path = primary only, one call, byte-identical"
else
  fail "disabled path (rc=$rc calls=$(calls) resolved=$(resolved) out=$(outval))"
fi

# ── 2. primary overloaded ⇒ next rung succeeds ─────────────────────────────────
reset
_MOCK=([haiku]='1|{"type":"overloaded_error"}|' [sonnet]='0||{"result":"ok2"}')
MODEL_FALLBACK_ENABLED=1 MODEL_FALLBACK_PRIMARY=haiku MODEL_FALLBACK_LADDER="sonnet,opus" \
  _model_call_with_fallback --runner _mock_run >"$OUT"
rc=$?
if [ "$rc" -eq 0 ] && [ "$(outval)" = '{"result":"ok2"}' ] && [ "$(calls)" = "haiku,sonnet" ] && [ "$(resolved)" = "sonnet" ]; then
  pass "overloaded primary ⇒ falls to sonnet, succeeds"
else
  fail "overloaded fallback (rc=$rc calls=$(calls) resolved=$(resolved) out=$(outval))"
fi

# ── 3. primary auth-error ⇒ STOP, no retry ─────────────────────────────────────
reset
_MOCK=([haiku]='1|{"type":"authentication_error"}|' [sonnet]='0||{"result":"should-not-reach"}')
MODEL_FALLBACK_ENABLED=1 MODEL_FALLBACK_PRIMARY=haiku MODEL_FALLBACK_LADDER="sonnet,opus" \
  _model_call_with_fallback --runner _mock_run >"$OUT"
rc=$?
if [ "$rc" -ne 0 ] && [ "$(calls)" = "haiku" ]; then
  pass "auth error ⇒ STOP, no retry (only primary called)"
else
  fail "auth no-retry (rc=$rc calls=$(calls) — expected only 'haiku')"
fi

# ── 4. all overloaded ⇒ exhaust at max_retries (cost cap) ──────────────────────
reset
_MOCK=([haiku]='1|overloaded_error|' [sonnet]='1|overloaded_error|' [opus]='1|overloaded_error|' [fable]='1|overloaded_error|')
MODEL_FALLBACK_ENABLED=1 MODEL_FALLBACK_PRIMARY=haiku MODEL_FALLBACK_LADDER="sonnet,opus,fable" MODEL_FALLBACK_MAX_RETRIES=2 \
  _model_call_with_fallback --runner _mock_run >"$OUT"
rc=$?
# primary + 2 retries = 3 calls; the 4th rung (fable) must NOT be reached.
if [ "$rc" -ne 0 ] && [ "$(calls)" = "haiku,sonnet,opus" ]; then
  pass "all overloaded ⇒ exhausts at max_retries=2 (3 calls), fail-safe non-zero"
else
  fail "max_retries cap (rc=$rc calls=$(calls) — expected 'haiku,sonnet,opus')"
fi

# ── 5. --exclude is skipped ────────────────────────────────────────────────────
reset
_MOCK=([haiku]='1|overloaded_error|' [sonnet]='0||{"result":"nope"}' [opus]='0||{"result":"ok5"}')
MODEL_FALLBACK_ENABLED=1 MODEL_FALLBACK_PRIMARY=haiku MODEL_FALLBACK_LADDER="sonnet,opus" \
  _model_call_with_fallback --runner _mock_run --exclude sonnet >"$OUT"
rc=$?
if [ "$rc" -eq 0 ] && [ "$(outval)" = '{"result":"ok5"}' ] && [ "$(calls)" = "haiku,opus" ] && [ "$(resolved)" = "opus" ]; then
  pass "--exclude sonnet ⇒ skipped, resolves to opus"
else
  fail "exclude (rc=$rc calls=$(calls) resolved=$(resolved) out=$(outval))"
fi

# ── 6. MUST-FAIL HALF: strip the classifier ⇒ auth retries (proves teeth) ──────
reset
_mf_classify() { printf 'retry\n'; } # mutate: every failure looks retryable (the bug)
_MOCK=([haiku]='1|{"type":"authentication_error"}|' [sonnet]='1|{"type":"authentication_error"}|' [opus]='1|{"type":"authentication_error"}|')
MODEL_FALLBACK_ENABLED=1 MODEL_FALLBACK_PRIMARY=haiku MODEL_FALLBACK_LADDER="sonnet,opus" MODEL_FALLBACK_MAX_RETRIES=2 \
  _model_call_with_fallback --runner _mock_run >"$OUT"
rc=$?
if [ "$(calls)" != "haiku" ]; then
  pass "must-fail half: stripped classifier retries auth (calls=$(calls)) — real 'stop' has teeth"
else
  fail "must-fail half did NOT diverge — the classifier guard is a no-op (calls=$(calls))"
fi

rm -f "$OUT" "$RESF" "$CALLSF"
echo ""
if [ "$fails" -eq 0 ]; then
  echo "Gate 120 PASS — model-fallback helper: classification, cost cap, exclude, disabled-byte-identical, teeth."
  exit 0
else
  echo "Gate 120 FAIL — $fails subtest(s) failed."
  exit 1
fi
