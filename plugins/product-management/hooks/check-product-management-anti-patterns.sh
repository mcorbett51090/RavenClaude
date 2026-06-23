#!/usr/bin/env bash
# check-product-management-anti-patterns.sh — advisory PreToolUse hook for the product-management plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set PM_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()
if grep -nEi "(roadmap|deliver(y|able)).*(Q[1-4]\\s*20[0-9]{2}|by\\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec))" "$file" >/dev/null 2>&1; then
  findings+=("Dated feature commitment in a product doc — frame the roadmap as outcome bets with confidence; delivery dates belong with project-management.")
fi
if grep -nEi "(total\\s+(signups|users|downloads|registrations)|cumulative\\s+\\w+)" "$file" >/dev/null 2>&1; then
  findings+=("Possible vanity metric (cumulative total) — prefer rates/cohorts/retention that a team can act on.")
fi
if grep -Pzi "(we (will|should) build|the solution is|spec:.*implement)(?![\\s\\S]{0,120}(problem|outcome|because))" "$file" >/dev/null 2>&1; then
  findings+=("Spec leads with a solution, not a problem/outcome — frame the problem + target outcome first; the solution is a hypothesis.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── product-management advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${PM_STRICT:-0}" = "1" ]; then
  echo "(blocking: PM_STRICT=1)" >&2
  exit 2
fi
exit 0
