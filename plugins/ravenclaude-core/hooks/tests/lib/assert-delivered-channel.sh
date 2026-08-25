#!/usr/bin/env bash
# assert-delivered-channel.sh — the assertion 56 hook tests did not have.
#
# ⛔ WHY THIS EXISTS. Measured 2026-08-19: five advisory hooks wrote to stderr and
# exited 0 for their entire service life, and that channel reaches the model on NO
# event — PostToolUse, PreToolUse or Stop alike. Every one of their unit tests
# passed the whole time, because those tests asserted on STDERR, which is exactly
# what the hooks were (correctly) producing. The tests could not fail.
#
# control: a SessionStart additionalContext sentinel arrived in EVERY trial of that
# bake-off, so each negative was a fact about the channel and not a blind harness.
#
# So the defect was never "a hook is broken". It was "no test asserts that a hook's
# output ARRIVES". At the time of writing: 56 hook tests, 5 assert additionalContext,
# ZERO assert updatedToolOutput. This library exists so that stops being true, and so
# the next hook cannot ship on a dead channel without a test noticing.
#
# ── USAGE ───────────────────────────────────────────────────────────────────
#   . "$(dirname "${BASH_SOURCE[0]}")/lib/assert-delivered-channel.sh"
#   adc_init                       # required: sets up the scratch dir + counters
#   assert_delivers_additional_context  <hook> <payload-file> <sentinel>
#   assert_delivers_updated_tool_output <hook> <payload-file> <sentinel>
#   assert_denies                       <hook> <payload-file>
#   assert_terminal_only                <hook> <payload-file> <sentinel>
#   adc_report                     # prints the tally, returns non-zero on any failure
#
# ⛔ EVERY assertion has a NEUTERED-COPY CANARY. Each helper, on success, copies the
# hook, strips its emitting construct, and re-runs — requiring the assertion to FAIL
# on the copy. Without that, "the hook delivers" and "the helper never actually
# checked" are indistinguishable, which is the very defect this file exists to catch,
# reproduced inside the fixer. A helper whose canary does not bite reports FAIL.
#
# ⛔ FOUR TIERS, because "not on the delivered channel" is not automatically a bug:
#   advisory        -> assert_delivers_additional_context   (reaches the model)
#   tool-rewriting  -> assert_delivers_updated_tool_output  (REPLACES the result)
#   fail-closed     -> assert_denies                        (exit 2 / permissionDecision)
#   internal-logging-> assert_terminal_only                 (stderr AND no delivered channel)
# The last one is the point: an internal-logging hook becomes TESTED AS SUCH rather
# than untested, so a later edit that silently adds or drops delivery fails.
#
# Portability: bash 3.2 / BSD-safe. No declare -A, no mapfile, no GNU timeout.

ADC_PASS=0
ADC_FAIL=0
ADC_SCRATCH=""

adc_init() {
  ADC_PASS=0
  ADC_FAIL=0
  ADC_SCRATCH="$(mktemp -d "${TMPDIR:-/tmp}/adc.XXXXXX")" || return 1
  trap 'rm -rf "$ADC_SCRATCH"' EXIT
}

_adc_ok()   { ADC_PASS=$((ADC_PASS + 1)); printf '  ok   %s\n' "$1"; }
_adc_bad()  { ADC_FAIL=$((ADC_FAIL + 1)); printf '  FAIL %s\n' "$1"; }

# _adc_run <hook> <payload-file> -> stdout in $ADC_OUT, stderr in $ADC_ERR, rc in $ADC_RC
_adc_run() {
  ADC_OUT="$ADC_SCRATCH/out.$$"
  ADC_ERR="$ADC_SCRATCH/err.$$"
  bash "$1" < "$2" > "$ADC_OUT" 2> "$ADC_ERR"
  ADC_RC=$?
  return 0
}

# _adc_field <json-file> <dotted.path> -> prints the value, empty if absent/unparseable
_adc_field() {
  ADC_F="$1" ADC_P="$2" python3 -c '
import json, os, sys
try:
    d = json.load(open(os.environ["ADC_F"]))
except Exception:
    sys.exit(0)
for part in os.environ["ADC_P"].split("."):
    if not isinstance(d, dict) or part not in d:
        sys.exit(0)
    d = d[part]
print(d if isinstance(d, str) else json.dumps(d))
' 2>/dev/null
}

# _adc_neuter <hook> <regex-to-strip> -> path to a neutered copy
_adc_neuter() {
  _n="$ADC_SCRATCH/neutered.$$.sh"
  ADC_SRC="$1" ADC_RX="$2" ADC_DST="$_n" python3 -c '
import os, re
src = open(os.environ["ADC_SRC"], errors="replace").read()
out = re.sub(os.environ["ADC_RX"], "", src)
open(os.environ["ADC_DST"], "w").write(out)
' 2>/dev/null || return 1
  printf '%s' "$_n"
}

# ── TIER 1: advisory. Reaches the model via additionalContext. ──────────────
assert_delivers_additional_context() {
  _hook="$1"; _payload="$2"; _sentinel="$3"; _name="$(basename "$_hook")"
  _adc_run "$_hook" "$_payload"
  _got="$(_adc_field "$ADC_OUT" "hookSpecificOutput.additionalContext")"
  case "$_got" in
    *"$_sentinel"*) _adc_ok "$_name delivers additionalContext containing the sentinel" ;;
    "")             _adc_bad "$_name emitted NO additionalContext (the dead-channel defect)"; return 1 ;;
    *)              _adc_bad "$_name emitted additionalContext without the sentinel"; return 1 ;;
  esac
  # canary: strip every additionalContext emit; the assertion must now fail.
  _cp="$(_adc_neuter "$_hook" '.*additionalContext.*')" || { _adc_bad "$_name canary could not build"; return 1; }
  _adc_run "$_cp" "$_payload"
  _c="$(_adc_field "$ADC_OUT" "hookSpecificOutput.additionalContext")"
  case "$_c" in
    *"$_sentinel"*) _adc_bad "$_name CANARY DID NOT BITE — a neutered hook still passed; this assertion proves nothing"; return 1 ;;
    *)              _adc_ok "$_name canary bites (neutered copy delivers nothing)" ;;
  esac
}

# ── TIER 2: tool-rewriting. REPLACES the tool result. Zero tests did this. ──
assert_delivers_updated_tool_output() {
  _hook="$1"; _payload="$2"; _sentinel="$3"; _name="$(basename "$_hook")"
  _adc_run "$_hook" "$_payload"
  _got="$(_adc_field "$ADC_OUT" "hookSpecificOutput.updatedToolOutput")"
  case "$_got" in
    *"$_sentinel"*) _adc_ok "$_name delivers updatedToolOutput containing the sentinel" ;;
    "")             _adc_bad "$_name emitted NO updatedToolOutput"; return 1 ;;
    *)              _adc_bad "$_name emitted updatedToolOutput without the sentinel"; return 1 ;;
  esac
  _cp="$(_adc_neuter "$_hook" '.*updatedToolOutput.*')" || { _adc_bad "$_name canary could not build"; return 1; }
  _adc_run "$_cp" "$_payload"
  _c="$(_adc_field "$ADC_OUT" "hookSpecificOutput.updatedToolOutput")"
  case "$_c" in
    *"$_sentinel"*) _adc_bad "$_name CANARY DID NOT BITE on updatedToolOutput"; return 1 ;;
    *)              _adc_ok "$_name canary bites (neutered copy rewrites nothing)" ;;
  esac
}

# ── TIER 3: fail-closed. exit 2 / permissionDecision. This channel already works. ──
assert_denies() {
  _hook="$1"; _payload="$2"; _name="$(basename "$_hook")"
  _adc_run "$_hook" "$_payload"
  _dec="$(_adc_field "$ADC_OUT" "hookSpecificOutput.permissionDecision")"
  if [ "$_dec" = "deny" ] || [ "$ADC_RC" -eq 2 ]; then
    _adc_ok "$_name denies (permissionDecision=deny or exit 2)"
  else
    _adc_bad "$_name did NOT deny (decision='$_dec' rc=$ADC_RC)"; return 1
  fi
}

# ── TIER 4: internal-logging. The POSITIVE statement of the stderr tier. ────
# Asserts BOTH halves: the message is on stderr AND no delivered channel is used.
# So a later edit that silently ADDS delivery fails, and one that silently DROPS
# the message fails. The tier becomes a tested decision, not an exemption.
assert_terminal_only() {
  _hook="$1"; _payload="$2"; _sentinel="$3"; _name="$(basename "$_hook")"
  _adc_run "$_hook" "$_payload"
  if ! grep -q "$_sentinel" "$ADC_ERR" 2>/dev/null; then
    _adc_bad "$_name: expected the message on stderr and it was absent"; return 1
  fi
  _ac="$(_adc_field "$ADC_OUT" "hookSpecificOutput.additionalContext")"
  _ut="$(_adc_field "$ADC_OUT" "hookSpecificOutput.updatedToolOutput")"
  if [ -n "$_ac" ] || [ -n "$_ut" ]; then
    _adc_bad "$_name is classified internal-logging but USES a delivered channel — reclassify it or drop the emit"; return 1
  fi
  _adc_ok "$_name is terminal-only (stderr carries it; no delivered channel)"
}

adc_report() {
  printf '\n  delivered-channel assertions: %d passed, %d failed\n' "$ADC_PASS" "$ADC_FAIL"
  [ "$ADC_FAIL" -eq 0 ]
}

# ── SELF-TEST — prove the library before any suite trusts it ────────────────
if [ "${1:-}" = "--self-test" ]; then
  adc_init || { echo "adc: cannot init"; exit 1; }
  _f="$ADC_SCRATCH/fx"; mkdir -p "$_f"
  printf '{"hook_event_name":"PostToolUse","tool_name":"Bash","tool_input":{"command":"x"},"tool_response":{"stdout":"","stderr":"","interrupted":false}}' > "$_f/p.json"

  printf '#!/usr/bin/env bash\ncat >/dev/null\nprintf %%s %s\n' \
    "'{\"hookSpecificOutput\":{\"hookEventName\":\"PostToolUse\",\"additionalContext\":\"SENTINEL_OK\"}}'" > "$_f/adv.sh"
  printf '#!/usr/bin/env bash\ncat >/dev/null\nprintf %%s %s\n' \
    "'{\"hookSpecificOutput\":{\"hookEventName\":\"PostToolUse\",\"updatedToolOutput\":{\"stdout\":\"SENTINEL_OK\"}}}'" > "$_f/rew.sh"
  printf '#!/usr/bin/env bash\ncat >/dev/null\necho "SENTINEL_OK" >&2\nexit 0\n' > "$_f/log.sh"

  assert_delivers_additional_context  "$_f/adv.sh" "$_f/p.json" SENTINEL_OK
  assert_delivers_updated_tool_output "$_f/rew.sh" "$_f/p.json" SENTINEL_OK
  assert_terminal_only                "$_f/log.sh" "$_f/p.json" SENTINEL_OK

  # ⛔ the cross-tier check: a terminal-only hook must FAIL the advisory assertion.
  # This is what makes the two tiers distinguishable rather than merely labelled.
  _before="$ADC_FAIL"
  assert_delivers_additional_context "$_f/log.sh" "$_f/p.json" SENTINEL_OK >/dev/null 2>&1
  if [ "$ADC_FAIL" -gt "$_before" ]; then
    ADC_FAIL="$_before"; _adc_ok "cross-tier: a stderr-only hook correctly FAILS the advisory assertion"
  else
    _adc_bad "cross-tier: a stderr-only hook PASSED the advisory assertion — the tiers are not distinguishable"
  fi

  adc_report
  exit $?
fi
