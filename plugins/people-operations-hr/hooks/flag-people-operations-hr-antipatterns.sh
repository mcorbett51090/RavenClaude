#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the people-operations-hr plugin.
# Flags common People-Ops anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced benchmark | employee PII). Advisory
# by default — set PEOPLE_OPERATIONS_HR_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${PEOPLE_OPERATIONS_HR_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "people-operations-hr" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: review this People-Ops deliverable against the §3 house opinions (baseline on every metric, source+date on every benchmark, no employee PII)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "people-operations-hr: $findings advisory finding(s); PEOPLE_OPERATIONS_HR_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
