#!/usr/bin/env bash
# emit-permission-denied.sh
# PermissionDenied hook — record auto-mode / permission-system denials in hook-events.jsonl
# so Heimdall and workaround-exhaustion.sh see classifier denials, not only RavenClaude guards.
#
# Input:  PermissionDenied event JSON on stdin (tool_name and optional permission rule fields).
# Output: exit 0 always; never blocks or mutates the denial.
#
# Egress: DERIVED VALUES ONLY — tool name + a fixed/sanitized rule token. Never reads or writes
# tool_input command text, file paths from Bash rules, or other free-form payload fields.

set -uo pipefail
trap 'exit 0' EXIT

here="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd)" || here="."
HOOKNAME="emit-permission-denied.sh"
payload="$(cat 2>/dev/null || true)"

if [ -f "$here/_emit-event.sh" ]; then
  # shellcheck source=/dev/null
  . "$here/_emit-event.sh" 2>/dev/null || true
fi
command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }

_token() { printf '%s' "${1:-}" | tr -dc 'A-Za-z0-9._:*-' | cut -c1-64; }

tool=""
rule_token="permission-denied"
_raw_rule=""

if [ -n "$payload" ]; then
  if command -v jq >/dev/null 2>&1; then
    tool="$(printf '%s' "$payload" | jq -r '.tool_name // .tool // empty' 2>/dev/null || true)"
    _raw_rule="$(printf '%s' "$payload" | jq -r '
      .permission_rule // .permissionRule // .rule // .denied_rule // .deniedRule // empty
    ' 2>/dev/null || true)"
  elif command -v python3 >/dev/null 2>&1; then
    _parsed="$(printf '%s' "$payload" | python3 -c '
import json, sys
try:
    o = json.load(sys.stdin)
except Exception:
    sys.exit(0)
tool = o.get("tool_name") or o.get("tool") or ""
rule = (
    o.get("permission_rule")
    or o.get("permissionRule")
    or o.get("rule")
    or o.get("denied_rule")
    or o.get("deniedRule")
    or ""
)
print(tool)
print(rule)
' 2>/dev/null || true)"
    tool="$(printf '%s' "$_parsed" | sed -n '1p')"
    _raw_rule="$(printf '%s' "$_parsed" | sed -n '2p')"
  fi
fi

if [ -n "$_raw_rule" ]; then
  _san="$(_token "$_raw_rule")"
  if [ -n "$_san" ]; then
    rule_token="permission-rule:${_san}"
  fi
fi

tool="$(_token "$tool")"
[ -z "$tool" ] && tool="unknown"

_emit_hook_event "$HOOKNAME" "deny" "$tool" "" "$rule_token" 0 || true
exit 0
