#!/usr/bin/env bash
# check-backend-engineering-anti-patterns.sh — advisory PreToolUse hook for the backend-engineering plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set BACKEND_STRICT=1 to make it blocking (exit 2).
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

findings=()
if grep -Pzi "(requests\\.(get|post)\\((?![\\s\\S]{0,80}timeout)|fetch\\((?![\\s\\S]{0,80}(signal|timeout))|http\\.(Get|Post)\\()" "$file" >/dev/null 2>&1; then
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
