#!/usr/bin/env bash
# check-studio-anti-patterns.sh — advisory PreToolUse hook for the fitness-studio-operations plugin.
# Flags mechanically-detectable studio-ops anti-patterns on Edit/Write/MultiEdit of .md files.
# Advisory by default (exit 0, prints a notice); set STUDIO_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect markdown files (pricing plans, retention dashboards, schedule/pay plans).
case "$file" in
  *.md) ;;
  *) exit 0 ;;
esac

findings=()

# 1. A pricing/membership doc with no churn/retention view.
if grep -nEi 'pricing|membership|ltv|revenue per member' "$file" >/dev/null 2>&1; then
  if ! grep -nEi 'churn|retention|lifetime' "$file" >/dev/null 2>&1; then
    findings+=("This looks like a pricing/membership doc with no churn/retention view — retention is the economic engine; price the model against churn and lifetime, not in isolation.")
  fi
fi

# 2. A schedule/capacity doc with no utilization/fill-rate view.
if grep -nEi 'schedule|class slot|capacity|waitlist' "$file" >/dev/null 2>&1; then
  if ! grep -nEi 'utilization|fill.?rate|attendance' "$file" >/dev/null 2>&1; then
    findings+=("This schedule/capacity doc names no utilization/fill-rate — capacity is utilization per slot (attendance / capacity), not headcount.")
  fi
fi

# 3. An instructor-pay doc with no classification (1099/W2) view.
if grep -nEi 'instructor pay|trainer pay|rev.?share|per.?head|instructor comp' "$file" >/dev/null 2>&1; then
  if ! grep -nEi '1099|w-?2|classif|contractor|employee' "$file" >/dev/null 2>&1; then
    findings+=("This instructor-pay doc names no 1099/W2 classification flag — the contractor-vs-employee line is consequential; flag it and defer the binding call to people-operations-hr + counsel.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── fitness-studio-operations advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${STUDIO_STRICT:-0}" = "1" ]; then
  echo "(blocking: STUDIO_STRICT=1)" >&2
  exit 2
fi
exit 0
