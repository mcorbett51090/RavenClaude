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

# Classify a worktree. Prints exactly one of: clean | DIRTY | UNKNOWN
#
# ⛔ UNKNOWN is the whole point of this helper. When `git status` itself FAILS —
# not a git repo, a corrupt or absent .git, a linked worktree whose parent repo
# is gone, git missing from PATH, permission denied — it writes NOTHING to
# stdout and exits non-zero. That empty stdout is byte-identical to a genuinely
# clean tree's. So `[ -z "$(git ... 2>/dev/null)" ]` reads a FAILED inspection as
# "clean", and remove_all_clean would then DELETE a worktree it never managed to
# look at. Verified 2026-08-17: a non-git dir yields exit 128 with empty stdout.
#
# Capturing the exit code separately is what splits "I looked and it is clean"
# from "I could not look". Fail toward NOT deleting.
# See docs/best-practices/verification-probe-discipline.md.
worktree_state() { # $1=dir -> prints clean|DIRTY|UNKNOWN
  local out rc=0
  out="$(git -C "$1" status --porcelain 2>/dev/null)" || rc=$?
  if [ "$rc" -ne 0 ]; then
    printf 'UNKNOWN'
  elif [ -z "$out" ]; then
    printf 'clean'
  else
    printf 'DIRTY'
  fi
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
    status="$(worktree_state "$d")"
    printf '  %-30s  %s\n' "$slug" "$status"
  done
}

remove_one() {
  local slug="$1" force="${2:-}"
  if ! printf '%s' "$slug" | grep -qE '^[A-Za-z0-9._-]+$'; then
    printf 'error: slug must match [A-Za-z0-9._-]+\n' >&2
    return 2
  fi
  # The charset above permits '.' — explicitly reject the traversal slugs it would otherwise allow.
  case "$slug" in
    .|..) printf 'error: slug may not be . or ..\n' >&2; return 2 ;;
  esac
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
    case "$(worktree_state "$d")" in
      clean)
        remove_one "$slug" || printf '  skipped %s\n' "$slug"
        ;;
      DIRTY)
        printf '  skipped %s (dirty)\n' "$slug"
        ;;
      *)
        # UNKNOWN — `git status` failed, so we never learned whether this tree
        # holds work. Deleting on an unreadable inspection is the exact defect
        # this case exists to prevent. Skip loudly and let a human look.
        printf '  skipped %s (UNKNOWN — git status failed; inspect by hand, then use: %s %s --force)\n' \
          "$slug" "$0" "$slug"
        ;;
    esac
  done
}

case "${1:-}" in
  --status) list_worktrees ;;
  --all) remove_all_clean ;;
  --help|-h) usage 0 ;;
  "") usage 2 ;;
  *) remove_one "$1" "${2:-}" ;;
esac
