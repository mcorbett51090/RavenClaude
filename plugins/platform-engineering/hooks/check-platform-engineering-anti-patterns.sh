#!/usr/bin/env bash
# check-platform-engineering-anti-patterns.sh — advisory PreToolUse hook for the platform-engineering plugin.
# Flags mechanically-detectable platform anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set PLATFORM_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# 1. A Backstage-style catalog entity with no owner — the §4 #7 ownership rule.
if grep -qiE "^kind:\s*(Component|System|API|Resource)\b" "$file" 2>/dev/null \
  || printf '%s' "$file" | grep -qiE "catalog-info(\.ya?ml)?$" 2>/dev/null; then
  if ! grep -qiE "^\s*owner:\s*\S" "$file" 2>/dev/null; then
    findings+=("Catalog entity with no 'owner:' — every component needs a team owner (un-owned services page nobody).")
  fi
fi

# 2. A scaffolder/software template that doesn't register the service it creates — onboarding stays manual.
if grep -qiE "^kind:\s*Template\b" "$file" 2>/dev/null; then
  if ! grep -qiE "(catalog:register|catalog-info|register.*location)" "$file" 2>/dev/null; then
    findings+=("Scaffolder Template with no catalog-registration step — the template should register the new service, not leave it as a follow-up ticket.")
  fi
fi

# 3. A doc that calls something "self-service" but still routes to a ticket queue — that's a faster queue, not self-service.
if grep -qiE "self[ -]?service" "$file" 2>/dev/null; then
  if grep -qiE "(open|file|raise|submit|create)\s+(a\s+)?(jira\s+)?ticket|service\s*now|ServiceNow" "$file" 2>/dev/null; then
    findings+=("'Self-service' that routes to a ticket — if a human must action it, it's a queue, not self-service. Design the human out.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── platform-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${PLATFORM_STRICT:-0}" = "1" ]; then
  echo "(blocking: PLATFORM_STRICT=1)" >&2
  exit 2
fi
exit 0
