#!/usr/bin/env bash
# check-hospitality-hotels-anti-patterns.sh — advisory PreToolUse hook for the
# hospitality-hotels plugin. Flags mechanically-detectable hotel revenue anti-patterns
# on Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice to stderr);
# set HOSPITALITY_HOTELS_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect text-ish files; skip binaries and non-relevant types.
case "$file" in
*.md | *.yaml | *.yml | *.json | *.txt | *.py | *.sh) ;;
*) exit 0 ;;
esac

findings=()

# 1. Rate set with no RevPAR or demand basis.
# Detects: a BAR/rate/pricing recommendation without any of: revpar, oTB, occupancy, demand,
# pick-up, pace, comp-set, comp set. Looks for "set.*rate" or "BAR" or "pricing" adjacent to
# a missing demand signal.
if grep -nEi "\b(set|raise|increase|lower|decrease|change|update)\s+(the\s+)?(bar|rate|pricing|room\s+rate|best\s+available)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(revpar|rev_par|on.the.books|otb|occupancy|demand|pick.?up|pace|comp.?set|comp set|forecast)\b" "$file" >/dev/null 2>&1; then
    findings+=("Rate change with no demand basis — a BAR/rate recommendation requires at least one: OTB pace, RevPAR context, comp-set position, or demand-calendar signal. Add the demand evidence before finalizing.")
  fi
fi

# 2. OTA channel referenced with no net-ADR or commission note.
# Detects: OTA channel (Booking.com, Expedia, or generic "OTA") mentioned without any
# commission, net ADR, or distribution cost reference.
if grep -nEi "\b(booking\.com|expedia|ota\s+channel|online\s+travel\s+agent)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(commission|net.?adr|distribution\s+cost|tdc|net\s+rate|net\s+revenue|after\s+(commission|fee))\b" "$file" >/dev/null 2>&1; then
    findings+=("OTA channel referenced with no net-ADR or commission note — every OTA channel discussion must include the commission rate or net ADR. Gross ADR without distribution cost is an incomplete figure.")
  fi
fi

# 3. Hard-coded occupancy or ADR figure with no date or source context.
# Detects: a bare numeric occupancy percentage (e.g. "occupancy of 78%") or ADR dollar
# (e.g. "ADR of $185") with no surrounding date, year, period, or source qualifier.
if grep -nEi "(occupancy\s+(of\s+|at\s+|is\s+|:?\s*)[0-9]{1,3}%|adr\s+(of\s+|at\s+|is\s+|:?\s*)\$?[0-9]{2,4})" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(20[0-9]{2}|q[1-4]|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|ytd|mtd|last\s+(year|month|quarter|week)|period|forecast|budget|actual|str\b|verify.at.use)\b" "$file" >/dev/null 2>&1; then
    findings+=("Hard-coded occupancy or ADR figure with no date or period qualifier — a bare occupancy % or ADR \$ with no time context is ambiguous (is it actual, forecast, budget, or a benchmark?). Add a date, period, or source qualifier.")
  fi
fi

# 4. Overbooking policy or level with no no-show or walk basis.
# Detects: "overbook" or "overbooking" mentioned without any of: no-show, no show,
# cancellation, walk cost, walk rate, cancel rate.
if grep -nEi "\b(overbook(ing)?|over\s+book(ing)?)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(no.?show|cancell?ation|walk\s+(cost|rate|risk)|cancel\s+rate|walked\s+guest)\b" "$file" >/dev/null 2>&1; then
    findings+=("Overbooking policy or level with no no-show or walk basis — an overbooking recommendation requires: 12-month no-show rate, cancellation rate, and a walk-cost model. Without these, the policy is a guess. Add the data basis or flag it as requiring historical data before implementation.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── hospitality-hotels advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${HOSPITALITY_HOTELS_STRICT:-0}" = "1" ]; then
  echo "(blocking: HOSPITALITY_HOTELS_STRICT=1)" >&2
  exit 2
fi
exit 0
