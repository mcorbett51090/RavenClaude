#!/usr/bin/env bash
# remind-tests.sh
# Stop hook. If any source files were modified in the working tree this
# session, print a reminder to run the full quality gate before reporting
# the task complete. Output goes to stderr — Claude sees it as a system
# notice, the user sees it in the transcript.

set -euo pipefail

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
