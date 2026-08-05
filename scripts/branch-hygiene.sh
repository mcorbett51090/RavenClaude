#!/usr/bin/env bash
# branch-hygiene.sh — retire provably-merged branches and their worktrees, safely.
#
# WHY THIS EXISTS
#   Feature branches and their worktrees accumulate until nobody can tell which
#   hold real work. The obvious cleanup ("delete anything already merged") is
#   wrong in three specific ways that each cost real work when they bite. This
#   script runs those three checks plus git's own veto, in order, and deletes
#   only what clears all four.
#
#   The gates are NOT redundant. On 2026-08-04, cleaning 31 branches in
#   RavenPower-Website, each of the last three caught something the previous
#   one had already cleared:
#     gate 1 (merged)   passed forge/configurator-v2 -> gate 2 caught 1 uncommitted file
#     gate 2 (clean)    passed forge/page-allowance-reprice -> gate 3 caught open PR #184
#     gate 3 (no PR)    passed forge/portal-intake-tree -> gate 4 (git -d) vetoed it
#   Drop any one gate and you lose something. That is the whole design.
#
# SAFETY POSTURE
#   - Dry-run by DEFAULT. Deleting requires --execute.
#   - Uses `git branch -d`, never -D. Git's own merge check is gate 4, an
#     independent second opinion on gate 1. It is also why this script does not
#     trip guard-destructive.sh (which blocks -D).
#   - Uses `git worktree remove` without --force, so a dirty worktree vetoes
#     itself.
#   - Records every deleted branch + its SHA to a log before deleting.
#
#   DRY-RUN IS LOOSER THAN EXECUTE, deliberately. Gate 4 is `git branch -d`,
#   which only renders a verdict at delete time, so a dry run cannot consult it
#   and may list a branch that --execute then refuses. Erring in this direction
#   is safe: the surprise is always "fewer deleted than predicted", never more.
#   (Observed: portal-intake-tree and pricing-v3 predicted deletable, both
#   vetoed by gate 4 because their remote refs sat 8 commits behind.)
#
# SCOPE — merged branches only. For UNMERGED / abandoned work whose commits are
#   NOT in the base branch, this script refuses (gate 1). That case needs
#   scripts/archive-branch.sh, which tags the tip so it stays recoverable.
#   See AGENTS.md house rule 5.
#
# PORTABILITY: bash 3.2 (stock macOS). No declare -A, mapfile, ${x^^}, globstar,
#   GNU timeout, grep -P, or sed -i. See the macOS-doors milestones in
#   plugins/ravenclaude-core/CLAUDE.md.
#
# USAGE
#   branch-hygiene.sh [--repo DIR] [--base REF] [--pattern GLOB] [--execute]
#   --repo DIR      repository to clean (default: cwd)
#   --base REF      branch things must be merged into (default: origin/main)
#   --pattern GLOB  only consider branches matching (default: all except base)
#   --execute       actually delete (default: report only)

set -euo pipefail

REPO="$PWD"
BASE="origin/main"
PATTERN=""
EXECUTE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --repo)    REPO="$2"; shift 2 ;;
    --base)    BASE="$2"; shift 2 ;;
    --pattern) PATTERN="$2"; shift 2 ;;
    --execute) EXECUTE=1; shift ;;
    -h|--help) sed -n '2,44p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

cd "$REPO" || { echo "not a directory: $REPO" >&2; exit 2; }
git rev-parse --git-dir >/dev/null 2>&1 || { echo "not a git repo: $REPO" >&2; exit 2; }

git fetch origin --quiet 2>/dev/null || echo "warning: fetch failed; '$BASE' may be stale" >&2
git rev-parse --verify --quiet "$BASE" >/dev/null || { echo "base ref not found: $BASE" >&2; exit 2; }

# Gate 3 needs the open-PR list. If gh is unavailable we cannot prove a branch
# has no PR, so we fail CLOSED: every branch is held rather than risk closing a
# PR. An unprovable gate is not a passed gate.
PRS=""
PR_CHECK_OK=0
if command -v gh >/dev/null 2>&1; then
  if PRS="$(gh pr list --state open --json headRefName --jq '.[].headRefName' 2>/dev/null)"; then
    PR_CHECK_OK=1
  fi
fi
[ "$PR_CHECK_OK" -eq 1 ] || echo "warning: no open-PR list (gh missing/unauthenticated) — holding every branch" >&2

BASE_LOCAL="${BASE##*/}"
LOG="${TMPDIR:-/tmp}/branch-hygiene-$(git rev-parse --short HEAD)-$$.log"
deleted=0; held=0

echo "repo: $(pwd)    base: $BASE    mode: $([ "$EXECUTE" -eq 1 ] && echo EXECUTE || echo DRY-RUN)"
echo

for b in $(git for-each-ref --format='%(refname:short)' refs/heads/); do
  [ "$b" = "$BASE_LOCAL" ] && continue
  case "$b" in
    main|master|develop) continue ;;
  esac
  if [ -n "$PATTERN" ]; then
    case "$b" in $PATTERN) ;; *) continue ;; esac
  fi

  sha="$(git rev-parse --short "$b")"

  # --- Gate 1: every commit on this branch is already in the base ---
  if [ "$(git rev-list --count "$BASE".."$b")" != "0" ]; then
    printf "  HOLD    %-38s unmerged commits vs %s\n" "$b" "$BASE"; held=$((held+1)); continue
  fi

  # --- Gate 2: its worktree (if any) has no uncommitted or untracked work ---
  # `|| true` is load-bearing: with `set -o pipefail`, a branch that has NO
  # worktree makes the inner grep exit 1, which under `set -e` aborts the whole
  # run mid-sweep. "No worktree" is the common case, not an error.
  wt="$(git worktree list --porcelain \
        | grep -B2 "^branch refs/heads/$b\$" \
        | grep '^worktree ' | cut -d' ' -f2- | head -1 || true)"
  if [ -n "$wt" ] && [ -d "$wt" ]; then
    dirty="$(git -C "$wt" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
    if [ "$dirty" != "0" ]; then
      printf "  HOLD    %-38s worktree has %s uncommitted/untracked file(s)\n" "$b" "$dirty"
      held=$((held+1)); continue
    fi
  fi

  # --- Gate 3: no open pull request would be closed by deleting it ---
  if [ "$PR_CHECK_OK" -ne 1 ]; then
    printf "  HOLD    %-38s open-PR status unknown (failing closed)\n" "$b"; held=$((held+1)); continue
  fi
  if printf '%s\n' "$PRS" | grep -qx "$b"; then
    printf "  HOLD    %-38s has an open PR\n" "$b"; held=$((held+1)); continue
  fi

  if [ "$EXECUTE" -ne 1 ]; then
    printf "  would delete  %-32s %s\n" "$b" "$sha"; deleted=$((deleted+1)); continue
  fi

  # --- Gate 4: git's own veto. -d refuses anything it does not consider merged. ---
  if [ -n "$wt" ] && [ -d "$wt" ]; then
    git worktree remove "$wt" 2>/dev/null \
      || { printf "  HOLD    %-38s worktree refused removal\n" "$b"; held=$((held+1)); continue; }
  fi
  if git branch -d "$b" >/dev/null 2>&1; then
    echo "$b $sha" >> "$LOG"
    printf "  deleted %-38s was %s\n" "$b" "$sha"; deleted=$((deleted+1))
  else
    printf "  HOLD    %-38s git refused -d (not fully merged to HEAD or upstream)\n" "$b"
    held=$((held+1))
  fi
done

echo
if [ "$EXECUTE" -eq 1 ]; then
  echo "  deleted: $deleted    held: $held"
  [ "$deleted" -gt 0 ] && echo "  record:  $LOG"
else
  echo "  would delete: $deleted    held: $held"
  echo "  (dry run — re-run with --execute to act)"
fi
