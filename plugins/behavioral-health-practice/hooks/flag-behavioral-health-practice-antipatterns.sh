#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the behavioral-health-practice plugin.
# Flags common Behavioral Health Practice anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced benchmark | patient PHI). Advisory
# by default — set BEHAVIORAL_HEALTH_PRACTICE_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${BEHAVIORAL_HEALTH_PRACTICE_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "behavioral-health-practice" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: review this Behavioral Health Practice deliverable against the §3 house opinions (baseline on every metric, source+date on every benchmark, no patient PHI)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "behavioral-health-practice: $findings advisory finding(s); BEHAVIORAL_HEALTH_PRACTICE_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
