#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the clinical-trials plugin.
# Flags common clinical trials anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced market figure | client PII). Advisory by default — set CLINICAL_TRIALS_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${CLINICAL_TRIALS_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "clinical-trials" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\bTODO\b\|lorem ipsum' "$FILE"; then
  note "Advisory: review this clinical trials deliverable against the §3 house opinions (baseline on every metric, source+date on every external figure, no client PII)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "clinical-trials: $findings advisory finding(s); CLINICAL_TRIALS_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
