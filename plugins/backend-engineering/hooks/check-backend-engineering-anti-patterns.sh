#!/usr/bin/env bash
# check-backend-engineering-anti-patterns.sh — advisory PreToolUse hook for the backend-engineering plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set BACKEND_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()
if grep -nEi "(requests\\.(get|post)\\((?![\\s\\S]{0,80}timeout)|fetch\\((?![\\s\\S]{0,80}(signal|timeout))|http\\.(Get|Post)\\()" "$file" >/dev/null 2>&1; then
  findings+=("Outbound HTTP call without an apparent timeout — every external call needs one or a slow dependency cascades.")
fi
if grep -nEi "(catch\\s*\\([^)]*\\)\\s*\\{\\s*\\}|except\\s*:\\s*pass|except Exception:\\s*pass)" "$file" >/dev/null 2>&1; then
  findings+=("Swallowed exception (empty catch / except: pass) — model the error; don't hide failures.")
fi
if grep -nEi "(for\\b[\\s\\S]{0,120}(\\.find\\(|\\.get\\(|SELECT|query\\())" "$file" >/dev/null 2>&1; then
  findings+=("Possible N+1: a query inside a loop — eager-load/batch instead (route SQL tuning to database-engineering).")
fi
if grep -nEi "(publish|emit|send).*event[\\s\\S]{0,80}(commit|save)|(commit|save)[\\s\\S]{0,80}(publish|emit)" "$file" >/dev/null 2>&1; then
  findings+=("Possible dual-write (publish + commit separately) — use the transactional outbox so events match committed state.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── backend-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${BACKEND_STRICT:-0}" = "1" ]; then
  echo "(blocking: BACKEND_STRICT=1)" >&2
  exit 2
fi
exit 0
