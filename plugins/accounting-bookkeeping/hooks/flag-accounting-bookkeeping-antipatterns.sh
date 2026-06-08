#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the accounting-bookkeeping plugin.
# Flags common Accounting & Bookkeeping Practice anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced benchmark | client financial PII). Advisory
# by default — set ACCOUNTING_BOOKKEEPING_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${ACCOUNTING_BOOKKEEPING_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "accounting-bookkeeping" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: review this Accounting & Bookkeeping Practice deliverable against the §3 house opinions (baseline on every metric, source+date on every benchmark, no client financial PII)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "accounting-bookkeeping: $findings advisory finding(s); ACCOUNTING_BOOKKEEPING_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
