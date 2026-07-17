#!/usr/bin/env bash
# worktree-guard.sh — portable worktree-hygiene guard (the CORE detection engine).
#
# Fires on exactly TWO locally-detectable conditions, per session, per working
# tree (everything else is silent — a lone checkout in a fresh container satisfies
# neither, which is why "all repos, not opt-in" is safe):
#   (a) CONTENTION — another *live* Claude session is already operating in this
#       same working tree (same realpath(toplevel), same host). Only the LATECOMER
#       fires; the incumbent stays silent.
#   (b) ANCHOR-WORK — this checkout is the repo's primary/anchor, worktrees already
#       exist, and HEAD is on the anchor branch.
#
# Subcommands (selected by $1):
#   register       SessionStart. Records this session's own file, GC-sweeps the
#                  bucket, emits a banner (warn/block, when flagged). ALWAYS exit 0
#                  (a SessionStart hook can never block).
#   check          PreToolUse. warn -> stderr nudge (throttled 1/session/clause),
#                  exit 0. block -> exit 2 DENY only on a MUTATING op (never a read
#                  / git status / rcwt). Escape hatch: RC_WORKTREE_GUARD_ACK=1.
#   status --json  Read-only JSON snapshot for the dashboard / tests.
#
# Keying: TOPLEVEL=git rev-parse --show-toplevel; PATH_KEY=sha256(realpath TOPLEVEL).
# A submodule resolves its own toplevel -> an independent bucket (never contends
# with the superproject).
#
# Registry: ${RC_WORKTREE_GUARD_HOME:-$HOME/.ravenclaude/worktree-guard}/sessions/
#           <PATH_KEY>/<session_id>.json = {session_id,pid,ppid,host,branch,started_at}
# Each session writes ONLY its own file -> no shared mutable file -> no write race.
# Liveness = kill -0(pid) AND (now - mtime(file) <= STALE_TTL, default 900). Both,
# not either: PID catches idle-but-alive; TTL bounds PID-reuse. Touch throttled to
# <=1/60s. GC is folded into `register` (never depends on Stop firing).
#
# Knob: `worktree_guard: off|warn|block` in <repo>/.ravenclaude/comfort-posture.yaml.
# DEFAULT warn even if the key OR the file is absent (T6 — all repos, not opt-in).
# `off` short-circuits BEFORE any git shell-out (a fast no-op for non-adopters).
#
# Portability: set -uo pipefail (NOT -e — a guard must not die mid-check). macOS
# bash 3.2 / BSD-safe (no declare -A / mapfile / grep -P / timeout / sed -i /
# ${x^^} / globstar). Fail-OPEN (missing git/jq/shasum -> exit 0 allow).

set -uo pipefail

# ── sourced helpers (fail-safe: define stubs if absent) ───────────────────────
_wg_script_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || printf '.')"
# shellcheck source=/dev/null
[ -f "$_wg_script_dir/_portable.sh" ] && . "$_wg_script_dir/_portable.sh" 2>/dev/null || true
# shellcheck source=/dev/null
[ -f "$_wg_script_dir/_emit-event.sh" ] && . "$_wg_script_dir/_emit-event.sh" 2>/dev/null || true
command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }
command -v _ee_resolve_session >/dev/null 2>&1 || _ee_resolve_session() { printf '%s' "${CLAUDE_SESSION_ID:-unknown}"; }
command -v _ee_sanitize_session >/dev/null 2>&1 || _ee_sanitize_session() {
  local s; s="$(printf '%s' "${1:-}" | tr -dc 'A-Za-z0-9._-' | cut -c1-128)"
  case "$s" in .|.. | "") s="unknown" ;; esac; printf '%s' "$s"
}

SUBCMD="${1:-}"

# ── read the stdin payload (check/register carry one; status usually does not) ─
payload=""
[ ! -t 0 ] && payload="$(cat 2>/dev/null || printf '')"

# ── project dir (for the knob) + cwd (for git) ────────────────────────────────
cwd=""
if [ -n "$payload" ] && command -v jq >/dev/null 2>&1; then
  cwd="$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null || printf '')"
fi
[ -z "$cwd" ] && cwd="${CLAUDE_PROJECT_DIR:-$PWD}"
posture="${cwd}/.ravenclaude/comfort-posture.yaml"

# ── KNOB: worktree_guard: off|warn|block (default warn). Read with the
#    runaway-brake sed/grep idiom. `off` short-circuits BEFORE any git shell-out. ─
mode="$(sed -n 's/^[[:space:]]*worktree_guard:[[:space:]]*\([A-Za-z]\{1,\}\).*/\1/p' "$posture" 2>/dev/null | head -1)"
[ -z "$mode" ] && mode="warn"
case "$mode" in off|warn|block) ;; *) mode="warn" ;; esac
if [ "$mode" = "off" ]; then
  # Fast no-op: nothing written, no git invoked. status still reports (below).
  [ "$SUBCMD" = "status" ] || exit 0
fi

# ── fail-open dependency floor (missing git/jq/shasum -> allow) ────────────────
command -v git >/dev/null 2>&1 || exit 0

wg_git() { git -C "$cwd" "$@" 2>/dev/null; }

# realpath of a DIRECTORY, portably (pwd -P resolves symlinks; no realpath(1)).
_wg_realpath() { ( cd "$1" 2>/dev/null && pwd -P ) 2>/dev/null; }

# sha256 of a string. sha256sum (GNU) or shasum -a 256 (stock macOS Perl).
_wg_sha256() {
  if command -v sha256sum >/dev/null 2>&1; then
    printf '%s' "$1" | sha256sum 2>/dev/null | cut -d' ' -f1
  elif command -v shasum >/dev/null 2>&1; then
    printf '%s' "$1" | shasum -a 256 2>/dev/null | cut -d' ' -f1
  else
    return 1
  fi
}

# mtime (epoch seconds) of a file, portably (BSD stat -f / GNU stat -c).
_wg_mtime() { stat -f %m "$1" 2>/dev/null || stat -c %Y "$1" 2>/dev/null; }

# extract a scalar field from a small record JSON (jq, else a grep/sed fallback).
_wg_json_field() {
  [ -f "$1" ] || return 1
  if command -v jq >/dev/null 2>&1; then
    jq -r --arg k "$2" '.[$k] // empty' "$1" 2>/dev/null
  else
    grep -o "\"$2\"[[:space:]]*:[[:space:]]*\"\{0,1\}[^,\"}]*" "$1" 2>/dev/null \
      | head -1 | sed 's/.*:[[:space:]]*"\{0,1\}//'
  fi
}

# ── keying ────────────────────────────────────────────────────────────────────
TOPLEVEL="$(wg_git rev-parse --show-toplevel)"
[ -z "$TOPLEVEL" ] && exit 0            # not a git repo -> allow (fail-open)
REAL_TOP="$(_wg_realpath "$TOPLEVEL")"
[ -z "$REAL_TOP" ] && REAL_TOP="$TOPLEVEL"
PATH_KEY="$(_wg_sha256 "$REAL_TOP")"
[ -z "$PATH_KEY" ] && exit 0            # no sha tool -> allow (fail-open)

GUARD_HOME="${RC_WORKTREE_GUARD_HOME:-$HOME/.ravenclaude/worktree-guard}"
SESS_DIR="$GUARD_HOME/sessions/$PATH_KEY"
THROTTLE_DIR="$GUARD_HOME/throttle/$PATH_KEY"
STALE_TTL="${RC_WORKTREE_GUARD_STALE_TTL:-900}"
case "$STALE_TTL" in ''|*[!0-9]*) STALE_TTL=900 ;; esac

# session identity (like _emit-event.sh: $CLAUDE_SESSION_ID -> payload .session_id
# -> unknown; sanitized path-safe).
session="$(_ee_sanitize_session "$(_ee_resolve_session 2>/dev/null || printf 'unknown')")"
SELF_FILE="$SESS_DIR/$session.json"
SESSION_PID="$PPID"                     # the long-lived Claude process (hooks are
                                        # ephemeral; $PPID is stable across a session)

# ── liveness: kill -0(pid) AND (now - mtime <= STALE_TTL) ─────────────────────
_wg_is_live() {
  local f="$1" pid m now
  [ -f "$f" ] || return 1
  pid="$(_wg_json_field "$f" pid)"
  [ -n "$pid" ] || return 1
  case "$pid" in ''|*[!0-9]*) return 1 ;; esac
  kill -0 "$pid" 2>/dev/null || return 1
  m="$(_wg_mtime "$f")"
  [ -n "$m" ] || return 1
  case "$m" in ''|*[!0-9]*) return 1 ;; esac
  now="$(date +%s 2>/dev/null || printf '0')"
  [ $(( now - m )) -le "$STALE_TTL" ] || return 1
  return 0
}

# write THIS session's own record (never touches another session's file).
_wg_write_record() {
  local file="$1" started="$2" host branch ppid_val
  host="$(hostname 2>/dev/null || printf 'unknown')"
  branch="$(wg_git rev-parse --abbrev-ref HEAD)"
  [ -n "$branch" ] || branch=""
  ppid_val="$(ps -o ppid= -p "$SESSION_PID" 2>/dev/null | tr -dc '0-9')"
  [ -n "$ppid_val" ] || ppid_val=0
  case "$started" in ''|*[!0-9]*) started="$(date +%s 2>/dev/null || printf '0')" ;; esac
  if command -v jq >/dev/null 2>&1; then
    jq -cn --arg sid "$session" --argjson pid "${SESSION_PID:-0}" \
       --argjson ppid "${ppid_val:-0}" --arg host "$host" --arg branch "$branch" \
       --argjson started "$started" \
       '{session_id:$sid,pid:$pid,ppid:$ppid,host:$host,branch:$branch,started_at:$started}' \
       > "$file" 2>/dev/null || return 1
  else
    printf '{"session_id":"%s","pid":%s,"ppid":%s,"host":"%s","branch":"%s","started_at":%s}\n' \
      "$session" "${SESSION_PID:-0}" "$ppid_val" "$host" "$branch" "$started" > "$file" 2>/dev/null || return 1
  fi
  return 0
}

# heartbeat: create my record if absent (started_at=now), else throttled touch (<=1/60s).
_wg_heartbeat() {
  if [ -f "$SELF_FILE" ]; then
    local m now
    m="$(_wg_mtime "$SELF_FILE")"; now="$(date +%s 2>/dev/null || printf '0')"
    if [ -n "$m" ]; then
      case "$m" in ''|*[!0-9]*) m="$now" ;; esac
      [ $(( now - m )) -ge 60 ] && touch "$SELF_FILE" 2>/dev/null || true
    fi
  else
    _wg_write_record "$SELF_FILE" "$(date +%s 2>/dev/null || printf '0')" || true
  fi
}

# GC: sweep my PATH_KEY bucket, delete every non-live file. Folded into register.
_wg_gc() {
  local f
  for f in "$SESS_DIR"/*.json; do
    [ -f "$f" ] || continue
    _wg_is_live "$f" || rm -f "$f" 2>/dev/null || true
  done
}

# CONTENTION: >=1 OTHER live record for this bucket AND I am the LATECOMER
# (my started_at > that record's). Only the latecomer fires; incumbent stays silent.
_wg_contention() {
  local my_started f ostarted
  my_started="$(_wg_json_field "$SELF_FILE" started_at)"
  case "$my_started" in ''|*[!0-9]*) return 1 ;; esac
  for f in "$SESS_DIR"/*.json; do
    [ -f "$f" ] || continue
    [ "$f" = "$SELF_FILE" ] && continue
    _wg_is_live "$f" || continue
    ostarted="$(_wg_json_field "$f" started_at)"
    case "$ostarted" in ''|*[!0-9]*) continue ;; esac
    [ "$my_started" -gt "$ostarted" ] && return 0   # I arrived later -> I contend
  done
  return 1
}

# anchor branch: posture override -> main-if-exists -> master -> main.
_wg_anchor_branch() {
  local b
  b="$(sed -n 's/^[[:space:]]*worktree_guard_anchor_branch:[[:space:]]*\([A-Za-z0-9._/-]\{1,\}\).*/\1/p' "$posture" 2>/dev/null | head -1)"
  if [ -n "$b" ]; then printf '%s' "$b"; return 0; fi
  if wg_git show-ref --verify --quiet refs/heads/main; then printf 'main'
  elif wg_git show-ref --verify --quiet refs/heads/master; then printf 'master'
  else printf 'main'; fi
}

# ANCHOR (dynamic): git worktree list --porcelain; entries<=1 -> NOT anchor
# (single-checkout silence); else realpath(TOPLEVEL)==realpath(first entry) AND
# current branch == anchor branch -> IS anchor.
_wg_is_anchor() {
  local out count first rp_first cur anchor
  out="$(wg_git worktree list --porcelain)"
  [ -n "$out" ] || return 1
  count="$(printf '%s\n' "$out" | grep -c '^worktree ')"
  case "$count" in ''|*[!0-9]*) return 1 ;; esac
  [ "$count" -le 1 ] && return 1
  first="$(printf '%s\n' "$out" | grep '^worktree ' | head -1 | sed 's/^worktree //')"
  [ -n "$first" ] || return 1
  rp_first="$(_wg_realpath "$first")"
  [ -n "$rp_first" ] || rp_first="$first"
  [ "$rp_first" = "$REAL_TOP" ] || return 1
  cur="$(wg_git rev-parse --abbrev-ref HEAD)"
  anchor="$(_wg_anchor_branch)"
  [ "$cur" = "$anchor" ] || return 1
  return 0
}

# ── MUTATING-op classification (block mode only denies these) ──────────────────
tn=""; cmd=""; fp=""
if [ -n "$payload" ] && command -v jq >/dev/null 2>&1; then
  tn="$(printf '%s' "$payload" | jq -r '.tool_name // ""' 2>/dev/null)"
  [ "$tn" = "Bash" ] && cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // ""' 2>/dev/null)"
  case "$tn" in Write|Edit|MultiEdit) fp="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // ""' 2>/dev/null)" ;; esac
fi

_wg_path_under_tree() {
  local p="$1" d rp
  [ -n "$p" ] || return 1
  case "$p" in /*) d="$(dirname "$p")" ;; *) d="$cwd/$(dirname "$p")" ;; esac
  rp="$( cd "$d" 2>/dev/null && pwd -P )" || return 1
  [ -n "$rp" ] || return 1
  [ "$rp" = "$REAL_TOP" ] && return 0
  case "$rp/" in "$REAL_TOP"/*) return 0 ;; esac
  return 1
}

# A MUTATING op = a Write/Edit/MultiEdit under the tree, OR a Bash git mutation
# (commit/add/checkout/switch/merge/rebase/cherry-pick/revert/stash/rm/mv). NEVER
# a read / git status / rcwt.
_wg_is_mutating() {
  case "$tn" in
    Write|Edit|MultiEdit)
      if [ -n "$fp" ]; then _wg_path_under_tree "$fp" && return 0 || return 1; fi
      return 0 ;;               # unknown path -> fail-safe (treat as under-tree)
    Bash) : ;;
    *) return 1 ;;
  esac
  [ -n "$cmd" ] || return 1
  case " $cmd " in
    *"git commit"*|*"git add"*|*"git checkout"*|*"git switch"*|*"git merge"*|\
    *"git rebase"*|*"git cherry-pick"*|*"git revert"*|*"git stash"*|\
    *"git rm "*|*"git mv "*) return 0 ;;
  esac
  return 1
}

# nudge throttle: 1/session/clause. Returns 0 if already nudged (skip), else marks
# and returns 1 (proceed to nudge).
_wg_already_nudged() {
  local mk="$THROTTLE_DIR/${session}.$1"
  [ -f "$mk" ] && return 0
  mkdir -p "$THROTTLE_DIR" 2>/dev/null || return 1
  : > "$mk" 2>/dev/null || true
  return 1
}

# ── subcommand dispatch ───────────────────────────────────────────────────────
case "$SUBCMD" in

  register)
    # SessionStart: cannot block. GC the bucket, write our own fresh record,
    # evaluate flags, emit a banner (warn/block only, when flagged). Always exit 0.
    mkdir -p "$SESS_DIR" 2>/dev/null || exit 0
    _wg_gc
    _wg_write_record "$SELF_FILE" "$(date +%s 2>/dev/null || printf '0')" || true

    contention=1; anchor=1
    _wg_contention && contention=0
    _wg_is_anchor  && anchor=0
    if [ "$contention" -eq 0 ] || [ "$anchor" -eq 0 ]; then
      reasons=""
      [ "$contention" -eq 0 ] && reasons="Another live session is already working in this working tree (${REAL_TOP}); you joined later."
      if [ "$anchor" -eq 0 ]; then
        ab="$(_wg_anchor_branch)"
        reasons="${reasons:+$reasons }You are on the anchor branch '${ab}' in the primary checkout while worktrees exist."
      fi
      banner="worktree-guard: ${reasons} Prefer a dedicated git worktree to avoid collisions. (mode=${mode}; set 'worktree_guard: off' in .ravenclaude/comfort-posture.yaml to silence"
      [ "$mode" = "block" ] && banner="${banner}; RC_WORKTREE_GUARD_ACK=1 overrides a mutating-op block"
      banner="${banner}.)"
      if command -v jq >/dev/null 2>&1; then
        jq -cn --arg c "$banner" \
          '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$c}}' 2>/dev/null || true
      fi
      rule="anchor-branch"; [ "$contention" -eq 0 ] && rule="contention-latecomer"
      _emit_hook_event "worktree-guard.sh" "warn" "SessionStart" "$REAL_TOP" "$rule" "0"
    fi
    exit 0
    ;;

  check)
    # PreToolUse. warn -> throttled stderr nudge, exit 0. block -> exit 2 DENY only
    # on a MUTATING op (never a read / git status / rcwt); RC_WORKTREE_GUARD_ACK=1 escapes.
    mkdir -p "$SESS_DIR" 2>/dev/null || exit 0
    _wg_heartbeat

    contention=1; anchor=1
    _wg_contention && contention=0
    _wg_is_anchor  && anchor=0
    if [ "$contention" -ne 0 ] && [ "$anchor" -ne 0 ]; then
      exit 0                     # not flagged -> silent allow
    fi

    flag_rule="anchor-branch"; [ "$contention" -eq 0 ] && flag_rule="contention-latecomer"

    if [ "$mode" = "block" ]; then
      if [ "${RC_WORKTREE_GUARD_ACK:-}" = "1" ]; then
        exit 0                   # explicit override
      fi
      if _wg_is_mutating; then
        msg="worktree-guard: DENIED — "
        if [ "$contention" -eq 0 ]; then
          msg="${msg}another live session is active in this working tree and you are the latecomer; "
        else
          ab="$(_wg_anchor_branch)"
          msg="${msg}you are on the anchor branch '${ab}' with worktrees present; "
        fi
        msg="${msg}a mutating op here risks a collision. Open your own git worktree, or set RC_WORKTREE_GUARD_ACK=1 to override, or set 'worktree_guard: warn' (or 'off') in .ravenclaude/comfort-posture.yaml."
        printf '%s\n' "$msg" >&2
        _emit_hook_event "worktree-guard.sh" "deny" "${tn:-Bash}" "${cmd:-$fp}" "$flag_rule" "2"
        exit 2
      fi
      exit 0                     # block mode, but a read / non-mutating op -> allow
    fi

    # warn mode: throttled stderr nudge (1/session/clause), never blocks.
    nudged=1
    if [ "$contention" -eq 0 ] && ! _wg_already_nudged "contention"; then
      printf '%s\n' "worktree-guard: another live Claude session is already working in this working tree (${REAL_TOP}). You joined later — coordinate, or open your own git worktree. (set 'worktree_guard: off' in .ravenclaude/comfort-posture.yaml to silence)" >&2
      nudged=0
    fi
    if [ "$anchor" -eq 0 ] && ! _wg_already_nudged "anchor"; then
      ab="$(_wg_anchor_branch)"
      printf '%s\n' "worktree-guard: you are on the anchor branch '${ab}' in the primary checkout while worktrees exist. Prefer a dedicated worktree. (worktree_guard: off to silence)" >&2
      nudged=0
    fi
    [ "$nudged" -eq 0 ] && _emit_hook_event "worktree-guard.sh" "warn" "${tn:-Bash}" "${cmd:-$fp}" "$flag_rule" "0"
    exit 0
    ;;

  status)
    # Read-only JSON snapshot (only --json is supported; it is also the default).
    is_anchor=false; _wg_is_anchor && is_anchor=true
    current_branch="$(wg_git rev-parse --abbrev-ref HEAD)"
    anchor_branch="$(_wg_anchor_branch)"

    sessions_json="[]"; live_count=0
    if command -v jq >/dev/null 2>&1; then
      for f in "$SESS_DIR"/*.json; do
        [ -f "$f" ] || continue
        s_sid="$(_wg_json_field "$f" session_id)"
        s_pid="$(_wg_json_field "$f" pid)"; case "$s_pid" in ''|*[!0-9]*) s_pid=0 ;; esac
        s_started="$(_wg_json_field "$f" started_at)"; case "$s_started" in ''|*[!0-9]*) s_started=0 ;; esac
        s_live=false
        if _wg_is_live "$f"; then s_live=true; live_count=$((live_count + 1)); fi
        entry="$(jq -cn --arg sid "$s_sid" --argjson pid "$s_pid" --argjson started "$s_started" --argjson live "$s_live" \
          '{session_id:$sid,pid:$pid,started_at:$started,live:$live}' 2>/dev/null)"
        [ -n "$entry" ] && sessions_json="$(printf '%s' "$sessions_json" | jq -c --argjson e "$entry" '. + [$e]' 2>/dev/null)"
      done
    fi
    contention_flag=false; [ "$live_count" -ge 2 ] && contention_flag=true

    if command -v jq >/dev/null 2>&1; then
      jq -cn \
        --arg pk "$PATH_KEY" --arg top "$REAL_TOP" --arg mode "$mode" \
        --argjson anchor "$is_anchor" --arg ab "$anchor_branch" --arg cur "$current_branch" \
        --argjson live "$live_count" --argjson contention "$contention_flag" \
        --argjson sessions "$sessions_json" \
        '{schema_version:1,path_key:$pk,toplevel:$top,mode:$mode,is_anchor:$anchor,anchor_branch:$ab,current_branch:$cur,live_sessions:$live,contention:$contention,sessions:$sessions}' \
        2>/dev/null || printf '{"schema_version":1,"path_key":"%s","is_anchor":%s,"live_sessions":%s}\n' "$PATH_KEY" "$is_anchor" "$live_count"
    else
      printf '{"schema_version":1,"path_key":"%s","toplevel":"%s","mode":"%s","is_anchor":%s,"anchor_branch":"%s","current_branch":"%s","live_sessions":%s,"contention":%s,"sessions":[]}\n' \
        "$PATH_KEY" "$REAL_TOP" "$mode" "$is_anchor" "$anchor_branch" "$current_branch" "$live_count" "$contention_flag"
    fi
    exit 0
    ;;

  *)
    printf '%s\n' "worktree-guard.sh: unknown subcommand '${SUBCMD}' (expected: register | check | status --json)" >&2
    exit 0
    ;;
esac
