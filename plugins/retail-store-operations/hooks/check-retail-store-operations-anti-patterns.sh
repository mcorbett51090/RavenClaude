#!/usr/bin/env bash
# check-retail-store-operations-anti-patterns.sh — advisory PreToolUse hook for the
# retail-store-operations plugin. Flags mechanically-detectable retail anti-patterns on
# Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice to stderr);
# set RETAIL_STORE_OPS_STRICT=1 to make it blocking (exit 2).
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

# Only inspect text/config/document files; skip binaries.
case "$file" in
*.md | *.yaml | *.yml | *.json | *.txt | *.py | *.sh | *.csv) ;;
*) exit 0 ;;
esac

findings=()

# 1. Labor schedule with no traffic/sales basis.
# Fires when a file looks like a schedule (contains "schedule" or "shift") but has no
# reference to traffic data, transaction count, or sales.
if grep -nEi "\b(schedule|shift)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(traffic|transaction[s]?|sales per|splh|coverage ratio)\b" "$file" >/dev/null 2>&1; then
    findings+=("Labor schedule with no traffic/sales basis — staffing decisions must reference hourly traffic data, transaction counts, or coverage ratios. A schedule without a demand basis is a shift-filling exercise, not a labor model.")
  fi
fi

# 2. Markdown with no sell-through rationale.
# Fires when a file recommends a markdown/discount but contains no sell-through or
# weeks-of-supply reference.
if grep -nEi "\b(mark.?down|discount|clearance|price reduction)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(sell.?through|weeks.of.supply|wos|season week|season end)\b" "$file" >/dev/null 2>&1; then
    findings+=("Markdown recommendation with no sell-through or weeks-of-supply rationale — every markdown decision requires a current sell-through rate, weeks-of-supply, and a count of weeks remaining in the selling season. Without these, the depth is a guess.")
  fi
fi

# 3. Hard-coded sales or shrink figure with no date.
# Fires when a specific sales or shrink percentage/dollar is stated without a date or
# source reference nearby.
if grep -nEi "\b(shrink rate|shrink of|sales of \$|sales were \$|revenue of \$)[[:space:]]*[0-9]" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(as of|week end|period end|ytd|qtd|date|source)\b" "$file" >/dev/null 2>&1; then
    findings+=("Hard-coded sales or shrink figure with no date or source — a specific shrink rate or sales figure without a reporting period and source is unanchored. Retail metrics move; always attach a date and source to any cited number.")
  fi
fi

# 4. Safety stock or replenishment trigger with no service-level note.
# Fires when a file mentions safety stock, reorder point, or min/max without a
# service level (e.g., 95%, 98%, 99% in-stock).
if grep -nEi "\b(safety stock|reorder point|min.?max|reorder trigger)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(service.?level|in.?stock rate|[0-9]{2}%[[:space:]]*(in.?stock|service))\b" "$file" >/dev/null 2>&1; then
    findings+=("Safety stock or replenishment trigger with no service-level note — safety stock without a stated service-level target (e.g., 98% in-stock) is just a number. State the service level the trigger is designed to achieve.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── retail-store-operations advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${RETAIL_STORE_OPS_STRICT:-0}" = "1" ]; then
  echo "(blocking: RETAIL_STORE_OPS_STRICT=1)" >&2
  exit 2
fi
exit 0
