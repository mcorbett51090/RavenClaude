#!/usr/bin/env bash
# sanitize-mcp-output.sh — PostToolUse(mcp__*) wrapper.
#
# FAIL-CLOSED when the sanitizer cannot run (2026-10-13): if python3 or the
# sibling .py is missing, the untrusted MCP tool result is NOT passed through raw.
# The hook emits decision=block with a clear reason and replaces the output
# with a static notice (updatedToolOutput), so the model never reads an
# unscanned body. Built from static strings only: no python, no jq needed.
#
# Still fail-OPEN for sanitizer-internal errors (parse/IO/oversize): the .py
# itself exits 0 and prints nothing in those cases, by its own contract.
set -u
_dir="$(cd "$(dirname "$0")" && pwd)"
_py="${_dir}/sanitize-mcp-output.py"
_block() {
  # Drain stdin with a builtin so the host never sees a broken pipe.
  while IFS= read -r _l || [ -n "${_l:-}" ]; do _l=; done 2>/dev/null
  printf '%s\n' '{"decision":"block","reason":"[mcp-sanitize] BLOCKED: python3 (or the sibling sanitize-mcp-output.py) is missing on this host, so this MCP tool result could not be scanned for injection-shaped content and has been withheld. Install python3 to restore mcp__* results.","hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"[mcp-sanitize] BLOCKED: python3 (or the sibling sanitize-mcp-output.py) is missing on this host, so this MCP tool result could not be scanned for injection-shaped content and has been withheld. Install python3 to restore mcp__* results.","updatedToolOutput":{"content":[{"type":"text","text":"[mcp-sanitize] BLOCKED: python3 (or the sibling sanitize-mcp-output.py) is missing on this host, so this MCP tool result could not be scanned for injection-shaped content and has been withheld. Install python3 to restore mcp__* results."}]}}}'
  printf '%s\n' "[mcp-sanitize] BLOCKED: python3 (or the sibling sanitize-mcp-output.py) is missing on this host, so this MCP tool result could not be scanned for injection-shaped content and has been withheld. Install python3 to restore mcp__* results." >&2
  exit 0
}
command -v python3 >/dev/null 2>&1 || _block
[ -f "$_py" ] || _block
python3 "$_py" "$@" || exit 0
exit 0
