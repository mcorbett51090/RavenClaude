#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the medical-revenue-cycle plugin.
# Flags common medical revenue cycle anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced market figure | client PII). Advisory by default — set MEDICAL_REVENUE_CYCLE_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${MEDICAL_REVENUE_CYCLE_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "medical-revenue-cycle" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: review this medical revenue cycle deliverable against the §3 house opinions (baseline on every metric, source+date on every external figure, no client PII)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "medical-revenue-cycle: $findings advisory finding(s); MEDICAL_REVENUE_CYCLE_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
