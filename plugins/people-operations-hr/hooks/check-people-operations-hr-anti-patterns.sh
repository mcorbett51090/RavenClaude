#!/usr/bin/env bash
# check-people-operations-hr-anti-patterns.sh — advisory PreToolUse hook for the
# people-operations-hr plugin. Flags mechanically-detectable HR anti-patterns on
# Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice);
# set PEOPLE_OPS_HR_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect text-based files; skip binaries.
case "$file" in
*.md | *.yaml | *.yml | *.json | *.txt | *.csv) ;;
*) exit 0 ;;
esac

findings=()

# 1. Biased / exclusionary job-description language.
# Flags: rockstar, ninja, guru (as role descriptors), "young" or "young and", gendered
# diminutives, and "culture fit" used as a sole or primary criterion.
if grep -nEi "\b(rockstar|ninja|guru)\b" "$file" >/dev/null 2>&1; then
  findings+=("Exclusionary JD language: 'rockstar', 'ninja', or 'guru' — these terms signal in-group culture and deter underrepresented candidates. Use specific skill or competency language instead.")
fi

if grep -nEi "\byoung\b.{0,30}(and |energy|talent|hunger|hungry|enthusiast|dynamic)" "$file" >/dev/null 2>&1; then
  findings+=("Age-coded JD language: 'young' combined with descriptor terms — this may constitute age discrimination. Replace with the specific energy, pace, or skill being sought.")
fi

if grep -nEi "culture fit" "$file" >/dev/null 2>&1 && ! grep -nEi "(one of|among|in addition to|alongside|example)" "$file" >/dev/null 2>&1; then
  findings+=("'Culture fit' appears as a standalone criterion — without a behavioral definition it is a bias amplifier. Define the specific observable behaviors expected, or remove.")
fi

# Gendered terms commonly flagged in JD bias audits.
if grep -nEi "\b(aggressive(ly)?|dominate|dominant|competitive drive|strong man|man up|man-hours)\b" "$file" >/dev/null 2>&1; then
  findings+=("Gendered / exclusionary language detected — terms like 'aggressive', 'dominant', 'man-hours' skew applicant pools. Rewrite with gender-neutral, behavior-specific language.")
fi

# 2. Plaintext PII — SSN-shaped pattern.
if grep -nEi "\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b" "$file" >/dev/null 2>&1; then
  findings+=("Possible plaintext SSN pattern (XXX-XX-XXXX) detected — Social Security Numbers must never appear in Markdown, text files, or shared documents. Remove and store in encrypted HRIS only.")
fi

# 3. Comp figure with no band or date — a salary figure standing alone.
# Heuristic: a dollar sign followed by digits (e.g. $120,000 or $120k) with no nearby
# "band", "range", "minimum", "maximum", "midpoint", or effective date within 200 chars.
if grep -nEi '\$[0-9]{2,3}[,k]' "$file" >/dev/null 2>&1; then
  if ! grep -nEi "(band|range|minimum|maximum|midpoint|p[0-9]{2}|percentile|effective|as of|survey)" "$file" >/dev/null 2>&1; then
    findings+=("Comp figure(s) detected without a band anchor, range, or effective date — a salary figure without a band is a negotiation, not a framework. Add the band reference or an effective date and market source.")
  fi
fi

# 4. Interview file without a structured scorecard reference.
# A file with "interview" in the name or that contains interview-stage content but
# has no "scorecard" or "competency" reference is flagged.
case "$file" in
*interview* | *Interview*)
  if ! grep -nEi "(scorecard|competency|rubric|rating|must.have|nice.to.have)" "$file" >/dev/null 2>&1; then
    findings+=("Interview file with no scorecard or competency reference — every interview stage must have a structured scorecard with rubric anchors. Add a scorecard or reference ../templates/interview-scorecard.md.")
  fi
  ;;
esac

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── people-operations-hr advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${PEOPLE_OPS_HR_STRICT:-0}" = "1" ]; then
  echo "(blocking: PEOPLE_OPS_HR_STRICT=1)" >&2
  exit 2
fi
exit 0
