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
# cannot block anyway, and this one must never try to). This INCLUDES a
# planted symlink anywhere on the write path (the report file itself, its
# parent directories, or an ancestor under .ravenclaude) — the hook refuses
# rather than following it, silently, same exit-0 contract either way (see
# the symlink-safe write below, AppSec finding F2).

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

# ⛔ SYMLINK-SAFE WRITE (AppSec finding F2, 2026-11-10). PROJECT_DIR is
# CLAUDE_PROJECT_DIR — attacker-influenceable by anyone who can get a victim
# to open a malicious repo (or one with a linked worktree) as a project. A
# repo that commits `.ravenclaude/runs/worktree-cleanup/report.md` as a
# symlink (or symlinks any ancestor directory under `.ravenclaude`) made the
# ORIGINAL `> "$RUN_DIR/report.md"` single-redirection write FOLLOW the link
# and overwrite whatever it pointed at — every session end, on every
# consumer with >=1 linked worktree. Two layers close this, deliberately
# mirroring worktree-clean.sh's own WT_ROOT containment style ("that check
# alone is NOT enough" — a per-component check and a post-mkdir realpath
# re-check catch different attack shapes):
#   (1) refuse a symlink on ANY already-existing path component UNDER
#       .ravenclaude — BEFORE `mkdir -p` ever runs. `mkdir -p` silently
#       no-ops on a directory that already exists, INCLUDING a
#       symlink-to-directory, so this must run first, not after.
#   (2) after `mkdir -p`, re-resolve the real path of the resulting RUN_DIR
#       and require it stay CONTAINED under PROJECT_DIR's own real path —
#       closes the case where an ancestor already existed as a symlink and
#       (1)'s per-component scan raced with something else creating it.
# And the write itself never redirects straight to the final path either
# way: it writes a mktemp'd sibling file INSIDE the now-verified RUN_DIR,
# then `mv`s it into place. On the same filesystem `mv` is a rename(2),
# which replaces a symlink's OWN directory entry rather than dereferencing
# it to its target — so even a report.md planted as a symlink cannot be
# written-through by the final step.
PROJECT_REAL="$(cd "$PROJECT_DIR" 2>/dev/null && pwd -P)" || exit 0
[ -n "$PROJECT_REAL" ] || exit 0

_rcwcr_dir="$PROJECT_DIR"
for _rcwcr_seg in .ravenclaude runs worktree-cleanup; do
  _rcwcr_dir="$_rcwcr_dir/$_rcwcr_seg"
  if [ -L "$_rcwcr_dir" ]; then
    exit 0   # a path component is a symlink -- refuse, never follow it
  fi
done
unset _rcwcr_dir _rcwcr_seg

RUN_DIR="$PROJECT_DIR/.ravenclaude/runs/worktree-cleanup"
mkdir -p "$RUN_DIR" 2>/dev/null || exit 0

RUN_DIR_REAL="$(cd "$RUN_DIR" 2>/dev/null && pwd -P)" || exit 0
case "$RUN_DIR_REAL/" in
  "$PROJECT_REAL"/*) ;;
  *) exit 0 ;;
esac

REPORT_FILE="$RUN_DIR/report.md"
[ -L "$REPORT_FILE" ] && exit 0   # the final file itself must not already be a symlink

TS="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo unknown-ts)"
TMP_REPORT="$(mktemp "$RUN_DIR/.report.XXXXXX" 2>/dev/null)" || exit 0
{
  printf '# Worktree cleanup — dry-run report\n\n'
  printf 'Generated %s at session end. DRY RUN ONLY — nothing below was removed, pruned,\n' "$TS"
  printf 'or deleted. PR status was not checked (--no-network): a PR-UNKNOWN entry is one\n'
  printf 'whose open-PR status could not be verified (never treated as clean — refuses\n'
  printf 'removal even with --force); a STALE entry may ALSO carry an unverified PR status\n'
  printf 'when its commit is old enough that age alone already flags it.\n\n'
  printf 'To act on this:\n'
  printf '  `%s --all --execute`           bulk: removes every "clean" entry, then\n' "$SCRIPT"
  printf '                                       prunes and runs cleanup-branches.sh\n'
  printf '  `%s <slug>` / `--target <path>` one worktree (needs --force for a flagged class)\n' "$SCRIPT"
  printf 'See skills/cleanup-worktrees/SKILL.md.\n\n'
  printf '```\n%s\n```\n' "$OUT"
} > "$TMP_REPORT" 2>/dev/null || { rm -f "$TMP_REPORT" 2>/dev/null; exit 0; }
mv -f "$TMP_REPORT" "$REPORT_FILE" 2>/dev/null || { rm -f "$TMP_REPORT" 2>/dev/null; exit 0; }

exit 0
