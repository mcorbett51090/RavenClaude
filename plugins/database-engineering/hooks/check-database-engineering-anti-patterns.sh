#!/usr/bin/env bash
# check-database-engineering-anti-patterns.sh — advisory PreToolUse hook for the database-engineering plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set DBENG_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()
if grep -nEi "select\\s+\\*\\s+from" "$file" >/dev/null 2>&1; then
  findings+=("SELECT * — name the columns (avoids wide-row reads, breaks on schema change, blocks covering-index use).")
fi
if grep -nEi "create\\s+index\\s+(?!concurrently)" "$file" >/dev/null 2>&1; then
  findings+=("CREATE INDEX without CONCURRENTLY — on a live table this takes a blocking lock; use CONCURRENTLY.")
fi
if grep -nEi "(alter\\s+table\\s+\\S+\\s+add\\s+column\\s+.*not\\s+null(?!.*default)|set\\s+not\\s+null)" "$file" >/dev/null 2>&1; then
  findings+=("Adding NOT NULL / SET NOT NULL can lock a hot table — use nullable add + backfill + ADD CONSTRAINT NOT VALID then VALIDATE.")
fi
if grep -nEi "where\\s+\\w+\\s*\\(\\s*\\w+\\s*\\)\\s*=|where\\s+(lower|upper|date)\\s*\\(" "$file" >/dev/null 2>&1; then
  findings+=("Function on a filtered column (non-sargable) — the index can't be used; rewrite or use an expression index.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── database-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${DBENG_STRICT:-0}" = "1" ]; then
  echo "(blocking: DBENG_STRICT=1)" >&2
  exit 2
fi
exit 0
