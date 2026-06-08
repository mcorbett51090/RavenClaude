#!/usr/bin/env bash
# check-platform-engineering-idp-anti-patterns.sh — advisory PreToolUse hook for the
# platform-engineering-idp plugin. Flags mechanically-detectable platform-as-a-product
# anti-patterns on Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice);
# set PLATFORM_IDP_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect platform/portal-ish text + config files; skip binaries.
case "$file" in
*.md | *.yaml | *.yml | *.json | *.tf | *.txt) ;;
*) exit 0 ;;
esac

findings=()

# 1. Mandate language — adoption should be earned, not decreed.
if grep -nEi "\b(mandator(y|ily)|must use the platform|required to use the (platform|portal)|no exceptions, use)\b" "$file" >/dev/null 2>&1; then
  findings+=("Mandate language — the platform is a product; adoption is earned by being the easy path, not decreed. Re-frame as a paved road with an escape hatch.")
fi

# 2. Ticket-driven "self-service" — a self-service that opens a ticket is a service desk.
if grep -nEi "self-?service" "$file" >/dev/null 2>&1 && grep -nEi "(open|file|raise|submit)\s+a?\s*(ticket|request form|jira)" "$file" >/dev/null 2>&1; then
  findings+=("'Self-service' alongside ticket/request-form language — if the common case still routes through a human ticket, it's a service desk, not self-service. Guardrail the button instead.")
fi

# 3. Backstage catalog entity with no owner.
if grep -nEi "^\s*kind:\s*(Component|API|Resource|System)\b" "$file" >/dev/null 2>&1 && ! grep -nEi "^\s*owner:\s*\S" "$file" >/dev/null 2>&1; then
  findings+=("Catalog entity (kind: Component/API/Resource/System) with no 'owner:' — every entity must have an owner; unowned == unmaintained.")
fi

# 4. Vanity output metric as a platform KPI.
if grep -nEi "(platform features shipped|lines of code|number of (features|commits)).{0,30}(kpi|success metric|goal)" "$file" >/dev/null 2>&1; then
  findings+=("Output (features-shipped / LOC) used as a platform KPI — measure outcomes (adoption, time-to-prod, friction), not platform output.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── platform-engineering-idp advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${PLATFORM_IDP_STRICT:-0}" = "1" ]; then
  echo "(blocking: PLATFORM_IDP_STRICT=1)" >&2
  exit 2
fi
exit 0
