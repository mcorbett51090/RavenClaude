#!/usr/bin/env bash
# check-automotive-dealership-anti-patterns.sh — advisory PreToolUse hook for the
# automotive-dealership plugin. Flags mechanically-detectable dealership anti-patterns
# on Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice to stderr);
# set AUTOMOTIVE_DEALERSHIP_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect text-format files; skip binaries.
case "$file" in
*.md | *.yaml | *.yml | *.json | *.txt | *.csv | *.html) ;;
*) exit 0 ;;
esac

findings=()

# 1. Payment packing — F&I product bundled into a payment without disclosure.
#    Looks for patterns like "$299/mo includes VSC" or "payment includes GAP"
#    or "includes [product] in the payment" without an explicit disclosure note.
if grep -nEi "(payment|monthly).{0,40}(includes?|bundle|pack).{0,40}(vsc|gap|warranty|protection|maintenance)" "$file" >/dev/null 2>&1; then
  findings+=("Possible payment packing: a quoted payment that appears to include an F&I product. Every F&I product must be disclosed separately with its individual price. Payment packing is an FTC Act § 5 violation — rephrase with full product disclosure on a separate menu line.")
fi

# 2. Undisclosed F&I product in a payment — "per month" combined with F&I product name
#    without an explicit "disclosed" or "menu" context nearby.
if grep -nEi "\\\$[0-9]+[[:space:]]*(per month|\/mo|\/month)" "$file" >/dev/null 2>&1 && \
   grep -nEi "\b(vsc|vehicle service contract|gap|gap waiver|maintenance agreement|tire.wheel|appearance protection)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "(menu|disclosed|individual price|separately|product price)" "$file" >/dev/null 2>&1; then
    findings+=("A payment figure and an F&I product name appear in the same file without disclosure language. Verify that the product is presented on a fully-disclosed menu with its individual price — not bundled into the payment.")
  fi
fi

# 3. Plaintext customer NPI — SSN pattern, full account/card number shape.
if grep -nEi "\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b" "$file" >/dev/null 2>&1; then
  findings+=("Possible plaintext SSN detected (pattern: NNN-NN-NNNN). Customer NPI must not be stored in plaintext files. GLBA Safeguards Rule requires encryption at rest. Remove or encrypt immediately.")
fi

# Full credit/debit card number pattern (13–16 digits, optionally grouped)
if grep -nEi "\b([0-9]{4}[[:space:]-]?){3}[0-9]{4}\b" "$file" >/dev/null 2>&1; then
  findings+=("Possible plaintext payment card number detected. Customer financial account data must not be stored in plaintext. Remove or encrypt per GLBA Safeguards Rule requirements.")
fi

# 4. Rate or PVR figure with no date — a rate or PVR benchmark stated without a
#    retrieval date or [verify-at-use] marker.
if grep -nEi "\b(average pvr|pvr benchmark|typical pvr|industry pvr|average apr|floor.?plan rate|prime rate)" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "(verify.at.use|\[verify\]|as of [0-9]{4}|retrieved [0-9]{4}|source:|benchmark.*\[)" "$file" >/dev/null 2>&1; then
    findings+=("A rate or PVR benchmark figure appears without a retrieval date or [verify-at-use] marker. Market rates and PVR benchmarks are volatile — add a date and a [verify-at-use] note so the figure is not treated as current.")
  fi
fi

# 5. Advertised price with no required-disclosure note — an ad-style payment quote
#    without any APR / term / down-payment disclosure language (TILA/Reg Z trigger terms).
if grep -nEi "^\$[0-9]+(\/mo|/month| per month)" "$file" >/dev/null 2>&1 || \
   grep -nEi "^(advertised|sale price|special offer|as low as).{0,20}\$[0-9]+" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "(apr|annual percentage rate|down payment|term|months|financing)" "$file" >/dev/null 2>&1; then
    findings+=("An advertised payment or price appears without required TILA/Reg Z disclosure terms (APR, down payment, term). If a payment is a trigger term in an ad, all required disclosures must accompany it. Review with dealership-compliance-advisor.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── automotive-dealership advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${AUTOMOTIVE_DEALERSHIP_STRICT:-0}" = "1" ]; then
  echo "(blocking: AUTOMOTIVE_DEALERSHIP_STRICT=1)" >&2
  exit 2
fi
exit 0
