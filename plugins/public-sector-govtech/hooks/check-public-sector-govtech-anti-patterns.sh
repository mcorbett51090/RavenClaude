#!/usr/bin/env bash
# check-public-sector-govtech-anti-patterns.sh — advisory PreToolUse hook for the
# public-sector-govtech plugin. Flags mechanically-detectable govtech anti-patterns on
# Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice);
# set GOVTECH_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect text-format files; skip binaries.
case "$file" in
*.md | *.yaml | *.yml | *.json | *.txt | *.html | *.htm) ;;
*) exit 0 ;;
esac

findings=()

# 1. RFP / proposal file missing a mandatory/required section marker.
#    A proposal file (matching rfp, proposal, response, solicitation in the filename or path)
#    that contains "shall" or "must" language (SOW requirements) but has no compliance matrix
#    or mandatory-requirement annotation is a risk.
case "$file" in
*rfp* | *proposal* | *response* | *solicitation* | *RFP* | *Proposal*)
  if grep -nEi "\b(shall|must)\b" "$file" >/dev/null 2>&1 && \
     ! grep -nEi "(compliance matrix|mandatory requirement|shall.*met|must.*met|section [lL]|[Mm]andatory)" "$file" >/dev/null 2>&1; then
    findings+=("RFP/proposal file contains 'shall/must' language but no compliance matrix or mandatory-requirement annotation. Build the compliance matrix before drafting prose — an unresolved mandatory requirement disqualifies the proposal.")
  fi
  ;;
esac

# 2. UI or document file with no 508/accessibility note.
#    A UI spec, design doc, or deliverable document with no mention of 508, WCAG, or accessibility.
case "$file" in
*ui* | *design* | *spec* | *deliverable* | *UI* | *Design* | *Spec* | *Deliverable* | *wireframe* | *mockup*)
  if ! grep -nEi "(508|wcag|accessibility|a11y|screen.?reader|alt.?text)" "$file" >/dev/null 2>&1; then
    findings+=("UI/design/deliverable file with no Section 508 or WCAG accessibility note. Every federal ICT deliverable requires 508 conformance — add an accessibility section or a VPAT reference.")
  fi
  ;;
esac

# 3. Grant-related file with no restriction/tracking note.
#    A grant budget, spending, or financial file with no mention of restricted funds or allowability.
case "$file" in
*grant* | *award* | *budget* | *expenditure* | *drawdown* | *Grant* | *Award* | *Budget*)
  if grep -nEi "\$[0-9]" "$file" >/dev/null 2>&1 && \
     ! grep -nEi "(restricted|allowabl|2 cfr 200|uniform guidance|object.?class|unallowable|prior approval)" "$file" >/dev/null 2>&1; then
    findings+=("Grant/award/budget file contains dollar amounts but no restriction, allowability, or Uniform Guidance (2 CFR 200) reference. Grant funds are restricted — document the allowability basis for every expenditure.")
  fi
  ;;
esac

# 4. Citizen-facing document with jargon patterns where plain language is required.
#    Flags common government jargon phrases in files likely to be citizen-facing.
case "$file" in
*notice* | *letter* | *citizen* | *public* | *benefit* | *form* | *guidance* | *Notice* | *Letter* | *Public* | *Benefit* | *Form* | *Guidance*)
  if grep -nEi "\b(utilize|aforementioned|hereinafter|pursuant to|notwithstanding|in accordance with|shall be required to)\b" "$file" >/dev/null 2>&1; then
    findings+=("Citizen-facing document contains bureaucratic jargon (utilize/aforementioned/hereinafter/pursuant to/notwithstanding). The Plain Writing Act requires plain language in public-facing federal documents — replace with common words (use / as mentioned / from now on / under / despite / consistent with / must).")
  fi
  ;;
esac

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── public-sector-govtech advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${GOVTECH_STRICT:-0}" = "1" ]; then
  echo "(blocking: GOVTECH_STRICT=1)" >&2
  exit 2
fi
exit 0
