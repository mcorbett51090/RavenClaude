#!/usr/bin/env bash
# sanitize-webfetch-output.sh — PostToolUse(WebFetch) fail-open wrapper.
#
# Always exits 0. If python3 or the sibling .py is missing, prints nothing
# so the original WebFetch body is left in place.
set -u
_dir="$(cd "$(dirname "$0")" && pwd)"
_py="${_dir}/sanitize-webfetch-output.py"
command -v python3 >/dev/null 2>&1 || exit 0
[ -f "$_py" ] || exit 0
python3 "$_py" "$@" || exit 0
exit 0
