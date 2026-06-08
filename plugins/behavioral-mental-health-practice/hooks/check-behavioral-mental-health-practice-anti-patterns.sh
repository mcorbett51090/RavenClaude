#!/usr/bin/env bash
# check-behavioral-mental-health-practice-anti-patterns.sh — advisory PreToolUse hook for the
# behavioral-mental-health-practice plugin. Flags mechanically-detectable behavioral-health
# documentation anti-patterns on Edit/Write/MultiEdit. Advisory by default (exit 0, prints a
# notice); set BH_PRACTICE_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect text files that could contain patient/clinical documentation.
case "$file" in
*.md | *.txt | *.yaml | *.yml | *.json | *.csv) ;;
*) exit 0 ;;
esac

findings=()

# 1. Plaintext SSN pattern (NNN-NN-NNNN) — PHI exposure risk.
if grep -nEi "\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b" "$file" >/dev/null 2>&1; then
  findings+=("Possible plaintext SSN detected (NNN-NN-NNNN pattern) — PHI must not appear in clear text in documentation files. Scrub before committing. See best-practices/protect-phi-and-part-2-records.md.")
fi

# 2. Diagnosis tied to a name pattern — PHI disclosure risk.
# Heuristic: a capitalized name-like string followed closely by a DSM/ICD diagnosis term.
if grep -nEi "(Mr\.|Ms\.|Mrs\.|Dr\.|patient)\s+[A-Z][a-z]+.{0,60}(depression|anxiety|PTSD|bipolar|schizophrenia|substance use disorder|SUD|OCD|ADHD|BPD|MDD|GAD)" "$file" >/dev/null 2>&1; then
  findings+=("Possible diagnosis tied to a patient name — PHI minimum-necessary risk. Remove identifying information or confirm this is within a secured clinical record context. See best-practices/protect-phi-and-part-2-records.md.")
fi

# 3. Disclosure language without a Part 2 consent note.
# Heuristic: a file that mentions disclosing records but lacks any reference to Part 2 consent.
if grep -nEi "\b(disclose|disclosure|release of information|ROI|share records|send records)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "(part 2|42 cfr|part two|consent to disclose|written consent|prohibited re-disclosure)" "$file" >/dev/null 2>&1; then
    findings+=("Disclosure language present without a 42 CFR Part 2 consent reference — if SUD records may be involved, a specific Part 2 written consent is required before disclosure. HIPAA TPO does not apply to Part 2 records. See best-practices/42-cfr-part-2-is-stricter-than-hipaa.md.")
  fi
fi

# 4. Service/session description without a medical-necessity note.
# Heuristic: a file mentioning a billed session or treatment plan without any medical-necessity language.
if grep -nEi "\b(treatment plan|progress note|session note|individual therapy|group therapy|90837|90834|90832|90847|90853|90791|90792)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "(medical necessity|medically necessary|functional impairment|clinical necessity)" "$file" >/dev/null 2>&1; then
    findings+=("Session/service or treatment-plan content present without a medical-necessity reference — every billable service requires documented medical necessity. See best-practices/document-medical-necessity-for-every-service.md.")
  fi
fi

# 5. Telehealth content without a patient-state licensure note.
# Heuristic: a file mentioning telehealth without any licensure cross-check reference.
if grep -nEi "\b(telehealth|tele-health|video session|virtual session|remote session)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "(licensed in|state licensure|patient.{0,20}state|patient.{0,20}location|compact|PSYPACT)" "$file" >/dev/null 2>&1; then
    findings+=("Telehealth content present without a patient-state licensure reference — the clinician must be licensed in the state where the patient is physically located at time of service. See best-practices/telehealth-follows-the-patients-state-licensure.md.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── behavioral-mental-health-practice advisory: review before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${BH_PRACTICE_STRICT:-0}" = "1" ]; then
  echo "(blocking: BH_PRACTICE_STRICT=1)" >&2
  exit 2
fi
exit 0
