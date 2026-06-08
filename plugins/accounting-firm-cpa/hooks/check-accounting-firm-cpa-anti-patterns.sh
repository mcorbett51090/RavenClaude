#!/usr/bin/env bash
# check-accounting-firm-cpa-anti-patterns.sh — advisory PreToolUse hook for the
# accounting-firm-cpa plugin. Flags mechanically-detectable CPA-firm anti-patterns on
# Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice to stderr);
# set ACCOUNTING_FIRM_CPA_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect text-based files; skip binaries.
case "$file" in
*.md | *.yaml | *.yml | *.json | *.txt | *.py | *.sh | *.csv) ;;
*) exit 0 ;;
esac

findings=()

# 1. Attest engagement with an independence-impairing service noted side-by-side.
#    Flag: file mentions both an attest engagement type AND a management-function service
#    (signing checks, making decisions, controlling assets) for the same client context.
if grep -nEi "\b(audit|review engagement|attest)\b" "$file" >/dev/null 2>&1 && \
   grep -nEi "\b(sign(ing)? checks|make(s)? business decisions|control(s|ling)? assets|management function)\b" "$file" >/dev/null 2>&1; then
  findings+=("Attest engagement + management-function language detected in the same file. Management participation impairs independence with no available safeguard — verify these do not apply to the same client, or decline the attest engagement.")
fi

# 2. A number or dollar amount with no workpaper support reference.
#    Flag: dollar amounts in workpaper-like files (containing 'workpaper', 'tick mark', or
#    assertion language) that have no tick-mark legend reference (e.g., no 'per', 'agreed to',
#    'traced to', 'footed', or bracket reference like [C-1]).
if grep -nEi "(workpaper|tick.?mark|per client|audit area|assertion)" "$file" >/dev/null 2>&1 && \
   grep -nE "\\\$[0-9,]+" "$file" >/dev/null 2>&1 && \
   ! grep -nEi "(per |agreed to|traced to|footed|cross.?ref|\[.+-[0-9]+\])" "$file" >/dev/null 2>&1; then
  findings+=("Dollar amounts found in a workpaper-style file with no tick-mark or source reference (e.g., 'per bank statement', 'agreed to [C-1]', 'traced to vendor invoice'). Every workpaper number must have a documented source.")
fi

# 3. Client PII — SSN or EIN in plaintext.
#    Flag: SSN pattern (XXX-XX-XXXX) or EIN pattern (XX-XXXXXXX) as literal digits.
if grep -nE "\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b" "$file" >/dev/null 2>&1; then
  findings+=("SSN-pattern (XXX-XX-XXXX) detected in plaintext. Client SSNs must not be stored or transmitted in unencrypted plaintext files. Scrub or mask before including in any document or prompt.")
fi
if grep -nE "\b[0-9]{2}-[0-9]{7}\b" "$file" >/dev/null 2>&1; then
  findings+=("EIN-pattern (XX-XXXXXXX) detected in plaintext. Client EINs are sensitive PII. Verify this is intentional, encrypted, and access-controlled per the firm's data-security policy.")
fi

# 4. A fee or realization figure with no date or [verify-at-use] marker.
#    Flag: a dollar-per-hour rate or percentage realization figure in a pricing/strategy
#    context with no date, year, or verify-at-use annotation.
if grep -nEi "(realization rate|billing rate|standard rate|hourly rate|per hour)" "$file" >/dev/null 2>&1 && \
   ! grep -nEi "(\[verify.at.use\]|20[0-9]{2}|as of |dated)" "$file" >/dev/null 2>&1; then
  findings+=("Realization rate or billing rate figure found with no date or [verify-at-use] marker. Billing rates and realization benchmarks are volatile — tag with a retrieval date or [verify-at-use] so the figure is not treated as perpetually current.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── accounting-firm-cpa advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${ACCOUNTING_FIRM_CPA_STRICT:-0}" = "1" ]; then
  echo "(blocking: ACCOUNTING_FIRM_CPA_STRICT=1)" >&2
  exit 2
fi
exit 0
