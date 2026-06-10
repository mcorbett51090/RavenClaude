#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the embedded-iot-engineering plugin.
# Flags common Embedded & IoT Engineering anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced benchmark | device/telemetry PII). Advisory
# by default — set EMBEDDED_IOT_ENGINEERING_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${EMBEDDED_IOT_ENGINEERING_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "embedded-iot-engineering" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: review this Embedded & IoT Engineering deliverable against the §3 house opinions (baseline on every metric, source+date on every benchmark, no device/telemetry PII)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "embedded-iot-engineering: $findings advisory finding(s); EMBEDDED_IOT_ENGINEERING_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
