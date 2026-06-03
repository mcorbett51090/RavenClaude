#!/usr/bin/env bash
# route-decision-review.sh
# PreToolUse(AskUserQuestion) hook — ENFORCES the decision-review tribunal so
# rule/fact-derivable yes/no questions are auto-resolved instead of interrupting
# the human. This is the enforcement surface for the `decision-review` skill +
# thing-decide.py (previously behavioral / skill-invoked only).
#
# Contract (Claude Code PreToolUse):
#   - stdin: {tool_name, tool_input, cwd, session_id, ...}
#   - on exit 0 we emit hookSpecificOutput.permissionDecision (allow | deny | ask)
#   - deny feeds permissionDecisionReason back to the agent; here a deny carries
#     the tribunal's binding verdict so the agent proceeds WITHOUT re-asking.
#
# Safety envelope (deliberately conservative — fail toward asking the human):
#   - decision_review OFF/absent in comfort-posture.yaml -> allow (no engine call;
#     zero cost when not opted in). Off is the default.
#   - Only a SINGLE, genuinely BINARY yes/no question is eligible; multi-question,
#     multi-select, or >2 / non-yes-no option sets -> allow (human answers).
#   - The engine (thing-decide.py) owns the rest of the envelope: high-blast ->
#     defer, low-confidence / split / abstain / injection -> defer, advisory ->
#     non-binding. Only a BINDING yes/no denies (auto-resolves); anything else
#     allows. Any error/timeout/missing-dependency -> allow (ask the human).
#
# Every routed decision is Sága-logged by thing-decide.py under
# .ravenclaude/runs/thing/decisions/ — the refinement-loop substrate.

set -euo pipefail

# ── Structured hook-event substrate (Phase 0). Source the emit helper so the
#    binding-verdict deny path below is recorded in hook-events.jsonl. Fail-safe:
#    absent helper -> no-op stub (the deny verdict is unaffected).
_emit_event_helper="$(dirname "${BASH_SOURCE[0]}")/_emit-event.sh"
if [ -f "$_emit_event_helper" ]; then
  # shellcheck source=/dev/null
  . "$_emit_event_helper" 2>/dev/null || true
fi
command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }

payload="$(cat 2>/dev/null || true)"

# --- helpers: always fail safe to ALLOW (let the human answer) ---
emit_allow() { printf '%s' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}'; exit 0; }
command -v jq >/dev/null 2>&1 || emit_allow
[ -n "$payload" ] || emit_allow

root="${CLAUDE_PROJECT_DIR:-$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null)}"
root="${root:-$PWD}"
posture="$root/.ravenclaude/comfort-posture.yaml"

# --- 1. Off-by-default short-circuit (no engine call unless opted in) ---
[ -f "$posture" ] || emit_allow
mode="$(grep -E '^[[:space:]]*decision_review:' "$posture" 2>/dev/null | head -1 | sed -E 's/.*decision_review:[[:space:]]*//; s/["'\'' ]//g; s/#.*//' | tr '[:upper:]' '[:lower:]')"
case "$mode" in
  advisory | binding) ;;            # opted in -> continue
  *) emit_allow ;;                   # off / absent / unknown -> human answers
esac

ti="$(printf '%s' "$payload" | jq -c '.tool_input // {}' 2>/dev/null || echo '{}')"

# --- 2. Eligibility: exactly one question, not multi-select, exactly 2 options ---
qcount="$(printf '%s' "$ti" | jq '(.questions // []) | length' 2>/dev/null || echo 0)"
[ "$qcount" = "1" ] || emit_allow
multi="$(printf '%s' "$ti" | jq -r '.questions[0].multiSelect // false' 2>/dev/null || echo true)"
[ "$multi" = "false" ] || emit_allow
optcount="$(printf '%s' "$ti" | jq '(.questions[0].options // []) | length' 2>/dev/null || echo 0)"
[ "$optcount" = "2" ] || emit_allow

qtext="$(printf '%s' "$ti" | jq -r '.questions[0].question // ""' 2>/dev/null)"
opt0="$(printf '%s' "$ti" | jq -r '.questions[0].options[0].label // ""' 2>/dev/null)"
opt1="$(printf '%s' "$ti" | jq -r '.questions[0].options[1].label // ""' 2>/dev/null)"

# The two options must be recognizably yes/no-shaped (else a yes|no verdict can't map).
opts_lc="$(printf '%s\n%s' "$opt0" "$opt1" | tr '[:upper:]' '[:lower:]')"
echo "$opts_lc" | grep -Eq '^(yes|no|proceed|cancel|approve|reject|confirm|deny|do it|don.?t|continue|stop|accept|decline|merge|skip|enable|disable|allow|block)$' || emit_allow
# require BOTH options to be yes/no-ish (2 matching lines)
[ "$(echo "$opts_lc" | grep -Ecx '(yes|no|proceed|cancel|approve|reject|confirm|deny|do it|don.?t|continue|stop|accept|decline|merge|skip|enable|disable|allow|block)')" = "2" ] || emit_allow

# --- 3. high-blast heuristic (engine also guards; belt + suspenders) ---
hb=false
if printf '%s %s %s' "$qtext" "$opt0" "$opt1" | grep -Eiq 'force[- ]?push|reset --hard|\brm -rf\b|delete|drop |prod(uction)?|publish|secret|credential|merge to main|push to main'; then hb=true; fi

# --- 4. Route through the tribunal engine (fail safe to allow on any error) ---
engine="${CLAUDE_PLUGIN_ROOT:-$root/plugins/ravenclaude-core}/scripts/thing-decide.py"
[ -f "$engine" ] || engine="$root/plugins/ravenclaude-core/scripts/thing-decide.py"
[ -f "$engine" ] || emit_allow

req="$(jq -nc --arg q "$qtext" --arg c "Binary user prompt intercepted by route-decision-review. Options: [$opt0 | $opt1]. Auto-resolve only if rule/fact-derivable." --argjson hb "$hb" '{question:$q,context:$c,high_blast:$hb}' 2>/dev/null || echo '')"
[ -n "$req" ] || emit_allow

out="$(printf '%s' "$req" | timeout 80 python3 "$engine" --root "$root" decide 2>/dev/null || echo '')"
[ -n "$out" ] || emit_allow

verdict="$(printf '%s' "$out" | jq -r '.verdict // "defer"' 2>/dev/null || echo defer)"
binding="$(printf '%s' "$out" | jq -r '.binding // false' 2>/dev/null || echo false)"
reasoning="$(printf '%s' "$out" | jq -r '.reasoning // ""' 2>/dev/null || echo '')"
saga="$(printf '%s' "$out" | jq -r '.saga_log // "n/a"' 2>/dev/null || echo 'n/a')"

# --- 5. Act: only a BINDING yes/no auto-resolves; everything else asks ---
if { [ "$verdict" = "yes" ] || [ "$verdict" = "no" ]; } && [ "$binding" = "true" ]; then
  if [ "$verdict" = "yes" ]; then pick="$opt0"; else pick="$opt1"; fi
  reason="Decision-review tribunal ($mode) auto-resolved this yes/no prompt so the user was NOT interrupted. Verdict: ${verdict^^} -> choose the \"$pick\" option and proceed; do NOT call AskUserQuestion again for this. Panel reasoning: ${reasoning}. (Sága: ${saga}.) If you believe this is wrong or a genuine preference, state so and proceed with the user's likely intent rather than re-prompting."
  _emit_hook_event "route-decision-review.sh" "deny" "AskUserQuestion" "$qtext" "binding-verdict-${verdict}" 2
  jq -nc --arg r "$reason" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}'
  exit 0
fi

emit_allow
