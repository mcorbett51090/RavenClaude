#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the customer-support-cx-operations plugin.
# Flags common Customer Support & CX Operations anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced benchmark | customer PII). Advisory
# by default — set CUSTOMER_SUPPORT_CX_OPERATIONS_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${CUSTOMER_SUPPORT_CX_OPERATIONS_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "customer-support-cx-operations" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: review this Customer Support & CX Operations deliverable against the §3 house opinions (baseline on every metric, source+date on every benchmark, no customer PII)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "customer-support-cx-operations: $findings advisory finding(s); CUSTOMER_SUPPORT_CX_OPERATIONS_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
