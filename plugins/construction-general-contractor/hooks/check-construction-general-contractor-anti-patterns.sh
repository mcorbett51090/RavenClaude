#!/usr/bin/env bash
# check-construction-general-contractor-anti-patterns.sh — advisory PreToolUse hook for the
# construction-general-contractor plugin. Flags mechanically-detectable GC anti-patterns on
# Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice to stderr);
# set CONSTRUCTION_GC_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect text files that are likely to contain GC estimates, schedules, or docs.
case "$file" in
*.md | *.txt | *.csv | *.yaml | *.yml | *.json | *.xml | *.html) ;;
*) exit 0 ;;
esac

findings=()

# 1. Markup confused with margin — a % applied without distinguishing basis.
#    Triggers when a document uses "markup" and "margin" in the same calculation context
#    without a conversion statement, or uses a bare "%" after "profit" with no basis label.
if grep -nEi "(markup|margin)" "$file" >/dev/null 2>&1; then
  if grep -nEi "\b(markup|margin)\b" "$file" | grep -qEi "(markup|margin)" && \
     ! grep -qEi "(markup.{0,40}margin|margin.{0,40}markup|markup on cost|markup on direct|margin on revenue|% markup|% margin)" "$file" 2>/dev/null; then
    findings+=("Markup/margin language detected without a stated basis — markup is profit ÷ cost; margin is profit ÷ revenue. State which basis you are using and show the conversion (20% markup ≠ 20% margin).")
  fi
fi

# 2. Hard-coded labor or material rate with no date.
#    Triggers on dollar-per-hour, dollar-per-unit, or dollar-per-ton patterns with no
#    adjacent date marker (common in estimates and CO pricing).
if grep -nEi "\\\$[0-9]+(\.[0-9]+)?[[:space:]]*(per|/)[[:space:]]*(hr|hour|lf|sf|cy|ton|each|ea|lb)\b" "$file" >/dev/null 2>&1; then
  if ! grep -qEi "(rate date|as of|effective [0-9]|[0-9]{4}[-/][0-9]{1,2}[-/][0-9]{1,2}|rs means [0-9]{4}|prevailing wage [0-9]{4}|quote dated)" "$file" 2>/dev/null; then
    findings+=("Unit rate or labor rate detected with no adjacent date or source. Labor and material rates age — note the effective date and source (prevailing-wage schedule, RS Means edition, or quote date) on every rate used.")
  fi
fi

# 3. Verbal change order — work started or described without written authorization.
#    Triggers on phrases indicating verbal direction or work preceding paperwork.
if grep -nEi "(verbal(ly)?|orally|told us to|said to|instructed us verbally|proceed.{0,30}without.{0,30}(change order|co|written)|work.{0,20}(before|without).{0,20}(change order|co|written|paperwork))" "$file" >/dev/null 2>&1; then
  findings+=("Verbal change order language detected — a verbal direction is not a change order. Obtain written authorization (email confirmation, signed PCO, or RFI response) before performing out-of-scope work.")
fi

# 4. Schedule with no critical path / a task with no logic tie.
#    Triggers on schedule or activity descriptions that lack predecessor/successor language,
#    or explicit statements that no critical path has been calculated.
if grep -nEi "(no critical path|no logic|no predecessor|no successor|floating activity|activities are independent|tasks are independent)" "$file" >/dev/null 2>&1; then
  findings+=("Schedule language suggests missing logic ties or no critical-path calculation. Every CPM activity needs a predecessor and a successor (except project start/finish milestones). A schedule without logic is a Gantt chart, not a CPM network.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── construction-general-contractor advisory: review before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${CONSTRUCTION_GC_STRICT:-0}" = "1" ]; then
  echo "(blocking: CONSTRUCTION_GC_STRICT=1)" >&2
  exit 2
fi
exit 0
