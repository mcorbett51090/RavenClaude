#!/usr/bin/env bash
# Gate 286 — explore-tier-pin.sh (model-tier delegation, prevention leg).
# Bidirectional, on the real hook binary fed real PreToolUse(Agent) payloads:
#   A fires-on-bad: an un-pinned built-in Explore (under a comfort-posture
#     project) is rewritten — stdout is ONE hookSpecificOutput envelope whose
#     updatedInput carries model=haiku AND every original field, carries an
#     additionalContext explaining the pin, carries NO permissionDecision (the
#     posture's subagent_dispatch gate is untouched), and one hook-events.jsonl
#     warn line is written.
#   B silent-on-good: an Explore WITH an explicit model (opus) -> no stdout;
#     an explicit "inherit" -> no stdout; scout / general-purpose -> no stdout.
#   C opt-in: no comfort-posture -> no stdout.
#   D not-a-dispatch: a Bash payload -> no stdout.
#   E knobs: pin_explore: sonnet -> model=sonnet; pin_explore: off -> no stdout;
#     handoff_tax: off -> no stdout.
#   F env: CLAUDE_CODE_SUBAGENT_MODEL set -> no stdout (fleet route wins).
#   G teeth (must-fail half): the python module's own --self-test (contains a
#     must-fail canary), plus a mutant whose PIN_TYPES is emptied does NOT
#     rewrite the un-pinned Explore — proving A depends on the type match.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
HOOKS="$(cd "$HERE/.." && pwd)"
HOOK="$HOOKS/explore-tier-pin.sh"
PIN="$(cd "$HOOKS/../scripts" && pwd)/explore-tier-pin.py"
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

# payload <session> <subagent_type> [model] [tool_name]
payload() {
  if [ -n "${3:-}" ]; then
    jq -cn --arg sid "$1" --arg st "$2" --arg m "$3" --arg tn "${4:-Agent}" --arg cwd "$PROJ" \
      '{session_id:$sid, tool_name:$tn, cwd:$cwd, hook_event_name:"PreToolUse",
        tool_input:{prompt:"list every caller of foo under src/", description:"t", subagent_type:$st, model:$m}}'
  else
    jq -cn --arg sid "$1" --arg st "$2" --arg tn "${4:-Agent}" --arg cwd "$PROJ" \
      '{session_id:$sid, tool_name:$tn, cwd:$cwd, hook_event_name:"PreToolUse",
        tool_input:{prompt:"list every caller of foo under src/", description:"t", subagent_type:$st}}'
  fi
}

run_hook() { # $1=payload $2=project-dir -> stdout captured (env-clean)
  printf '%s' "$1" | env -u CLAUDE_CODE_SUBAGENT_MODEL CLAUDE_PROJECT_DIR="$2" "$HOOK" 2>/dev/null
}

# ── A: fires on bad (un-pinned Explore) ──────────────────────────────────────
out="$(run_hook "$(payload sA Explore)" "$PROJ")"
if [ "$(printf '%s' "$out" | grep -c '^{')" = "1" ]; then
  pass "A1: exactly one JSON object on stdout"
else
  fail "A1: expected exactly one JSON object, got: $(printf '%s' "$out" | head -c 200)"
fi
if printf '%s' "$out" | jq -e '.hookSpecificOutput.hookEventName == "PreToolUse"' >/dev/null 2>&1; then
  pass "A2: envelope is a PreToolUse hookSpecificOutput"
else
  fail "A2: not a PreToolUse envelope"
fi
[ "$(printf '%s' "$out" | jq -r '.hookSpecificOutput.updatedInput.model' 2>/dev/null)" = "haiku" ] \
  && pass "A3: updatedInput.model == haiku" || fail "A3: model not pinned to haiku"
[ "$(printf '%s' "$out" | jq -r '.hookSpecificOutput.updatedInput.prompt' 2>/dev/null)" = "list every caller of foo under src/" ] \
  && pass "A4: updatedInput preserves the original prompt (whole-object replacement rule)" || fail "A4: prompt lost in rewrite"
[ "$(printf '%s' "$out" | jq -r '.hookSpecificOutput.updatedInput.subagent_type' 2>/dev/null)" = "Explore" ] \
  && pass "A5: updatedInput preserves subagent_type" || fail "A5: subagent_type lost"
if printf '%s' "$out" | jq -e '.hookSpecificOutput | has("permissionDecision") | not' >/dev/null 2>&1; then
  pass "A6: no permissionDecision — the posture's subagent_dispatch gate is untouched"
else
  fail "A6: envelope carries a permissionDecision"
fi
printf '%s' "$out" | jq -r '.hookSpecificOutput.additionalContext' 2>/dev/null | grep -q "pin_explore" \
  && pass "A7: additionalContext names the knob" || fail "A7: additionalContext missing/knob not named"
ev="$(cat "$PROJ"/.ravenclaude/runs/*/hook-events.jsonl 2>/dev/null | grep -c '"hook":"explore-tier-pin.sh".*"verdict":"warn".*pinned:haiku' || true)"
[ "${ev:-0}" -ge 1 ] && pass "A8: one hook-events.jsonl warn line (rule pinned:haiku)" || fail "A8: hook-event line missing"

# plugin-scoped Explore name is still Explore
out="$(run_hook "$(payload sA2 'some-plugin:Explore')" "$PROJ")"
[ "$(printf '%s' "$out" | jq -r '.hookSpecificOutput.updatedInput.model' 2>/dev/null)" = "haiku" ] \
  && pass "A9: plugin-scoped Explore is matched on its basename" || fail "A9: scoped Explore not pinned"

# ── B: silent on good ────────────────────────────────────────────────────────
[ -z "$(run_hook "$(payload sB Explore opus)" "$PROJ")" ] && pass "B1: explicit model=opus -> silent (explicit choice honoured)" || fail "B1: rewrote an explicit model"
[ -z "$(run_hook "$(payload sB Explore inherit)" "$PROJ")" ] && pass "B2: explicit model=inherit -> silent" || fail "B2: rewrote an explicit inherit"
[ -z "$(run_hook "$(payload sB scout)" "$PROJ")" ] && pass "B3: scout -> silent (pins haiku in frontmatter)" || fail "B3: touched scout"
[ -z "$(run_hook "$(payload sB general-purpose)" "$PROJ")" ] && pass "B4: general-purpose -> silent (does real work)" || fail "B4: touched general-purpose"

# ── C: opt-in ────────────────────────────────────────────────────────────────
NOPOST="$TMP/nopost"; mkdir -p "$NOPOST"
p="$(payload sC Explore | jq -c --arg cwd "$NOPOST" '.cwd=$cwd')"
[ -z "$(run_hook "$p" "$NOPOST")" ] && pass "C1: no comfort-posture -> silent (opt-in)" || fail "C1: fired without a posture"

# ── D: not a dispatch ────────────────────────────────────────────────────────
[ -z "$(run_hook "$(payload sD Explore '' Bash)" "$PROJ")" ] && pass "D1: Bash payload -> silent" || fail "D1: fired on a non-dispatch tool"

# ── E: knobs ─────────────────────────────────────────────────────────────────
KNOB="$TMP/knob"; mkdir -p "$KNOB/.ravenclaude"
printf 'schema_version: 5\nhandoff_tax:\n  pin_explore: sonnet\n' >"$KNOB/.ravenclaude/comfort-posture.yaml"
p="$(payload sE Explore | jq -c --arg cwd "$KNOB" '.cwd=$cwd')"
[ "$(run_hook "$p" "$KNOB" | jq -r '.hookSpecificOutput.updatedInput.model' 2>/dev/null)" = "sonnet" ] \
  && pass "E1: pin_explore: sonnet -> model=sonnet" || fail "E1: sonnet knob not honoured"
printf 'schema_version: 5\nhandoff_tax:\n  pin_explore: off\n' >"$KNOB/.ravenclaude/comfort-posture.yaml"
[ -z "$(run_hook "$p" "$KNOB")" ] && pass "E2: pin_explore: off -> silent" || fail "E2: pinned despite pin_explore: off"
printf 'schema_version: 5\nhandoff_tax: off\n' >"$KNOB/.ravenclaude/comfort-posture.yaml"
[ -z "$(run_hook "$p" "$KNOB")" ] && pass "E3: handoff_tax: off -> silent" || fail "E3: pinned despite handoff_tax: off"

# ── F: fleet-wide env route wins ─────────────────────────────────────────────
out="$(printf '%s' "$(payload sF Explore)" | CLAUDE_CODE_SUBAGENT_MODEL=haiku CLAUDE_PROJECT_DIR="$PROJ" "$HOOK" 2>/dev/null)"
[ -z "$out" ] && pass "F1: CLAUDE_CODE_SUBAGENT_MODEL set -> silent (would override the fleet route)" || fail "F1: pinned over the env route"

# ── G: teeth ─────────────────────────────────────────────────────────────────
if python3 "$PIN" --self-test >/dev/null 2>&1; then
  pass "G1: module self-test passes (contains the must-fail canary)"
else
  fail "G1: module self-test failed"
fi
MUT="$TMP/mut"; mkdir -p "$MUT/scripts" "$MUT/hooks"
sed 's/^PIN_TYPES = frozenset({"explore"})/PIN_TYPES = frozenset()/' "$PIN" >"$MUT/scripts/explore-tier-pin.py"
grep -q 'PIN_TYPES = frozenset()' "$MUT/scripts/explore-tier-pin.py" || fail "G2-setup: mutant not applied"
cp "$HOOK" "$MUT/hooks/explore-tier-pin.sh"; cp "$HOOKS/_emit-event.sh" "$MUT/hooks/" 2>/dev/null || true
chmod +x "$MUT/hooks/explore-tier-pin.sh"
out="$(printf '%s' "$(payload sG Explore)" | env -u CLAUDE_CODE_SUBAGENT_MODEL CLAUDE_PROJECT_DIR="$PROJ" "$MUT/hooks/explore-tier-pin.sh" 2>/dev/null)"
[ -z "$out" ] && pass "G2: type-match mutant does NOT rewrite -> assertion A depends on the Explore match" || fail "G2: mutant still rewrote (A is not load-bearing)"

echo
if [ "$fails" -eq 0 ]; then
  echo "Gate 286 (explore-tier-pin): PASS"
  exit 0
fi
echo "Gate 286 (explore-tier-pin): FAIL ($fails)"
exit 1
