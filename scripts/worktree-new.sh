#!/usr/bin/env bash
# worktree-new.sh — create an isolated git worktree under .claude/worktrees/<slug>.
#
# Thin wrapper around `git worktree add`. Used by sub-agent dispatch so parallel
# specialists can't collide on the working tree. See
# plugins/ravenclaude-core/skills/new-worktree/SKILL.md for the canonical flow.
#
# Usage:
#   scripts/worktree-new.sh <slug>                  # branch off current HEAD
#   scripts/worktree-new.sh <slug> <base-ref>       # branch off a specific ref
#
# The slug is the leaf directory name AND the branch name. Allowed: [A-Za-z0-9._-].

set -euo pipefail

SLUG="${1:-}"
BASE_REF="${2:-HEAD}"

if [ -z "$SLUG" ]; then
  printf 'usage: %s <slug> [<base-ref>]\n' "$0" >&2
  exit 2
fi

# Enforce slug shape so a malicious slug can't traverse out of .claude/worktrees/.
# ⛔ A bash `case` pattern, NOT `printf … | grep -qE '^…$'`. grep anchors PER LINE
# and -q succeeds if ANY line matches, so a multi-line slug (e.g. $'ok\n../../x')
# passed the grep check whose error message promises a strict charset — the leaked
# line then lands verbatim in $WT_DIR and traverses out of .claude/worktrees/. The
# case pattern has no line semantics and no subprocess. Sibling worktree-clean.sh's
# remove_one() documents and fixed this exact bug class; this is the ported fix.
case "$SLUG" in
  ''|*[!A-Za-z0-9._-]*)
    printf 'error: slug must match [A-Za-z0-9._-]+\n' >&2
    exit 2
    ;;
esac
# The charset above permits '.' and '-' — reject the traversal slugs and the
# option-shaped ones it would otherwise allow (a leading '-' reads as a flag).
case "$SLUG" in
  .|..) printf 'error: slug may not be . or ..\n' >&2; exit 2 ;;
  -*)   printf 'error: slug may not begin with "-"\n' >&2; exit 2 ;;
esac

REPO_ROOT="$(git rev-parse --show-toplevel)"
WT_DIR="$REPO_ROOT/.claude/worktrees/$SLUG"
BRANCH="agent/$SLUG"

if [ -e "$WT_DIR" ]; then
  printf 'error: worktree path already exists: %s\n' "$WT_DIR" >&2
  exit 1
fi

mkdir -p "$REPO_ROOT/.claude/worktrees"

# If the branch already exists, attach to it; otherwise create from BASE_REF.
# A literal `--` separates flags from the path/ref operands so an unvalidated,
# flag-shaped BASE_REF (e.g. `--no-checkout`) is parsed as the commit-ish, not as
# a git option — which would otherwise silently produce an empty, unusable worktree.
if git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/$BRANCH"; then
  git -C "$REPO_ROOT" worktree add -- "$WT_DIR" "$BRANCH"
else
  git -C "$REPO_ROOT" worktree add -b "$BRANCH" -- "$WT_DIR" "$BASE_REF"
fi

printf '\n== Worktree ready ==\n  path:   %s\n  branch: %s\n  base:   %s\n' \
  "$WT_DIR" "$BRANCH" "$BASE_REF"
printf '\nWhen done: scripts/worktree-clean.sh %s\n' "$SLUG"
