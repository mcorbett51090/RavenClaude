#!/usr/bin/env bash
# check-esg-sustainability-reporting-anti-patterns.sh — advisory PreToolUse hook for the esg-sustainability-reporting plugin.
# Flags mechanically-detectable ESG-reporting anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set ESG_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# 1. An emission figure that names an emission factor but no source/vintage — un-traceable, un-assurable.
if grep -qiE "emission[ _-]?factor|tCO2e?|kgCO2e?|tonnes?\s+CO2" "$file" 2>/dev/null; then
  if ! grep -qiE "(source|vintage|version|published|year)\s*[:=]" "$file" 2>/dev/null; then
    findings+=("Emission factor / CO2e figure with no factor source or vintage — every factor needs a named source and year, or the number can't be traced or assured.")
  fi
fi

# 2. A Scope 2 figure reported as only one method where both are required — the dual-reporting rule.
if grep -qiE "scope[ _-]?2" "$file" 2>/dev/null; then
  if grep -qiE "location[ -]?based|market[ -]?based" "$file" 2>/dev/null; then
    if ! { grep -qiE "location[ -]?based" "$file" 2>/dev/null && grep -qiE "market[ -]?based" "$file" 2>/dev/null; }; then
      findings+=("Scope 2 reported with only one method — report BOTH location-based and market-based where instruments exist (dual-reporting requirement).")
    fi
  fi
fi

# 3. A sustainability claim with no substantiation reference — greenwashing risk.
if grep -qiE "carbon[ -]?neutral|net[ -]?zero|climate[ -]?positive|[0-9]+%\s*(reduction|reduced)" "$file" 2>/dev/null; then
  if ! grep -qiE "(substantiat|evidence|methodology|basis|verif|assur|reference)" "$file" 2>/dev/null; then
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
