#!/usr/bin/env bash
# handoff-tax-meter.sh
# PostToolUse hook for Agent (the subagent-dispatch tool; matcher also accepts
# its pre-rename name Task). ADVISORY meter (never blocks) for the handoff tax
# of every dispatch — the measurement leg of
# plugins/ravenclaude-core/knowledge/model-tier-delegation.md.
#
# WHAT IT MEASURES, per dispatch, from the PostToolUse payload alone:
#   brief_words    tool_input.prompt         — what the Team Lead wrote
#   report_words   tool_response.content[]   — what the worker sent back
#   tier           resolvedModel / requested model -> fast | mid | frontier
#   tokens         tool_response.totalTokens etc. (FINAL request only — a
#                  lower bound, stated as such in the ledger's docstring)
# and appends one JSON line to .ravenclaude/runs/<session>/dispatch-ledger.jsonl
# (counts + ids only — NEVER the prompt or report text).
#
# WHEN IT SPEAKS (additionalContext to the Team Lead, via _advise.sh):
#   report_over_cap    worker report longer than the posture cap (default 400
#                      words) — "if it is longer than what you would have pasted
#                      yourself, the handoff failed"
#   brief_over_cap     brief longer than the cap (default 600) — the
#                      transcript-forwarding tell
#   frontier_readonly  a read-only/search worker (Explore, scout) ran on a
#                      frontier model — the un-pinned-Explore sink
#
# HONEST SCOPE: a hook cannot make a worker write less or make the Team Lead
# pin a cheaper model. It can only make the cost VISIBLE on the turn it was
# paid, and keep a per-session ledger so "cost per completed task" is a number
# instead of a feeling. It is ADVISORY (exit 0 always), OPT-IN (no-op unless
# the project has a .ravenclaude/comfort-posture.yaml — same rule as every
# other advisory hook here), and FAIL-SAFE (any error -> exit 0, dispatch
# result untouched). `handoff_tax: off` in the posture silences the advisory
# but still writes the ledger; the caps are `handoff_tax: { report_cap_words,
# brief_cap_words }`.
#
# The analysis lives in scripts/handoff-tax-meter.py (stdlib only, self-tested
# with `--self-test`); this wrapper is the hook contract: stdin -> python ->
# stderr-buffered advisory -> one hook-event line. Exactly one writer per
# substrate: python owns the dispatch ledger, this file owns hook-events.jsonl.

set -euo pipefail

_rc_hd="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || printf '.')"
# Buffer stderr and re-emit at exit as additionalContext (stderr at exit 0 is
# measured UNDELIVERED to the model — see _advise.sh header).
if [ -f "$_rc_hd/_advise.sh" ]; then . "$_rc_hd/_advise.sh"; rc_advise_init PostToolUse 0; fi
if [ -f "$_rc_hd/_emit-event.sh" ]; then . "$_rc_hd/_emit-event.sh"; fi
command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }

command -v python3 >/dev/null 2>&1 || exit 0
[ -t 0 ] && exit 0
payload="$(cat 2>/dev/null || true)"
[ -n "$payload" ] || exit 0

# Only the dispatch tool. A cheap grep before any python spawn: the payload
# carries `"tool_name":"Agent"` (or the legacy `"Task"`); anything else no-ops.
printf '%s' "$payload" | grep -Eq '"tool_name"[[:space:]]*:[[:space:]]*"(Agent|Task)"' || exit 0

# Project root: CLAUDE_PROJECT_DIR, else the payload's cwd, else $PWD.
root="${CLAUDE_PROJECT_DIR:-}"
if [ -z "$root" ] && command -v jq >/dev/null 2>&1; then
  root="$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null || true)"
fi
[ -n "$root" ] || root="$PWD"

# OPT-IN: no-op unless the project has adopted a comfort-posture (bounded walk-up).
posture_found=0
dir="$root"
for _ in 1 2 3 4 5 6 7 8 9 10; do
  [ -z "$dir" ] && break
  if [ -f "$dir/.ravenclaude/comfort-posture.yaml" ]; then posture_found=1; root="$dir"; break; fi
  [ "$dir" = "/" ] && break
  dir="$(dirname "$dir")"
done
[ "$posture_found" -eq 0 ] && exit 0

meter="$_rc_hd/../scripts/handoff-tax-meter.py"
[ -f "$meter" ] || exit 0

out="$(printf '%s' "$payload" | python3 "$meter" --project-root "$root" 2>/dev/null || printf 'OK\n')"
signal="$(printf '%s\n' "$out" | head -n 1)"
case "$signal" in
  SIGNAL\ *)
    flags="${signal#SIGNAL }"
    subagent="$(printf '%s' "$payload" | jq -r '.tool_input.subagent_type // "general-purpose"' 2>/dev/null || printf 'general-purpose')"
    _emit_hook_event "handoff-tax-meter.sh" "warn" "Agent" "$subagent" "$flags" "0" || true
    advisory="$(printf '%s\n' "$out" | tail -n +2)"
    if [ -n "$(printf '%s' "$advisory" | tr -d '[:space:]')" ]; then
      printf '%s\n' "$advisory" >&2
    fi
    ;;
  *)
    _emit_hook_event "handoff-tax-meter.sh" "allow" "Agent" "" "within-caps" "0" || true
    ;;
esac

exit 0
