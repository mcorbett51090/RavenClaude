#!/usr/bin/env bash
# check-cybersecurity-grc-anti-patterns.sh — advisory PreToolUse hook for the cybersecurity-grc plugin.
# Flags mechanically-detectable GRC anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set GRC_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# 1. A Statement-of-Applicability exclusion marked N/A with no justification — the §4 #6 SoA rule.
if grep -qiE "statement of applicability|\bSoA\b|annex\s*a" "$file" 2>/dev/null; then
  if grep -qiE "(not[ -]applicable|\bN/?A\b|excluded)" "$file" 2>/dev/null \
    && ! grep -qiE "(justif|rationale|reason|because|residual\s+risk)" "$file" 2>/dev/null; then
    findings+=("SoA exclusion ('N/A' / not-applicable) with no justification/rationale — every exclusion needs an auditor-defensible reason traced to the risk register.")
  fi
fi

# 2. A risk-register row with no treating control or no owner — the §4 #7 risk-drives-controls rule.
if grep -qiE "risk\s*register|likelihood|inherent\s+risk|residual\s+risk" "$file" 2>/dev/null; then
  if ! grep -qiE "(control|treatment|mitigat|accept|transfer|avoid)" "$file" 2>/dev/null; then
    findings+=("Risk register with no treatment/control column — risk drives controls; a top risk with no control is the real exposure.")
  fi
  if ! grep -qiE "(owner|accountable|responsible)" "$file" 2>/dev/null; then
    findings+=("Risk register with no owner — every risk row needs a named owner (an un-owned accepted risk is an ignored one).")
  fi
fi

# 3. A control/policy doc that claims a control "operates" / is "operating effectively" with no evidence reference.
if grep -qiE "operating[ -]effective|operates effectively|control is in place|control operates" "$file" 2>/dev/null; then
  if ! grep -qiE "(evidence|artifact|log|screenshot|export|sample|test\s+result|monitor)" "$file" 2>/dev/null; then
    findings+=("Claims a control operates effectively with no evidence reference — a control has three states; 'operating-effectively' needs evidence it ran over the period.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── cybersecurity-grc advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${GRC_STRICT:-0}" = "1" ]; then
  echo "(blocking: GRC_STRICT=1)" >&2
  exit 2
fi
exit 0
