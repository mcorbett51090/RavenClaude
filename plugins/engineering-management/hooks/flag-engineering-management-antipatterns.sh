#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the engineering-management plugin.
# Flags common Engineering Management anti-patterns in generated deliverables
# (a verdict-not-hypothesis about a person | an individual ranked by velocity |
# an unsourced benchmark | personnel PII). Advisory by default — set
# ENGINEERING_MANAGEMENT_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${ENGINEERING_MANAGEMENT_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "engineering-management" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: review this Engineering Management deliverable against the §3 house opinions (a claim about a person is a hypothesis not a verdict, no velocity-ranked individuals, source+date on every benchmark, no personnel PII)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "engineering-management: $findings advisory finding(s); ENGINEERING_MANAGEMENT_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
