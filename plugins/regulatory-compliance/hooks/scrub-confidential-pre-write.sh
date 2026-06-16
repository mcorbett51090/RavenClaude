#!/usr/bin/env bash
# scrub-confidential-pre-write.sh
# PreToolUse hook for Write | Edit | MultiEdit.
#
# Scans the *pending* target file (its current on-disk content if it exists;
# the agent's about-to-write content is not directly visible here, so this
# hook acts as a second line of defense by re-scanning the file AFTER the
# tool runs is one option, but this hook is PreToolUse and so checks the
# existing file content for prior leakage and warns the agent before it
# adds more. Pair with a separate PostToolUse if you want fail-after-write).
#
# Catches:
#   1. US SSN-shaped (NNN-NN-NNNN)
#   2. US EIN-shaped (NN-NNNNNNN)
#   3. IBAN-shaped (2 letters + 2 digits + 11-30 alphanumerics)
#   4. Credit-card PAN-shaped (Visa / MC / Amex / Discover prefixes; basic shape)
#   5. Bermuda TIN-shaped (BMU-####### or BM#######) — synthetic; tune
#   6. Bermuda passport/DL-shaped — synthetic prefix patterns; tune
#   7. Free-form wire-instruction markers (Wire ABA:, SWIFT:, Routing:)
#
# Advisory by default: prints warnings to stderr, exits 0 (allow write).
# **For sensitive engagements and ALWAYS for SAR/STR drafting, flip the
# bottom `exit 0` to `exit 2`** so the hook denies the write entirely.
# (exit 2 is the documented PreToolUse "deny" exit code; see the
# ravenclaude-core enforce-layout.sh hook for the canonical reference.)
#
# This hook is conservative — false positives are cheap (annoy the agent),
# false negatives are expensive (leak PII).

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0

# Allow files explicitly named as synthetic / template / example.
case "$file" in
  *synthetic*|*example*|*template*|*placeholder*) exit 0 ;;
esac

# Only scan the existing on-disk content (if any). For a brand-new file
# being created, there's nothing to scan yet, and the PostToolUse hook
# in finance / power-platform would be the layer to add for after-write
# scanning. The PreToolUse role here is to flag existing leakage and
# warn the agent not to amplify.
[[ ! -f "$file" ]] && exit 0

# Scope: scan files in compliance-conventional locations OR matching
# compliance file-name patterns. Conservative — unrelated code edits
# aren't scanned by this hook.
case "$file" in
  */compliance/*|*/kyc/*|*/aml/*|*/sar/*|*/edd/*|*/exam/*|*/regulatory/*) ;;
  *kyc*.md|*edd*.md|*sar*.md|*str*.md|*aml*.md|*risk*.md|*compliance*.md|*policy*.md|*return*.md|*csr*.md|*sfr*.md|*ebs*.md|*bscr*.md) ;;
  *) exit 0 ;;
esac

violations=()
remediation_required=0

# --- Check 1: US SSN-shaped ---
if grep -En '\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b' "$file" 2>/dev/null \
    | grep -Ev '(000-00-0000|123-45-6789|XXX-XX-XXXX|<.*>)' >/dev/null 2>&1; then
  violations+=("  [pii-ssn] $file contains a string matching the US SSN pattern (NNN-NN-NNNN). If real, replace with placeholder before write.")
  remediation_required=1
fi

# --- Check 2: US EIN-shaped ---
if grep -En '\b[0-9]{2}-[0-9]{7}\b' "$file" 2>/dev/null \
    | grep -Ev '(00-0000000|<.*>|99-9999999)' >/dev/null 2>&1; then
  violations+=("  [pii-ein] $file contains a string matching the US EIN pattern (NN-NNNNNNN). If real, replace with placeholder.")
  remediation_required=1
fi

# --- Check 3: IBAN-shaped ---
if grep -Eni '\b[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}\b' "$file" >/dev/null 2>&1; then
  violations+=("  [pii-iban] $file contains a string matching the IBAN pattern. If real bank account, replace with placeholder.")
  remediation_required=1
fi

# --- Check 4: Credit-card PAN-shaped ---
# Conservative: Visa / MC / Amex / Discover prefixes, basic length.
if grep -Eni '\b(4[0-9]{12}([0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(011|5[0-9]{2})[0-9]{12})\b' "$file" >/dev/null 2>&1; then
  violations+=("  [pii-card] $file contains a string matching a credit-card PAN pattern. Replace with placeholder if real.")
  remediation_required=1
fi

# --- Check 5: Bermuda TIN-shaped (synthetic — tune to actual format) ---
# Two common shapes worth catching. Adjust for actual engagement-specific TIN formats.
if grep -Eni '\b(BMU?-?[0-9]{7,9})\b' "$file" >/dev/null 2>&1; then
  violations+=("  [pii-bmu-tin] $file contains a string matching a possible Bermuda TIN pattern (BMU-NNNNNNN). Verify and scrub if real.")
  remediation_required=1
fi

# --- Check 6: Bermuda passport / DL synthetic prefix ---
# Two common shapes used in working documents — tune to actual format.
if grep -Eni '\b(BMP-?[0-9]{6,8}|BDL-?[0-9]{6,8})\b' "$file" >/dev/null 2>&1; then
  violations+=("  [pii-bmu-id] $file contains a string matching a possible Bermuda passport/DL pattern. Verify and scrub if real.")
  remediation_required=1
fi

# --- Check 7: Free-form wire-instruction markers ---
# Wire details should never be in plain text in a working repo.
if grep -EniH '\b(Wire ABA|SWIFT[ :]+[A-Z0-9]{8,11}\b|Routing[ :]+[0-9]{9}\b|Beneficiary Account[ :]+[0-9]{6,})\b' "$file" >/dev/null 2>&1; then
  violations+=("  [pii-wire] $file contains likely wire-instruction details (ABA / SWIFT / Routing / Beneficiary Account). Move to secure storage; do not commit.")
  remediation_required=1
fi

# --- Report ---
if [[ ${#violations[@]} -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  Regulatory-compliance confidentiality check flagged ${#violations[@]} issue(s) on:
       $file

EOF
  for v in "${violations[@]}"; do
    echo "$v" >&2
  done
  cat >&2 <<'EOF'

  See plugins/regulatory-compliance/CLAUDE.md §3 (house opinion #9 —
  privacy by default) and §4 (anti-patterns — real client PII in
  committed files).

  This hook is ADVISORY by default. For SAR / STR drafting and other
  sensitive engagements, change `exit 0` to `exit 2` at the bottom of
  plugins/regulatory-compliance/hooks/scrub-confidential-pre-write.sh
  so the hook BLOCKS the write entirely.
────────────────────────────────────────────────────────────────────

EOF
fi

exit 0
