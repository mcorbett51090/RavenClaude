#!/usr/bin/env bash
# Gate 229 — a worktree belongs to one session, with a stale fallback.
#
# TWO DEFECTS, ONE GATE.
#
# (1) FOREIGN-TREE ownership by path prefix.
#     control: with cwd = a linked worktree and the target a file INSIDE that
#     same worktree, the guard answered "FOREIGN — ... not <that worktree>",
#     naming the very tree the file lives in. Positive control on the same
#     harness: a genuine sibling target -> FOREIGN, a /tmp target -> silent, so
#     the own-tree answer was a real reading and not a dead probe. Mechanism
#     confirmed separately: `case "$WT/" in "$PRIMARY"/*)` matches, because this
#     repo's convention puts worktrees at `<primary>/.claude/worktrees/<name>`
#     ("worktrees UNDER the repo, never /tmp") — so the primary is both a
#     sibling AND an ancestor of every linked worktree, and `_wg_is_foreign`
#     returned on the FIRST prefix hit. (2026-08-18)
#
#     ⛔ A suppressed message is not a negative result. The guard throttles a
#     repeated nudge per (path_key, session, kind); reading that silence as "the
#     predicate stopped firing" produced one false "regression" report during
#     this work. Every probe below therefore drives a FRESH guard home.
#
#     That is why `worktree_bound` sat at `warn` on main with a comment saying
#     the deadlock left "no legal place to edit" — the guard had been switched
#     off rather than fixed, so the isolation it advertised did not exist.
#     Ownership is now the LONGEST matching worktree prefix.
#
# (2) CONTENTION only ever NUDGED — it told the latecomer someone else was in the
#     tree and let both proceed. The lease is the enforcement, and the stale
#     fallback is what makes enforcement safe: a lock with no expiry strands the
#     tree when a session dies, and a lock people cannot get out of is a lock
#     they route around.
#
# ⛔ THE TEETH THAT MATTER MOST ARE THE NEGATIVE ONES. A guard that denies
# everything passes any "did it deny?" test. Every deny case here is paired with
# one that must NOT deny, and the takeover case asserts the holder's work
# SURVIVED — a takeover that loses work is worse than the deadlock it replaces.
#
# bash 3.2-safe. No GNU-only tools.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
GUARD="$(cd "$HERE/.." && pwd)/worktree-guard.sh"

MUST_FAIL=0
[ "${1:-}" = "--must-fail-prefix" ] && MUST_FAIL=1

pass=0; fail=0
ok_() { pass=$((pass + 1)); printf '  ok   %s\n' "$1"; }
no_() { fail=$((fail + 1)); printf '  FAIL %s\n' "$1"; }

TMP="$(mktemp -d 2>/dev/null || mktemp -d -t gate229)"
cleanup() { [ -n "${TMP:-}" ] && [ -d "$TMP" ] && rm -rf "$TMP"; }
trap cleanup EXIT

[ -f "$GUARD" ] || { echo "Gate 229: cannot find $GUARD" >&2; exit 1; }

SUT="$GUARD"
if [ "$MUST_FAIL" -eq 1 ]; then
  # Rebuild defect (1): ownership by the FIRST containing worktree, not the
  # deepest. Under the nested layout that is always the primary.
  SUT="$TMP/mutant-guard.sh"
  python3 - "$GUARD" "$SUT" <<'MUTATE' || {
import sys
src, dst = sys.argv[1], sys.argv[2]
t = open(src, encoding="utf-8").read()
old = "done | sort | tail -1\n}"
if old not in t:
    sys.stderr.write("mutant anchor not found\n"); raise SystemExit(1)
t = t.replace(old, "done | head -1\n}", 1)
open(dst, "w", encoding="utf-8").write(t)
MUTATE
    echo "Gate 229 must-fail: could not rebuild the defect (anchor moved)" >&2
    exit 1
  }
  grep -q 'done | head -1' "$SUT" || { echo "Gate 229 must-fail: mutation did not apply" >&2; exit 1; }
fi

git_q() { git "$@" >/dev/null 2>&1; }

# ── fixture: a primary checkout with a linked worktree UNDER it (the layout
# that triggers the bug; a flat layout would not reproduce it) ────────────────
PRIMARY="$TMP/repo"
mkdir -p "$PRIMARY"
git_q init -q "$PRIMARY"
git_q -C "$PRIMARY" config user.email t@example.com
git_q -C "$PRIMARY" config user.name t
mkdir -p "$PRIMARY/.ravenclaude"
printf 'seed\n' > "$PRIMARY/file.txt"
git_q -C "$PRIMARY" add -A
git_q -C "$PRIMARY" commit -qm one
git_q -C "$PRIMARY" branch -M main
WT="$PRIMARY/.claude/worktrees/wt1"
git_q -C "$PRIMARY" worktree add -q -b feat/wt1 "$WT"
mkdir -p "$WT/.ravenclaude"

echo "Gate 229 — worktree ownership + session lease"

# ⛔ POSITIVE CONTROL on the fixture itself: the defect only exists when the
# primary is a path-prefix of the worktree. If the fixture is not nested, every
# assertion below is about nothing.
case "$WT/" in "$PRIMARY"/*) ok_ "control: fixture reproduces the nested layout" ;;
  *) no_ "control: fixture is NOT nested — the defect cannot appear here" ;; esac

posture() { printf '%s\n' "$1" > "$2/.ravenclaude/comfort-posture.yaml"; }

# Each probe gets a FRESH guard home so a throttled nudge can never be misread
# as a predicate that stopped firing.
_n=0
run() { # $1 target  $2 cwd  $3 session
  _n=$((_n + 1))
  printf '{"tool_name":"Edit","tool_input":{"file_path":"%s"},"cwd":"%s","session_id":"%s"}' "$1" "$2" "$3" \
    | env RC_WORKTREE_GUARD_HOME="$TMP/gh$_n" CLAUDE_SESSION_ID="$3" bash "$SUT" check 2>&1
  printf 'EXIT=%s\n' "$?"
}
# The lease needs state to PERSIST across sessions, so those probes share one home.
runL() { # $1 target  $2 cwd  $3 session
  printf '{"tool_name":"Edit","tool_input":{"file_path":"%s"},"cwd":"%s","session_id":"%s"}' "$1" "$2" "$3" \
    | env RC_WORKTREE_GUARD_HOME="$GHL" CLAUDE_SESSION_ID="$3" bash "$SUT" check 2>&1
  printf 'EXIT=%s\n' "$?"
}
exit_of() { printf '%s\n' "$1" | sed -n 's/^EXIT=//p' | tail -1; }

# ── part 1: FOREIGN-TREE ownership ──────────────────────────────────────────
posture "worktree_guard: off
worktree_bound: block
worktree_lease: off" "$WT"
posture "worktree_guard: off
worktree_bound: block
worktree_lease: off" "$PRIMARY"

out="$(run "$WT/file.txt" "$WT" s1)"
[ "$(exit_of "$out")" = "0" ] && ok_ "own-tree write is allowed (the deadlock is gone)" \
                              || no_ "own-tree write DENIED — the prefix bug is back"

out="$(run "$WT/file.txt" "$PRIMARY" s1)"
[ "$(exit_of "$out")" = "2" ] && ok_ "primary -> linked worktree is still denied (teeth)" \
                              || no_ "cross-tree write ALLOWED — the guard lost its teeth"

out="$(run "$PRIMARY/file.txt" "$WT" s1)"
[ "$(exit_of "$out")" = "2" ] && ok_ "linked worktree -> primary is still denied (teeth)" \
                              || no_ "cross-tree write ALLOWED — the guard lost its teeth"

out="$(run "$TMP/outside.txt" "$WT" s1)"
[ "$(exit_of "$out")" = "0" ] && ok_ "a path outside every worktree is not a sibling problem" \
                              || no_ "outside-the-repo write denied (over-reach)"

# ── part 2: the lease ───────────────────────────────────────────────────────
GHL="$TMP/ghlease"
posture "worktree_guard: off
worktree_bound: off
worktree_lease: on
worktree_lease_idle_minutes: 20" "$WT"

out="$(runL "$WT/file.txt" "$WT" sA)"
[ "$(exit_of "$out")" = "0" ] && ok_ "first session claims the lease and proceeds" \
                              || no_ "the claiming session was denied its own tree"

out="$(runL "$WT/file.txt" "$WT" sA)"
[ "$(exit_of "$out")" = "0" ] && ok_ "the holder is never blocked by its own lease" \
                              || no_ "the holder blocked itself"

out="$(runL "$WT/file.txt" "$WT" sB)"
[ "$(exit_of "$out")" = "2" ] && ok_ "a SECOND session is denied while the lease is live" \
                              || no_ "second session got in — there is no exclusion"
case "$out" in *sA*) ok_ "the denial names the holder" ;;
  *) no_ "the denial does not say who holds it" ;; esac

# ── part 3: stale takeover, and the work survives ───────────────────────────
printf 'work-in-progress\n' > "$WT/holder-work.txt"          # untracked
printf 'edited\n' >> "$WT/file.txt"                          # tracked
touch -t 200001010000 "$GHL/leases/"*/lease.json 2>/dev/null

out="$(runL "$WT/file.txt" "$WT" sB)"
[ "$(exit_of "$out")" = "0" ] && ok_ "a STALE lease is taken over, not stranded" \
                              || no_ "stale lease still blocked — the fallback does not work"
case "$out" in *"took over"*) ok_ "the takeover is announced" ;;
  *) no_ "takeover happened silently" ;; esac

# ⛔ THE ASSERTION THIS GATE EXISTS FOR.
committed="$(git -C "$WT" log -1 --pretty=%s 2>/dev/null || printf '')"
case "$committed" in "wip(worktree-lease)"*) ok_ "the holder's work was auto-committed" ;;
  *) no_ "no auto-checkin commit — the takeover may have lost work (HEAD: $committed)" ;; esac
if git -C "$WT" show --stat HEAD 2>/dev/null | grep -q 'holder-work.txt'; then
  ok_ "untracked work was included (owner ruling: tracked AND untracked)"
else
  no_ "untracked work was NOT captured"
fi
[ -z "$(git -C "$WT" status --porcelain 2>/dev/null)" ] \
  && ok_ "the tree is clean for the new holder" \
  || no_ "the new session inherited a dirty tree"

# ── part 4: the anchor branch is never auto-committed ───────────────────────
GHL="$TMP/ghanchor"
posture "worktree_guard: off
worktree_bound: off
worktree_lease: on
worktree_lease_idle_minutes: 20" "$PRIMARY"
printf 'dirty\n' >> "$PRIMARY/file.txt"
out="$(runL "$PRIMARY/file.txt" "$PRIMARY" sC)"      # sC claims
touch -t 200001010000 "$GHL/leases/"*/lease.json 2>/dev/null
out="$(runL "$PRIMARY/file.txt" "$PRIMARY" sD)"
[ "$(exit_of "$out")" = "2" ] && ok_ "a stale lease on the ANCHOR refuses to auto-commit" \
                              || no_ "auto-committed on main — the shared anchor was rewritten"
anchor_head="$(git -C "$PRIMARY" log -1 --pretty=%s 2>/dev/null || printf '')"
case "$anchor_head" in "wip(worktree-lease)"*) no_ "main carries an auto-checkin commit" ;;
  *) ok_ "main's history is untouched" ;; esac

# ── part 5: the off switch, and independence from the other two knobs ───────
GHL="$TMP/ghoff"
posture "worktree_guard: off
worktree_bound: off
worktree_lease: off" "$WT"
out="$(runL "$WT/file.txt" "$WT" sZ)"
[ "$(exit_of "$out")" = "0" ] && ok_ "worktree_lease: off disables enforcement" \
                              || no_ "lease still enforcing when switched off"

# ⛔ guard:off + bound:off used to short-circuit BEFORE the lease clause ran, so
# silencing the two nudges silently removed cross-session exclusion too.
GHL="$TMP/ghindep"
posture "worktree_guard: off
worktree_bound: off
worktree_lease: on
worktree_lease_idle_minutes: 20" "$WT"
out="$(runL "$WT/file.txt" "$WT" sE)"      # sE claims
out="$(runL "$WT/file.txt" "$WT" sF)"
[ "$(exit_of "$out")" = "2" ] \
  && ok_ "the lease survives guard:off + bound:off (independent knob)" \
  || no_ "the other two knobs silently disabled the lease"

echo "  pass=$pass fail=$fail"

if [ "$MUST_FAIL" -eq 1 ]; then
  if [ "$fail" -gt 0 ]; then
    echo "Gate 229 must-fail half: mutant CAUGHT ($fail red) — teeth confirmed"; exit 0
  fi
  echo "Gate 229 must-fail half: MUTANT NOT CAUGHT — the ownership assertions are inert" >&2
  exit 1
fi
[ "$fail" -gt 0 ] && { echo "Gate 229 FAILED" >&2; exit 1; }
echo "Gate 229 PASSED"
exit 0
