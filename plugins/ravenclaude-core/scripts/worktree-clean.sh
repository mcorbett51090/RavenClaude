#!/usr/bin/env bash
# worktree-clean.sh — unified worktree + branch lifecycle for RavenClaude /
# Sleipnir worktrees (and any other git worktree this repo's own tooling or a
# human created): discover every worktree via `git worktree list --porcelain`
# (not only .claude/worktrees/, so a sibling or ad-hoc worktree is covered
# too), classify it, and — ONLY on an explicit human action — remove it,
# prune its admin metadata, and retire its branch through
# cleanup-branches.sh's OWN safety checks (never a second, parallel -D path).
#
# CANONICAL HOME: plugins/ravenclaude-core/scripts/worktree-clean.sh (this
# file). scripts/worktree-clean.sh at the repo root is a thin shim so a
# marketplace/plugin install (where only plugins/ravenclaude-core/ ships)
# still gets the cleaner — same pattern as
# scripts/cleanup-branches.sh -> plugins/ravenclaude-core/scripts/cleanup-branches.sh.
#
# Usage:
#   worktree-clean.sh --status [--no-network]
#       Read-only report. Discovers EVERY worktree via `git worktree list
#       --porcelain` and classifies each one:
#         clean | DIRTY | IGNORED | DETACHED-unreachable | UNKNOWN-* |
#         STALE | PR-UNKNOWN | OPEN-PR | LOCKED | PRUNABLE | MAIN | SELF
#       Never mutates anything. --no-network skips the per-branch
#       `gh pr list` call — a worktree whose PR status could not be checked
#       is reported honestly ("PR status not checked") and classified
#       PR-UNKNOWN, never silently treated as "no open PR" (see the
#       PR-UNKNOWN classification below).
#
#   worktree-clean.sh --all [--execute] [--no-network]
#       Without --execute: the SAME dry-run report as --status, framed as
#       what `--all --execute` would do to each entry. This is the default —
#       dry run is the default for the whole bulk path.
#       With --execute: performs the unified lifecycle (remove -> prune ->
#       branch cleanup via cleanup-branches.sh) for every worktree
#       classified "clean" — never for DIRTY / IGNORED /
#       DETACHED-unreachable / UNKNOWN-* / STALE / PR-UNKNOWN / OPEN-PR /
#       LOCKED / the main worktree / the worktree this process is running
#       in. Also runs `git worktree prune` for any entry git itself reports
#       PRUNABLE. A "clean" entry is ADDITIONALLY skipped, bulk-only, when
#       another live session is using it as its cwd (BUSY — see
#       is_worktree_busy() below); single-target removal is unaffected.
#       --execute NEVER passes --force to the underlying removal, by design
#       (the brief: "do not remove without confirmation" for anything
#       outside plain "clean" — a bulk sweep is exactly the automated path
#       that must never force a flagged class past a human).
#
#   worktree-clean.sh <slug> [--force]
#       Legacy single-target removal, addressed under
#       .claude/worktrees/<slug> — SAME addressing, slug charset, and
#       WT_ROOT containment as the original script (unchanged). Performs the
#       unified lifecycle live (remove -> prune -> branch cleanup). --force
#       is honored only for DIRTY / IGNORED / DETACHED-unreachable / STALE;
#       UNKNOWN-* / PR-UNKNOWN / OPEN-PR / LOCKED / MAIN / SELF refuse even
#       with --force.
#
#   worktree-clean.sh --target <path> [--force]
#       Same removal semantics as <slug>, but addresses any worktree
#       `git worktree list --porcelain` reports — a sibling or ad-hoc
#       worktree outside .claude/worktrees/. Safety here is anchored to
#       PORCELAIN MEMBERSHIP instead of WT_ROOT containment: the resolved
#       path must equal a path git itself reported, or the removal refuses.
#       This is deliberately a STRONGER invariant than the slug path's
#       prefix-containment check — git told us the path, we never invented
#       it, so the "attacker plants a symlink inside a globbed directory"
#       class has no entry point here.
#
#   worktree-clean.sh --help|-h
#
# WHY "--all" NOW DEFAULTS TO DRY RUN (a behavior change from the prior
# version of this script, called out as a migration note):
#   The brief this revision implements requires "Dry run is the default.
#   Live remove/delete happens only with an explicit human flag plus
#   confirmation" for any AUTOMATED or BULK path. A single <slug> or
#   --target removal is already an explicit, individually-named human
#   action (the force contract below is the confirmation); --all sweeping
#   every worktree on the box is not, so it now requires a second explicit
#   flag (--execute) before it mutates anything.
#
# SAFETY CLASSES (every one of these must still hold after this revision;
# see individual function comments below for the full reasoning — this is
# just the index):
#
#   dirty       — uncommitted changes. Refuses; --force removes anyway.
#   UNKNOWN-*   — the tree could not be inspected (git status failed, or
#                 succeeded against an ancestor, or is unreadable). Refuses
#                 even with --force — see worktree_state()'s own comment.
#   IGNORED     — nothing tracked, but ignored files remain (.env,
#                 node_modules/, …). Refuses by default; --force removes
#                 anyway, because unlike UNKNOWN we can SEE what's there.
#   DETACHED-unreachable — clean by every other measure, but HEAD is
#                 detached at a commit no branch or tag contains. Refuses
#                 by default, same --force contract as IGNORED, plus a
#                 printed `git branch <name> <sha>` rescue.
#   open PR     — the worktree's branch has an open PR. Refuses, EVEN WITH
#                 --force (removing the worktree while a PR is still being
#                 reviewed against that branch is not a "I've seen the
#                 risk and accept it" situation the way IGNORED/DETACHED
#                 are — the branch and its review thread are still live).
#   stale       — last commit older than STALE_DAYS (default 14, matching
#                 skills/cleanup-worktrees/SKILL.md), or its age could not
#                 be determined at all. FLAG ONLY: never auto-removed under
#                 --all --execute; a single-target removal needs --force,
#                 same contract as IGNORED/DETACHED-unreachable.
#                 ⛔ An UNVERIFIABLE open-PR status (--no-network / gh
#                 absent) is deliberately NOT, by itself, grounds for
#                 STALE — only commit age decides that. An OLD commit with
#                 unverifiable PR status is STALE (age alone already flags
#                 it, same as a known-clear PR); a RECENT commit with
#                 unverifiable PR status is its own class, PR-UNKNOWN (see
#                 below) — it is NOT folded into "clean" the way an earlier
#                 revision of this file did (AppSec finding F1, 2026-11-10):
#                 that let --no-network / a missing-or-unauthenticated `gh`
#                 remove a worktree whose branch might have an open PR,
#                 without ever checking.
#   PR-UNKNOWN  — a branch whose open-PR status could not be verified
#                 (--no-network, `gh` absent, `gh` unauthenticated, or `gh`
#                 itself failing) AND whose commit is recent enough that age
#                 alone would not already flag it STALE. Refuses removal
#                 UNCONDITIONALLY — EVEN WITH --force, same contract as
#                 OPEN-PR/UNKNOWN/LOCKED — because "we could not check" is
#                 not "we checked and it's clear"; unknown PR status is
#                 never, by itself, a removal path, in any mode, bulk or
#                 single-target. Skipped under --all --execute, same as
#                 OPEN-PR. Retry without --no-network, or once `gh` is
#                 available/authenticated, to let it resolve to `clean` or
#                 `OPEN-PR` for real.
#   LOCKED      — `git worktree lock` or the admin `locked` file. Refuses
#                 unconditionally — no --force escape (unlock first:
#                 `git worktree unlock <path>`).
#   PRUNABLE    — git itself reports the worktree's directory is gone from
#                 disk. The correct action is `git worktree prune`, never
#                 `git worktree remove` (which would error on a missing
#                 directory anyway) — handled as its own branch, not folded
#                 into UNKNOWN.
#   MAIN / SELF — the primary checkout, and the worktree this process is
#                 currently running in, respectively. Never touched, no
#                 force escape, ever.
#   BUSY        — (bulk-only, --all --execute) a "clean" worktree that
#                 another LIVE session is using as its cwd, per the
#                 existing worktree-guard.sh SessionStart registry
#                 (reused, not reinvented — same PATH_KEY=sha256(realpath)
#                 keying plus kill-0(pid)-and-mtime liveness contract that
#                 file already uses, so a worktree registered by a live
#                 session there is honored here with no second heuristic).
#                 Skipped under --all --execute so a bulk sweep can't pull
#                 a worktree out from under another live session. NOT a
#                 top-level classification token — it never shows up in
#                 --status/classify_all's RESULT_TOKEN; it is checked only
#                 at the moment execute_all() is about to remove a "clean"
#                 entry. Single-target removal is unaffected: addressing a
#                 worktree by <slug>/--target is already the explicit,
#                 individually-named human action the brief carves out.
#
# Never uses --force on the underlying git call for a class this file
# doesn't explicitly decide to; never invents a second `git branch -D`
# path — all branch deletion is delegated to cleanup-branches.sh, which
# owns that decision and its own safety checks (merged-PR-tip match,
# ancestry, the open-PR veto, the SHA-guarded atomic delete).
#
# Codex-managed worktrees (per skills/cleanup-worktrees/SKILL.md and
# skills/new-worktree/SKILL.md, UNVERIFIED): Codex 0.155's agents overview
# owns confirmed-delete for ITS OWN managed worktrees, which can show up in
# `git worktree list --porcelain` exactly like any other worktree. There is
# no verified on-disk marker that distinguishes one deterministically, so
# this script does NOT fabricate detection for it. The mitigation is
# structural instead: --all defaults to dry-run, so a human reviews the
# full porcelain-wide list (which now includes any Codex-managed tree)
# before --execute can touch anything — the same review point the skill
# already asks for by naming the caveat.
#
# Portability: set -euo pipefail. macOS bash 3.2 / BSD-safe (no declare -A
# / mapfile / grep -P / timeout(1) / sed -i / ${x^^} / globstar), matching
# every other script in this plugin.

set -euo pipefail

# Stale threshold in days — matches skills/cleanup-worktrees/SKILL.md's
# documented "> 14 days old, no PR" rule. Overridable for testing/tuning.
STALE_DAYS="${WORKTREE_CLEAN_STALE_DAYS:-14}"
NO_NETWORK=0

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
  # ⛔ THE SCRUB ALONE IS NOT ENOUGH, and believing it was is what made the
  # comment below this function false for a while. Unsetting GIT_* closes the
  # GIT_CONFIG_COUNT/KEY_n/VALUE_n family, but git ALSO reads $HOME/.gitconfig,
  # $XDG_CONFIG_HOME/git/config and the system config — none of which is
  # GIT_-prefixed, so no amount of enumerating GIT_* reaches them.
  #
  # That matters far more than a misclassification, because some config values
  # are PROGRAMS GIT EXECUTES. `core.fsmonitor` is run during `git status`.
  # Measured 2026-08-17 against this script before this line existed:
  #   repo-local .git/config core.fsmonitor -> 2 executions per --status
  #   $HOME/.gitconfig       core.fsmonitor -> 2 executions per --status
  #   GIT_CONFIG_COUNT=... (control)        -> 0   (the scrub held this route)
  # i.e. arbitrary command execution as the operator, from a tool whose entire
  # reason to exist is being the safe one.
  #
  # Pointing GLOBAL and SYSTEM at /dev/null closes those two whole FILES for
  # every key, rather than naming keys one at a time — the same
  # allowlist-by-construction argument as the GIT_* enumeration above, applied
  # one layer out. `env` applies -u before assignments, so this composes with
  # the scrub. Repo-local `.git/config` is NOT covered here (it is per-call, and
  # a `-c` pin at the call site is the only thing that outranks it).
  #
  # Losing the user's global config is CORRECT for a classification probe: we
  # want git's stock semantics, not whatever this machine was tuned to. And the
  # one plausible casualty — a global `safe.directory` — makes git refuse, which
  # this script reads as UNKNOWN-rc and fails toward NOT deleting.
  #
  # bash 3.2: an empty array under `set -u` errors on plain "${_u[@]}".
  env ${_u[@]+"${_u[@]}"} GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null git "$@"
}

# Strip terminal control characters from anything attacker-influenced before it
# is printed. A directory name carrying ESC[2K + CR erases its own row and
# repaints a forged one ("SAFE-LOOKING … clean"); a newline forges an extra row.
# Applies to slugs AND paths, in every printing function.
sanitize() { LC_ALL=C tr -d '\000-\037\177'; }

REPO_ROOT="$(rcgit rev-parse --show-toplevel)"
WT_ROOT="$REPO_ROOT/.claude/worktrees"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
CLEANUP_BRANCHES="$SCRIPT_DIR/cleanup-branches.sh"

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
# This block is specific to the .claude/worktrees/<slug> addressing path
# (<slug> below) — the --target / --all / --status paths are anchored instead to
# PORCELAIN MEMBERSHIP (git itself reported the path), a stronger and more
# general invariant that doesn't depend on a single conventional root at all.
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
usage: $0 --status [--no-network]
       $0 --all [--execute] [--no-network]
       $0 <slug> [--force]
       $0 --target <path> [--force]
EOF
  exit "${1:-2}"
}

# Classify a worktree. Prints exactly one of:
#   clean | DIRTY | IGNORED | DETACHED-unreachable | UNKNOWN-rc |
#   UNKNOWN-scope | UNKNOWN-perm
# The three UNKNOWN-* causes collapse to "UNKNOWN" for DISPLAY; they stay
# distinct internally because they need opposite operator advice.
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
worktree_state() { # $1=dir -> clean|DIRTY|IGNORED|DETACHED-unreachable|UNKNOWN-rc|UNKNOWN-scope|UNKNOWN-perm
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
  # ⛔ THE CONFIG VECTOR (landed on main as #952 while this branch was open, and
  # reconciled here rather than dropped). `rcgit` scrubs GIT_* from the
  # ENVIRONMENT, which is necessary and not sufficient: `status.showUntrackedFiles`
  # and `core.excludesFile` also arrive from the repo-local `.git/config`, from
  # `$HOME/.gitconfig`, and from `$XDG_CONFIG_HOME` — none of which is GIT_-prefixed
  # and none of which an env scrub can reach. Measured on main's script with NO
  # environment variables at all, just `git config status.showUntrackedFiles no`:
  # a worktree holding uncommitted work classified `clean` and was removed.
  #
  # ⛔ Scope, stated exactly — an earlier version of this comment said the pins
  # "outrank every config source", which is false and was called out in review.
  # What is true: a `-c` pin outranks every source FOR THE KEYS IT NAMES. It says
  # nothing about keys it does not name, which is why the config-EXECUTION vector
  # (core.fsmonitor) needed closing in rcgit rather than here.
  # Division of labour: rcgit closes GIT_* and the global/system FILES wholesale;
  # these per-call pins close the repo-local `.git/config`, which nothing else can.
  out="$(rcgit -C "$1" -c core.excludesFile=/dev/null -c core.fsmonitor= status --porcelain --untracked-files=normal 2>/dev/null)" || rc=$?
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
  if [ -n "$out" ]; then printf 'DIRTY'; return; fi

  # ⛔ THE IGNORED-ONLY CLASS (landed on main as #953, reconciled here).
  # `status --porcelain` is SILENT ON IGNORED FILES BY DESIGN, so a tree holding
  # only .env / node_modules/ / a local db comes back empty with git working
  # perfectly — the probe answering "is anything TRACKED here?" when the caller
  # asked "is anything here?". The .env case is unrecoverable by construction:
  # the rule that hides it from the probe is the rule that means git has no copy.
  # Measured: fresh worktree of this repo -> 0 ignored entries (so this stays
  # signal), node_modules -> ONE line (`traditional` collapses it, so it is cheap).
  # Reached only when the tree is already a deletion candidate.
  local ig igrc=0
  ig="$(rcgit -C "$1" -c core.excludesFile=/dev/null -c core.fsmonitor= status --porcelain --untracked-files=normal --ignored=traditional 2>/dev/null)" || igrc=$?
  if [ "$igrc" -ne 0 ]; then printf 'UNKNOWN-rc'; return; fi
  if [ -n "$ig" ]; then printf 'IGNORED'; return; fi

  # ⛔ FIFTH FACE, and the first where the work is COMMITTED. Everything above
  # asks "is there uncommitted content here?". A detached-HEAD worktree can be
  # spotlessly clean by that measure and still be the only thing holding a
  # commit: nothing points at it, so `git worktree remove` makes it unreachable.
  #
  # control 2026-08-17 (scratch repo, detached worktree carrying commit 92011128,
  # then `git worktree remove --force`):
  #   before: .git/worktrees/dw/logs/HEAD exists;  reflog --all | grep -c -> 0
  #   after : that file is GONE;                   reflog --all | grep -c -> 0
  #           for-each-ref --contains <sha>        -> 0 refs (unreachable)
  #           git fsck --unreachable | grep -c     -> 1  (fsck is the only route)
  #   positive control, same probe on a reachable sha:
  #           reflog --all | grep -c $(rev-parse --short HEAD) -> 2
  # So the reflog does not rescue it — the admin dir holding that reflog is
  # deleted with the worktree — and `git fsck --lost-found` is the only path,
  # until gc prunes. That is why DETACHED-unreachable names the SHA and prints a
  # rescue command rather than a bare warning.
  #
  # The discriminator is REACHABILITY, not detachment. Measured 2026-08-17:
  #   detached + own commits  -> contained-by NONE            -> would be lost
  #   detached at a ref tip   -> contained-by refs/heads/main -> loses nothing
  #   branch-backed worktree  -> symbolic HEAD                -> loses nothing
  # Flagging every detached worktree would fire on the middle case, which is
  # common and harmless — and a guard that fires on the harmless case is one
  # that gets ignored on the harmful one.
  #
  # Cost is paid only here, on a tree already queued for deletion, and
  # `--count=1` lets the walk stop at the first containing ref.
  if ! rcgit -C "$1" symbolic-ref -q HEAD >/dev/null 2>&1; then
    local head_sha anyref
    head_sha="$(rcgit -C "$1" rev-parse HEAD 2>/dev/null)" || { printf 'UNKNOWN-rc'; return; }
    if [ -n "$head_sha" ]; then
      # A failure here means we could not determine reachability. That is "I
      # could not look", not "nothing is there" — the whole thesis of this file.
      anyref="$(rcgit -C "$1" for-each-ref --count=1 --contains "$head_sha" \
                  --format='%(refname)' 2>/dev/null)" || { printf 'UNKNOWN-rc'; return; }
      [ -n "$anyref" ] || { printf 'DETACHED-unreachable'; return; }
    fi
  fi
  printf 'clean'
}

# The HEAD commit of a detached worktree, short form, so the operator gets a
# message they can act on rather than one they can only be alarmed by.
detached_head() { # $1=dir
  rcgit -C "$1" rev-parse --short HEAD 2>/dev/null | sanitize
}

# First few ignored entries, for a message an operator can act on. Bounded, and
# sanitized like every other attacker-influenced string this file prints — an
# ignored PATH is named by whoever created the file, so it reaches a terminal.
# ⛔ ORDER IS LOAD-BEARING in the pipeline below. `sanitize` deletes \000-\037,
# which INCLUDES the newline (0x0A) — so running it BEFORE `tr` left the tr with
# nothing to translate and glued every entry into one token: `.envnode_modules/`.
# That is the exact string an operator reads before deciding to type --force on
# something unrecoverable, made unparseable by the guard meant to make it safe.
# Translate the separator FIRST, then strip whatever control bytes remain.
ignored_sample() { # $1=dir -> "a b c" or "a b c (+N more)"
  local _all _n
  _all="$(rcgit -C "$1" -c core.excludesFile=/dev/null -c core.fsmonitor= status --porcelain \
      --untracked-files=normal --ignored=traditional 2>/dev/null \
    | sed -n 's/^!! //p')" || true
  [ -n "$_all" ] || { printf ''; return; }
  _n="$(printf '%s\n' "$_all" | wc -l | tr -d ' ')"
  printf '%s' "$(printf '%s\n' "$_all" | head -3 | tr '\n' ' ' | sanitize)"
  # ⛔ SAY WHEN YOU TRUNCATED. Review reproduced the consequence: three decoy
  # names sorting before `.env` (an ordinary .gitignore covering .cache/,
  # .coverage, .DS_Store does this with no attacker at all) meant the operator
  # was shown "(.aaa .bbb .ccc)", typed --force on that basis, and destroyed a
  # .env they were never shown. The whole justification for honouring --force
  # here is "we can see it and we print it" — a silent cap makes that false.
  [ "$_n" -gt 3 ] && printf '(+%s more)' "$((_n - 3))"
  return 0
}

# UNKNOWN has two causes and they need OPPOSITE operator advice, so they are
# distinct states internally and collapse to "UNKNOWN" only for display.
#   UNKNOWN-rc    : git status FAILED -> git's stderr names the cause, print it
#   UNKNOWN-scope : git status SUCCEEDED against an ANCESTOR -> stderr is EMPTY,
#                   so printing it left the operator staring at "git said: " and
#                   "Fix the cause above" pointing at a blank line.
is_unknown() { case "$1" in UNKNOWN-*) return 0 ;; *) return 1 ;; esac; }
explain_unknown() { # $1=state  $2=dir   -> one indented line of real diagnosis
  # ⛔ SANITIZE ONCE, AT THE TOP, so every branch inherits it. Two of the three
  # branches piped through `sanitize` individually and the UNKNOWN-perm branch
  # did not — it printed the attacker-named path RAW. Reproduced in review: a
  # directory named with ESC[2K + CR, mode 000, erased its own output row under
  # --all and repainted a forged `<name>  clean` row; chaining two such entries
  # erased a genuine `skipped … (dirty)` line entirely. The per-branch approach
  # is the bug — it is an allowlist maintained by hand, and it was already wrong
  # for one of three branches. One assignment covers every present and future
  # branch by construction.
  local _d
  _d="$(printf '%s' "$2" | sanitize)"
  set -- "$1" "$_d"
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

# ─────────────────────────────────────────────────────────────────────────────
# PORCELAIN DISCOVERY (new) — covers every worktree, not only .claude/worktrees/
# ─────────────────────────────────────────────────────────────────────────────

# Parses `git worktree list --porcelain` into parallel indexed arrays (bash 3.2
# has no associative arrays — one `declare -A` already took out a security
# control's bash-3.2 support elsewhere in this plugin; this file does not repeat
# that). Index 0 is ALWAYS the main worktree — git's porcelain format lists the
# main worktree first, by documented contract.
#
#   PW_PATH[i]            absolute path, exactly as git reports it
#   PW_HEAD[i]             full HEAD sha
#   PW_BRANCH[i]           short branch name, "" if detached / bare
#   PW_DETACHED[i]         "1" if HEAD is detached, else ""
#   PW_LOCKED[i]           "1" if `git worktree lock` (or the admin `locked`
#                          file) is set, else ""
#   PW_LOCKED_REASON[i]    the locked reason text, sanitized (may be "")
#   PW_PRUNABLE[i]         "1" if git itself reports this entry prunable
#                          (its directory is gone from disk), else ""
#   PW_PRUNABLE_REASON[i]  the prunable reason text, sanitized (may be "")
#   PW_BARE[i]             "1" for a bare-repository record — never a real
#                          worktree target, always skipped by classify_all
#
# Degrades gracefully: an unrecognized porcelain line (a future git version
# adding a new field) is ignored rather than crashing. Returns 1 (arrays left
# empty) only if `git worktree list --porcelain` itself fails.
porcelain_worktrees() {
  PW_PATH=(); PW_HEAD=(); PW_BRANCH=(); PW_DETACHED=(); PW_LOCKED=()
  PW_LOCKED_REASON=(); PW_PRUNABLE=(); PW_PRUNABLE_REASON=(); PW_BARE=()
  local raw
  raw="$(rcgit -C "$REPO_ROOT" worktree list --porcelain 2>/dev/null)" || return 1
  local i=-1 line _rest
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      "worktree "*)
        i=$((i + 1))
        PW_PATH[i]="$(printf '%s' "${line#worktree }" | sanitize)"
        PW_HEAD[i]=""; PW_BRANCH[i]=""; PW_DETACHED[i]=""; PW_LOCKED[i]=""
        PW_LOCKED_REASON[i]=""; PW_PRUNABLE[i]=""; PW_PRUNABLE_REASON[i]=""; PW_BARE[i]=""
        ;;
      "HEAD "*)
        [ "$i" -ge 0 ] && PW_HEAD[i]="$(printf '%s' "${line#HEAD }" | sanitize)"
        ;;
      "branch "*)
        if [ "$i" -ge 0 ]; then
          _rest="${line#branch }"
          _rest="${_rest#refs/heads/}"
          PW_BRANCH[i]="$(printf '%s' "$_rest" | sanitize)"
        fi
        ;;
      "detached")
        [ "$i" -ge 0 ] && PW_DETACHED[i]="1"
        ;;
      "bare")
        [ "$i" -ge 0 ] && PW_BARE[i]="1"
        ;;
      "locked"*)
        if [ "$i" -ge 0 ]; then
          PW_LOCKED[i]="1"
          _rest="${line#locked}"
          _rest="${_rest# }"
          PW_LOCKED_REASON[i]="$(printf '%s' "$_rest" | sanitize)"
        fi
        ;;
      "prunable"*)
        if [ "$i" -ge 0 ]; then
          PW_PRUNABLE[i]="1"
          _rest="${line#prunable}"
          _rest="${_rest# }"
          PW_PRUNABLE_REASON[i]="$(printf '%s' "$_rest" | sanitize)"
        fi
        ;;
      *)
        : # blank record separator, or a porcelain field this version doesn't
          # know about yet — ignored by design (degrade, never crash)
        ;;
    esac
  done <<EOF_PORCELAIN
$raw
EOF_PORCELAIN
  return 0
}

# Best-effort real-path resolution that TOLERATES $1 itself not existing on
# disk — a PRUNABLE worktree's directory is, by definition, already gone, so
# a plain `cd "$1" && pwd -P` can never resolve it and every consumer of that
# idiom would silently treat a prunable entry as unmatchable. Falls back to
# resolving the PARENT (which does exist for a prunable entry — only the
# worktree's own directory is gone) and appending the basename. Returns 1
# only when NEITHER the path nor its parent can be resolved.
real_or_prunable() { # $1=path -> resolved real path (echoed), or return 1
  local target="$1" parent base preal
  if [ -d "$target" ]; then
    (cd "$target" 2>/dev/null && pwd -P) || return 1
    return 0
  fi
  parent="$(dirname "$target")"
  base="$(basename "$target")"
  preal="$(cd "$parent" 2>/dev/null && pwd -P)" || return 1
  printf '%s/%s' "$preal" "$base"
  return 0
}

# Resolves $1 to a real path and returns its index in PW_PATH[], or returns 1.
# This is the anchor for --target's safety: the resolved path must equal one
# git itself reported via `worktree list --porcelain` — never a path we built
# from a slug or a glob. Uses real_or_prunable on BOTH sides so a PRUNABLE
# entry (whose directory is already gone) can still be found and dispatched
# to `git worktree prune` rather than becoming permanently unaddressable.
find_index_by_real_path() { # $1=resolved-or-best-effort real path -> echoes index, or return 1
  local target="$1" n=${#PW_PATH[@]} idx=0 cand
  while [ "$idx" -lt "$n" ]; do
    cand="$(real_or_prunable "${PW_PATH[$idx]}")" || cand=""
    if [ -n "$cand" ] && [ "$cand" = "$target" ]; then
      printf '%s' "$idx"
      return 0
    fi
    idx=$((idx + 1))
  done
  return 1
}

# Days since the last commit on HEAD in worktree $1, or "" if it could not be
# determined (detached-unreachable already handled upstream; this is reached
# only for an otherwise-clean worktree with real commit history).
branch_last_commit_age_days() { # $1=dir -> integer days, or ""
  local ts now
  ts="$(rcgit -C "$1" log -1 --format=%ct HEAD 2>/dev/null)" || { printf ''; return; }
  case "$ts" in ''|*[!0-9]*) printf ''; return ;; esac
  now="$(date +%s 2>/dev/null)" || { printf ''; return; }
  printf '%s' "$(( (now - ts) / 86400 ))"
}

# Open-PR count for $1=branch, or the literal string "unknown" when it cannot
# be determined (--no-network, gh absent, or gh itself failed/returned
# something non-numeric). "unknown" is a FIRST-CLASS, distinct answer from "0"
# — see the STALE classification below for why an unverifiable PR status is
# treated the same as a stale commit, never as "no open PR".
branch_open_pr_count() { # $1=branch -> integer or "unknown"
  if [ "$NO_NETWORK" = "1" ] || ! command -v gh >/dev/null 2>&1; then
    printf 'unknown'
    return
  fi
  local n
  n="$(cd "$REPO_ROOT" 2>/dev/null && gh pr list --state open --head "$1" --json number -q 'length' 2>/dev/null)" || { printf 'unknown'; return; }
  case "$n" in ''|*[!0-9]*) printf 'unknown'; return ;; esac
  printf '%s' "$n"
}

# RESULT_TOKEN[i] / RESULT_DETAIL[i] — populated by classify_all(), indexed
# identically to PW_*[]. One classification pass, reused by every consumer
# (--status, --all preview, --all --execute, <slug>, --target) so there is
# exactly one place that decides what a worktree IS, and it is never
# re-derived differently by two code paths.
classify_all() {
  porcelain_worktrees || return 1
  RESULT_TOKEN=(); RESULT_DETAIL=()
  local n=${#PW_PATH[@]} idx=0
  local here
  here="$(cd "$REPO_ROOT" 2>/dev/null && pwd -P)" || here=""
  while [ "$idx" -lt "$n" ]; do
    local path="${PW_PATH[$idx]}" token="" detail=""
    if [ -n "${PW_BARE[$idx]:-}" ]; then
      token="BARE"; detail="bare repository record — not a worktree to manage"
    else
      local real
      real="$(cd "$path" 2>/dev/null && pwd -P)" || real=""
      if [ -n "$real" ] && [ -n "$here" ] && [ "$real" = "$here" ]; then
        token="SELF"; detail="the worktree this session is running in"
      elif [ "$idx" = "0" ]; then
        token="MAIN"; detail="the primary checkout"
      elif [ -n "${PW_PRUNABLE[$idx]:-}" ]; then
        token="PRUNABLE"
        detail="${PW_PRUNABLE_REASON[$idx]:-git reports this worktree is gone from disk}"
      elif [ -n "${PW_LOCKED[$idx]:-}" ]; then
        token="LOCKED"
        detail="${PW_LOCKED_REASON[$idx]:-locked}"
      else
        local state
        state="$(worktree_state "$path")"
        case "$state" in
          DIRTY)
            token="DIRTY"; detail="uncommitted changes"
            ;;
          IGNORED)
            token="IGNORED"; detail="holds only ignored files: $(ignored_sample "$path")"
            ;;
          DETACHED-unreachable)
            token="DETACHED-unreachable"
            detail="commit $(detached_head "$path") not reachable from any branch or tag — rescue: git -C $(printf '%s' "$REPO_ROOT" | sanitize) branch <name> $(detached_head "$path")"
            ;;
          UNKNOWN-*)
            token="$state"
            detail="could not inspect this tree (git status failed, or succeeded against an ancestor)"
            ;;
          clean)
            local branch="${PW_BRANCH[$idx]}" pr="unknown" age=""
            if [ -n "$branch" ]; then
              pr="$(branch_open_pr_count "$branch")"
              age="$(branch_last_commit_age_days "$path")"
            fi
            # ⛔ "PR status unknown" is NOT, by itself, grounds for STALE —
            # but it is ALSO never, by itself, grounds for "clean" (AppSec
            # finding F1, 2026-11-10: a prior revision of this file DID treat
            # a recent commit with unconfirmed PR status as "clean", which let
            # --no-network / a missing-or-unauthenticated `gh` remove a
            # worktree whose branch might have an open PR, without ever
            # checking — in single-target mode EVEN WITH --force, and in bulk
            # under --all --execute). An UNVERIFIABLE PR status is now its
            # own class, PR-UNKNOWN, reached only when age does not already
            # decide the outcome: an OLD commit with unconfirmed PR status is
            # still "STALE" (age alone already flags it — --no-network stays
            # useful for legitimate offline cleanup of genuinely old work);
            # a RECENT commit with unconfirmed PR status is "PR-UNKNOWN", not
            # "clean" — unknown is never treated as clear. An UNDETERMINABLE
            # age (git log itself failed) is treated as STALE, not clean — the
            # one case this errs cautious, because "clean" here would mean
            # asserting freshness we could not actually measure.
            if [ -n "$branch" ] && [ "$pr" != "unknown" ] && [ "$pr" -gt 0 ] 2>/dev/null; then
              token="OPEN-PR"
              detail="branch '$branch' has $pr open PR(s)"
            elif [ -n "$branch" ] && [ -z "$age" ]; then
              token="STALE"
              detail="could not determine last-commit age for branch '$branch' — flagged, not auto-removed"
            elif [ -n "$branch" ] && [ "$age" -ge "$STALE_DAYS" ] 2>/dev/null; then
              token="STALE"
              if [ "$pr" = "unknown" ]; then
                detail="last commit ${age}d ago (threshold ${STALE_DAYS}d); PR status not checked"
              else
                detail="last commit ${age}d ago (threshold ${STALE_DAYS}d), no open PR"
              fi
            elif [ -n "$branch" ] && [ "$pr" = "unknown" ]; then
              token="PR-UNKNOWN"
              detail="last commit ${age}d ago; PR status could not be verified (--no-network, gh absent, or gh unauthenticated) — refuses removal, even with --force, until status is known"
            else
              token="clean"
              if [ -z "$branch" ]; then
                detail="detached at a reachable ref — loses nothing"
              else
                detail="no open PR, last commit ${age}d ago"
              fi
            fi
            ;;
          *)
            token="UNKNOWN-rc"; detail="unrecognized classification '$state'"
            ;;
        esac
      fi
    fi
    RESULT_TOKEN[idx]="$token"
    RESULT_DETAIL[idx]="$(printf '%s' "$detail" | sanitize)"
    idx=$((idx + 1))
  done
  return 0
}

print_report() {
  local n=${#PW_PATH[@]} idx=0
  if [ "$n" -eq 0 ]; then
    printf '  no worktrees found (git worktree list --porcelain returned nothing)\n'
    return 0
  fi
  while [ "$idx" -lt "$n" ]; do
    if [ "${RESULT_TOKEN[$idx]}" != "BARE" ]; then
      local p b
      p="$(printf '%s' "${PW_PATH[$idx]}" | sanitize)"
      b="${PW_BRANCH[$idx]:-(detached)}"
      printf '  %s\n      branch: %s  state: %s\n      %s\n' \
        "$p" "$b" "${RESULT_TOKEN[$idx]}" "${RESULT_DETAIL[$idx]}"
    fi
    idx=$((idx + 1))
  done
}

# Removes (or, under dry_run=1, previews removing) ONE worktree and runs the
# rest of the unified lifecycle: `git worktree prune`, then branch cleanup
# through cleanup-branches.sh — NEVER a parallel `git branch -D` path. This is
# the single removal primitive every caller (dispatch_removal, execute_all)
# funnels through.
remove_and_cleanup() { # $1=path $2=branch $3=dry_run(0/1) $4=force("" or "--force")
  local path="$1" branch="$2" dry_run="$3" force="$4"
  if [ "$dry_run" = "1" ]; then
    printf '  WOULD remove: %s\n' "$(printf '%s' "$path" | sanitize)"
    printf '  then: git worktree prune\n'
    if [ -n "$branch" ]; then
      printf '  then (branch cleanup, dry-run):\n'
      if [ -f "$CLEANUP_BRANCHES" ]; then
        bash "$CLEANUP_BRANCHES" --dry-run "$branch" 2>&1 | sed 's/^/    /' || true
      else
        printf '    (cleanup-branches.sh not found at %s — branch left untouched)\n' "$(printf '%s' "$CLEANUP_BRANCHES" | sanitize)"
      fi
    fi
    return 0
  fi
  # `|| return 1` is load-bearing: a bare `git worktree remove` that FAILED must
  # never fall through to a "removed" message — see the original script's own
  # note on this (a failed operation rendering as a successful one).
  if ! rcgit -C "$REPO_ROOT" worktree remove "$path" ${force:+--force}; then
    printf '  error: git worktree remove failed for %s\n' "$(printf '%s' "$path" | sanitize)" >&2
    return 1
  fi
  printf '  removed: %s\n' "$(printf '%s' "$path" | sanitize)"
  rcgit -C "$REPO_ROOT" worktree prune >/dev/null 2>&1 || true
  if [ -n "$branch" ]; then
    if [ -f "$CLEANUP_BRANCHES" ]; then
      bash "$CLEANUP_BRANCHES" "$branch" 2>&1 | sed 's/^/    /' || true
    else
      printf '    branch cleanup skipped: cleanup-branches.sh not found at %s\n' "$(printf '%s' "$CLEANUP_BRANCHES" | sanitize)"
    fi
  fi
  return 0
}

# The shared decision function for a SINGLE, explicitly-named target (<slug> or
# --target): applies the exact force contract documented at the top of this
# file to the classification classify_all() already computed for index $1.
dispatch_removal() { # $1=idx $2=force("" or "--force") $3=dry_run(0/1)
  local idx="$1" force="$2" dry_run="$3"
  local token="${RESULT_TOKEN[$idx]}" detail="${RESULT_DETAIL[$idx]}"
  local path="${PW_PATH[$idx]}" branch="${PW_BRANCH[$idx]}"
  case "$token" in
    SELF)
      echo "error: refusing to remove the worktree this session is running in" >&2; return 1 ;;
    MAIN)
      echo "error: refusing to remove the main working tree" >&2; return 1 ;;
    BARE)
      echo "error: not a removable worktree (bare repository record)" >&2; return 1 ;;
    LOCKED)
      printf 'error: %s is locked (%s) — refusing to remove.\n' "$(printf '%s' "$path" | sanitize)" "$detail" >&2
      printf '       Unlock first: git worktree unlock %s\n' "$(printf '%s' "$path" | sanitize)" >&2
      return 1 ;;
    PRUNABLE)
      if [ "$dry_run" = "1" ]; then
        printf '  WOULD run: git worktree prune  (%s is gone from disk: %s)\n' "$(printf '%s' "$path" | sanitize)" "$detail"
      else
        rcgit -C "$REPO_ROOT" worktree prune >/dev/null 2>&1 || true
        printf '  pruned: %s (%s)\n' "$(printf '%s' "$path" | sanitize)" "$detail"
      fi
      return 0 ;;
    UNKNOWN-*)
      printf 'error: could not inspect %s — refusing to remove, even with --force.\n' "$(printf '%s' "$path" | sanitize)" >&2
      printf '       %s\n' "$detail" >&2
      printf '       Fix the cause, then re-run. Do NOT use --force: it discards uncommitted\n' >&2
      printf '       work, and the point is that we could not rule any out.\n' >&2
      return 1 ;;
    OPEN-PR)
      printf 'error: %s — %s. Refusing to remove, even with --force:\n' "$(printf '%s' "$path" | sanitize)" "$detail" >&2
      printf '       removing the worktree while its branch is under active review is not\n' >&2
      printf '       a considered-risk case the way a dirty/ignored/detached tree is.\n' >&2
      return 1 ;;
    PR-UNKNOWN)
      printf 'error: %s — %s. Refusing to remove, even with --force:\n' "$(printf '%s' "$path" | sanitize)" "$detail" >&2
      printf '       PR status could not be verified, so it is never treated as clear —\n' >&2
      printf '       retry without --no-network, or once \`gh\` is available/authenticated.\n' >&2
      return 1 ;;
    DIRTY)
      if [ "$force" != "--force" ]; then
        printf 'error: %s has uncommitted changes; pass --force to remove anyway\n' "$(printf '%s' "$path" | sanitize)" >&2
        return 1
      fi
      ;;
    IGNORED)
      if [ "$force" != "--force" ]; then
        printf 'error: %s — %s. Refusing to remove.\n' "$(printf '%s' "$path" | sanitize)" "$detail" >&2
        printf '       Nothing is tracked here, so git has no copy. Check it, then pass --force.\n' >&2
        return 1
      fi
      ;;
    DETACHED-unreachable)
      if [ "$force" != "--force" ]; then
        printf 'error: %s — %s\n' "$(printf '%s' "$path" | sanitize)" "$detail" >&2
        printf '       Keep the commit first (see the rescue command above), then re-run, or\n' >&2
        printf '       pass --force to discard it.\n' >&2
        return 1
      fi
      ;;
    STALE)
      if [ "$force" != "--force" ]; then
        printf 'error: %s — %s. Flagged, not removed. Pass --force to remove anyway.\n' "$(printf '%s' "$path" | sanitize)" "$detail" >&2
        return 1
      fi
      ;;
    clean)
      : # proceeds below unconditionally
      ;;
    *)
      printf 'error: unknown classification "%s" for %s — refusing to remove.\n' "$token" "$(printf '%s' "$path" | sanitize)" >&2
      return 1 ;;
  esac
  remove_and_cleanup "$path" "$branch" "$dry_run" "$force"
}

# Best-effort check: is another LIVE session already using worktree $1 as its
# cwd? Reuses the EXISTING worktree-guard.sh SessionStart registry rather than
# inventing a second liveness mechanism — same PATH_KEY=sha256(realpath(dir))
# keying, same kill-0(pid)-AND-mtime-within-TTL liveness contract that file
# already uses for its own CONTENTION/LEASE checks. A session that has been
# working inside $1 as its cwd will have already registered a live record
# there via that hook's own `register` subcommand; this just reads it.
#
# FAILS OPEN (prints nothing, returns 1 = "not busy") whenever it cannot tell:
# no hashing tool, no registry directory, no jq AND the no-jq fallback grep
# also finds nothing parseable. This is deliberate — the brief warns against
# "a fragile heuristic that false-positives the bulk skip on every idle
# worktree"; failing open means an inability to check never turns into an
# over-eager skip of a genuinely idle, removable worktree. It can only ever
# make --all --execute LESS aggressive, never more.
is_worktree_busy() { # $1=path -> 0=busy (another live session registered), 1=not busy/unknown
  local path="$1" real key home sess_dir f pid m now ttl
  real="$(cd "$path" 2>/dev/null && pwd -P)" || return 1
  [ -n "$real" ] || return 1
  if command -v sha256sum >/dev/null 2>&1; then
    key="$(printf '%s' "$real" | sha256sum 2>/dev/null | cut -d' ' -f1)"
  elif command -v shasum >/dev/null 2>&1; then
    key="$(printf '%s' "$real" | shasum -a 256 2>/dev/null | cut -d' ' -f1)"
  else
    return 1
  fi
  [ -n "$key" ] || return 1
  home="${RC_WORKTREE_GUARD_HOME:-$HOME/.ravenclaude/worktree-guard}"
  sess_dir="$home/sessions/$key"
  [ -d "$sess_dir" ] || return 1
  ttl="${RC_WORKTREE_GUARD_STALE_TTL:-900}"
  case "$ttl" in ''|*[!0-9]*) ttl=900 ;; esac
  now="$(date +%s 2>/dev/null || printf '0')"
  for f in "$sess_dir"/*.json; do
    [ -f "$f" ] || continue
    if command -v jq >/dev/null 2>&1; then
      pid="$(jq -r '.pid // empty' "$f" 2>/dev/null)"
    else
      pid="$(grep -o '"pid"[[:space:]]*:[[:space:]]*[0-9]*' "$f" 2>/dev/null | head -1 | grep -o '[0-9]*$')"
    fi
    case "$pid" in ''|*[!0-9]*) continue ;; esac
    kill -0 "$pid" 2>/dev/null || continue
    m="$(stat -c %Y "$f" 2>/dev/null)" || m="$(stat -f %m "$f" 2>/dev/null)"
    case "$m" in ''|*[!0-9]*) continue ;; esac
    [ $(( now - m )) -le "$ttl" ] || continue
    return 0
  done
  return 1
}

# The bulk path: applied ONLY to entries classify_all() marked "clean" — a
# bulk sweep NEVER forces a flagged class past a human, by design (see the
# header comment on why --all defaults to dry-run and --execute never forces).
execute_all() {
  local n=${#PW_PATH[@]} idx=0
  while [ "$idx" -lt "$n" ]; do
    local token="${RESULT_TOKEN[$idx]}" path="${PW_PATH[$idx]}"
    case "$token" in
      BARE|SELF|MAIN)
        : ;;
      PRUNABLE)
        printf '  pruning (gone from disk): %s (%s)\n' "$(printf '%s' "$path" | sanitize)" "${RESULT_DETAIL[$idx]}"
        ;;
      DIRTY|IGNORED|DETACHED-unreachable|UNKNOWN-*|STALE|PR-UNKNOWN|OPEN-PR|LOCKED)
        printf '  skipped %s (%s): %s\n' "$(printf '%s' "$path" | sanitize)" "$token" "${RESULT_DETAIL[$idx]}"
        ;;
      clean)
        if is_worktree_busy "$path"; then
          printf '  skipped %s (BUSY): another live session appears to be using this worktree (worktree-guard registry)\n' "$(printf '%s' "$path" | sanitize)"
        else
          remove_and_cleanup "$path" "${PW_BRANCH[$idx]}" 0 "" || true
        fi
        ;;
      *)
        printf '  skipped %s (unrecognized "%s")\n' "$(printf '%s' "$path" | sanitize)" "$token" >&2
        ;;
    esac
    idx=$((idx + 1))
  done
  rcgit -C "$REPO_ROOT" worktree prune >/dev/null 2>&1 || true
}

cmd_status() {
  if ! classify_all; then
    echo "error: could not enumerate worktrees (git worktree list --porcelain failed)" >&2
    return 1
  fi
  if [ "$NO_NETWORK" = "1" ]; then
    echo "Worktrees (git worktree list --porcelain; network checks skipped --no-network):"
  else
    echo "Worktrees (git worktree list --porcelain):"
  fi
  print_report
}

cmd_all() { # $1=execute(0/1)
  if ! classify_all; then
    echo "error: could not enumerate worktrees (git worktree list --porcelain failed)" >&2
    return 1
  fi
  if [ "$1" = "1" ]; then
    echo "Executing the unified lifecycle (remove -> prune -> branch cleanup) for every 'clean' worktree:"
    execute_all
  else
    echo "DRY RUN (the default) — pass --execute to actually perform this:"
    print_report
    echo
    echo "Only 'clean' entries above would be removed; every other state is skipped, as shown."
    local idx2=0 n2=${#PW_PATH[@]} busy_noted=0
    while [ "$idx2" -lt "$n2" ]; do
      if [ "${RESULT_TOKEN[$idx2]}" = "clean" ] && is_worktree_busy "${PW_PATH[$idx2]}"; then
        if [ "$busy_noted" -eq 0 ]; then
          echo "Note: at least one 'clean' entry above is currently in use by another live session and would be skipped (BUSY), not removed, under --execute too."
          busy_noted=1
        fi
      fi
      idx2=$((idx2 + 1))
    done
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Single-target removal, two addressing modes
# ─────────────────────────────────────────────────────────────────────────────

remove_one() { # $1=slug $2=force("" or "--force")
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
  # ⛔ Validate ONCE, here, against the exact set — a typo like "--froce" must
  # error, never be silently treated as "no force".
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
  if ! classify_all; then
    echo "error: could not enumerate worktrees (git worktree list --porcelain failed)" >&2
    return 1
  fi
  local idx
  idx="$(find_index_by_real_path "$wt_real")" || {
    printf 'error: %s exists on disk but git does not report it as a worktree (run: git worktree prune)\n' "$wt_dir" >&2
    return 1
  }
  dispatch_removal "$idx" "$force" 0
}

remove_target() { # $1=path $2=force("" or "--force")
  local target="$1" force="${2:-}"
  case "$force" in
    ''|--force) ;;
    *) printf 'error: unknown flag: %s (expected --force or nothing)\n' "$force" >&2; return 2 ;;
  esac
  if [ -z "$target" ]; then
    printf 'error: --target requires a path\n' >&2
    return 2
  fi
  # ⛔ Do NOT require $target to exist. A PRUNABLE worktree's directory is
  # already gone from disk by definition — refusing here would make a
  # prunable entry permanently unaddressable via --target. Only refuse when
  # the path exists AND is something other than a directory (a plain file,
  # which could never be a worktree).
  if [ -e "$target" ] && [ ! -d "$target" ]; then
    printf 'error: not a directory: %s\n' "$target" >&2
    return 1
  fi
  # Same symlink refusal as remove_one, for the same reason: `git worktree
  # remove` resolves a symlink and would delete its TARGET, not the link.
  # (A symlink to a now-missing target still stats as a symlink via -L.)
  if [ -L "$target" ]; then
    printf 'error: %s is a symlink — refusing (it would resolve through the link, not the worktree itself)\n' "$target" >&2
    return 1
  fi
  local real
  real="$(real_or_prunable "$target")" || {
    printf 'error: could not resolve %s (and its parent does not exist either) — refusing\n' "$target" >&2; return 1; }
  if ! classify_all; then
    echo "error: could not enumerate worktrees (git worktree list --porcelain failed)" >&2
    return 1
  fi
  local idx
  idx="$(find_index_by_real_path "$real")" || {
    printf 'error: %s resolves to %s, which `git worktree list --porcelain` does not report\n' "$target" "$real" >&2
    printf '       — refusing (not a worktree git itself manages).\n' >&2
    return 1
  }
  dispatch_removal "$idx" "$force" 0
}

# ─────────────────────────────────────────────────────────────────────────────
# Argument parsing
# ─────────────────────────────────────────────────────────────────────────────

ACTION=""
TARGET_ARG=""
FORCE=""
EXECUTE=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --status)
      ACTION="status"; shift ;;
    --all)
      ACTION="all"; shift ;;
    --execute)
      EXECUTE=1; shift ;;
    --no-network)
      NO_NETWORK=1; shift ;;
    --target)
      ACTION="target"; shift
      TARGET_ARG="${1:-}"
      [ "$#" -gt 0 ] && shift
      ;;
    --force)
      FORCE="--force"; shift ;;
    --help|-h)
      usage 0 ;;
    -*)
      printf 'error: unknown flag: %s\n' "$1" >&2
      usage 2
      ;;
    *)
      if [ -z "$ACTION" ]; then
        ACTION="slug"; TARGET_ARG="$1"; shift
      else
        # ACTION is already set (e.g. a slug was already given) — a second
        # bare token here is a typo or stray positional, never silently
        # ignored. Mirrors the original script's strict `force` validation.
        printf 'error: unexpected extra argument: %s\n' "$1" >&2
        usage 2
      fi
      ;;
  esac
done

[ -n "$ACTION" ] || usage 2

case "$ACTION" in
  status) cmd_status ;;
  all)    cmd_all "$EXECUTE" ;;
  target) remove_target "$TARGET_ARG" "$FORCE" ;;
  slug)   remove_one "$TARGET_ARG" "$FORCE" ;;
esac
