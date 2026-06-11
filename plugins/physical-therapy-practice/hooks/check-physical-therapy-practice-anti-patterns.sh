#!/usr/bin/env bash
# check-physical-therapy-practice-anti-patterns.sh — advisory PreToolUse hook for the
# physical-therapy-practice plugin. Flags mechanically-detectable PT anti-patterns on
# Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice to stderr);
# set PT_STRICT=1 to make it blocking (exit 2).
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

# 1. Timed CPT units with no 8-minute-rule / minute basis.
if grep -nEi "\b(timed (code|unit)|billable units?|units? billed|units? per visit|97110|97112|97140|therapeutic exercise)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(8.?minute|eight.?minute|timed minutes?|total minutes?|minute basis|rule of eights?)\b" "$file" >/dev/null 2>&1; then
    findings+=("Timed CPT units with no 8-minute-rule / minute basis — billable units follow documented timed minutes; cite the minute basis (best-practices/the-eight-minute-rule-governs-units.md).")
  fi
fi

# 2. Billing/coding decision with no medical-necessity / documentation basis.
if grep -nEi "\b(cpt ?code|coding decision|upcod|maximize reimbursement|revenue ?target|bill (higher|more)|code selection)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(medical ?necessity|documentation|documented|skilled ?service|plan ?of ?care|defensible)\b" "$file" >/dev/null 2>&1; then
    findings+=("Billing/coding decision with no medical-necessity or documentation basis — code forward from documented, medically necessary care, never backward from a target (best-practices/code-what-was-documented-not-the-reverse.md).")
  fi
fi

# 3. Cancellation framed as revenue-only with no adherence/episode framing.
if grep -nEi "\b(no.?show|cancellation|missed (visit|appointment)|cancel ?fee)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(adherence|plan ?of ?care|episode|clinical ?outcome|drop.?out|completion|engagement)\b" "$file" >/dev/null 2>&1; then
    findings+=("Cancellation/no-show framed with no adherence/episode/outcome context — a missed visit is a broken episode of care first, a revenue leak second (best-practices/cancellations-are-a-clinical-outcome.md).")
  fi
fi

[ ${#findings[@]} -eq 0 ] && exit 0

{
  echo "physical-therapy-practice advisory — ${#findings[@]} possible anti-pattern(s) in $file:"
  for f in "${findings[@]}"; do
    echo "  • $f"
  done
} >&2

if [ "${PT_STRICT:-0}" = "1" ]; then
  exit 2
fi
exit 0
