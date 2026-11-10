#!/usr/bin/env bash
# worktree-cleanup-report.sh — SessionEnd dry-run report for the unified
# worktree + branch lifecycle (scripts/worktree-clean.sh /
# skills/cleanup-worktrees/SKILL.md).
#
# NEVER mutates anything: it runs `worktree-clean.sh --status --no-network`
# (porcelain-wide discovery, zero network calls — see that script's own
# header for why --no-network matters here: a per-worktree `gh pr list` call
# on every session end is unacceptable cost for a hook that fires that
# often) and, when there is anything beyond the solo main worktree to
# report, FLUSHES it to a stable run-artifact file —
# `.ravenclaude/runs/worktree-cleanup/report.md` — for a human or a later
# session to read.
#
# This mirrors the documented SessionEnd contract in
# knowledge/claude-code-permissions.md ("Flush run artifacts, emit a
# summary") and the existing SessionEnd siblings already in this plugin
# (stream-session-close.sh / thing-denial-kb-sync.sh: file writes only,
# never stdout) — a SessionEnd hook's stdout is not injected into any live
# context, because the session is ending and there is no further turn to
# attach `additionalContext`/`systemMessage` to, so this does not attempt
# either.
#
# Opt-out: RC_WORKTREE_CLEANUP_REPORT=off.
# Fail-safe: no git / no bash / no worktree-clean.sh / project dir missing /
# any internal error -> silent no-op, always exits 0 (a SessionEnd hook
# cannot block anyway, and this one must never try to).

set +e

[ "${RC_WORKTREE_CLEANUP_REPORT:-}" = "off" ] && exit 0

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -d "$PROJECT_DIR" ] || exit 0
command -v git >/dev/null 2>&1 || exit 0
command -v bash >/dev/null 2>&1 || exit 0

# Resolve the shipped script: the installed-plugin layout first
# (${CLAUDE_PLUGIN_ROOT}/scripts/worktree-clean.sh — what a consumer who
# installed ravenclaude-core via the marketplace actually has on disk),
# then this marketplace repo's own in-tree layout, then the root shim.
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-}"
SCRIPT=""
if [ -n "$PLUGIN_ROOT" ] && [ -f "$PLUGIN_ROOT/scripts/worktree-clean.sh" ]; then
  SCRIPT="$PLUGIN_ROOT/scripts/worktree-clean.sh"
elif [ -f "$PROJECT_DIR/plugins/ravenclaude-core/scripts/worktree-clean.sh" ]; then
  SCRIPT="$PROJECT_DIR/plugins/ravenclaude-core/scripts/worktree-clean.sh"
elif [ -f "$PROJECT_DIR/scripts/worktree-clean.sh" ]; then
  SCRIPT="$PROJECT_DIR/scripts/worktree-clean.sh"
fi
[ -n "$SCRIPT" ] || exit 0

cd "$PROJECT_DIR" 2>/dev/null || exit 0
git rev-parse --show-toplevel >/dev/null 2>&1 || exit 0

OUT="$(bash "$SCRIPT" --status --no-network 2>/dev/null)"
[ -n "$OUT" ] || exit 0

# Only flush when there is something BEYOND the solo main worktree — a
# report that is all "MAIN" is noise nobody needs to read every session end.
# One "state: " line per non-BARE entry (see worktree-clean.sh's
# print_report); more than one means at least one worktree besides the main
# checkout exists.
n_entries="$(printf '%s\n' "$OUT" | grep -c 'state: ' 2>/dev/null)"
n_entries="${n_entries:-0}"
case "$n_entries" in ''|*[!0-9]*) exit 0 ;; esac
[ "$n_entries" -gt 1 ] || exit 0

RUN_DIR="$PROJECT_DIR/.ravenclaude/runs/worktree-cleanup"
mkdir -p "$RUN_DIR" 2>/dev/null || exit 0
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo unknown-ts)"
{
  printf '# Worktree cleanup — dry-run report\n\n'
  printf 'Generated %s at session end. DRY RUN ONLY — nothing below was removed, pruned,\n' "$TS"
  printf 'or deleted. PR status was not checked (--no-network): a STALE entry may just be\n'
  printf 'one whose open-PR status this report could not verify.\n\n'
  printf 'To act on this:\n'
  printf '  `%s --all --execute`           bulk: removes every "clean" entry, then\n' "$SCRIPT"
  printf '                                       prunes and runs cleanup-branches.sh\n'
  printf '  `%s <slug>` / `--target <path>` one worktree (needs --force for a flagged class)\n' "$SCRIPT"
  printf 'See skills/cleanup-worktrees/SKILL.md.\n\n'
  printf '```\n%s\n```\n' "$OUT"
} > "$RUN_DIR/report.md" 2>/dev/null || exit 0

exit 0
