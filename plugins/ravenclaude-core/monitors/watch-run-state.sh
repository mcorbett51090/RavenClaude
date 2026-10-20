#!/usr/bin/env bash
# watch-run-state.sh
# Reactive run-state MONITOR for ravenclaude-core (FORGE roadmap #7).
#
# WHAT IT IS
#   The *push* complement to the read-only Heimdall / Víðarr dashboard tabs.
#   Those tabs are pull surfaces — you open them and read what already happened.
#   This monitor streams the same guardrail/run-state signals to Claude Code as
#   native notifications, so the agent reacts to a deny/warn *as it lands* during
#   a multi-agent run, without the human asking it to go look.
#
#   It is declared in monitors/monitors.json with `when: "on-skill-invoke:spawn-team"`
#   (NOT `when: always`). It starts the first time the `spawn-team` skill is
#   dispatched — i.e. exactly when multiple agents are running and guardrails
#   matter most — and stays up for the rest of the session. Scoping it to the
#   skill invoke is the cost bound: it never runs during ordinary single-agent
#   sessions.
#
# WHAT IT EMITS  (the safety rule — read before changing the emit line)
#   For each NEW line appended to the session's hook-events.jsonl it prints ONE
#   line of DERIVED labels only — the whitelisted fields:
#       verdict, hook (basename), tool, rule
#   It NEVER echoes raw event content: not the `path` field (a file path or the
#   raw command string), not `ts`, not `session_id`, nothing free-form. This
#   mirrors the capability-banner injection-safety invariant — a hostile path or
#   command captured in a deny event must not flow back into the session as text
#   a downstream model could read as instructions. Every stdout line of a monitor
#   becomes a Claude notification, so the emit surface is an injection surface;
#   keeping it to a fixed vocabulary of derived labels is the defense.
#
#   Example emitted line:
#       ⚠ guard-destructive.sh denied Bash (rule: destructive-pattern)
#
# READ-ONLY
#   The monitor only tails and summarizes. It writes nothing to the substrate,
#   mutates no run state, runs no tool. It is a pure reader, like Heimdall.
#
# FAIL-SAFE (the red-team's `tail -F` empty-glob fragility, handled)
#   * No .ravenclaude/runs/ dir yet            -> sleep and re-poll, never crash.
#   * runs/ exists but no hook-events.jsonl    -> sleep and re-poll for one.
#   * The active jsonl rotates (new run dir)   -> re-resolve the newest file.
#   We deliberately do NOT `tail -F <glob>`: a bare glob that matches nothing
#   makes `tail -F` exit immediately, and the monitor host would crash-loop
#   restarting it (a notification-spam / cost problem the red-team flagged).
#   Instead we resolve the single newest jsonl ourselves, tail that one file,
#   and when it disappears or a newer run dir appears we re-resolve — bounded,
#   no busy-spin, no restart storm.
#
# WHICH LOG, AND FROM WHICH LINE
#   * When $CLAUDE_SESSION_ID is set we follow ONLY runs/<that id>/ (sanitized
#     the way _emit-event.sh names the dir). Picking the newest log by mtime
#     across ALL sessions made two concurrent sessions in one checkout flap:
#     every switch restarted tail at EOF, dropping events, and the
#     notifications mixed sessions. Without the id we keep newest-by-mtime.
#   * Only the log that already exists when the monitor starts is joined at its
#     end (its backlog is history). A log first seen later is read from line 1:
#     a session's log is created BY its first event, so starting at EOF lost
#     the first deny/warn of every new log. A log we already followed once is
#     rejoined at its end, so a switch back never replays it.
#
# CLAUDE-CODE-ONLY
#   Plugin monitors are a Claude Code component (v2.1.105+) and run only in
#   interactive CLI sessions on hosts where the Monitor tool is available. There
#   is no GitHub Copilot CLI equivalent, so under Copilot this component simply
#   does not load — the read-only Heimdall/Víðarr tabs remain the pull surface
#   there. See knowledge/run-state-monitor.md.
#
# CONTRACT NOTE
#   Monitors run from the session working directory. We resolve the project root
#   from $CLAUDE_PROJECT_DIR when set (the canonical substrate anchor used by
#   _emit-event.sh), falling back to $PWD.

set -euo pipefail

# --- tunables (env-overridable; sensible defaults) --------------------------
POLL_SECONDS="${RC_MONITOR_POLL_SECONDS:-5}"   # re-resolve cadence when idle
# Guard against a hostile/absurd override; keep the poll bounded and positive.
case "$POLL_SECONDS" in
  '' | *[!0-9]*) POLL_SECONDS=5 ;;
esac
[ "$POLL_SECONDS" -lt 1 ] && POLL_SECONDS=5

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
RUNS_DIR="$PROJECT_DIR/.ravenclaude/runs"

# --- helpers ----------------------------------------------------------------

# The run-dir name hooks use for $CLAUDE_SESSION_ID (same rule as
# _ee_sanitize_session in hooks/_emit-event.sh). Empty when the id is unset.
session_run_name() {
  [ -n "${CLAUDE_SESSION_ID:-}" ] || return 0
  local s
  s="$(printf '%s' "$CLAUDE_SESSION_ID" | tr -dc 'A-Za-z0-9._-' | cut -c1-128)"
  case "$s" in . | .. | "") s="unknown" ;; esac
  printf '%s\n' "$s"
}

# Print the hook-events.jsonl to follow, or empty: this session's own log when
# $CLAUDE_SESSION_ID is set (never another session's), else the single newest
# one under .ravenclaude/runs/ — most-recently-modified, so a fresh run dir's
# log wins automatically.
newest_log() {
  [ -d "$RUNS_DIR" ] || return 0
  local _sess
  _sess="$(session_run_name)"
  if [ -n "$_sess" ]; then
    [ -f "$RUNS_DIR/$_sess/hook-events.jsonl" ] && printf '%s\n' "$RUNS_DIR/$_sess/hook-events.jsonl"
    return 0
  fi
  # Enumerate with -print0 (space-safe) and pick the newest by mtime OURSELVES.
  # We deliberately do NOT use `find -printf` — that is a GNU-find extension;
  # stock macOS/BSD find exits with "unknown primary -printf", the 2>/dev/null
  # swallows it, and the pipeline yields empty -> the monitor idle-polls forever
  # and never emits a notification (silent, every macOS session — the exact
  # macOS-door failure class the repo has closed elsewhere). mtime is read by ONE
  # `stat` over every candidate (xargs batches the list), keeping the portable
  # GNU `-c '%Y %n'` / BSD `-f '%m %N'` split: a fork per run dir cost ~6 s per
  # call at 1,500 run dirs, and .ravenclaude/runs/ is never pruned. awk keeps the
  # first strictly-newest line and reads all of its input (no early exit, so no
  # SIGPIPE under pipefail). bash-3.2-safe: no mapfile / assoc arrays / globstar.
  local _flag="-f" _fmt="%m %N"
  if stat -c '%Y' "$RUNS_DIR" >/dev/null 2>&1; then _flag="-c" _fmt="%Y %n"; fi  # noport: probe only; BSD -f is the default
  find "$RUNS_DIR" -maxdepth 2 -name 'hook-events.jsonl' -type f -print0 2>/dev/null |
    xargs -0 stat "$_flag" "$_fmt" 2>/dev/null |
    awk '{ mt = $1 + 0; if (mt > best) { best = mt; line = $0 } }
      END { if (line != "") { sub(/^[0-9]+ /, "", line); print line } }'
}

# Derive and print ONE notification line from ONE jsonl line.
# Whitelist: verdict, hook, tool, rule. Never path/ts/session_id/raw content.
emit_derived() {
  local json_line="$1"
  [ -n "$json_line" ] || return 0

  local verdict hook tool rule
  if command -v jq >/dev/null 2>&1; then
    # `// empty` => missing fields drop out; we never interpolate `path`.
    verdict="$(printf '%s' "$json_line" | jq -r '.verdict // empty' 2>/dev/null || true)"
    hook="$(printf '%s' "$json_line" | jq -r '.hook // empty' 2>/dev/null || true)"
    tool="$(printf '%s' "$json_line" | jq -r '.tool // empty' 2>/dev/null || true)"
    rule="$(printf '%s' "$json_line" | jq -r '.rule // empty' 2>/dev/null || true)"
  else
    # No jq: a deliberately strict, whitelist-only extractor. We pull only the
    # four known scalar fields by name with a narrow regex and ignore anything
    # else on the line — so even without jq we never surface `path`/content.
    verdict="$(printf '%s' "$json_line" | grep -oE '"verdict"[[:space:]]*:[[:space:]]*"[^"]*"' | head -n1 | sed -E 's/.*:[[:space:]]*"([^"]*)".*/\1/' || true)"
    hook="$(printf '%s' "$json_line" | grep -oE '"hook"[[:space:]]*:[[:space:]]*"[^"]*"' | head -n1 | sed -E 's/.*:[[:space:]]*"([^"]*)".*/\1/' || true)"
    tool="$(printf '%s' "$json_line" | grep -oE '"tool"[[:space:]]*:[[:space:]]*"[^"]*"' | head -n1 | sed -E 's/.*:[[:space:]]*"([^"]*)".*/\1/' || true)"
    rule="$(printf '%s' "$json_line" | grep -oE '"rule"[[:space:]]*:[[:space:]]*"[^"]*"' | head -n1 | sed -E 's/.*:[[:space:]]*"([^"]*)".*/\1/' || true)"
  fi

  # Belt-and-suspenders: strip any newline/CR a field might carry so one event
  # is always exactly one notification line (and can't smuggle a second line).
  verdict="$(printf '%s' "$verdict" | tr -d '\r\n')"
  hook="$(printf '%s' "$hook" | tr -d '\r\n')"
  tool="$(printf '%s' "$tool" | tr -d '\r\n')"
  rule="$(printf '%s' "$rule" | tr -d '\r\n')"

  # A line with no recognizable verdict isn't ours to summarize — skip silently.
  [ -n "$verdict" ] || return 0

  # Fixed-vocabulary glyph + verb per verdict. No free-form content.
  local glyph verb
  case "$verdict" in
    deny) glyph="⚠"; verb="denied" ;;
    warn) glyph="•"; verb="warned on" ;;
    allow) glyph="✓"; verb="allowed" ;;
    *) glyph="•"; verb="$verdict" ;;
  esac

  local line="$glyph ${hook:-hook} $verb ${tool:-tool}"
  [ -n "$rule" ] && line="$line (rule: $rule)"
  printf '%s\n' "$line"
}

# True when $1 is one of the newline-separated lines of $2 (no pipe, so no
# SIGPIPE-under-pipefail false negative on a long list).
_line_in() {
  local _l
  while IFS= read -r _l; do
    [ "$_l" = "$1" ] && return 0
  done <<<"$2"
  return 1
}

# --- main loop --------------------------------------------------------------
# Resolve the log, tail it (from its end if it existed at startup, so the
# backlog is not replayed; from line 1 if it appeared later), and when it
# vanishes / is superseded by a newer run dir, re-resolve. tail's own --pid isn't available portably, so
# we bound each tail by re-checking the newest log on a poll and restarting the
# tail if it changed. Fail-safe at every step: a missing dir/file just sleeps.
#
# Wrapped in a function + a sourced-guard at the bottom so the helpers above
# (newest_log / emit_derived) can be sourced for testing WITHOUT entering the
# infinite follow loop. The monitor host executes the script directly, so the
# guard runs the loop in production exactly as before.

_run_monitor_loop() {
  local current="" first_pass=1 followed="" tail_from
  while true; do
    local log
    log="$(newest_log || true)"

    if [ -z "$log" ] || [ ! -f "$log" ]; then
      # No runs dir yet, or no jsonl yet, or it disappeared. Idle-poll; do NOT
      # tail a glob (that crash-loops on an empty match). Just wait and re-check.
      current=""
      first_pass=0
      sleep "$POLL_SECONDS"
      continue
    fi

    if [ "$log" != "$current" ]; then
      # A new (or first) log to follow. The log present at startup, and any log
      # already followed once, are joined at end-of-file; a log first seen
      # after startup is read from line 1, because its first line is the event
      # that created it. `tail -F` (capital) re-opens on truncate/rotate of THIS
      # one named file; it does not exit on a missing glob because we always
      # hand it a concrete, existing path.
      if _line_in "$log" "$followed"; then
        tail_from="0"
      else
        if [ "$first_pass" -eq 1 ]; then tail_from="0"; else tail_from="+1"; fi
        followed="$followed
$log"
      fi
      first_pass=0
      current="$log"
      # Stream until either the file is gone or a newer run dir appears, then
      # break out to re-resolve. We background the tail and poll alongside it so
      # a rotation is picked up without leaking the tail process.
      local tail_pid newer
      # Wrap `tail -F | while read` in its OWN subshell group ( ... ) & so we
      # have one PID that owns the whole pipeline's process group. Backgrounding
      # the bare pipeline (no outer parens) makes $! the PID of the LAST command
      # in the pipe — the `while read` subshell, NOT `tail` — so `kill "$tail_pid"`
      # would only kill the reader loop and orphan the real `tail -F` process,
      # which keeps following the now-superseded log file forever: one leaked
      # `tail -F` per run-dir rotation for the life of the session.
      ( tail -n "$tail_from" -F "$log" 2>/dev/null | while IFS= read -r jsonl_line; do
          emit_derived "$jsonl_line" || true
        done ) &
      tail_pid=$!

      # Watch for supersession: a newer run dir's log, or this log disappearing.
      while kill -0 "$tail_pid" 2>/dev/null; do
        sleep "$POLL_SECONDS"
        newer="$(newest_log || true)"
        if [ "$newer" != "$current" ] || [ ! -f "$current" ]; then
          # Stop following the stale file; the outer loop re-resolves.
          # Kill the subshell's CHILDREN first (this is where the real `tail -F`
          # process lives), then the subshell itself — otherwise `tail -F` is
          # orphaned and never reaped (see the comment above the subshell wrap).
          pkill -P "$tail_pid" 2>/dev/null || true
          kill "$tail_pid" 2>/dev/null || true
          wait "$tail_pid" 2>/dev/null || true
          break
        fi
      done
      # Loop back around: outer while re-resolves newest_log.
    else
      sleep "$POLL_SECONDS"
    fi
  done
}

# --- sourced-guard ----------------------------------------------------------
# Run the follow loop ONLY when executed directly (the monitor host does this).
# When sourced (e.g. by a test that wants newest_log / emit_derived in isolation),
# define the functions and return without entering the infinite loop.
if [ "${BASH_SOURCE[0]:-$0}" = "${0}" ]; then
  _run_monitor_loop
fi
