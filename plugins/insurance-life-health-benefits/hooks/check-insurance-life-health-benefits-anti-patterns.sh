#!/usr/bin/env bash
# check-insurance-life-health-benefits-anti-patterns.sh — advisory PreToolUse hook for the
# insurance-life-health-benefits plugin. Flags mechanically-detectable benefits anti-patterns on
# Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice); set BENEFITS_STRICT=1 to make
# it blocking (exit 2). Educational scaffolding only — never legal, tax, or actuarial advice.
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# 1. Benefits content that reads as advice with no sign-off / not-advice framing — the cardinal rule.
if grep -qiE "(self-funded|fully-insured|level-funded|deductible|coinsurance|loss ratio|medical-loss|renewal|COBRA|ACA|ERISA|1095|5500)" "$file" 2>/dev/null; then
  if grep -qiE "\b(you should|we recommend|the right choice is|definitely (go|choose)|guaranteed)\b" "$file" 2>/dev/null; then
    if ! grep -qiE "(not (legal|tax|actuarial) advice|educational|sign[ -]?off|broker|actuary|ERISA counsel)" "$file" 2>/dev/null; then
      findings+=("Benefits recommendation phrased as advice with no 'not advice' framing / sign-off — frame trade-offs and name the broker / actuary / ERISA counsel who signs off.")
    fi
  fi
fi

# 2. An HDHP discussed with no HSA contribution mentioned — a likely cost-shift sold as a benefit.
if grep -qiE "\bHDHP\b|high[ -]deductible" "$file" 2>/dev/null; then
  if ! grep -qiE "\bHSA\b|health savings" "$file" 2>/dev/null; then
    findings+=("HDHP / high-deductible plan with no HSA mention — an HDHP without funded employer HSA contributions is a cost-shift, not a benefit. Pair it or say so.")
  fi
fi

# 3. A dated/regulatory figure quoted with no [verify-at-build] marker — these shift year to year.
if grep -qiE "(80%|85%|50[ -]?(FTE|full-time)|18 months|36 months|minimum value|affordability)" "$file" 2>/dev/null; then
  if ! grep -qiE "verify-at-build" "$file" 2>/dev/null; then
    findings+=("ACA/MLR/COBRA/5500 figure quoted with no [verify-at-build] marker — thresholds and deadlines are re-indexed annually; tag every quantitative figure for current-year re-check.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── insurance-life-health-benefits advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${BENEFITS_STRICT:-0}" = "1" ]; then
  echo "(blocking: BENEFITS_STRICT=1)" >&2
  exit 2
fi
exit 0
