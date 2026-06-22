#!/usr/bin/env bash
# worktree-clean.sh — remove a worktree created by worktree-new.sh.
#
# Safer than `git worktree remove` directly: refuses to delete a worktree with
# uncommitted changes unless --force is passed, and never touches the main
# working tree. See plugins/ravenclaude-core/skills/cleanup-worktrees/SKILL.md.
#
# Usage:
#   scripts/worktree-clean.sh <slug>              # remove if clean
#   scripts/worktree-clean.sh <slug> --force      # remove even if dirty
#   scripts/worktree-clean.sh --all               # remove all clean worktrees
#   scripts/worktree-clean.sh --status            # list worktrees + clean/dirty

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
WT_ROOT="$REPO_ROOT/.claude/worktrees"

usage() {
  cat <<EOF >&2
usage: $0 <slug> [--force]
       $0 --all
       $0 --status
EOF
  exit "${1:-2}"
}

list_worktrees() {
  if [ ! -d "$WT_ROOT" ]; then
    printf 'no worktrees (%s missing)\n' "$WT_ROOT"
    return 0
  fi
  for d in "$WT_ROOT"/*/; do
    [ -d "$d" ] || continue
    local slug
    slug="$(basename "$d")"
    local status
    if [ -z "$(git -C "$d" status --porcelain 2>/dev/null)" ]; then
      status="clean"
    else
      status="DIRTY"
    fi
    printf '  %-30s  %s\n' "$slug" "$status"
  done
}

remove_one() {
  local slug="$1" force="${2:-}"
  if ! printf '%s' "$slug" | grep -qE '^[A-Za-z0-9._-]+$'; then
    printf 'error: slug must match [A-Za-z0-9._-]+\n' >&2
    return 2
  fi
  local wt_dir="$WT_ROOT/$slug"
  if [ ! -d "$wt_dir" ]; then
    printf 'error: worktree not found: %s\n' "$wt_dir" >&2
    return 1
  fi
  if [ "$wt_dir" -ef "$REPO_ROOT" ]; then
    printf 'error: refusing to remove the main working tree\n' >&2
    return 1
  fi
  if [ -n "$(git -C "$wt_dir" status --porcelain 2>/dev/null)" ]; then
    if [ "$force" != "--force" ]; then
      printf 'error: worktree has uncommitted changes; pass --force to remove anyway\n' >&2
      return 1
    fi
  fi
  git -C "$REPO_ROOT" worktree remove "$wt_dir" ${force:+--force}
  # Best-effort: delete the matching agent/ branch only if it's fully merged.
  local branch="agent/$slug"
  if git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/$branch"; then
    git -C "$REPO_ROOT" branch -d "$branch" 2>/dev/null \
      && printf '  deleted branch %s\n' "$branch" \
      || printf '  branch %s left (not fully merged)\n' "$branch"
  fi
  printf '  removed %s\n' "$wt_dir"
}

remove_all_clean() {
  if [ ! -d "$WT_ROOT" ]; then
    printf 'no worktrees (%s missing)\n' "$WT_ROOT"
    return 0
  fi
  for d in "$WT_ROOT"/*/; do
    [ -d "$d" ] || continue
    local slug
    slug="$(basename "$d")"
    if [ -z "$(git -C "$d" status --porcelain 2>/dev/null)" ]; then
      remove_one "$slug" || printf '  skipped %s\n' "$slug"
    else
      printf '  skipped %s (dirty)\n' "$slug"
    fi
  done
}

case "${1:-}" in
  --status) list_worktrees ;;
  --all) remove_all_clean ;;
  --help|-h) usage 0 ;;
  "") usage 2 ;;
  *) remove_one "$1" "${2:-}" ;;
esac
