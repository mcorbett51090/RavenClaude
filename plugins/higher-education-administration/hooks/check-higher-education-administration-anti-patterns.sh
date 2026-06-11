#!/usr/bin/env bash
# check-higher-education-administration-anti-patterns.sh — advisory PreToolUse hook for the
# higher-education-administration plugin. Flags mechanically-detectable anti-patterns on
# Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice to stderr);
# set HIGHERED_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect text/config/doc files; skip binaries.
case "$file" in
*.md | *.yaml | *.yml | *.json | *.txt | *.py | *.sh) ;;
*) exit 0 ;;
esac

findings=()

# 1. Discount/aid decision with no net-revenue basis.
if grep -nEi "\b(discount ?rate|tuition discount|institutional aid|merit ?aid|financial aid leverag|scholarship budget)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(net ?tuition ?revenue|net ?revenue|net ?price|yield ?per|diminishing ?return)\b" "$file" >/dev/null 2>&1; then
    findings+=("Aid/discount decision with no net-tuition-revenue basis — gross tuition and sticker price are vanity figures; evaluate aid against net tuition revenue (best-practices/net-tuition-revenue-is-the-real-number.md).")
  fi
fi

# 2. Retention claim with no cohort/persistence basis.
if grep -nEi "\b(retention ?rate|retention ?is|completion ?rate|graduation ?rate|attrition)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(cohort|persistence|entering ?class|year.?1.?to.?year.?2|first.?year|by ?term)\b" "$file" >/dev/null 2>&1; then
    findings+=("Retention/completion claim with no cohort or persistence framing — retention is a cohort phenomenon; frame by entering cohort, not a point-in-time headcount (best-practices/measure-cohorts-not-snapshots.md).")
  fi
fi

# 3. Student-data handling with no FERPA note.
if grep -nEi "\b(student ?record|education ?record|student ?data|early.?alert|student ?dashboard|risk ?score|grades? ?data)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(ferpa|privacy|legitimate ?educational ?interest|access ?control|de.?identif|consent)\b" "$file" >/dev/null 2>&1; then
    findings+=("Student-data handling with no FERPA/privacy note — student education records carry legal handling requirements; design access around legitimate educational interest (best-practices/ferpa-is-a-design-constraint-not-an-afterthought.md).")
  fi
fi

[ ${#findings[@]} -eq 0 ] && exit 0

{
  echo "higher-education-administration advisory — ${#findings[@]} possible anti-pattern(s) in $file:"
  for f in "${findings[@]}"; do
    echo "  • $f"
  done
} >&2

if [ "${HIGHERED_STRICT:-0}" = "1" ]; then
  exit 2
fi
exit 0
