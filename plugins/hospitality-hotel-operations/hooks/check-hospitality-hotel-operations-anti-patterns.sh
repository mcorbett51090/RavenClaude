#!/usr/bin/env bash
# check-hospitality-hotel-operations-anti-patterns.sh — advisory PreToolUse hook for the hospitality-hotel-operations plugin.
# Flags mechanically-detectable hospitality anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set HOTEL_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# 1. Optimizing occupancy / ADR with no RevPAR mention — the §4 #1 RevPAR-first rule.
if grep -qiE "occupancy|\bADR\b|average daily rate" "$file" 2>/dev/null; then
  if ! grep -qiE "RevPAR|revenue per available room" "$file" 2>/dev/null; then
    findings+=("Occupancy/ADR discussed with no RevPAR — optimize RevPAR (read against GOPPAR), never occupancy or ADR alone.")
  fi
fi

# 2. Comparing channels / OTA on rate with no net-ADR / commission accounting.
if grep -qiE "\bOTA\b|booking\.com|expedia|channel mix|distribution" "$file" 2>/dev/null; then
  if ! grep -qiE "net ADR|commission|distribution cost|net-adr|contribution" "$file" 2>/dev/null; then
    findings+=("Channel/OTA discussed with no net-ADR/commission accounting — compare channels on net ADR after distribution cost, not gross rate.")
  fi
fi

# 3. Overbooking with no walk-protocol — the §4 #7 don't-oversell-the-guarantee rule.
if grep -qiE "overbook|oversell" "$file" 2>/dev/null; then
  if ! grep -qiE "walk[ -]?protocol|walk the guest|walk-cost|re-accommodat|no[ -]?show rate" "$file" 2>/dev/null; then
    findings+=("Overbooking with no walk-protocol / no-show rate — overbook only to a forecasted no-show rate, with an owned walk-protocol.")
  fi
fi

# 4. Loyalty measured by member/enrollment count — the §4 #8 repeat-economics rule.
if grep -qiE "loyalty|members? enrolled|enrolled members?|member count|sign[ -]?ups?" "$file" 2>/dev/null; then
  if grep -qiE "member count|enrolled members?|members? enrolled|number of members|sign[ -]?up count" "$file" 2>/dev/null; then
    if ! grep -qiE "repeat rate|direct[ -]?booking share|CLV|customer lifetime value|repeat business" "$file" 2>/dev/null; then
      findings+=("Loyalty measured by member/enrollment count — measure repeat rate / direct share / CLV, never enrolled-member count.")
    fi
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── hospitality-hotel-operations advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${HOTEL_STRICT:-0}" = "1" ]; then
  echo "(blocking: HOTEL_STRICT=1)" >&2
  exit 2
fi
exit 0
