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

  # --- Gate 1: the branch's work is provably already in the base ---
  # TWO sound proofs, because ancestry ALONE IS NOT ENOUGH: a squash merge
  # replays the branch as one NEW commit, so the originals are never ancestors
  # of the base and `rev-list` reports the branch as unmerged forever. (Found by
  # running this script on its own squash-merged branch — it refused to retire
  # it.) The second proof matches the merged PR's head SHA against the local
  # tip, which is the pre-squash tip, so squash merges are covered.
  #
  # The tip must MATCH: `gh pr list --head <branch>` by name alone is unsound
  # when branch names are reused (merge, delete, recreate with new work) — the
  # stale merged PR would clear a branch carrying unmerged commits.
  merged_proof=""
  if [ "$(git rev-list --count "$BASE".."$b")" = "0" ]; then
    merged_proof="all commits in $BASE"
  elif [ "$PR_CHECK_OK" -eq 1 ]; then
    tip="$(git rev-parse --verify --quiet "refs/heads/$b" 2>/dev/null || true)"
    if [ -n "$tip" ] && gh pr list --state merged --head "$b" --json headRefOid 2>/dev/null \
         | jq -e --arg t "$tip" 'any(.[]; .headRefOid == $t)' >/dev/null 2>&1; then
      merged_proof="squash-merged (PR head tip matches)"
    fi
  fi
  if [ -z "$merged_proof" ]; then
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
    # ⛔ Capture the EXIT CODE, not just the line count. A FAILED `git status`
    # — a stale linked worktree whose admin dir under .git/worktrees/ is gone,
    # a corrupt .git, git off PATH, permission denied — writes NOTHING to
    # stdout and exits non-zero.
    #
    # What that COST here, measured 2026-08-17 on a corrupt-index worktree:
    # this script sets `set -euo pipefail` (:51), so the failed pipeline's 128
    # propagates through the command substitution and `set -e` ABORTS THE WHOLE
    # SWEEP mid-loop — later branches are never examined and the summary line
    # never prints. Before/after on the same fixture:
    #   main: HOLD feat/clean … ; EXIT=128, feat/merged never reported
    #   HEAD: HOLD feat/clean … ; HOLD feat/merged (git status exit 128);
    #         "would delete: 0  held: 2"; EXIT=0
    # So the fix converts a silent mid-sweep abort into a proper HOLD that
    # finishes the sweep — a availability/correctness fix, not a deletion fix.
    #
    # ⛔ An earlier version of this comment claimed the pipe "yields 0, so gate 2
    # PASSED on an inspection that never happened", and stamped it *Measured*.
    # That was an INFERENCE from a true observation (status exits 128 with empty
    # stdout) and it is false under `pipefail` — controlled both ways: with
    # pipefail the substitution aborts at 128; without it, and only without it,
    # the pipe yields "0". Grounding the observation did not ground the
    # inference drawn from it.
    # See docs/best-practices/verification-probe-discipline.md.
    wt_status=""; wt_rc=0
    wt_status="$(git -C "$wt" status --porcelain 2>/dev/null)" || wt_rc=$?
    if [ "$wt_rc" -ne 0 ]; then
      printf "  HOLD    %-38s worktree could not be inspected (git status exit %s) — inspect by hand\n" "$b" "$wt_rc"
      held=$((held+1)); continue
    fi
    if [ -z "$wt_status" ]; then
      dirty=0
    else
      dirty="$(printf '%s\n' "$wt_status" | wc -l | tr -d ' ')"
    fi
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
    # Predict the squash case here too. Dry-run cannot consult gate 4 in
    # general, but this one outcome IS knowable now, and printing "would
    # delete" for something --execute will certainly refuse is a dry run that
    # lies about its own next step.
    if [ "$merged_proof" = "squash-merged (PR head tip matches)" ]; then
      printf "  HOLD    %-38s squash-merged; git -d can't see it — use scripts/cleanup-branches.sh %s\n" "$b" "$b"
      held=$((held+1)); continue
    fi
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
    # `-d` shares gate 1's ancestry blindness, so a squash-merged branch lands
    # here even though it IS merged. We deliberately do NOT fall back to `-D`:
    # that is guard-destructive.sh's blocked pattern and its ONE sanctioned
    # escape hatch is cleanup-branches.sh. Duplicating the escape here would
    # give the repo two force-delete paths to keep correct instead of one.
    if [ "$merged_proof" = "squash-merged (PR head tip matches)" ]; then
      printf "  HOLD    %-38s squash-merged; git -d can't see it — use scripts/cleanup-branches.sh %s\n" "$b" "$b"
    else
      printf "  HOLD    %-38s git refused -d (not fully merged to HEAD or upstream)\n" "$b"
    fi
    held=$((held+1))
  fi
done

echo
if [ "$EXECUTE" -eq 1 ]; then
  echo "  deleted: $deleted    held: $held"
  # An `x && y` tail is the LAST command, so under `set -e` a run that deleted
  # nothing exits 1 — a clean "nothing to do" reported as a failure. Use `if`.
  if [ "$deleted" -gt 0 ]; then echo "  record:  $LOG"; fi
else
  echo "  would delete: $deleted    held: $held"
  echo "  (dry run — re-run with --execute to act)"
fi
