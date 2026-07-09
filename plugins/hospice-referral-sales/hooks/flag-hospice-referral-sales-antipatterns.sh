#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the hospice-referral-sales plugin.
# Flags the three highest-consequence anti-patterns in a generated deliverable:
#   1. an eligibility/coverage GUARANTEE by the rep (the physician certifies),
#   2. a possible un-cleared value exchange to a referral source (anti-kickback),
#   3. possible PHI (patient-identifying data) in the deliverable (HIPAA).
# Advisory by default — set HOSPICE_REFERRAL_SALES_STRICT=1 to make it blocking.
# It NEVER edits the file; it only prints advisory notes to stderr.

FILE="${1:-}"
# $CLAUDE_TOOL_FILE_PATH (passed as $1 by hooks.json) is NOT a real Claude Code
# hook variable, so under Claude Code the arg is empty and the path arrives via
# the canonical stdin JSON contract. Fall back to it (2026-07-09 review) — the
# same dual-source pattern guard-destructive.sh / the core file hooks use.
if [ -z "$FILE" ] && [ ! -t 0 ] && command -v jq >/dev/null 2>&1; then
  payload="$(cat 2>/dev/null || true)"
  if [ -n "$payload" ]; then
    FILE="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)"
  fi
fi
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${HOSPICE_REFERRAL_SALES_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "hospice-referral-sales" "$1" >&2
  findings=$((findings + 1))
}

# 1. Eligibility / coverage guarantee language (the rep educates; the physician certifies).
if grep -Eiq 'qualif(y|ies|ied) for hospice|is eligible for hospice|guarantee(d)? (admission|coverage|eligibility)|will be covered|definitely (eligible|covered)' "$FILE"; then
  note "Possible eligibility/coverage GUARANTEE — the rep educates; the attending physician and medical director certify. Reword to 'indicators present; route to physician'. (best-practices/the-rep-educates-eligibility-the-physician-certifies-it.md)"
fi

# 2. Possible un-cleared value exchange toward a referral source (anti-kickback).
if grep -Eiq 'gift card|cash (gift|incentive)|free (staff|service|staffing)|sponsor(ship)?|comp(ed)? (lunch|meal|dinner)|in exchange for (referral|referring)' "$FILE"; then
  note "Possible value-exchange toward a referral source — route to the compliance officer and run the anti-kickback gate BEFORE acting; no cash/cash-equivalents, nothing volume-based. (best-practices/every-referral-source-arrangement-must-clear-anti-kickback.md)"
fi

# 3. Possible PHI — a date-of-birth / MRN shape. Conservative; advisory only.
if grep -Eiq '\b(dob|m\.?r\.?n\.?|medical record (number|no))\b|\b[0-1]?[0-9]/[0-3]?[0-9]/(19|20)[0-9]{2}\b' "$FILE"; then
  note "Possible PHI (a DOB/MRN shape) — deliverables carry NO patient-identifying data; use counts and rates, de-identify examples. (best-practices/protect-phi-at-every-step.md)"
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "hospice-referral-sales: $findings advisory finding(s); HOSPICE_REFERRAL_SALES_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
