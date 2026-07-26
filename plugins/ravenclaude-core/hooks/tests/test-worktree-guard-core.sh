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
