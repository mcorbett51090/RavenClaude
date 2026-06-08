#!/usr/bin/env bash
# check-property-management-residential-anti-patterns.sh — advisory PreToolUse hook for the
# property-management-residential plugin. Flags mechanically-detectable residential property
# anti-patterns on Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice);
# set PM_STRICT=1 to make it blocking (exit 2). It is a prompt to review — NOT legal advice.
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# 1. Protected-class / steering language in an ad or screening criteria — a fair-housing FLAG (not a ruling).
if grep -qiE "(adults?[ -]only|no (kids|children)|christian|no section[ -]?8|must (be able to )?climb|able[ -]bodied|perfect for (a )?(single|couple|bachelor)|ideal for (young|mature))" "$file" 2>/dev/null; then
  findings+=("Possible protected-class / steering language (familial status, religion, source of income, disability). FLAG to counsel — do not adjudicate. This is a prompt to review, not legal advice.")
fi

# 2. A habitability/emergency keyword routed as 'routine' / 'low priority' / 'non-urgent'.
if grep -qiE "(no heat|no water|no power|gas leak|sewage|no (working )?lock|carbon monoxide)" "$file" 2>/dev/null; then
  if grep -qiE "(routine|low[ -]priority|non[ -]urgent|non[ -]emergency|can wait|defer)" "$file" 2>/dev/null; then
    findings+=("A habitability/emergency condition (no heat/water/power, gas, sewage, no lock) appears alongside 'routine/low-priority/defer' — habitability events are emergencies with a duty to act fast, never routine.")
  fi
fi

# 3. NOI written with debt service / depreciation / capex mixed in, or equated to cash flow.
if grep -qiE "\bNOI\b" "$file" 2>/dev/null; then
  if grep -qiE "(debt service|mortgage|depreciation|principal|interest|capex|capital expenditure|cash[ -]?flow)" "$file" 2>/dev/null; then
    findings+=("'NOI' appears near debt service / depreciation / capex / cash-flow — NOI is operating-only (excl. debt service, capex, depreciation) and is NOT cash flow. Verify the calculation.")
  fi
fi

# 4. A bare tenant SSN pattern in an output — PII that should never be pasted.
if grep -qE "\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b" "$file" 2>/dev/null; then
  findings+=("A 9-digit SSN-shaped value (###-##-####) is present — tenant PII must be minimized, never pasted into an output/report/ticket. Remove or redact it.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── property-management-residential advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${PM_STRICT:-0}" = "1" ]; then
  echo "(blocking: PM_STRICT=1)" >&2
  exit 2
fi
exit 0
