#!/usr/bin/env bash
# sanitize-webfetch-output.sh — PostToolUse(WebFetch) wrapper.
#
# FAIL-CLOSED whenever the sanitizer cannot scan: if python3, the sibling .py, or
# its real transitive dependency (scripts/sanitize-webfetch-body.py) is missing,
# OR the .py exits non-zero (a crash, an ImportError, a SyntaxError in the shared
# body sanitizer) OR it runs past its time bound, the untrusted WebFetch body is
# NOT passed through raw. The hook emits decision=block with a clear reason and
# replaces the output with a static notice (updatedToolOutput), so the model never
# reads an unscanned body. Built from static strings only: no python, no jq.
#
# The .py itself exits 0 and prints nothing for its own parse/IO/oversize cases,
# by its contract, and that pass-through is unchanged. Before 2026-10-19 a CRASH
# of the .py also passed the body through (`|| exit 0`), and nothing bounded a
# hostile body that drove the sanitizer quadratic; both now block.
set -u
_dir="$(cd "$(dirname "$0")" && pwd)"
_py="${_dir}/sanitize-webfetch-output.py"
_dep="${_dir}/../scripts/sanitize-webfetch-body.py"
# _rc_timeout (timeout -> gtimeout -> perl alarm). Absent helper: run unbounded,
# the house degradation for a missing _portable.sh.
# shellcheck source=/dev/null
[ -f "${_dir}/_portable.sh" ] && . "${_dir}/_portable.sh"
command -v _rc_timeout >/dev/null 2>&1 || _rc_timeout() { shift; "$@"; }

_MISSING="python3 (or the sibling sanitize-webfetch-output.py, or scripts/sanitize-webfetch-body.py) is missing on this host"
_MISSING_FIX="Install python3 to restore WebFetch results."
_FAILED="the sanitizer failed or timed out on this body"
_FAILED_FIX="Re-run the fetch; if it repeats, check scripts/sanitize-webfetch-body.py."

_block() {
  # $1/$2 are ALWAYS one of the fixed phrases above, never caller data, so the
  # envelope stays valid JSON by construction.
  local msg="[webfetch-sanitize] BLOCKED: ${1}, so this WebFetch body could not be scanned for injection-shaped content and has been withheld. ${2}"
  # Drain stdin with a builtin so the host never sees a broken pipe.
  while IFS= read -r _l || [ -n "${_l:-}" ]; do _l=; done 2>/dev/null
  printf '{"decision":"block","reason":"%s","hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"%s","updatedToolOutput":"%s"}}\n' "$msg" "$msg" "$msg"
  printf '%s\n' "$msg" >&2
  exit 0
}
command -v python3 >/dev/null 2>&1 || _block "$_MISSING" "$_MISSING_FIX"
[ -f "$_py" ] || _block "$_MISSING" "$_MISSING_FIX"
[ -f "$_dep" ] || _block "$_MISSING" "$_MISSING_FIX"
_rc=0
_out="$(_rc_timeout "${RC_SANITIZE_TIMEOUT:-10}" python3 "$_py" "$@")" || _rc=$?
[ "$_rc" -eq 0 ] || _block "$_FAILED" "$_FAILED_FIX"
[ -n "$_out" ] && printf '%s\n' "$_out"
exit 0
