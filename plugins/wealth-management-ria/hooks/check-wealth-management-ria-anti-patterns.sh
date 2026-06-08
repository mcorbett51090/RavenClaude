#!/usr/bin/env bash
# check-wealth-management-ria-anti-patterns.sh — advisory PreToolUse hook for the wealth-management-ria plugin.
# Flags mechanically-detectable advisory anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set RIA_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# 1. A planning/portfolio output that reads like a personalized recommendation but has no
#    not-investment-advice disclaimer — the §0 / not-personalized-investment-advice rule.
if grep -qiE "(recommend|you should|buy|sell|allocate)\b" "$file" 2>/dev/null \
  && grep -qiE "(portfolio|allocation|withdrawal|retire|invest|fund|IRA|Roth|401)" "$file" 2>/dev/null; then
  if ! grep -qiE "not (personalized )?(investment|legal|tax)? ?advice|not a recommendation|educational" "$file" 2>/dev/null; then
    findings+=("Reads as a personalized recommendation with no not-investment-advice disclaimer — every advisory output must state it's educational/operational support, not a personalized recommendation.")
  fi
fi

# 2. An IPS / Investment Policy Statement draft with no rebalancing policy — the-ips-is-the-governing-document
#    / rebalancing-is-a-written-rule rules.
if grep -qiE "investment policy statement|\bIPS\b" "$file" 2>/dev/null; then
  if ! grep -qiE "rebalanc" "$file" 2>/dev/null; then
    findings+=("Investment Policy Statement with no rebalancing policy — an IPS must document a written rebalancing rule (calendar or threshold/bands), not leave it to discretion.")
  fi
fi

# 3. "Fiduciary" and "Reg BI" used as if interchangeable — the fiduciary-is-not-reg-bi rule.
if grep -qiE "fiduciary" "$file" 2>/dev/null && grep -qiE "reg(ulation)? ?bi\b|best.interest" "$file" 2>/dev/null; then
  if grep -qiE "fiduciary.{0,30}(=|is|same as|equivalent to|means).{0,30}(reg ?bi|best.interest)" "$file" 2>/dev/null \
    || grep -qiE "(reg ?bi|best.interest).{0,30}(=|is|same as|equivalent to|means).{0,30}fiduciary" "$file" 2>/dev/null; then
    findings+=("'Fiduciary' and 'Reg BI' treated as interchangeable — they are different standards (Advisers Act fiduciary duty vs broker-dealer best-interest). Name which applies; never conflate.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── wealth-management-ria advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${RIA_STRICT:-0}" = "1" ]; then
  echo "(blocking: RIA_STRICT=1)" >&2
  exit 2
fi
exit 0
