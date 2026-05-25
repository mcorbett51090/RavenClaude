#!/usr/bin/env bash
# thing-orchestrator.sh — the "Lawspeaker" of the command-review tribunal ("the Thing").
#
# A PreToolUse(Bash) hook. When command review is toggled ON for a command's
# comfort-posture category, it convenes the tribunal — in T2, a SINGLE seat
# (code-reviewer-shaped, via thing-seat.sh) that renders ALLOW or DENY — writes
# an audit-trail ("Sága log") entry, and returns a Claude Code permission
# verdict. EDIT verdicts and the full multi-seat panel arrive in T3+.
#
# Protocol (code.claude.com/docs/en/hooks, re-verified 2026-05-25):
#   - stdin is the tool call as JSON: {tool_name, tool_input, cwd, session_id, ...}
#   - On exit 0 we emit hookSpecificOutput.permissionDecision (allow|deny|ask).
#     (deny blocks even under --dangerously-skip-permissions; allow resolves an
#      "ask" to a run; allow can NOT loosen a settings `deny` floor.)
#   - The platform FAILS OPEN on hook timeout, so the deadline below is OUR job.
#
# T2 scope: fires when `thing: on` for a category (regardless of comfort level —
# the §B.6 "only adjudicate inside the ask bucket" optimization is a later
# refinement). Single category proven end-to-end: shell_readonly.
#
# Fail-closed posture (never silently allow on our own error):
#   - missing jq / decision helper      -> deny  (E14: detect-and-deny)
#   - present-but-malformed thing.yaml  -> ask
#   - seat timeout / abstain / malformed-> ask
# A command in NO enabled category falls through (exit 0, no output) to the
# normal comfort-posture flow — that flow is the safety floor.

set -euo pipefail

# ── Recursion guard: the seat runs `claude -p --bare` (which already skips
#    hooks); this is belt-and-suspenders so a tribunal call can never reconvene
#    the tribunal on its own sub-commands. ─────────────────────────────────────
[ -n "${THING_SEAT_ACTIVE:-}" ] && exit 0

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
DECISION="${PLUGIN_ROOT}/scripts/thing-decision.py"
SEAT="${PLUGIN_ROOT}/scripts/thing-seat.sh"

# Read the tool call from stdin (canonical contract).
payload=""
if [ ! -t 0 ]; then payload="$(cat)"; fi
[ -z "$payload" ] && exit 0

# ── Emit a Claude Code PreToolUse verdict and exit. ───────────────────────────
emit() {  # emit <allow|deny|ask> <reason>
  jq -cn --arg d "$1" --arg r "$2" \
    '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:$d,permissionDecisionReason:$r}}'
  exit 0
}

# jq is required to read the payload at all. If it is missing we cannot even
# parse stdin — detect-and-deny rather than fail open (design E14).
if ! command -v jq >/dev/null 2>&1; then
  echo "[Command review] jq not available; blocking to fail closed." >&2
  # No jq means we cannot emit JSON either; exit 2 is the unconditional block.
  exit 2
fi

tool_name="$(printf '%s' "$payload" | jq -r '.tool_name // empty')"
[ "$tool_name" != "Bash" ] && exit 0

cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // empty')"
[ -z "$cmd" ] && exit 0

cwd="$(printf '%s' "$payload" | jq -r '.cwd // empty')"
[ -z "$cwd" ] && cwd="$PWD"
session_id="$(printf '%s' "$payload" | jq -r '.session_id // empty')"

# ── Fast short-circuit: if no category is toggled on (no "thing:" in the posture
#    file), do nothing — keeps the common case at a single grep, no python. ─────
posture_file="${cwd}/.ravenclaude/comfort-posture.yaml"
if [ ! -f "$posture_file" ] || ! grep -Eq '^[[:space:]]*thing:[[:space:]]*(on|true|yes)\b' "$posture_file"; then
  exit 0
fi

# ── Routing: category + toggle + seat config (one python call). ───────────────
[ -f "$DECISION" ] || emit ask "Command review enabled but decision helper is missing; deferring to you."
decision="$(THING_SEAT_ACTIVE= python3 "$DECISION" --root "$cwd" classify "$cmd" 2>/dev/null || true)"
[ -z "$decision" ] && emit ask "Command review could not classify the command; deferring to you."

enabled="$(printf '%s' "$decision" | jq -r '.thing_enabled // false')"
[ "$enabled" != "true" ] && exit 0   # category not toggled on -> normal flow

category="$(printf '%s' "$decision" | jq -r '.category // "unknown"')"
config_error="$(printf '%s' "$decision" | jq -r '.config_error // empty')"
[ -n "$config_error" ] && emit ask "Command review config error ($config_error); deferring to you."

model="$(printf '%s' "$decision" | jq -r '.seat.model // "haiku"')"
timeout_s="$(printf '%s' "$decision" | jq -r '.internal_timeout_seconds // 18')"
audit_dir_rel="$(printf '%s' "$decision" | jq -r '.audit_dir // ".ravenclaude/runs/thing"')"

run_id="thing-$(date -u +%Y-%m-%dT%H-%M-%SZ)-$$"
started_ms="$(date +%s%3N 2>/dev/null || echo 0)"

# ── Pre-LLM critical screen (deterministic, no credits). Mirrors the catalog's
#    pre-LLM denials: secret material and injection-shaped payloads are blocked
#    before any model sees them (§B.9.3). ──────────────────────────────────────
pre_verdict=""; pre_concern=""; injection="false"
inj_re='ignore (all )?(previous|prior) instructions|disregard (the )?(above|previous)|you are now|<system>|approve this command|override.{0,12}(safety|security|deny)'
sec_re='(AKIA[0-9A-Z]{12,})|(sk-[A-Za-z0-9]{20,})|(sk-ant-[A-Za-z0-9-]{20,})|(ghp_[A-Za-z0-9]{30,})|(-----BEGIN [A-Z ]*PRIVATE KEY-----)|(-p[[:space:]]+[^[:space:]]{6,})'
shopt -s nocasematch
if [[ "$cmd" =~ $inj_re ]]; then
  pre_verdict="deny"; pre_concern="xc.injection-attempt"; injection="true"
elif [[ "$cmd" =~ $sec_re ]]; then
  pre_verdict="deny"; pre_concern="xc.secret-in-command"
fi
shopt -u nocasematch

# ── Convene the seat (unless pre-screened). ───────────────────────────────────
verdict="ask"; reason=""; concerns="[]"; confidence="null"; seat_status="pre-screen"
if [ -n "$pre_verdict" ]; then
  verdict="$pre_verdict"; concerns="[\"$pre_concern\"]"; confidence="1.0"
  reason="Command review (the Thing): DENIED before review — matched critical concern ${pre_concern}."
else
  seat_out=""; seat_rc=0
  seat_out="$(THING_SEAT_ACTIVE=1 THING_CMD="$cmd" THING_CATEGORY="$category" THING_MODEL="$model" \
              THING_SEAT_MOCK_VERDICT="${THING_SEAT_MOCK_VERDICT:-}" \
              timeout "${timeout_s}s" bash "$SEAT" 2>/dev/null)" || seat_rc=$?
  if [ "${seat_rc:-0}" -ne 0 ] || [ -z "$seat_out" ] || ! printf '%s' "$seat_out" | jq -e . >/dev/null 2>&1; then
    seat_status="abstain"
    verdict="ask"
    reason="Command review: the reviewer abstained (timeout or error); deferring to you."
  else
    seat_status="voted"
    sv="$(printf '%s' "$seat_out" | jq -r '.verdict // "ask"')"
    injection="$(printf '%s' "$seat_out" | jq -r '.injection_detected // false')"
    confidence="$(printf '%s' "$seat_out" | jq -r '.confidence // 0')"
    concerns="$(printf '%s' "$seat_out" | jq -c '.concerns_cited // []')"
    seat_reason="$(printf '%s' "$seat_out" | jq -r '.reasoning // ""')"
    # Aggregation (single seat): injection is a unilateral deny; low confidence
    # escalates to ask; otherwise the seat's allow/deny stands.
    if [ "$injection" = "true" ]; then
      verdict="deny"; reason="Command review: DENIED — injection detected. ${seat_reason}"
    elif [ "$sv" = "deny" ]; then
      verdict="deny"; reason="Command review: DENIED. ${seat_reason}"
    elif [ "$sv" = "allow" ]; then
      awk_lo="$(awk -v c="$confidence" 'BEGIN{print (c<0.5)?"1":"0"}')"
      if [ "$awk_lo" = "1" ]; then
        verdict="ask"; reason="Command review: reviewer allowed but with low confidence (${confidence}); deferring to you."
      else
        verdict="allow"; reason="Command review: ALLOWED. ${seat_reason}"
      fi
    else
      verdict="ask"; reason="Command review: inconclusive verdict; deferring to you."
    fi
  fi
fi

# ── Sága log (best-effort; never let a logging failure change the verdict). ───
audit_dir="${cwd}/${audit_dir_rel}"
ended_ms="$(date +%s%3N 2>/dev/null || echo 0)"
duration_ms=$(( ended_ms - started_ms ))
if mkdir -p "$audit_dir" 2>/dev/null; then
  jq -cn \
    --arg id "$run_id" --arg sid "$session_id" \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg cmd "$cmd" --arg cat "$category" \
    --arg verdict "$verdict" --arg seat_status "$seat_status" \
    --arg model "$model" --arg injection "$injection" \
    --argjson concerns "$concerns" \
    --argjson confidence "${confidence:-null}" \
    --argjson duration "${duration_ms:-0}" \
    '{id:$id,session_id:$sid,timestamp:$ts,tool_name:"Bash",
      tool_input:{command:$cmd},category:$cat,phase:"T2-single-seat",
      seat:{name:"mimir",agent:"code-reviewer",model:$model,status:$seat_status,
            confidence:$confidence,injection_detected:($injection=="true")},
      concerns_cited:$concerns,final_verdict:$verdict,updated_input:null,
      duration_ms:$duration}' \
    > "${audit_dir}/${run_id}.json" 2>/dev/null || true
fi

emit "$verdict" "$reason Sága log: ${audit_dir_rel}/${run_id}.json"
