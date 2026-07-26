#!/usr/bin/env bash
# forge-worktree.sh — the FORGE pipeline's worktree + checkpoint provisioner.
#
# Purpose: /forge always runs its plan-landing + implementation on an isolated
# `forge/<slug>` branch inside a dedicated git worktree, and checkpoints (git
# commits) that work at gate boundaries — so a FORGE run never mutates the
# primary checkout's tree, parallel runs can't collide, and an interrupted run
# is recoverable from the branch. See skills/forge-pipeline/SKILL.md §0.5.
#
# The helper is DETERMINISTIC and FAIL-SAFE by contract: every guard that can't
# provision (not a git repo, already inside a linked worktree, opted out, or any
# git error) exits 0 with a `status=skipped|disabled` receipt so the pipeline
# proceeds in the primary checkout. Provisioning is a safety anchor, NEVER a gate
# — it must never block a planning run.
#
# Portability: written to run on macOS's stock bash 3.2 (no `declare -A`, no
# `mapfile`, no `${x^^}`, no `shopt -s globstar`) and with no dependency on GNU
# `timeout`, `grep -P`, or `sed -i` — the exact traps recorded in the
# ravenclaude-core CLAUDE.md "macOS door" milestones.
#
# Usage:
#   forge-worktree.sh init  <slug> [--base <ref>]   provision (or reuse) the worktree
#   forge-worktree.sh checkpoint <slug> <label>     commit tracked work as a checkpoint
#   forge-worktree.sh path  <slug>                  print the worktree path (or nothing)
#   forge-worktree.sh --self-test                   run built-in fixtures (nonzero on failure)
#
# Opt-out: FORGE_WORKTREE=off (env) OR `forge_worktree: off` in
# .ravenclaude/comfort-posture.yaml. Absent ⇒ ON (the default).

set -euo pipefail

WT_ROOT_REL=".claude/worktrees"
SLUG_RE='^[a-z0-9][a-z0-9-]{1,60}$'

# --- tiny helpers -----------------------------------------------------------

# Emit a one-line JSON receipt on stdout. All values are pre-sanitized/simple.
_receipt() {
  # $1=status $2=path $3=branch $4=slug $5=reason(optional)
  printf '{"status":"%s","path":"%s","branch":"%s","slug":"%s","reason":"%s"}\n' \
    "${1:-}" "${2:-}" "${3:-}" "${4:-}" "${5:-}"
}

_is_git_repo() {
  git rev-parse --is-inside-work-tree >/dev/null 2>&1
}

# True when we are inside a LINKED worktree (not the primary checkout). In a
# linked worktree the per-worktree git dir differs from the common git dir.
_in_linked_worktree() {
  local gd cd
  gd="$(git rev-parse --git-dir 2>/dev/null || echo '')"
  cd="$(git rev-parse --git-common-dir 2>/dev/null || echo '')"
  [ -n "$gd" ] && [ -n "$cd" ] && [ "$gd" != "$cd" ]
}

# Resolve the repo top level of the PRIMARY checkout (the common dir's parent),
# so provisioning always anchors worktrees at the real repo root even if called
# from a subdir.
_repo_toplevel() {
  git rev-parse --show-toplevel 2>/dev/null || echo ''
}

# Read the opt-out knob. Precedence: FORGE_WORKTREE env > comfort-posture > on.
# Returns "off" or "on". Fail-safe: any read error ⇒ on.
_worktree_mode() {
  local env_val top posture line
  env_val="${FORGE_WORKTREE:-}"
  if [ "$env_val" = "off" ]; then
    echo "off"; return 0
  fi
  top="$(_repo_toplevel)"
  posture="${top}/.ravenclaude/comfort-posture.yaml"
  if [ -n "$top" ] && [ -f "$posture" ]; then
    # Minimal scalar read — no PyYAML. Match a top-level `forge_worktree: off`.
    line="$(grep -E '^[[:space:]]*forge_worktree:[[:space:]]*off([[:space:]]|#|$)' "$posture" 2>/dev/null || echo '')"
    if [ -n "$line" ]; then
      echo "off"; return 0
    fi
  fi
  echo "on"
}

# Does a worktree already exist at the given absolute path?
_worktree_exists_at() {
  # $1 = absolute path
  git worktree list --porcelain 2>/dev/null | grep -Fxq "worktree $1"
}

# Does a local branch exist?
_branch_exists() {
  # $1 = branch name
  git show-ref --verify --quiet "refs/heads/$1"
}

# Pick a base ref that exists: prefer requested --base, else main, else HEAD.
_resolve_base() {
  # $1 = requested base (may be empty)
  local req="$1"
  if [ -n "$req" ] && git rev-parse --verify --quiet "$req" >/dev/null 2>&1; then
    echo "$req"; return 0
  fi
  if git rev-parse --verify --quiet "main" >/dev/null 2>&1; then
    echo "main"; return 0
  fi
  echo "HEAD"
}

# --- subcommands ------------------------------------------------------------

cmd_init() {
  local slug="${1:-}"; shift || true
  local base=""
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --base) base="${2:-}"; shift 2 || shift ;;
      --base=*) base="${1#--base=}"; shift ;;
      *) shift ;;
    esac
  done

  if ! printf '%s' "$slug" | grep -Eq "$SLUG_RE"; then
    _receipt "skipped" "" "" "$slug" "invalid-slug"
    return 0
  fi

  # Guard 1: opt-out.
  if [ "$(_worktree_mode)" = "off" ]; then
    _receipt "disabled" "" "" "$slug" "opted-out"
    return 0
  fi

  # Guard 2: not a git repo — nothing to isolate. Proceed in place.
  if ! _is_git_repo; then
    _receipt "skipped" "" "" "$slug" "not-a-git-repo"
    return 0
  fi

  # Guard 3: already inside a linked worktree — do NOT nest.
  if _in_linked_worktree; then
    _receipt "skipped" "" "" "$slug" "already-in-worktree"
    return 0
  fi

  local top wt_abs branch
  top="$(_repo_toplevel)"
  if [ -z "$top" ]; then
    _receipt "skipped" "" "" "$slug" "no-toplevel"
    return 0
  fi
  wt_abs="${top}/${WT_ROOT_REL}/forge-${slug}"
  branch="forge/${slug}"

  # Idempotent reuse: a resume must re-enter the SAME worktree, not refuse.
  if _worktree_exists_at "$wt_abs"; then
    _receipt "reused" "$wt_abs" "$branch" "$slug" "worktree-exists"
    printf 'FORGE_WORKTREE %s\n' "$wt_abs"
    return 0
  fi

  local resolved_base
  resolved_base="$(_resolve_base "$base")"

  # Create the worktree. Reuse the branch if it already exists (checkout it),
  # else create it off the resolved base. Any failure is fail-safe (skip).
  if _branch_exists "$branch"; then
    if git worktree add "$wt_abs" "$branch" >/dev/null 2>&1; then
      _receipt "created" "$wt_abs" "$branch" "$slug" "existing-branch"
      printf 'FORGE_WORKTREE %s\n' "$wt_abs"
      return 0
    fi
  else
    if git worktree add -b "$branch" "$wt_abs" "$resolved_base" >/dev/null 2>&1; then
      _receipt "created" "$wt_abs" "$branch" "$slug" "new-branch"
      printf 'FORGE_WORKTREE %s\n' "$wt_abs"
      return 0
    fi
  fi

  _receipt "skipped" "" "$branch" "$slug" "git-worktree-add-failed"
  return 0
}

cmd_path() {
  local slug="${1:-}"
  if ! printf '%s' "$slug" | grep -Eq "$SLUG_RE"; then
    return 0
  fi
  _is_git_repo || return 0
  local top wt_abs
  top="$(_repo_toplevel)"
  [ -n "$top" ] || return 0
  wt_abs="${top}/${WT_ROOT_REL}/forge-${slug}"
  if _worktree_exists_at "$wt_abs"; then
    printf '%s\n' "$wt_abs"
  fi
}

cmd_checkpoint() {
  local slug="${1:-}"; shift || true
  local label="${*:-checkpoint}"

  if ! printf '%s' "$slug" | grep -Eq "$SLUG_RE"; then
    _receipt "skipped" "" "" "$slug" "invalid-slug"
    return 0
  fi
  if ! _is_git_repo; then
    _receipt "skipped" "" "" "$slug" "not-a-git-repo"
    return 0
  fi

  local top wt_abs branch
  top="$(_repo_toplevel)"
  [ -n "$top" ] || { _receipt "skipped" "" "" "$slug" "no-toplevel"; return 0; }
  wt_abs="${top}/${WT_ROOT_REL}/forge-${slug}"
  branch="forge/${slug}"

  if ! _worktree_exists_at "$wt_abs"; then
    _receipt "skipped" "$wt_abs" "$branch" "$slug" "worktree-missing"
    return 0
  fi

  # Stage everything in the worktree. Nothing tracked-and-changed ⇒ no-op.
  git -C "$wt_abs" add -A >/dev/null 2>&1 || true
  if git -C "$wt_abs" diff --cached --quiet 2>/dev/null; then
    _receipt "noop" "$wt_abs" "$branch" "$slug" "nothing-to-commit"
    return 0
  fi

  # Newline-strip the label so the commit subject is always one line.
  local safe_label
  safe_label="$(printf '%s' "$label" | tr '\n\r' '  ')"
  if git -C "$wt_abs" commit -m "forge(${slug}): checkpoint — ${safe_label}" >/dev/null 2>&1; then
    _receipt "committed" "$wt_abs" "$branch" "$slug" "$safe_label"
    return 0
  fi

  _receipt "skipped" "$wt_abs" "$branch" "$slug" "commit-failed"
  return 0
}

# --- self-test --------------------------------------------------------------

_st_fail() { echo "SELF-TEST FAIL: $1" >&2; ST_RC=1; }

cmd_self_test() {
  ST_RC=0
  local scratch
  scratch="$(mktemp -d 2>/dev/null || echo '')"
  if [ -z "$scratch" ]; then
    echo "SELF-TEST FAIL: mktemp unavailable" >&2
    return 1
  fi
  # shellcheck disable=SC2064
  trap "rm -rf '$scratch'" EXIT

  local script_abs
  script_abs="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"

  # Fixture 1: not-a-git-repo ⇒ skipped, exit 0, pipeline proceeds.
  (
    cd "$scratch"
    out="$(FORGE_WORKTREE= bash "$script_abs" init demo-slug 2>/dev/null || echo 'RC-NONZERO')"
    printf '%s' "$out" | grep -q '"status":"skipped"' || exit 21
    printf '%s' "$out" | grep -q 'not-a-git-repo' || exit 22
  ) || _st_fail "not-a-git-repo did not fail-safe ($?)"

  # Build a real scratch repo for the remaining fixtures.
  local repo="${scratch}/repo"
  mkdir -p "$repo"
  (
    cd "$repo"
    git init -q .
    git config user.email st@example.com
    git config user.name selftest
    git checkout -q -b main
    echo seed > seed.txt
    git add -A && git commit -qm seed
  ) || { _st_fail "scratch repo setup"; return "$ST_RC"; }

  # Fixture 2: invalid slug ⇒ skipped/invalid-slug.
  (
    cd "$repo"
    out="$(bash "$script_abs" init 'Bad Slug!' 2>/dev/null)"
    printf '%s' "$out" | grep -q 'invalid-slug' || exit 23
  ) || _st_fail "invalid slug not rejected ($?)"

  # Fixture 3: init creates the worktree + branch off main.
  (
    cd "$repo"
    out="$(bash "$script_abs" init alpha 2>/dev/null)"
    printf '%s' "$out" | grep -q '"status":"created"' || exit 24
    [ -d "${repo}/.claude/worktrees/forge-alpha" ] || exit 25
    git show-ref --verify --quiet refs/heads/forge/alpha || exit 26
  ) || _st_fail "init did not create worktree/branch ($?)"

  # Fixture 4: init is idempotent — a second init REUSES, never errors.
  (
    cd "$repo"
    out="$(bash "$script_abs" init alpha 2>/dev/null)"
    printf '%s' "$out" | grep -q '"status":"reused"' || exit 27
  ) || _st_fail "second init did not reuse ($?)"

  # Fixture 5: checkpoint with nothing to commit ⇒ noop.
  (
    cd "$repo"
    out="$(bash "$script_abs" checkpoint alpha 'after G3' 2>/dev/null)"
    printf '%s' "$out" | grep -q '"status":"noop"' || exit 28
  ) || _st_fail "empty checkpoint was not a noop ($?)"

  # Fixture 6: checkpoint commits real tracked work in the worktree.
  (
    cd "$repo"
    echo "plan body" > ".claude/worktrees/forge-alpha/plan.md"
    out="$(bash "$script_abs" checkpoint alpha 'landed plan' 2>/dev/null)"
    printf '%s' "$out" | grep -q '"status":"committed"' || exit 29
    # The commit lands on the forge/alpha branch inside the worktree.
    git -C ".claude/worktrees/forge-alpha" log -1 --pretty=%s | grep -q 'forge(alpha): checkpoint — landed plan' || exit 30
  ) || _st_fail "checkpoint did not commit tracked work ($?)"

  # Fixture 7: nesting guard — init from INSIDE the linked worktree skips.
  (
    cd "${repo}/.claude/worktrees/forge-alpha"
    out="$(bash "$script_abs" init beta 2>/dev/null)"
    printf '%s' "$out" | grep -q 'already-in-worktree' || exit 31
  ) || _st_fail "nesting guard did not fire ($?)"

  # Fixture 8: opt-out via env ⇒ disabled.
  (
    cd "$repo"
    out="$(FORGE_WORKTREE=off bash "$script_abs" init gamma 2>/dev/null)"
    printf '%s' "$out" | grep -q '"status":"disabled"' || exit 32
  ) || _st_fail "env opt-out did not disable ($?)"

  # Fixture 9: opt-out via comfort-posture ⇒ disabled.
  (
    cd "$repo"
    mkdir -p .ravenclaude
    echo 'forge_worktree: off' > .ravenclaude/comfort-posture.yaml
    out="$(bash "$script_abs" init delta 2>/dev/null)"
    printf '%s' "$out" | grep -q '"status":"disabled"' || exit 33
    rm -f .ravenclaude/comfort-posture.yaml
  ) || _st_fail "comfort-posture opt-out did not disable ($?)"

  if [ "$ST_RC" -eq 0 ]; then
    echo "SELF-TEST PASS: forge-worktree.sh (9 fixtures)"
  fi
  return "$ST_RC"
}

# --- dispatch ---------------------------------------------------------------

main() {
  local sub="${1:-}"; shift || true
  case "$sub" in
    init)        cmd_init "$@" ;;
    checkpoint)  cmd_checkpoint "$@" ;;
    path)        cmd_path "$@" ;;
    --self-test|self-test) cmd_self_test ;;
    ""|-h|--help|help)
      grep -E '^#( |$)' "$0" | sed -E 's/^# ?//'
      ;;
    *)
      echo "forge-worktree.sh: unknown subcommand '$sub' (init|checkpoint|path|--self-test)" >&2
      exit 2
      ;;
  esac
}

main "$@"
