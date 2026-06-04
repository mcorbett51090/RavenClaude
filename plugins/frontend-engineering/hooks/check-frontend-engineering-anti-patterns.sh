#!/usr/bin/env bash
# check-frontend-engineering-anti-patterns.sh — advisory PreToolUse hook for the frontend-engineering plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set FE_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()
if grep -nEi ":\\s*any\\b|<any>|as any\\b" "$file" >/dev/null 2>&1; then
  findings+=("TypeScript `any` — type the boundary; `any` at API/prop seams is a runtime bug waiting.")
fi
if grep -nEi "<div[^>]*onClick|<span[^>]*onClick" "$file" >/dev/null 2>&1; then
  findings+=("Click handler on a div/span — use a real <button>/<a> for keyboard + screen-reader accessibility.")
fi
if grep -nEi "useEffect\\([^,]+,\\s*\\[\\s*\\]\\s*\\)[\\s\\S]{0,200}(props\\.|state)" "$file" >/dev/null 2>&1; then
  findings+=("useEffect with [] deps referencing props/state — likely a stale-closure/missing-dep bug.")
fi
if grep -nEi "dangerouslySetInnerHTML" "$file" >/dev/null 2>&1; then
  findings+=("dangerouslySetInnerHTML — XSS risk; sanitize, or avoid raw HTML injection.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── frontend-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${FE_STRICT:-0}" = "1" ]; then
  echo "(blocking: FE_STRICT=1)" >&2
  exit 2
fi
exit 0
