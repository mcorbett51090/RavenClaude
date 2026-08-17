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
#   scripts/worktree-clean.sh --status            # list worktrees + clean/DIRTY/UNKNOWN
#
# UNKNOWN means `git status` itself failed for that worktree (stale linked
# worktree, corrupt .git, permission denied) — it is NOT a third flavour of
# clean. --all skips it and remove_one refuses it, even with --force.

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
  local out rc=0 top
  # ⛔ FIRST: prove git resolved to THIS directory, not an ancestor.
  # `git status` exiting 0 does NOT mean "I inspected this tree". Git's
  # discovery walks UPWARD: for a plain directory, or a registered worktree
  # whose .git file has been removed, git finds the PARENT repo and reports the
  # parent's status. And because .claude/worktrees/ is gitignored (this repo:
  # .gitignore:47), the directory's own contents are invisible to that parent
  # status — so it comes back rc=0 with EMPTY stdout and classified `clean`,
  # which is precisely the "empty means nothing there" trap this whole file
  # exists to close, one level deeper.
  # Measured 2026-08-17 in a gitignored-worktrees fixture with a clean parent:
  #   plain dir              -> status rc=0, out_len=0, toplevel=<PARENT>  (was: clean)
  #   worktree, .git removed -> status rc=0, out_len=0, toplevel=<PARENT>  (was: clean)
  #   healthy linked worktree-> toplevel=<ITSELF>                          (still clean)
  # A healthy linked worktree's toplevel IS itself, so this costs nothing on
  # the normal path.
  top="$(git -C "$1" rev-parse --show-toplevel 2>/dev/null)" || { printf 'UNKNOWN'; return; }
  [ -n "$top" ] && [ "$top" -ef "$1" ] || { printf 'UNKNOWN'; return; }
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
  # The charset above permits '.' and '-' — reject the traversal slugs and the
  # option-shaped ones it would otherwise allow (`--` makes the NEXT argument
  # land in $force, and `-rf` reads as a flag to anything that forgets to `--`).
  case "$slug" in
    .|..) printf 'error: slug may not be . or ..\n' >&2; return 2 ;;
    -*)   printf 'error: slug may not begin with "-"\n' >&2; return 2 ;;
  esac
  # ⛔ $force is used two ways below: a string compare on the DIRTY branch, and
  # `${force:+--force}` when invoking git. The second expands to --force for ANY
  # non-empty value, so `worktree-clean.sh <slug> --froce` (or -f, or xyz)
  # performed a FORCED removal of a tree classified clean — the typo silently
  # upgraded the operation. Validate once, here, against the exact set.
  case "$force" in
    ''|--force) ;;
    *) printf 'error: unknown flag: %s (expected --force or nothing)\n' "$force" >&2; return 2 ;;
  esac
  local wt_dir="$WT_ROOT/$slug"
  if [ ! -d "$wt_dir" ]; then
    printf 'error: worktree not found: %s\n' "$wt_dir" >&2
    return 1
  fi
  # ⛔ Refuse a symlink. `[ -d ]` and the */ glob both match a symlink-to-dir,
  # `git -C` follows it, and `git worktree remove` resolves it — so the tool
  # deleted the symlink's TARGET, outside .claude/worktrees/, while printing the
  # in-tree path as if that were what went. Reproduced: a symlink to a sibling
  # registered worktree removed the sibling and left the link dangling. A
  # "clean" outside lane can still hold irreplaceable gitignored state
  # (.ravenclaude/runs/, .env, node_modules).
  # The -ef check below catches a link to the repo root but nothing else.
  if [ -L "$wt_dir" ]; then
    printf 'error: %s is a symlink — refusing (it would delete the target, not the link)\n' "$wt_dir" >&2
    return 1
  fi
  if [ "$wt_dir" -ef "$REPO_ROOT" ]; then
    printf 'error: refusing to remove the main working tree\n' >&2
    return 1
  fi
  # ⛔ This is the function that actually deletes, so it gets the SAME three-state
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
    *)
      # UNKNOWN — could not inspect. Refuse even with --force: --force discards
      # uncommitted work, and here we do not know whether there is any.
      #
      # ⛔ Show the REAL diagnostic, not a guessed remedy. The previous version
      # suggested `git worktree repair` / `prune`; both were measured to be
      # no-ops on every UNKNOWN shape constructed (corrupt index: repair rc=0 no
      # output, prune rc=0, state unchanged; chmod 000 .git: repair reports
      # permission denied, prune rc=0, state unchanged). An operator following
      # printed advice that cannot work loops forever — and that pressure is
      # exactly what produces tunnelling (a hand `rm -rf`, or re-adding
      # --force). git's own stderr names the actual cause; print that instead.
      printf 'error: could not inspect %s — refusing to remove.\n' "$wt_dir" >&2
      printf '       git said: ' >&2
      git -C "$wt_dir" status --porcelain 2>&1 >/dev/null | head -1 >&2 || true
      printf '       Fix the cause above, then re-run. Do NOT reach for --force:\n' >&2
      printf '       it discards uncommitted work, and the point is that we could not rule any out.\n' >&2
      printf '       If you have confirmed by hand there is nothing to keep, move it aside rather than delete it.\n' >&2
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
    # Strip the trailing / the glob adds, then strip control characters: a
    # directory name containing a newline otherwise splits the status line and
    # lets an attacker-named directory forge a plausible extra line in the
    # operator's terminal.
    slug="$(basename "${d%/}" | tr -d '\r\n')"
    # Refuse symlinks here too, so the skip message is accurate rather than
    # relying on remove_one to catch it after classification. See remove_one.
    if [ -L "${d%/}" ]; then
      printf '  skipped %s (symlink — refusing; it would delete the target, not the link)\n' "$slug"
      continue
    fi
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
        #
        # ⛔ Deliberately NOT a runnable command. The earlier version printed
        # `<script> <slug> --force`, which was wrong twice: --force is the flag
        # that DISCARDS uncommitted work (exactly what we just failed to rule
        # out), and the slug is unvalidated here — validation lives in
        # remove_one, which UNKNOWN never reaches — so a directory named
        # `x$(id)y` produced a copy-pasteable line that executes on paste.
        # Print the PATH (as data, %s) and git's OWN diagnostic — the earlier
        # `worktree repair`/`prune` suggestion was measured to be a no-op on
        # every UNKNOWN shape constructed, so it sent the operator in a loop.
        printf '  skipped %s (UNKNOWN — could not inspect; not removed)\n' "$slug"
        printf '      path: %s\n' "${d%/}"
        printf '      git said: '
        git -C "${d%/}" status --porcelain 2>&1 >/dev/null | head -1 || true
        printf '      Fix the cause above, then re-run. Do NOT use --force — it discards\n'
        printf '      uncommitted work and the point is that we could not rule any out.\n'
        printf '      If nothing there matters, move it aside rather than delete it.\n'
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
