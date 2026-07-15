#!/usr/bin/env bash
# agent-dispatch-evaluator.sh
# SubagentStart hook — Phase 3 of docs/plans/2026-06-03-agent-dispatch-evaluator/plan.md.
#
# SHIPS AS AUDIT-ONLY (RM1). The plan's Phase 3 design emits a DENY+redispatch on a
# downgrade verdict, BUT Panel B R1 flagged that SubagentStart fires AFTER the subagent
# process is initiated — a DENY may be a late-stage cancel, not a pre-dispatch intercept,
# so a "downgrade" deny could waste the spawn it was trying to right-size. The plan's own
# fail-disposition: "Until that's verified live, the hook should ship as audit-only (logs
# verdict, no DENY emitted)." This session could not run a live armed dispatch to measure
# whether deny is pre-commit, so this hook is audit-only: it computes the right-sizing
# verdict and LOGS it (shadow), but ALWAYS allows the dispatch (exit 0, no permissionDecision).
# The Phase-2 workflow wrapper (evaluate-dispatch.js) remains the sole BINDING path.
#
# To promote this hook to binding once deny-is-pre-commit is verified: see SKILL.md
# §"Phase 3 — SubagentStart hook (audit-only)" for the exact change + the verification gate.
#
# Contract (Claude Code SubagentStart):
#   - stdin: a JSON object describing the subagent about to start. The exact field
#     names are [unverified — not confirmed against a live SubagentStart payload this
#     session]; this hook reads several candidate keys defensively and fails open if
#     none are present.
#   - On exit 0 with no output: allow (the dispatch proceeds unchanged). This is the
#     ONLY disposition this audit-only hook ever emits.
#
# Safety envelope (deliberately conservative — fail toward allowing the dispatch):
#   - dispatch-config.json absent / enabled != true  -> allow (single grep, zero cost
#     when not opted in; enabled:false is the shipped default).
#   - subagent_type on the allowlist (Explore / statusline-setup / claude)  -> allow.
#   - _predispatch:"skip" anywhere in the input  -> allow.
#   - THING_SEAT_ACTIVE=1 in env (this spawn IS a tribunal seat)  -> shadow-log + allow.
#   - classifier subprocess missing / times out / unparseable  -> allow (fail-open).
#   - ANY error  -> allow.
#
# Every computed verdict is recorded via _emit_hook_event (verdict="warn", so it lands in
# Heimdall's grey/advisory tier, never the security-deny tier) AND appended to the
# dispatch-eval JSONL the Phase-5 sampler reads.

set -euo pipefail

# Stock-toolchain portability: coreutils `timeout` is ABSENT on macOS (exit 127), which
# would make the `claude -p` probe below silently take its error path on every macOS
# session. Fail-safe: an absent helper degrades to an unbounded run, never a broken hook.
_portable_helper="$(dirname "${BASH_SOURCE[0]}")/_portable.sh"
[ -f "$_portable_helper" ] && . "$_portable_helper" 2>/dev/null || true
command -v _rc_timeout >/dev/null 2>&1 || _rc_timeout() { shift; "$@"; }

# ── Structured hook-event substrate. Source the emit helper so every shadow verdict is
#    recorded in hook-events.jsonl. Fail-safe: absent helper -> no-op stub.
_emit_event_helper="$(dirname "${BASH_SOURCE[0]}")/_emit-event.sh"
if [ -f "$_emit_event_helper" ]; then
  # shellcheck source=/dev/null
  . "$_emit_event_helper" 2>/dev/null || true
fi
command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }

# --- allow == exit 0 with no body. SubagentStart has no "permissionDecision:allow" to
#     emit; the absence of a deny IS the allow. Every exit path below funnels here. ---
emit_allow() { exit 0; }

payload="$(cat 2>/dev/null || true)"
[ -n "$payload" ] || emit_allow
command -v jq >/dev/null 2>&1 || emit_allow

root="${CLAUDE_PROJECT_DIR:-$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null)}"
root="${root:-$PWD}"

# --- 1. Off-by-default short-circuit. Resolve the dispatch-config the consumer adopted
#        (project .ravenclaude/ first, then the plugin template as a read-only fallback so
#        the hook is inert-but-present even before a consumer copies the template). A single
#        grep for `"enabled": true` keeps this zero-cost for everyone not opted in. ---
cfg="$root/.ravenclaude/dispatch-config.json"
if [ ! -f "$cfg" ]; then
  _tmpl="${CLAUDE_PLUGIN_ROOT:-$root/plugins/ravenclaude-core}/skills/agent-dispatch-evaluator/templates/dispatch-config.json"
  [ -f "$_tmpl" ] && cfg="$_tmpl" || emit_allow
fi
grep -Eq '"enabled"[[:space:]]*:[[:space:]]*true' "$cfg" 2>/dev/null || emit_allow

# --- 2. Parse the config (now that we know it's enabled). Fail-open on a parse error. ---
cfg_json="$(jq -c '.' "$cfg" 2>/dev/null || echo '')"
[ -n "$cfg_json" ] || emit_allow
mode="$(printf '%s' "$cfg_json" | jq -r '.mode // "shadow"' 2>/dev/null || echo shadow)"

# --- 3. Extract the dispatch envelope defensively (candidate key names, unverified shape). ---
subagent_type="$(printf '%s' "$payload" | jq -r '
  .subagent_type // .subagentType // .agent_type // .agentType //
  .tool_input.subagent_type // .tool_input.subagentType //
  .input.subagent_type // .input.subagentType // "unknown"' 2>/dev/null || echo unknown)"
description="$(printf '%s' "$payload" | jq -r '
  .description // .tool_input.description // .input.description // .label // ""' 2>/dev/null || echo '')"
prompt_head="$(printf '%s' "$payload" | jq -r '
  (.prompt // .tool_input.prompt // .input.prompt // "") | tostring' 2>/dev/null | head -c 1800 || echo '')"
requested_model="$(printf '%s' "$payload" | jq -r '
  .model // .tool_input.model // .input.model // ""' 2>/dev/null || echo '')"

# --- 4. _predispatch:"skip" carve-out (per-call bypass marker, anywhere in the input). ---
if printf '%s' "$payload" | jq -e '.. | objects | select(._predispatch? == "skip")' >/dev/null 2>&1; then
  emit_allow
fi

# --- 5. subagent_type allowlist carve-out (built-in cheap subagents the evaluator skips). ---
allowlisted="$(printf '%s' "$cfg_json" | jq -r --arg t "$subagent_type" '
  (.subagent_type_allowlist // []) | map(select(. as $a | $t | test($a; "i"))) | length' 2>/dev/null || echo 0)"
[ "${allowlisted:-0}" != "0" ] && emit_allow

# --- 6. Tribunal-seat detection. A spawn that IS a tribunal seat is shadow-only forever
#        for MVP (RM2 — protects the >=2-distinct-backbones invariant). It is also handled
#        by Phase 4 inside thing-decide.py; here we just record it and allow. ---
caller_context="toplevel"
if [ "${THING_SEAT_ACTIVE:-}" = "1" ]; then
  caller_context="tribunal_seat"
fi

# --- 7. Fire the classifier subprocess (best-effort, hard timeout, fail-open). The plan's
#        RM7 structural exemption: a `claude -p --bare` subprocess spawned from a hook never
#        enters the agent's tool-call stream, so it does not count against runaway-brake.sh.
#        `claude` absent on PATH -> skip the classifier and allow (we still recorded nothing
#        actionable; audit-only means a missing classifier is simply no shadow data). ---
command -v claude >/dev/null 2>&1 || emit_allow

envelope="$(jq -nc \
  --arg st "$subagent_type" \
  --arg d "$(printf '%s' "$description" | head -c 200)" \
  --arg ph "$prompt_head" \
  --arg rm "$requested_model" \
  --arg cc "$caller_context" \
  '{subagent_type:$st, description:$d, prompt_head:$ph, requested_model:$rm, caller_context:$cc}' \
  2>/dev/null || echo '')"
[ -n "$envelope" ] || emit_allow

classifier_instr='You are a dispatch evaluator. Given this dispatch envelope, return ONLY a JSON object with fields: verdict ("keep"|"upgrade"|"downgrade"), suggested_tier ("fast"|"balanced"|"top"), confidence ("low"|"medium"|"high"), rationale (one sentence). Envelope: '
raw="$(_rc_timeout 3 claude -p --bare --output-format json --model claude-haiku-4-5-20251001 \
  "${classifier_instr}${envelope}" 2>/dev/null || echo '')"
[ -n "$raw" ] || emit_allow

# The --output-format json wrapper may nest the model text under .result; tolerate both
# a bare JSON verdict and a wrapped envelope. Extract the first {...} verdict object.
verdict_json="$(printf '%s' "$raw" | jq -c 'if type=="object" and has("verdict") then .
  elif type=="object" and has("result") then (.result | fromjson? // {})
  else . end' 2>/dev/null || echo '')"
verdict="$(printf '%s' "$verdict_json" | jq -r '.verdict // empty' 2>/dev/null || echo '')"
suggested_tier="$(printf '%s' "$verdict_json" | jq -r '.suggested_tier // empty' 2>/dev/null || echo '')"
confidence="$(printf '%s' "$verdict_json" | jq -r '.confidence // empty' 2>/dev/null || echo '')"
rationale="$(printf '%s' "$verdict_json" | jq -r '.rationale // ""' 2>/dev/null | tr -d '\n\r' | head -c 200 || echo '')"

# Unparseable / incomplete verdict -> nothing to log, allow (fail-open).
{ [ -n "$verdict" ] && [ -n "$suggested_tier" ] && [ -n "$confidence" ]; } || emit_allow

# --- 8. Record the shadow verdict. Two sinks:
#        (a) hook-events.jsonl (verdict="warn" -> Heimdall grey/advisory tier; this is
#            observability, never a security signal).
#        (b) the dispatch-eval JSONL the Phase-5 quality sampler reads. ---
rule="dispatch-${verdict}-shadow:${subagent_type}->${suggested_tier}(${confidence})"
_emit_hook_event "agent-dispatch-evaluator.sh" "warn" "Agent" "$subagent_type" "$rule" 0

session="${CLAUDE_SESSION_ID:-unknown}"
eval_dir="$root/.ravenclaude/runs/dispatch-eval"
eval_log="$eval_dir/${session}.jsonl"
if mkdir -p "$eval_dir" 2>/dev/null; then
  line="$(jq -nc \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || true)" \
    --arg st "$subagent_type" \
    --arg d40 "$(printf '%s' "$description" | head -c 40)" \
    --arg rm "$requested_model" \
    --arg cc "$caller_context" \
    --arg v "$verdict" \
    --arg t "$suggested_tier" \
    --arg c "$confidence" \
    --arg r "$(printf '%s' "$rationale" | head -c 120)" \
    --arg src "subagentstart-hook" \
    '{ts:$ts, subagent_type:$st, description_first40:$d40, requested_model:$rm,
       caller_context:$cc, verdict:$v, suggested_tier:$t, confidence:$c,
       rationale_first120:$r, applied:"shadow", source:$src}' \
    2>/dev/null || echo '')"
  [ -n "$line" ] && printf '%s\n' "$line" >> "$eval_log" 2>/dev/null || true
fi

# --- 9. AUDIT-ONLY: always allow. No permissionDecision, no DENY, regardless of verdict
#        or mode. The verdict was recorded above; acting on it is the workflow wrapper's job
#        (binding) until SubagentStart deny-is-pre-commit is verified live (see header + SKILL.md). ---
emit_allow
