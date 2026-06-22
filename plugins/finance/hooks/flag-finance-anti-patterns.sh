#!/usr/bin/env bash
# flag-finance-anti-patterns.sh
# PostToolUse hook for Edit | Write | MultiEdit on finance-conventional files.
# Flags mechanically-detectable violations of the finance team constitution
# (see plugins/finance/CLAUDE.md §3 "house opinions" and §4 "anti-patterns"):
#
#   1. Hardcoded rate-like numbers in model files (`*0.21`, `*1.25` etc.)
#      where the number looks like a tax rate, growth rate, or discount factor
#      buried in a formula — should be promoted to an inputs sheet (§3 #2).
#   2. Plaintext PII patterns (SSN, IBAN, full credit-card numbers) in any
#      finance-conventional file (§3 #10 — confidentiality by default).
#   3. Variance commentary files (matching *variance*.md) without a
#      `Sources:` or `Source:` line — violates §3 #1 (source-cite every
#      number) and §3 #7 (numbers don't ship without commentary).
#   4. Forecast / budget files (matching *forecast*.md, *budget*.md)
#      without an `Assumptions:` section — violates §4 anti-pattern
#      (forecast without documented assumption set).
#
# Advisory by default: prints warnings to stderr so Claude and the user
# both see them, but exits 0 so the edit is not blocked. To make this hook
# BLOCK on violation (e.g. for a sensitive client engagement), change the
# final `exit 0` to `exit 1`.

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

# Only run on files in a finance-conventional location, OR matching a
# finance file-name pattern. Heuristic: file lives under one of these
# folders, OR has a finance-coded name. Conservative — unrelated code
# edits aren't flagged.
case "$file" in
  */finance/*|*/workpapers/*|*/board/*|*/models/*|*/close/*) ;;
  *variance*.md|*forecast*.md|*budget*.md|*model*.md|*board-pack*.md|*recon*.md|*pbc*.md) ;;
  *) exit 0 ;;
esac

violations=()

# --- Check 1: Hardcoded rate-like numbers in model markdown ---
# Pattern: `*0.21` or `*0.15` or `*1.25` etc. — common tax rate, growth
# rate, or discount factor hardcodes buried in formula text. Skip the
# Assumptions / Inputs sections (these are where inputs SHOULD live).
case "$file" in
  *model*.md|*/models/*)
    # Look for `* 0.xx` or `*0.xx` patterns (Excel-style formula text).
    # Cap rate-like at 0.50 (typical tax / growth / margin range).
    if grep -Eni '\*\s?0\.[0-5][0-9]' "$file" >/dev/null 2>&1; then
      while IFS= read -r line; do
        violations+=("  [hardcoded-rate] $file: $line")
      done < <(grep -En '\*\s?0\.[0-5][0-9]' "$file" | head -3)
    fi
    ;;
esac

# --- Check 2: Plaintext PII / financial identifiers ---
# Block: SSN-shaped, IBAN-shaped, credit-card-shaped patterns.
# Skip files that explicitly say "synthetic" or "example" in the name.
case "$file" in
  *synthetic*|*example*|*template*) ;;
  *)
    # SSN-shaped: 3-2-4 digits with hyphens. Excludes common placeholders.
    if grep -En '\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b' "$file" 2>/dev/null \
        | grep -Ev '(000-00-0000|123-45-6789|XXX-XX-XXXX|<.*>)' >/dev/null 2>&1; then
      violations+=("  [plaintext-pii-ssn] $file contains a number matching the SSN pattern (NNN-NN-NNNN). Verify it's not real client PII; replace with placeholder if it is.")
    fi
    # IBAN-shaped: 2 letters + 2 digits + 11-30 alphanumerics. Conservative.
    if grep -Eni '\b[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}\b' "$file" >/dev/null 2>&1; then
      violations+=("  [plaintext-pii-iban] $file contains a string matching the IBAN pattern. Verify it's not a real bank account; replace with placeholder if it is.")
    fi
    # Credit-card-shaped: 13-19 digits, often with separators. Very conservative.
    if grep -Eni '\b(4[0-9]{12}([0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(011|5[0-9]{2})[0-9]{12})\b' "$file" >/dev/null 2>&1; then
      violations+=("  [plaintext-pii-card] $file contains a string matching a credit-card number pattern. Replace with placeholder if it is real.")
    fi
    ;;
esac

# --- Check 3: Variance commentary without a Sources line ---
case "$file" in
  *variance*.md)
    if ! grep -qEi '^\s*\*?\*?(sources?|source-cited):' "$file" 2>/dev/null; then
      violations+=("  [variance-missing-sources] $file is a variance commentary file but has no 'Sources:' / 'Source:' line. House opinion §3 #1 (source-cite every number) requires it.")
    fi
    ;;
esac

# --- Check 4: Forecast / budget without an Assumptions section ---
case "$file" in
  *forecast*.md|*budget*.md)
    if ! grep -qEi '^\s*#+\s*assumptions' "$file" 2>/dev/null \
       && ! grep -qEi '^\s*\*?\*?assumptions:' "$file" 2>/dev/null; then
      violations+=("  [forecast-missing-assumptions] $file is a forecast/budget file but has no 'Assumptions' section. Anti-pattern §4 — forecast without documented assumption set.")
    fi
    ;;
esac

# --- Report ---
if [[ ${#violations[@]} -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  Finance house-opinion check flagged ${#violations[@]} issue(s) in:
       $file

EOF
  for v in "${violations[@]}"; do
    echo "$v" >&2
  done
  cat >&2 <<'EOF'

  See plugins/finance/CLAUDE.md §3 (house opinions) and §4
  (anti-patterns) for the full rules. This hook is advisory — the
  edit was not blocked. To enforce on a sensitive engagement, change
  `exit 0` to `exit 1` at the bottom of
  plugins/finance/hooks/flag-finance-anti-patterns.sh.
────────────────────────────────────────────────────────────────────

EOF
fi

exit 0
