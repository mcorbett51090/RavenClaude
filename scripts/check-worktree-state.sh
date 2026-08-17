#!/usr/bin/env bash
# check-worktree-state.sh — Gate 216. Proves scripts/worktree-clean.sh
# distinguishes "I looked and it is clean" from "I could not look".
#
# THE DEFECT THIS CLOSES (found 2026-08-17)
# ----------------------------------------
# remove_all_clean() gated deletion on:
#
#     if [ -z "$(git -C "$d" status --porcelain 2>/dev/null)" ]; then remove_one …
#
# When `git status` FAILS — not a git repo, corrupt/absent .git, a linked
# worktree whose parent repo is gone, git off PATH, permission denied — it
# writes NOTHING to stdout and exits non-zero. The 2>/dev/null hides the error,
# and the empty stdout is byte-identical to a genuinely clean tree's. So the
# failed inspection read as "clean" and the worktree was DELETED unexamined.
# Measured 2026-08-17: a non-git dir yields exit 128 with empty stdout.
#
# The fix is worktree_state(), which captures the exit code separately and emits
# a third state, UNKNOWN, that fails toward NOT deleting.
#
# WHY THE MUST-FAIL HALF IS LOAD-BEARING
# --------------------------------------
# The positive assertions alone would also pass against a script that classified
# EVERYTHING as UNKNOWN. The must-fail half restores the original one-line
# expression and requires the broken fixture to then be classified `clean` — so
# this gate is proven to measure the actual defect rather than merely be green.
#
# Run directly: bash scripts/check-worktree-state.sh
# Run via gate: scripts/audit-gates.sh --check 216

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SUT="$REPO_ROOT/scripts/worktree-clean.sh"
FAILED=0
pass() { printf '  ✓ %s\n' "$1"; }
fail() { printf '  ✗ %s\n' "$1"; FAILED=$((FAILED + 1)); }

[ -f "$SUT" ] || { printf '  ✗ subject under test missing: %s\n' "$SUT"; exit 1; }

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

# Rewrite worktree_state's call site back to the original one-line expression,
# reintroducing the defect. Used twice: for this checker's own must-fail half,
# and for --must-fail-nofix (the external teeth invocation audit-gates records
# with must_fail).
make_mutant() { # $1=src $2=dest
  awk '
    /status="\$\(worktree_state "\$d"\)"/ {
      print "    if [ -z \"$(git -C \"$d\" status --porcelain 2>/dev/null)\" ]; then status=clean; else status=DIRTY; fi"
      next
    }
    { print }
  ' "$1" > "$2"
}

# ⛔ TEETH MODE. Points the positive assertions at a MUTANT with the fix removed.
# audit-gates records this run with must_fail: if it PASSES, the positive
# assertions are not actually measuring the fix and this gate is vacuous.
# An external oracle beats a self-asserted one — see the self-certifying-change
# trap in plugins/ravenclaude-core/CLAUDE.md.
if [ "${1:-}" = "--must-fail-nofix" ]; then
  make_mutant "$SUT" "$T/nofix.sh"
  SUT="$T/nofix.sh"
  printf '  [teeth mode] running positive assertions against a fix-removed mutant\n'
fi

# ---------------------------------------------------------------- fixture ----
# A host repo whose .claude/worktrees/ holds three shapes: genuinely clean,
# genuinely dirty, and un-inspectable (a plain directory with no .git at all).
build_fixture() { # $1=dest root
  r="$1"
  mkdir -p "$r/.claude/worktrees"
  git -C "$r" init -q
  git -C "$r" config user.email t@example.com
  git -C "$r" config user.name t
  printf 'seed\n' > "$r/seed.txt"
  git -C "$r" add seed.txt
  git -C "$r" -c commit.gpgsign=false commit -qm seed

  mkdir -p "$r/.claude/worktrees/cleanwt"
  git -C "$r/.claude/worktrees/cleanwt" init -q
  git -C "$r/.claude/worktrees/cleanwt" config user.email t@example.com
  git -C "$r/.claude/worktrees/cleanwt" config user.name t
  printf 'x\n' > "$r/.claude/worktrees/cleanwt/f.txt"
  git -C "$r/.claude/worktrees/cleanwt" add f.txt
  git -C "$r/.claude/worktrees/cleanwt" -c commit.gpgsign=false commit -qm f

  mkdir -p "$r/.claude/worktrees/dirtywt"
  git -C "$r/.claude/worktrees/dirtywt" init -q
  printf 'uncommitted\n' > "$r/.claude/worktrees/dirtywt/pending.txt"

  # A STALE LINKED WORKTREE — created properly, then its admin dir under
  # .git/worktrees/ is orphaned. This is the real-world shape `git worktree
  # prune` exists for, and `git -C <dir> status` then exits 128 with EMPTY
  # stdout (verified 2026-08-17; the healthy worktree above exits 0, which is
  # the control proving this fixture can produce both answers).
  #
  # ⛔ A plain non-git subdirectory does NOT reproduce it: git's discovery walks
  # UPWARD, finds the parent repo, succeeds, and reports the file as untracked —
  # so the fixture would read DIRTY and the gate would pass without ever
  # exercising the defect. That mistake was made and caught while writing this.
  git -C "$r" worktree add -q "$r/.claude/worktrees/brokenwt" >/dev/null 2>&1
  printf 'work that would be lost\n' > "$r/.claude/worktrees/brokenwt/precious.txt"
  mv "$r/.git/worktrees/brokenwt" "$r/.git/worktrees/_orphaned"
}

status_of() { # $1=root $2=slug -> prints the classification column
  ( cd "$1" && bash "$SUT" --status 2>/dev/null ) \
    | awk -v s="$2" '$1 == s { print $2 }'
}

# ------------------------------------------------------------ positive half ---
build_fixture "$T/live"

CLEAN_S="$(status_of "$T/live" cleanwt)"
DIRTY_S="$(status_of "$T/live" dirtywt)"
BROKEN_S="$(status_of "$T/live" brokenwt)"

if [ "$CLEAN_S" = "clean" ]; then
  pass "a genuinely clean worktree reads clean"
else
  fail "clean worktree read '$CLEAN_S' (expected clean)"
fi

if [ "$DIRTY_S" = "DIRTY" ]; then
  pass "a dirty worktree reads DIRTY"
else
  fail "dirty worktree read '$DIRTY_S' (expected DIRTY)"
fi

if [ "$BROKEN_S" = "UNKNOWN" ]; then
  pass "an un-inspectable worktree reads UNKNOWN, not clean"
else
  fail "un-inspectable worktree read '$BROKEN_S' (expected UNKNOWN)"
fi

# --all must SKIP the un-inspectable tree and leave its contents on disk.
( cd "$T/live" && bash "$SUT" --all >"$T/all.out" 2>&1 )
if [ -f "$T/live/.claude/worktrees/brokenwt/precious.txt" ]; then
  pass "--all did not delete the worktree it could not inspect"
else
  fail "--all DELETED an un-inspectable worktree (the defect this gate exists for)"
fi
if grep -q 'UNKNOWN' "$T/all.out" 2>/dev/null; then
  pass "--all reports the skip reason as UNKNOWN"
else
  fail "--all skipped silently — an operator cannot tell inspection failed"
fi

# ----------------------------------------------------------- must-fail half ---
# Restore the original expression. The broken fixture MUST then read clean.
MUT="$T/mutant.sh"
make_mutant "$SUT" "$MUT"

if grep -q 'status=clean' "$MUT" && ! grep -q 'status="\$(worktree_state' "$MUT"; then
  build_fixture "$T/mutant"
  MB="$( ( cd "$T/mutant" && bash "$MUT" --status 2>/dev/null ) | awk '$1=="brokenwt"{print $2}' )"
  if [ "$MB" = "clean" ]; then
    pass "must-fail half: the original expression DOES misread broken as clean (gate has teeth)"
  else
    fail "must-fail half did not reproduce the defect (read '$MB') — gate may be vacuous"
  fi
else
  fail "must-fail half: mutation did not apply — cannot prove the gate has teeth"
fi

printf '\n'
if [ "$FAILED" -eq 0 ]; then
  printf 'check-worktree-state (Gate 216): ALL PASS\n'
  exit 0
fi
printf 'check-worktree-state (Gate 216): %d FAILED\n' "$FAILED"
exit 1
