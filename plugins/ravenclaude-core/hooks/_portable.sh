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

# ── Host-env normalisation (added 2026-07-28 — multi-host audit, Codex P0) ────
#
# WHY: Codex CLI has converged on the CLAUDE CODE hook contract — same event
# names, same stdin fields, the same hookSpecificOutput envelope, the same
# `exit 2 + stderr = block`, and a loader that reads hooks/hooks.json directly.
# It needs NO envelope adapter (unlike Copilot, which required a 456-line
# generator plus ~300 lines of translation).
#
# CORRECTED 2026-07-28 after reading Codex's OWN hooks doc
# (learn.chatgpt.com/docs/hooks; see knowledge/codex-cli-customization.md).
# An earlier version of this comment claimed Codex supplies PLUGIN_ROOT *instead
# of* CLAUDE_PLUGIN_ROOT, so every hook failed open on its helper path. THAT WAS
# WRONG: Codex publishes CLAUDE_PLUGIN_ROOT and CLAUDE_PLUGIN_DATA as
# legacy-compatibility names, so helper-path resolution works unaided.
#
# What IS genuinely absent under Codex — and why this shim is still correct:
#   CLAUDE_PROJECT_DIR — not in the compatibility set. 25 hook files read it, and
#                        _emit-event.sh no-ops without it, so NO hook event is ever
#                        written and the Guardrails dashboard stays dark.
#   CLAUDE_SESSION_ID  — not in the compatibility set. 14 hook files read it, so
#                        events land under runs/unknown/ even if the dir resolved.
# Codex passes session values (cwd, session_id) via STDIN JSON rather than the
# environment, which is why an env-only reader finds nothing.
#
# The alias fills blanks only, so where Codex already supplies CLAUDE_PLUGIN_ROOT
# it is a harmless no-op. The shim is right; one sentence of its original
# justification was not, and is corrected rather than left standing.
#
# Deliberately a 3-line-per-var ALIAS, not an adapter. Adding a second
# Copilot-shaped translation layer for a host that already speaks the contract
# would be the expensive wrong answer.
#
# INVARIANT: never overwrite a CLAUDE_* value the host already set. Claude Code
# is authoritative about its own vocabulary; this fills genuine blanks only.
_rc_host_env() {
  [ -z "${CLAUDE_PLUGIN_ROOT:-}" ] && [ -n "${PLUGIN_ROOT:-}" ] && export CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT"
  [ -z "${CLAUDE_PROJECT_DIR:-}" ] && [ -n "${PROJECT_DIR:-}" ] && export CLAUDE_PROJECT_DIR="$PROJECT_DIR"
  [ -z "${CLAUDE_PROJECT_DIR:-}" ] && [ -n "${CODEX_PROJECT_ROOT:-}" ] && export CLAUDE_PROJECT_DIR="$CODEX_PROJECT_ROOT"
  [ -z "${CLAUDE_SESSION_ID:-}" ] && [ -n "${SESSION_ID:-}" ] && export CLAUDE_SESSION_ID="$SESSION_ID"
  [ -z "${CLAUDE_SESSION_ID:-}" ] && [ -n "${CODEX_SESSION_ID:-}" ] && export CLAUDE_SESSION_ID="$CODEX_SESSION_ID"
  return 0
}

# _rc_host — POSITIVE-signal host identification. Prints exactly one of:
#   claude-code | copilot | codex | unknown
#
# HONESTY, and it is load-bearing: this returns `unknown` rather than guessing.
# An in-session probe on 2026-07-28 found COPILOT_DEBUG_NONCE set INSIDE a
# Claude Code session, so "any COPILOT_* implies Copilot" would mislabel a live
# session. Copilot is therefore identified ONLY by THING_HOST, which
# copilot-hook-adapter.sh exports explicitly — an assertion made by the adapter,
# never an inference from ambient environment. A wrong host verdict is worse
# than no verdict, because callers branch on it.
_rc_host() {
  if [ -n "${THING_HOST:-}" ]; then printf '%s\n' "$THING_HOST"; return 0; fi
  if [ -n "${CLAUDECODE:-}" ] || [ -n "${CLAUDE_CODE_ENTRYPOINT:-}" ]; then printf 'claude-code\n'; return 0; fi
  if [ -n "${CODEX_SESSION_ID:-}" ] || [ -n "${CODEX_PROJECT_ROOT:-}" ]; then printf 'codex\n'; return 0; fi
  printf 'unknown\n'
}

# ── Normalise ON SOURCE. ──────────────────────────────────────────────────────
# Deliberate: the alias is useless if every hook has to remember to call it, and
# it shipped with ZERO callers. Running it here means every hook that already
# sources this file is fixed without touching it, and any hook added later gets
# it for free — the failure mode was hooks silently failing open on a variable
# NAME, so the fix must not itself depend on being remembered.
#
# Safe to run at source time: it only ever FILLS BLANKS (never overwrites a
# CLAUDE_* the host set), touches no shell options, and returns 0 unconditionally,
# so it cannot alter a sourcing hook's control flow. That is why this file's
# "carries no top-level `set`" contract is still honoured.
#
# NOT paired with a hard `exit 2` when PLUGIN_ROOT is absent, despite that being
# the obvious fail-closed move. `.claude/settings.json`'s marketplace dev-mirror
# invokes these hooks by `${CLAUDE_PROJECT_DIR}` path, where CLAUDE_PLUGIN_ROOT is
# legitimately unset — a blanket exit 2 would block every tool call in the repo
# that develops the plugin. Fail-closed on a variable that is *correctly* empty
# in a supported configuration is not a guardrail, it is an outage.
_rc_host_env
