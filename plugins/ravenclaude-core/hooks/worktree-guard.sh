#!/usr/bin/env bash
#
# rc-state-key: PATH_KEY = sha256(realpath of the git toplevel), then
#               "$GUARD_HOME/{sessions,throttle}/$PATH_KEY/<session_id>.json"
# rc-state-scope: worktree
# rc-state-rationale: PATH_KEY IS the per-worktree component — it hashes each
#   checkout's own toplevel, so two worktrees of one repo land in different
#   buckets by construction. That is required, because the question the guard
#   answers ("is another live session already on this working tree?") is only
#   meaningful within one checkout.
#   ⚑ The state root is $HOME/.ravenclaude/worktree-guard/, NOT .ravenclaude/runs/ —
#   deliberately, since it must be visible ACROSS checkouts to count siblings.
# rc-state-escape: comfort-posture — 'worktree_guard: off' silences CONTENTION /
#   ANCHOR (default warn). 'worktree_bound: off' silences FOREIGN-TREE (default
#   block). 'worktree_lease: off' silences the SESSION LEASE (default on).
#   All three are independent — ALL-off is the only full short-circuit, and the
#   lease deliberately survives the other two being off.
#
# worktree-guard.sh — portable worktree-hygiene guard (the CORE detection engine).
#
# Fires on FOUR locally-detectable conditions, per session, per working
# tree (a lone checkout with no sibling worktrees satisfies none, which is why
# "all repos, not opt-in" is safe):
#   (a) CONTENTION — another *live* Claude session is already operating in this
#       same working tree (same realpath(toplevel), same host). Only the LATECOMER
#       fires; the incumbent stays silent. Knob: worktree_guard (default warn).
#   (b) ANCHOR-WORK — this checkout is the repo's primary/anchor, worktrees already
#       exist, and HEAD is on the anchor branch. Knob: worktree_guard (default warn).
#   (c) FOREIGN-TREE — a Write/Edit/MultiEdit or a mutating git -C / GIT_WORK_TREE
#       / --work-tree whose target resolves under a *different* `git worktree list`
#       path than this session's realpath(toplevel). Sibling-worktree only — not a
#       general jail. Knob: worktree_bound (default block). Escape: RC_WORKTREE_BOUND_ACK=1.
#   (d) LEASE-HELD — another session holds a live claim on THIS worktree. (a)
#       only nudges; this DENIES. Goes stale after worktree_lease_idle_minutes
#       (default 20), after which the next session auto-commits the holder's
#       work as a wip(worktree-lease) checkpoint and takes over — never on the
#       anchor branch. Knob: worktree_lease (default on).
#
# Subcommands (selected by $1):
#   register       SessionStart. Records this session's own file, GC-sweeps the
#                  bucket, emits a banner (warn/block, when flagged). ALWAYS exit 0
#                  (a SessionStart hook can never block).
#   check          PreToolUse. FOREIGN-TREE (worktree_bound) is evaluated first and
#                  independently of CONTENTION/ANCHOR. bound=block -> exit 2 DENY
#                  on a foreign mutating op (sibling Write / git -C <sibling>).
#                  bound=warn -> stderr nudge, exit 0. Escape: RC_WORKTREE_BOUND_ACK=1.
#                  Then worktree_guard warn/block as before (CONTENTION/ANCHOR only).
#                  Reads / git status / rcwt / sibling Read are never denied.
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
# Knobs (independent):
#   worktree_guard: off|warn|block  DEFAULT warn if absent (CONTENTION/ANCHOR).
#   worktree_bound: off|warn|block  DEFAULT block if absent (FOREIGN-TREE).
#   worktree_lease: on|warn|off     DEFAULT on    if absent (SESSION LEASE).
#   worktree_lease_idle_minutes: N  DEFAULT 20    if absent.
# ALL-off short-circuits BEFORE any git shell-out. Either-on still shells out
# git so the live clause can fire (T13: guard=off + bound=block still denies).
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
# ⛔ BOUNDED ON PURPOSE — a bare `cat` here blocks FOREVER.
# `[ ! -t 0 ]` cannot tell "a payload is on its way" from "fd 0 is an open pipe
# nobody will ever write to". Both are simply not-a-tty, so the test that gates
# the read is satisfied in precisely the case that hangs, and the guard stalls
# every caller downstream of it — including audit-gates.sh Gate 140, which
# invokes this hook and inherits whatever stdin the harness was launched with.
# control: measured 2026-08-25 under a FIFO with a held-open writer — `status
# --json` and `check` both hung until killed at 6s, while a control script that
# reads no stdin exited in 1s under the identical fd. The differential is the
# read, not the environment.
# The bound covers the FIRST line only. Once a writer is demonstrably delivering,
# the remainder drains unbounded, so a large or slow payload is never truncated —
# the failure this fixes is "no writer at all", not "a slow writer".
payload=""
#
# ⛔ THE DEADLINE IS 10s, NOT 2s, AND THE NUMBER IS LOAD-BEARING.
# An empty payload carries no `tool_input`, so the payload-derived checks have
# nothing to test and the call is allowed through. That fail-open is PRE-EXISTING
# behaviour for an unreadable payload — but a deadline short enough for a merely
# SLOW writer to trip would convert it from "stdin was broken" into "the guard
# was disarmed under load", which is new and worse. 10s sits far above any real
# hook writer and is still finite.
# control: two-worktree fixture, `worktree_bound: block`, sibling Write —
#   full payload      -> exit 2 (the positive control: this fixture DOES deny)
#   empty payload     -> exit 0
#   writer 3s late, deadline 1s  -> exit 0   (disarmed)
#   writer 3s late, deadline 10s -> exit 2   (correct)
#   measured 2026-08-25; pinned by T18(d) in test-worktree-guard-core.sh.
_wg_read_payload() {
  local first="" rest="" t="${RC_GUARD_STDIN_TIMEOUT:-10}"
  # Non-numeric or absent -> the default. `read -t` rejects garbage outright, and
  # a guard must never die on a malformed knob.
  case "$t" in ''|*[!0-9]*) t=10 ;; esac
  # 0 is the documented escape back to the old unbounded read.
  if [ "$t" = "0" ]; then cat 2>/dev/null || printf ''; return 0; fi
  if IFS= read -r -t "$t" first; then
    rest="$(cat 2>/dev/null || printf '')"
    if [ -n "$rest" ]; then printf '%s\n%s' "$first" "$rest"; else printf '%s' "$first"; fi
  elif [ -n "$first" ]; then
    # EOF carrying a partial line — real payload that must not be dropped.
    printf '%s' "$first"
  else
    # Timed out with nothing. SAY SO. The call proceeds either way, so the only
    # thing left to protect is the operator's ability to tell a disarmed check
    # from a clean one. stderr reaches the terminal and the CI log but NOT the
    # model (see the hook-message-channels inventory entry) — the right audience
    # for a stdin fault.
    printf 'worktree-guard: no stdin payload within %ss — this call proceeds UNGUARDED (RC_GUARD_STDIN_TIMEOUT)\n' \
      "$t" >&2
  fi
}
[ -t 0 ] || payload="$(_wg_read_payload)"

# ── project dir (for the knob) + cwd (for git) ────────────────────────────────
cwd=""
if [ -n "$payload" ] && command -v jq >/dev/null 2>&1; then
  cwd="$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null || printf '')"
fi
[ -z "$cwd" ] && cwd="${CLAUDE_PROJECT_DIR:-$PWD}"
posture="${cwd}/.ravenclaude/comfort-posture.yaml"

# ── KNOBS (independent). sed/grep idiom, no PyYAML.
#    worktree_guard: off|warn|block  DEFAULT warn  (CONTENTION / ANCHOR)
#    worktree_bound: off|warn|block  DEFAULT block (FOREIGN-TREE)
#    worktree_lease: on|warn|off     DEFAULT on    (SESSION LEASE - one worktree,
#                                    one session. INDEPENDENT: the two knobs
#                                    above cannot silence it.)
#    worktree_lease_idle_minutes: N  DEFAULT 20    (idle holder -> the next
#                                    session auto-commits their work and takes over)
#    Both-off short-circuits BEFORE any git shell-out. status still reports. ─
mode="$(sed -n 's/^[[:space:]]*worktree_guard:[[:space:]]*\([A-Za-z]\{1,\}\).*/\1/p' "$posture" 2>/dev/null | head -1)"
[ -z "$mode" ] && mode="warn"
case "$mode" in off|warn|block) ;; *) mode="warn" ;; esac
bound="$(sed -n 's/^[[:space:]]*worktree_bound:[[:space:]]*\([A-Za-z]\{1,\}\).*/\1/p' "$posture" 2>/dev/null | head -1)"
[ -z "$bound" ] && bound="block"
case "$bound" in off|warn|block) ;; *) bound="block" ;; esac
# ⛔ The lease is a THIRD, INDEPENDENT knob and must not be switched off by the
# other two. Without this clause `worktree_guard: off` + `worktree_bound: off`
# short-circuits here — before the lease clause in `check` ever runs — so a
# consumer who silenced the two nudges would silently lose cross-session
# exclusion as well, with nothing saying so.
_wg_lease_knob="$(sed -n 's/^[[:space:]]*worktree_lease:[[:space:]]*\([A-Za-z]\{1,\}\).*/\1/p' "$posture" 2>/dev/null | head -1)"
case "$_wg_lease_knob" in on|warn|off) ;; *) _wg_lease_knob="on" ;; esac
if [ "$mode" = "off" ] && [ "$bound" = "off" ] && [ "$_wg_lease_knob" = "off" ]; then
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

# mtime (epoch seconds) of a file, portably. GNU `stat -c` is tried FIRST: on Linux it
# succeeds cleanly and short-circuits, whereas the BSD form `stat -f %m` on GNU means
# `--file-system` and prints a multi-line filesystem block to stdout (while still failing
# on the `%m` operand) — that garbage would fail the numeric guard in _wg_is_live and make
# every liveness check read not-live. On macOS `stat -c` fails with no stdout, so the BSD
# form runs. Leading-digits strip is a belt-and-suspenders against any stray trailing byte.
_wg_mtime() {
  local m
  m="$(stat -c %Y "$1" 2>/dev/null)"                    # GNU / Linux
  [ -n "$m" ] || m="$(stat -f %m "$1" 2>/dev/null)"     # BSD / macOS
  m="${m%%[!0-9]*}"
  printf '%s' "$m"
}

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
  case "$tn" in
    Write|Edit|MultiEdit)
      fp="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // ""' 2>/dev/null)"
      ;;
  esac
fi

_wg_path_under_tree() {
  local p="$1" d rp parent
  [ -n "$p" ] || return 1
  case "$p" in /*) d="$(dirname "$p")" ;; *) d="$cwd/$(dirname "$p")" ;; esac
  # The target's parent dir may not exist yet — creating a brand-new file in a
  # brand-new subdirectory is the normal case. `cd` into a non-existent dir fails,
  # so walk UP to the nearest EXISTING ancestor and resolve that. Without this,
  # a new-subdir Write resolves to "not under tree" and block mode wrongly ALLOWS
  # a mutating write it should deny (resolving the ancestor keeps the outside-tree
  # case correct too — an ancestor outside REAL_TOP still returns 1).
  while [ -n "$d" ] && [ ! -d "$d" ]; do
    parent="$(dirname "$d")"
    [ "$parent" = "$d" ] && break   # reached the filesystem root; stop
    d="$parent"
  done
  rp="$( cd "$d" 2>/dev/null && pwd -P )" || return 1
  [ -n "$rp" ] || return 1
  [ "$rp" = "$REAL_TOP" ] && return 0
  case "$rp/" in "$REAL_TOP"/*) return 0 ;; esac
  return 1
}

# A MUTATING op = a Write/Edit/MultiEdit under the tree, OR a Bash git mutation
# (commit/add/checkout/switch/merge/rebase/cherry-pick/revert/stash/rm/mv/
# reset/restore/clean). NEVER a read / git status / rcwt. reset/restore/clean
# discard or overwrite working-tree file contents — the same "yanks the tree out
# from under everyone" collision hazard the guard already flags for checkout — so
# they belong in this list (mirrors runaway-brake.sh's fuller mutating-token set).
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
    *"git rm "*|*"git mv "*|\
    *"git reset"*|*"git restore"*|*"git clean"*) return 0 ;;
  esac
  return 1
}

# Sibling worktree paths (realpath), one per line, excluding REAL_TOP.
_wg_sibling_list() {
  local out line p rp
  out="$(wg_git worktree list --porcelain)"
  [ -n "$out" ] || return 0
  printf '%s\n' "$out" | while IFS= read -r line; do
    case "$line" in
      "worktree "*)
        p="${line#worktree }"
        rp="$(_wg_realpath "$p")"
        [ -n "$rp" ] || rp="$p"
        [ "$rp" = "$REAL_TOP" ] && continue
        printf '%s\n' "$rp"
        ;;
    esac
  done
}

_wg_sibling_count() {
  local list n
  list="$(_wg_sibling_list)"
  [ -n "$list" ] || { printf '0'; return 0; }
  n="$(printf '%s\n' "$list" | grep -c .)"
  case "$n" in ''|*[!0-9]*) n=0 ;; esac
  printf '%s' "$n"
}

# Resolve a path for FOREIGN-TREE. An existing directory (git -C <worktree>)
# is itself. A file or a not-yet-created path walks to the nearest existing
# ancestor (same walk as _wg_path_under_tree).
_wg_resolve_existing() {
  local p="$1" d parent rp
  [ -n "$p" ] || return 1
  case "$p" in /*) d="$p" ;; *) d="$cwd/$p" ;; esac
  if [ ! -d "$d" ]; then
    d="$(dirname "$d")"
    while [ -n "$d" ] && [ ! -d "$d" ]; do
      parent="$(dirname "$d")"
      [ "$parent" = "$d" ] && break
      d="$parent"
    done
  fi
  rp="$( cd "$d" 2>/dev/null && pwd -P )" || return 1
  [ -n "$rp" ] || return 1
  printf '%s' "$rp"
}

# 0 if $1 resolves under a sibling worktree (not REAL_TOP, not /tmp, not elsewhere).
# Here-doc (not a pipe) so `return` is this function, not a subshell.
# ⛔ OWNERSHIP IS THE LONGEST MATCHING WORKTREE PREFIX — NOT "matches any sibling".
#
# This predicate used to walk the sibling list and return foreign on the FIRST
# prefix hit. That is wrong whenever one worktree path contains another, and this
# repo's own convention guarantees exactly that: worktrees live at
# `<primary>/.claude/worktrees/<name>` ("worktrees UNDER the repo, never /tmp").
# So from inside any linked worktree, the PRIMARY checkout is a sibling AND a
# path-prefix of you — and every write to your own files matched it and was
# reported foreign.
#
# Measured 2026-08-18: with cwd = a linked worktree and the target a file INSIDE
# that same worktree, the guard answered FOREIGN while naming that very worktree
# as "this tree". It was not a corner case — it was every mutating write in every
# linked worktree, which is why `worktree_bound` was set to `warn` on main with a
# comment saying the deadlock left "no legal place to edit". The guard had been
# switched off rather than fixed, so the isolation it advertises did not exist.
#
# Correct rule: a path belongs to the DEEPEST worktree that contains it. Compare
# that owner to this session's tree; only a different owner is foreign. Under the
# nested layout the deepest match for a file in your worktree is your worktree,
# so self-writes resolve to self and the primary no longer shadows its children.
_wg_owning_worktree() {
  local rp="$1" out
  out="$(wg_git worktree list --porcelain)"
  [ -n "$out" ] || return 1
  # Print every worktree that CONTAINS rp, then take the longest.
  #
  # `sort | tail -1` is the longest here, not merely the lexicographic max: every
  # candidate is a prefix of the same rp, so any two are prefix-comparable, and a
  # proper prefix always sorts BEFORE the longer string. Total order, so max ==
  # deepest. (Length-sorting would need `awk '{print length, $0}'`; this is the
  # same answer with fewer moving parts.)
  printf '%s\n' "$out" | while IFS= read -r line; do
    case "$line" in
      "worktree "*)
        p="${line#worktree }"
        cand="$(_wg_realpath "$p")"
        [ -n "$cand" ] || cand="$p"
        if [ "$rp" = "$cand" ]; then
          printf '%s\n' "$cand"
        else
          case "$rp/" in "$cand"/*) printf '%s\n' "$cand" ;; esac
        fi
        ;;
    esac
  done | sort | tail -1
}

# ═══ SESSION LEASE — one worktree, one session, with a stale fallback ═══════
#
# CONTENTION (above) only ever NUDGED: it told the latecomer someone else was
# here and let both proceed into the same tree. That is a report, not isolation.
# The lease is the enforcement: a session CLAIMS a worktree, and another
# session's mutating ops there are denied while the claim is live.
#
# ⛔ THE STALE FALLBACK IS THE WHOLE REASON THIS IS SAFE TO ENFORCE. A hard lock
# with no expiry strands the worktree the moment a session crashes, is killed, or
# is simply closed — and the next session has no sanctioned way in, so it learns
# to bypass the guard. That is how a lock becomes a thing people route around.
# So: after `worktree_lease_idle_minutes` (default 20) with no activity, the next
# session TAKES OVER — auto-committing the holder's work first so nothing is lost.
#
# Liveness is the lease file's MTIME, refreshed on every mutating op by the
# holder. Not a pid check: a pid says the process exists, not that it is still
# working this tree, and a reused pid says nothing at all.
LEASE_DIR="$GUARD_HOME/leases/$PATH_KEY"
LEASE_FILE="$LEASE_DIR/lease.json"

# ⛔ These `case`s are written MULTI-LINE with an explicit `*)` arm on its own
# line, on purpose. `check-verdict-default-nonpermissive.py` scans from the line
# AFTER the `case` for a default arm, so a one-liner hides its `*)` from the
# check and is reported as failing open. The value here is a verdict about
# whether to enforce, so the shape the checker wants is the shape it should
# have: an unrecognised knob value must land on a NAMED default, never fall out.
_wg_lease_mode() {
  local v
  v="$(sed -n 's/^[[:space:]]*worktree_lease:[[:space:]]*\([A-Za-z]\{1,\}\).*/\1/p' "$posture" 2>/dev/null | head -1)"
  case "$v" in
    on|off|warn) printf '%s' "$v" ;;
    *) printf 'on' ;;          # unset or garbage -> ENFORCE (the safe direction)
  esac
}

_wg_lease_idle_secs() {
  local v
  v="$(sed -n 's/^[[:space:]]*worktree_lease_idle_minutes:[[:space:]]*\([0-9]\{1,\}\).*/\1/p' "$posture" 2>/dev/null | head -1)"
  case "$v" in
    ''|*[!0-9]*) v=20 ;;       # unset or non-numeric -> the documented default
    *) ;;                      # a valid number is used as-is
  esac
  [ "$v" -lt 1 ] 2>/dev/null && v=1
  printf '%s' "$(( v * 60 ))"
}

_wg_lease_holder() { _wg_json_field "$LEASE_FILE" session_id 2>/dev/null || printf ''; }

_wg_lease_write() {
  mkdir -p "$LEASE_DIR" 2>/dev/null || return 1
  printf '{"session_id":"%s","pid":"%s","tree":"%s","claimed_at":"%s"}\n' \
    "$session" "$SESSION_PID" "$REAL_TOP" "$(date +%s 2>/dev/null || printf '0')" \
    > "$LEASE_FILE" 2>/dev/null || return 1
  return 0
}

# Idle seconds since the holder last touched the lease. Empty => unknown, and an
# unknown age must NEVER be treated as stale (that would hand the tree away from
# a session that is actively working it).
_wg_lease_idle() {
  local m now
  m="$(_wg_mtime "$LEASE_FILE" 2>/dev/null)" || return 1
  [ -n "$m" ] || return 1
  now="$(date +%s 2>/dev/null)" || return 1
  case "$m" in ''|*[!0-9]*) return 1 ;; esac
  printf '%s' "$(( now - m ))"
}

# Auto-checkin: commit the stale holder's work so the takeover loses nothing.
# Owner ruling 2026-08-18: tracked AND untracked (`git add -A`). .gitignore is
# still honoured, so `.ravenclaude/runs/` scratch is not swept.
#
# ⛔ REFUSES ON THE ANCHOR BRANCH. This repo keeps main as the shared anchor and
# has a dedicated check against working on it; auto-committing a stranded tree
# there would be the guard creating exactly the mess it exists to prevent. On the
# anchor we report and decline the takeover rather than commit.
_wg_lease_autocheckin() {
  local holder="$1" idle="$2" branch mins
  # ⛔ ORDER IS LOAD-BEARING — this check MUST precede the anchor refusal below.
  # Nothing to check in is a clean takeover, not a failure, and that is true on
  # EVERY branch INCLUDING the anchor: there is no work to auto-checkin, so the
  # hazard the refusal exists to prevent cannot arise.
  #
  # It used to sit AFTER the `case`, which made the refusal UNCONDITIONAL on the
  # anchor. MEASURED 2026-08-24: a CLEAN anchor (one untracked file), a holder
  # session dead 4.4 days, and every mutating op still denied — for hours, across
  # two sessions. The denial tells you to "Land or move that work by hand, then
  # retry", but the retry never reached the line that checks whether you landed
  # it, so the instruction was unsatisfiable BY CONSTRUCTION. Because the house
  # convention keeps the anchor checkout on `main` permanently, that stranded the
  # anchor for good rather than transiently.
  #
  # The safety property is UNCHANGED: an anchor with real work still refuses,
  # because this returns only when the tree is clean. Only the vacuous case moves.
  [ -z "$(wg_git status --porcelain 2>/dev/null)" ] && return 0
  branch="$(wg_git rev-parse --abbrev-ref HEAD 2>/dev/null || printf '')"
  case "$branch" in
    main|master|HEAD|"")
      printf '%s\n' "worktree-guard: stale lease (holder ${holder}, idle $(( idle / 60 ))m) but HEAD is '${branch:-detached}' — REFUSING to auto-commit the anchor. Land or move that work by hand, then retry." >&2
      return 1
      ;;
  esac
  wg_git add -A >/dev/null 2>&1 || return 1
  mins="$(( idle / 60 ))"
  wg_git commit -q -m "wip(worktree-lease): auto-checkin of a stale worktree

Session ${holder} held this worktree and went idle for ${mins}m, so the lease
expired and another session took it over. This commit is that session's work,
committed automatically so the takeover could not lose it.

Tracked AND untracked files are included (.gitignore still applies). Reword,
amend or reset this commit freely — it is a checkpoint, not a decision." \
    >/dev/null 2>&1 || return 1
  return 0
}

# Which operations the lease governs: a mutating op aimed at THIS tree. Foreign
# targets are already handled by the FOREIGN-TREE clause above, and a read is
# never contended.
_wg_lease_should_enforce() {
  case "$tn" in
    Write|Edit|MultiEdit)
      [ -n "$fp" ] || return 1
      # ⛔ ENFORCE ONLY INSIDE THIS TREE. This used to read
      # `_wg_is_foreign "$fp" && return 1`, which skips only a SIBLING-owned path
      # — so a path owned by NO worktree came back "not foreign" and was enforced.
      # The lease exists to stop a second writer colliding on THIS working tree; a
      # file outside every worktree cannot cause that collision, so denying it buys
      # nothing and turns the lease into precisely the "general jail" that
      # _wg_is_foreign's own comment says this predicate must never be.
      #
      # control 2026-08-24, observed twice in one session: with a lease held on
      # ~/RavenClaude, an Edit to ~/.claude/projects/.../memory/*.md — a path in no
      # git worktree at all — was DENIED with the lease message, while the same
      # content written via a Bash heredoc went through untouched. So the clause
      # blocked the honest tool and not the workaround, which is the shape that
      # teaches tunnelling rather than preventing collisions.
      _wg_is_in_this_tree "$fp" || return 1
      return 0
      ;;
    Bash) _wg_bash_is_mutating || return 1; return 0 ;;
    *) return 1 ;;
  esac
}

_wg_is_foreign() {
  local target="$1" rp owner
  [ -n "$target" ] || return 1
  rp="$(_wg_resolve_existing "$target")" || return 1
  owner="$(_wg_owning_worktree "$rp")"
  # No worktree owns it (outside the repo entirely) -> not a SIBLING problem.
  # This predicate is scoped to sibling worktrees, never a general jail.
  [ -n "$owner" ] || return 1
  [ "$owner" = "$REAL_TOP" ] && return 1
  return 0
}

# Positive counterpart to _wg_is_foreign. "Not foreign" is NOT the same as "mine":
# a path owned by no worktree satisfies the first and not the second, and conflating
# them is what made the lease enforce on files outside every repo. Ask the question
# you mean — is this target inside THIS working tree?
_wg_is_in_this_tree() {
  local target="$1" rp
  [ -n "$target" ] || return 1
  rp="$(_wg_resolve_existing "$target")" || return 1
  [ "$(_wg_owning_worktree "$rp")" = "$REAL_TOP" ]
}

# Candidate dirs from a Bash command: -C, --work-tree, --git-dir, GIT_WORK_TREE, GIT_DIR, cd.
_wg_bash_targets() {
  local tok prev=""
  [ -n "$cmd" ] || return 0
  # shellcheck disable=SC2086
  for tok in $cmd; do
    tok="${tok#\"}"; tok="${tok%\"}"
    tok="${tok#\'}"; tok="${tok%\'}"
    case "$tok" in
      GIT_WORK_TREE=*) printf '%s\n' "${tok#GIT_WORK_TREE=}"; prev=""; continue ;;
      GIT_DIR=*)       printf '%s\n' "${tok#GIT_DIR=}"; prev=""; continue ;;
      --work-tree=*)   printf '%s\n' "${tok#--work-tree=}"; prev=""; continue ;;
      --git-dir=*)     printf '%s\n' "${tok#--git-dir=}"; prev=""; continue ;;
      -C|--work-tree|--git-dir) prev="$tok"; continue ;;
      cd) prev="cd"; continue ;;
    esac
    case "$prev" in
      -C|--work-tree|--git-dir|cd) printf '%s\n' "$tok"; prev="" ;;
      *) prev="" ;;
    esac
  done
}

_wg_bash_is_mutating() {
  [ -n "$cmd" ] || return 1
  # Must look like a git invocation. `git -C <dir> commit` does NOT contain
  # the substring "git commit", so match the subcommand as its own token too.
  case " $cmd " in
    *" git "*|*"git "*|*"git") : ;;
    *) return 1 ;;
  esac
  case " $cmd " in
    *"git commit"*|*"git add"*|*"git checkout"*|*"git switch"*|*"git merge"*|\
    *"git rebase"*|*"git cherry-pick"*|*"git revert"*|*"git stash"*|\
    *"git rm "*|*"git mv "*|\
    *"git reset"*|*"git restore"*|*"git clean"*|\
    *" commit "*|*" add "*|*" checkout "*|*" switch "*|*" merge "*|\
    *" rebase "*|*" cherry-pick "*|*" revert "*|*" stash "*|\
    *" rm "*|*" mv "*|*" reset "*|*" restore "*|*" clean "*) return 0 ;;
  esac
  return 1
}

# FOREIGN-TREE deny class (inverts the _wg_is_mutating hole): sibling Write, or
# mutating git whose -C / GIT_WORK_TREE / --work-tree target is a sibling.
# Unknown tool + no resolvable path -> allow (fail-open). Sibling Read -> allow.
_wg_bound_should_deny() {
  local t
  case "$tn" in
    Write|Edit|MultiEdit)
      [ -n "$fp" ] || return 1
      _wg_is_foreign "$fp"
      return $?
      ;;
    Bash)
      _wg_bash_is_mutating || return 1
      for t in $(_wg_bash_targets); do
        [ -n "$t" ] || continue
        _wg_is_foreign "$t" && return 0
      done
      return 1
      ;;
    *) return 1 ;;
  esac
}

_wg_lane_task() {
  local f="$REAL_TOP/.ravenclaude/lane.md"
  [ -f "$f" ] || return 0
  sed -n 's/^[[:space:]]*task:[[:space:]]*//p' "$f" 2>/dev/null | head -1
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
    # SessionStart: cannot block. Registry write is gated on worktree_guard != off
    # (T7: guard=off writes nothing). Lane pin is gated on worktree_bound != off
    # and sibling count > 0 — no registry mkdir (so T7 still holds when bound=block).
    ctx=""
    if [ "$mode" != "off" ]; then
      mkdir -p "$SESS_DIR" 2>/dev/null || true
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
        ctx="worktree-guard: ${reasons} Prefer a dedicated git worktree to avoid collisions. (mode=${mode}; set 'worktree_guard: off' in .ravenclaude/comfort-posture.yaml to silence"
        [ "$mode" = "block" ] && ctx="${ctx}; RC_WORKTREE_GUARD_ACK=1 overrides a mutating-op block"
        ctx="${ctx}.)"
        rule="anchor-branch"; [ "$contention" -eq 0 ] && rule="contention-latecomer"
        _emit_hook_event "worktree-guard.sh" "warn" "SessionStart" "$REAL_TOP" "$rule" "0"
      fi
    fi

    if [ "$bound" != "off" ]; then
      sibs_n="$(_wg_sibling_count)"
      case "$sibs_n" in ''|*[!0-9]*) sibs_n=0 ;; esac
      if [ "$sibs_n" -ge 1 ]; then
        host="$(hostname 2>/dev/null || printf 'unknown')"
        br="$(wg_git rev-parse --abbrev-ref HEAD)"
        [ -n "$br" ] || br=""
        lane="LANE: toplevel=${REAL_TOP} branch=${br} host=${host} siblings=${sibs_n}"
        task="$(_wg_lane_task)"
        [ -n "$task" ] && lane="${lane} task=${task}"
        ctx="${ctx:+$ctx }$lane"
      fi
    fi

    if [ -n "$ctx" ] && command -v jq >/dev/null 2>&1; then
      jq -cn --arg c "$ctx" \
        '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$c}}' 2>/dev/null || true
    fi
    exit 0
    ;;

  check)
    # ── SESSION LEASE (before FOREIGN/CONTENTION: it answers "may I write HERE
    # at all", which precedes "is this the right tree"). Fail-OPEN throughout —
    # a lease bug must never be able to brick a session, so every unknown
    # (no session id, unreadable lease, unknown age, failed write) allows.
    if [ "$(_wg_lease_mode)" != "off" ] && [ "$session" != "unknown" ] \
       && _wg_lease_should_enforce; then
      _wg_holder="$(_wg_lease_holder)"
      if [ -z "$_wg_holder" ] || [ "$_wg_holder" = "$session" ]; then
        _wg_lease_write || true          # claim / heartbeat; failure is not fatal
      else
        _wg_idle="$(_wg_lease_idle || printf '')"
        _wg_ttl="$(_wg_lease_idle_secs)"
        if [ -n "$_wg_idle" ] && [ "$_wg_idle" -ge "$_wg_ttl" ] 2>/dev/null; then
          # STALE -> take over, but only after the holder's work is safely in.
          if _wg_lease_autocheckin "$_wg_holder" "$_wg_idle"; then
            _wg_lease_write || true
            printf '%s\n' "worktree-guard: took over a stale worktree lease from session ${_wg_holder} (idle $(( _wg_idle / 60 ))m). Their work was auto-committed as a wip(worktree-lease) checkpoint first." >&2
            _emit_hook_event "worktree-guard.sh" "warn" "${tn:-Bash}" "" "lease-takeover" "0"
          elif [ "$(_wg_lease_mode)" = "warn" ]; then
            : # advisory mode: the refusal was reported, proceed anyway
          else
            _emit_hook_event "worktree-guard.sh" "deny" "${tn:-Bash}" "" "lease-stale-anchor" "2"
            exit 2
          fi
        elif [ "$(_wg_lease_mode)" = "warn" ]; then
          printf '%s\n' "worktree-guard: session ${_wg_holder} holds this worktree (idle $(( ${_wg_idle:-0} / 60 ))m of ${_wg_ttl} s). Proceeding because worktree_lease is 'warn'." >&2
        else
          printf '%s\n' "worktree-guard: DENIED — session ${_wg_holder} holds a live lease on ${REAL_TOP} (idle $(( ${_wg_idle:-0} / 60 ))m; it expires at $(( _wg_ttl / 60 ))m). Open your own worktree (rcwt / forge-worktree.sh), or wait for the lease to go stale — the next session then takes over automatically and their work is auto-committed first. Set 'worktree_lease: off' in .ravenclaude/comfort-posture.yaml to disable." >&2
          _emit_hook_event "worktree-guard.sh" "deny" "${tn:-Bash}" "" "lease-held" "2"
          exit 2
        fi
      fi
    fi

    # PreToolUse. FOREIGN-TREE first (independent of CONTENTION/ANCHOR), then
    # the existing two-writers / anchor clauses if worktree_guard != off.
    if [ "$bound" != "off" ] && _wg_bound_should_deny; then
      if [ "${RC_WORKTREE_BOUND_ACK:-}" = "1" ]; then
        : # explicit override — fall through to CONTENTION/ANCHOR
      elif [ "$bound" = "block" ]; then
        printf '%s\n' "worktree-guard: DENIED — FOREIGN-TREE: the target resolves under a sibling worktree, not ${REAL_TOP}. Stay in this tree, or set RC_WORKTREE_BOUND_ACK=1 to override, or set 'worktree_bound: warn' (or 'off') in .ravenclaude/comfort-posture.yaml." >&2
        _emit_hook_event "worktree-guard.sh" "deny" "${tn:-Bash}" "${cmd:-$fp}" "foreign-tree" "2"
        exit 2
      else
        # warn: throttled stderr nudge, never blocks this clause.
        if ! _wg_already_nudged "foreign"; then
          printf '%s\n' "worktree-guard: FOREIGN — the target resolves under a sibling worktree, not ${REAL_TOP}. Stay in this tree. (worktree_bound: off to silence)" >&2
          _emit_hook_event "worktree-guard.sh" "warn" "${tn:-Bash}" "${cmd:-$fp}" "foreign-tree" "0"
        fi
      fi
    fi

    if [ "$mode" = "off" ]; then
      exit 0                     # CONTENTION/ANCHOR silenced; FOREIGN-TREE already handled
    fi

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
        msg="${msg}a mutating op here risks a collision. Open your own git worktree, or set RC_WORKTREE_GUARD_ACK=1 to override THIS check (it does not release a held SESSION LEASE — that denial names its own escapes), or set 'worktree_guard: warn' (or 'off') in .ravenclaude/comfort-posture.yaml."
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

    sibs_n="$(_wg_sibling_count)"
    case "$sibs_n" in ''|*[!0-9]*) sibs_n=0 ;; esac
    foreign_flag=false
    if [ -n "$fp" ] && _wg_is_foreign "$fp"; then foreign_flag=true; fi

    if command -v jq >/dev/null 2>&1; then
      jq -cn \
        --arg pk "$PATH_KEY" --arg top "$REAL_TOP" --arg mode "$mode" \
        --arg bound "$bound" \
        --argjson anchor "$is_anchor" --arg ab "$anchor_branch" --arg cur "$current_branch" \
        --argjson live "$live_count" --argjson contention "$contention_flag" \
        --argjson foreign "$foreign_flag" --argjson siblings "$sibs_n" \
        --argjson sessions "$sessions_json" \
        '{schema_version:1,path_key:$pk,toplevel:$top,mode:$mode,worktree_bound:$bound,is_anchor:$anchor,anchor_branch:$ab,current_branch:$cur,live_sessions:$live,contention:$contention,foreign:$foreign,siblings:$siblings,sessions:$sessions}' \
        2>/dev/null || printf '{"schema_version":1,"path_key":"%s","is_anchor":%s,"live_sessions":%s}\n' "$PATH_KEY" "$is_anchor" "$live_count"
    else
      printf '{"schema_version":1,"path_key":"%s","toplevel":"%s","mode":"%s","worktree_bound":"%s","is_anchor":%s,"anchor_branch":"%s","current_branch":"%s","live_sessions":%s,"contention":%s,"foreign":%s,"siblings":%s,"sessions":[]}\n' \
        "$PATH_KEY" "$REAL_TOP" "$mode" "$bound" "$is_anchor" "$anchor_branch" "$current_branch" "$live_count" "$contention_flag" "$foreign_flag" "$sibs_n"
    fi
    exit 0
    ;;

  *)
    printf '%s\n' "worktree-guard.sh: unknown subcommand '${SUBCMD}' (expected: register | check | status --json)" >&2
    exit 0
    ;;
esac
