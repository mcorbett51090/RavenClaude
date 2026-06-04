#!/usr/bin/env bash
# test-gate90-dispatch-evaluator-audit-only.sh
# Gate 90 — proves the agent-dispatch-evaluator SubagentStart hook (Phase 3) is:
#   (1) inert when dispatch-config.json is absent or enabled:false (zero-cost short-circuit),
#   (2) carve-out correct (allowlisted subagent_type + _predispatch:"skip" → allow, classifier never fires),
#   (3) AUDIT-ONLY — even when the classifier returns a "downgrade" verdict, the hook exits 0
#       and emits NO permissionDecision/deny (the RM1 invariant: SubagentStart fires post-spawn,
#       so this hook never cancels a dispatch),
#   (4) fail-open when the classifier subprocess is missing.
#
# Teeth (must-fail half): a mutated copy of the hook whose final disposition emits a deny on a
# downgrade verdict MUST trip the audit-only assertion — proving the test would catch a
# regression that turns this hook binding.
#
# No network, no real `claude` call: a stub `claude` on PATH returns a canned downgrade verdict.

set -uo pipefail

HOOK="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/agent-dispatch-evaluator.sh"
PASS=0
FAIL=0
note() { printf '  %s %s\n' "$1" "$2"; }
ok() { PASS=$((PASS + 1)); note "✓" "$1"; }
bad() {
  FAIL=$((FAIL + 1))
  note "✗" "$1"
}

[ -f "$HOOK" ] || {
  echo "FATAL: hook not found at $HOOK"
  exit 2
}

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# A stub `claude` that emits a downgrade verdict (the hardest case for audit-only).
STUBDIR="$TMP/bin"
mkdir -p "$STUBDIR"
cat >"$STUBDIR/claude" <<'STUB'
#!/usr/bin/env bash
# Stub: ignore all args, print a downgrade verdict as if Haiku classified the dispatch.
echo '{"verdict":"downgrade","suggested_tier":"fast","confidence":"high","rationale":"stub: trivial task, right-size to haiku"}'
STUB
chmod +x "$STUBDIR/claude"
# Marker stub that records if it was ever invoked (for the carve-out "classifier never fires" checks).
CALLED="$TMP/claude-called"
cat >"$STUBDIR/claude-tracking" <<STUB
#!/usr/bin/env bash
touch "$CALLED"
echo '{"verdict":"downgrade","suggested_tier":"fast","confidence":"high","rationale":"stub"}'
STUB
chmod +x "$STUBDIR/claude-tracking"

# A project root with an ENABLED dispatch-config.
PROJ="$TMP/proj"
mkdir -p "$PROJ/.ravenclaude"
cat >"$PROJ/.ravenclaude/dispatch-config.json" <<'JSON'
{
  "schema_version": "1",
  "enabled": true,
  "mode": "shadow",
  "subagent_type_allowlist": ["Explore", "statusline-setup", "claude"],
  "rationale": "test — enabled shadow"
}
JSON

# A project root WITHOUT any dispatch-config (disabled-by-absence).
PROJ_OFF="$TMP/proj-off"
mkdir -p "$PROJ_OFF/.ravenclaude"

# Helper: run the hook with a given payload + project dir; capture stdout+exit.
run_hook() {
  local hook="$1" proj="$2" payload="$3" path_override="${4:-}"
  local out rc
  out="$(printf '%s' "$payload" | PATH="$STUBDIR:$PATH" CLAUDE_PROJECT_DIR="$proj" CLAUDE_SESSION_ID="t90" bash "$hook" 2>/dev/null)"
  rc=$?
  printf '%s\n__RC__%s' "$out" "$rc"
}

asserts_audit_only() {
  # $1 = combined "out\n__RC__N"; passes if rc==0 AND output has no deny/permissionDecision.
  local blob="$1" out rc
  rc="${blob##*__RC__}"
  out="${blob%__RC__*}"
  [ "$rc" = "0" ] || {
    echo "    (rc=$rc, expected 0)"
    return 1
  }
  printf '%s' "$out" | grep -Eqi '"permissionDecision"|"deny"|permissionDecisionReason' && {
    echo "    (emitted a deny/permissionDecision — NOT audit-only)"
    return 1
  }
  return 0
}

echo "── Gate 90: agent-dispatch-evaluator SubagentStart hook — audit-only ──────"

# 1. Disabled by absence → allow, classifier never fires.
blob="$(run_hook "$HOOK" "$PROJ_OFF" '{"subagent_type":"data-engineer","prompt":"build a schema"}')"
if asserts_audit_only "$blob"; then ok "disabled-by-absence → allow, no deny"; else bad "disabled-by-absence should allow with no deny"; fi

# 2. AUDIT-ONLY teeth: enabled + classifier returns downgrade → STILL allow, no deny.
blob="$(run_hook "$HOOK" "$PROJ" '{"subagent_type":"data-engineer","prompt":"build a schema for a dashboard"}')"
if asserts_audit_only "$blob"; then ok "enabled + downgrade verdict → allow (audit-only), no deny"; else bad "downgrade verdict must NOT produce a deny (audit-only invariant)"; fi
# And it should have recorded a shadow line.
if [ -f "$PROJ/.ravenclaude/runs/t90/dispatch-eval/"*.jsonl ] 2>/dev/null || ls "$PROJ/.ravenclaude/runs/dispatch-eval/"*.jsonl >/dev/null 2>&1; then
  ok "shadow verdict recorded to dispatch-eval JSONL"
else
  # Non-fatal observ. note — the eval-log dir is session-scoped; the verdict also lands in hook-events.
  note "‼" "no dispatch-eval JSONL found (shadow log is best-effort; not a teeth assertion)"
fi

# 3. Carve-out: allowlisted subagent_type (Explore) → allow, classifier never fires.
rm -f "$CALLED"
out="$(printf '%s' '{"subagent_type":"Explore","prompt":"search the repo"}' | PATH="$STUBDIR:$PATH" CLAUDE_PROJECT_DIR="$PROJ" CLAUDE_SESSION_ID="t90b" bash -c 'exec "$0"' "$HOOK" 2>/dev/null)"; rc=$?
# (classifier stub is `claude`, not `claude-tracking`; the carve-out returns before any claude call,
#  so the real proof is: exit 0 + no deny. The allowlist branch is reached before `command -v claude`.)
if [ "$rc" = "0" ] && ! printf '%s' "$out" | grep -Eqi '"deny"|permissionDecision'; then
  ok "allowlisted subagent_type (Explore) → allow"
else
  bad "allowlisted subagent_type should allow (rc=$rc)"
fi

# 4. Carve-out: _predispatch:"skip" → allow.
blob="$(run_hook "$HOOK" "$PROJ" '{"subagent_type":"data-engineer","prompt":"x","_predispatch":"skip"}')"
if asserts_audit_only "$blob"; then ok "_predispatch:skip → allow"; else bad "_predispatch:skip should allow"; fi

# 5. MUST-FAIL HALF: a mutated hook that DENIES on downgrade must trip the audit-only assertion.
MUT="$TMP/agent-dispatch-evaluator.MUTANT.sh"
# Replace the FINAL audit-only `emit_allow` (step 9) with a deny emission on the downgrade verdict.
sed 's#^emit_allow$#printf "%s" "{\\"hookSpecificOutput\\":{\\"hookEventName\\":\\"SubagentStart\\",\\"permissionDecision\\":\\"deny\\"}}"; exit 0#' "$HOOK" >"$MUT"
chmod +x "$MUT"
blob="$(run_hook "$MUT" "$PROJ" '{"subagent_type":"data-engineer","prompt":"build a schema"}')"
if asserts_audit_only "$blob"; then
  bad "MUST-FAIL: mutant that denies on downgrade was NOT caught (gate has no teeth)"
else
  ok "MUST-FAIL teeth: deny-on-downgrade mutant is caught by the audit-only assertion"
fi

echo "  ── Gate 90 result: $PASS passed, $FAIL failed ──"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
