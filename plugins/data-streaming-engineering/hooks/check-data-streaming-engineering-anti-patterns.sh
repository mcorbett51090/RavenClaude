#!/usr/bin/env bash
# check-data-streaming-engineering-anti-patterns.sh — advisory PreToolUse hook for the data-streaming-engineering plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set STREAM_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()
if grep -nEi "(processingTime|ProcessingTime|TimeCharacteristic\\.ProcessingTime)" "$file" >/dev/null 2>&1; then
  findings+=("Processing-time used for windowing/aggregation — prefer event-time + watermarks for correctness with late/out-of-order events.")
fi
if grep -nEi "(acks\\s*=\\s*['\\\"]?0|acks\\s*=\\s*['\\\"]?1\\b)" "$file" >/dev/null 2>&1; then
  findings+=("Producer acks=0/1 — risks data loss; use acks=all (+ idempotent producer) for durability unless loss is acceptable.")
fi
if grep -nEi "(send|produce)\\([\\s\\S]{0,80}(commit|save|update)|(commit|save|update)[\\s\\S]{0,80}(producer\\.send|kafka)" "$file" >/dev/null 2>&1; then
  findings+=("Possible dual-write (DB write + produce separately) — use CDC/transactional outbox so events match committed state.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── data-streaming-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${STREAM_STRICT:-0}" = "1" ]; then
  echo "(blocking: STREAM_STRICT=1)" >&2
  exit 2
fi
exit 0
