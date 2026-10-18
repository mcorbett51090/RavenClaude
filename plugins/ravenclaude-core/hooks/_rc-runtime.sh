#!/usr/bin/env bash
# _rc-runtime.sh — sourced helper: a private per-user runtime dir for RavenClaude's
# short-lived hook state (seat-child locks, pre-tool review records).
#
#   ${XDG_RUNTIME_DIR:-/tmp}/ravenclaude-$UID     created 0700, must be owned by us
#
# Trust rules (AppSec hook-env, 2026-10-18): XDG_RUNTIME_DIR is env and a project's
# .claude/settings.json can plant env, so a base that is relative or lies inside
# $CLAUDE_PROJECT_DIR falls back to /tmp. The dir itself must be a real directory
# (not a symlink) owned by $UID with mode exactly 0700 — a git checkout cannot
# produce that under the usual umask, so a repo cannot ship a pre-made lock dir.
# bash-3.2 safe; no GNU-only flags (find -user/-perm/-mmin exist on BSD and GNU).

_rc_runtime_dir() {
  local base="${XDG_RUNTIME_DIR:-/tmp}" uid d proj="${CLAUDE_PROJECT_DIR:-}"
  case "$base" in /*) : ;; *) base=/tmp ;; esac
  if [ -n "$proj" ]; then
    case "$base/" in "${proj%/}/"*) base=/tmp ;; esac
  fi
  uid="$(id -u)"
  d="${base%/}/ravenclaude-$uid"
  if [ ! -e "$d" ]; then (umask 077 && mkdir -p "$d") 2>/dev/null || return 1; fi
  [ -L "$d" ] && return 1
  [ -n "$(find "$d" -maxdepth 0 -type d -user "$uid" -perm 700 2>/dev/null)" ] || return 1
  printf '%s' "$d"
}

# _rc_runtime_subdir <name> — a 0700 subdirectory of the runtime dir.
_rc_runtime_subdir() {
  local d uid
  d="$(_rc_runtime_dir)" || return 1
  uid="$(id -u)"
  d="$d/$1"
  if [ ! -e "$d" ]; then (umask 077 && mkdir -p "$d") 2>/dev/null || return 1; fi
  [ -L "$d" ] && return 1
  [ -n "$(find "$d" -maxdepth 0 -type d -user "$uid" -perm 700 2>/dev/null)" ] || return 1
  printf '%s' "$d"
}

# _rc_safe_id <string> — keep [A-Za-z0-9_-], cap 128; empty if nothing remains.
_rc_safe_id() { printf '%s' "$1" | tr -cd 'A-Za-z0-9_-' | cut -c1-128; }

# _rc_new_nonce — 32 hex chars from /dev/urandom.
_rc_new_nonce() { od -An -N16 -tx1 /dev/urandom 2>/dev/null | tr -d ' \n'; }

# _rc_seat_child_lock <session_id> <nonce> — create the 0600 lock; prints its path.
_rc_seat_child_lock() {
  local d sid f
  d="$(_rc_runtime_dir)" || return 1
  sid="$(_rc_safe_id "$1")"; [ -n "$sid" ] || sid="nosession"
  f="$d/$sid.$2"
  (umask 077 && : >"$f") 2>/dev/null || return 1
  chmod 600 "$f" 2>/dev/null || return 1
  printf '%s' "$f"
}

# _rc_seat_child_ok <nonce> — 0 only if a lock named *.<nonce> exists in the runtime
# dir, is a regular file owned by $UID, mode exactly 0600, and is < 30 min old.
_rc_seat_child_ok() {
  local n="$1" d uid
  case "$n" in *[!0-9a-f]* | "") return 1 ;; esac
  [ "${#n}" -eq 32 ] || return 1
  d="$(_rc_runtime_dir)" || return 1
  uid="$(id -u)"
  [ -n "$(find "$d" -maxdepth 1 -type f -name "*.$n" -user "$uid" -perm 600 -mmin -30 2>/dev/null | head -1)" ]
}

# _rc_add_claude_to_path — the hardened launch line pins PATH to
# /usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin, which drops the native installer's
# ~/.local/bin (and the legacy ~/.claude/local). When `claude` is not on PATH, look
# ONLY there, using the passwd home (never $HOME — that is env and can be planted),
# and prepend the directory that holds it. No-op if claude already resolves.
_rc_add_claude_to_path() {
  command -v claude >/dev/null 2>&1 && return 0
  local home="" c
  if command -v getent >/dev/null 2>&1; then
    home="$(getent passwd "$(id -u)" 2>/dev/null | cut -d: -f6)"
  elif [ -x /usr/bin/dscl ]; then
    home="$(/usr/bin/dscl . -read "/Users/$(id -un)" NFSHomeDirectory 2>/dev/null | awk '{print $2}')"
  fi
  [ -n "$home" ] || return 1
  for c in "$home/.local/bin/claude" "$home/.claude/local/claude"; do
    if [ -x "$c" ] && [ ! -d "$c" ]; then
      case "$c" in "${CLAUDE_PROJECT_DIR:-/nonexistent}"/*) continue ;; esac
      PATH="${c%/claude}:$PATH"; export PATH
      return 0
    fi
  done
  return 1
}
