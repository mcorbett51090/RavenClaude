#!/usr/bin/env bash
# check-esg-sustainability-reporting-anti-patterns.sh — advisory PreToolUse hook for the esg-sustainability-reporting plugin.
# Flags mechanically-detectable ESG-reporting anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set ESG_STRICT=1 to make it blocking (exit 2).
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

# 1. An emission figure that names an emission factor but no source/vintage — un-traceable, un-assurable.
if grep -qiE "emission[ _-]?factor|tCO2e?|kgCO2e?|tonnes?\s+CO2" "$scan_target" 2>/dev/null; then
  if ! grep -qiE "(source|vintage|version|published|year)\s*[:=]" "$scan_target" 2>/dev/null; then
    findings+=("Emission factor / CO2e figure with no factor source or vintage — every factor needs a named source and year, or the number can't be traced or assured.")
  fi
fi

# 2. A Scope 2 figure reported as only one method where both are required — the dual-reporting rule.
if grep -qiE "scope[ _-]?2" "$scan_target" 2>/dev/null; then
  if grep -qiE "location[ -]?based|market[ -]?based" "$scan_target" 2>/dev/null; then
    if ! { grep -qiE "location[ -]?based" "$scan_target" 2>/dev/null && grep -qiE "market[ -]?based" "$scan_target" 2>/dev/null; }; then
      findings+=("Scope 2 reported with only one method — report BOTH location-based and market-based where instruments exist (dual-reporting requirement).")
    fi
  fi
fi

# 3. A sustainability claim with no substantiation reference — greenwashing risk.
if grep -qiE "carbon[ -]?neutral|net[ -]?zero|climate[ -]?positive|[0-9]+%\s*(reduction|reduced)" "$scan_target" 2>/dev/null; then
  if ! grep -qiE "(substantiat|evidence|methodology|basis|verif|assur|reference)" "$scan_target" 2>/dev/null; then
    findings+=("Sustainability claim (carbon-neutral / net-zero / %-reduction) with no substantiation reference — a claim the evidence can't carry is greenwashing; cite the basis or remove it.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── esg-sustainability-reporting advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${ESG_STRICT:-0}" = "1" ]; then
  echo "(blocking: ESG_STRICT=1)" >&2
  exit 2
fi
exit 0
