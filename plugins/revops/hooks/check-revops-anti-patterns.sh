#!/usr/bin/env bash
# check-revops-anti-patterns.sh — advisory PreToolUse hook for the revops plugin.
# Flags mechanically-detectable RevOps anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set REVOPS_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# 1. A forecast doc with no named methodology — the §4 #3 rule.
if grep -qiE "forecast" "$file" 2>/dev/null; then
  if ! grep -qiE "weighted|commit|category|regression|methodolog|stage[ -]?weighted|AI" "$file" 2>/dev/null; then
    findings+=("A 'forecast' with no named methodology — name the method (weighted-by-stage / commit-category / AI-regression) and its bias; a gut-feel commit can't be improved.")
  fi
fi

# 2. A hard-coded coverage multiple with no win-rate derivation — the §4 #6 rule.
if grep -qiE "[0-9](\.[0-9])?x[ -]?coverage|coverage[ -]?(ratio|target|of)?[ ]*[0-9](\.[0-9])?x" "$file" 2>/dev/null; then
  if ! grep -qiE "win[ -]?rate|win[ -]?ratio|conversion|derive" "$file" 2>/dev/null; then
    findings+=("A hard-coded coverage multiple (e.g. '3x') with no win-rate derivation — coverage = gap / stage-weighted win-rate, not a folk constant.")
  fi
fi

# 3. A pipeline-stage definition with no objective exit criterion — the §4 #4 rule.
if grep -qiE "^\s*(stage|pipeline[ -]?stage)\s*[:=]" "$file" 2>/dev/null; then
  if ! grep -qiE "exit[ -]?criteri|buyer[ -]?action|verifiable|objective" "$file" 2>/dev/null; then
    findings+=("A pipeline stage with no exit criterion — every stage needs an objective, verifiable buyer-action exit criterion, not rep optimism.")
  fi
fi

# 4. A lead-routing doc with no speed-to-lead SLA — the §4 #7 rule.
if grep -qiE "lead[ -]?rout|routing|round[ -]?robin|lead[ -]?assign" "$file" 2>/dev/null; then
  if ! grep -qiE "speed[ -]?to[ -]?lead|SLA|response[ -]?time|owner" "$file" 2>/dev/null; then
    findings+=("Lead routing with no speed-to-lead SLA or defined owner — an unrouted lead is lost revenue; put a clock and an owner on it.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── revops advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${REVOPS_STRICT:-0}" = "1" ]; then
  echo "(blocking: REVOPS_STRICT=1)" >&2
  exit 2
fi
exit 0
