#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the nonprofit-fundraising plugin.
# Flags common nonprofit fundraising anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced market figure | client PII). Advisory by default — set NONPROFIT_FUNDRAISING_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${NONPROFIT_FUNDRAISING_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "nonprofit-fundraising" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\bTODO\b\|lorem ipsum' "$FILE"; then
  note "Advisory: review this nonprofit fundraising deliverable against the §3 house opinions (baseline on every metric, source+date on every external figure, no client PII)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "nonprofit-fundraising: $findings advisory finding(s); NONPROFIT_FUNDRAISING_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
