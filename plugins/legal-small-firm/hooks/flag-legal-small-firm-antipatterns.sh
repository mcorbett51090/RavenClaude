#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the legal-small-firm plugin.
# Flags common small-firm legal practice anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced market figure | client PII). Advisory by default — set LEGAL_SMALL_FIRM_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${LEGAL_SMALL_FIRM_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "legal-small-firm" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: review this small-firm legal practice deliverable against the §3 house opinions (baseline on every metric, source+date on every external figure, no client PII)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "legal-small-firm: $findings advisory finding(s); LEGAL_SMALL_FIRM_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
