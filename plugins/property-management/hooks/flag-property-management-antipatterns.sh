#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the property-management plugin.
# Flags common Property Management Operations anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced benchmark | tenant PII). Advisory
# by default — set PROPERTY_MANAGEMENT_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${PROPERTY_MANAGEMENT_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "property-management" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: review this Property Management Operations deliverable against the §3 house opinions (baseline on every metric, source+date on every benchmark, no tenant PII)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "property-management: $findings advisory finding(s); PROPERTY_MANAGEMENT_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
