#!/usr/bin/env bash
# check-supply-chain-planning-anti-patterns.sh — advisory PreToolUse hook for the
# supply-chain-planning plugin. Flags mechanically-detectable supply-chain planning
# anti-patterns on Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice);
# set SUPPLY_CHAIN_PLANNING_STRICT=1 to make it blocking (exit 2).
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
[ ! -f "$file" ] && exit 0

# Only inspect planning-ish text and config files; skip binaries.
case "$file" in
*.md | *.yaml | *.yml | *.json | *.csv | *.txt | *.py) ;;
*) exit 0 ;;
esac

findings=()

# 1. Safety-stock or reorder number with no service-level or lead-time-variability basis.
# Trigger: a line mentions "safety stock" or "reorder" AND contains a number,
# but has no z-score / service level / sigma / std dev reference nearby.
if grep -nEi "(safety.?stock|reorder.?point)\s*[=:]\s*[0-9]" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "(z[-_ ]?score|service.?level|sigma|std.?dev|variability|fill.?rate|csl)" "$file" >/dev/null 2>&1; then
    findings+=("Safety-stock or reorder-point figure with no service-level or variability basis — a number without z, σ_demand, or CSL is a days-of-supply guess, not a grounded safety-stock calculation. Document the service level, z-score, and demand standard deviation.")
  fi
fi

# 2. A forecast with no accuracy metric (MAPE or bias).
# Trigger: file mentions "forecast" but has no MAPE, bias, or accuracy reference.
if grep -nEi "\bforecast\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "(mape|mean.?absolute.?percent|bias|forecast.?accuracy|tracking.?signal)" "$file" >/dev/null 2>&1; then
    findings+=("Forecast mentioned with no accuracy metric — every published forecast must report MAPE and bias from a holdout period. A forecast without measured accuracy is a guess with authority.")
  fi
fi

# 3. Hard-coded demand figure with no date.
# Trigger: a line that looks like demand = <number> (or "demand: 1000") with no date nearby.
if grep -nEi "(annual.?demand|demand.?rate|demand.?volume)\s*[=:]\s*[0-9]" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "([0-9]{4}-[0-9]{2}|as.?of|dated|last.?updated|year\s+[0-9]{4})" "$file" >/dev/null 2>&1; then
    findings+=("Hard-coded demand figure with no date — demand figures become stale. Add a 'as of YYYY-MM' or 'last updated' annotation so readers know the vintage of the input.")
  fi
fi

# 4. "Just-in-time" with no risk or buffer note.
# Trigger: JIT / just-in-time language with no mention of risk, buffer, contingency, or dual-source.
if grep -nEi "\b(just.?in.?time|jit)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "(risk|buffer|contingency|dual.?source|safety.?stock|disruption|mitigation)" "$file" >/dev/null 2>&1; then
    findings+=("'Just-in-time' or 'JIT' mentioned with no risk/buffer note — JIT eliminates inventory buffers and concentrates supply risk. Document the risk acknowledgement, any dual-sourcing strategy, and the disruption-response plan.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── supply-chain-planning advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${SUPPLY_CHAIN_PLANNING_STRICT:-0}" = "1" ]; then
  echo "(blocking: SUPPLY_CHAIN_PLANNING_STRICT=1)" >&2
  exit 2
fi
exit 0
