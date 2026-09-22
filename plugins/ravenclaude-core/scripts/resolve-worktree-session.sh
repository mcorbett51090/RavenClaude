#!/usr/bin/env bash
# resolve-worktree-session.sh — find which LIVE Claude Code session (if any) is
# bound to a given worktree of this repo, by reading worktree-guard.sh's own
# session registry. Read-only; never mutates anything.
#
# Why this exists: the `session-relay` skill needs to answer "which live
# session is working in worktree X?" before it can SendMessage a finding or a
# small handoff task to the right peer. worktree-guard.sh already tracks
# exactly this (it uses the registry to detect CONTENTION), so this script
# reuses that registry rather than inventing a second one — same PATH_KEY
# algorithm, same liveness check, byte-for-byte.
#
# What this script does NOT do: it does not know the ListAgents-visible
# name/ref for the resolved session_id — that mapping is not a documented
# contract (see knowledge/cross-session-messaging.md "Open questions"). The
# session-relay skill bridges that last hop by calling ListAgents and matching
# on session_id prefix / cwd, which is inherently a best-effort join, not a
# guaranteed one. This script gives the DETERMINISTIC half: which session_id,
# pid, and branch are bound to the worktree right now.
#
# Usage:
#   resolve-worktree-session.sh [<path>]        resolve by worktree path
#                                                 (default: current git toplevel)
#   resolve-worktree-session.sh --branch <name>  resolve by branch name (scans
#                                                 `git worktree list` for a
#                                                 checkout on that branch, then
#                                                 resolves that path)
#   resolve-worktree-session.sh --self-test      run built-in fixtures
#
# Output (stdout, always valid JSON, always exit 0 — read-only, fail-safe):
#   {"path_key":"<sha256>","toplevel":"<path>","live_sessions":[
#     {"session_id":"...","pid":123,"branch":"...","started_at":1234567890,
#      "peer_name":"matthewcorbett-bc","peer_status":"busy"}
#   ]}
# `peer_name` is the string to hand `SendMessage`'s `to` field directly (null
# when ~/.claude/sessions/<pid>.json is unreadable/absent — e.g. a session
# that has since exited; the pid liveness check should already have excluded
# that case, but the two registries are independent so a race is possible).
# An empty `live_sessions` array means "no live session found here" — that is
# a normal, expected answer (nobody working there right now / not a worktree
# of this repo / registry absent), never an error.
#
# Portability: bash 3.2-safe (no `declare -A` / `mapfile` / `${x^^}` /
# `shopt -s globstar`), no GNU `timeout` / `grep -P` / `sed -i` — the exact
# traps recorded in the ravenclaude-core CLAUDE.md "macOS door" milestones.
# Mirrors worktree-guard.sh's own PATH_KEY + liveness logic exactly so the
# two never disagree about which worktree a session belongs to.

set -uo pipefail

_guard_home() { printf '%s' "${RC_WORKTREE_GUARD_HOME:-$HOME/.ravenclaude/worktree-guard}"; }
_stale_ttl() {
  t="${RC_WORKTREE_GUARD_STALE_TTL:-900}"
  case "$t" in '' | *[!0-9]*) t=900 ;; esac
  printf '%s' "$t"
}

# ── the second hop: pid -> the display name / status ListAgents actually shows ──
# Verified 2026-09-01 (see knowledge/cross-session-messaging.md "correlation
# problem"): the ListAgents-visible ref is NOT derivable from session_id, but
# ~/.claude/sessions/<pid>.json's own `name` field IS the same string
# ListAgents displays (confirmed against this authoring session itself: pid ->
# name "matthewcorbett-bc", ListAgents row "matthewcorbett-bc [2eb70b]"). This
# is the reliable half of the join; the bracketed [ref] disambiguator is not
# reproduced here and is not needed — SendMessage's own contract says a bare
# name that matches exactly one live agent delivers directly.
_claude_sessions_home() { printf '%s' "${RC_CLAUDE_SESSIONS_HOME:-$HOME/.claude/sessions}"; }

_peer_field() {
  # $1 = pid, $2 = field name (name|status)
  f="$(_claude_sessions_home)/$1.json"
  [ -f "$f" ] || { printf ''; return 0; }
  sed -n "s/.*\"$2\":\"\\([^\"]*\\)\".*/\\1/p" "$f" | head -1
}

_sha256() {
  if command -v sha256sum >/dev/null 2>&1; then
    printf '%s' "$1" | sha256sum 2>/dev/null | cut -d' ' -f1
  elif command -v shasum >/dev/null 2>&1; then
    printf '%s' "$1" | shasum -a 256 2>/dev/null | cut -d' ' -f1
  else
    printf ''
  fi
}

_mtime() {
  # GNU stat vs BSD stat; empty stdout on failure (not-live), matching
  # worktree-guard.sh's own handling of the same platform split.
  stat -c %Y "$1" 2>/dev/null || stat -f %m "$1" 2>/dev/null
}

_is_live() {
  # kill -0(pid) AND (now - mtime <= STALE_TTL) — both, not either.
  f="$1"
  pid="$(sed -n 's/.*"pid":\([0-9]*\).*/\1/p' "$f" | head -1)"
  [ -n "$pid" ] || return 1
  kill -0 "$pid" 2>/dev/null || return 1
  m="$(_mtime "$f")"
  [ -n "$m" ] || return 1
  now="$(date +%s)"
  [ $((now - m)) -le "$(_stale_ttl)" ]
}

_json_escape() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

_resolve_toplevel() {
  git -C "$1" rev-parse --show-toplevel 2>/dev/null
}

emit_empty() {
  printf '{"path_key":"","toplevel":"","live_sessions":[]}\n'
}

resolve_path() {
  target="${1:-.}"
  TOPLEVEL="$(_resolve_toplevel "$target")"
  [ -n "$TOPLEVEL" ] || { emit_empty; return 0; }
  REAL_TOP="$(cd "$TOPLEVEL" 2>/dev/null && pwd -P)"
  [ -n "$REAL_TOP" ] || { emit_empty; return 0; }
  PATH_KEY="$(_sha256 "$REAL_TOP")"
  [ -n "$PATH_KEY" ] || { emit_empty; return 0; }

  SESS_DIR="$(_guard_home)/sessions/$PATH_KEY"
  entries=""
  if [ -d "$SESS_DIR" ]; then
    for f in "$SESS_DIR"/*.json; do
      [ -f "$f" ] || continue
      _is_live "$f" || continue
      sid="$(sed -n 's/.*"session_id":"\([^"]*\)".*/\1/p' "$f" | head -1)"
      pid="$(sed -n 's/.*"pid":\([0-9]*\).*/\1/p' "$f" | head -1)"
      branch="$(sed -n 's/.*"branch":"\([^"]*\)".*/\1/p' "$f" | head -1)"
      started="$(sed -n 's/.*"started_at":\([0-9]*\).*/\1/p' "$f" | head -1)"
      [ -n "$sid" ] || continue
      pname="$(_peer_field "${pid:-0}" name)"
      pstatus="$(_peer_field "${pid:-0}" status)"
      if [ -n "$pname" ]; then pname_json="\"$(_json_escape "$pname")\""; else pname_json="null"; fi
      if [ -n "$pstatus" ]; then pstatus_json="\"$(_json_escape "$pstatus")\""; else pstatus_json="null"; fi
      entry="{\"session_id\":\"$(_json_escape "$sid")\",\"pid\":${pid:-null},\"branch\":\"$(_json_escape "${branch:-}")\",\"started_at\":${started:-null},\"peer_name\":$pname_json,\"peer_status\":$pstatus_json}"
      if [ -z "$entries" ]; then entries="$entry"; else entries="$entries,$entry"; fi
    done
  fi
  printf '{"path_key":"%s","toplevel":"%s","live_sessions":[%s]}\n' \
    "$(_json_escape "$PATH_KEY")" "$(_json_escape "$REAL_TOP")" "$entries"
}

resolve_branch() {
  wanted="$1"
  root="$(_resolve_toplevel .)"
  [ -n "$root" ] || { emit_empty; return 0; }
  # `git worktree list --porcelain` -> pairs of `worktree <path>` / `branch refs/heads/<name>`
  path=""
  found=""
  while IFS= read -r line; do
    case "$line" in
      worktree\ *) path="${line#worktree }" ;;
      branch\ refs/heads/*)
        b="${line#branch refs/heads/}"
        if [ "$b" = "$wanted" ]; then found="$path"; break; fi
        ;;
    esac
  done < <(git -C "$root" worktree list --porcelain 2>/dev/null)
  [ -n "$found" ] || { emit_empty; return 0; }
  resolve_path "$found"
}

self_test() {
  fail=0
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT

  # Fixture repo with one worktree.
  repo="$tmp/repo"
  git init -q "$repo"
  git -C "$repo" config user.email test@example.com
  git -C "$repo" config user.name test
  git -C "$repo" commit -q --allow-empty -m init
  git -C "$repo" branch -q feature-x

  real_repo="$(cd "$repo" && pwd -P)"
  key="$(_sha256 "$real_repo")"

  export RC_WORKTREE_GUARD_HOME="$tmp/guard"
  mkdir -p "$RC_WORKTREE_GUARD_HOME/sessions/$key"

  # T1: no session file yet -> empty
  out="$(resolve_path "$repo")"
  case "$out" in *'"live_sessions":[]'*) : ;; *) echo "T1 FAIL: expected empty, got $out"; fail=1 ;; esac

  # T2: a live session (this test's own PID is always alive) -> found
  cat > "$RC_WORKTREE_GUARD_HOME/sessions/$key/aaaa.json" <<EOF
{"session_id":"aaaa-live","pid":$$,"ppid":1,"host":"test","branch":"feature-x","started_at":1234}
EOF
  out="$(resolve_path "$repo")"
  case "$out" in *'"session_id":"aaaa-live"'*) : ;; *) echo "T2 FAIL: expected aaaa-live, got $out"; fail=1 ;; esac

  # T3: a session with a dead pid (999999, vanishingly unlikely to be live) -> excluded
  cat > "$RC_WORKTREE_GUARD_HOME/sessions/$key/bbbb.json" <<EOF
{"session_id":"bbbb-dead","pid":999999,"ppid":1,"host":"test","branch":"main","started_at":1234}
EOF
  out="$(resolve_path "$repo")"
  case "$out" in *'"session_id":"bbbb-dead"'*) echo "T3 FAIL: dead pid should be excluded, got $out"; fail=1 ;; *) : ;; esac
  case "$out" in *'"session_id":"aaaa-live"'*) : ;; *) echo "T3b FAIL: live entry should still be present, got $out"; fail=1 ;; esac

  # T4: --branch resolution finds the same worktree via its branch name.
  # resolve_branch operates relative to the CALLER's cwd (by design — it asks
  # "within the repo I'm standing in, which worktree has branch X checked
  # out?"), so the fixture must cd into the fixture repo first, or this would
  # resolve against whatever real repo the self-test happens to run from.
  default_branch="$(git -C "$repo" branch --show-current)"
  if [ "$default_branch" = "main" ]; then
    out="$(cd "$repo" && resolve_branch main)"
    case "$out" in *'"session_id":"aaaa-live"'*) : ;; *) echo "T4 FAIL: --branch main should resolve the same worktree, got $out"; fail=1 ;; esac
  fi

  # T5: not a git repo -> empty, exit 0, never an error.
  nogit="$tmp/not-a-repo"
  mkdir -p "$nogit"
  out="$(resolve_path "$nogit")"
  case "$out" in *'"live_sessions":[]'*) : ;; *) echo "T5 FAIL: non-repo should yield empty, got $out"; fail=1 ;; esac

  # T6 (teeth): stripped liveness check must let the dead-pid session leak
  # through — proves T3 is actually testing something.
  out_mutant="$(_is_live() { return 0; }; resolve_path "$repo")"
  case "$out_mutant" in *'"session_id":"bbbb-dead"'*) : ;; *) echo "T6 FAIL (teeth): mutant should have leaked bbbb-dead, got $out_mutant"; fail=1 ;; esac

  # T7: the pid -> peer_name/peer_status second hop, positive control (a
  # distinct, non-obvious name/status pair proves the sed extracts the real
  # field rather than a coincidental match).
  export RC_CLAUDE_SESSIONS_HOME="$tmp/claude-sessions"
  mkdir -p "$RC_CLAUDE_SESSIONS_HOME"
  cat > "$RC_CLAUDE_SESSIONS_HOME/$$.json" <<EOF
{"pid":$$,"sessionId":"aaaa-live","cwd":"/nowhere","name":"zzz-peer-42","status":"waiting"}
EOF
  out="$(resolve_path "$repo")"
  case "$out" in *'"peer_name":"zzz-peer-42"'*) : ;; *) echo "T7 FAIL: expected peer_name zzz-peer-42, got $out"; fail=1 ;; esac
  case "$out" in *'"peer_status":"waiting"'*) : ;; *) echo "T7b FAIL: expected peer_status waiting, got $out"; fail=1 ;; esac

  # T8: absent ~/.claude/sessions/<pid>.json (a registry the worktree-guard
  # session file's OWN pid has no matching Claude-sessions file for) -> null,
  # never a crash or a stale/wrong value.
  rm -f "$RC_CLAUDE_SESSIONS_HOME/$$.json"
  out="$(resolve_path "$repo")"
  case "$out" in *'"peer_name":null'*) : ;; *) echo "T8 FAIL: expected peer_name null when the sessions file is absent, got $out"; fail=1 ;; esac

  if [ "$fail" -eq 0 ]; then
    echo "resolve-worktree-session.sh --self-test: ALL PASS (8/8)"
  else
    echo "resolve-worktree-session.sh --self-test: FAILURES ABOVE"
  fi
  return "$fail"
}

case "${1:-}" in
  --self-test) self_test; exit $? ;;
  --branch)
    shift
    [ -n "${1:-}" ] || { emit_empty; exit 0; }
    resolve_branch "$1"
    ;;
  *) resolve_path "${1:-.}" ;;
esac
