#!/usr/bin/env bash
# Gate 285 — handoff-tax-meter.sh (model-tier delegation, measurement leg).
# Bidirectional, on the real hook binary fed real PostToolUse(Agent) payloads:
#   A fires-on-bad: an over-cap report from an Explore dispatch that resolved to an
#     opus-class model (under a comfort-posture project) emits the advisory as a
#     hookSpecificOutput.additionalContext envelope carrying BOTH flags
#     (report_over_cap + frontier_readonly), writes one dispatch-ledger line with
#     tier=frontier, and writes one hook-events.jsonl warn line.
#   B silent-on-good: a within-cap haiku scout dispatch emits nothing on stdout,
#     but STILL writes its ledger line (the ledger is the "cost per completed task"
#     denominator — it must record the good dispatches, not just the bad ones).
#   C opt-in: no comfort-posture -> no stdout, no ledger.
#   D not-a-dispatch: a Bash payload -> no stdout, no ledger.
#   E knob: `handoff_tax: off` -> advisory suppressed, ledger still written.
#   F privacy: the ledger never carries the prompt or the report TEXT.
#   G teeth (must-fail half): the python module's own --self-test, which contains
#     a must-fail canary (an over-cap report that MUST flag); plus a mutant of the
#     module with the report cap disabled does NOT flag the over-cap report —
#     proving assertion A depends on the cap, not on incidental output.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
HOOKS="$(cd "$HERE/.." && pwd)"
HOOK="$HOOKS/handoff-tax-meter.sh"
METER="$(cd "$HOOKS/../scripts" && pwd)/handoff-tax-meter.py"
fails=0
pass() { echo "  ✓ $1"; }
fail() {
  echo "  ✗ $1"
  fails=$((fails + 1))
}

command -v python3 >/dev/null 2>&1 || { echo "  ✗ python3 required"; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "  ✗ jq required"; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
PROJ="$TMP/proj"
mkdir -p "$PROJ/.ravenclaude"
printf 'schema_version: 5\n' >"$PROJ/.ravenclaude/comfort-posture.yaml"

LONG="$(python3 -c 'print(" ".join(["lorem"]*450))')"
SHORT="$(python3 -c 'print(" ".join(["ipsum"]*40))')"

# payload <session> <subagent_type> <resolvedModel> <report_text> [tool_name]
payload() {
  jq -cn --arg sid "$1" --arg st "$2" --arg rm "$3" --arg rep "$4" --arg tn "${5:-Agent}" --arg cwd "$PROJ" \
    '{session_id:$sid, tool_name:$tn, cwd:$cwd,
      tool_input:{prompt:"list every caller of foo under src/ as path:line", description:"t", subagent_type:$st},
      tool_response:{status:"completed", agentId:"a1", resolvedModel:$rm,
                     content:[{type:"text", text:$rep}], totalTokens:321, totalToolUseCount:2, totalDurationMs:50}}'
}

run_hook() { # $1=payload $2=project-dir -> stdout captured
  printf '%s' "$1" | CLAUDE_PROJECT_DIR="$2" "$HOOK" 2>/dev/null
}

# ── A: fires on bad (over-cap report + Explore on opus) ──────────────────────
out="$(run_hook "$(payload sA Explore claude-opus-4-8 "$LONG")" "$PROJ")"
if printf '%s' "$out" | jq -e '.hookSpecificOutput.additionalContext' >/dev/null 2>&1; then
  ctx="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.additionalContext')"
  printf '%s' "$ctx" | grep -q "report_over_cap" && pass "A1: over-cap report -> additionalContext carries report_over_cap" \
    || fail "A1: advisory missing report_over_cap"
  printf '%s' "$ctx" | grep -q "frontier_readonly" && pass "A2: Explore on opus -> additionalContext carries frontier_readonly" \
    || fail "A2: advisory missing frontier_readonly"
  printf '%s' "$ctx" | grep -q "RavenClaude guard notice" && pass "A3: advisory is self-identifying (banner present)" \
    || fail "A3: banner missing"
  printf '%s' "$ctx" | grep -q "450 words" && pass "A4: advisory reports the measured word count" \
    || fail "A4: word count not reported"
else
  fail "A1-A4: no additionalContext envelope on stdout (got: $(printf '%s' "$out" | head -c 200))"
fi
LEDGER="$PROJ/.ravenclaude/runs/sA/dispatch-ledger.jsonl"
if [[ -f "$LEDGER" ]] && [[ "$(wc -l <"$LEDGER" | tr -d ' ')" == "1" ]]; then
  pass "A5: exactly one dispatch-ledger line written"
  tier="$(jq -r '.tier' "$LEDGER")"; rw="$(jq -r '.report_words' "$LEDGER")"
  [[ "$tier" == "frontier" && "$rw" == "450" ]] && pass "A6: ledger records tier=frontier, report_words=450" \
    || fail "A6: ledger tier/report_words wrong (tier=$tier report_words=$rw)"
  jq -e '.flags | index("report_over_cap") and index("frontier_readonly")' "$LEDGER" >/dev/null 2>&1 \
    && pass "A7: ledger flags carry both trips" || fail "A7: ledger flags incomplete"
else
  fail "A5-A7: dispatch ledger missing or wrong line count"
fi
EVENTS="$PROJ/.ravenclaude/runs/sA/hook-events.jsonl"
if [[ -f "$EVENTS" ]] && jq -e 'select(.hook=="handoff-tax-meter.sh" and .verdict=="warn")' "$EVENTS" >/dev/null 2>&1; then
  pass "A8: hook-events.jsonl carries a warn line from handoff-tax-meter.sh"
else
  fail "A8: no warn hook-event written"
fi

# ── B: silent on good, ledger still written ──────────────────────────────────
out="$(run_hook "$(payload sB scout claude-haiku-4-5-20251001 "$SHORT")" "$PROJ")"
[[ -z "$out" ]] && pass "B1: within-cap haiku scout -> no stdout" || fail "B1: good dispatch produced output: $(printf '%s' "$out" | head -c 120)"
LB="$PROJ/.ravenclaude/runs/sB/dispatch-ledger.jsonl"
if [[ -f "$LB" ]] && [[ "$(jq -r '.tier' "$LB")" == "fast" ]] && [[ "$(jq -r '.flags|length' "$LB")" == "0" ]]; then
  pass "B2: good dispatch still recorded (tier=fast, no flags) — the denominator is kept"
else
  fail "B2: good dispatch not recorded in the ledger"
fi

# ── C: opt-in — no posture -> nothing ────────────────────────────────────────
NOP="$TMP/noposture"; mkdir -p "$NOP"
pl="$(payload sC Explore claude-opus-4-8 "$LONG" | jq -c --arg cwd "$NOP" '.cwd=$cwd')"
out="$(printf '%s' "$pl" | CLAUDE_PROJECT_DIR="$NOP" "$HOOK" 2>/dev/null)"
[[ -z "$out" && ! -e "$NOP/.ravenclaude/runs/sC/dispatch-ledger.jsonl" ]] \
  && pass "C: no comfort-posture -> no output, no ledger (opt-in)" || fail "C: fired without a posture file"

# ── D: not a dispatch tool -> nothing ────────────────────────────────────────
out="$(run_hook "$(payload sD Explore claude-opus-4-8 "$LONG" Bash)" "$PROJ")"
[[ -z "$out" && ! -e "$PROJ/.ravenclaude/runs/sD/dispatch-ledger.jsonl" ]] \
  && pass "D: Bash payload -> no output, no ledger" || fail "D: fired on a non-Agent tool"

# ── E: knob off -> advisory suppressed, ledger kept ──────────────────────────
printf 'schema_version: 5\nhandoff_tax: off\n' >"$PROJ/.ravenclaude/comfort-posture.yaml"
out="$(run_hook "$(payload sE Explore claude-opus-4-8 "$LONG")" "$PROJ")"
LE="$PROJ/.ravenclaude/runs/sE/dispatch-ledger.jsonl"
if [[ -z "$out" ]] && [[ -f "$LE" ]] && jq -e '.flags | index("report_over_cap")' "$LE" >/dev/null 2>&1; then
  pass "E: handoff_tax: off -> advisory suppressed, ledger line (with flags) still written"
else
  fail "E: knob off misbehaved (out=$(printf '%s' "$out" | head -c 80), ledger=$([[ -f "$LE" ]] && echo yes || echo no))"
fi
printf 'schema_version: 5\n' >"$PROJ/.ravenclaude/comfort-posture.yaml"

# ── F: privacy — the ledger never carries the text ───────────────────────────
if ! grep -q "lorem" "$LEDGER" && ! grep -q "list every caller" "$LEDGER"; then
  pass "F: ledger carries counts and ids only — no report or prompt text"
else
  fail "F: ledger leaked prompt/report text"
fi

# ── G: teeth ─────────────────────────────────────────────────────────────────
if python3 "$METER" --self-test >/dev/null 2>&1; then
  pass "G1: handoff-tax-meter.py --self-test passes (contains its own must-fail canary)"
else
  fail "G1: python self-test failed"
fi
MUT="$TMP/mut-handoff-tax-meter.py"
sed -e 's/if report_words is not None and report_words > posture\["report_cap"\]:/if False:/' "$METER" >"$MUT"
if ! grep -q 'if False:' "$MUT"; then
  fail "G2: could not neuter the report cap (sed no-op — fixture stale)"
else
  sig="$(printf '%s' "$(payload sG Explore claude-sonnet-5 "$LONG")" | python3 "$MUT" --project-root "$PROJ" 2>/dev/null | head -n 1)"
  [[ "$sig" == "OK" ]] \
    && pass "G2: must-fail half — with the report cap neutered the over-cap report is NOT flagged (A depends on the cap)" \
    || fail "G2: mutant still flagged (got: $sig) — assertion A is not load-bearing"
fi

echo
if [[ $fails -eq 0 ]]; then echo "Gate 285 handoff-tax-meter: PASS"; exit 0; fi
echo "Gate 285 handoff-tax-meter: FAIL ($fails)"; exit 1
