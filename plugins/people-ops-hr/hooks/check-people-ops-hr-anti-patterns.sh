#!/usr/bin/env bash
# check-people-ops-hr-anti-patterns.sh — advisory PreToolUse hook for the people-ops-hr plugin.
# Flags mechanically-detectable people-ops/HR anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set HR_STRICT=1 to make it blocking (exit 2).
# NOTE: heuristic only — it never makes a legal determination; it nudges toward "flag for counsel".
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# 1. A policy/handbook doc that touches employment law but never routes it to counsel — the cardinal risk.
if grep -qiE "(handbook|policy|FLSA|exempt|at-will|EEO|ADA|termination|leave\s+entitlement|pay[ -]transparency|equal[ -]pay)" "$file" 2>/dev/null; then
  if ! grep -qiE "(counsel|legal|attorney|lawyer)" "$file" 2>/dev/null; then
    findings+=("Employment-law topic (FLSA/at-will/EEO/leave/etc.) with no 'flag for counsel' — this plugin does not give legal advice; route the legal determination to qualified counsel.")
  fi
fi

# 2. A comp band / salary range with no leveling framework underneath — a range with no logic for who lands where.
if grep -qiE "(salary\s+band|comp(ensation)?\s+band|pay\s+band|salary\s+range|midpoint)" "$file" 2>/dev/null; then
  if ! grep -qiE "(level|leveling|job\s+architecture|ladder|job\s+famil)" "$file" 2>/dev/null; then
    findings+=("Comp band/range with no leveling framework — build the leveling ladder first; a band with no level under it has no logic for who lands where.")
  fi
fi

# 3. An interview scorecard / kit with no anchored rating levels — a feelings form, not a structured assessment.
if grep -qiE "(scorecard|interview\s+kit|interview\s+loop|rubric)" "$file" 2>/dev/null; then
  if ! grep -qiE "(anchor|rating\s+level|1[ -]?(to|-)[ -]?[45]|level\s+[1-5]|competenc)" "$file" 2>/dev/null; then
    findings+=("Interview scorecard/kit with no anchored rating levels or competency map — anchor what a 1 vs a 4 looks like, or it's a feelings form that amplifies bias.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── people-ops-hr advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${HR_STRICT:-0}" = "1" ]; then
  echo "(blocking: HR_STRICT=1)" >&2
  exit 2
fi
exit 0
