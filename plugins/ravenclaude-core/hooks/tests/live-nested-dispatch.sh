#!/usr/bin/env bash
# live-nested-dispatch.sh — OPT-IN live test of nested subagent dispatch against a
# REAL Claude Code runtime. Not wired into audit-gates.sh (it spends the signed-in
# account's usage — ~US$0.10–0.15 per run on 2026-09-14 — and needs a login), so it
# only runs when you say so:
#
#   RC_LIVE=1 bash plugins/ravenclaude-core/hooks/tests/live-nested-dispatch.sh [N]
#
# N = number of coordinator layers between the main thread and the read-only leaf
# (default 1: main -> coord1 -> leaf; 2 gives three subagent layers, the platform
# default ceiling; 3 shows the ceiling biting). Without RC_LIVE=1, or without a
# `claude` binary that reports loggedIn, it prints SKIP and exits 0 — a skip is
# NOT a pass, and it says so.
#
# What it builds (in a fresh mktemp dir, never deleted by this script):
#   coordN  — tools: Agent, Read  (the grant Gate 289 forbids in SHIPPED agents;
#             here it is the deliberate fixture)          model: sonnet
#   leaf    — tools: Read, Glob, Grep                      model: haiku
# and wires the real handoff-tax-meter hook on PostToolUse(Agent). If the
# platform nests, the meter's ledger shows nested=true lines whose
# caller_agent_id is the caller's real agentId, and --summary resolves the depth.
#
# Live facts established with this script on 2.1.271 (2026-09-14), recorded in
# docs/decisions/2026-09-14-nested-dispatch-determination.md § 7:
#   * N=1 and N=2 nest; N=3 does not — the 3rd subagent layer has NO Agent tool
#     in its toolset even though its definition lists it (ceiling = tool removal,
#     not an error on the call).
#   * Hooks fire child-first, so ledger lines land leaf, coord2, coord1.
#   * One dispatch from inside a subagent returned `async_launched` with
#     run_in_background unset; its report never reaches PostToolUse.
set -uo pipefail

N="${1:-1}"
HERE="$(cd "$(dirname "$0")" && pwd)"
HOOK="$(cd "$HERE/.." && pwd)/handoff-tax-meter.sh"
METER="$(cd "$HERE/../../scripts" && pwd)/handoff-tax-meter.py"

skip() { echo "live-nested-dispatch: SKIP — $1"; echo "  (a skip is NOT a pass: nothing about the platform was observed)"; exit 0; }
[[ "${RC_LIVE:-}" == "1" ]] || skip "set RC_LIVE=1 to run (spends the signed-in account's usage)"
command -v claude >/dev/null 2>&1 || skip "no \`claude\` on PATH (use the native installer from claude.ai; npm -g needs a writable prefix)"
command -v jq >/dev/null 2>&1 || skip "jq required"
if ! claude auth status 2>/dev/null | jq -e '.loggedIn == true' >/dev/null 2>&1; then
  skip "claude is not signed in (\`claude auth login\`, or set CLAUDE_CODE_OAUTH_TOKEN / ANTHROPIC_API_KEY)"
fi

OUT="$(mktemp -d "${TMPDIR:-/tmp}/rc-live-nested-$N-XXXX")"; P="$OUT/proj"
mkdir -p "$P/.claude/agents" "$P/.ravenclaude" "$P/src"
printf 'schema_version: 5\n' >"$P/.ravenclaude/comfort-posture.yaml"
printf 'def target_marker_zebra():\n    return 2\n' >"$P/src/b.py"
i=1
while [[ $i -le $N ]]; do
  if [[ $i -eq $N ]]; then next=leaf; else next="coord$((i+1))"; fi
  cat >"$P/.claude/agents/coord$i.md" <<AG
---
name: coord$i
description: Coordinator layer $i of the nested-dispatch live test. Delegates everything to $next.
tools: Agent, Read
model: sonnet
---
You are coordinator layer $i. You MUST NOT search files yourself and MUST NOT answer from
memory. Dispatch the \`$next\` subagent with a one-line brief, then relay its answer
verbatim prefixed with "L$i> ". If the dispatch tool is unavailable or refused, reply
exactly: "L$i> DISPATCH REFUSED: <the error text>".
AG
  i=$((i+1))
done
cat >"$P/.claude/agents/leaf.md" <<'AG'
---
name: leaf
description: Read-only search fixture for the nested-dispatch live test.
tools: Read, Glob, Grep
model: haiku
---
Answer the brief with a single line: "LEAF: <path>:<line>" where the requested symbol is defined.
AG
jq -n --arg h "$HOOK" '{hooks:{PostToolUse:[{matcher:"Agent",hooks:[{type:"command",command:$h}]}]}}' >"$P/.claude/settings.json"

chain="main"; i=1; while [[ $i -le $N ]]; do chain="$chain -> coord$i"; i=$((i+1)); done; chain="$chain -> leaf"
echo "== runtime : $(claude --version 2>/dev/null)"
echo "== project : $P"
echo "== chain   : $chain   ($((N+1)) subagent layers)"
cd "$P" || exit 1
claude -p "Dispatch the coord1 agent to tell me where target_marker_zebra is defined. Report exactly what it returns, verbatim." \
  --allowedTools "Agent,Read,Glob,Grep" --output-format json --max-turns 12 >"$OUT/result.json" 2>"$OUT/stderr.log"
echo "== claude exit $?"
jq -r '"   result  : \(.result | tostring | .[0:400])\n   cost_usd: \(.total_cost_usd)"' "$OUT/result.json" 2>/dev/null \
  || { echo "   (no JSON result)"; head -20 "$OUT/stderr.log"; }

echo "== ledger lines, in write order (caller chain reconstructed by --summary):"
found=0
for L in "$P"/.ravenclaude/runs/*/dispatch-ledger.jsonl; do
  [[ -f "$L" ]] || continue; found=1
  jq -c '{subagent_type, tier, status, nested, depth_at_write: .depth, floor: .depth_is_lower_bound, caller_agent_type, caller_agent_id}' "$L" | sed 's/^/   /'
  S="$(basename "$(dirname "$L")")"
  echo "== summary:"
  CLAUDE_PROJECT_DIR="$P" python3 "$METER" --summary --session "$S" 2>/dev/null | grep -E "tier mix|handoff|flags|nesting" | sed 's/^/ /'
done
[[ $found == 0 ]] && echo "   (none — the hook never fired; see $OUT/stderr.log)"

echo "== verdict:"
if [[ $found == 1 ]] && cat "$P"/.ravenclaude/runs/*/dispatch-ledger.jsonl | jq -e 'select(.nested == true and .subagent_type == "leaf")' >/dev/null 2>&1; then
  echo "   NESTED DISPATCH OBSERVED LIVE: leaf was spawned by a coordinator subagent (see caller_agent_id); meter recorded nested=true."
elif [[ $found == 1 ]]; then
  echo "   Leaf was NOT reached. Deepest line above is where the chain stopped — with N>=3 that is the default depth ceiling (CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH); read result.json for the refusal text."
else
  echo "   Nothing observed."
fi
echo "   artifacts: $OUT"
