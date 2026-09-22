#!/usr/bin/env bash
# sanitize-mcp-output.sh — PostToolUse(mcp__*) fail-open wrapper.
#
# Always exits 0. If python3 or the sibling .py is missing, prints nothing
# so the original MCP tool result is left in place.
set -u
_dir="$(cd "$(dirname "$0")" && pwd)"
_py="${_dir}/sanitize-mcp-output.py"
command -v python3 >/dev/null 2>&1 || exit 0
[ -f "$_py" ] || exit 0
python3 "$_py" "$@" || exit 0
exit 0
