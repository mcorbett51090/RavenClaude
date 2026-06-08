#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the wealth-management-ria plugin.
# Flags common Wealth Management (RIA Practice) anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced benchmark | client financial PII). Advisory
# by default — set WEALTH_MANAGEMENT_RIA_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${WEALTH_MANAGEMENT_RIA_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "wealth-management-ria" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: review this Wealth Management (RIA Practice) deliverable against the §3 house opinions (baseline on every metric, source+date on every benchmark, no client financial PII)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "wealth-management-ria: $findings advisory finding(s); WEALTH_MANAGEMENT_RIA_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
