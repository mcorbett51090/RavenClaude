#!/usr/bin/env bash
# check-property-management-residential-anti-patterns.sh — advisory PreToolUse hook for the
# property-management-residential plugin. Flags mechanically-detectable anti-patterns on
# Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice to stderr);
# set PM_RESIDENTIAL_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect text / markdown / config files; skip binaries and scripts.
case "$file" in
*.md | *.txt | *.yaml | *.yml | *.json | *.html | *.csv) ;;
*) exit 0 ;;
esac

findings=()

# 1. Fair-housing risky listing language — implied preference or exclusion for a protected class.
#    Checks for common phrases that indicate familial status, age, religion, or national-origin bias.
if grep -nEi "\bno kids\b|\bno children\b" "$file" >/dev/null 2>&1; then
  findings+=("Fair-housing: 'no kids' / 'no children' — familial status exclusion language. Use 'no pets' if pets are the concern; a legal senior-housing exemption is required to restrict children.")
fi

if grep -nEi "(perfect|ideal|great|designed)\s+for\s+(a\s+)?(single\s+professional|young\s+(couple|professional)|empty\s+nester|retired|senior|college\s+student|family|couples)" "$file" >/dev/null 2>&1; then
  findings+=("Fair-housing: 'perfect/ideal for [resident type]' implies a preferred resident profile. Describe the unit, not the ideal tenant.")
fi

if grep -nEi "\b(familial|religion(s|ous)?|national[- ]origin|congregation|mosque|church|synagogue|temple)\b.{0,60}(ideal|perfect|great|close)" "$file" >/dev/null 2>&1; then
  findings+=("Fair-housing: listing references a religious institution or national-origin/familial context near preference language. Review with pm-compliance-advisor before publishing.")
fi

if grep -nEi "\badults[- ]only\b|\bmature\s+community\b|\b55\+\b|\bno\s+minors\b" "$file" >/dev/null 2>&1; then
  findings+=("Fair-housing: age-restriction language detected. Lawful senior housing exemptions (HOPA) have strict requirements — verify the property qualifies before using this language.")
fi

# 2. Plaintext tenant PII — SSN pattern.
if grep -nE "\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b" "$file" >/dev/null 2>&1; then
  findings+=("Tenant PII: SSN-shaped value detected (###-##-####). Social Security numbers must be collected and stored in the PM software, never in plaintext files, email, or notes.")
fi

# 3. Screening decision without a consistent-criteria note.
#    Heuristic: a file whose name or content suggests a screening decision, but lacks any reference
#    to the written criteria or policy applied.
if grep -nEi "(applicant|application).{0,40}(denied|approved|rejected|declined)" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "(criteria|policy|standard|income multiple|credit score|consistent)" "$file" >/dev/null 2>&1; then
    findings+=("Screening: approval/denial language found but no reference to written screening criteria or policy. Document which criterion was met or not met to support a consistent-application defense.")
  fi
fi

# 4. Work order without an SLA / priority tier.
#    Heuristic: a file that mentions a work order but has no priority tier or SLA language.
if grep -nEi "(work[- ]order|maintenance\s+request|repair\s+request)" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "(emergency|urgent|routine|priority|sla|response\s+time|resolution\s+time|hours?|days?)" "$file" >/dev/null 2>&1; then
    findings+=("Work order: maintenance request language found but no priority tier or SLA language detected. Every work order must be assigned Emergency/Urgent/Routine with a committed response time.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── property-management-residential advisory: review before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${PM_RESIDENTIAL_STRICT:-0}" = "1" ]; then
  echo "(blocking: PM_RESIDENTIAL_STRICT=1)" >&2
  exit 2
fi
exit 0
