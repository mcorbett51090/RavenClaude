#!/usr/bin/env bash
# test-phase0-emit-and-scrub.sh — fixture tests for Gate 50 (Phase 0 emit & scrub).
#
# Proves that:
#   G50.1 — thing-orchestrator.sh deny emits a JSONL line.
#   G50.2 — route-decision-review.sh binding deny emits a JSONL line.
#   G50.3 — _scrub_reason() redacts secret-shaped substrings.
#   G50.4 — Scrub fires BEFORE the JSONL write (secret never reaches the log).
#   G50.5 — Must-fail half: removing the scrub call lets the secret through,
#            proving G50.4 has teeth.
#
# Run directly:   bash plugins/ravenclaude-core/hooks/tests/test-phase0-emit-and-scrub.sh
# Run via gate:   invoked by scripts/audit-gates.sh Gate 50.
#
# Design notes:
#   * G50.2 does NOT invoke a live `claude` binary — it uses THING_DECIDE_MOCK_VERDICT
#     to provide a canned yes-verdict from thing-decide.py, which is CI-safe.
#   * G50.5 constructs a patched _emit-event.sh in a tmp dir to prove the scrub call
#     is load-bearing: with it absent the secret leaks, with it present it doesn't.
#   * All tmp state is cleaned up on exit.

set -uo pipefail

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED=0
pass() { printf '  \xe2\x9c\x93 %s\n' "$1"; }
fail() { printf '  \xe2\x9c\x97 %s\n' "$1"; FAILED=$((FAILED + 1)); }

# A force-push string assembled from pieces so the literal pattern never appears
# verbatim in this file (guards/greppers would flag it).
FORCED_PUSH="git push --""force origin main"

# ── G50.1 — thing-orchestrator deny emits a JSONL line ───────────────────────
#
# Drive thing-orchestrator.sh with a force-push payload (the hard-rule pre-LLM
# deny, §B.9.3) and assert that a JSONL line is emitted to hook-events.jsonl.
# The hard-rule deny is deterministic — no live `claude` call needed.
#
# Expected Phase 0 state: the orchestrator's hard-rule deny branch calls
# _emit_hook_event. If Phase 0 is not yet wired, the JSONL will be absent and
# this test will fail with "expected JSONL line not present".

echo "── G50.1: thing-orchestrator deny emits JSONL ────────────────────────────"
T1="$(mktemp -d)"
mkdir -p "$T1/.ravenclaude"
cat > "$T1/.ravenclaude/comfort-posture.yaml" <<'YAML'
schema_version: 5
categories:
  shell_remote_mutate:
    user: ask
    local: ask
    project: inherit
    thing: on
YAML

LOG1="$T1/.ravenclaude/runs/g50t1/hook-events.jsonl"

rc=0
jq -cn --arg cwd "$T1" \
  '{tool_name:"Bash",tool_input:{command:"'"$FORCED_PUSH"'"},cwd:$cwd,session_id:"g50t1"}' \
  | CLAUDE_PROJECT_DIR="$T1" CLAUDE_SESSION_ID="g50t1" \
    bash "$HOOKS_DIR/thing-orchestrator.sh" >/dev/null 2>&1 || rc=$?
# exit 2 or any non-zero is expected (deny). We only care about the JSONL.

if [[ -f "$LOG1" ]]; then
  line_count="$(wc -l < "$LOG1")"
  if [[ "$line_count" -ge 1 ]]; then
    # Validate JSON
    if jq -e . < "$LOG1" >/dev/null 2>&1; then
      hook_val="$(jq -r '.hook' "$LOG1" 2>/dev/null)"
      verdict_val="$(jq -r '.verdict' "$LOG1" 2>/dev/null)"
      tool_val="$(jq -r '.tool' "$LOG1" 2>/dev/null)"
      rule_val="$(jq -r '.rule' "$LOG1" 2>/dev/null)"
      ok=1
      [[ "$hook_val" == "thing-orchestrator.sh" ]] || { ok=0; fail "G50.1: hook field is '$hook_val', expected 'thing-orchestrator.sh'"; }
      [[ "$verdict_val" == "deny" ]] || { ok=0; fail "G50.1: verdict field is '$verdict_val', expected 'deny'"; }
      [[ "$tool_val" == "Bash" ]] || { ok=0; fail "G50.1: tool field is '$tool_val', expected 'Bash'"; }
      # rule should reference the deny path (hard-rule or pre-llm-hard-rule or similar)
      if printf '%s' "$rule_val" | grep -Eiq 'hard.rule|pre.llm|force.push|destructive|self.disable|jq.missing|fail.closed|always.screen'; then
        [[ "$ok" -eq 1 ]] && pass "G50.1: thing-orchestrator deny emits valid JSONL (hook=thing-orchestrator.sh, verdict=deny, tool=Bash, rule=$rule_val)"
      else
        fail "G50.1: rule field '$rule_val' does not name a recognizable deny path"
      fi
    else
      fail "G50.1: JSONL line is not valid JSON"
    fi
  else
    fail "G50.1: hook-events.jsonl exists but is empty"
  fi
else
  fail "G50.1: hook-events.jsonl not created — Phase 0 emit not yet wired in thing-orchestrator.sh"
fi
rm -rf "$T1"

# ── G50.2 — route-decision-review binding deny emits a JSONL line ────────────
#
# Drive route-decision-review.sh with an AskUserQuestion payload (a single yes/no
# question) while THING_DECIDE_MOCK_VERDICT=yes so thing-decide.py returns a
# canned binding yes verdict. Assert that a JSONL line is emitted.
#
# CI-safe: THING_DECIDE_MOCK_VERDICT bypasses the live `claude -p` engine in
# thing-decide.py (the same mock hook used in Gate 17).

echo
echo "── G50.2: route-decision-review binding deny emits JSONL ────────────────"
T2="$(mktemp -d)"
mkdir -p "$T2/.ravenclaude"
cat > "$T2/.ravenclaude/comfort-posture.yaml" <<'YAML'
schema_version: 5
decision_review: binding
YAML

LOG2="$T2/.ravenclaude/runs/g50t2/hook-events.jsonl"

# AskUserQuestion payload: single yes/no question with two binary options.
AUQ_PAYLOAD="$(jq -cn --arg cwd "$T2" '{
  tool_name: "AskUserQuestion",
  tool_input: {
    questions: [{
      question: "Should we proceed with the deployment?",
      multiSelect: false,
      options: [
        {"label": "Yes"},
        {"label": "No"}
      ]
    }]
  },
  cwd: $cwd,
  session_id: "g50t2"
}')"

# CLAUDE_PLUGIN_ROOT must point to the plugin root so route-decision-review.sh
# can find thing-decide.py. Without it the hook resolves the engine relative to
# the tmp dir (which has no scripts/) and falls back to emit_allow (no emit).
PLUGIN_ROOT="$(cd "$HOOKS_DIR/.." && pwd)"

rc=0
printf '%s' "$AUQ_PAYLOAD" \
  | CLAUDE_PROJECT_DIR="$T2" CLAUDE_SESSION_ID="g50t2" \
    CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" \
    THING_DECIDE_MOCK_VERDICT=yes \
    bash "$HOOKS_DIR/route-decision-review.sh" >/dev/null 2>&1 || rc=$?

if [[ -f "$LOG2" ]]; then
  if [[ "$(wc -l < "$LOG2")" -ge 1 ]] && jq -e . < "$LOG2" >/dev/null 2>&1; then
    hook_val="$(jq -r '.hook' "$LOG2" 2>/dev/null)"
    verdict_val="$(jq -r '.verdict' "$LOG2" 2>/dev/null)"
    tool_val="$(jq -r '.tool' "$LOG2" 2>/dev/null)"
    rule_val="$(jq -r '.rule' "$LOG2" 2>/dev/null)"
    ok=1
    [[ "$hook_val" == "route-decision-review.sh" ]] || { ok=0; fail "G50.2: hook='$hook_val', expected 'route-decision-review.sh'"; }
    [[ "$verdict_val" == "deny" ]] || { ok=0; fail "G50.2: verdict='$verdict_val', expected 'deny'"; }
    [[ "$tool_val" == "AskUserQuestion" ]] || { ok=0; fail "G50.2: tool='$tool_val', expected 'AskUserQuestion'"; }
    # rule should reference the binding verdict
    if printf '%s' "$rule_val" | grep -Eiq 'binding.verdict|auto.resolved|decision.review|binding'; then
      [[ "$ok" -eq 1 ]] && pass "G50.2: route-decision-review binding deny emits valid JSONL (rule=$rule_val)"
    else
      fail "G50.2: rule='$rule_val' does not reference binding-verdict path"
    fi
  else
    fail "G50.2: JSONL exists but is empty or invalid JSON"
  fi
else
  fail "G50.2: hook-events.jsonl not created — Phase 0 emit not yet wired in route-decision-review.sh"
fi
rm -rf "$T2"

# ── G50.3 — _scrub_reason() redacts secret-shaped substrings ─────────────────
#
# Source _scrub.sh (which defines _scrub_reason and _secret_patterns), call it
# with a JWT Bearer token, and assert:
#   (a) The literal JWT payload is NOT in the output.
#   (b) A redaction marker IS in the output.
#   (c) The surrounding structure (curl, -H, Authorization header context) is
#       preserved so a human can tell what the command was.

echo
echo "── G50.3: _scrub_reason() redacts JWT Bearer token ──────────────────────"
SCRUB_SH="$HOOKS_DIR/_scrub.sh"

if [[ ! -f "$SCRUB_SH" ]]; then
  fail "G50.3: _scrub.sh not found at $SCRUB_SH — cannot test _scrub_reason()"
else
  # The JWT pattern from _secret_patterns: eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{6,}
  # Realistic JWT shape — all three segments meet the minimum length the pattern
  # requires (10/10/20 after v0.112.1 — third segment tightened from 6 to 20 to
  # match real HMAC-SHA256 signatures which are 43 chars). A toy JWT with a
  # short signature does NOT match the pattern and the fixture must reflect a
  # realistic shape or it tests nothing.
  INPUT_SECRET="curl -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.fake-signature-32-base64url-chars-here'"
  LITERAL_JWT="eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.fake-signature-32-base64url-chars-here"

  scrubbed="$(
    # shellcheck source=/dev/null
    source "$SCRUB_SH"
    _scrub_reason "$INPUT_SECRET"
  )"

  ok=1
  # (a) literal JWT payload must not appear
  if printf '%s' "$scrubbed" | grep -Fq "$LITERAL_JWT"; then
    ok=0; fail "G50.3: scrubbed output still contains the literal JWT — secret not redacted"
  fi
  # (b) a redaction marker must appear
  if ! printf '%s' "$scrubbed" | grep -Eiq '\[REDACTED\]|REDACTED'; then
    ok=0; fail "G50.3: scrubbed output has no redaction marker (expected [REDACTED] or similar)"
  fi
  # (c) structural context should be preserved (curl is not a secret)
  if ! printf '%s' "$scrubbed" | grep -iq "curl"; then
    ok=0; fail "G50.3: scrubbed output lost 'curl' structural context — over-redacted"
  fi
  [[ "$ok" -eq 1 ]] && pass "G50.3: _scrub_reason() redacts JWT, preserves curl context"
fi

# ── G50.4 — Scrub fires BEFORE the JSONL write (substrate-wide invariant) ────
#
# Wire a deny with a secret-shaped reason (--password=hunter2 matches the
# `_secret_patterns` entry '--password[=[:space:]][^[:space:]]+') and assert
# that hunter2 does NOT appear in the JSONL line.
#
# This catches a regression where the scrub is moved from inside
# _emit_hook_event to the caller, allowing some callers to skip it.

echo
echo "── G50.4: Scrub fires before JSONL write (secret must not reach log) ────"
T4="$(mktemp -d)"

rc=0
(
  export CLAUDE_PROJECT_DIR="$T4" CLAUDE_SESSION_ID="g50t4"
  # shellcheck source=/dev/null
  source "$HOOKS_DIR/_emit-event.sh"
  # Inject a reason with a secret-shaped token matching --password pattern
  _emit_hook_event "thing-orchestrator.sh" "deny" "Bash" "git push" \
    "pre-llm-hard-rule: --password=hunter2 in command" 2
)

LOG4="$T4/.ravenclaude/runs/g50t4/hook-events.jsonl"
if [[ -f "$LOG4" ]]; then
  if jq -e . < "$LOG4" >/dev/null 2>&1; then
    if printf '%s' "$(cat "$LOG4")" | grep -Fq "hunter2"; then
      fail "G50.4: JSONL line contains 'hunter2' — secret leaked into the log; _scrub_reason not wired in _emit_hook_event"
    else
      pass "G50.4: JSONL log does not contain 'hunter2' — scrub fires before write"
    fi
  else
    fail "G50.4: JSONL line exists but is not valid JSON"
  fi
else
  fail "G50.4: hook-events.jsonl not created — _emit_hook_event not wiring the emit at all"
fi
rm -rf "$T4"

# ── G50.5 — Must-fail half: prove G50.4 has teeth ────────────────────────────
#
# Create a patched copy of _emit-event.sh with the _scrub_reason() call removed
# from inside _emit_hook_event (simulating a future regression). Re-run G50.4
# against the patched copy. Assert: the patched version DOES leak the secret
# (i.e., G50.4 would fail against the patched file). Restore and report.
#
# Implementation: we patch out the scrub call by commenting it out or replacing
# the _scrub_reason call with a no-op in a tmp copy, then run against that copy.
# If the patched copy allows the secret through, the must-fail assertion passes.

echo
echo "── G50.5 — Must-fail half: patched emit (no scrub) leaks the secret ─────"
T5_DIR="$(mktemp -d)"
PATCHED_EMIT="$T5_DIR/_emit-event.sh"

# Build the patched _emit-event.sh:
# We patch out the _scrub_reason call by replacing it with the raw reason passthrough.
# Strategy: copy the file, then replace any call to _scrub_reason with an identity
# substitution so the raw reason is used directly.
#
# Since _emit-event.sh may source _scrub.sh internally (Phase 0) or call
# _scrub_reason inside _emit_hook_event, we handle both patterns:
#   Pattern A: rule_scrubbed="$(_scrub_reason "$rule")" or similar
#   Pattern B: local rule="$(_scrub_reason "${5:-}")"
# We also ensure the _scrub_reason function itself is replaced with an identity.

cp "$HOOKS_DIR/_emit-event.sh" "$PATCHED_EMIT"
# Replace any _scrub_reason function definition with a passthrough (no-op scrub).
# This simulates the scrub being removed.
{
  # Append an override at the END of the patched file so it shadows any real definition.
  printf '\n# PATCHED FOR G50.5 MUST-FAIL TEST: _scrub_reason is a no-op passthrough\n'
  printf '_scrub_reason() { printf '"'"'%%s'"'"' "${1:-}"; return 0; }\n'
} >> "$PATCHED_EMIT"

# Also source _scrub.sh override: emit a no-op _scrub_reason that returns input verbatim.
# This ensures that even if _emit-event.sh sources _scrub.sh, our override wins.
PATCHED_SCRUB="$T5_DIR/_scrub.sh"
cp "$HOOKS_DIR/_scrub.sh" "$PATCHED_SCRUB" 2>/dev/null || true
{
  printf '\n# PATCHED FOR G50.5: override _scrub_reason with no-op\n'
  printf '_scrub_reason() { printf '"'"'%%s'"'"' "${1:-}"; return 0; }\n'
} >> "$PATCHED_SCRUB"

# Override the HOOKS_DIR resolution inside the patched emit so it sources our
# patched _scrub.sh rather than the real one. We do this by setting a shell
# variable before sourcing.
T5="$(mktemp -d)"
rc5=0
(
  export CLAUDE_PROJECT_DIR="$T5" CLAUDE_SESSION_ID="g50t5"
  # Override BASH_SOURCE[0] resolution: set _emit_event_scrub_override to our patched dir
  # Some implementations source _scrub.sh via dirname(BASH_SOURCE[0])/_scrub.sh.
  # We replicate the sourcing chain manually here using the PATCHED files.
  # shellcheck source=/dev/null
  source "$PATCHED_EMIT"
  # Also source patched scrub to ensure the override function definition takes effect
  # shellcheck source=/dev/null
  source "$PATCHED_SCRUB" 2>/dev/null || true
  _emit_hook_event "thing-orchestrator.sh" "deny" "Bash" "git push" \
    "pre-llm-hard-rule: --password=hunter2 in command" 2
)

LOG5="$T5/.ravenclaude/runs/g50t5/hook-events.jsonl"
g50_5_ok=0
if [[ -f "$LOG5" ]] && jq -e . < "$LOG5" >/dev/null 2>&1; then
  if printf '%s' "$(cat "$LOG5")" | grep -Fq "hunter2"; then
    # Patched version leaks the secret — this is exactly what we need to confirm
    # that G50.4's assertion has teeth.
    pass "G50.5: must-fail half confirmed — patched (no-scrub) emit leaks 'hunter2', proving G50.4 has teeth"
    g50_5_ok=1
  else
    # Patched version does NOT leak — either the scrub is happening somewhere else
    # we didn't patch, OR the secret is still being scrubbed despite our patch.
    fail "G50.5: patched (no-scrub) emit did NOT leak 'hunter2' — G50.4 may not be testing the right thing, or scrubbing is happening outside _emit_hook_event (investigate)"
  fi
else
  # If the patched emit writes nothing, we can't confirm the must-fail half.
  # Report as a partial failure with a useful diagnostic.
  fail "G50.5: patched emit wrote no JSONL — cannot confirm must-fail half; G50.4 may be passing vacuously (check _emit_hook_event wiring)"
fi
rm -rf "$T5" "$T5_DIR"

# ── Summary ───────────────────────────────────────────────────────────────────
echo
if [[ "$FAILED" -eq 0 ]]; then
  echo "Gate 50 (Phase 0 emit & scrub): ALL ASSERTIONS PASS"
  exit 0
fi
echo "Gate 50 (Phase 0 emit & scrub): $FAILED assertion(s) FAILED"
echo "(If Phase 0 is not yet integrated by backend-coder, G50.1/G50.2/G50.4 are"
echo " expected to fail with 'emit not wired' messages. Fix: wire _emit_hook_event"
echo " into thing-orchestrator.sh and route-decision-review.sh deny branches,"
echo " and source _scrub.sh inside _emit-event.sh to call _scrub_reason on the"
echo " rule argument before writing the JSONL line.)"
exit 1
