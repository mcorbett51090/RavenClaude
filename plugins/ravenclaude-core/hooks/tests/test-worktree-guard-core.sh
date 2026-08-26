#!/usr/bin/env bash
# test-worktree-guard-core.sh — acceptance tests for the worktree-hygiene guard
# CORE detection engine (hooks/worktree-guard.sh), per the FORGE plan §5.
#
# Self-contained: every fixture is a throwaway `git init` under mktemp, and the
# registry is redirected to a scratch RC_WORKTREE_GUARD_HOME — the real
# $HOME/.ravenclaude registry is NEVER touched.
#
# Subtests:
#   T1  single-worktree fixture -> status is_anchor:false ALWAYS (on-main + off-main).
#   T2  two-worktree (primary on main + sibling) -> primary anchor only on main,
#       sibling never.
#   T3  two live records, same PATH_KEY -> the LATECOMER contends (warn nudge),
#       the incumbent stays silent.
#   T4  stale records (dead pid / mtime>TTL) -> NOT counted live, NOT contention,
#       and REAPED by the next `register` GC.
#   T5  block mode: a MUTATING op -> exit 2 DENY; a read -> exit 0; +ACK -> exit 0.
#   T6  submodule-shaped fixture (nested independent toplevel) -> independent bucket
#       (distinct PATH_KEY from the superproject).
#   T7  `worktree_guard: off` -> register writes NOTHING (no registry dir created).
#   T8  two-worktree; Write absolute path under sibling B:
#       worktree_bound=block -> exit 2; warn -> 0 + FOREIGN; off -> 0, no stderr.
#   T9  two-worktree; Write under A (this tree) -> exit 0.
#   T10 Write to /tmp/rc-wt-probe -> exit 0 (not a listed worktree).
#   T11 Bash `git -C <B> commit` from cwd A -> exit 2 when bound=block.
#   T12 RC_WORKTREE_BOUND_ACK=1 + Write to B -> exit 0.
#   T13 worktree_guard: off + worktree_bound: block + Write to B -> still exit 2.
#   T14 lone checkout (no other worktrees) + Write under tree -> exit 0.
#   T15 GIT_WORK_TREE=<B> git add -A from cwd A -> exit 2.
#   T16 git status (no -C) from A -> exit 0.
#   T18 stdin read is BOUNDED: (a) the hook exits under a held-open pipe,
#       (b) must-fail — the bare `cat` restored still hangs there, (c) a
#       multi-line payload still denies (the bound must not truncate), (d) a
#       3s-late writer clears the shipped deadline while a 1s one disarms
#       the guard — an empty payload fails OPEN, so the margin is the fix.
#   MF  must-fail half — strip the latecomer-only guard in _wg_contention and assert
#       the incumbent now ALSO fires, proving T3's incumbent-silence has teeth.
#
# Run directly:  bash plugins/ravenclaude-core/hooks/tests/test-worktree-guard-core.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$(cd "$SCRIPT_DIR/.." && pwd)/worktree-guard.sh"

PASS=0
FAIL=0
pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

# jq is required for the fixtures (they parse status JSON + seed records).
if ! command -v jq >/dev/null 2>&1; then
  echo "SKIP: jq not available — the worktree-guard fixtures need it to parse status JSON"
  exit 0
fi

# ── fixture helpers ───────────────────────────────────────────────────────────

# mk_repo <dir> [posture-mode] — a git repo on `main` with one commit + a posture.
mk_repo() {
  local d="$1" mode="${2:-}"
  git init -q "$d"
  git -C "$d" config user.email t@example.com
  git -C "$d" config user.name test
  git -C "$d" commit --allow-empty -q -m init
  git -C "$d" branch -M main
  mkdir -p "$d/.ravenclaude"
  [ -n "$mode" ] && printf 'worktree_guard: %s\n' "$mode" > "$d/.ravenclaude/comfort-posture.yaml"
}

# path_key <dir> — the sha256(realpath) key the hook computes for a working tree.
path_key() {
  local rt; rt="$(cd "$1" 2>/dev/null && pwd -P)"
  if command -v sha256sum >/dev/null 2>&1; then
    printf '%s' "$rt" | sha256sum | cut -d' ' -f1
  else
    printf '%s' "$rt" | shasum -a 256 | cut -d' ' -f1
  fi
}

# seed_record <bucket-dir> <sid> <pid> <started_at> — write a registry record file.
seed_record() {
  mkdir -p "$1"
  printf '{"session_id":"%s","pid":%s,"ppid":0,"host":"h","branch":"main","started_at":%s}\n' \
    "$2" "$3" "$4" > "$1/$2.json"
}

# mk_payload <cwd> <sid> <tool_name> <tool_input-json>
mk_payload() {
  jq -cn --arg cwd "$1" --arg sid "$2" --arg tn "$3" --argjson ti "$4" \
    '{cwd:$cwd, session_id:$sid, tool_name:$tn, tool_input:$ti}'
}

# status_field <repo> <jq-filter>
status_field() { ( cd "$1" && bash "$HOOK" status --json ) | jq -r "$2"; }

echo
echo "── T1: single-worktree fixture -> is_anchor false always ─────────────────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R"
A_MAIN="$(status_field "$R" '.is_anchor')"
git -C "$R" checkout -q -b feature-x
A_OFF="$(status_field "$R" '.is_anchor')"
if [ "$A_MAIN" = "false" ] && [ "$A_OFF" = "false" ]; then
  pass "T1: single checkout is never anchor (on main=$A_MAIN, off main=$A_OFF)"
else
  fail "T1: single checkout reported anchor (on main=$A_MAIN, off main=$A_OFF) — must be false"
fi
rm -rf "$SB"

echo
echo "── T2: two-worktree — primary anchor only on main; sibling never ─────────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R"
git -C "$R" worktree add -q -b sib "$SB/sibling"
P_MAIN="$(status_field "$R" '.is_anchor')"
S_ANY="$(status_field "$SB/sibling" '.is_anchor')"
git -C "$R" checkout -q -b notmain
P_OFF="$(status_field "$R" '.is_anchor')"
if [ "$P_MAIN" = "true" ]; then pass "T2: primary on main with worktrees present -> anchor"; else fail "T2: primary on main was not anchor ($P_MAIN)"; fi
if [ "$P_OFF" = "false" ]; then pass "T2: primary off the anchor branch -> not anchor"; else fail "T2: primary off main still anchor ($P_OFF)"; fi
if [ "$S_ANY" = "false" ]; then pass "T2: sibling worktree is never anchor"; else fail "T2: sibling reported anchor ($S_ANY)"; fi
rm -rf "$SB"

echo
echo "── T3: two live records -> latecomer contends, incumbent silent ──────────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" warn
PK="$(path_key "$R")"; BUCKET="$SB/guard/sessions/$PK"
sleep 300 & INC_PID=$!; disown 2>/dev/null || true
NOW="$(date +%s)"
seed_record "$BUCKET" incumbent "$INC_PID" "$((NOW - 100))"
# Latecomer session: its check writes a self-record with started_at=now (> incumbent).
LATE_ERR="$(mk_payload "$R" latecomer Bash '{"command":"git status"}' | bash "$HOOK" check 2>&1 1>/dev/null)"
LATE_RC=$?
# Incumbent session: oldest started_at -> never a latecomer -> silent.
INC_ERR="$(mk_payload "$R" incumbent Bash '{"command":"git status"}' | bash "$HOOK" check 2>&1 1>/dev/null)"
INC_RC=$?
kill "$INC_PID" 2>/dev/null
if printf '%s' "$LATE_ERR" | grep -q 'another live' && [ "$LATE_RC" -eq 0 ]; then
  pass "T3: the latecomer got a contention nudge (exit 0, warn)"
else
  fail "T3: the latecomer did NOT get nudged (rc=$LATE_RC, err='$LATE_ERR')"
fi
if [ -z "$INC_ERR" ] && [ "$INC_RC" -eq 0 ]; then
  pass "T3: the incumbent stayed silent (no nudge)"
else
  fail "T3: the incumbent was NOT silent (rc=$INC_RC, err='$INC_ERR')"
fi
rm -rf "$SB"

echo
echo "── T4: stale records not live / not contention / reaped by register ──────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" warn
PK="$(path_key "$R")"; BUCKET="$SB/guard/sessions/$PK"
# (a) dead pid (very high, not running) + fresh mtime.
seed_record "$BUCKET" deadpid 999999 "$(date +%s)"
# (b) live pid ($$ — this shell) but mtime far in the past -> stale by TTL.
seed_record "$BUCKET" oldmtime "$$" "$(date +%s)"
touch -t 200001010000 "$BUCKET/oldmtime.json"
LIVE="$(status_field "$R" '.live_sessions')"
CONT="$(status_field "$R" '.contention')"
if [ "$LIVE" = "0" ] && [ "$CONT" = "false" ]; then
  pass "T4: stale records are not counted live and do not raise contention"
else
  fail "T4: stale records counted live=$LIVE contention=$CONT (expected 0/false)"
fi
# A fresh session's check must NOT see contention against only-stale records.
NEW_ERR="$(mk_payload "$R" fresh Bash '{"command":"git status"}' | bash "$HOOK" check 2>&1 1>/dev/null)"
if [ -z "$NEW_ERR" ]; then
  pass "T4: a new session sees no contention when the only other records are stale"
else
  fail "T4: a new session was nudged against stale-only records (err='$NEW_ERR')"
fi
# register GC reaps the stale files.
mk_payload "$R" reaper Bash '{"command":"ls"}' | bash "$HOOK" register >/dev/null 2>&1
if [ ! -f "$BUCKET/deadpid.json" ] && [ ! -f "$BUCKET/oldmtime.json" ]; then
  pass "T4: register GC reaped the stale (dead-pid + old-mtime) records"
else
  fail "T4: register GC did NOT reap the stale records ($(ls "$BUCKET" 2>/dev/null | tr '\n' ' '))"
fi
rm -rf "$SB"

echo
echo "── T5: block mode — mutating denies (exit 2), read allows, ACK escapes ───"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" block
# ⛔ Lease OFF so this block tests the CONTENTION clause in isolation, which is
# what T5's name claims. The lease clause is evaluated FIRST and denies on the
# same fixture (another live session in this tree), so with it on, the 4th call
# below never reaches the contention code and the ACK assertion measured the
# wrong clause. That is not hypothetical: T5's ACK case had been RED since the
# lease landed, and nobody saw it because this suite is invoked by no workflow.
# The lease/contention layering is pinned separately in T5b — deleting this line
# does not silently weaken T5, it makes T5 test something else.
printf 'worktree_lease: off\n' >> "$R/.ravenclaude/comfort-posture.yaml"
PK="$(path_key "$R")"; BUCKET="$SB/guard/sessions/$PK"
sleep 300 & INC_PID=$!; disown 2>/dev/null || true
NOW="$(date +%s)"
seed_record "$BUCKET" incumbent "$INC_PID" "$((NOW - 100))"
# latecomer + mutating git commit -> DENY (exit 2)
mk_payload "$R" late-mut Bash '{"command":"git commit -m x"}' | bash "$HOOK" check >/dev/null 2>&1
[ "$?" -eq 2 ] && pass "T5: block + mutating (git commit) -> exit 2 DENY" || fail "T5: block + mutating did NOT deny"
# latecomer + read git status -> allow (exit 0)
mk_payload "$R" late-read Bash '{"command":"git status"}' | bash "$HOOK" check >/dev/null 2>&1
[ "$?" -eq 0 ] && pass "T5: block + read (git status) -> exit 0 allow" || fail "T5: block + read did NOT allow"
# latecomer + Write under the tree -> DENY (exit 2)
mk_payload "$R" late-write Write "$(jq -cn --arg fp "$R/newfile.txt" '{file_path:$fp, content:"x"}')" | bash "$HOOK" check >/dev/null 2>&1
[ "$?" -eq 2 ] && pass "T5: block + Write under the tree -> exit 2 DENY" || fail "T5: block + Write under the tree did NOT deny"
# latecomer + mutating + ACK -> allow (exit 0)
mk_payload "$R" late-ack Bash '{"command":"git commit -m x"}' | RC_WORKTREE_GUARD_ACK=1 bash "$HOOK" check >/dev/null 2>&1
[ "$?" -eq 0 ] && pass "T5: block + mutating + RC_WORKTREE_GUARD_ACK=1 -> exit 0 (escape)" || fail "T5: ACK did NOT escape the block"
kill "$INC_PID" 2>/dev/null
rm -rf "$SB"

echo
echo "── T5b: the LEASE clause is evaluated before contention, and shadows GUARD_ACK ──"
# ⛔ PINS THE LAYERING, and it is currently a SHARP EDGE rather than a clean one.
# On the same two-writers fixture the lease denies first, so RC_WORKTREE_GUARD_ACK
# — documented in hooks.json, dashboard-schema.json and the contention deny's own
# text as the override for exactly this situation — does NOT get you through.
# The lease's own message names a DIFFERENT, working escape (worktree_lease: off),
# so the user is not stranded; they are told about a hatch that does not apply.
# This test asserts the behaviour AS IT IS so a future change to it is deliberate
# and visible, NOT that the behaviour is correct. Whether GUARD_ACK should also
# release the lease is an owner call: it would add a bypass to a mutual-exclusion
# control, which is not a call a test should make by encoding it.
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" block
printf 'worktree_lease: on\nworktree_lease_idle_minutes: 20\n' >> "$R/.ravenclaude/comfort-posture.yaml"
# The lease needs a live holder, which a real `check` call establishes.
mk_payload "$R" holder Bash '{"command":"git commit -m x"}' | bash "$HOOK" check >/dev/null 2>&1
out5b="$(mk_payload "$R" latecomer Bash '{"command":"git commit -m x"}' | RC_WORKTREE_GUARD_ACK=1 bash "$HOOK" check 2>&1)"
rc5b=$?
[ "$rc5b" -eq 2 ] \
  && pass "T5b: a held lease denies (exit 2) even with RC_WORKTREE_GUARD_ACK=1" \
  || fail "T5b: expected the lease to deny at exit 2, got $rc5b"
case "$out5b" in
  *"holds a live lease"*) pass "T5b: the denial is the LEASE clause, naming its own escape" ;;
  *) fail "T5b: denied, but not by the lease clause — layering changed: $out5b" ;;
esac
rm -rf "$SB"

echo
echo "── T6: submodule-shaped nested repo -> independent bucket ────────────────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/super"; mk_repo "$R"
# A nested independent git repo stands in for a submodule's own toplevel: both
# resolve their OWN `git rev-parse --show-toplevel`, so both get a distinct
# PATH_KEY -> distinct registry bucket (never contend with the superproject).
NESTED="$R/vendor/mod"; mk_repo "$NESTED"
SUPER_PK="$(status_field "$R" '.path_key')"
NESTED_PK="$(status_field "$NESTED" '.path_key')"
NESTED_TOP="$(status_field "$NESTED" '.toplevel')"
if [ -n "$SUPER_PK" ] && [ -n "$NESTED_PK" ] && [ "$SUPER_PK" != "$NESTED_PK" ] && [ "$NESTED_TOP" = "$(cd "$NESTED" && pwd -P)" ]; then
  pass "T6: the nested repo resolves its own toplevel -> a distinct bucket"
else
  fail "T6: nested bucket not independent (super=$SUPER_PK nested=$NESTED_PK top=$NESTED_TOP)"
fi
rm -rf "$SB"

echo
echo "── T7: worktree_guard: off -> register writes nothing ────────────────────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" off
mk_payload "$R" s Bash '{"command":"ls"}' | bash "$HOOK" register >/dev/null 2>&1
if [ ! -e "$SB/guard" ]; then
  pass "T7: off mode short-circuited before any registry write"
else
  fail "T7: off mode created registry state: $(find "$SB/guard" -type f 2>/dev/null | tr '\n' ' ')"
fi
rm -rf "$SB"

echo
echo "── T8: FOREIGN-TREE Write to sibling — block/warn/off ────────────────────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" warn
git -C "$R" worktree add -q -b sibt8 "$SB/sibling"
printf 'worktree_guard: warn\nworktree_bound: block\n' > "$R/.ravenclaude/comfort-posture.yaml"
T8_ERR="$(mk_payload "$R" s Write "$(jq -cn --arg fp "$SB/sibling/x.txt" '{file_path:$fp, content:"x"}')" | bash "$HOOK" check 2>&1 1>/dev/null)"
T8_RC=$?
if [ "$T8_RC" -eq 2 ] && printf '%s' "$T8_ERR" | grep -q 'FOREIGN'; then
  pass "T8: bound=block + Write to sibling -> exit 2 DENY"
else
  fail "T8: block expected exit 2 + FOREIGN (rc=$T8_RC err='$T8_ERR')"
fi
printf 'worktree_guard: warn\nworktree_bound: warn\n' > "$R/.ravenclaude/comfort-posture.yaml"
T8W_ERR="$(mk_payload "$R" s Write "$(jq -cn --arg fp "$SB/sibling/x.txt" '{file_path:$fp, content:"x"}')" | bash "$HOOK" check 2>&1 1>/dev/null)"
T8W_RC=$?
if [ "$T8W_RC" -eq 0 ] && printf '%s' "$T8W_ERR" | grep -qi 'FOREIGN'; then
  pass "T8: bound=warn + Write to sibling -> exit 0 + FOREIGN nudge"
else
  fail "T8: warn expected exit 0 + FOREIGN (rc=$T8W_RC err='$T8W_ERR')"
fi
printf 'worktree_guard: warn\nworktree_bound: off\n' > "$R/.ravenclaude/comfort-posture.yaml"
T8O_ERR="$(mk_payload "$R" s Write "$(jq -cn --arg fp "$SB/sibling/x.txt" '{file_path:$fp, content:"x"}')" | bash "$HOOK" check 2>&1 1>/dev/null)"
T8O_RC=$?
if [ "$T8O_RC" -eq 0 ] && [ -z "$T8O_ERR" ]; then
  pass "T8: bound=off + Write to sibling -> exit 0, no stderr"
else
  fail "T8: off expected silent allow (rc=$T8O_RC err='$T8O_ERR')"
fi
rm -rf "$SB"

echo
echo "── T9: Write under this tree (sibling exists) -> allow ───────────────────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" warn
git -C "$R" worktree add -q -b sibt9 "$SB/sibling"
mk_payload "$R" s Write "$(jq -cn --arg fp "$R/here.txt" '{file_path:$fp, content:"x"}')" | bash "$HOOK" check >/dev/null 2>&1
[ "$?" -eq 0 ] && pass "T9: Write under A with sibling present -> exit 0" || fail "T9: Write under A was denied"
rm -rf "$SB"

echo
echo "── T10: Write to /tmp is not a listed worktree -> allow ──────────────────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" warn
git -C "$R" worktree add -q -b sibt10 "$SB/sibling"
mk_payload "$R" s Write "$(jq -cn --arg fp "/tmp/rc-wt-probe" '{file_path:$fp, content:"x"}')" | bash "$HOOK" check >/dev/null 2>&1
[ "$?" -eq 0 ] && pass "T10: Write to /tmp/rc-wt-probe -> exit 0" || fail "T10: /tmp Write was denied"
rm -rf "$SB"

echo
echo "── T11: git -C <sibling> commit -> FOREIGN deny ──────────────────────────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" warn
git -C "$R" worktree add -q -b sibt11 "$SB/sibling"
T11_RC=0
mk_payload "$R" s Bash "$(jq -cn --arg c "git -C $SB/sibling commit -m x" '{command:$c}')" | bash "$HOOK" check >/dev/null 2>&1
T11_RC=$?
[ "$T11_RC" -eq 2 ] && pass "T11: git -C <B> commit -> exit 2" || fail "T11: expected exit 2, got $T11_RC"
rm -rf "$SB"

echo
echo "── T12: RC_WORKTREE_BOUND_ACK=1 escapes sibling Write ────────────────────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" warn
git -C "$R" worktree add -q -b sibt12 "$SB/sibling"
mk_payload "$R" s Write "$(jq -cn --arg fp "$SB/sibling/x.txt" '{file_path:$fp, content:"x"}')" | RC_WORKTREE_BOUND_ACK=1 bash "$HOOK" check >/dev/null 2>&1
[ "$?" -eq 0 ] && pass "T12: ACK + Write to sibling -> exit 0" || fail "T12: ACK did not escape"
rm -rf "$SB"

echo
echo "── T13: worktree_guard=off does not disable FOREIGN-TREE ─────────────────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" off
git -C "$R" worktree add -q -b sibt13 "$SB/sibling"
printf 'worktree_guard: off\nworktree_bound: block\n' > "$R/.ravenclaude/comfort-posture.yaml"
T13_RC=0
mk_payload "$R" s Write "$(jq -cn --arg fp "$SB/sibling/x.txt" '{file_path:$fp, content:"x"}')" | bash "$HOOK" check >/dev/null 2>&1
T13_RC=$?
[ "$T13_RC" -eq 2 ] && pass "T13: guard=off + bound=block + sibling Write -> exit 2" || fail "T13: expected exit 2, got $T13_RC"
rm -rf "$SB"

echo
echo "── T14: lone checkout Write under tree -> FOREIGN cannot fire ────────────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" warn
mk_payload "$R" s Write "$(jq -cn --arg fp "$R/solo.txt" '{file_path:$fp, content:"x"}')" | bash "$HOOK" check >/dev/null 2>&1
[ "$?" -eq 0 ] && pass "T14: lone checkout Write under tree -> exit 0" || fail "T14: lone Write was denied"
rm -rf "$SB"

echo
echo "── T15: GIT_WORK_TREE=<B> git add -> FOREIGN deny ────────────────────────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" warn
git -C "$R" worktree add -q -b sibt15 "$SB/sibling"
T15_RC=0
mk_payload "$R" s Bash "$(jq -cn --arg c "GIT_WORK_TREE=$SB/sibling git add -A" '{command:$c}')" | bash "$HOOK" check >/dev/null 2>&1
T15_RC=$?
[ "$T15_RC" -eq 2 ] && pass "T15: GIT_WORK_TREE=<B> git add -A -> exit 2" || fail "T15: expected exit 2, got $T15_RC"
rm -rf "$SB"

echo
echo "── T16: git status (no -C) from A -> allow ───────────────────────────────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" warn
git -C "$R" worktree add -q -b sibt16 "$SB/sibling"
mk_payload "$R" s Bash '{"command":"git status"}' | bash "$HOOK" check >/dev/null 2>&1
[ "$?" -eq 0 ] && pass "T16: git status (no -C) -> exit 0" || fail "T16: git status was denied"
rm -rf "$SB"

echo
echo "── T17: the lease governs THIS tree, not every file on the disk ──────────"
# ⛔ REGRESSION PIN, and BOTH halves are required. _wg_lease_should_enforce used to
# skip only a SIBLING-owned path (_wg_is_foreign), so a path owned by NO worktree
# came back "not foreign" and was enforced — the lease became a general jail over
# files that cannot possibly collide with this working tree.
#
# control 2026-08-24, observed live: with a lease held on the anchor checkout, an
# Edit to ~/.claude/projects/<proj>/memory/*.md was DENIED with the lease message,
# while the same bytes written through a Bash heredoc went through untouched — the
# clause blocked the honest tool and not the workaround.
#
# The out-of-tree half alone would pass against a hook that enforces NOTHING, so
# the in-tree half is what proves the fix narrowed the scope instead of removing it.
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R"
printf 'worktree_lease: on\nworktree_lease_idle_minutes: 20\n' >> "$R/.ravenclaude/comfort-posture.yaml"
OUTSIDE="$SB/not-a-repo"; mkdir -p "$OUTSIDE"
# A real check call establishes the lease for 'holder'.
mk_payload "$R" holder Write "$(jq -cn --arg fp "$R/seed.txt" '{file_path:$fp, content:"x"}')" \
  | bash "$HOOK" check >/dev/null 2>&1
# (a) IN-TREE write by a second session must STILL be denied — the lease's whole job.
mk_payload "$R" latecomer Write "$(jq -cn --arg fp "$R/intree.txt" '{file_path:$fp, content:"x"}')" \
  | bash "$HOOK" check >/dev/null 2>&1
[ "$?" -eq 2 ] \
  && pass "T17: in-tree write by a second session -> exit 2 (lease still protects the tree)" \
  || fail "T17: the lease stopped protecting its own working tree"
# (b) OUT-OF-TREE write by that same session must be allowed.
mk_payload "$R" latecomer Write "$(jq -cn --arg fp "$OUTSIDE/notes.md" '{file_path:$fp, content:"x"}')" \
  | bash "$HOOK" check >/dev/null 2>&1
[ "$?" -eq 0 ] \
  && pass "T17: write to a path owned by NO worktree -> exit 0 (not a general jail)" \
  || fail "T17: the lease denied a file outside every worktree"
rm -rf "$SB"

echo
echo "── T18: the stdin read is BOUNDED — an open pipe must not hang the guard ─"
# ⛔ REGRESSION PIN, and ALL THREE halves are load-bearing.
# `[ ! -t 0 ]` cannot tell "a payload is on its way" from "fd 0 is an open pipe
# nobody will ever write to" — both are simply not-a-tty — so the bare `cat` that
# used to sit here blocked FOREVER on an inherited pipe, stalling every caller
# downstream of the hook, audit-gates.sh Gate 140 included.
#
#   (a) the shipped hook EXITS under a FIFO whose writer is held open;
#   (b) the must-fail half — the same hook with the bare `cat` restored must
#       still HANG on that same FIFO. Without (b), (a) passes against a fixture
#       that never blocked anything and the pin measures the environment, not
#       the read. Both halves run against ONE fifo shape for exactly that reason.
#   (c) a MULTI-LINE payload still denies. A bound that truncates the JSON to its
#       first line yields a payload jq cannot parse, and an unparseable payload
#       makes the guard ALLOW — a bounded read that silently disarms the guard is
#       a worse defect than the hang it replaced.
#
# control 2026-08-25: under a FIFO with a held-open writer, the pre-fix hook hung
# until killed at 6s while a script that reads no stdin exited in 1s.

# _wg_bounded <limit-secs> <fifo-path> <cmd...> -> prints DONE | TIMEOUT
_wg_bounded() {
  local limit="$1" fifo="$2"; shift 2
  rm -f "$fifo"; mkfifo "$fifo"
  sleep "$((limit + 20))" > "$fifo" & local holder=$!
  ( "$@" >/dev/null 2>&1 < "$fifo" ) & local pid=$!
  local w=0
  while kill -0 "$pid" 2>/dev/null && [ "$w" -lt "$limit" ]; do sleep 1; w=$((w + 1)); done
  local verdict="DONE"
  if kill -0 "$pid" 2>/dev/null; then kill -9 "$pid" 2>/dev/null; verdict="TIMEOUT"; fi
  wait "$pid" 2>/dev/null
  kill -9 "$holder" 2>/dev/null; wait "$holder" 2>/dev/null
  rm -f "$fifo"
  printf '%s' "$verdict"
}

SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R"

# (a) the shipped hook must come back on its own. The watchdog limit MUST exceed
# the shipped deadline (10s) or this half kills a guard that was about to exit
# and reports the fix as broken — which is exactly what it did at limit 8.
T18_STATUS="$(_wg_bounded 16 "$SB/fifo" bash "$HOOK" status --json)"
T18_CHECK="$(_wg_bounded 16 "$SB/fifo" bash "$HOOK" check)"
if [ "$T18_STATUS" = "DONE" ] && [ "$T18_CHECK" = "DONE" ]; then
  pass "T18: status + check both exit under a held-open pipe (no unbounded read)"
else
  fail "T18: the guard hung on an open pipe (status=$T18_STATUS check=$T18_CHECK)"
fi

# (b) must-fail half — restore the bare `cat` and prove THAT still hangs.
T18_TMP="$(mktemp -d)"; T18_HOOK="$T18_TMP/worktree-guard-unbounded.sh"
python3 - "$HOOK" "$T18_HOOK" <<'T18PY'
import sys
src = open(sys.argv[1]).read()
needle = '[ -t 0 ] || payload="$(_wg_read_payload)"'
repl   = '[ ! -t 0 ] && payload="$(cat 2>/dev/null || printf \'\')"'
assert needle in src, "T18 anchor drift: the bounded-read call site is gone"
open(sys.argv[2], "w").write(src.replace(needle, repl))
T18PY
chmod +x "$T18_HOOK"
T18_MF="$(_wg_bounded 6 "$SB/fifo" bash "$T18_HOOK" status --json)"
if [ "$T18_MF" = "TIMEOUT" ]; then
  pass "T18: must-fail — the unbounded read still HANGS, so (a) measures the read"
else
  fail "T18: the unbounded hook exited too ($T18_MF) — the fixture blocks nothing, (a) is vacuous"
fi
rm -rf "$T18_TMP"

# (c) fidelity — a pretty-printed (multi-line) payload must still be parsed whole.
git -C "$R" worktree add -q -b t18sib "$SB/t18sib"
printf 'worktree_bound: block\n' >> "$R/.ravenclaude/comfort-posture.yaml"
T18_ONELINE="$(mk_payload "$R" t18 Write "$(jq -cn --arg fp "$SB/t18sib/x.txt" '{file_path:$fp, content:"x"}')")"
printf '%s' "$T18_ONELINE" | bash "$HOOK" check >/dev/null 2>&1; T18_RC1=$?
printf '%s' "$T18_ONELINE" | jq '.' | bash "$HOOK" check >/dev/null 2>&1; T18_RCM=$?
if [ "$T18_RC1" -eq 2 ] && [ "$T18_RCM" -eq 2 ]; then
  pass "T18: a multi-line payload still denies (rc=$T18_RCM) — the bound does not truncate"
else
  fail "T18: payload fidelity broke (one-line rc=$T18_RC1, multi-line rc=$T18_RCM; both must be 2)"
fi

# (d) a SLOW writer must not be mistaken for an ABSENT one.
# ⛔ This is the deadline's own risk, and it is the reverse of the hang: an empty
# payload carries no tool_input, so the guard has nothing to test and ALLOWS. A
# deadline short enough for a live-but-slow writer to trip therefore disarms the
# guard on a loaded machine, and the run looks identical to a clean one. BOTH
# halves are required — the tight half proves the failure is real and reachable,
# the shipped-default half proves the deadline actually clears it. A margin
# asserted without the tight half is a number nobody has tested.
# ⛔ pipefail is ON in this file, and it MUST be off for these two. When the hook
# gives up early it closes the read end, the still-sleeping producer takes SIGPIPE,
# and pipefail promotes that 141 over the hook's own status — the tight half then
# reads 141 instead of 0 and the assertion blames the wrong process. Exit 128-165
# is a signal, not a verdict. Measured here on the first run of this very block.
set +o pipefail
( sleep 3; printf '%s' "$T18_ONELINE" ) | RC_GUARD_STDIN_TIMEOUT=1 bash "$HOOK" check >/dev/null 2>&1
T18_SLOW_TIGHT=$?
( sleep 3; printf '%s' "$T18_ONELINE" ) | bash "$HOOK" check >/dev/null 2>&1
T18_SLOW_DEFAULT=$?
set -o pipefail
if [ "$T18_SLOW_TIGHT" -eq 0 ] && [ "$T18_SLOW_DEFAULT" -eq 2 ]; then
  pass "T18: a 3s-late writer is served by the shipped deadline (exit 2); a 1s deadline demonstrably disarms it (exit 0)"
else
  fail "T18: slow-writer margin wrong (tight=$T18_SLOW_TIGHT want 0, default=$T18_SLOW_DEFAULT want 2)"
fi
rm -rf "$SB"

echo
echo "── MF: must-fail half — strip the latecomer-only guard -> incumbent fires ─"
# Neutralize the latecomer test in _wg_contention so ANY other live record counts
# as contention; the incumbent (T3-silent) must then ALSO get nudged, proving the
# incumbent-silence property in T3 has real teeth.
PATCH_TMP="$(mktemp -d)"; PATCH_HOOK="$PATCH_TMP/worktree-guard-nolate.sh"
python3 - "$HOOK" "$PATCH_HOOK" <<'PY'
import sys
src = open(sys.argv[1]).read()
needle = '[ "$my_started" -gt "$ostarted" ] && return 0   # I arrived later -> I contend'
repl   = 'return 0   # MF: latecomer guard stripped — any other live record contends'
assert needle in src, "MF anchor drift: latecomer guard line not found"
open(sys.argv[2], "w").write(src.replace(needle, repl))
PY
chmod +x "$PATCH_HOOK"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" warn
PK="$(path_key "$R")"; BUCKET="$SB/guard/sessions/$PK"
sleep 300 & INC_PID=$!; disown 2>/dev/null || true
NOW="$(date +%s)"
# Seed a LATER live record so the incumbent has an "other" record to (wrongly) contend with.
seed_record "$BUCKET" latecomer "$INC_PID" "$((NOW + 100))"
INC_ERR="$(mk_payload "$R" incumbent Bash '{"command":"git status"}' | bash "$PATCH_HOOK" check 2>&1 1>/dev/null)"
kill "$INC_PID" 2>/dev/null
rm -rf "$SB" "$PATCH_TMP"
if printf '%s' "$INC_ERR" | grep -q 'another live'; then
  pass "MF: with the latecomer guard stripped, the incumbent ALSO fires — T3 has teeth"
else
  fail "MF: the stripped hook did NOT nudge the incumbent — the must-fail patch missed its target"
fi

echo
if [ "$FAIL" -eq 0 ]; then
  echo "worktree-guard core: ALL ASSERTIONS PASS"
  exit 0
else
  echo "worktree-guard core: $FAIL assertion(s) FAILED"
  exit 1
fi
