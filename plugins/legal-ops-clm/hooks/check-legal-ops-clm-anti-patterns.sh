#!/usr/bin/env bash
# check-legal-ops-clm-anti-patterns.sh — advisory PreToolUse hook for the legal-ops-clm plugin.
# Flags mechanically-detectable legal-ops/CLM anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set CLM_STRICT=1 to make it blocking (exit 2).
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

# 1. A contract/legal-ops deliverable that gives positions/advice but never states the "not legal advice" boundary.
if grep -qiE "(clause librar|fallback position|redline|standard position|playbook|legal[ -]?ops|contract review)" "$file" 2>/dev/null; then
  if ! grep -qiE "not legal advice|operational (support|/process)|process support|a (qualified|licensed) (lawyer|attorney)" "$file" 2>/dev/null; then
    findings+=("Legal-ops/contract deliverable with no 'not legal advice' boundary — state that this is operational/process support and a qualified lawyer owns the legal judgement.")
  fi
fi

# 2. A clause library / standard position with no fallback or walk-away — every deviation then escalates.
if grep -qiE "standard position|clause librar" "$file" 2>/dev/null; then
  if ! grep -qiE "fallback|walk[ -]?away" "$file" 2>/dev/null; then
    findings+=("Clause library / standard position with no 'fallback' or 'walk-away' — without bounds every deviation escalates (a queue, not self-serve).")
  fi
fi

# 3. A renewal/auto-renew tracker that tracks expiry but never the notice window — you learn too late to stop a renewal.
if grep -qiE "auto[ -]?renew|renewal track|expiry|expiration" "$file" 2>/dev/null; then
  if ! grep -qiE "notice (window|period|deadline)|notice[- ]?window" "$file" 2>/dev/null; then
    findings+=("Renewal/auto-renew tracking with an expiry but no 'notice window/period/deadline' — track the notice deadline, not just the end date, or an auto-renew fires before you decide.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── legal-ops-clm advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${CLM_STRICT:-0}" = "1" ]; then
  echo "(blocking: CLM_STRICT=1)" >&2
  exit 2
fi
exit 0
