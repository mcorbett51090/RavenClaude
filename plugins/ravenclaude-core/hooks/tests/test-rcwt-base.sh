#!/usr/bin/env bash
# test-rcwt-base.sh — `rcwt new <task> <base>` must refuse a base that git would
# parse as an option, and must never reach `git fetch` with it.
#
# Why: rcwt passed the base straight to `git fetch --prune origin "$base"`, and
# git parses a leading '-' there as an option, so a base of
# '--upload-pack=<cmd>' ran <cmd> with the user's rights (repo-review
# 2026-10-19, corescripts-18). The fix validates the base with
# `git check-ref-format --branch` and puts '--' before the refspec.
#
# A PATH shim records every git invocation, so "never runs git fetch" is an
# observation, not an inference from the exit code. Teeth: the same run against
# a mutant with both defenses removed must execute the planted command.
#
# The option string is assembled at runtime, never written literally.
# bash 3.2-safe; no GNU-only tools. Invoke with `bash <this file>`.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
RCWT="$HERE/../../bin/rcwt"
[ -f "$RCWT" ] || { echo "FAIL: rcwt not found at $RCWT"; exit 1; }
REAL_GIT="$(command -v git)" || { echo "FAIL: git not on PATH"; exit 1; }

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

fails=0
pass() { echo "  ok   $1"; }
fail() { echo "  FAIL $1"; fails=$((fails + 1)); }

# git shim: log argv (one line per call), then run the real git.
mkdir -p "$T/shim"
GITLOG="$T/git-calls.log"
: > "$GITLOG"
{
  printf '#!/bin/sh\n'
  printf 'printf "%%s\\n" "$*" >> "%s"\n' "$GITLOG"
  printf 'exec "%s" "$@"\n' "$REAL_GIT"
} > "$T/shim/git"
chmod +x "$T/shim/git"

# A bare origin with a main branch, and a clone of it.
"$REAL_GIT" init -q --bare "$T/origin.git"
"$REAL_GIT" init -q "$T/seed"
(
  cd "$T/seed" || exit 1
  "$REAL_GIT" config user.email t@example.invalid
  "$REAL_GIT" config user.name test
  echo a > a
  "$REAL_GIT" add a
  "$REAL_GIT" commit -qm init
  "$REAL_GIT" branch -M main
  "$REAL_GIT" push -q "$T/origin.git" main 2>/dev/null
) || { echo "FAIL: fixture"; exit 1; }
"$REAL_GIT" clone -q "$T/origin.git" "$T/clone" 2>/dev/null

# $1 = rcwt to run, $2 = task, $3 = base. Echoes rcwt's exit code.
_run() {
  (
    cd "$T/clone" || exit 99
    PATH="$T/shim:$PATH" RAVENCLAUDE_WORKTREE_ROOT="$T/wts" RCWT_NO_CHAT_SANDBOX=1 \
      bash "$1" new "$2" "$3" > "$T/out.log" 2>&1
    echo $?
  )
}

MARK="$T/marker"
bad_base="--upload"
bad_base="${bad_base}-pack=touch $MARK"

echo "== real rcwt =="
: > "$GITLOG"
rc="$(_run "$RCWT" probe-task "$bad_base")"
[ "$rc" = "2" ] && pass "option-shaped base exits 2" || fail "option-shaped base exits 2 (got $rc)"
[ -e "$MARK" ] && fail "planted command did NOT run" || pass "planted command did NOT run"
grep -q '^-C .* fetch' "$GITLOG" && fail "git fetch was never invoked" || pass "git fetch was never invoked"
[ -d "$T/wts/probe-task" ] && fail "no worktree was created" || pass "no worktree was created"

: > "$GITLOG"
rc="$(_run "$RCWT" good-task main)"
[ "$rc" = "0" ] && pass "a valid base still works (exit 0)" || fail "a valid base still works (got $rc: $(tail -n 2 "$T/out.log"))"
[ -d "$T/wts/good-task" ] && pass "the valid-base worktree exists" || fail "the valid-base worktree exists"
grep -q 'fetch --prune origin -- main' "$GITLOG" \
  && pass "fetch ends option parsing with -- before the refspec" \
  || fail "fetch ends option parsing with -- before the refspec"

echo "== teeth: both defenses removed =="
mkdir -p "$T/mutant/bin"
sed -e 's/git check-ref-format --branch "\$base"/true/' \
    -e 's/fetch --prune origin -- "\$base"/fetch --prune origin "$base"/' \
    "$RCWT" > "$T/mutant/bin/rcwt"
if cmp -s "$RCWT" "$T/mutant/bin/rcwt"; then
  fail "mutant differs from the real script (sed targets not found)"
else
  rm -f "$MARK"
  _run "$T/mutant/bin/rcwt" probe-task2 "$bad_base" >/dev/null
  [ -e "$MARK" ] && pass "mutant runs the planted command (assertions have teeth)" \
    || fail "mutant runs the planted command (assertions have teeth)"
fi

if [ "$fails" -eq 0 ]; then
  echo "PASS: test-rcwt-base.sh"
  exit 0
fi
echo "FAIL: test-rcwt-base.sh ($fails failing)"
exit 1
