#!/usr/bin/env bash
# check-manufacturing-operations-anti-patterns.sh — advisory PreToolUse hook for the manufacturing-operations plugin.
# Flags mechanically-detectable manufacturing anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set MFG_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# 1. An OEE figure quoted without a stated ideal cycle time / downtime basis — undefined denominators = theater.
if grep -qiE "\bOEE\b" "$file" 2>/dev/null; then
  if ! grep -qiE "(ideal\s+cycle\s+time|cycle\s+time|planned\s+downtime|unplanned\s+downtime|availability.*performance.*quality)" "$file" 2>/dev/null; then
    findings+=("OEE referenced with no stated ideal cycle time / downtime basis — define the denominators or the number is uncomparable theater.")
  fi
fi

# 2. A CAPA/NCR that contains containment but no root-cause or preventive action — the defect will recur.
if grep -qiE "\b(CAPA|NCR|nonconformance|non-conformance)\b" "$file" 2>/dev/null \
  && grep -qiE "\b(contain|containment|scrap|rework)\b" "$file" 2>/dev/null; then
  if ! grep -qiE "(root[ -]?cause|preventive\s+action|5[ -]?why|fishbone|ishikawa|corrective\s+and\s+preventive)" "$file" 2>/dev/null; then
    findings+=("CAPA/NCR with containment but no root-cause / preventive action — containment alone is not a CAPA; the defect is scheduled to recur.")
  fi
fi

# 3. A master schedule / MPS asserted with no capacity or constraint reference — infinite-capacity planning.
if grep -qiE "(master\s+schedule|\bMPS\b|production\s+schedule)" "$file" 2>/dev/null; then
  if ! grep -qiE "(capacity|bottleneck|constraint|finite|takt|load)" "$file" 2>/dev/null; then
    findings+=("Master schedule / MPS with no capacity or constraint reference — plan to the bottleneck's finite rate, not to infinite capacity.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── manufacturing-operations advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${MFG_STRICT:-0}" = "1" ]; then
  echo "(blocking: MFG_STRICT=1)" >&2
  exit 2
fi
exit 0
