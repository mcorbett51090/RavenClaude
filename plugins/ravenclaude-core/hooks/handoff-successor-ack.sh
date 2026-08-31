#!/usr/bin/env bash
# handoff-successor-ack.sh — SessionStart (matcher: startup).
#
# When a pending handoff exists for this project, write successor-ack.json
# so the originating spawn can see that the new session started.
# SessionStart stdout is IGNORED on Grok — this is a file write, not injection.
# Fail-open. Never echo transcript. bash 3.2.
trap 'exit 0' EXIT
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || exit 0
engine="${here}/../scripts/handoff-successor-ack.py"
[ -f "$engine" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0
python3 "$engine" 2>/dev/null || true
exit 0
