#!/usr/bin/env bash
# flag-se-antipatterns.sh
# PreToolUse hook for Edit | Write | MultiEdit on sales-engineering artifact files
# (.md). Flags four mechanically-detectable violations of the sales-engineering
# team constitution (see plugins/sales-engineering/CLAUDE.md §3, §4):
#
#   1. A POC / success-criteria doc with NO exit / kill criterion
#      (poc-and-evaluation-best-practices.md — un-failable = un-winnable)
#   2. A security answer claiming "yes/comply/implemented" with NO evidence
#      anchor nearby (SOC 2 / ISO / control / evidence) — unsupported security claim
#   3. Overpromise / feature-dump absolutes ("fully supports", "no limitations",
#      "can do everything", "unlimited everything") — the fabricated-yes smell
#   4. A demo script with NO pain mapping (no "pain" / "business issue" / "impact")
#      — the feature-tour smell
#
# Advisory by default: prints warnings to stderr (so Claude and the user both see
# them) but exits 0 so the edit is not blocked. Set SE_STRICT=1 to make violations
# blocking (exit 2).
#
# Claude Code PreToolUse: exit 2 = BLOCK the tool call with stderr surfaced to the
# agent. exit 1 = non-blocking error (silently swallowed).

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

base_lc=$(basename "$file" | tr '[:upper:]' '[:lower:]')

# Only inspect markdown artifacts.
case "$base_lc" in
  *.md) : ;;
  *) exit 0 ;;
esac

# Lowercased content for case-insensitive matching.
content_lc=$(tr '[:upper:]' '[:lower:]' < "$file" 2>/dev/null || true)
[[ -z "$content_lc" ]] && exit 0

warnings=()

# --- Check 1: POC / success-criteria doc with no exit/kill criterion ---------
if printf '%s' "$content_lc" | grep -Eq 'success crit|proof of concept|\bpoc\b|pilot'; then
  if ! printf '%s' "$content_lc" | grep -Eq 'exit crit|kill rule|fail|pass/fail|pass ?/ ?fail'; then
    warnings+=("POC/success-criteria content with no exit/kill/pass-fail rule — a POC you can't fail is one you can't win (CLAUDE.md §3; poc-and-evaluation-best-practices.md).")
  fi
fi

# --- Check 2: security 'yes' claim with no evidence anchor ------------------
if printf '%s' "$content_lc" | grep -Eq 'sig |caiq|security questionnaire|vendor (risk|security)|soc ?2|iso ?27001'; then
  if printf '%s' "$content_lc" | grep -Eq '\b(comply|implemented|yes\b|we support|fully (support|compliant))'; then
    if ! printf '%s' "$content_lc" | grep -Eq 'evidence|control|soc ?2|iso ?27001|statement of applicability|policy|attestation'; then
      warnings+=("Security answer asserts compliance with no evidence anchor (control / SOC 2 / ISO / policy) — a 'yes' with no evidence is a finding/clawback risk; flag for security-reviewer (CLAUDE.md §4; security-questionnaire-and-trust.md).")
    fi
  fi
fi

# --- Check 3: overpromise / feature-dump absolutes -------------------------
if printf '%s' "$content_lc" | grep -Eq 'no limitations|can do everything|does everything|unlimited everything|handles? (any|every)thing|fully supports? all'; then
  warnings+=("Overpromise/absolute language detected ('no limitations' / 'does everything' / 'fully supports all') — distinguish shipped vs roadmap vs unsupported; a fabricated yes surfaces in the POC (CLAUDE.md §3).")
fi

# --- Check 4: demo script with no pain mapping -----------------------------
if printf '%s' "$base_lc" | grep -Eq 'demo'; then
  if ! printf '%s' "$content_lc" | grep -Eq 'pain|business issue|impact'; then
    warnings+=("Demo content with no pain/business-issue/impact mapping — a demo with no discovered pain is a feature tour (CLAUDE.md §3; discovery-and-demo-playbook.md, Great Demo!).")
  fi
fi

[[ ${#warnings[@]} -eq 0 ]] && exit 0

{
  echo "⚠️  sales-engineering advisory — $(basename "$file"):"
  for w in "${warnings[@]}"; do
    echo "   • $w"
  done
} >&2

if [[ "${SE_STRICT:-0}" == "1" ]]; then
  exit 2
fi
exit 0
