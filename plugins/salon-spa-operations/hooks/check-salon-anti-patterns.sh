#!/usr/bin/env bash
# check-salon-anti-patterns.sh — advisory PreToolUse hook for the salon-spa-operations plugin.
# Flags mechanically-detectable salon/spa-ops anti-patterns on Edit/Write/MultiEdit of .md
# files. Advisory by default (exit 0, prints a notice); set SALON_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect markdown files (policies, menus, comp plans).
case "$file" in
  *.md) ;;
  *) exit 0 ;;
esac

findings=()

# 1. A no-show / cancellation policy with no deposit / card-on-file / fee mechanism.
if grep -nEi 'no.?show|cancellation' "$file" >/dev/null 2>&1; then
  if ! grep -nEi 'deposit|card.?on.?file|card on file|fee|forfeit' "$file" >/dev/null 2>&1; then
    findings+=("This no-show/cancellation policy names no deposit / card-on-file / fee — a policy without that mechanism is a wish (the deposit makes the chair-time recoverable).")
  fi
fi

# 2. A compensation / comp-plan doc that names a split but never the classification test.
if grep -nEi 'commission|booth.?rent|chair.?rent' "$file" >/dev/null 2>&1; then
  if ! grep -nEi 'classif|employee|independent contractor|contractor|people-operations-hr' "$file" >/dev/null 2>&1; then
    findings+=("This compensation doc names a pay model but not worker classification — flag the employee/contractor test (it is legal + jurisdiction-dependent) and route the verdict to people-operations-hr; never call a model 'legal'.")
  fi
fi

# 3. A service-menu / pricing doc with no retail-attachment or rebooking mention.
if grep -nEi 'service menu|pricing|price list|menu of services' "$file" >/dev/null 2>&1; then
  if ! grep -nEi 'retail|attach|rebook|retention' "$file" >/dev/null 2>&1; then
    findings+=("This menu/pricing doc mentions no retail attachment or rebooking — retail is the margin lifeline and rebooking is the core KPI; design the menu to drive both.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── salon-spa-operations advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${SALON_STRICT:-0}" = "1" ]; then
  echo "(blocking: SALON_STRICT=1)" >&2
  exit 2
fi
exit 0
