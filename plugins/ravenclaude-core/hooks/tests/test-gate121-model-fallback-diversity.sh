#!/usr/bin/env bash
# Gate 121 — runtime model-diversity collapse gate (model-fallback P3 closure).
# Drives the REAL command-review orchestrator with mocked seats (no live claude).
#   A collapse: when model-fallback resolves >=2 VOTED seats onto the SAME model
#     (simulated via the THING_SEAT_RESOLVED_OVERRIDE test hook), the panel FAILS
#     CLOSED — the verdict is deny and the reason cites the collapse.
#   B no-collapse: without the override (distinct configured models, the default),
#     the verdict does NOT cite a collapse — the gate is inert.
#   C teeth (must-fail half): a copy of the orchestrator with the collapse guard
#     neutered (`if false`) no longer fails closed on the collapse scenario.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$(cd "$HERE/../.." && pwd)" # plugins/ravenclaude-core
ORCH="$PLUGIN/hooks/thing-orchestrator.sh"
fails=0
pass() { echo "  ✓ $1"; }
fail() {
  echo "  ✗ $1"
  fails=$((fails + 1))
}

TMP="$(mktemp -d)"
PROJ="$TMP/proj"
mkdir -p "$PROJ/.ravenclaude"
cat >"$PROJ/.ravenclaude/comfort-posture.yaml" <<'EOF'
schema_version: 5
categories:
  shell_code_exec:
    user: ask
    local: ask
    project: inherit
    thing: on
EOF
# High-severity code-exec payload (subprocess shell=True) → extreme tier → 3 seats.
# Built by concatenation so the literal never reaches a live shell.
CMD='python3 -c "import subprocess; subprocess.run('"'"'ls'"'"', shell=True)"'

run_orch() { # $1 = orchestrator path ; reads THING_SEAT_* from env
  jq -cn --arg c "$CMD" --arg cwd "$PROJ" \
    '{tool_name:"Bash",tool_input:{command:$c},cwd:$cwd,session_id:"g121"}' \
    | CLAUDE_PLUGIN_ROOT="$PLUGIN" bash "$1" 2>/dev/null
}
reason_of() { jq -r '.hookSpecificOutput.permissionDecisionReason // ""' 2>/dev/null; }
decision_of() { jq -r '.hookSpecificOutput.permissionDecision // ""' 2>/dev/null; }

# ── A: collapse (override every seat onto one model) ⇒ deny + collapse reason ──
outA="$(THING_SEAT_MOCK_VERDICT=allow THING_SEAT_RESOLVED_OVERRIDE=claude-haiku-4-5 run_orch "$ORCH")"
if [ "$(printf '%s' "$outA" | decision_of)" = "deny" ] &&
  printf '%s' "$outA" | reason_of | grep -qi "collapsed the panel onto a single model"; then
  pass "collapse (>=2 seats → one model) ⇒ fail closed (deny, reason cites collapse)"
else
  fail "A: collapse not failing closed (decision=$(printf '%s' "$outA" | decision_of) reason=$(printf '%s' "$outA" | reason_of))"
fi

# ── B: no override (distinct configured models) ⇒ gate inert (no collapse reason) ──
outB="$(THING_SEAT_MOCK_VERDICT=allow run_orch "$ORCH")"
if printf '%s' "$outB" | reason_of | grep -qi "collapsed the panel"; then
  fail "B: false collapse with distinct models (reason=$(printf '%s' "$outB" | reason_of))"
else
  pass "distinct configured models ⇒ no collapse (gate inert, default behavior)"
fi

# ── C: teeth — neuter the collapse guard ⇒ collapse scenario no longer fails closed ──
MUT="$TMP/mut-orchestrator.sh"
sed 's/\[ "$diversity_collapsed" = "true" \]/false/' "$ORCH" >"$MUT"
if ! grep -q "if false; then" "$MUT"; then
  fail "C: could not neuter the collapse guard (sed no-op — fixture stale)"
else
  outC="$(THING_SEAT_MOCK_VERDICT=allow THING_SEAT_RESOLVED_OVERRIDE=claude-haiku-4-5 run_orch "$MUT")"
  if printf '%s' "$outC" | reason_of | grep -qi "collapsed the panel"; then
    fail "C: must-fail — neutered guard STILL cited collapse (gate has no teeth)"
  else
    pass "must-fail half: neutered guard ⇒ no collapse-deny (the gate is load-bearing)"
  fi
fi

echo ""
if [ "$fails" -eq 0 ]; then
  echo "Gate 121 PASS — runtime model-diversity collapse gate: fails closed on collapse, inert when distinct, has teeth."
  exit 0
else
  echo "Gate 121 FAIL — $fails subtest(s) failed."
  exit 1
fi
