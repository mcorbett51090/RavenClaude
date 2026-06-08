#!/usr/bin/env bash
# check-construction-field-management-anti-patterns.sh — advisory PreToolUse hook for the construction-field-management plugin.
# Flags mechanically-detectable field anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set CONSTRUCTION_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# 1. An RFI / submittal / change log that references ball-in-court tracking but has no owner or no date.
if grep -qiE "(^|\s)(rfi|submittal|change[ -]?order|pco|cor)\b" "$file" 2>/dev/null \
  && grep -qiE "ball[ -]?in[ -]?court" "$file" 2>/dev/null; then
  if ! grep -qiE "ball[ -]?in[ -]?court:\s*\S" "$file" 2>/dev/null \
    && ! grep -qiE "(needed[ -]?by|required[ -]?by|date\s+(sent|returned|due))" "$file" 2>/dev/null; then
    findings+=("RFI/submittal/change log mentions ball-in-court but has no owner value and no date field — every open item needs one party and a due date, or it's a stall.")
  fi
fi

# 2. A pay application / schedule of values with no retainage line — retainage is held, not lost.
if grep -qiE "(pay\s*app(lication)?|g70[23]|schedule\s+of\s+values|\bSOV\b)" "$file" 2>/dev/null; then
  if ! grep -qiE "retainage|retention" "$file" 2>/dev/null; then
    findings+=("Pay app / SOV with no retainage line — retainage is a withheld balance that releases at completion; compute and track it explicitly.")
  fi
fi

# 3. A JHA / toolbox talk that names hazards but no control — a hazard list with no mitigation isn't a plan.
if grep -qiE "(\bJHA\b|\bJSA\b|job[ -]hazard|toolbox\s+talk)" "$file" 2>/dev/null; then
  if grep -qiE "hazard" "$file" 2>/dev/null && ! grep -qiE "control|mitigation|ppe|fall\s+protection|lockout|tagout|\bLOTO\b" "$file" 2>/dev/null; then
    findings+=("JHA/toolbox talk lists hazards but names no control — every hazard needs the specific control for the task (OSHA is the floor).")
  fi
fi

# 4. A punch list with items but no responsible trade / no assignment — a punch list with no owner never reaches zero.
if grep -qiE "punch\s*(list|item)" "$file" 2>/dev/null; then
  if ! grep -qiE "(responsible\s+(trade|party)|assigned\s+to|trade:|owner:)" "$file" 2>/dev/null; then
    findings+=("Punch list with no responsible-trade / assignment field — assign each item a trade, location, and date or it never reaches zero.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── construction-field-management advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${CONSTRUCTION_STRICT:-0}" = "1" ]; then
  echo "(blocking: CONSTRUCTION_STRICT=1)" >&2
  exit 2
fi
exit 0
