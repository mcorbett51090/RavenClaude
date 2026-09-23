#!/usr/bin/env bash
# check-insurance-life-health-benefits-anti-patterns.sh — advisory PreToolUse hook for the
# insurance-life-health-benefits plugin. Flags mechanically-detectable benefits anti-patterns on
# Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice); set BENEFITS_STRICT=1 to make
# it blocking (exit 2). Educational scaffolding only — never legal, tax, or actuarial advice.
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
[ -z "$file" ] && exit 0
# --- proposed-edit scan target (repo-review 2026-09-23) ----------------------
# At PreToolUse the write has NOT landed: the on-disk file is the PRE-edit state
# (or absent for a new-file Write), so grepping "$file" misses the very content
# this hook exists to catch. Build the scan target from the tool payload —
# .tool_input.content (Write) / .tool_input.new_string (Edit) /
# .tool_input.edits[].new_string (MultiEdit) — and scan THAT. The on-disk file is
# used only as a legacy fallback for a manual, no-stdin invocation (payload unset).
# (Fix propagated from data-platform/hooks/flag-data-platform-smells.sh, 2026-09-03.)
scan_target="$file"
if [ -n "${payload:-}" ] && command -v jq >/dev/null 2>&1; then
  _rc_proposed="$(printf '%s' "$payload" | jq -r '[.tool_input.content // empty, .tool_input.new_string // empty, ((.tool_input.edits // [])[]?.new_string // empty)] | map(select(. != "")) | join("\n")' 2>/dev/null || true)"
  if [ -n "$_rc_proposed" ]; then
    _rc_scan_tmp="$(mktemp 2>/dev/null || true)"
    if [ -n "$_rc_scan_tmp" ]; then
      printf '%s\n' "$_rc_proposed" > "$_rc_scan_tmp"
      scan_target="$_rc_scan_tmp"
      trap 'rm -f "$_rc_scan_tmp"' EXIT
    fi
  fi
fi
[ -z "$scan_target" ] && exit 0
[ ! -f "$scan_target" ] && exit 0

findings=()

# 1. Benefits content that reads as advice with no sign-off / not-advice framing — the cardinal rule.
if grep -qiE "(self-funded|fully-insured|level-funded|deductible|coinsurance|loss ratio|medical-loss|renewal|COBRA|ACA|ERISA|1095|5500)" "$scan_target" 2>/dev/null; then
  if grep -qiE "\b(you should|we recommend|the right choice is|definitely (go|choose)|guaranteed)\b" "$scan_target" 2>/dev/null; then
    if ! grep -qiE "(not (legal|tax|actuarial) advice|educational|sign[ -]?off|broker|actuary|ERISA counsel)" "$scan_target" 2>/dev/null; then
      findings+=("Benefits recommendation phrased as advice with no 'not advice' framing / sign-off — frame trade-offs and name the broker / actuary / ERISA counsel who signs off.")
    fi
  fi
fi

# 2. An HDHP discussed with no HSA contribution mentioned — a likely cost-shift sold as a benefit.
if grep -qiE "\bHDHP\b|high[ -]deductible" "$scan_target" 2>/dev/null; then
  if ! grep -qiE "\bHSA\b|health savings" "$scan_target" 2>/dev/null; then
    findings+=("HDHP / high-deductible plan with no HSA mention — an HDHP without funded employer HSA contributions is a cost-shift, not a benefit. Pair it or say so.")
  fi
fi

# 3. A dated/regulatory figure quoted with no [verify-at-build] marker — these shift year to year.
if grep -qiE "(80%|85%|50[ -]?(FTE|full-time)|18 months|36 months|minimum value|affordability)" "$scan_target" 2>/dev/null; then
  if ! grep -qiE "verify-at-build" "$scan_target" 2>/dev/null; then
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
