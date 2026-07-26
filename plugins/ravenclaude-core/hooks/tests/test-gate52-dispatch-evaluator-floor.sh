#!/usr/bin/env bash
# test-gate52-dispatch-evaluator-floor.sh
# Gate 52 — proves the agent-dispatch-evaluator Phase-2 workflow integration keeps the
# HARD INVARIANT: with dispatch-config absent/disabled (the default), every
# evaluatedAgent() dispatch is byte-identical to the unwrapped baseline.
#
# Three assertions:
#   (A) GOOD fixture — a faithful wrapper block whose disabled path is
#       `return agent(prompt, opts);` → check-dispatch-evaluator-floor.mjs PASSES (exit 0).
#   (B) BAD fixture  — a wrapper whose disabled path clones+mutates opts.model →
#       the checker FAILS (exit nonzero). This is the must-fail half: it proves the
#       gate's must-PASS assertions have teeth (they reject a broken floor).
#   (C) REAL workflow — .claude/workflows/rc-deep-research.js must carry the copied
#       wrapper fence AND satisfy the disabled-floor invariant. This is the live
#       regression floor the Phase-2 integration commits to.
#
# CI-safe: pure node, no network, no `claude` call. Fixtures are written to a tmp dir.

set -uo pipefail

ROOT="$(git rev-parse --show-toplevel)"
CHECKER="$ROOT/scripts/check-dispatch-evaluator-floor.mjs"
WORKFLOW="$ROOT/.claude/workflows/rc-deep-research.js"

PASS=0
FAIL=0
note() { printf '  %s %s\n' "$1" "$2"; }
ok() { PASS=$((PASS + 1)); note "✓" "$1"; }
bad() {
  FAIL=$((FAIL + 1))
  note "✗" "$1"
}

command -v node >/dev/null 2>&1 || {
  echo "── Gate 52: SKIP (node not on PATH) ──"
  echo "  THIS IS NOT A PASS — node is required to run check-dispatch-evaluator-floor.mjs"
  exit 1
}
[ -f "$CHECKER" ] || {
  echo "FATAL: checker not found at $CHECKER"
  exit 2
}

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# ── GOOD fixture: faithful disabled-floor wrapper ────────────────────────────
cat >"$TMP/good.js" <<'GOOD'
// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║ BEGIN copied block — agent-dispatch-evaluator wrapper (Phase 2)            ║
// ╚═══════════════════════════════════════════════════════════════════════════╝
const DISPATCH_TIER_MODEL = { fast: "claude-haiku-4-5-20251001", balanced: "claude-sonnet-5", top: "claude-opus-4-8" };
const _latency = { window: [], tripped: false };
async function evaluatedAgent(prompt, opts = {}, dispatchCfg) {
  if (!dispatchCfg) return agent(prompt, opts);
  if (!dispatchCfg.enabled) return agent(prompt, opts);
  if (_latency.tripped) return agent(prompt, opts);
  if (opts._predispatch === "skip") return agent(prompt, opts);
  const appliedOpts = { ...opts };
  appliedOpts.model = DISPATCH_TIER_MODEL.balanced;
  return agent(prompt, appliedOpts);
}
// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║ END copied block — agent-dispatch-evaluator wrapper (Phase 2)              ║
// ╚═══════════════════════════════════════════════════════════════════════════╝
GOOD

# ── BAD fixture: disabled path clones + rewrites opts.model (broken floor) ────
cat >"$TMP/bad.js" <<'BAD'
// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║ BEGIN copied block — agent-dispatch-evaluator wrapper (Phase 2)            ║
// ╚═══════════════════════════════════════════════════════════════════════════╝
async function evaluatedAgent(prompt, opts = {}, dispatchCfg) {
  if (!dispatchCfg) return agent(prompt, { ...opts, model: "claude-haiku-4-5-20251001" });
  if (!dispatchCfg.enabled) return agent(prompt, { ...opts, model: "claude-haiku-4-5-20251001" });
  return agent(prompt, opts);
}
// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║ END copied block — agent-dispatch-evaluator wrapper (Phase 2)              ║
// ╚═══════════════════════════════════════════════════════════════════════════╝
BAD

echo "── Gate 52: agent-dispatch-evaluator disabled-floor ───────────────────────"

# (A) good fixture → exit 0
rc=0
node "$CHECKER" "$TMP/good.js" >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 0 ]; then ok "GOOD fixture: faithful disabled floor passes"; else bad "GOOD fixture should pass (rc=$rc)"; fi

# (B) bad fixture → nonzero (must-fail half — the gate has teeth)
rc=0
node "$CHECKER" "$TMP/bad.js" >/dev/null 2>&1 || rc=$?
if [ "$rc" -ne 0 ]; then ok "BAD fixture: cloned/mutated disabled floor is caught (teeth)"; else bad "BAD fixture should FAIL but the checker passed it (no teeth)"; fi

# (C) real workflow → must carry the wrapper fence AND satisfy the floor
if grep -q "BEGIN copied block — agent-dispatch-evaluator wrapper" "$WORKFLOW" 2>/dev/null; then
  rc=0
  node "$CHECKER" "$WORKFLOW" >/dev/null 2>&1 || rc=$?
  if [ "$rc" -eq 0 ]; then ok "REAL workflow rc-deep-research.js: disabled floor is byte-identical"; else bad "REAL workflow violates the disabled floor (rc=$rc)"; fi
else
  bad "REAL workflow rc-deep-research.js is MISSING the copied wrapper block (Phase-2 integration not applied)"
fi

echo "  ── Gate 52 result: $PASS passed, $FAIL failed ──"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
