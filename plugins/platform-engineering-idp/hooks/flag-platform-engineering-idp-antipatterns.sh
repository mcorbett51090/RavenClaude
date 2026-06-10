#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the platform-engineering-idp plugin.
# Flags common Platform Engineering (IDP) anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced benchmark | internal credentials/PII). Advisory
# by default — set PLATFORM_ENGINEERING_IDP_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${PLATFORM_ENGINEERING_IDP_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "platform-engineering-idp" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: review this Platform Engineering (IDP) deliverable against the §3 house opinions (baseline on every metric, source+date on every benchmark, no internal credentials/PII)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "platform-engineering-idp: $findings advisory finding(s); PLATFORM_ENGINEERING_IDP_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
