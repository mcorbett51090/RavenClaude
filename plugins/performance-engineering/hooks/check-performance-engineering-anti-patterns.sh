#!/usr/bin/env bash
# check-performance-engineering-anti-patterns.sh — advisory PreToolUse hook for the performance-engineering plugin.
# Flags mechanically-detectable performance anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set PERF_STRICT=1 to make it blocking (exit 2).
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

# 1. A performance target/NFR with no load attached or no percentile — the §4 #1 / #2 rules.
#    Heuristic: a line that sets a latency target (ms/p50/p95/p99) but the file mentions no req/s or RPS load.
if grep -qiE "(p9[0-9]|p50|latency|response\s*time).*(<=?|<|target|budget|SLA|SLO)" "$file" 2>/dev/null \
  || grep -qiE "(target|budget|nfr).*(latency|response\s*time|ms\b)" "$file" 2>/dev/null; then
  if ! grep -qiE "(req/s|rps|requests?/s|requests? per second|arrival rate|throughput|concurrent|vus?\b)" "$file" 2>/dev/null; then
    findings+=("A latency target with no load attached — state the percentile + threshold + the load it holds at (e.g. 'p99 <= 200 ms at 5,000 req/s'). A target with no workload is unfalsifiable.")
  fi
fi

# 2. An assertion on average/mean latency instead of a percentile — the §4 #2 rule.
if grep -qiE "(average|mean|avg)[ _-]*(latency|response\s*time|duration)" "$file" 2>/dev/null \
  || grep -qiE "(latency|response\s*time|duration)[ _-]*(average|mean|avg)" "$file" 2>/dev/null; then
  findings+=("Average/mean latency used as a target or assertion — report p95/p99/max instead; the mean hides the tail that pages you.")
fi

# 3. A load-test script that pins neither think time nor an arrival rate — likely a stampede / coordinated-omission risk.
if grep -qiE "(k6|gatling|locust|jmeter|import http from)" "$file" 2>/dev/null \
  || grep -qiE "(scenarios?|executor|virtual users?|\bvus?\b)" "$file" 2>/dev/null; then
  if ! grep -qiE "(think|sleep|pacing|arrival|rate|constant-arrival|ramping-arrival|throughput)" "$file" 2>/dev/null; then
    findings+=("Load-test scenario with no think time and no arrival rate — a zero-think-time closed loop measures a stampede and risks coordinated omission. Set an open arrival-rate executor or explicit think time.")
  fi
fi

# 4. A regression claim with no baseline — the §4 #8 rule.
if grep -qiE "(regress|slower|faster|degrad|improv)" "$file" 2>/dev/null; then
  if ! grep -qiE "(baseline|threshold|delta|compared? to|vs\.?\s|reference run)" "$file" 2>/dev/null; then
    findings+=("A performance regression/improvement claim with no baseline or threshold — gate on a committed baseline + a p95/p99 delta, not 'feels slower'.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── performance-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${PERF_STRICT:-0}" = "1" ]; then
  echo "(blocking: PERF_STRICT=1)" >&2
  exit 2
fi
exit 0
