#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the mortgage-lending plugin.
# Flags common Mortgage Lending Operations anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced benchmark | borrower PII / NPI). Advisory
# by default — set MORTGAGE_LENDING_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${MORTGAGE_LENDING_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "mortgage-lending" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: review this Mortgage Lending Operations deliverable against the §3 house opinions (baseline on every metric, source+date on every benchmark, no borrower PII / NPI)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "mortgage-lending: $findings advisory finding(s); MORTGAGE_LENDING_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
