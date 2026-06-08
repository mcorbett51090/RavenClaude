#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the automotive-dealership plugin.
# Flags common Automotive Dealership Operations anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced benchmark | customer PII). Advisory
# by default — set AUTOMOTIVE_DEALERSHIP_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${AUTOMOTIVE_DEALERSHIP_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "automotive-dealership" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: review this Automotive Dealership Operations deliverable against the §3 house opinions (baseline on every metric, source+date on every benchmark, no customer PII)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "automotive-dealership: $findings advisory finding(s); AUTOMOTIVE_DEALERSHIP_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
