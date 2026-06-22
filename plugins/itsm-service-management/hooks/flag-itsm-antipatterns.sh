#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the itsm-service-management plugin.
# Flags common ITSM anti-patterns in generated deliverables against the §2 house
# opinions: an SLA with no OLA/underpinning-contract behind it, a major incident
# with no commander/comms, or an unsourced benchmark figure.
# Advisory by default — set ITSM_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${ITSM_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "itsm-service-management" "$1" >&2
  findings=$((findings + 1))
}

# §2 #4: an SLA mentioned with no OLA / underpinning contract backing it.
if grep -Eiq '\bSLA\b' "$FILE"; then
  if ! grep -Eiq '\b(OLA|underpinning contract|operational level agreement)\b' "$FILE"; then
    note "Advisory (§2 #4): an SLA appears with no OLA / underpinning contract behind it — every SLA must be backed end-to-end."
  fi
fi

# §2 #5: a major incident with no commander/comms role named.
if grep -Eiq '\bmajor incident\b' "$FILE"; then
  if ! grep -Eiq '\b(commander|comms lead|communications lead)\b' "$FILE"; then
    note "Advisory (§2 #5): a major incident appears with no commander/comms role — assign a commander + comms lead, not just engineers."
  fi
fi

# §2 #8 / placeholder smell.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: placeholder text present — review against the §2 house opinions before shipping (date+source every benchmark/SLA/tool figure)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "itsm-service-management: $findings advisory finding(s); ITSM_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
