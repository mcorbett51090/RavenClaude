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
#   scripts/worktree-clean.sh --status            # list worktrees + clean/DIRTY/IGNORED/UNKNOWN
#
# UNKNOWN means `git status` itself failed for that worktree (stale linked
# worktree, corrupt .git, permission denied) — it is NOT another flavour of
# clean. --all skips it and remove_one refuses it, even with --force.
#
# IGNORED means the tree holds nothing tracked or untracked, but DOES hold
# ignored files (.env, node_modules/, a local db). --all skips it and names
# what is there; remove_one refuses it without --force and honours --force,
# because unlike UNKNOWN we can see exactly what would be destroyed.

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

# Classify a worktree. Prints exactly one of: clean | DIRTY | IGNORED | UNKNOWN
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
worktree_state() { # $1=dir -> prints clean|DIRTY|IGNORED|UNKNOWN
  local out rc=0 top
  # ⛔ SECOND HALF OF THE SAME DEFECT: `git status` exiting 0 does NOT mean
  # "I inspected this tree". Git's discovery walks UPWARD — for a plain
  # directory, or a registered worktree whose .git file has been removed, git
  # finds the PARENT repo and reports the parent's status. And because
  # .claude/worktrees/ is gitignored (this repo: .gitignore:47), the directory's
  # own contents are invisible to that parent status, so it returns rc=0 with
  # EMPTY stdout and classifies `clean` — a tree nobody looked at, queued for
  # deletion. Exactly the "empty means nothing there" trap above, one level
  # deeper: there the exit code was ignored, here a success was taken as
  # evidence of the wrong thing.
  #
  # Measured 2026-08-17 in a gitignored-worktrees fixture with a clean parent:
  #   plain dir               -> status rc=0, out_len=0, toplevel=<PARENT>
  #   worktree, .git removed  -> status rc=0, out_len=0, toplevel=<PARENT>
  #   healthy linked worktree -> toplevel=<ITSELF>            (still clean)
  # A healthy worktree's toplevel IS itself, so this costs nothing normally.
  top="$(git -C "$1" rev-parse --show-toplevel 2>/dev/null)" || { printf 'UNKNOWN'; return; }
  [ -n "$top" ] && [ "$top" -ef "$1" ] || { printf 'UNKNOWN'; return; }
  # ⛔ THIRD FACE OF THE SAME DEFECT: a status that ran, against the right tree,
  # and exited 0 can STILL report "nothing here" because CONFIG told it to stay
  # quiet. `status.showUntrackedFiles=no` suppresses untracked files entirely,
  # and `core.excludesFile` can point at a pattern file that hides them. Neither
  # needs an adversary — both are ordinary user settings, and git reads them from
  # the repo-local `.git/config`, `$HOME/.gitconfig`, `$XDG_CONFIG_HOME`, the
  # system config, or `GIT_CONFIG_*`. A worktree holding only untracked work then
  # classifies `clean` and --all deletes it.
  #
  # Measured 2026-08-17 against this script, dirty worktree holding one untracked
  # file, no env vars set at all — just `git config status.showUntrackedFiles no`
  # in the parent repo:
  #   plain `status --porcelain`                       -> clean  -> DELETED
  #   with the two pins below                          -> DIRTY  -> refused
  # and a genuinely clean worktree still reads `clean` under the pins, so this
  # costs nothing normally.
  #
  # Pinning at the CALL SITE is what makes this total: `-c` and an explicit flag
  # outrank every config source, so one change closes repo-local, $HOME,
  # XDG, system and GIT_CONFIG_* at once rather than enumerating them.
  # Out of scope here: a PATH shim or an LD_PRELOAD replacing git itself — those
  # need an adversary who already controls the process, and are handled on the
  # hardening branch. This closes the no-adversary config vectors.
  out="$(git -C "$1" -c core.excludesFile=/dev/null status --porcelain --untracked-files=normal 2>/dev/null)" || rc=$?
  if [ "$rc" -ne 0 ]; then printf 'UNKNOWN'; return; fi
  if [ -n "$out" ]; then printf 'DIRTY'; return; fi

  # ⛔ FOURTH STATE. Nothing tracked is modified and nothing is untracked — but
  # `status --porcelain` is SILENT ON IGNORED FILES BY DESIGN, so "empty" here
  # still does not mean "empty tree". A worktree holding only `.env`,
  # `node_modules/`, a local sqlite db or an un-pushed build classified `clean`
  # and was removed. The credentials case is the one that hurts: `.env` is
  # ignored precisely BECAUSE it is not in git, which makes it unrecoverable —
  # the ignore rule that hides it from this probe is the same rule that means no
  # copy exists anywhere else.
  #
  # This is the same "empty is a claim about the probe" shape a third time, and
  # the narrowest version of it: the probe ran, against the right tree, exited 0,
  # honoured no misleading config — and was still answering a narrower question
  # than the one the caller needed ("is there anything here?" vs "is there
  # anything git is TRACKING here?").
  #
  # Measured 2026-08-17:
  #   fresh worktree of this repo -> 0 ignored entries (so this does not fire
  #                                  on every newly created tree — it would be
  #                                  noise, and a guard that always fires is a
  #                                  guard that gets switched off)
  #   worktree holding .env       -> `!! .env`
  #   node_modules with 5 files   -> `!! node_modules/` (ONE line: `traditional`
  #                                  collapses a wholly-ignored directory rather
  #                                  than walking it, so this stays cheap)
  #
  # Only reached when the tree is otherwise a deletion CANDIDATE, so the extra
  # git call is paid exactly where the care is warranted and nowhere else.
  local ig igrc=0
  ig="$(git -C "$1" -c core.excludesFile=/dev/null status --porcelain --untracked-files=normal --ignored=traditional 2>/dev/null)" || igrc=$?
  # Could not determine -> fail toward NOT deleting, same as any failed probe.
  if [ "$igrc" -ne 0 ]; then printf 'UNKNOWN'; return; fi
  if [ -n "$ig" ]; then printf 'IGNORED'; return; fi
  printf 'clean'
}

# The first few ignored entries, for a message an operator can act on. Bounded:
# a wholly-ignored directory is already one line, but a tree with many distinct
# ignore rules is not, and a skip message is not a place to print 200 paths.
ignored_sample() { # $1=dir
  git -C "$1" -c core.excludesFile=/dev/null status --porcelain \
      --untracked-files=normal --ignored=traditional 2>/dev/null \
    | sed -n 's/^!! //p' | head -3 | tr '\n' ' '
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
  # ⛔ This is the function that actually deletes, so it gets the SAME four-state
  # classification as --all. The previous `[ -n "$(git … 2>/dev/null)" ]` was the
  # identical blind idiom inverted: on a FAILED git status the substitution is
  # empty, `-n` is false, the uncommitted-changes guard never fired, and control
  # reached `git worktree remove` on a tree nobody had inspected. Safety then
  # rested on git's own removal validation — real, but not this script's, and
  # not what the guard claims to do.
  case "$(worktree_state "$wt_dir")" in
    clean) : ;;
    DIRTY)
      if [ "$force" != "--force" ]; then
        printf 'error: worktree has uncommitted changes; pass --force to remove anyway\n' >&2
        return 1
      fi
      ;;
    IGNORED)
      # ⛔ Refused WITHOUT --force, but honoured WITH it — deliberately the DIRTY
      # contract, not the UNKNOWN one. The difference is knowledge, not danger:
      # for UNKNOWN we cannot see what we would destroy, so --force is refused;
      # here we CAN see it, and we name it, so --force is a considered choice
      # rather than a blind one. Treating these two alike would either strand
      # every node_modules tree forever or delete .env files unexamined.
      if [ "$force" != "--force" ]; then
        printf 'error: %s holds only ignored files (%s) — refusing to remove.\n' \
          "$wt_dir" "$(ignored_sample "$wt_dir")" >&2
        printf '       Nothing is tracked here, so git has no copy: an ignored file is\n' >&2
        printf '       unrecoverable once removed. Check it, then pass --force.\n' >&2
        return 1
      fi
      ;;
    *)
      # UNKNOWN — could not inspect. Refuse even with --force: --force discards
      # uncommitted work, and here we do not know whether there is any.
      printf 'error: could not inspect %s (git status failed) — refusing to remove.\n' "$wt_dir" >&2
      printf '       Try: git -C %s worktree repair   (or: worktree prune)\n' "$REPO_ROOT" >&2
      printf '       If you have confirmed by hand there is nothing to keep, move it aside, do not delete.\n' >&2
      return 1
      ;;
  esac
  # `|| return 1` is load-bearing: a bare `git worktree remove` that FAILED fell
  # through to the success printf below and returned 0 — a failed operation
  # rendering as a successful one, the very class this file was edited to close.
  # control (2026-08-17): with `set -euo pipefail`, a function containing
  #   `false; printf REACHED` prints REACHED when invoked as `f || …`, and the
  #   script aborts before REACHED when invoked bare. Same function, opposite
  #   outcomes by invocation context — so `set -e` does not cover this body,
  #   because remove_all_clean calls it as `remove_one … || printf`.
  git -C "$REPO_ROOT" worktree remove "$wt_dir" ${force:+--force} || {
    printf 'error: git worktree remove failed for %s\n' "$wt_dir" >&2
    return 1
  }
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
      IGNORED)
        # Named, with what is actually there, so the operator can decide in one
        # look instead of going to inspect it. --force on the single-slug form is
        # the sanctioned removal path; --all deliberately never forces.
        printf '  skipped %s (holds only ignored files: %s)\n' "$slug" "$(ignored_sample "$d")"
        ;;
      *)
        # UNKNOWN — `git status` failed, so we never learned whether this tree
        # holds work. Deleting on an unreadable inspection is the exact defect
        # this case exists to prevent. Skip loudly and let a human look.
        #
        # ⛔ Deliberately NOT a runnable command. The earlier version printed
        # `<script> <slug> --force`, which was wrong twice: --force is the flag
        # that DISCARDS uncommitted work (exactly what we just failed to rule
        # out), and the slug is unvalidated here — validation lives in
        # remove_one, which UNKNOWN never reaches — so a directory named
        # `x$(id)y` produced a copy-pasteable line that executes on paste.
        # Print the PATH (as data, %s) and a non-destructive remedy instead.
        printf '  skipped %s (UNKNOWN — git status failed; not removed)\n' "$slug"
        printf '      path: %s\n' "$d"
        printf '      try:  git -C %s worktree repair   (or: worktree prune)\n' "$REPO_ROOT"
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
