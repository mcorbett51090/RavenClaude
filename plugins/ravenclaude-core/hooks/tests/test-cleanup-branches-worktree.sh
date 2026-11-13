#!/usr/bin/env bash
# test-cleanup-branches-worktree.sh — cleanup-branches.sh must refuse a merged
# branch that is checked out in another (live or prunable) worktree, and still
# delete a merged branch that no worktree uses.
#
# Why: the script deletes with `git update-ref -d`, which, unlike
# `git branch -d`, does not refuse a branch checked out elsewhere. The linked
# worktree was left on an unborn HEAD whose next commit is a parentless root
# (repo-review 2026-10-19, corescripts-9).
#
# Teeth: the same assertions are re-run against a mutant copy with the worktree
# check neutered; the in-use branch must then be DELETED, or the positive
# assertions prove nothing.
#
# bash 3.2-safe; no GNU-only tools. Invoke with `bash <this file>`.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
CB="$HERE/../../scripts/cleanup-branches.sh"
[ -f "$CB" ] || { echo "FAIL: cleanup-branches.sh not found at $CB"; exit 1; }

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
mkdir -p "$T/bin"
# gh that always fails: check 1 (merged PR) and the open-PR veto stay silent,
# so the verdict rests on ancestry + the worktree check alone.
printf '#!/bin/sh\nexit 1\n' > "$T/bin/gh"
chmod +x "$T/bin/gh"
PATH="$T/bin:$PATH"
export PATH

fails=0
pass() { echo "  ok   $1"; }
fail() { echo "  FAIL $1"; fails=$((fails + 1)); }

# Build a repo: main + three branches at main's tip (all "merged"):
#   feature/live    checked out in a live linked worktree
#   feature/gone    checked out in a worktree whose dir was removed (prunable)
#   feature/free    no worktree
_build() {
  local root="$1"
  git init -q "$root/repo"
  (
    cd "$root/repo" || exit 1
    git config user.email t@example.invalid
    git config user.name test
    echo a > a
    git add a
    git commit -qm init
    git branch -M main
    git branch feature/live
    git branch feature/gone
    git branch feature/free
    git worktree add -q "$root/wt-live" feature/live
    git worktree add -q "$root/wt-gone" feature/gone
  ) || return 1
  rm -rf "$root/wt-gone"
}

# $1 = script under test, $2 = scratch root. Prints the script's output.
_run() {
  (cd "$2/repo" && bash "$1" feature/live feature/gone feature/free 2>&1)
}

_has_branch() { git -C "$1/repo" show-ref --verify --quiet "refs/heads/$2"; }

echo "== real cleanup-branches.sh =="
R="$T/real"
mkdir -p "$R"
_build "$R" || { echo "FAIL: fixture build"; exit 1; }
out="$(_run "$CB" "$R")"
rc=$?
[ "$rc" -eq 3 ] && pass "exit 3 (at least one refused)" || fail "exit 3 (got $rc)"
_has_branch "$R" feature/live && pass "branch in a live worktree is KEPT" || fail "branch in a live worktree is KEPT"
# Match on the basename: git may print the realpath (macOS /var -> /private/var).
printf '%s' "$out" | grep -q "feature/live.*checked out in worktree .*/wt-live" \
  && pass "refusal names the live worktree path" || fail "refusal names the live worktree path"
_has_branch "$R" feature/gone && pass "branch in a prunable worktree is KEPT" || fail "branch in a prunable worktree is KEPT"
_has_branch "$R" feature/free && fail "merged branch with no worktree is DELETED" || pass "merged branch with no worktree is DELETED"
git -C "$R/wt-live" rev-parse --verify --quiet HEAD >/dev/null \
  && pass "the live worktree still has a born HEAD" || fail "the live worktree still has a born HEAD"

echo "== teeth: worktree check neutered =="
M="$T/mutant"
mkdir -p "$M"
sed 's/-n "\$_wt"/-n ""/' "$CB" > "$M/cleanup-branches.sh"
if cmp -s "$CB" "$M/cleanup-branches.sh"; then
  fail "mutant differs from the real script (sed target not found)"
else
  _build "$M" || { echo "FAIL: mutant fixture build"; exit 1; }
  _run "$M/cleanup-branches.sh" "$M" >/dev/null
  _has_branch "$M" feature/live \
    && fail "mutant deletes the in-use branch (assertions have teeth)" \
    || pass "mutant deletes the in-use branch (assertions have teeth)"
fi

if [ "$fails" -eq 0 ]; then
  echo "PASS: test-cleanup-branches-worktree.sh"
  exit 0
fi
echo "FAIL: test-cleanup-branches-worktree.sh ($fails failing)"
exit 1
