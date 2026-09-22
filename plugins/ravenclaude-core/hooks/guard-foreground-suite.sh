#!/usr/bin/env bash
# guard-foreground-suite.sh
# PreToolUse hook for Bash. Denies a FOREGROUND invocation of a long-running
# suite that provably cannot finish inside the Bash tool's hard timeout ceiling.
#
# Input:  the tool call as JSON on stdin — {"tool_input": {"command": "...",
#         "run_in_background": bool, "timeout": ms}} (canonical Claude Code hook
#         contract).
# Output: exit 2 to BLOCK (stderr is fed back to the model, which can then retry
#         with run_in_background:true). Exit 2 is the ONLY blocking code —
#         Claude Code treats every other non-zero as a NON-blocking error and
#         runs the command anyway.
#
# ⛔ WHY THIS EXISTS, AND WHY A NOTE WAS NOT ENOUGH.
# The Bash tool's `timeout` is clamped at 600000 ms. `scripts/audit-gates.sh`
# (917 gates) outgrew that, so a foreground full-suite run is now STRUCTURALLY
# guaranteed to block for the full 10 minutes and then be auto-backgrounded —
# the session is wedged for 10 minutes and the operator sees a stall.
# control, measured 2026-08-25 in session 94d2ba9f:
#   foreground call 02:21:45Z -> result 02:31:49Z, "Command did not complete
#   within its 600s timeout and was moved to the background (ID: bg7y7j7s7)".
# ⛔ RAISING THE TIMEOUT IS A NON-FIX AND FAILS SILENTLY: the same session tried
#   `timeout: 900000` at 07:17:42Z and got the byte-identical "within its 600s
#   timeout" message at 07:27:45Z. 900000 is clamped to 600000 with no warning.
# ⛔ THE SAME SESSION HAD ALREADY FOUND THE FIX AND REGRESSED OFF IT — five clean
#   `run_in_background:true` runs that morning, foreground again that night, and
#   a third occurrence hours later. A memory note is not a control; this is.
#
# POSTURE: this is an ERGONOMIC guard, not a security control, so it FAILS OPEN.
# An unreadable payload, an absent jq/python3, or a parse it cannot do all ALLOW
# and emit a warn event. Contrast worktree-guard.sh, which gates a trust boundary
# and therefore fails CLOSED. Do not "harden" this one into a deny-on-unknown:
# blocking a tool call because a convenience hook could not read its own input
# would be a worse failure than the ten minutes it is preventing.

set -euo pipefail

# ⛔ NO `cmd | grep -q` ANYWHERE IN THIS FILE. With `pipefail` on, `grep -q`
# closes the pipe on its FIRST match, the producer takes SIGPIPE, and the
# pipeline returns 141 — turning a successful match into a failed pipeline. All
# matching below is bash `case` globbing, which needs no pipe at all.

_gfs_self="$(basename "$0")"

# ── fail-safe helpers ─────────────────────────────────────────────────────────
_gfs_dir="$(dirname "$0")"
if [ -f "${_gfs_dir}/_emit-event.sh" ]; then
  # shellcheck source=/dev/null
  . "${_gfs_dir}/_emit-event.sh" 2>/dev/null || true
fi
command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }

if [ -f "${_gfs_dir}/_portable.sh" ]; then
  # shellcheck source=/dev/null
  . "${_gfs_dir}/_portable.sh" 2>/dev/null || true
fi
# ⛔ Degrade to an UNBOUNDED read, never to an empty payload. A stub returning
# nothing would turn a missing helper into a guard that silently never fires.
command -v _rc_timeout >/dev/null 2>&1 || _rc_timeout() { shift; "$@"; }

# ── the suites this guard covers ──────────────────────────────────────────────
# Space-separated basenames. Kept as a list so a second long suite can be added
# without touching the logic. Matching is on the basename only, so any invocation
# path (./scripts/x.sh, bash plugins/../x.sh, an absolute path) is covered.
GFS_SUITES="${RC_FOREGROUND_SUITES:-audit-gates.sh}"

# ── read the payload, BOUNDED ─────────────────────────────────────────────────
# ⛔ A bare `cat` here blocks FOREVER when fd 0 is an open pipe with no writer —
# `[ ! -t 0 ]` cannot tell "a payload is coming" from "nobody will ever write".
# Bounding the WRITER with _rc_timeout+cat, never `read -t`: `read -t` deadlines
# a COMPLETE LINE and bash reads a pipe one byte per read(2), so on a single-line
# JSON payload the deadline races bash's byte loop and payload SIZE eats the
# budget. Measured 2026-08-25: an 11 MB single-line payload through a real pipe
# lost every byte at `read -t 10` under load, while `_rc_timeout 10 cat` took 0.3s.
payload=""
_gfs_rc=0
if [ ! -t 0 ]; then
  payload="$(_rc_timeout 10 cat 2>/dev/null)" || _gfs_rc=$?
fi
case "$_gfs_rc" in
  0) : ;;
  # 124 GNU timeout, 142 perl alarm. Both mean "no usable payload" -> allow.
  124|142)
    _emit_hook_event "$_gfs_self" "warn" "Bash" "" "stdin-timeout" "0" || true
    exit 0 ;;
  *)
    _emit_hook_event "$_gfs_self" "warn" "Bash" "" "stdin-error" "0" || true
    exit 0 ;;
esac
[ -n "$payload" ] || exit 0

# ── extract the three fields ──────────────────────────────────────────────────
cmd=""; bg=""; tmo=""
if command -v jq >/dev/null 2>&1; then
  cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // empty' 2>/dev/null || true)"
  bg="$(printf '%s'  "$payload" | jq -r '.tool_input.run_in_background // empty' 2>/dev/null || true)"
  tmo="$(printf '%s' "$payload" | jq -r '.tool_input.timeout // empty' 2>/dev/null || true)"
elif command -v python3 >/dev/null 2>&1; then
  # jq-free fallback. Kept because a silent no-op here is indistinguishable from
  # "the guard passed", which is the defect class this repo keeps paying for.
  _gfs_fields="$(printf '%s' "$payload" | python3 -c 'import json,sys
try:
    ti = (json.load(sys.stdin).get("tool_input") or {})
except Exception:
    ti = {}
print(json.dumps(ti.get("command", "") or ""))
print(ti.get("run_in_background", "") if ti.get("run_in_background") is not None else "")
print(ti.get("timeout", "") if ti.get("timeout") is not None else "")' 2>/dev/null || printf '""\n\n\n')"
  cmd="$(printf '%s' "$_gfs_fields" | sed -n '1p')"
  # Unwrap the json.dumps quoting so `case` globbing sees the real text.
  cmd="$(printf '%s' "$cmd" | python3 -c 'import json,sys
try: sys.stdout.write(json.loads(sys.stdin.read()))
except Exception: pass' 2>/dev/null || true)"
  bg="$(printf '%s' "$_gfs_fields" | sed -n '2p')"
  tmo="$(printf '%s' "$_gfs_fields" | sed -n '3p')"
else
  # No parser at all -> allow. Ergonomic guard, fail open.
  _emit_hook_event "$_gfs_self" "warn" "Bash" "" "no-json-parser" "0" || true
  exit 0
fi
[ -n "$cmd" ] || exit 0

# ── the two legitimate ways to run a long suite ───────────────────────────────
case "$bg" in true|True|TRUE|1) exit 0 ;; esac

# ⛔ The ACK must be read out of the COMMAND TEXT, not the environment. An env var
# set by the caller cannot reach a PreToolUse hook from inside the command it
# gates — the hook runs in its own process, before the command does. A literal
# `RC_SUITE_FOREGROUND_ACK=1` prefix IS visible here because the hook inspects
# the command string, which is why the escape is spelled this way.
case "$cmd" in *RC_SUITE_FOREGROUND_ACK=1*) exit 0 ;; esac

# ── invocation vs mention ─────────────────────────────────────────────────────
# ⛔ A GUARD THAT CANNOT TELL A COMMAND FROM A DESCRIPTION OF ONE BLOCKS ITS OWN
# REPAIR. `grep -n audit-gates.sh`, `sed -n '1,60p' …/audit-gates.sh` and
# `git show HEAD:scripts/audit-gates.sh` all MENTION the suite and must run. So
# this does not substring-match the whole command. It splits into segments and
# checks each segment's FIRST WORD: a hit requires the suite to be the program
# being executed, or the argument of a shell interpreter.
_gfs_hit=0
_gfs_segments="$(printf '%s' "$cmd" | awk '{ gsub(/&&|\|\||[;|]/, "\n"); print }')"

while IFS= read -r _seg; do
  # strip leading whitespace
  _seg="${_seg#"${_seg%%[![:space:]]*}"}"
  [ -n "$_seg" ] || continue

  # strip any number of leading VAR=value assignments (FOO=1 BAR=2 bash x.sh)
  while :; do
    _first="${_seg%%[[:space:]]*}"
    case "$_first" in
      [A-Za-z_]*=*)
        _rest="${_seg#*[[:space:]]}"
        # ⛔ An explicit `if`, not `[ … ] && break`. Under `set -e` a bare
        # `test && cmd` whose test FAILS leaves the list status non-zero, and
        # this guard must never die on its own parsing.
        if [ "$_rest" = "$_seg" ]; then
          break                          # no space left; nothing more to strip
        fi
        _seg="${_rest#"${_rest%%[![:space:]]*}"}"
        ;;
      *) break ;;
    esac
  done

  _first="${_seg%%[[:space:]]*}"
  _base="${_first##*/}"

  # A `--check N` run is ONE gate and finishes in seconds — always allowed.
  case "$_seg" in *--check*) continue ;; esac

  for _suite in $GFS_SUITES; do
    case "$_base" in
      "$_suite")
        _gfs_hit=1 ;;
      bash|sh|zsh|ksh|dash)
        # the suite as an argument to an interpreter
        case "$_seg" in *"$_suite"*) _gfs_hit=1 ;; esac
        ;;
    esac
  done
done <<EOF
$_gfs_segments
EOF

[ "$_gfs_hit" = "1" ] || exit 0

# ── deny ──────────────────────────────────────────────────────────────────────
_gfs_tmo_note=""
case "$tmo" in
  ''|*[!0-9]*) : ;;
  *)
    # Same `set -e` reasoning as the assignment-stripper above: explicit `if`.
    if [ "$tmo" -gt 600000 ]; then
      _gfs_tmo_note=" Your timeout of ${tmo}ms is above the 600000ms ceiling and is silently clamped to it — raising it does nothing."
    fi
    ;;
esac

_emit_hook_event "$_gfs_self" "deny" "Bash" "$cmd" "foreground-long-suite" "2" || true

{
  printf '%s\n' "[guard-foreground-suite] BLOCKED: this runs a full suite in the FOREGROUND, where the Bash tool's hard 600000ms ceiling will wedge the session for 10 minutes and then background it anyway.${_gfs_tmo_note}"
  printf '%s\n' "Use ONE of:"
  printf '%s\n' "  1. run_in_background: true   — then poll the log file. This is the right answer for a full-suite run."
  printf '%s\n' "  2. --check N                 — run the single gate you actually care about, in the foreground."
  printf '%s\n' "  3. prefix the command with RC_SUITE_FOREGROUND_ACK=1 if you genuinely want to spend the 10 minutes."
} >&2

exit 2
