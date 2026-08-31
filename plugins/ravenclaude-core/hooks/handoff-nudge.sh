#!/usr/bin/env bash
# handoff-nudge.sh — Stop hook. Advisory context-hot nudge.
#
# When comfort-posture context_handoff.mode is nag|block AND live usage is
# at/over the soft threshold, emit Stop additionalContext telling the model
# to run session-handoff NOW. Never writes handoff.md. Never a compact hook.
# Never UserPromptSubmit. Fail-open: EXIT trap first, no set -e.
#
# bash 3.2-safe. Derived values only (engine).
trap 'exit 0' EXIT
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || exit 0
engine="${here}/../scripts/handoff-nudge.py"

[ -f "$engine" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

python3 "$engine" 2>/dev/null || true
exit 0
