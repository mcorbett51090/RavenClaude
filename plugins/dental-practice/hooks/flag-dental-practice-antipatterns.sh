#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the dental-practice plugin.
# Flags common dental practice anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced market figure | client PII). Advisory by default — set DENTAL_PRACTICE_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${DENTAL_PRACTICE_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "dental-practice" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: review this dental practice deliverable against the §3 house opinions (baseline on every metric, source+date on every external figure, no client PII)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "dental-practice: $findings advisory finding(s); DENTAL_PRACTICE_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
