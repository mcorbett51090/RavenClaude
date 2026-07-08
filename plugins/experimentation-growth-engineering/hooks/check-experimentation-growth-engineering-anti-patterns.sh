#!/usr/bin/env bash
# check-experimentation-growth-engineering-anti-patterns.sh — advisory PreToolUse hook for the experimentation-growth-engineering plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set EXP_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
# $CLAUDE_TOOL_FILE_PATH (passed as $1 by hooks.json) is NOT a real Claude Code
# hook variable, so under Claude Code the arg is empty and the path arrives only
# via the canonical stdin JSON contract. Fall back to it — same dual-source
# pattern regen-on-manifest-change.sh / guard-destructive.sh already use.
if [[ -z "$file" ]] && [[ ! -t 0 ]] && command -v jq >/dev/null 2>&1; then
  payload="$(cat 2>/dev/null || true)"
  if [[ -n "$payload" ]]; then
    file="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)"
  fi
fi
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()
if grep -nEi "(p[_-]?value|p\\s*<\\s*0\\.0?5|statistically significant|significant at)" "$file" >/dev/null 2>&1; then
  findings+=("Computing/asserting statistical significance here — route significance (power/MDE/p-value) to applied-statistics; this layer produces clean data, not verdicts.")
fi
if grep -nEi "(stop.*experiment.*significan|peek|check.*results.*daily.*stop)" "$file" >/dev/null 2>&1; then
  findings+=("Possible peeking-to-stop — pre-register duration or use a sequential method (with applied-statistics); peeking inflates false positives.")
fi
if grep -Pzi "(flag|feature)\\s*[:=].*(true|enabled)(?![\\s\\S]{0,120}(owner|remove|expire|kill))" "$file" >/dev/null 2>&1; then
  findings+=("Feature flag without an apparent owner/removal/kill-switch nearby — every temp flag needs an owner + removal date; risky ones need a kill switch.")
fi
if grep -nEi "(track|capture|logEvent)\\([\\s\\S]{0,40}[\\\"'][A-Z ]{2,}|track\\([\\s\\S]{0,40}[\\\"'][a-z]+ [a-z]+" "$file" >/dev/null 2>&1; then
  findings+=("Possibly ad-hoc/inconsistent event name — follow the tracking plan's object_action convention; inconsistent names are the data mess.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── experimentation-growth-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${EXP_STRICT:-0}" = "1" ]; then
  echo "(blocking: EXP_STRICT=1)" >&2
  exit 2
fi
exit 0
