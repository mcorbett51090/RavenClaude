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
# The unmutated subject, kept so mutant_is_defective can byte-compare against it
# even in teeth mode (where SUT is reassigned to the mutant).
SUT_PRISTINE="$SUT"
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
  # ⛔ A BYTE COMPARISON, not a string grep. The previous version grepped for
  # `printf 'UNKNOWN'` — a literal that stopped appearing in the PRISTINE
  # subject once UNKNOWN was split into UNKNOWN-rc / UNKNOWN-scope. So it
  # returned "the fix is genuinely gone" unconditionally and its own
  # "mutation did not apply" branch became unreachable: a dead oracle, in the
  # guard whose comment warns that a no-op mutation makes the teeth half a
  # second copy of the positive half. A diff cannot rot when the strings change.
  ! diff -q "$SUT_PRISTINE" "$1" >/dev/null 2>&1
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

# ------------------------------------------------- invariant: no bare git ----
# ⛔ A SOURCE-SCAN, because the behavioural assertions cannot see this class.
# Rounds 3 and 4 both found holes of the same shape: the CLASSIFICATION calls
# were env-scrubbed while the DESTRUCTIVE ones were not, so an exported GIT_DIR
# steered the removal and `branch -d` at a different repository. Every fix that
# enumerated call sites left the next one open. Assert the invariant instead:
# every git invocation in the subject goes through rcgit.
# ⛔ Match git in a COMMAND POSITION only — line start, or after a shell
# separator. An earlier version matched `git ` anywhere and flagged
# `printf '      git said: '` and the wrapper's own `env … git "$@"` line: a
# grep satisfied by the thing being DESCRIBED rather than done, which is the
# same class this gate exists to catch, in the check written to catch it.
bare_git="$(grep -nE '(^|[;&|(]|\$\()[[:space:]]*git[[:space:]]' "$SUT" \
             | grep -v 'rcgit' \
             | grep -vE '^[0-9]+:[[:space:]]*#' || true)"
if [ -z "$bare_git" ]; then
  pass "invariant: every git call in the subject goes through the env-scrubbing wrapper"
else
  fail "bare git call(s) bypass the env scrub: $(printf '%s' "$bare_git" | head -3 | tr '\n' ' ')"
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
  # (this repo: .gitignore:47) git walks up, finds the clean parent, exits 0
  # with EMPTY stdout, and the tree classifies `clean` while never having been
  # inspected at all. Measured 2026-08-17: both shapes gave status rc=0,
  # out_len=0, toplevel=<PARENT>.
  printf '.claude/worktrees/\n.env\nnode_modules/\n' > "$r/.gitignore"
  git -C "$r" add .gitignore >/dev/null 2>&1 || return 1
  git -C "$r" -c commit.gpgsign=false commit -qm ignore >/dev/null 2>&1 || return 1

  # linktarget: a REGISTERED worktree, so the symlink assertion's oracle is this
  # script's guard rather than git's refusal (see the assertion's comment).
  git -C "$r" worktree add -q "$r/.claude/worktrees/linktarget" >/dev/null 2>&1 || return 1
  printf 'LINKTARGET\n' > "$r/.claude/worktrees/linktarget/keep.txt"
  git -C "$r/.claude/worktrees/linktarget" add keep.txt >/dev/null 2>&1 || true
  git -C "$r/.claude/worktrees/linktarget" -c commit.gpgsign=false commit -qm k >/dev/null 2>&1 || true

  # g_plaindir: a plain directory that was never a worktree at all.
  mkdir -p "$r/.claude/worktrees/g_plaindir"
  printf 'G-PRECIOUS\n' > "$r/.claude/worktrees/g_plaindir/keep.txt"
  # h_nogit: a REGISTERED worktree whose .git file has been removed.
  git -C "$r" worktree add -q "$r/.claude/worktrees/h_nogit" >/dev/null 2>&1 || return 1
  printf 'H-PRECIOUS\n' > "$r/.claude/worktrees/h_nogit/keep.txt"
  rm -f "$r/.claude/worktrees/h_nogit/.git"

  # A plain non-git subdirectory does NOT reproduce the *status-fails* UNKNOWN:
  # git's discovery walks UPWARD and succeeds. That is why it is a fixture for
  # the upward-walk class above, and why using it as the status-fails fixture
  # (the first mistake made writing this gate) produced a vacuous pass.
  # ⛔ IGNORED shape, added AFTER the .gitignore commit on purpose: the worktree
  # checks out HEAD, so a worktree created before that commit would not carry the
  # ignore rule and its .env would read as an ordinary untracked file — the tree
  # would classify DIRTY and the IGNORED assertions would pass for the wrong
  # reason, measuring nothing. `secrets.env` also matches nothing here; the file
  # must be exactly `.env` for the committed rule to hide it.
  git -C "$r" worktree add -q "$r/.claude/worktrees/ignoredwt" >/dev/null 2>&1 || return 1
  printf 'DB_PASSWORD=irreplaceable\n' > "$r/.claude/worktrees/ignoredwt/.env"
  mkdir -p "$r/.claude/worktrees/ignoredwt/node_modules/pkg"
  printf 'x\n' > "$r/.claude/worktrees/ignoredwt/node_modules/pkg/index.js"
  # ⛔ DETACHED shapes, BOTH of them. det_work is detached with its own commit
  # (no ref contains it — removing it loses the commit). det_safe is detached at
  # a ref tip, which is common and harmless. Without the second, an assertion
  # that "detached reads DETACHED" would pass against a script that flags EVERY
  # detached worktree — noise that gets the guard ignored on the real case.
  git -C "$r" worktree add -q --detach "$r/.claude/worktrees/det_work" >/dev/null 2>&1 || return 1
  ( cd "$r/.claude/worktrees/det_work" \
      && printf 'IRREPLACEABLE\n' > committed.txt \
      && git add committed.txt \
      && git -c commit.gpgsign=false commit -qm detached-work >/dev/null 2>&1 ) || return 1
  git -C "$r" worktree add -q --detach "$r/.claude/worktrees/det_safe" >/dev/null 2>&1 || return 1

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

# THE UPWARD-WALK CLASS: git status exits 0 by resolving to an ANCESTOR, so
# rc==0 is not evidence this directory was inspected.
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
# (the upward-walk SURVIVAL assertion lives after --all runs — see below)

# Any non-empty second argument must NOT silently upgrade to --force.
bad_flag_out="$( cd "$T/live" && bash "$SUT" cleanwt --froce 2>&1 )" || true
case "$bad_flag_out" in
  *"unknown flag"*) pass "a mistyped flag is rejected, not treated as --force" ;;
  *) fail "a mistyped flag was not rejected: $bad_flag_out" ;;
esac

# A symlink under the worktree root must be refused, not followed.
#
# ⛔ THE TARGET MUST BE SOMETHING GIT WILL ACTUALLY DELETE, or the assertion has
# no teeth. The first version pointed at a plain directory: worktree_state
# returned UNKNOWN via the -ef check and `git worktree remove` would have
# refused it anyway, so the assertion passed with BOTH -L guards stripped from
# the SUT — proven. Pointing it at a REGISTERED worktree of the fixture repo
# means only this script's guard stands between the link and deletion.
ln -s "$T/live/.claude/worktrees/linktarget" "$T/live/.claude/worktrees/e_link" 2>/dev/null || true
link_out="$( cd "$T/live" && bash "$SUT" e_link 2>&1 )" || true
if [ -f "$T/live/.claude/worktrees/linktarget/keep.txt" ]; then
  pass "a symlinked entry does not delete its target (a real worktree git would remove)"
else
  fail "a symlink under .claude/worktrees/ deleted a REGISTERED worktree via the link"
fi

# The ancestor case: .claude/worktrees itself symlinked. `[ -L "$wt_dir" ]`
# stats only the last component and passes; only full-path resolution catches
# it. Reproduced on both call sites before the fix.
# ⛔ The target must be OUTSIDE the repository. An earlier version of this
# fixture moved the worktrees dir to `$anc/.claude/_real_wt` — still inside the
# repo — so containment correctly ALLOWED it and the assertion failed against a
# working fix. Redirecting within your own repo is not the threat; escaping it
# is. Verified: with the target inside, --all removes (correctly); with the
# target outside, it must refuse.
anc="$T/anc"
if build_fixture "$anc" >/dev/null 2>&1; then
  mkdir -p "$T/outside_anc"
  mv "$anc/.claude/worktrees" "$T/outside_anc/_real_wt"
  ln -s "$T/outside_anc/_real_wt" "$anc/.claude/worktrees"
  ( cd "$anc" && bash "$SUT" --all >"$T/anc.out" 2>&1 ) || true
  # ⛔ Survival is the oracle, and it must name a file the fixture ACTUALLY
  # creates. An earlier version tested `cleanwt/f.txt`, which appears nowhere
  # else in this file — build_fixture never creates it — so that operand was
  # permanently false and the assertion rested entirely on a bare grep for the
  # word "symlink" anywhere in the output. seed.txt is committed by
  # build_fixture, so it exists.
  if [ -f "$T/outside_anc/_real_wt/cleanwt/seed.txt" ]; then
    pass "a symlinked worktree ROOT is refused (ancestor components resolve too)"
  else
    fail "a symlinked .claude/worktrees let --all delete through the ancestor link"
  fi
fi

# The OTHER ancestor shape: .claude itself symlinked. The previous fix guarded
# only .claude/worktrees, so this one still deleted outside the repo — the
# containment is now anchored to REPO_ROOT, which closes both by construction.
anc2="$T/anc2"
if build_fixture "$anc2" >/dev/null 2>&1; then
  mkdir -p "$T/outside_anc2"
  mv "$anc2/.claude" "$T/outside_anc2/_real_dotclaude"
  ln -s "$T/outside_anc2/_real_dotclaude" "$anc2/.claude"
  ( cd "$anc2" && bash "$SUT" --all >"$T/anc2.out" 2>&1 ) || true
  if [ -f "$T/outside_anc2/_real_dotclaude/worktrees/cleanwt/seed.txt" ]; then
    pass "a symlinked .claude ROOT is refused too (containment anchored to the repo)"
  else
    fail "a symlinked .claude let --all delete a worktree outside the repository"
  fi
else
  fail "ancestor-symlink fixture failed to build"
fi

# ⛔ The ignored-only class. `status --porcelain` is silent on ignored files BY
# DESIGN, so a tree holding only .env / node_modules produced empty output while
# git was working perfectly — no failure, no wrong subject, no misleading config.
# The probe simply answered a narrower question than the caller needed.
IGNORED_S="$(status_of "$T/live" ignoredwt)"
if [ "$IGNORED_S" = "IGNORED" ]; then
  pass "a worktree holding only ignored files reads IGNORED, not clean"
else
  fail "ignored-only worktree read '$IGNORED_S' (expected IGNORED)"
fi

# ⛔ The committed-work class. Every state above asks "is there UNCOMMITTED
# content here?"; this tree is clean by all of them and still holds the only
# copy of a commit.
DET_S="$(status_of "$T/live" det_work)"
SAFE_S="$(status_of "$T/live" det_safe)"
if [ "$DET_S" = "DETACHED" ]; then
  pass "a detached worktree whose commit no ref contains reads DETACHED"
else
  fail "detached-with-own-commit read '$DET_S' (expected DETACHED)"
fi
# THE NO-FALSE-POSITIVE HALF. Without it, flagging every detached worktree
# passes — and a guard that fires on the harmless case gets ignored on the
# harmful one.
if [ "$SAFE_S" = "clean" ]; then
  pass "a detached worktree at a reachable commit still reads clean (no false positive)"
else
  fail "detached-but-reachable read '$SAFE_S' (expected clean) — the guard fires on the harmless case"
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

# ⛔ THIS ASSERTION USED TO RUN 24 LINES *BEFORE* --all AND WAS THEREFORE
# VACUOUS — it could not fail. Proven by pointing the gate at a SUT whose --all
# rm -rf's every worktree slot: this stayed green while every file it names was
# deleted, and it passed unchanged in teeth mode. It is the ONLY assertion
# covering the upward-walk class on the deletion path, which is the class the
# rev-parse containment fix was written for. Order is the whole assertion.
if [ -f "$T/live/.claude/worktrees/g_plaindir/keep.txt" ] \
   && [ -f "$T/live/.claude/worktrees/h_nogit/keep.txt" ]; then
  pass "--all left both upward-walk shapes on disk (asserted AFTER --all ran)"
else
  fail "--all DELETED an upward-walk shape it never actually inspected"
fi

if [ -f "$T/live/.claude/worktrees/ignoredwt/.env" ]; then
  pass "--all did not delete the worktree holding only ignored files"
else
  fail "--all DELETED an ignored-only worktree (.env is untracked by definition — unrecoverable)"
fi

# Refusal WITHOUT --force must be asserted before the --force case below, or
# "--force removed it" is consistent with a script that removes it either way.
ig_bare="$( cd "$T/live" && bash "$SUT" ignoredwt 2>&1 )" || true
if [ -f "$T/live/.claude/worktrees/ignoredwt/.env" ]; then
  pass "remove_one refuses an ignored-only worktree without --force"
else
  fail "remove_one removed an ignored-only worktree with no --force"
fi
case "$ig_bare" in
  *"ignored files"*) pass "remove_one names what the ignored-only tree holds" ;;
  *) fail "remove_one refused without naming the ignored content: $ig_bare" ;;
esac

# ⛔ THE OVER-BLOCKING HALF, and it is not optional. Every assertion above is
# satisfied by a script that refuses to remove ANYTHING ignored under any
# circumstances — which would strand every node_modules tree forever and quietly
# convert a safety fix into a broken tool. IGNORED must take --force, unlike
# UNKNOWN which must refuse it. Asserting only the refusal tests half a contract.
ig_forced="$( cd "$T/live" && bash "$SUT" ignoredwt --force 2>&1 )" || true
if [ ! -d "$T/live/.claude/worktrees/ignoredwt" ]; then
  pass "remove_one --force DOES remove an ignored-only worktree (IGNORED is not UNKNOWN)"
else
  fail "remove_one --force refused an ignored-only worktree — over-blocking: $ig_forced"
fi

if [ -f "$T/live/.claude/worktrees/det_work/committed.txt" ]; then
  pass "--all did not delete the detached worktree holding an unreachable commit"
else
  fail "--all DELETED a detached worktree whose commit no ref contains (unreachable, reflog gone)"
fi
if [ ! -d "$T/live/.claude/worktrees/det_safe" ]; then
  pass "--all DID delete the harmless detached worktree (DETACHED is not over-broad)"
else
  fail "--all refused a detached worktree that was reachable — over-blocking"
fi
det_bare="$( cd "$T/live" && bash "$SUT" det_work 2>&1 )" || true
case "$det_bare" in
  *"branch <name>"*) pass "remove_one prints a rescue command for the detached commit" ;;
  *) fail "remove_one refused a DETACHED tree without printing the rescue: $det_bare" ;;
esac
det_forced="$( cd "$T/live" && bash "$SUT" det_work --force 2>&1 )" || true
if [ ! -d "$T/live/.claude/worktrees/det_work" ]; then
  pass "remove_one --force DOES remove a DETACHED worktree (DIRTY contract, not UNKNOWN)"
else
  fail "remove_one --force refused a DETACHED worktree — over-blocking: $det_forced"
fi

# ⛔ Bound to the SLUG, not a bare grep for the word. `grep -q UNKNOWN` over
# combined stdout+stderr passes if the string appears anywhere at all.
if grep -q 'skipped brokenwt (UNKNOWN' "$T/all.out" 2>/dev/null; then
  pass "--all names brokenwt as UNKNOWN, so an operator can tell inspection failed"
else
  fail "--all did not report brokenwt as UNKNOWN"
fi

# The remedy must not be a runnable --force COMMAND (it either fails on this
# shape or destroys unreviewed work, depending on the invisible cause).
#
# ⛔ Keyed on an invocation-shaped line, not the bare token. The first version
# grepped for `--force` anywhere, which flagged the message's own PROHIBITION
# ("Do NOT use --force") as a recommendation — a grep satisfied by the thing
# being described, which is the same class this gate exists to catch.
if grep -qE 'worktree-clean(\.sh)?[^|&;]*--force' "$T/all.out" 2>/dev/null; then
  fail "--all's UNKNOWN advice still prints a runnable --force command"
else
  pass "--all's UNKNOWN advice prints no runnable --force command"
fi
# ...and it must still WARN about --force, or the prohibition was simply dropped.
if grep -qi 'not use --force\|NOT reach for --force' "$T/all.out" 2>/dev/null; then
  pass "--all's UNKNOWN advice explicitly warns against --force"
else
  fail "--all's UNKNOWN advice no longer warns against --force"
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

  # ⛔ CROSS THE TWO FIXES. The assertion above only exercises the pin on the
  # `out` probe; the IGNORED probe is a SEPARATE call with its OWN pins, and the
  # same config silences it too — `status.showUntrackedFiles=no` suppresses
  # `--ignored` output as well. Measured: strip `--untracked-files=normal` from
  # the ignored probe alone and an ignored-only tree flips IGNORED -> clean ->
  # removed, with every other assertion in this gate still green. Two fixes
  # reconciled independently, and the test for one did not cover the other.
  if [ -f "$root/.claude/worktrees/ignoredwt/.env" ]; then
    pass "$label: ignored-only worktree survived --all (the ignored probe is pinned too)"
  else
    fail "$label: --all DELETED an ignored-only worktree (config steered the IGNORED probe)"
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
    # Survival cannot be used on THIS path: the UNFORCED `git worktree remove`
    # that --all issues refuses the corrupt shape (rc=128 measured), so brokenwt
    # survives whatever the script decides. (The --force path is different —
    # git DOES delete the corrupt shape there, which is why the
    # `remove_one --force` assertion above can and does use survival as its
    # oracle. Do not generalise "git refuses it" across both paths.)
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
# ⛔ Matches the UNKNOWN FAMILY, not the bare literal. This file classifies
# UNKNOWN-rc / UNKNOWN-scope / UNKNOWN-perm — a `printf 'UNKNOWN'` grep finds
# none of them and reported "the stand-in lost the UNKNOWN fix" about a
# stand-in that had kept it perfectly. Ported straight from main, where the
# single-state literal was correct; the anchor had to move with the code.
elif ! grep -q "printf 'UNKNOWN" "$CMUT"; then
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

# --- narrow teeth for the ignored-only state ---------------------------------
# Same discipline as the config pins: strip ONLY the ignored probe, keep every
# other guard, and the ignored-only tree must then be destroyed. Without this,
# the IGNORED assertions could be passing on the strength of the earlier fixes.
IMUT="$T/ig-mutant.sh"
awk '
  /^  local ig igrc=0$/ { skip = 1; print "  local ig igrc=0"; next }
  skip && /^  if \[ -n "\$ig" \]/ { skip = 0; next }
  skip { next }
  { print }
' "$SUT" > "$IMUT"
if grep -q 'ignored=traditional' "$IMUT" && grep -q 'printf .IGNORED' "$IMUT"; then
  # The classifier still has both halves, so nothing was removed. `ignored_sample`
  # also contains `ignored=traditional`, so this checks the CLASSIFIER's own two
  # markers together rather than a bare filename grep that the helper satisfies.
  if awk '/^worktree_state\(\)/,/^\}/' "$IMUT" | grep -q 'ignored=traditional'; then
    fail "teeth: ignored-probe stand-in did not apply — cannot prove the IGNORED assertions have teeth"
  else
    IMUT_OK=1
  fi
else
  IMUT_OK=1
fi
if [ "${IMUT_OK:-0}" = "1" ]; then
  if build_fixture "$T/igmut"; then
    ( cd "$T/igmut" && bash "$IMUT" --all >/dev/null 2>&1 )
    if [ -f "$T/igmut/.claude/worktrees/ignoredwt/.env" ]; then
      fail "teeth: the ignored-only tree survived even WITHOUT the ignored probe — the IGNORED assertions are vacuous"
    else
      pass "teeth: strip only the ignored probe and the .env worktree IS destroyed (IGNORED assertions are real)"
    fi
  else
    fail "teeth: ignored-probe stand-in fixture failed to build"
  fi
fi

# --- narrow teeth for the DETACHED state -------------------------------------
# Strip ONLY the reachability check, keep every other guard, and the commit-
# bearing worktree must then be destroyed. Same discipline as the config-pin and
# ignored-probe stand-ins: proves these assertions measure THIS state rather
# than riding on the five that came before it.
DMUT="$T/det-mutant.sh"
awk '
  /^  if ! rcgit -C "\$1" symbolic-ref -q HEAD/ { skip = 1; next }
  skip && /^  fi$/ { skip = 0; next }
  skip { next }
  { print }
' "$SUT" > "$DMUT"
if awk '/^worktree_state\(\)/,/^\}/' "$DMUT" | grep -q 'symbolic-ref'; then
  fail "teeth: detached stand-in did not apply — cannot prove the DETACHED assertions have teeth"
elif build_fixture "$T/detmut"; then
  ( cd "$T/detmut" && bash "$DMUT" --all >/dev/null 2>&1 )
  if [ -f "$T/detmut/.claude/worktrees/det_work/committed.txt" ]; then
    fail "teeth: the detached worktree survived even WITHOUT the reachability check — the DETACHED assertions are vacuous"
  else
    pass "teeth: strip only the reachability check and the unreachable commit IS destroyed (DETACHED assertions are real)"
  fi
else
  fail "teeth: detached stand-in fixture failed to build"
fi

printf '\n'
if [ "$FAILED" -eq 0 ]; then
  printf 'check-worktree-state (Gate 216): ALL PASS\n'
  exit 0
fi
printf 'check-worktree-state (Gate 216): %d FAILED\n' "$FAILED"
exit 1
