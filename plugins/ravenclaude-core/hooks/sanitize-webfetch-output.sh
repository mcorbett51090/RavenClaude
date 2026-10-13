#!/usr/bin/env bash
# sanitize-webfetch-output.sh — PostToolUse(WebFetch) wrapper.
#
# FAIL-CLOSED when the sanitizer cannot run (2026-10-13): if python3 or the
# sibling .py is missing, the untrusted WebFetch body is NOT passed through raw.
# The hook emits decision=block with a clear reason and replaces the output
# with a static notice (updatedToolOutput), so the model never reads an
# unscanned body. Built from static strings only: no python, no jq needed.
#
# Still fail-OPEN for sanitizer-internal errors (parse/IO/oversize): the .py
# itself exits 0 and prints nothing in those cases, by its own contract.
set -u
_dir="$(cd "$(dirname "$0")" && pwd)"
_py="${_dir}/sanitize-webfetch-output.py"
_block() {
  # Drain stdin with a builtin so the host never sees a broken pipe.
  while IFS= read -r _l || [ -n "${_l:-}" ]; do _l=; done 2>/dev/null
  printf '%s\n' '{"decision":"block","reason":"[webfetch-sanitize] BLOCKED: python3 (or the sibling sanitize-webfetch-output.py) is missing on this host, so this WebFetch body could not be scanned for injection-shaped content and has been withheld. Install python3 to restore WebFetch results.","hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"[webfetch-sanitize] BLOCKED: python3 (or the sibling sanitize-webfetch-output.py) is missing on this host, so this WebFetch body could not be scanned for injection-shaped content and has been withheld. Install python3 to restore WebFetch results.","updatedToolOutput":"[webfetch-sanitize] BLOCKED: python3 (or the sibling sanitize-webfetch-output.py) is missing on this host, so this WebFetch body could not be scanned for injection-shaped content and has been withheld. Install python3 to restore WebFetch results."}}'
  printf '%s\n' "[webfetch-sanitize] BLOCKED: python3 (or the sibling sanitize-webfetch-output.py) is missing on this host, so this WebFetch body could not be scanned for injection-shaped content and has been withheld. Install python3 to restore WebFetch results." >&2
  exit 0
}
command -v python3 >/dev/null 2>&1 || _block
[ -f "$_py" ] || _block
python3 "$_py" "$@" || exit 0
exit 0
