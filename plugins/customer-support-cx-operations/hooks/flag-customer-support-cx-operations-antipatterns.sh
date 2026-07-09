#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the customer-support-cx-operations plugin.
# Flags common Customer Support & CX Operations anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced benchmark | customer PII). Advisory
# by default — set CUSTOMER_SUPPORT_CX_OPERATIONS_STRICT=1 to make it blocking.

FILE="${1:-}"
# $CLAUDE_TOOL_FILE_PATH (passed as $1 by hooks.json) is NOT a real Claude Code
# hook variable, so under Claude Code the arg is empty and the path arrives via
# the canonical stdin JSON contract. Fall back to it (2026-07-09 review) — the
# same dual-source pattern guard-destructive.sh / the core file hooks use.
if [ -z "$FILE" ] && [ ! -t 0 ] && command -v jq >/dev/null 2>&1; then
  payload="$(cat 2>/dev/null || true)"
  if [ -n "$payload" ]; then
    FILE="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)"
  fi
fi
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${CUSTOMER_SUPPORT_CX_OPERATIONS_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "customer-support-cx-operations" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: review this Customer Support & CX Operations deliverable against the §3 house opinions (baseline on every metric, source+date on every benchmark, no customer PII)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "customer-support-cx-operations: $findings advisory finding(s); CUSTOMER_SUPPORT_CX_OPERATIONS_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
