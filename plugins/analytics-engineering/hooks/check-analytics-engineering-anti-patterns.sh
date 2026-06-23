#!/usr/bin/env bash
# check-analytics-engineering-anti-patterns.sh — advisory PreToolUse hook for the analytics-engineering plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set AE_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()
if grep -nEi "\\bfrom\\s+(raw|source|prod)\\.[a-z_]+\\.[a-z_]+|\\bfrom\\s+`[^`]+\\.[^`]+`" "$file" >/dev/null 2>&1; then
  findings+=("Querying a raw/source table directly — use {{ source() }} (in staging) or {{ ref() }} for lineage; don't hardcode warehouse paths.")
fi
if grep -Pzi "materialized\\s*=\\s*['\\\"]incremental['\\\"](?![\\s\\S]{0,200}unique_key)" "$file" >/dev/null 2>&1; then
  findings+=("Incremental model without a unique_key nearby — incremental needs a reliable unique key or it drops/dups rows.")
fi
if grep -nEi "select\\s+\\*\\s+from\\s+\\{\\{\\s*ref" "$file" >/dev/null 2>&1; then
  findings+=("SELECT * from a ref in a mart — name columns to keep a stable contract and avoid surprise column drift.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── analytics-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${AE_STRICT:-0}" = "1" ]; then
  echo "(blocking: AE_STRICT=1)" >&2
  exit 2
fi
exit 0
