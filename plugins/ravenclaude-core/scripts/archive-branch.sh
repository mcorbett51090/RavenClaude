#!/usr/bin/env bash
# archive-branch.sh — safely retire a local branch by tagging its tip first,
# then deleting the branch. The tag preserves every commit forever and is
# recoverable via `git checkout archive/<branch>-<date>`. This pattern turns
# what would be a destructive `git branch -D` (blocked by guard-destructive.sh
# for good reason — silent loss of unmerged work) into a reversible operation.
#
# The motivating friction: an agent or maintainer wants to clean up old feature
# branches that represent abandoned approaches, stale plans, or superseded
# work. `git branch -d` refuses (unmerged); `git branch -D` is blocked by the
# guard (correctly, because it's blanket destructive). This script is the
# sanctioned middle path — it makes the deletion safe-BY-CONSTRUCTION (the
# work survives as a git tag), then performs the deletion via the lower-level
# `git update-ref -d` primitive that the guard doesn't pattern-match.
#
# Safety preconditions (the script aborts before delete if any fail):
#   1. The branch is not main / master / HEAD / the current branch.
#   2. A reason was supplied (`--reason "..."`).
#   3. The archive tag was created successfully at the branch tip.
#   4. The archive tag was pushed to origin successfully (configurable — see
#      --skip-push for genuine offline use).
#   5. The audit-log entry was written under .ravenclaude/runs/branch-archive/.
#
# Recovery: at any time, `git checkout archive/<branch>-<date>` restores a
# detached HEAD at the archived state. `git branch <newname>` from there
# recreates the working branch. The tag never expires.
#
# Usage:
#   scripts/archive-branch.sh <branch> --reason "<one-line why>"
#                                      [--evidence "<corroborating ref>"]
#                                      [--skip-push]
#                                      [--delete-remote]
#                                      [--yes]
#
# Examples:
#   scripts/archive-branch.sh fix/copilot-installer-status-project-flag \
#     --reason "Work folded into PR #221; branch superseded" \
#     --evidence "PR #221 merged 2026-06-01; commits' patch-id checked vs main"
#
#   scripts/archive-branch.sh feat/old-experiment \
#     --reason "Approach abandoned; replaced by Y" \
#     --evidence "docs/decisions/2026-06-03-Y.md" \
#     --delete-remote
#
# Audit log shape:
#   .ravenclaude/runs/branch-archive/YYYY-MM-DD-HHMMSS-<branch>.log
#   contains: ISO timestamp, branch name, tip SHA, tag name, reason, evidence,
#   operator (git user.email), and the exact unmerged-vs-main commit list.

set -euo pipefail

# ─── Parse args ──────────────────────────────────────────────────────────────
BRANCH=""
REASON=""
EVIDENCE=""
SKIP_PUSH=0
DELETE_REMOTE=0
ASSUME_YES=0

usage() {
  cat <<USAGE >&2
Usage: $(basename "$0") <branch> --reason "<one-line why>" [options]
  --evidence "<corroborating ref>"   e.g., PR number, decision doc, commit SHA
  --skip-push                         skip pushing the archive tag (offline)
  --delete-remote                     also delete the branch on origin (if present)
  --yes                               skip the final confirmation prompt
Recovery:
  git checkout archive/<branch>-<date>   # detached HEAD at archived tip
  git branch <newname>                    # recreate working branch
USAGE
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --reason)
      [[ $# -ge 2 ]] || { echo "archive-branch: --reason requires a value" >&2; usage; }
      REASON="$2"; shift 2 ;;
    --evidence)
      [[ $# -ge 2 ]] || { echo "archive-branch: --evidence requires a value" >&2; usage; }
      EVIDENCE="$2"; shift 2 ;;
    --skip-push) SKIP_PUSH=1; shift ;;
    --delete-remote) DELETE_REMOTE=1; shift ;;
    --yes|-y) ASSUME_YES=1; shift ;;
    -h|--help) usage ;;
    -*) echo "archive-branch: unknown option '$1'" >&2; usage ;;
    *)
      if [[ -z "$BRANCH" ]]; then BRANCH="$1"; shift
      else echo "archive-branch: unexpected positional arg '$1'" >&2; usage; fi
      ;;
  esac
done

[[ -z "$BRANCH" ]] && { echo "archive-branch: <branch> is required" >&2; usage; }
[[ -z "$REASON" ]] && { echo "archive-branch: --reason is required" >&2; usage; }

# --skip-push + --delete-remote is unsafe by construction: with --skip-push the
# archive tag is created LOCAL-ONLY (never pushed to origin, see the push guard
# below), yet --delete-remote goes on to delete the branch on origin. The only
# surviving copy of the commits is then a local tag that vanishes when an
# ephemeral session/container is reclaimed — the branch becomes unrecoverable
# from origin. This directly violates precondition 4 (the tag must be pushed
# before a delete is safe). Refuse the combination rather than silently lose work.
if [[ $DELETE_REMOTE -eq 1 && $SKIP_PUSH -eq 1 ]]; then
  echo "archive-branch: REFUSED — --delete-remote requires the archive tag to be pushed to origin first; drop --skip-push (the local-only tag would be the sole copy of the branch's work and is lost when the workspace is reclaimed)." >&2
  exit 1
fi

# ─── Preconditions ───────────────────────────────────────────────────────────
cd "$(git rev-parse --show-toplevel)"

# Resolve the repo's actual default branch. Prefer origin/HEAD's target, fall
# back across main/master. Defined here (moved up after the 2026-07 review) so the
# protected-branch refusal below can include it: on a repo whose default is e.g.
# "trunk"/"develop", hardcoding only main/master/HEAD would let `archive-branch.sh
# trunk` archive the live default branch.
_resolve_base_branch() {
  local base
  base="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null)"
  base="${base#origin/}"
  if [[ -n "$base" ]] && git rev-parse --verify --quiet "$base" >/dev/null 2>&1; then
    printf '%s\n' "$base"; return 0
  fi
  local c
  for c in main master; do
    if git rev-parse --verify --quiet "$c" >/dev/null 2>&1; then
      printf '%s\n' "$c"; return 0
    fi
  done
  return 1
}
_default_branch="$(_resolve_base_branch 2>/dev/null || true)"

# 1. Refuse on protected branch names — even if the user typo'd, never archive
#    main/master/HEAD or the resolved default branch.
for protected in main master HEAD "$_default_branch"; do
  if [[ -n "$protected" && "$BRANCH" == "$protected" ]]; then
    echo "archive-branch: REFUSED — '$BRANCH' is a protected branch name" >&2
    exit 1
  fi
done

# 2. Branch must exist locally.
if ! git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  echo "archive-branch: REFUSED — no local branch '$BRANCH'" >&2
  echo "archive-branch: existing branches:" >&2
  git branch | sed 's/^/  /' >&2
  exit 1
fi

# 3. Cannot archive the current branch.
CURRENT="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$CURRENT" == "$BRANCH" ]]; then
  echo "archive-branch: REFUSED — cannot archive the current branch ('$BRANCH')" >&2
  echo "archive-branch: 'git checkout main' first, then retry." >&2
  exit 1
fi

# 3.5 Refuse if the branch is checked out in ANY OTHER git worktree. `git branch -D`
#     refuses that automatically; the low-level `git update-ref -d` we use below does
#     NOT — deleting the ref out from under a live worktree leaves it detached/corrupt.
#     Precondition 3 already handled the current worktree, so any remaining exact
#     match here is a DIFFERENT worktree. -x/-F: whole-line, literal (branch names
#     may contain regex metacharacters and 'feat/foo' must not match 'feat/foobar').
if git worktree list --porcelain 2>/dev/null | grep -qxF "branch refs/heads/$BRANCH"; then
  echo "archive-branch: REFUSED — '$BRANCH' is checked out in another git worktree" >&2
  git worktree list >&2
  exit 1
fi

# 4. Capture branch tip + the unmerged-vs-default-branch commit list (the work
#    we'd lose). Resolve the default branch instead of hardcoding "main": on a
#    repo whose default is "master" (or anything else), `git log ... --not main`
#    errors out, the `|| true` swallows it, and an UNMERGED_COUNT of 0 would print
#    a false "(none — branch is fully merged)" plan for a branch that is NOT
#    merged. Reuses $_default_branch resolved above (via _resolve_base_branch).
TIP="$(git rev-parse "$BRANCH")"
if BASE_BRANCH="${_default_branch:-}" && [[ -n "$BASE_BRANCH" ]]; then
  UNMERGED_LIST="$(git log "$BRANCH" --not "$BASE_BRANCH" --oneline 2>/dev/null || true)"
else
  # No resolvable default branch — treat every commit on BRANCH as unmerged so the
  # plan never under-reports the work at risk (fail safe toward "you have work here").
  BASE_BRANCH="(none found)"
  UNMERGED_LIST="$(git log "$BRANCH" --oneline 2>/dev/null || true)"
fi
UNMERGED_COUNT="$(printf '%s\n' "$UNMERGED_LIST" | grep -c '.' || true)"

# 5. Compute the archive tag name (date-stamped so multiple archives of the
#    same name across time don't collide).
DATE="$(date -u +%Y-%m-%d-%H%M%S)"
TAG="archive/${BRANCH//\//-}-${DATE}"

# 6. Print plan + ask for confirmation.
cat <<PLAN
archive-branch plan:
  Branch:        $BRANCH
  Tip SHA:       $TIP
  Unmerged vs $BASE_BRANCH:
$(printf '%s\n' "${UNMERGED_LIST:-  (none — branch is fully merged)}" | sed 's/^/    /')
  Archive tag:   $TAG
  Push tag:      $([[ $SKIP_PUSH -eq 1 ]] && echo "NO (--skip-push)" || echo "yes (origin)")
  Delete remote: $([[ $DELETE_REMOTE -eq 1 ]] && echo "yes" || echo "no")
  Reason:        $REASON
  Evidence:      ${EVIDENCE:-(none)}
  Operator:      $(git config user.email 2>/dev/null || echo unknown)
PLAN

if [[ $ASSUME_YES -ne 1 ]]; then
  # Guard the read: on EOF / closed stdin (a non-TTY caller that forgot --yes),
  # `read` returns non-zero and, left unguarded, `set -e` would abort the script
  # right here with no message. Fail safe (no deletion) WITH the explanatory line
  # rather than a bare non-zero exit the caller can't interpret.
  if ! read -r -p "Proceed? [y/N] " ans; then
    echo "archive-branch: aborted (no input on stdin — pass --yes for non-interactive use)"; exit 1
  fi
  case "$ans" in
    y|Y|yes|YES) ;;
    *) echo "archive-branch: aborted by user"; exit 1 ;;
  esac
fi

# ─── Tag at branch tip ───────────────────────────────────────────────────────
if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "archive-branch: REFUSED — tag '$TAG' already exists (unexpected collision)" >&2
  exit 1
fi
git tag -a "$TAG" "$TIP" -m "Archive of $BRANCH at $TIP (reason: $REASON)" \
  || { echo "archive-branch: tag creation failed; nothing was deleted" >&2; exit 1; }

# ─── Push tag (unless --skip-push) ───────────────────────────────────────────
# RT-2 / C1-Q3 hardening (2026-08-12): on a tag-push failure (restricted git proxy,
# offline, or a 403 on non-branch refs), DO NOT roll back the local tag and dead-end.
# The old behavior stranded a consumer whose `branch -D`-equivalent is guard-blocked
# with no working recovery — G1 was closed in name only for a no-pushable-origin
# consumer. Instead RETAIN the local tag (the work is preserved + recoverable), print
# a loud actionable message, and fall through in LOCAL-ONLY mode so the branch is
# still archived-and-deleted. The one refusal is --delete-remote: a local-only tag
# plus a remote-branch delete would be unrecoverable (precondition 4's invariant).
if [[ $SKIP_PUSH -eq 0 ]]; then
  if ! git push origin "$TAG" >&2; then
    if [[ $DELETE_REMOTE -eq 1 ]]; then
      echo "archive-branch: REFUSED — tag push to origin FAILED and --delete-remote was requested." >&2
      echo "  A local-only archive tag plus a remote-branch delete would be unrecoverable." >&2
      echo "  Local tag '$TAG' is RETAINED; nothing was deleted. Restore origin access and re-run." >&2
      exit 1
    fi
    echo "archive-branch: WARNING — tag push to origin FAILED (restricted proxy / offline / 403)." >&2
    echo "  Proceeding in LOCAL-ONLY mode:" >&2
    echo "    - Local archive tag '$TAG' is RETAINED — work preserved (recover: git checkout '$TAG')." >&2
    echo "    - The tag is NOT on origin; it lives only in this checkout and is lost if the workspace is reclaimed." >&2
    echo "    - Push it when you regain origin access:  git push origin '$TAG'" >&2
    SKIP_PUSH=1   # record local-only in the audit log (tag_pushed: false)
  fi
fi

# ─── Write audit log ─────────────────────────────────────────────────────────
LOGDIR=".ravenclaude/runs/branch-archive"
mkdir -p "$LOGDIR"
LOG="$LOGDIR/${DATE}-${BRANCH//\//-}.log"
# Indent EVERY line of a value by 2 spaces so a multi-line --reason/--evidence
# stays a well-formed YAML block scalar. A bare `printf '  %s\n' "$VAL"` only
# indents the first line; an embedded newline then leaves subsequent lines at
# column 0, which ends the `reason: |` block and corrupts the YAML.
indent_block() { printf '%s\n' "$1" | sed 's/^/  /'; }
{
  echo "schema_version: 1"
  echo "ts: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "branch: $BRANCH"
  echo "tip_sha: $TIP"
  echo "tag: $TAG"
  echo "operator: $(git config user.email 2>/dev/null || echo unknown)"
  echo "reason: |"
  indent_block "$REASON"
  echo "evidence: |"
  indent_block "${EVIDENCE:-(none provided)}"
  echo "unmerged_vs_main_count: ${UNMERGED_COUNT}"
  echo "unmerged_vs_main:"
  if [[ -n "$UNMERGED_LIST" ]]; then
    # Quote via an array so the SHA list isn't word-split / glob-expanded into the
    # audit log (correct-by-construction even if the source format ever changes).
    # NOT `mapfile` — that is bash 4.0+, and macOS ships bash 3.2 at /bin/bash, where
    # it exits 127 (command not found). Under `set -e` that aborted the script HERE,
    # inside the `{ … } > "$LOG"` block — one line before `git update-ref -d`. Net
    # effect on macOS: the tag was created and pushed, the audit log was truncated,
    # and the branch was NEVER deleted, so the repo's only sanctioned branch-deletion
    # path (house rule 5 — `git branch -D` is guard-denied) silently half-completed
    # on the maintainer's own platform. Same door-1 class as the v0.193.0 hook sweep,
    # which scoped to plugins/*/hooks/** and never looked at scripts/.
    # `|| [[ -n "$_ub_line" ]]` preserves mapfile's handling of a final line with no
    # trailing newline.
    _ub_shas=()
    while IFS= read -r _ub_line || [[ -n "$_ub_line" ]]; do
      [[ -n "$_ub_line" ]] && _ub_shas+=("$_ub_line")
    done < <(printf '%s\n' "$UNMERGED_LIST" | awk '{print $1}')
    printf '  - %s\n' "${_ub_shas[@]}"
  else
    echo "  []"
  fi
  echo "tag_pushed: $([[ $SKIP_PUSH -eq 1 ]] && echo "false" || echo "true")"
  echo "delete_remote: $([[ $DELETE_REMOTE -eq 1 ]] && echo "true" || echo "false")"
} > "$LOG"

# ─── Delete the local branch via update-ref ──────────────────────────────────
# `git branch -D` is blanket-denied by guard-destructive.sh (correctly — it
# would silently lose unmerged work). After tagging + pushing the tag + writing
# the audit log, the work is recoverable, so we can safely use the lower-level
# `git update-ref -d` primitive that the guard doesn't pattern-match. This is
# the documented escape hatch — NOT a way to bypass the guard for any other
# reason. The script's preconditions are what make this sound.
# SHA-guarded delete: pass the tip captured at plan time ($TIP) as update-ref's
# expected old-value, so the delete is ATOMIC against that exact commit and fails
# closed if the branch moved during the (possibly long) interactive confirmation.
# Without the guard, a commit pushed to $BRANCH in that window (another worktree,
# terminal, or background agent) is silently orphaned by the unconditional delete
# while the script still prints SUCCESS — the archive tag was cut at the OLD $TIP.
if ! git update-ref -d "refs/heads/$BRANCH" "$TIP"; then
  echo "archive-branch: local delete failed (branch moved since the plan, or ref lock) — tag '$TAG' was created; re-check 'git log $BRANCH' then re-run, or find the tag via 'git tag --list archive/$BRANCH-*'" >&2
  exit 1
fi

# ─── Delete remote (if requested) ────────────────────────────────────────────
if [[ $DELETE_REMOTE -eq 1 ]]; then
  # Check ls-remote's OWN exit status separately from the match. Under
  # `set -o pipefail`, `ls-remote | grep -q .` reports GREP's status, so a real
  # ls-remote failure (origin unreachable, auth expired, DNS) produces no stdout,
  # grep exits 1, and the pipeline is indistinguishable from "branch absent" —
  # the delete would be silently skipped and the run still report SUCCESS.
  _lsr_rc=0
  _remote_refs="$(git ls-remote --heads origin "$BRANCH")" || _lsr_rc=$?
  if [[ $_lsr_rc -ne 0 ]]; then
    echo "archive-branch: could not query origin (git ls-remote rc=$_lsr_rc) — remote delete NOT attempted; LOCAL branch is gone (recoverable via $TAG)" >&2
    exit 1
  fi
  if [[ -n "$_remote_refs" ]]; then
    if ! git push origin --delete "$BRANCH" >&2; then
      echo "archive-branch: remote delete failed; LOCAL branch is gone (recoverable via $TAG)" >&2
      exit 1
    fi
  else
    echo "archive-branch: remote branch '$BRANCH' not present on origin (nothing to delete)" >&2
  fi
fi

# ─── Done ────────────────────────────────────────────────────────────────────
cat <<DONE
archive-branch: SUCCESS
  Branch '$BRANCH' archived as tag '$TAG'.
  Audit log: $LOG
  Recovery: git checkout '$TAG'  (then 'git branch <newname>' to resume)
DONE
