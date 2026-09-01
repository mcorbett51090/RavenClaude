#!/usr/bin/env bash
# remind-tests.sh
# Stop hook. If any source files were modified in the working tree this
# session, print a reminder to run the full quality gate before reporting
# the task complete. Fires ONCE per session — see rc-state-key below.
#
# rc-state-key: "${cwd}/.ravenclaude/runs/remind-tests/" + session_id
# rc-state-scope: session — a Stop hook fires on every turn boundary, so a
#   session that polls (e.g. waiting on a subagent) ends dozens of turns
#   while the same uncommitted files sit untouched; without a per-session
#   latch this hook re-injected the identical notice on every one of those
#   turns (hit in session 1a4354d8, 2026-09-01: 40+ repeats in ~12 minutes,
#   roughly every 10-30s, matching the polling cadence). One reminder per
#   session is enough — the model doesn't forget it was told.
# rc-state-escape: none — a new session_id starts fresh, so there is no
#   stale state to escape from.
#
# Output goes to stderr — Claude sees it as a system notice, the user sees
# it in the transcript.

set -uo pipefail

# ── ADVISORY DELIVERY (added 2026-08-19) ────────────────────────────────────
# ⛔ Stop + stderr + exit 0 is MEASURED UNDELIVERED — confirmed with a TWO-TURN
# test (turn 1 fires the hook, turn 2 asks), so the negative is not merely "the
# model had no turn in which to answer". See _advise.sh's header.
# Buffer fd2 and re-emit at exit as additionalContext, which IS delivered, while
# still printing the original UI notice. No call site below changes.
_rc_hd="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || printf '.')"
if [ -f "$_rc_hd/_advise.sh" ]; then . "$_rc_hd/_advise.sh"; rc_advise_init Stop; fi

payload=""
[ ! -t 0 ] && payload="$(cat 2>/dev/null || true)"

cwd=""
if command -v jq >/dev/null 2>&1 && [ -n "$payload" ]; then
  cwd="$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null)"
fi
[ -z "$cwd" ] && cwd="$PWD"

# Only run inside a git repo.
git -C "$cwd" rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

changed="$(git -C "$cwd" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
[ "$changed" -eq 0 ] && exit 0

# Look for changes in code (not just docs / config). Use awk for both
# filtering and counting so a "no matches" result doesn't break the
# pipeline under `set -e -o pipefail` (the previous grep + wc chain did).
code_changed="$(
  git -C "$cwd" status --porcelain 2>/dev/null \
    | awk '$2 ~ /\.(ts|tsx|js|jsx|mjs|cjs|py|go|rs|java|kt|rb|php|cs|swift|scala)$/ {n++} END {print n+0}'
)"

[ "$code_changed" -eq 0 ] && exit 0

# Once-per-session latch — see rc-state-key above. A missing/unparseable
# session_id (or a marker write that fails, e.g. read-only fs) fails OPEN
# toward reminding, never toward silence: dedup is best-effort, the reminder
# itself is the load-bearing behavior.
if command -v jq >/dev/null 2>&1 && [ -n "$payload" ]; then
  sid="$(printf '%s' "$payload" | jq -r '.session_id // empty' 2>/dev/null)"
  if [ -n "$sid" ]; then
    safe_sid="$(printf '%s' "$sid" | tr -dc 'A-Za-z0-9._-' | cut -c1-128)"
    if [ -n "$safe_sid" ]; then
      dir="${cwd}/.ravenclaude/runs/remind-tests"
      marker="${dir}/${safe_sid}.shown"
      if [ -f "$marker" ]; then
        exit 0
      fi
      mkdir -p "$dir" 2>/dev/null && : > "$marker" 2>/dev/null
    fi
  fi
fi

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
