#!/usr/bin/env bash
# compact-anchor.sh — SessionStart hook, scoped `matcher: "compact"`.
#
# Tells the post-compaction agent that its own pre-compaction record is still on
# disk, where the boundary fell, and how to search it. Thin guard around
# scripts/compact-anchor.py, which owns the parse, the derived-values-only
# invariant, and the emit.
#
# WHY THIS EXISTS. Compaction is append-only — the transcript keeps every turn
# from before the boundary. The post-compaction agent does not lack the data, it
# lacks the knowledge that the data exists. The loss is addressability, not
# durability, so the fix is a pointer. `SessionStart` is the ONLY placement that
# works: `PreCompact`'s stdout is not injected, and only UserPromptSubmit /
# UserPromptExpansion / SessionStart have their stdout added as context.
# See best-practices/precompact-hook-is-the-deterministic-enforcer-of-persist-before-compaction.md
#
# FAIL-OPEN BY CONSTRUCTION. The EXIT trap is armed FIRST, before anything can
# abort, and `-e` is deliberately absent so a failed command cannot become a
# non-zero exit. SessionStart cannot block, but a hook that errors at session
# start is still noise the user has to read, and this hook is a convenience.
#
# bash 3.2-safe (stock macOS): no `declare -A`, no `mapfile`, no `${x^^}`,
# no `shopt -s globstar`. No GNU `timeout`, no `grep -P`, no `sed -i`.
trap 'exit 0' EXIT
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || exit 0
engine="${here}/../scripts/compact-anchor.py"

[ -f "$engine" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

# stdin (the SessionStart payload) is inherited by the engine.
python3 "$engine" 2>/dev/null || true
exit 0
