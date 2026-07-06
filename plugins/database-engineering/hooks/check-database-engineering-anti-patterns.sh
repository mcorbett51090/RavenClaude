#!/usr/bin/env bash
# check-database-engineering-anti-patterns.sh — advisory PreToolUse hook for the database-engineering plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set DBENG_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# grep -P (PCRE) is a GNU extension; BSD/macOS grep lacks it and errors. Probe once
# so the PCRE-based multiline checks below don't SILENTLY no-op on non-GNU grep —
# emit a visible advisory instead of failing to "no finding" (2026-07 review).
_pcre_ok=1
printf 'x' | grep -Pq 'x' 2>/dev/null || _pcre_ok=0

findings=()
if grep -nEi "select\\s+\\*\\s+from" "$file" >/dev/null 2>&1; then
  findings+=("SELECT * — name the columns (avoids wide-row reads, breaks on schema change, blocks covering-index use).")
fi
if [ "$_pcre_ok" = 1 ]; then
  if grep -Pzi "create\\s+index\\s+(?!concurrently)" "$file" >/dev/null 2>&1; then
    findings+=("CREATE INDEX without CONCURRENTLY — on a live table this takes a blocking lock; use CONCURRENTLY.")
  fi
  if grep -Pzi "(alter\\s+table\\s+\\S+\\s+add\\s+column\\s+.*not\\s+null(?!.*default)|set\\s+not\\s+null)" "$file" >/dev/null 2>&1; then
    findings+=("Adding NOT NULL / SET NOT NULL can lock a hot table — use nullable add + backfill + ADD CONSTRAINT NOT VALID then VALIDATE.")
  fi
else
  printf "%s\n" "  • [note] CONCURRENTLY / NOT-NULL checks skipped — this grep lacks -P (PCRE); install GNU grep for full coverage." >&2
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
