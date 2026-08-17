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

T="$(mktemp -d)" || { printf '  ✗ mktemp -d failed\n'; exit 1; }
# Unchecked, an empty $T would send `mkdir -p "$T/live"` to /live and leave the
# trap deleting "" — harmless as a user, litter as root in a container.
[ -n "$T" ] && [ -d "$T" ] || { printf '  ✗ mktemp -d produced no usable dir\n'; exit 1; }
trap 'rm -rf "$T"' EXIT

# Reintroduce the defect by rewriting worktree_state's BODY so it can never
# return UNKNOWN — i.e. it collapses "I could not look" back into "clean",
# which is exactly the pre-fix behaviour.
#
# ⛔ AN EARLIER VERSION OF THIS MUTATION WAS VACUOUS, and the way it failed is
# the whole reason this comment is long. It rewrote the single call site
# `status="$(worktree_state "$d")"` — which occurs ONLY in list_worktrees, the
# --status DISPLAY path. remove_all_clean calls `case "$(worktree_state "$d")"`
# and remove_one calls `case "$(worktree_state "$wt_dir")"`, neither of which
# matched. So under --must-fail-nofix the two assertions that measure actual
# DATA LOSS still passed with "the fix removed", and the gate's own header
# claimed it was proven to measure the defect. It was proven to measure the
# cosmetic half.
#
# Mutating the FUNCTION covers every caller by construction — present and
# future — which a call-site regex cannot promise.
make_mutant() { # $1=src $2=dest
  awk '
    /^worktree_state\(\) \{/ { inside = 1; print; print "  git -C \"$1\" status --porcelain >/dev/null 2>&1"; print "  if [ -n \"$(git -C \"$1\" status --porcelain 2>/dev/null)\" ]; then printf DIRTY; else printf clean; fi"; next }
    inside && /^\}/          { inside = 0; print; next }
    inside                   { next }
    { print }
  ' "$1" > "$2"
}

# Assert the mutation actually landed. A mutation that silently no-ops turns the
# teeth half into a second copy of the positive half.
mutant_is_defective() { # $1=mutant path -> 0 if the fix is genuinely gone
  ! grep -q "printf 'UNKNOWN'" "$1"
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
build_fixture() { # $1=dest root -> 0 on success
  r="$1"
  mkdir -p "$r/.claude/worktrees" || return 1
  git -C "$r" init -q || return 1
  git -C "$r" config user.email t@example.com || return 1
  git -C "$r" config user.name t || return 1
  printf 'seed\n' > "$r/seed.txt"
  git -C "$r" add seed.txt || return 1
  git -C "$r" -c commit.gpgsign=false commit -qm seed || return 1

  # ⛔ CONTAINMENT. worktree-clean.sh derives REPO_ROOT from `git rev-parse
  # --show-toplevel`, which walks UPWARD. If `git init` above ever failed while
  # $TMPDIR sat inside a git repository, `--all` would resolve to the ENCLOSING
  # repo and delete its worktrees. Not reachable with mktemp -d -> /var/folders,
  # but TMPDIR is environment-controlled and CI runners point it into the
  # workspace. Assert the fixture is its own toplevel before anything runs.
  top="$(git -C "$r" rev-parse --show-toplevel 2>/dev/null || true)"
  [ -n "$top" ] && [ "$top" -ef "$r" ] || {
    printf '  ✗ fixture is not its own git toplevel (got %s) — refusing to run --all\n' "${top:-<none>}"
    return 1
  }

  # ⛔ All three are REAL linked worktrees (`git worktree add`), not standalone
  # `git init` repos. The earlier fixture used `git init` for cleanwt, so it was
  # not a worktree of the fixture repo at all — `git worktree remove` refused it
  # and --all NEVER DELETED ANYTHING in this test. There was therefore no
  # passing assertion on the deletion path, in a gate about a deletion bug.
  git -C "$r" worktree add -q "$r/.claude/worktrees/cleanwt" >/dev/null 2>&1 || return 1
  git -C "$r" worktree add -q "$r/.claude/worktrees/dirtywt" >/dev/null 2>&1 || return 1
  git -C "$r" worktree add -q "$r/.claude/worktrees/brokenwt" >/dev/null 2>&1 || return 1

  printf 'uncommitted\n' > "$r/.claude/worktrees/dirtywt/pending.txt"
  printf 'work that would be lost\n' > "$r/.claude/worktrees/brokenwt/precious.txt"

  # UNKNOWN shape: corrupt the worktree's index. `git status` then exits 128
  # with EMPTY stdout — byte-identical to a clean tree's output.
  # Measured 2026-08-17: corrupt index -> status rc=128; healthy -> rc=0.
  #
  # ⛔ Chosen over the orphaned-admin-dir shape ON PURPOSE. Both yield UNKNOWN,
  # but `git worktree remove` REFUSES an orphaned-admin-dir tree outright
  # (rc=128), so "brokenwt survived" would have passed no matter what the script
  # decided — the assertion would have been measuring git, not us. It still
  # cannot be measured by survival alone (git refuses the corrupt shape too,
  # rc=128 measured), which is why the teeth assertion below keys on the
  # script's DECISION (the UNKNOWN skip line), not on the file surviving.
  printf 'GARBAGE-NOT-AN-INDEX' > "$r/.git/worktrees/brokenwt/index"

  # ⛔ THE UPWARD-WALK CLASS. .claude/worktrees/ must be gitignored and the
  # parent clean, or these read DIRTY and the assertions are vacuous — the
  # untracked file would show in the PARENT's status. With the ignore in place
  # git walks up, finds the clean parent, exits 0 with EMPTY stdout, and the
  # tree classifies `clean` while never having been inspected at all.
  printf '.claude/worktrees/\n' > "$r/.gitignore"
  git -C "$r" add .gitignore >/dev/null 2>&1 || return 1
  git -C "$r" -c commit.gpgsign=false commit -qm ignore >/dev/null 2>&1 || return 1
  mkdir -p "$r/.claude/worktrees/g_plaindir"
  printf 'G-PRECIOUS\n' > "$r/.claude/worktrees/g_plaindir/keep.txt"
  git -C "$r" worktree add -q "$r/.claude/worktrees/h_nogit" >/dev/null 2>&1 || return 1
  printf 'H-PRECIOUS\n' > "$r/.claude/worktrees/h_nogit/keep.txt"
  rm -f "$r/.claude/worktrees/h_nogit/.git"

  # A plain non-git subdirectory does NOT reproduce UNKNOWN: git's discovery
  # walks UPWARD, finds the parent repo, succeeds, and reports the file as
  # untracked — the fixture reads DIRTY and the gate passes without ever
  # exercising the defect. That mistake was made and caught while writing this.
  return 0
}

status_of() { # $1=root $2=slug -> prints the classification column
  ( cd "$1" && bash "$SUT" --status 2>/dev/null ) \
    | awk -v s="$2" '$1 == s { print $2 }'
}

# ------------------------------------------------------------ positive half ---
# ⛔ The return value is load-bearing. This file runs `set -uo pipefail` with NO
# `-e`, so a bare `build_fixture "$T/live"` discards the failure — the
# containment guard inside it would print "refusing to run --all" and then --all
# would run anyway. And `mkdir -p "$r/.claude/worktrees"` happens BEFORE
# `git init`, so on failure the dir still exists, `cd` succeeds, and
# worktree-clean.sh's `git rev-parse --show-toplevel` walks UPWARD into whatever
# repo encloses $TMPDIR. A guard that announces a refusal it does not perform is
# worse than no guard.
build_fixture "$T/live" || {
  fail "live fixture failed to build — refusing to run --all against an unverified tree"
  printf '\ncheck-worktree-state (Gate 216): aborted\n'
  exit 1
}

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

# The upward-walk half: git exits 0 by resolving to an ANCESTOR, so rc==0 is not
# evidence THIS directory was inspected.
PLAIN_S="$(status_of "$T/live" g_plaindir)"
NOGIT_S="$(status_of "$T/live" h_nogit)"
if [ "$PLAIN_S" = "UNKNOWN" ]; then
  pass "a plain directory reads UNKNOWN (git resolved to an ancestor, not this tree)"
else
  fail "plain directory read '$PLAIN_S' — rc=0 from an ANCESTOR was trusted as an inspection"
fi
if [ "$NOGIT_S" = "UNKNOWN" ]; then
  pass "a registered worktree with .git removed reads UNKNOWN"
else
  fail "worktree with .git removed read '$NOGIT_S' (expected UNKNOWN)"
fi

# --- the deletion path -------------------------------------------------------
( cd "$T/live" && bash "$SUT" --all >"$T/all.out" 2>&1 )

# POSITIVE CONTROL on deletion. Without this the three assertions below could
# all pass against a script that deletes NOTHING — "it didn't delete the broken
# one" is worthless if it never deletes anything. Measured: a clean linked
# worktree IS removable (unforced `git worktree remove` rc=0).
if [ ! -d "$T/live/.claude/worktrees/cleanwt" ]; then
  pass "--all DOES delete a genuinely clean worktree (deletion is detectable here)"
else
  fail "--all did not delete the clean worktree — every 'did not delete' assertion below is vacuous"
fi

if [ -f "$T/live/.claude/worktrees/dirtywt/pending.txt" ]; then
  pass "--all did not delete the dirty worktree"
else
  fail "--all DELETED a worktree holding uncommitted work"
fi

if [ -f "$T/live/.claude/worktrees/brokenwt/precious.txt" ]; then
  pass "--all did not delete the worktree it could not inspect"
else
  fail "--all DELETED an un-inspectable worktree (the defect this gate exists for)"
fi

# ⛔ Asserted AFTER --all runs. An earlier draft placed the equivalent check
# BEFORE the invocation, where it could not fail — proven by pointing the gate
# at a stand-in that deletes every worktree slot: it stayed green while every
# file it names was destroyed. Order is the whole assertion.
if [ -f "$T/live/.claude/worktrees/g_plaindir/keep.txt" ] \
   && [ -f "$T/live/.claude/worktrees/h_nogit/keep.txt" ]; then
  pass "--all left both upward-walk shapes on disk (asserted AFTER --all ran)"
else
  fail "--all DELETED an upward-walk shape it never actually inspected"
fi

# ⛔ Bound to the SLUG, not a bare grep for the word. `grep -q UNKNOWN` over
# combined stdout+stderr passes if the string appears anywhere at all.
if grep -q 'skipped brokenwt (UNKNOWN' "$T/all.out" 2>/dev/null; then
  pass "--all names brokenwt as UNKNOWN, so an operator can tell inspection failed"
else
  fail "--all did not report brokenwt as UNKNOWN"
fi

# The remedy must not be a runnable --force command (it either fails on this
# shape or destroys unreviewed work, depending on the invisible cause).
if grep -q -- '--force' "$T/all.out" 2>/dev/null; then
  fail "--all's UNKNOWN advice still recommends --force on a tree it could not inspect"
else
  pass "--all's UNKNOWN advice does not recommend --force"
fi

# remove_one must refuse UNKNOWN even when --force is passed.
rm_out="$( cd "$T/live" && bash "$SUT" brokenwt --force 2>&1 )" || true
if [ -f "$T/live/.claude/worktrees/brokenwt/precious.txt" ]; then
  pass "remove_one --force refuses an un-inspectable worktree"
else
  fail "remove_one --force DELETED an un-inspectable worktree (reproduced data loss)"
fi
case "$rm_out" in
  *"could not inspect"*) pass "remove_one names the reason it refused" ;;
  *) fail "remove_one refused without saying why: $rm_out" ;;
esac

# --- the config vector -------------------------------------------------------
# ⛔ A status that RAN, against the RIGHT tree, and exited 0 can still report
# "nothing here" because CONFIG told it to stay quiet. Neither setting below
# needs an adversary — both are ordinary things a user types once and forgets,
# and git honours them from the repo-local config, $HOME, XDG, the system
# config, or GIT_CONFIG_*. The tree then classifies `clean` and --all deletes
# uncommitted work.
#
# The three earlier UNKNOWN shapes cannot cover this: they are all cases where
# git FAILED or resolved elsewhere. Here git succeeds, on the right tree, and
# answers honestly to a question that was narrowed behind the script's back.
#
# Two independent config sources are asserted because they arrive by different
# routes — a repo-local key needs no environment at all, and $HOME survives an
# env scrub that only enumerates GIT_*. A fix that closes one and not the other
# is not a fix.
config_vector_case() { # $1=label $2=root $3... = env assignments for the run
  label="$1"; root="$2"; shift 2
  if ! build_fixture "$root"; then
    fail "config-vector fixture ($label) failed to build"
    return 1
  fi
  # Apply the caller's config-shaping step.
  cfg_setup "$root" || { fail "config-vector setup ($label) failed"; return 1; }

  ( cd "$root" && env "$@" bash "$SUT" --all >"$root/all.out" 2>&1 )

  # POSITIVE CONTROL, and it is not optional here. "dirtywt survived" is
  # worthless if --all deleted nothing at all — and a script that errored out on
  # the crafted config would produce exactly that, passing the real assertion
  # for entirely the wrong reason.
  if [ ! -d "$root/.claude/worktrees/cleanwt" ]; then
    pass "$label: --all still deletes a genuinely clean worktree (deletion is detectable)"
  else
    fail "$label: --all deleted nothing — the survival assertion below is vacuous"
  fi

  if [ -f "$root/.claude/worktrees/dirtywt/pending.txt" ]; then
    pass "$label: uncommitted work survived --all"
  else
    fail "$label: --all DELETED a worktree holding uncommitted work (config steered the probe)"
  fi
}

cfg_setup() { git -C "$1" config status.showUntrackedFiles no; }
config_vector_case "repo-local status.showUntrackedFiles=no" "$T/cfg_local"

# $HOME carries BOTH keys: showUntrackedFiles suppresses the listing outright,
# and core.excludesFile hides the same files by a second, independent route —
# so pinning only one of the two would still lose this case.
mkdir -p "$T/evilhome"
printf '*\n' > "$T/evilhome/exclude"
{
  printf '[status]\n\tshowUntrackedFiles = no\n'
  printf '[core]\n\texcludesFile = %s/evilhome/exclude\n' "$T"
} > "$T/evilhome/.gitconfig"
cfg_setup() { :; }
config_vector_case "\$HOME gitconfig (showUntrackedFiles + excludesFile)" "$T/cfg_home" \
  "HOME=$T/evilhome" "XDG_CONFIG_HOME=$T/evilhome"

# ----------------------------------------------------------- must-fail half ---
# Restore the original expression. The broken fixture MUST then read clean.
MUT="$T/mutant.sh"
make_mutant "$SUT" "$MUT"

if mutant_is_defective "$MUT"; then
  if build_fixture "$T/mutant"; then
    MB="$( ( cd "$T/mutant" && bash "$MUT" --status 2>/dev/null ) | awk '$1=="brokenwt"{print $2}' )"
    if [ "$MB" = "clean" ]; then
      pass "teeth: with UNKNOWN removed, --status misreads broken as clean"
    else
      fail "teeth: mutant did not reproduce the display defect (read '$MB')"
    fi

    # ⛔ THE ASSERTION THAT MATTERS, and it keys on the script's DECISION.
    # Survival cannot be used here: `git worktree remove` refuses the corrupt
    # shape (rc=128 measured), so brokenwt survives whatever the script decides.
    # What changes is whether the script CHOSE to skip it. The fixed script
    # prints the UNKNOWN skip line; the mutant classifies it clean and attempts
    # removal instead. If this line is still present in the mutant's output, the
    # deletion path was never mutated and the teeth are cosmetic — which is
    # exactly how the previous version of this gate was vacuous.
    ( cd "$T/mutant" && bash "$MUT" --all >"$T/mutant-all.out" 2>&1 )
    if grep -q 'skipped brokenwt (UNKNOWN' "$T/mutant-all.out" 2>/dev/null; then
      fail "teeth: the mutant STILL skips brokenwt as UNKNOWN — the deletion path was not mutated (vacuous gate)"
    else
      pass "teeth: with UNKNOWN removed, --all no longer skips brokenwt (deletion path IS covered)"
    fi
  else
    fail "teeth: mutant fixture failed to build"
  fi
else
  fail "teeth: mutation did not apply — cannot prove the gate has teeth"
fi

# --- narrow teeth for the config vector --------------------------------------
# ⛔ The make_mutant teeth above are TOO BROAD to prove anything about the config
# assertions: that mutant deletes the whole three-state fix, so its failures are
# over-determined. A stand-in that keeps every other guard and strips ONLY the
# two call-site pins is the sharp control — it isolates this one change, and it
# is precisely the shape that shipped and lost data.
CMUT="$T/cfg-mutant.sh"
sed 's/ -c core\.excludesFile=\/dev\/null//; s/ --untracked-files=normal//' "$SUT" > "$CMUT"
# ⛔ Anchored on the STATUS CALL, not on the bare strings. Both names also occur
# in the prose above that call explaining why they are there, so a whole-file
# grep is satisfied by the comment and reports "not applied" on a stand-in that
# applied perfectly — this repo's own source-scan-matches-PROSE trap, hit here
# while writing this gate.
if grep -q 'out=.*status --porcelain.*--untracked-files' "$CMUT" \
   || grep -q 'out=.*excludesFile' "$CMUT"; then
  fail "teeth: config-pin stand-in did not apply — cannot prove the config assertions have teeth"
elif ! grep -q "printf 'UNKNOWN'" "$CMUT"; then
  fail "teeth: config-pin stand-in lost the UNKNOWN fix too — no longer a narrow control"
elif build_fixture "$T/cfgmut"; then
  git -C "$T/cfgmut" config status.showUntrackedFiles no
  ( cd "$T/cfgmut" && bash "$CMUT" --all >/dev/null 2>&1 )
  if [ -f "$T/cfgmut/.claude/worktrees/dirtywt/pending.txt" ]; then
    fail "teeth: uncommitted work survived even WITHOUT the config pins — the config assertions are vacuous"
  else
    pass "teeth: strip only the config pins and uncommitted work IS deleted (config assertions are real)"
  fi
else
  fail "teeth: config-pin stand-in fixture failed to build"
fi

printf '\n'
if [ "$FAILED" -eq 0 ]; then
  printf 'check-worktree-state (Gate 216): ALL PASS\n'
  exit 0
fi
printf 'check-worktree-state (Gate 216): %d FAILED\n' "$FAILED"
exit 1
