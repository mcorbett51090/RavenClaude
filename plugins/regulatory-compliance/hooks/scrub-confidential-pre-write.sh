#!/usr/bin/env bash
# scrub-confidential-pre-write.sh
# PreToolUse hook for Write | Edit | MultiEdit.
#
# Scans the content ABOUT TO BE WRITTEN, which the PreToolUse payload carries:
# .tool_input.content (Write), .tool_input.new_string (Edit) and
# .tool_input.edits[].new_string (MultiEdit). At PreToolUse the write has not
# landed, so the on-disk file is the PRE-edit state (absent for a new file);
# it is scanned only as a fallback for a manual, no-stdin invocation
# (`scrub-confidential-pre-write.sh <file>`).
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
# $CLAUDE_TOOL_FILE_PATH (passed as $1 by hooks.json) is NOT a real Claude Code
# hook variable, so under Claude Code the arg is empty and the path arrives only
# via the canonical stdin JSON contract. Fall back to it — same dual-source
# pattern regen-on-manifest-change.sh / guard-destructive.sh already use.
if [[ -z "$file" ]] && [[ ! -t 0 ]] && command -v jq >/dev/null 2>&1; then
  payload="$(cat 2>/dev/null || true)"
  if [[ -n "$payload" ]]; then
    file="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)"
  fi
fi
[[ -z "$file" ]] && exit 0

# Allow files explicitly named as synthetic / template / example.
case "$file" in
  *synthetic*|*example*|*template*|*placeholder*) exit 0 ;;
esac

# Scope: scan files in compliance-conventional locations OR matching
# compliance file-name patterns. Conservative — unrelated code edits
# aren't scanned by this hook. (Path filtering stays on $file.)
case "$file" in
  */compliance/*|*/kyc/*|*/aml/*|*/sar/*|*/edd/*|*/exam/*|*/regulatory/*) ;;
  *kyc*.md|*edd*.md|*sar*.md|*str*.md|*aml*.md|*risk*.md|*compliance*.md|*policy*.md|*return*.md|*csr*.md|*sfr*.md|*ebs*.md|*bscr*.md) ;;
  *) exit 0 ;;
esac

# --- proposed-edit scan target (repo-review 2026-10-19; pattern from the 29
# hooks fixed 2026-09-23, e.g. check-backend-engineering-anti-patterns.sh) ----
# Before this, the hook exited on a missing file and otherwise grepped the
# pre-edit bytes, so a new-file Write, or an Edit that ADDS an SSN, was never
# seen. control: hooks.json command, PreToolUse Write of a new compliance file
# holding an SSN shape -> rc=0, no output; same content on disk -> [pii-ssn].
scan_target="$file"
if [[ -n "${payload:-}" ]] && command -v jq >/dev/null 2>&1; then
  _rc_proposed="$(printf '%s' "$payload" | jq -r '[.tool_input.content // empty, .tool_input.new_string // empty, ((.tool_input.edits // [])[]?.new_string // empty)] | map(select(. != "")) | join("\n")' 2>/dev/null || true)"
  if [[ -n "$_rc_proposed" ]]; then
    _rc_scan_tmp="$(mktemp 2>/dev/null || true)"
    if [[ -n "$_rc_scan_tmp" ]]; then
      printf '%s\n' "$_rc_proposed" > "$_rc_scan_tmp"
      scan_target="$_rc_scan_tmp"
      trap 'rm -f "$_rc_scan_tmp"' EXIT
    fi
  fi
fi
[[ -z "$scan_target" ]] && exit 0
[[ ! -f "$scan_target" ]] && exit 0

violations=()
remediation_required=0

# --- Check 1: US SSN-shaped ---
# Filter placeholders per MATCHED TOKEN (grep -o), not per line. The old
# line-level `grep -Ev '(...|<.*>)'` dropped any line holding a '<' and a later
# '>' (a <br>, a <td>, a <KYC-12> ticket id), so a real SSN beside an HTML or
# markdown tag was never reported (repo-review 2026-10-19).
if grep -oE '\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b' "$scan_target" 2>/dev/null \
    | grep -Ev '^(000-00-0000|123-45-6789|XXX-XX-XXXX)$' >/dev/null 2>&1; then
  violations+=("  [pii-ssn] $file contains a string matching the US SSN pattern (NNN-NN-NNNN). If real, replace with placeholder before write.")
  remediation_required=1
fi

# --- Check 2: US EIN-shaped ---
if grep -oE '\b[0-9]{2}-[0-9]{7}\b' "$scan_target" 2>/dev/null \
    | grep -Ev '^(00-0000000|99-9999999)$' >/dev/null 2>&1; then
  violations+=("  [pii-ein] $file contains a string matching the US EIN pattern (NN-NNNNNNN). If real, replace with placeholder.")
  remediation_required=1
fi

# --- Check 3: IBAN-shaped ---
# Case-SENSITIVE (no -i): real IBANs are uppercase, and -i made [A-Z] also match
# lowercase, over-flagging ordinary tokens such as commit hashes. Same fix as
# finance/hooks/flag-finance-anti-patterns.sh (2026-07 review).
if grep -En '\b[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}\b' "$scan_target" >/dev/null 2>&1; then
  violations+=("  [pii-iban] $file contains a string matching the IBAN pattern. If real bank account, replace with placeholder.")
  remediation_required=1
fi

# --- Check 4: Credit-card PAN-shaped ---
# Conservative: Visa / MC / Amex / Discover prefixes, basic length.
if grep -Eni '\b(4[0-9]{12}([0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(011|5[0-9]{2})[0-9]{12})\b' "$scan_target" >/dev/null 2>&1; then
  violations+=("  [pii-card] $file contains a string matching a credit-card PAN pattern. Replace with placeholder if real.")
  remediation_required=1
fi

# --- Check 5: Bermuda TIN-shaped (synthetic — tune to actual format) ---
# Two common shapes worth catching. Adjust for actual engagement-specific TIN formats.
if grep -Eni '\b(BMU?-?[0-9]{7,9})\b' "$scan_target" >/dev/null 2>&1; then
  violations+=("  [pii-bmu-tin] $file contains a string matching a possible Bermuda TIN pattern (BMU-NNNNNNN). Verify and scrub if real.")
  remediation_required=1
fi

# --- Check 6: Bermuda passport / DL synthetic prefix ---
# Two common shapes used in working documents — tune to actual format.
if grep -Eni '\b(BMP-?[0-9]{6,8}|BDL-?[0-9]{6,8})\b' "$scan_target" >/dev/null 2>&1; then
  violations+=("  [pii-bmu-id] $file contains a string matching a possible Bermuda passport/DL pattern. Verify and scrub if real.")
  remediation_required=1
fi

# --- Check 7: Free-form wire-instruction markers ---
# Wire details should never be in plain text in a working repo.
if grep -EniH '\b(Wire ABA|SWIFT[ :]+[A-Z0-9]{8,11}\b|Routing[ :]+[0-9]{9}\b|Beneficiary Account[ :]+[0-9]{6,})\b' "$scan_target" >/dev/null 2>&1; then
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
