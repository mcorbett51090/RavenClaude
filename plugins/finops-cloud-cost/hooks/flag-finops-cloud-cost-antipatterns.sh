#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the finops-cloud-cost plugin.
# Flags common FinOps & Cloud Cost anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced benchmark | billing/account PII). Advisory
# by default — set FINOPS_CLOUD_COST_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${FINOPS_CLOUD_COST_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "finops-cloud-cost" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: review this FinOps & Cloud Cost deliverable against the §3 house opinions (baseline on every metric, source+date on every benchmark, no billing/account PII)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "finops-cloud-cost: $findings advisory finding(s); FINOPS_CLOUD_COST_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
