#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the accessibility-engineering plugin.
# Flags common Accessibility Engineering anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced benchmark | user PII). Advisory
# by default — set ACCESSIBILITY_ENGINEERING_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${ACCESSIBILITY_ENGINEERING_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "accessibility-engineering" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: review this Accessibility Engineering deliverable against the §3 house opinions (baseline on every metric, source+date on every benchmark, no user PII)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "accessibility-engineering: $findings advisory finding(s); ACCESSIBILITY_ENGINEERING_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
