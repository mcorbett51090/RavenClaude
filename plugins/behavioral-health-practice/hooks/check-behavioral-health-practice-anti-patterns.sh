#!/usr/bin/env bash
# check-behavioral-health-practice-anti-patterns.sh — advisory PreToolUse hook for the behavioral-health-practice plugin.
# Flags mechanically-detectable behavioral-health anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set BH_STRICT=1 to make it blocking (exit 2).
# NOTE: heuristic only — it does NOT guarantee an artifact is PHI-free. The standard is no real PHI in artifacts;
# this hook catches the obvious leaks, not all of them.
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# 1. Plaintext PHI patterns — a bare SSN (NNN-NN-NNNN) or a date-of-birth label with a real-looking date.
#    PHI belongs in the EHR, never in a plugin artifact. Placeholders like [DOB] / [Client] are fine.
if grep -qE "\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b" "$file" 2>/dev/null; then
  findings+=("Possible plaintext SSN (NNN-NN-NNNN) — no real PHI in artifacts; use a placeholder like [SSN]/[Member ID].")
fi
if grep -qiE "\b(dob|date of birth)\b\s*[:=]?\s*[0-9]{1,4}[-/][0-9]{1,2}[-/][0-9]{1,4}" "$file" 2>/dev/null; then
  findings+=("Possible plaintext date-of-birth — no real PHI in artifacts; use the placeholder [DOB].")
fi

# 2. A disclosure / record-sharing doc with no reference to consent / ROI — consent precedes disclosure.
if grep -qiE "(disclos|release of information|\bROI\b|send (the )?records?|share (the )?records?)" "$file" 2>/dev/null; then
  if ! grep -qiE "(consent|authoriz|\bROI\b|release of information)" "$file" 2>/dev/null; then
    findings+=("Disclosure/record-sharing with no consent/ROI reference — consent precedes disclosure; verify the ROI before any record leaves.")
  fi
fi

# 3. A Part 2 / substance-use record context with no consent reference — Part 2 is stricter than HIPAA.
if grep -qiE "(42 ?CFR ?Part ?2|substance use|\bSUD\b)" "$file" 2>/dev/null; then
  if ! grep -qiE "(specific (written )?consent|part ?2 consent|consent)" "$file" 2>/dev/null; then
    findings+=("Part 2 / substance-use content with no specific-consent reference — SUD records need specific Part 2 consent; a general HIPAA authorization is not enough.")
  fi
fi

# 4. A doc that calls something "self-service" but still routes to a ticket queue — a faster queue, not self-service.
if grep -qiE "self[ -]?service" "$file" 2>/dev/null; then
  if grep -qiE "(open|file|raise|submit|create)\s+(a\s+)?(jira\s+)?ticket|service\s*now|ServiceNow" "$file" 2>/dev/null; then
    findings+=("'Self-service' that routes to a ticket — if a human must action every case, it's a queue, not self-service. Self-service the routine, escalate the exception.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── behavioral-health-practice advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${BH_STRICT:-0}" = "1" ]; then
  echo "(blocking: BH_STRICT=1)" >&2
  exit 2
fi
exit 0
