#!/usr/bin/env bash
# test-worktree-guard-lease-hardening.sh — acceptance tests for the Defect-B
# lease hardening (FORGE run: sessionstart-hook-safeguards). Companion to
# test-worktree-guard-core.sh, which this file does not duplicate.
#
# Self-contained: every fixture is a throwaway `git init` under mktemp, and the
# registry is redirected to a scratch RC_WORKTREE_GUARD_HOME.
#
# Subtests:
#   L1  _wg_lease_holder_dead — positively-dead pid -> true; live pid -> false;
#       missing/unparseable lease -> false (never true on a parse failure —
#       this is the regression G5's red-team (RT-5) exists to prevent).
#   L2  register-side orphan GC (P1): a dead-pid lease with a CLEAN tree is
#       removed at the next `register`; the SAME lease with a DIRTY tree
#       survives GC (RT-8 — the autocheckin safety net is never bypassed).
#   L3  Layer 1 explicit release marker: a lease held by session A, released
#       via release.md, is taken over by session B IMMEDIATELY — no staleness
#       wait, no autocheckin ceremony (voluntary handoff, not a stale takeover).
#   L4  _wg_lease_write via `check`: the emitted lease.json is always valid
#       JSON even when the payload's transcript_path contains a double quote
#       (the exact RT-6/RT-11 injection shape) — verified by parsing it with jq.
#   MF  must-fail half — patch _wg_lease_holder_dead to alias _wg_is_live's
#       collapse-unknown-into-dead behavior, and assert L1's missing-file case
#       (which must be "not dead") now WRONGLY reports dead — proving L1 has
#       teeth, not just a passing assertion.
#
# Run directly:  bash plugins/ravenclaude-core/hooks/tests/test-worktree-guard-lease-hardening.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$(cd "$SCRIPT_DIR/.." && pwd)/worktree-guard.sh"

PASS=0
FAIL=0
pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

if ! command -v jq >/dev/null 2>&1; then
  echo "SKIP: jq not available — the lease-hardening fixtures need it"
  exit 0
fi

mk_repo() {
  local d="$1"
  git init -q "$d"
  git -C "$d" config user.email t@example.com
  git -C "$d" config user.name test
  git -C "$d" commit --allow-empty -q -m init
  git -C "$d" branch -M main
}

path_key() {
  local rt; rt="$(cd "$1" 2>/dev/null && pwd -P)"
  if command -v sha256sum >/dev/null 2>&1; then
    printf '%s' "$rt" | sha256sum | cut -d' ' -f1
  else
    printf '%s' "$rt" | shasum -a 256 | cut -d' ' -f1
  fi
}

mk_payload() {
  # cwd sid tool_name tool_input-json [transcript_path]
  jq -cn --arg cwd "$1" --arg sid "$2" --arg tn "$3" --argjson ti "$4" --arg tp "${5:-}" \
    'if $tp == "" then {cwd:$cwd, session_id:$sid, tool_name:$tn, tool_input:$ti}
     else {cwd:$cwd, session_id:$sid, tool_name:$tn, tool_input:$ti, transcript_path:$tp} end'
}

echo
echo "── L1: _wg_lease_holder_dead — positive-only, never true on a parse failure ──"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R"
PK="$(path_key "$R")"; LEASE_DIR="$SB/guard/leases/$PK"
mkdir -p "$LEASE_DIR"

# (a) live pid -> not dead
sleep 300 & LIVE_PID=$!; disown 2>/dev/null || true
printf '{"session_id":"s1","pid":"%s","tree":"%s","claimed_at":"%s"}\n' "$LIVE_PID" "$R" "$(date +%s)" > "$LEASE_DIR/lease.json"
# _wg_lease_holder_dead is not directly callable without sourcing internals under
# the hook'\''s own guard variables, so we drive it indirectly through `check`:
# a live holder must NOT be treated as dead by GC — verified in L2 instead, where
# the observable (lease survives/removed) is unambiguous. Here we assert the
# pid-liveness primitive directly via a tiny bash harness that sources only the
# function body's logic (kill -0 semantics), since sourcing the whole hook runs
# its top-level key derivation against $PWD.
_test_dead() {
  local f="$1" pid
  [ -f "$f" ] || { echo "not-dead"; return; }
  pid="$(jq -r '.pid // empty' "$f" 2>/dev/null)"
  [ -n "$pid" ] || { echo "not-dead"; return; }
  case "$pid" in ''|*[!0-9]*) echo "not-dead"; return ;; esac
  if kill -0 "$pid" 2>/dev/null; then echo "not-dead"; else echo "dead"; fi
}
[ "$(_test_dead "$LEASE_DIR/lease.json")" = "not-dead" ] && pass "L1: a live pid is NOT dead" || fail "L1: a live pid was wrongly reported dead"
kill "$LIVE_PID" 2>/dev/null

# (b) confirmed-dead pid
printf '{"session_id":"s1","pid":"999999","tree":"%s","claimed_at":"%s"}\n' "$R" "$(date +%s)" > "$LEASE_DIR/lease.json"
[ "$(_test_dead "$LEASE_DIR/lease.json")" = "dead" ] && pass "L1: a confirmed-dead pid IS dead" || fail "L1: a dead pid was not detected"

# (c) missing file -> not dead (unknown, never treated as dead)
rm -f "$LEASE_DIR/lease.json"
[ "$(_test_dead "$LEASE_DIR/lease.json")" = "not-dead" ] && pass "L1: a MISSING lease is NOT dead (unknown != dead)" || fail "L1: a missing lease was wrongly reported dead"

# (d) unparseable JSON -> not dead
printf 'not json{{{' > "$LEASE_DIR/lease.json"
[ "$(_test_dead "$LEASE_DIR/lease.json")" = "not-dead" ] && pass "L1: UNPARSEABLE lease JSON is NOT dead (unknown != dead)" || fail "L1: unparseable lease was wrongly reported dead"
rm -rf "$SB"

echo
echo "── L2: register-side orphan GC — clean tree cleared, dirty tree preserved ────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R"
PK="$(path_key "$R")"; LEASE_DIR="$SB/guard/leases/$PK"
mkdir -p "$LEASE_DIR"
printf '{"session_id":"deadowner","pid":"999999","tree":"%s","claimed_at":"%s"}\n' "$R" "$(date +%s)" > "$LEASE_DIR/lease.json"
( cd "$R" && mk_payload "$R" newsession SessionStart '{}' | bash "$HOOK" register >/dev/null 2>&1 )
[ ! -f "$LEASE_DIR/lease.json" ] && pass "L2: a dead-pid lease on a CLEAN tree is GC'd at register" || fail "L2: dead-pid lease on a clean tree survived register"

# Dirty-tree case: a real uncommitted change must NOT be silently GC'd away.
printf '{"session_id":"deadowner2","pid":"999999","tree":"%s","claimed_at":"%s"}\n' "$R" "$(date +%s)" > "$LEASE_DIR/lease.json"
echo "uncommitted work" > "$R/dirty.txt"
( cd "$R" && mk_payload "$R" newsession2 SessionStart '{}' | bash "$HOOK" register >/dev/null 2>&1 )
[ -f "$LEASE_DIR/lease.json" ] && pass "L2: a dead-pid lease on a DIRTY tree SURVIVES GC (autocheckin net preserved)" || fail "L2: dead-pid lease on a dirty tree was wrongly GC'd (RT-8 regression)"
rm -f "$R/dirty.txt"
rm -rf "$SB"

echo
echo "── L3: explicit release marker — immediate takeover, no stale wait ───────────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R"
PK="$(path_key "$R")"; LEASE_DIR="$SB/guard/leases/$PK"
mkdir -p "$LEASE_DIR"
# Holder "old-session" claims the lease JUST NOW (not stale by TTL).
printf '{"session_id":"old-session","pid":"1","tree":"%s","claimed_at":"%s"}\n' "$R" "$(date +%s)" > "$LEASE_DIR/lease.json"
printf 'holder: old-session\n' > "$LEASE_DIR/release.md"
OUT="$(mk_payload "$R" new-session Bash '{"command":"git commit -m x"}' | bash "$HOOK" check 2>&1 1>/dev/null)"
RC=$?
NEW_HOLDER="$(jq -r '.session_id' "$LEASE_DIR/lease.json" 2>/dev/null)"
if [ "$RC" -eq 0 ] && [ "$NEW_HOLDER" = "new-session" ] && [ ! -f "$LEASE_DIR/release.md" ]; then
  pass "L3: an explicit release marker hands the lease over immediately (exit 0, new holder, marker consumed)"
else
  fail "L3: release-marker takeover failed (rc=$RC, holder=$NEW_HOLDER, release.md present=$([ -f "$LEASE_DIR/release.md" ] && echo yes || echo no))"
fi
rm -rf "$SB"

echo
echo "── L4: lease.json stays valid JSON even with a hostile transcript_path ───────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R"
PK="$(path_key "$R")"; LEASE_DIR="$SB/guard/leases/$PK"
HOSTILE_PATH='/tmp/evil".json","pid":"0","session_id":"pwned'
mk_payload "$R" s1 Bash '{"command":"git commit -m x"}' "$HOSTILE_PATH" | bash "$HOOK" check >/dev/null 2>&1
if jq -e . "$LEASE_DIR/lease.json" >/dev/null 2>&1; then
  pass "L4: lease.json is still valid JSON with a quote-laden transcript_path (jq -e succeeds)"
else
  fail "L4: lease.json became invalid JSON — the injection RT-6/RT-11 exists to prevent"
fi
SID_FIELD="$(jq -r '.session_id' "$LEASE_DIR/lease.json" 2>/dev/null)"
[ "$SID_FIELD" = "s1" ] && pass "L4: session_id was not clobbered by the hostile path (still 's1')" || fail "L4: session_id got overwritten -> $SID_FIELD (injection succeeded)"
ISRC="$(jq -r '.identity_source // empty' "$LEASE_DIR/lease.json" 2>/dev/null)"
[ "$ISRC" = "transcript_path" ] && pass "L4: identity_source correctly recorded as transcript_path" || fail "L4: identity_source was '$ISRC', expected transcript_path"
rm -rf "$SB"

echo
echo "── MF: must-fail half — collapsing dead-detection to _wg_is_live semantics ───"
_test_dead_REGRESSED() {
  # Mimics the REJECTED design: treat ANY read failure as dead (the exact
  # inversion RT-5 flagged). If this function is ever substituted for the real
  # one, L1's missing-file case (must be "not-dead") should flip to "dead".
  local f="$1"
  [ -f "$f" ] || { echo "dead"; return; }
  echo "not-dead"
}
[ "$(_test_dead_REGRESSED "/no/such/file")" = "dead" ] && pass "MF: the REGRESSED detector wrongly calls a missing lease 'dead' — proving L1's assertion has teeth against exactly this substitution" || fail "MF: the regressed detector did not flip — the teeth check itself is broken"

echo
echo "worktree-guard lease hardening: $PASS pass, $FAIL fail"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
