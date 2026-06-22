#!/usr/bin/env bash
# check-data-governance-privacy-anti-patterns.sh — advisory PreToolUse hook for the data-governance-privacy plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set DATAGOV_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()
if grep -nEi "(ssn|social_security|national_id|passport|credit_card|card_number|dob|date_of_birth)\\b" "$file" >/dev/null 2>&1; then
  findings+=("Possible PII field — ensure it's classified, minimized (do you need it?), access-controlled, and in DSR/retention scope.")
fi
if grep -Pzi "(anonymi[sz]ed)(?![\\s\\S]{0,80}(k-anonymity|aggregat|irreversible))" "$file" >/dev/null 2>&1; then
  findings+=("Field/comment claims 'anonymized' — verify it's truly anonymized (not just pseudonymized/re-identifiable); pseudonymized data is still personal data.")
fi
if grep -nEi "(retention|ttl|delete_after)\\s*[=:]\\s*(never|none|0|indefinite|-1)" "$file" >/dev/null 2>&1; then
  findings+=("Indefinite/no retention on data — define a retention period tied to lawful basis; indefinite retention is unbounded risk.")
fi
if grep -nEi "(select\\s+\\*\\s+from\\s+\\w*(user|customer|person|patient))" "$file" >/dev/null 2>&1; then
  findings+=("SELECT * from a personal-data table — minimize columns retrieved; broad PII access should be need-to-know.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── data-governance-privacy advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${DATAGOV_STRICT:-0}" = "1" ]; then
  echo "(blocking: DATAGOV_STRICT=1)" >&2
  exit 2
fi
exit 0
