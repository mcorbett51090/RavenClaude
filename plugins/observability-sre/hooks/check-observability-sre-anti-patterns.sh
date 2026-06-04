#!/usr/bin/env bash
# check-observability-sre-anti-patterns.sh — advisory PreToolUse hook for the observability-sre plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set OBS_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()
if grep -nEi "(counter|gauge|histogram|metric)\\b.*\\b(user_id|userid|request_id|requestid|email|session_id)\\b" "$file" >/dev/null 2>&1; then
  findings+=("Possible high-cardinality metric label (user/request/session id) — move it to spans/logs; it will explode your TSDB.")
fi
if grep -nEi "alert.*\\b(cpu|memory|disk)\\s*(>|usage)" "$file" >/dev/null 2>&1; then
  findings+=("Possible cause-based alert (CPU/memory/disk) — prefer a symptom/SLO-burn alert unless this reliably precedes user pain.")
fi
if grep -nEi "(otlp|opentelemetry).*(localhost|127\\.0\\.0\\.1)" "$file" >/dev/null 2>&1; then
  findings+=("OTLP endpoint hardcoded to localhost — confirm this isn't shipping to a per-host collector that won't exist in prod.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── observability-sre advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${OBS_STRICT:-0}" = "1" ]; then
  echo "(blocking: OBS_STRICT=1)" >&2
  exit 2
fi
exit 0
