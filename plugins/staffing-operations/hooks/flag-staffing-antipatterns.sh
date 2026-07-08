#!/usr/bin/env bash
# flag-staffing-antipatterns.sh
# PostToolUse hook for Edit | Write | MultiEdit on staffing-operations artifact files.
# Flags the most common mechanically-detectable violations of the staffing-operations
# team constitution (see plugins/staffing-operations/CLAUDE.md §3, §4):
#
#   1. Fill rate mentioned without time-to-fill (or vice versa) in the same file
#      (§3 #2) — files matching *scorecard*, *fill*, *readout*, *funnel*, *review*.
#   2. A margin / gross-margin / % claim with no bill / pay / burden basis in the
#      same file (§3 #3) — files matching *margin*, *scorecard*, *readout*.
#   3. An external market/competitor number (a $-amount or a competitor name with a
#      figure) with no source URL anywhere in the file (§3 #9) — files matching
#      *market*, *trend*, *competit*, *brief*.
#   4. Candidate / client PII shapes — an SSN-like ###-##-#### token, or a
#      "Candidate:"/"Patient:"/"Student:" line followed by a capitalized name
#      (§3 #10) — any artifact file.
#
# Advisory by default: prints warnings to stderr (Claude and the user both see
# them) but exits 0 so the edit is not blocked. To BLOCK on violation, set
# STAFFING_OPS_STRICT=1 (exit 2 = block in Claude Code; exit 1 is non-blocking
# and would silently allow the edit).

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
[[ ! -f "$file" ]] && exit 0

base_lc=$(basename "$file" | tr '[:upper:]' '[:lower:]')

# Only inspect markdown artifacts; skip the plugin's own knowledge/skill/template
# scaffolding so we don't flag the rules that describe the anti-patterns.
case "$base_lc" in
  *.md) : ;;
  *) exit 0 ;;
esac
case "$file" in
  */knowledge/*|*/skills/*|*/templates/*|*/best-practices/*|*/commands/*|*/agents/*|*CLAUDE.md|*README.md) exit 0 ;;
esac

violations=()

# --- Check 1: fill rate without time-to-fill ---
case "$base_lc" in
  *scorecard*|*fill*|*readout*|*funnel*|*review*)
    if grep -qiE 'fill[ -]?rate' "$file" 2>/dev/null; then
      if ! grep -qiE 'time[ -]?to[ -]?fill|time[ -]?to[ -]?start|days to fill' "$file" 2>/dev/null; then
        violations+=("  [fill-without-speed] $file mentions fill rate but not time-to-fill — pair them (§3 #2). A 95% fill at 45 days can lose to 80% at 9 days.")
      fi
    fi
    ;;
esac

# --- Check 2: margin / % without bill-pay-burden basis ---
case "$base_lc" in
  *margin*|*scorecard*|*readout*)
    if grep -qiE 'gross margin|\bmargin\b|spread' "$file" 2>/dev/null; then
      if ! grep -qiE 'bill[ -]?rate|pay[ -]?rate|burden' "$file" 2>/dev/null; then
        violations+=("  [margin-without-decomposition] $file discusses margin/spread with no bill / pay / burden basis — decompose before diagnosing (§3 #3).")
      fi
    fi
    ;;
esac

# --- Check 3: external market number with no source URL ---
case "$base_lc" in
  *market*|*trend*|*competit*|*brief*)
    # A market figure looks like $<n>B / $<n>M / "<n>% share" / "<n>% CAGR".
    if grep -qiE '\$[0-9]+(\.[0-9]+)?[ ]?[MB]\b|[0-9]+(\.[0-9]+)?%[ ]?(share|cagr)' "$file" 2>/dev/null; then
      if ! grep -qiE 'https?://' "$file" 2>/dev/null; then
        violations+=("  [unsourced-market-number] $file cites a market/competitor figure with no source URL — every external number gets a source + date or [unverified] (§3 #9).")
      fi
    fi
    ;;
esac

# --- Check 4: candidate / client PII shapes ---
# SSN-like token.
if grep -qE '\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b' "$file" 2>/dev/null; then
  violations+=("  [pii-ssn-shape] $file contains an SSN-shaped token (###-##-####) — no candidate/client PII in deliverables (§3 #10).")
fi
# "Candidate:/Patient:/Student:" followed by a capitalized full name (two capitalized words).
if grep -qE '(Candidate|Patient|Student|Traveler|Clinician):[[:space:]]+[A-Z][a-z]+[[:space:]]+[A-Z][a-z]+' "$file" 2>/dev/null; then
  violations+=("  [pii-named-person] $file appears to name an individual candidate/patient/student — use roles/segments (<traveler>, <a 200-bed facility>) not names (§3 #10).")
fi

# --- Report ---
if [[ ${#violations[@]} -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  staffing-operations anti-pattern check flagged ${#violations[@]} potential issue(s) in:
       $file
EOF
  for v in "${violations[@]}"; do
    echo "$v" >&2
  done
  cat >&2 <<EOF

  Why this matters: the staffing-operations constitution (plugins/
  staffing-operations/CLAUDE.md §3, §4) treats these as credibility and
  privacy risks. Fill rate without speed misreads the problem; a margin
  with no bill/pay/burden sends operators to reprice the wrong thing; an
  unsourced market number gets challenged by an operator who lives the
  market; named PII does not belong in a consulting artifact.

  This hook is advisory — the edit was not blocked. To enforce, set
  STAFFING_OPS_STRICT=1 in your env (exit 2 = BLOCK; exit 1 is
  non-blocking and would silently allow the edit).
────────────────────────────────────────────────────────────────────

EOF
  if [[ "${STAFFING_OPS_STRICT:-0}" == "1" ]]; then exit 2; fi
fi

exit 0
