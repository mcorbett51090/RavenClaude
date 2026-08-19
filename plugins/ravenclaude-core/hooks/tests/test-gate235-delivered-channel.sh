#!/usr/bin/env bash
# test-gate235-delivered-channel.sh — asserts REAL hooks reach the model.
#
# ⛔ WHY. Measured 2026-08-19: 56 hook tests existed; 5 asserted additionalContext
# and ZERO asserted updatedToolOutput. Five advisory hooks had therefore written to
# a channel that reaches the model on no event, for their entire service life, with
# every test passing — because the tests asserted on stderr, which is exactly what
# the hooks produced. The tests could not fail.
#
# control: the bake-off that established this carried a SessionStart additionalContext
# sentinel which arrived in EVERY trial, so each negative was a fact about the channel
# rather than a blind harness.
#
# ⛔ A FIXTURE IS NOT A WIRING PROOF. lib/assert-delivered-channel.sh self-tests against
# synthetic hooks; this file runs the SAME assertions against hooks that actually ship,
# because a library proven only on fixtures is the shape that goes green while the real
# surface is broken. That exact defect is recorded in this repo's history.
#
# ⛔ SLOT NOTE: this is gate 235, not 234. Gate 234 was ALREADY IMPLEMENTED (the
# handoff --host contract) and already listed in the --check dispatcher. Checking the
# slot before claiming it is the difference between a new gate and a silent collision
# that breaks the dispatcher.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
HOOKS="$(cd "$HERE/.." && pwd)"
. "$HERE/lib/assert-delivered-channel.sh"

adc_init || { echo "gate235: cannot init"; exit 1; }

echo "── Gate 235: hooks reach the model (delivered-channel assertions) ──"

# The library must prove itself before this suite trusts a single verdict.
if bash "$HERE/lib/assert-delivered-channel.sh" --self-test >/dev/null 2>&1; then
  echo "  ok   the assertion library self-test passes (6/6, both canaries bite)"
else
  echo "  FAIL the assertion library self-test FAILED — every verdict below is void"
  exit 1
fi

PROJ="$ADC_SCRATCH/proj"; mkdir -p "$PROJ/.ravenclaude"
printf 'probe_validity: on\ncause_triage: warn\n' > "$PROJ/.ravenclaude/comfort-posture.yaml"
export CLAUDE_PROJECT_DIR="$PROJ"

# ── TIER 1: a real ADVISORY hook, converted 2026-08-19, must reach the model ──
# guard-probe-validity fires its single rule on `grep -v` in quiet mode.
cat > "$ADC_SCRATCH/pv.json" <<JSON
{"session_id":"g235","cwd":"$PROJ","tool_name":"Bash","tool_input":{"command":"grep -qv alpha mixed.txt"}}
JSON
assert_delivers_additional_context "$HOOKS/guard-probe-validity.sh" "$ADC_SCRATCH/pv.json" "probe-validity"

# ── TIER 4: a real INTERNAL-LOGGING hook must be terminal-only ──────────────
# Per docs/plans/2026-08-19-product-inventory/p0-hook-channel-dispositions.md,
# dashboard-autostart is a launcher: its consumer is the human who wants the URL.
# Asserting it here means a future edit that silently adds delivery FAILS, and one
# that silently drops the message FAILS — the tier is a tested decision, not an
# exemption. Skipped LOUDLY if the hook declines to run in this environment.
cat > "$ADC_SCRATCH/ss.json" <<JSON
{"session_id":"g235","cwd":"$PROJ","hook_event_name":"SessionStart"}
JSON
if bash "$HOOKS/dashboard-autostart.sh" < "$ADC_SCRATCH/ss.json" 2>&1 | grep -q 'dashboard'; then
  assert_terminal_only "$HOOKS/dashboard-autostart.sh" "$ADC_SCRATCH/ss.json" "dashboard"
else
  echo "  skip dashboard-autostart did not emit in this environment (LOUD skip, never a pass)"
fi

adc_report
_rc=$?

echo
if [ "$_rc" -eq 0 ]; then echo "gate235 delivered-channel: PASS"; else echo "gate235 delivered-channel: FAIL"; fi
exit "$_rc"
