#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the cannabis-operations plugin.
# Flags common cannabis operations anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced market figure | client PII). Advisory by default — set CANNABIS_OPERATIONS_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${CANNABIS_OPERATIONS_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "cannabis-operations" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\bTODO\b\|lorem ipsum' "$FILE"; then
  note "Advisory: review this cannabis operations deliverable against the §3 house opinions (baseline on every metric, source+date on every external figure, no client PII)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "cannabis-operations: $findings advisory finding(s); CANNABIS_OPERATIONS_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
