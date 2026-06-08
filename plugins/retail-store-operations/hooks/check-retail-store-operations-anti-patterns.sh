#!/usr/bin/env bash
# check-retail-store-operations-anti-patterns.sh — advisory PreToolUse hook for the retail-store-operations plugin.
# Flags mechanically-detectable retail anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set RETAIL_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# 1. A core retail metric quoted with no formula/window — every metric is ambiguous without numerator/denominator/window.
if grep -qiE "sell[ -]?through|GMROI|weeks[ -]?of[ -]?supply|\bWOS\b" "$file" 2>/dev/null; then
  if ! grep -qiE "(÷|/|divided by|numerator|denominator|formula|per week|over .*(week|month|day)|window)" "$file" 2>/dev/null; then
    findings+=("A retail metric (sell-through / GMROI / weeks-of-supply) appears with no formula or window — state the numerator, denominator, and time window or it's undefendable.")
  fi
fi

# 2. A markdown recommendation with no sell-through / weeks-of-supply trigger — markdown is a decision, not a default.
if grep -qiE "mark[ -]?down|markdown|clearance" "$file" 2>/dev/null; then
  if ! grep -qiE "sell[ -]?through|weeks[ -]?of[ -]?supply|\bWOS\b|trigger|cadence" "$file" 2>/dev/null; then
    findings+=("A markdown/clearance with no sell-through or weeks-of-supply trigger — markdown is a decision, not a default. Tie it to a metric trigger and a cadence.")
  fi
fi

# 3. A "safety stock" / "buffer" change with no named service / in-stock level — that's trapped cash with a story.
if grep -qiE "safety[ -]?stock|buffer stock|\bbuffer\b" "$file" 2>/dev/null; then
  if ! grep -qiE "service[ -]?level|in[ -]?stock|fill[ -]?rate|[0-9]{2}\s*%" "$file" 2>/dev/null; then
    findings+=("'Safety stock' / 'buffer' with no named service / in-stock level — size it to a stated target or it's just trapped cash.")
  fi
fi

# 4. Inventory judged on raw on-hand units instead of flow (sell-through / weeks-of-supply / GMROI).
if grep -qiE "on[ -]?hand|units in stock|inventory (is|are|level)" "$file" 2>/dev/null; then
  if grep -qiE "(too (much|many|high|low)|over[ -]?stock|under[ -]?stock|enough (stock|inventory|units))" "$file" 2>/dev/null \
    && ! grep -qiE "sell[ -]?through|weeks[ -]?of[ -]?supply|\bWOS\b|GMROI|turns" "$file" 2>/dev/null; then
    findings+=("Inventory called over/under-stocked on raw on-hand units — normalize to weeks-of-supply / sell-through / GMROI; raw units don't tell you the flow.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── retail-store-operations advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${RETAIL_STRICT:-0}" = "1" ]; then
  echo "(blocking: RETAIL_STRICT=1)" >&2
  exit 2
fi
exit 0
