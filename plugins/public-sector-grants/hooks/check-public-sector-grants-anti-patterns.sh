#!/usr/bin/env bash
# check-public-sector-grants-anti-patterns.sh — advisory PreToolUse hook for the public-sector-grants plugin.
# Flags mechanically-detectable grant anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set GRANTS_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# 1. An "objective" with no measure/target/deadline — the SMART rule.
if grep -qiE "objective[s]?\s*:" "$file" 2>/dev/null; then
  if ! grep -qiE "([0-9]+\s*%|by\s+(20[0-9]{2}|Q[1-4])|baseline|target|measured\s+by)" "$file" 2>/dev/null; then
    findings+=("An 'objective' with no measure/target/deadline — objectives are SMART or they're wishes (add a baseline, target, measure, and deadline).")
  fi
fi

# 2. A budget line/table with no budget narrative — every line needs a justification.
if grep -qiE "(budget|line\s*item|personnel|fringe|indirect\s+cost)" "$file" 2>/dev/null; then
  if ! grep -qiE "(budget\s+narrative|justif|allowable|allocable|reasonable)" "$file" 2>/dev/null; then
    findings+=("A budget reference with no budget-narrative/justification nearby — every line must be justified and pass allowable/allocable/reasonable.")
  fi
fi

# 3. A sub-recipient referenced with no monitoring — the pass-through liability.
if grep -qiE "sub[- ]?recipient" "$file" 2>/dev/null; then
  if ! grep -qiE "(monitor|risk\s+assessment|sub-?award|single\s+audit|follow-?up)" "$file" 2>/dev/null; then
    findings+=("A sub-recipient with no monitoring/risk-assessment/sub-award terms — the pass-through entity owes sub-recipient monitoring; a sub-recipient finding becomes yours.")
  fi
fi

# 4. A single-audit / threshold / 2 CFR number quoted with no authority cited.
if grep -qiE "(single\s+audit|de[- ]?minimis|threshold|2\s*CFR)" "$file" 2>/dev/null; then
  if ! grep -qiE "(2\s*CFR\s*(200|Part\s*200)|award\s+terms|verify-at-build|NOFO|\[unverified)" "$file" 2>/dev/null; then
    findings+=("A threshold / single-audit / 2 CFR reference with no authority cited — trace it to current 2 CFR 200 + the award terms, never to memory.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── public-sector-grants advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${GRANTS_STRICT:-0}" = "1" ]; then
  echo "(blocking: GRANTS_STRICT=1)" >&2
  exit 2
fi
exit 0
