#!/usr/bin/env bash
# coordinator-lock.sh — self-contained single-instance lock for the
# source-control-coordinator agent (build-plan.md Task 3.1 / §4.5).
#
# ⛔ Deliberately NOT composed with worktree-guard.sh's own lease reader. That
# reader writes {session_id, pid (string), tree, claimed_at (epoch), host,
# identity_source, transcript_hash} and its staleness check
# (_wg_lease_holder_dead()) reads a `pid` key this record never sets — it
# would never reap a stranded coordinator lock. This script is self-contained,
# at its own path outside worktree-guard.sh's namespace entirely, mirroring
# its lease idiom BY COPY (atomic mkdir + mtime/pid liveness), not by call.
#
# ⛔ Lives under bin/, not scripts/ — a deliberate, content-neutral placement.
# `plugins/ravenclaude-core/scripts/` is fully substrate-protected by the
# command-review tribunal's own self-tamper guard (THING_SUBSTRATE in
# thing-decision.py denies ANY write under that directory, new file or edit,
# regardless of content) because it holds the tribunal's OWN enforcement code
# and direct dependencies. This script has nothing to do with that — it is a
# plain operational lock manager, the same category as the existing bin/rcwt
# and bin/claude-launch-guard. Placing it in bin/ respects the guard's intent
# (protect the Thing's own code) without asking for an exemption to touch
# unrelated code that happens to share a directory with it.
#
# bash 3.2-safe: no declare -A / mapfile / ${x^^} / shopt -s globstar. No GNU
# `timeout` / `grep -P` / `sed -i` (per this repo's own recorded macOS-door
# discipline — see plugins/ravenclaude-core/CLAUDE.md's macOS-door milestones).
set -euo pipefail

RC_WORKTREE_GUARD_HOME="${RC_WORKTREE_GUARD_HOME:-$HOME/.ravenclaude}"
LOCK_ROOT="$RC_WORKTREE_GUARD_HOME/coordinator-lock"
HELD_DIR="$LOCK_ROOT/held"
LEASE_FILE="$LOCK_ROOT/lease.json"
# Serializes stale-holder REAPERS (see acquire()). A reap.lock older than this
# many minutes is a crashed reaper's leftover and is broken once.
REAP_LOCK="$LOCK_ROOT/reap.lock"
REAP_LOCK_STALE_MINUTES=1
# Staleness threshold: no heartbeat refresh within this many seconds means the
# holder is presumed dead IF ALSO its pid fails a kill -0 check (both signals
# required — see _is_stale below). Default 30 min.
STALE_SECONDS="${COORDINATOR_LOCK_STALE_SECONDS:-1800}"

mkdir -p "$LOCK_ROOT"

_now_iso() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

_pid_alive() { kill -0 "$1" 2>/dev/null; }

# ⛔ Resolve the STABLE session-identity PID, not this script's own $PPID.
# worktree-guard.sh's own SESSION_PID="$PPID" comment assumes a hook script is
# invoked as a DIRECT child of the long-lived `claude` CLI process — true for
# a hook, but this script is instead invoked BY the coordinator agent's own
# Bash tool call (`bash coordinator-lock.sh <verb>`), which adds one more
# process-tree hop: `claude` -> (a per-tool-call wrapper shell, fresh PID
# every single call) -> this script. A bare $PPID here is therefore that
# fresh per-call wrapper, NOT the stable `claude` process — verified live
# this session: two separate direct Bash tool calls both reported $PPID=503
# (comm=claude, stable), but a `bash coordinator-lock.sh` invocation's own
# $PPID varied per call (it was the fresh wrapper one level below 503).
#
# The fix walks UP the ancestor chain looking for a process whose `comm` is
# literally `claude` — portable across however many wrapper layers a given
# host's harness happens to insert, rather than hardcoding a specific hop
# count that would only hold for this one environment's process-tree shape.
# Bounded to 10 hops; falls back to $PPID (ambiguous, not a crash) if no
# `claude`-named ancestor is found within that bound — matching this file's
# own "ambiguous state is NOT-dead" fail-safe philosophy elsewhere.
_resolve_session_pid() {
  local p="$PPID" hops=0 comm
  while [ "$hops" -lt 10 ] && [ -n "$p" ] && [ "$p" != "0" ] && [ "$p" != "1" ]; do
    comm="$(ps -o comm= -p "$p" 2>/dev/null | tr -d '[:space:]')"
    if [ "$comm" = "claude" ]; then
      echo "$p"
      return 0
    fi
    p="$(ps -o ppid= -p "$p" 2>/dev/null | tr -d '[:space:]')"
    hops=$((hops + 1))
  done
  echo "$PPID"   # fall back to the immediate parent — ambiguous, not fatal
}

_write_lease() {
  # $1=session_id $2=pid $3=acquired_at $4=heartbeat_at $5=current_pr(or empty) $6=current_pr_started_at(or empty)
  local sid="$1" pid="$2" acquired="$3" heartbeat="$4" pr="${5:-}" pr_started="${6:-}"
  local pr_json="null" pr_started_json="null"
  [ -n "$pr" ] && pr_json="$pr"
  [ -n "$pr_started" ] && pr_started_json="\"$pr_started\""
  cat > "$LEASE_FILE" <<EOF
{
  "schema_version": 1,
  "holder_session_id": "$sid",
  "holder_pid": $pid,
  "acquired_at": "$acquired",
  "heartbeat_at": "$heartbeat",
  "current_pr": $pr_json,
  "current_pr_started_at": $pr_started_json
}
EOF
}

_lease_field() {
  # Cheap field extraction without a JSON-parser dependency (bash 3.2-safe).
  # Handles both quoted-string and bare (number/null) values.
  local field="$1"
  sed -n "s/.*\"${field}\":[[:space:]]*\"\{0,1\}\([^\",}]*\)\"\{0,1\}.*/\1/p" "$LEASE_FILE" 2>/dev/null | head -1
}

# Dead ONLY on an explicit `kill -0` failure. Any read/parse failure or
# ambiguous state is NOT-dead — mirrors worktree-guard.sh's own
# _wg_lease_holder_dead() caveat ("a reused pid says nothing at all" — the
# staleness window bound below is the mitigation, not a perfect liveness test).
_is_stale() {
  local dir="$1"
  local held_pid
  held_pid="$(cat "$dir/pid" 2>/dev/null || true)"
  [ -z "$held_pid" ] && return 1
  if _pid_alive "$held_pid"; then
    return 1
  fi
  return 0
}

_atomic_acquire() {
  # Real atomic path: mkdir is atomic on every POSIX filesystem — exactly one
  # concurrent caller's mkdir succeeds.
  mkdir "$HELD_DIR" 2>/dev/null
}

_disabled_atomic_acquire() {
  # THE MUST-FAIL CONTROL (Gate G10's paired run): swap the atomic create for
  # a check-then-create, deliberately reintroducing the TOCTOU gap so the
  # concurrency self-test's control run can prove it is capable of detecting
  # the race at all (a test that can't fail proves nothing). The sleep widens
  # the window so the race manifests reliably rather than probabilistically.
  #
  # ⛔ Must use `mkdir -p`, NOT bare `mkdir`. A first attempt with bare `mkdir`
  # here looked "disabled" but still routed through the OS's genuinely-atomic
  # mkdir(2) underneath — every racer's check-then-create still ended in a
  # real mkdir call, and mkdir(2) itself only ever lets one caller succeed
  # regardless of what preceded it, so the control silently measured nothing
  # (verified live: 3/3 control runs reported exactly 1 winner — a control
  # that cannot fail proves nothing, per this repo's own gate-audit
  # discipline). `mkdir -p` is idempotent — it returns 0 whether or not the
  # directory already existed — which is what actually removes the atomicity
  # signal and lets every check-then-create racer believe it won.
  if [ ! -d "$HELD_DIR" ]; then
    sleep 0.05
    mkdir -p "$HELD_DIR" 2>/dev/null
  else
    return 1
  fi
}

# Take the reaper mutex. A plain mkdir is the atomic step; on failure, a
# reap.lock older than REAP_LOCK_STALE_MINUTES is a crashed reaper's leftover
# and is broken ONCE before one retry. Failure means DENIED, which is already
# the documented lost-race result.
_reap_mutex_take() {
  [ "${_COORD_DISABLE_REAP_MUTEX:-0}" = "1" ] && return 0
  mkdir "$REAP_LOCK" 2>/dev/null && return 0
  if [ -n "$(find "$LOCK_ROOT" -maxdepth 1 -name reap.lock -mmin +"$REAP_LOCK_STALE_MINUTES" 2>/dev/null)" ]; then
    rmdir "$REAP_LOCK" 2>/dev/null || true
    mkdir "$REAP_LOCK" 2>/dev/null && return 0
  fi
  return 1
}

_reap_mutex_drop() {
  [ "${_COORD_DISABLE_REAP_MUTEX:-0}" = "1" ] && return 0
  rmdir "$REAP_LOCK" 2>/dev/null || true
}

acquire() {
  local disable_atomic="${1:-0}"
  local session_id="${CLAUDE_SESSION_ID:-unknown}"
  # ⛔ The resolved stable session pid, NOT $$ and NOT a bare $PPID — see
  # _resolve_session_pid's own header comment for why a bare $$ (a fresh
  # per-Bash-tool-call subprocess) or a bare $PPID (still one wrapper layer
  # short, for a script invoked via `bash coordinator-lock.sh`) both fail to
  # identify the same caller across separate `acquire`/`heartbeat`/`release`
  # invocations.
  local my_pid; my_pid="$(_resolve_session_pid)"
  local acquire_fn=_atomic_acquire
  [ "$disable_atomic" = "1" ] && acquire_fn=_disabled_atomic_acquire

  if $acquire_fn; then
    echo "$my_pid" > "$HELD_DIR/pid"
    local ts; ts="$(_now_iso)"
    _write_lease "$session_id" "$my_pid" "$ts" "$ts"
    echo "ACQUIRED session=$session_id pid=$my_pid"
    return 0
  fi

  # Contended. Rename the stale holder dir aside, then re-attempt the atomic
  # create — never delete-then-create.
  #
  # ⛔ Each step is atomic but the DECISION was not: two contenders could both
  # read the dead pid, the first renamed it aside and created a NEW live
  # holder, and the second's rename (decided on the stale reading) then moved
  # that live holder aside too — two ACQUIRED. Reapers are now serialized by
  # their own mkdir mutex and staleness is re-decided INSIDE it; the mutex is
  # dropped only after the new pid file is written, so the next reaper reads a
  # live (or still-empty, i.e. not-stale) holder.
  # control: 8 contenders on a dead-holder lock, 40 trials -> 9 double-holder
  # trials before; --self-test --dead-holder asserts 1 winner per trial after,
  # and --disable-reap-mutex reproduces >1 (2026-10-19).
  if _is_stale "$HELD_DIR" && _reap_mutex_take; then
    if _is_stale "$HELD_DIR"; then
      [ -n "${_COORD_TEST_REAP_SLEEP:-}" ] && sleep "$_COORD_TEST_REAP_SLEEP"
      local stale_aside="${HELD_DIR}.stale.$$"
      if mv "$HELD_DIR" "$stale_aside" 2>/dev/null; then
        if $acquire_fn; then
          echo "$my_pid" > "$HELD_DIR/pid"
          local ts; ts="$(_now_iso)"
          _write_lease "$session_id" "$my_pid" "$ts" "$ts"
          _reap_mutex_drop
          echo "ACQUIRED (after reap of stale holder) session=$session_id pid=$my_pid"
          rm -rf "$stale_aside" 2>/dev/null || true
          return 0
        fi
        # Lost the re-acquire race after winning the reap race (a plain
        # acquirer created $HELD_DIR in the gap) — putting it back is not
        # attempted; just clean up our stale-aside copy.
        rm -rf "$stale_aside" 2>/dev/null || true
      fi
    fi
    _reap_mutex_drop
  fi

  echo "DENIED holder-still-live-or-lost-race"
  return 1
}

heartbeat() {
  [ -f "$LEASE_FILE" ] || { echo "NO-LEASE"; return 1; }
  local sid pid acquired pr pr_started
  sid="$(_lease_field holder_session_id)"
  pid="$(_lease_field holder_pid)"
  acquired="$(_lease_field acquired_at)"
  pr="$(_lease_field current_pr)"
  pr_started="$(_lease_field current_pr_started_at)"
  local this_pid; this_pid="$(_resolve_session_pid)"
  [ "$pid" = "$this_pid" ] || { echo "NOT-HOLDER lease-pid=$pid this-pid=$this_pid"; return 1; }
  local ts; ts="$(_now_iso)"
  _write_lease "$sid" "$pid" "$acquired" "$ts" "$pr" "$pr_started"
  echo "HEARTBEAT-REFRESHED $ts"
}

release() {
  [ -d "$HELD_DIR" ] || { echo "NOT-HELD"; return 0; }
  local held_pid; held_pid="$(cat "$HELD_DIR/pid" 2>/dev/null || true)"
  local this_pid; this_pid="$(_resolve_session_pid)"
  if [ "$held_pid" != "$this_pid" ]; then
    echo "REFUSE-not-holder lease-pid=$held_pid this-pid=$this_pid"
    return 1
  fi
  rm -rf "$HELD_DIR" 2>/dev/null || true
  rm -f "$LEASE_FILE" 2>/dev/null || true
  echo "RELEASED"
}

status() {
  if [ ! -d "$HELD_DIR" ]; then
    echo "UNHELD"
    return 0
  fi
  local held_pid; held_pid="$(cat "$HELD_DIR/pid" 2>/dev/null || true)"
  if _pid_alive "${held_pid:-0}"; then
    echo "HELD pid=$held_pid alive=1"
  else
    echo "HELD pid=$held_pid alive=0 (stale — eligible for reap)"
  fi
}

_self_test_worker() {
  local disable_atomic="$1" out="$2"
  ( acquire "$disable_atomic" ) >> "$out" 2>&1 || true
}

self_test() {
  local concurrency="${1:-8}"
  local disable_atomic="${2:-0}"
  local scratch; scratch="$(mktemp -d)"
  export RC_WORKTREE_GUARD_HOME="$scratch"
  LOCK_ROOT="$RC_WORKTREE_GUARD_HOME/coordinator-lock"
  HELD_DIR="$LOCK_ROOT/held"
  LEASE_FILE="$LOCK_ROOT/lease.json"
  mkdir -p "$LOCK_ROOT"

  local out="$scratch/results.log"
  : > "$out"
  local i=0
  local pids=""
  while [ "$i" -lt "$concurrency" ]; do
    ( _self_test_worker "$disable_atomic" "$out" ) &
    pids="$pids $!"
    i=$((i + 1))
  done
  # shellcheck disable=SC2086
  wait $pids 2>/dev/null || true

  local winners
  winners="$(grep -c '^ACQUIRED' "$out" 2>/dev/null || echo 0)"
  echo "concurrency=$concurrency disable_atomic=$disable_atomic winners=$winners"
  rm -rf "$scratch" 2>/dev/null || true
  echo "$winners"
}

# Dead-holder reap race: pre-seed held/pid with a reaped (dead) pid, race N
# contenders through the REAP path, repeat for several trials. Prints the max
# winners seen in any trial and the count of zero-winner trials. The reap
# window is widened (_COORD_TEST_REAP_SLEEP) so a missing mutex shows up
# reliably rather than probabilistically.
self_test_dead_holder() {
  local concurrency="${1:-4}" disable_mutex="${2:-0}" trials="${3:-5}"
  local t=0 max_winners=0 zero_trials=0
  while [ "$t" -lt "$trials" ]; do
    local scratch; scratch="$(mktemp -d)"
    mkdir -p "$scratch/coordinator-lock/held"
    ( exit 0 ) &
    local dead=$!
    wait "$dead" 2>/dev/null || true
    echo "$dead" > "$scratch/coordinator-lock/held/pid"
    local out="$scratch/results.log"
    : > "$out"
    local i=0 pids=""
    while [ "$i" -lt "$concurrency" ]; do
      (
        export RC_WORKTREE_GUARD_HOME="$scratch"
        export _COORD_TEST_REAP_SLEEP=0.05
        export _COORD_DISABLE_REAP_MUTEX="$disable_mutex"
        bash "$0" acquire >> "$out" 2>&1 || true
      ) &
      pids="$pids $!"
      i=$((i + 1))
    done
    # shellcheck disable=SC2086
    wait $pids 2>/dev/null || true
    local winners
    winners="$(grep -c '^ACQUIRED' "$out" 2>/dev/null || true)"
    winners="${winners:-0}"
    [ "$winners" -gt "$max_winners" ] && max_winners="$winners"
    [ "$winners" -eq 0 ] && zero_trials=$((zero_trials + 1))
    rm -rf "$scratch" 2>/dev/null || true
    t=$((t + 1))
  done
  echo "dead-holder concurrency=$concurrency trials=$trials disable_reap_mutex=$disable_mutex max_winners=$max_winners zero_winner_trials=$zero_trials"
  echo "$max_winners $zero_trials"
}

case "${1:-}" in
  acquire) shift; acquire "${1:-0}" ;;
  heartbeat) heartbeat ;;
  release) release ;;
  status) status ;;
  --self-test)
    shift
    concurrency=8
    disable_atomic=0
    dead_holder=0
    disable_reap_mutex=0
    trials=5
    while [ $# -gt 0 ]; do
      case "$1" in
        --concurrency) concurrency="$2"; shift 2 ;;
        --disable-atomic-step) disable_atomic=1; shift ;;
        --dead-holder) dead_holder=1; shift ;;
        --disable-reap-mutex) disable_reap_mutex=1; dead_holder=1; shift ;;
        --trials) trials="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    if [ "$dead_holder" = "1" ]; then
      res="$(self_test_dead_holder "$concurrency" "$disable_reap_mutex" "$trials" | tail -1)"
      max_w="${res%% *}"
      zeros="${res##* }"
      if [ "$disable_reap_mutex" = "1" ]; then
        if [ "$max_w" -gt 1 ]; then
          echo "CONTROL OK: $max_w winners in one trial with the reap mutex disabled (dead-holder race reproduced, control has teeth)"
          exit 0
        fi
        echo "CONTROL FAILED: expected >1 winners in some trial with the reap mutex disabled, got max $max_w"
        exit 1
      fi
      if [ "$max_w" -eq 1 ] && [ "$zeros" -eq 0 ]; then
        echo "SELF-TEST PASS: exactly 1 winner in each of $trials dead-holder trials ($concurrency contenders)"
        exit 0
      fi
      echo "SELF-TEST FAIL: dead-holder reap — max winners $max_w, zero-winner trials $zeros (want 1 and 0)"
      exit 1
    fi
    winners="$(self_test "$concurrency" "$disable_atomic" | tail -1)"
    if [ "$disable_atomic" = "1" ]; then
      if [ "$winners" -gt 1 ]; then
        echo "CONTROL OK: $winners winners with the atomic step disabled (race reproduced, control has teeth)"
        exit 0
      else
        echo "CONTROL FAILED: expected >1 winners with the atomic step disabled, got $winners — the control cannot detect the race"
        exit 1
      fi
    else
      if [ "$winners" -eq 1 ]; then
        echo "SELF-TEST PASS: exactly 1 winner of $concurrency concurrent claimants"
        exit 0
      else
        echo "SELF-TEST FAIL: expected exactly 1 winner, got $winners"
        exit 1
      fi
    fi
    ;;
  *)
    echo "usage: coordinator-lock.sh {acquire [0|1]|heartbeat|release|status|--self-test [--concurrency N] [--disable-atomic-step]}" >&2
    exit 2
    ;;
esac
