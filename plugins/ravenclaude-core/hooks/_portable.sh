#!/usr/bin/env bash
# _portable.sh
# Shared, sourced helper for stock-toolchain portability. Sourced by hooks that must
# run on macOS, whose stock toolchain is NOT GNU: bash 3.2.57 (frozen at GPLv2), no
# coreutils, BSD userland. macOS is a first-class Claude Code platform.
#
# NOT a registered hook — the leading underscore keeps it out of the hook count
# (same convention as _emit-event.sh / _scrub.sh / _model-fallback.sh).
#
# Carries no top-level `set` (it is sourced, and must not change the caller's shell
# options). Every function is bash-3.2 compatible.

# _rc_timeout SECS CMD [ARGS...] — run CMD with a wall-clock ceiling, portably.
#
# WHY: GNU coreutils `timeout` is ABSENT on stock macOS `[verified: exit 127]`. A bare
# `timeout ...` in a hook therefore fails command-not-found, which — inside the usual
# `out="$(timeout N cmd)" || rc=$?` / `|| echo ''` shapes — silently takes the caller's
# error path on EVERY macOS session. That is how the tribunal's seats all "abstain" and
# how route-decision-review silently emits allow: not a timeout, an absent binary.
#
# Resolution order:
#   1. `timeout`   — GNU coreutils (Linux, CI, or a mac with coreutils on PATH).
#   2. `gtimeout`  — homebrew coreutils' prefixed name on macOS.
#   3. `perl`      — stock on macOS (/usr/bin/perl). `alarm` is preserved across execve
#                    and SIGALRM's disposition resets to default (terminate), so the
#                    exec'd command is killed at the deadline.
#   4. unbounded   — run it anyway. A hook that refuses to run is worse than one that
#                    runs without a ceiling; the caller's own error path still applies.
#
# EXIT-CODE CONTRACT (honest, and deliberately not papered over): GNU `timeout` returns
# **124** on expiry; the perl fallback's SIGALRM kill surfaces as **142** (128+14). No
# caller in this repo branches on 124 `[verified 2026-07-15: no `-eq 124` / `= 124` test
# exists in any hook]` — every one treats any non-zero as abstain/error, which is the
# correct behavior for a timeout either way. If a future caller needs to distinguish
# "timed out" from "failed", fix it HERE (a fork+waitpid perl shim can return 124) rather
# than assuming GNU semantics at the call site.
_rc_timeout() {
  local _secs="$1"
  shift
  if command -v timeout >/dev/null 2>&1; then
    timeout "${_secs}s" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then
    gtimeout "${_secs}s" "$@"
  elif command -v perl >/dev/null 2>&1; then
    perl -e 'alarm shift; exec @ARGV or exit 127' "$_secs" "$@"
  else
    "$@"
  fi
}

# _rc_upper STR — uppercase, portably.
#
# WHY: `${var^^}` is bash 4.0+; on bash 3.2 it is a "bad substitution" that exits 1 —
# a NON-blocking hook error, i.e. a silent fail-open. `tr` is POSIX and everywhere.
_rc_upper() {
  printf '%s' "$1" | tr '[:lower:]' '[:upper:]'
}

# _rc_pcre_match FILE PATTERN — case-insensitive PCRE match over the WHOLE file.
#
# The portable replacement for the `grep -Pzi PAT FILE` idiom:
#   -P  PCRE (lookaheads, \s, \b)      -z  whole file as ONE NUL-terminated record,
#                                          so `[\s\S]` and lookaheads span lines
#   -i  case-insensitive
#
# WHY: `grep -P` is a **GNU extension**. BSD/macOS grep exits **2** ("invalid option --
# P") `[verified]`, and inside the callers' `if grep -Pzi …; then findings+=(…); fi`
# shape an exit of 2 reads as **NO MATCH** — the finding is never emitted and the hook
# exits 0. Silent, unconditional, every macOS session.
#
# Why perl and not "install GNU grep": perl **is** the PCRE engine and is stock on macOS
# (/usr/bin/perl), so this gives REAL coverage. An "install GNU grep for full coverage"
# advisory only moves the failure to every mac without it — the same fragility as
# depending on a homebrew bash being ahead of /usr/bin on PATH.
#
# The BEGIN/END flag (rather than a bare `exit 0 if //`) is load-bearing: with -0777 an
# EMPTY file yields zero records, so the body never runs and a naive shim would exit 0
# = "match". Here $m stays 1 = no match. `[verified: empty file -> no-match]`
#
# The pattern crosses into perl via the ENVIRONMENT, never interpolated into the -e text,
# so shell/perl quoting can't mangle it. Returns 0 = match, 1 = no match / unreadable /
# no engine (fail to "no finding", matching the callers' existing contract).
_rc_pcre_match() {
  local _file="$1"
  local _pat="$2"
  [ -r "$_file" ] || return 1
  if command -v perl >/dev/null 2>&1; then
    RC_PCRE_PAT="$_pat" perl -0777 -ne 'BEGIN{$m=1} $m=0 if /$ENV{RC_PCRE_PAT}/i; END{exit $m}' -- "$_file" 2>/dev/null
    return $?
  fi
  # No perl (unusual). Fall back to GNU grep -P if this grep has it.
  grep -Pzi -- "$_pat" "$_file" >/dev/null 2>&1
}
