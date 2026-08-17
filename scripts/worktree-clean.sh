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

# ⛔ Scrub the git environment on EVERY git call in this script. `git -C <dir>`
# resolves against $dir PLUS the ambient git env, so an exported GIT_DIR makes
# `rev-parse --show-toplevel` return the inspected directory for an arbitrary
# non-worktree (defeating the containment check below), and GIT_WORK_TREE makes
# every healthy worktree read UNKNOWN (breaking ordinary cleanup entirely).
# Git hooks routinely export GIT_DIR, so this is not a contrived environment.
# Measured 2026-08-17: baseline plain=UNKNOWN/w1=clean; GIT_DIR exported ->
# plain=DIRTY (containment bypassed); GIT_WORK_TREE+GIT_DIR -> all UNKNOWN.
# ⛔ ALLOWLIST BY CONSTRUCTION — scrub EVERY GIT_* variable, not a named list.
# A blocklist of six was tried and was defeated by the config-injection family:
# GIT_CONFIG_GLOBAL / GIT_CONFIG_SYSTEM / GIT_CONFIG_COUNT+KEY_n+VALUE_n /
# GIT_CONFIG_PARAMETERS each set `status.showUntrackedFiles=no`, which flips a
# DIRTY worktree to `clean` and reaches the deletion path. Measured: with
# GIT_CONFIG_GLOBAL set, --all deleted a worktree whose only copy of the work
# was an untracked file.
#
# Naming more variables would repeat the mistake — the class is "anything git
# reads from the environment", so enumerate it from the environment itself.
# (`env -uall` is NOT a substitute: measured, it defeats GIT_CONFIG_PARAMETERS
# and GIT_CONFIG_GLOBAL but NOT the GIT_CONFIG_COUNT form.)
rcgit() {
  local _u=() _v
  for _v in $(env | sed -n 's/^\(GIT_[A-Za-z0-9_]*\)=.*/\1/p'); do
    _u+=(-u "$_v")
  done
  # bash 3.2: an empty array under `set -u` errors on plain "${_u[@]}".
  env ${_u[@]+"${_u[@]}"} git "$@"
}

# Strip terminal control characters from anything attacker-influenced before it
# is printed. A directory name carrying ESC[2K + CR erases its own row and
# repaints a forged one ("SAFE-LOOKING … clean"); a newline forges an extra row.
# Applies to slugs AND paths, in every printing function.
sanitize() { LC_ALL=C tr -d '\000-\037\177'; }

REPO_ROOT="$(rcgit rev-parse --show-toplevel)"
WT_ROOT="$REPO_ROOT/.claude/worktrees"

# ⛔ ANCHOR CONTAINMENT TO THE REPO, ONCE, AT DERIVATION.
# A `[ -L "$WT_ROOT" ]` refusal was tried and closed only the `.claude/worktrees`
# shape. When `.claude` ITSELF is the symlink, WT_ROOT is not a link, the guard
# passes, and every per-entry containment test then compares children against an
# already-redirected root — so containment is satisfied trivially and worktrees
# OUTSIDE the repo are deleted while the in-repo path is printed. Reproduced on
# both call sites.
#
# Resolving WT_ROOT and requiring it under the resolved REPO_ROOT closes every
# ancestor shape at once, because it constrains the ROOT rather than enumerating
# which component might be a link. --status, --all and remove_one all inherit it.
if [ -d "$WT_ROOT" ]; then
  _repo_real="$(cd "$REPO_ROOT" 2>/dev/null && pwd -P)" || {
    printf 'error: could not resolve %s — refusing\n' "$REPO_ROOT" >&2; exit 1; }
  _root_real="$(cd "$WT_ROOT" 2>/dev/null && pwd -P)" || {
    printf 'error: could not resolve %s — refusing\n' "$WT_ROOT" >&2; exit 1; }
  case "$_root_real/" in
    "$_repo_real"/*) ;;
    *)
      printf 'error: %s resolves to %s, outside the repository at %s — refusing\n' \
        "$WT_ROOT" "$_root_real" "$_repo_real" >&2
      exit 1
      ;;
  esac
fi

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
  # A worktree's .git is the fact that makes discovery STOP here rather than
  # walking up. Cheapest possible precondition, and it closes the upward-walk
  # class more directly than the resolution check alone.
  # ⛔ Split EACCES out. `[ -e ]` fails for ANY reason including permission
  # denied, and reporting that as UNKNOWN-scope produced a message that was both
  # blank and FALSE — "git resolves this directory to , not itself … it is not a
  # worktree" for a perfectly good worktree the process simply cannot read.
  # Wrong advice is the pressure that produces tunnelling.
  if [ ! -e "$1/.git" ]; then
    if [ -r "$1" ]; then printf 'UNKNOWN-scope'; else printf 'UNKNOWN-perm'; fi
    return
  fi
  top="$(rcgit -C "$1" rev-parse --show-toplevel 2>/dev/null)" || { printf 'UNKNOWN-rc'; return; }
  [ -n "$top" ] && [ "$top" -ef "$1" ] || { printf 'UNKNOWN-scope'; return; }
  out="$(rcgit -C "$1" status --porcelain 2>/dev/null)" || rc=$?
  if [ "$rc" -ne 0 ]; then
    printf 'UNKNOWN-rc'
    return
  fi
  # ⛔ Re-check AFTER status, not only before. The pre-check vouches for a state
  # that may no longer hold when status runs; a swap in that window returns the
  # pre-fix answer (rc=0 from an ancestor, empty stdout, classified clean).
  # Reproduced deterministically with a git shim that removed .git between the
  # two calls: a DIRTY tree holding uncommitted work flipped to `clean`.
  # A post-check attests to a state no older than the measurement. This is NOT
  # race-free — nothing in shell can be — it removes the free single-swap window.
  [ -e "$1/.git" ] || { printf 'UNKNOWN-scope'; return; }
  top="$(rcgit -C "$1" rev-parse --show-toplevel 2>/dev/null)" || { printf 'UNKNOWN-rc'; return; }
  [ -n "$top" ] && [ "$top" -ef "$1" ] || { printf 'UNKNOWN-scope'; return; }
  if [ -z "$out" ]; then
    printf 'clean'
  else
    printf 'DIRTY'
  fi
}

# UNKNOWN has two causes and they need OPPOSITE operator advice, so they are
# distinct states internally and collapse to "UNKNOWN" only for display.
#   UNKNOWN-rc    : git status FAILED -> git's stderr names the cause, print it
#   UNKNOWN-scope : git status SUCCEEDED against an ANCESTOR -> stderr is EMPTY,
#                   so printing it left the operator staring at "git said: " and
#                   "Fix the cause above" pointing at a blank line.
is_unknown() { case "$1" in UNKNOWN-*) return 0 ;; *) return 1 ;; esac; }
explain_unknown() { # $1=state  $2=dir   -> one indented line of real diagnosis
  case "$1" in
    UNKNOWN-rc)
      # ⛔ `|| true` on BOTH pipelines. This function is reached from paths where
      # `set -e` is live, and `git status` here exits NON-ZERO by definition —
      # that is why we are in this branch. Under `pipefail` the pipeline fails
      # and `set -e` aborted --all mid-loop, so it printed the skip line, then
      # silently stopped: no advice, and later worktrees never processed. Caught
      # by this gate's own positive control ("--all DOES delete a clean
      # worktree"), which is what that control exists for.
      printf '      git said: '
      { rcgit -C "$2" status --porcelain 2>&1 >/dev/null | head -1 | sanitize; } || true
      printf '\n'
      ;;
    UNKNOWN-perm)
      printf '      cause: %s is not readable by this process (permission denied).\n' "$2"
      printf '             It may be a perfectly good worktree — nothing was inspected.\n'
      ;;
    *)
      # Never print "resolves to , not itself" — if the substitution comes back
      # empty, git could not resolve the path at all, which is a different fact.
      local _top
      _top="$( { rcgit -C "$2" rev-parse --show-toplevel 2>/dev/null | sanitize; } || true )"
      if [ -n "$_top" ]; then
        printf '      cause: git resolves this directory to %s, not itself — it is not a\n' "$_top"
        printf '             worktree, or its .git file is missing. Nothing here was inspected.\n'
      else
        printf '      cause: git could not resolve this path at all — it is not inside a\n'
        printf '             repository this process can read. Nothing here was inspected.\n'
      fi
      ;;
  esac
}

list_worktrees() {
  if [ ! -d "$WT_ROOT" ]; then
    printf 'no worktrees (%s missing)\n' "$WT_ROOT"
    return 0
  fi
  for d in "$WT_ROOT"/*/; do
    [ -d "$d" ] || continue
    local slug status
    # sanitize: a name carrying ESC[2K + CR erases its own row and repaints a
    # forged one; --status previously did no filtering at all.
    slug="$(basename "${d%/}" | sanitize)"
    # Truncate to the printf field width: stripping control chars is necessary
    # but not sufficient — an over-long name renders as a second plausible
    # (slug, status) pair and pushes the real verdict past the screen edge.
    slug="$(printf '%.30s' "$slug")"
    status="$(worktree_state "$d")"
    # Both UNKNOWN causes display as one word; the distinction drives advice,
    # not the status column.
    if is_unknown "$status"; then status=UNKNOWN; fi
    if [ -L "${d%/}" ]; then status="$status (symlink)"; fi
    printf '  %-30s  %s\n' "$slug" "$status"
  done
}

remove_one() {
  local slug="$1" force="${2:-}"
  # ⛔ A bash pattern, not `printf | grep -qE '^…$'`. grep anchors PER LINE and
  # -q succeeds if ANY line matches, so a multi-line slug passed a check whose
  # error message promises a strict charset — verified: printf 'ok\nx y z' |
  # grep -qE '^[A-Za-z0-9._-]+$' MATCHES. The case pattern has no line
  # semantics and no subprocess.
  case "$slug" in
    ''|*[!A-Za-z0-9._-]*)
      printf 'error: slug must match [A-Za-z0-9._-]+\n' >&2
      return 2
      ;;
  esac
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
  # in-tree path as if that were what went.
  if [ -L "$wt_dir" ]; then
    printf 'error: %s is a symlink — refusing (it would delete the target, not the link)\n' "$wt_dir" >&2
    return 1
  fi
  # ⛔ ...and that check alone is NOT enough: it stats only the LAST component.
  # If .claude/worktrees — or .claude — is itself a symlink, $wt_dir is not a
  # link, the check passes, and removal resolves through the ancestor and
  # deletes a worktree outside the repo. Reproduced on BOTH call sites.
  # So resolve the whole path and require containment. `pwd -P` resolves every
  # component, which is exactly what `[ -L ]` cannot do.
  local wt_real root_real
  wt_real="$(cd "$wt_dir" 2>/dev/null && pwd -P)" || {
    printf 'error: could not resolve %s — refusing\n' "$wt_dir" >&2; return 1; }
  root_real="$(cd "$WT_ROOT" 2>/dev/null && pwd -P)" || {
    printf 'error: could not resolve %s — refusing\n' "$WT_ROOT" >&2; return 1; }
  case "$wt_real/" in
    "$root_real"/*) ;;
    *)
      printf 'error: %s resolves to %s, outside %s — refusing\n' \
        "$wt_dir" "$wt_real" "$root_real" >&2
      return 1
      ;;
  esac
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
      #
      # ⛔ ...and the diagnostic must be branched on WHY. Printing git's stderr
      # is only useful for UNKNOWN-rc; on the upward-walk class git SUCCEEDS, so
      # stderr is EMPTY and the operator got "git said: " followed by a blank
      # line and "Fix the cause above" pointing at nothing — the same
      # loop-forever pressure the repair/prune advice created.
      printf 'error: could not inspect %s — refusing to remove.\n' "$wt_dir" >&2
      explain_unknown "$(worktree_state "$wt_dir")" "$wt_dir" >&2
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
  rcgit -C "$REPO_ROOT" worktree remove "$wt_dir" ${force:+--force} || {
    printf 'error: git worktree remove failed for %s\n' "$wt_dir" >&2
    return 1
  }
  # Best-effort: delete the matching agent/ branch only if it's fully merged.
  local branch="agent/$slug"
  # ⛔ These two were bare `git` while the classification was scrubbed — so the
  # DESTRUCTIVE call was the unprotected one. Reproduced: with GIT_DIR set, the
  # ref lookup and `branch -d` executed against a DIFFERENT repository's ref
  # store than the one that had been inspected.
  if rcgit -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/$branch"; then
    rcgit -C "$REPO_ROOT" branch -d "$branch" 2>/dev/null \
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
    slug="$(basename "${d%/}" | sanitize)"
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
        printf '      path: %s\n' "$(printf '%s' "${d%/}" | sanitize)"
        explain_unknown "$(worktree_state "$d")" "${d%/}"
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
