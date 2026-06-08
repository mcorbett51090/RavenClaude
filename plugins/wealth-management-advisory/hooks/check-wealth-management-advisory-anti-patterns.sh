#!/usr/bin/env bash
# check-wealth-management-advisory-anti-patterns.sh — advisory PreToolUse hook for the
# wealth-management-advisory plugin. Flags mechanically-detectable advisory anti-patterns
# on Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice to stderr);
# set WEALTH_ADVISORY_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect text-based files; skip binaries.
case "$file" in
*.md | *.yaml | *.yml | *.json | *.txt | *.html) ;;
*) exit 0 ;;
esac

findings=()

# 1. Language guaranteeing or implying a return — absolute prohibition.
#    Catches: "guaranteed return", "can't lose", "risk-free", "guaranteed income",
#    "you won't lose", "no risk", "safe investment" (as a blanket claim).
if grep -nEi "\b(guaranteed?\s+(return|income|profit|gain|interest|rate)|can'?t\s+lose|risk.?free\s+(investment|return|option)|you\s+won'?t\s+lose|no\s+risk\s+(investment|here|at\s+all)|this\s+is\s+(safe|as\s+safe\s+as)|virtually\s+no\s+risk)\b" "$file" >/dev/null 2>&1; then
  findings+=("Guarantee or implied-return language detected — this violates the 'never-guarantee-or-imply-a-return' absolute rule and may constitute a misrepresentation under the Advisers Act §206 and FINRA Rule 2210. Replace with range language + the mandatory past-performance disclosure.")
fi

# 2. Plaintext client PII — SSN pattern or account-number-shaped patterns.
#    Catches: SSN (NNN-NN-NNNN), 9-digit account numbers, 16-digit card numbers.
if grep -nE "\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b" "$file" >/dev/null 2>&1; then
  findings+=("Possible Social Security Number (NNN-NN-NNNN pattern) detected in plaintext. Strip or mask client SSNs before including in any document. Route PII-handling to ravenclaude-core/security-reviewer.")
fi
if grep -nE "\b[0-9]{8,12}\b" "$file" >/dev/null 2>&1 && grep -nEi "(account\s*(number|no\.?|#)|acct\.?\s*(no\.?|#|number))" "$file" >/dev/null 2>&1; then
  findings+=("Possible account number adjacent to an 'account number' label detected. Mask account numbers (e.g., '...1234') before including in any document that may be shared or stored outside a secure system.")
fi

# 3. A recommendation block with no suitability or rationale note.
#    Catches: files containing "recommend" language but no "suitability" or "rationale" or "best interest".
if grep -nEi "\b(recommend(ation|ed|s|ing)?|we\s+suggest|advise\s+(you\s+to|the\s+client))\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(suitability|rationale|best\s+interest|client'?s?\s+(objective|goal|situation|profile)|reason\s+for|because|why\s+(this|we))\b" "$file" >/dev/null 2>&1; then
    findings+=("Recommendation language detected without a suitability, rationale, or best-interest note. Every recommendation must document the client's situation and why this recommendation is in their best interest (Reg BI care obligation; document-the-recommendation-rationale absolute rule).")
  fi
fi

# 4. A performance claim with no past-performance disclosure or date.
#    Catches: files referencing historical returns (%, YTD, annualized) without a disclosure line.
if grep -nEi "\b(returned?|return\s+of|performance\s+of|ytd|year.to.date|annualized|historical(ly)?)\b.{0,60}[0-9]+(\.[0-9]+)?\s*%" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "(past\s+performance|does\s+not\s+guarantee|prior\s+performance|historical\s+performance\s+is\s+not)" "$file" >/dev/null 2>&1; then
    findings+=("Performance figure (% with return/YTD/annualized language) detected without a past-performance disclosure. Add: 'Past performance does not guarantee future results.' Every historical return reference requires this disclosure.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── wealth-management-advisory advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${WEALTH_ADVISORY_STRICT:-0}" = "1" ]; then
  echo "(blocking: WEALTH_ADVISORY_STRICT=1)" >&2
  exit 2
fi
exit 0
