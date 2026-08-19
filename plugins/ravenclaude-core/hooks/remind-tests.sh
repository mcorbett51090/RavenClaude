#!/usr/bin/env bash
# remind-tests.sh
# Stop hook. If any source files were modified in the working tree this
# session, print a reminder to run the full quality gate before reporting
# the task complete. Output goes to stderr — Claude sees it as a system
# notice, the user sees it in the transcript.

set -euo pipefail

# ── ADVISORY DELIVERY (added 2026-08-19) ────────────────────────────────────
# ⛔ Stop + stderr + exit 0 is MEASURED UNDELIVERED — confirmed with a TWO-TURN
# test (turn 1 fires the hook, turn 2 asks), so the negative is not merely "the
# model had no turn in which to answer". See _advise.sh's header.
# Buffer fd2 and re-emit at exit as additionalContext, which IS delivered, while
# still printing the original UI notice. No call site below changes.
_rc_hd="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || printf '.')"
if [ -f "$_rc_hd/_advise.sh" ]; then . "$_rc_hd/_advise.sh"; rc_advise_init Stop; fi

# Only run inside a git repo.
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

changed="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
[[ "$changed" -eq 0 ]] && exit 0

# Look for changes in code (not just docs / config). Use awk for both
# filtering and counting so a "no matches" result doesn't break the
# pipeline under `set -e -o pipefail` (the previous grep + wc chain did).
code_changed="$(
  git status --porcelain 2>/dev/null \
    | awk '$2 ~ /\.(ts|tsx|js|jsx|mjs|cjs|py|go|rs|java|kt|rb|php|cs|swift|scala)$/ {n++} END {print n+0}'
)"

[[ "$code_changed" -eq 0 ]] && exit 0

cat >&2 <<'EOF'

────────────────────────────────────────────────────────────────────
  ⚠  Source files changed this session.
  Before declaring the task complete, run the full quality gate:

      /run-full-test-suite

  Format → lint → typecheck → unit → integration. Fail fast.
  See CLAUDE.md §4.
────────────────────────────────────────────────────────────────────

EOF

exit 0
