#!/usr/bin/env bash
# dashboard-autostart.sh — SessionStart: optionally bring the comfort-posture
# dashboard up (and, optionally, already open in a browser tab) the moment a
# session starts.
#
# WHY THIS EXISTS. The only auto-launch RavenClaude ever shipped was the
# Codespace devcontainer (`postStartCommand` + `portsAttributes.onAutoForward:
# openBrowser`). On a local/desktop machine NOTHING started the dashboard at
# session start — so "it didn't open automatically" was correct-by-design and
# completely undiscoverable. This closes that gap without making it the default.
#
# OPT-IN; absent ⇒ OFF — the same contract as every other comfort-posture knob:
#
#   # .ravenclaude/comfort-posture.yaml
#   dashboard_autostart: off | serve | open
#
#   off    default, and the behavior when the key is absent — no-op after one grep
#   serve  start the local server in the background; do NOT open a browser
#   open   start it AND open a browser tab
#
# NEVER DUPLICATES. It probes 127.0.0.1:<port>..<port+10> first; if THIS project's
# dashboard already answers on one of them it does nothing at all — no second
# server, no second tab. That is deliberate: several concurrent sessions in one
# project must not each spawn a server and steal focus with a new tab.
#
# NEVER ADOPTS ANOTHER PROJECT'S SERVER (repo-review dashboard-9). "A dashboard is
# live on the port" is not "it is ours": adopting another project's (or another
# worktree's) server lands Save & apply in the wrong repo. /__csrf carries
# project_id = sha256(<resolved project root>)[:12]; a live server whose id differs
# from ours, or that reports none (an older server), is skipped and ours starts on
# the next free port. Without curl the id cannot be read, so a live port is taken
# as ours (the old behaviour) rather than guessed at.
#
# FAIL-SAFE. Always exits 0. A SessionStart hook cannot block a session, and a
# dashboard that fails to launch must never be why a session doesn't start. The
# EXIT trap is armed FIRST (mirroring thing-orchestrator.sh's fail-CLOSED trap,
# inverted: SessionStart has nothing to fail closed to).
#
# PORTABILITY. bash 3.2-safe (stock macOS): no declare -A / mapfile / ${x^^} /
# globstar, and no GNU-only timeout / grep -P / sed -i. See the macOS-door
# milestones in CLAUDE.md.

trap 'exit 0' EXIT
set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
CFG="$PROJECT_DIR/.ravenclaude/comfort-posture.yaml"

# ── The cheapest possible no-op for everyone who has not opted in ────────────
[ -f "$CFG" ] || exit 0
grep -q 'dashboard_autostart' "$CFG" 2>/dev/null || exit 0

# Minimal scalar parse (no PyYAML in a consumer env). BRE only — portable to BSD
# sed. Anything unrecognised falls through to the `*)` no-op below, so a typo can
# never accidentally launch a server.
MODE="$(sed -n 's/^[[:space:]]*dashboard_autostart:[[:space:]]*\([a-z]*\).*/\1/p' "$CFG" 2>/dev/null | head -1)"
case "$MODE" in
  serve | open) ;;
  *) exit 0 ;;
esac

PORT="${RC_DASH_AUTOSTART_PORT:-8000}"

# Our project id, computed exactly as the server computes it (Path.resolve()), so
# the comparison below is like-for-like. Empty when python3 is absent — then no
# server could be launched anyway, and a live one is taken as ours.
LOCAL_ID=""
if command -v python3 >/dev/null 2>&1; then
  LOCAL_ID="$(python3 -c 'import hashlib, sys
from pathlib import Path
print(hashlib.sha256(str(Path(sys.argv[1]).resolve()).encode("utf-8")).hexdigest()[:12])' "$PROJECT_DIR" 2>/dev/null || true)"
fi

# ── Ownership probe ──────────────────────────────────────────────────────────
# /__csrf is the same same-origin signal the dashboard's own served-mode probe
# uses, so a 200 here means a real RavenClaude dashboard, not just an open port.
# _dash_owner <port> prints: ours | other | none. The two FORCE_* knobs are hidden
# test seams (precedent: reset-plugin-cache.py's --cache-root); they are never
# surfaced to users.
_dash_owner() {
  if [ -n "${RC_DASH_AUTOSTART_FORCE_LIVE:-}" ]; then echo ours; return 0; fi
  if [ -n "${RC_DASH_AUTOSTART_FORCE_DEAD:-}" ]; then echo none; return 0; fi
  if command -v curl >/dev/null 2>&1; then
    _body="$(curl -sf -m 2 "http://127.0.0.1:$1/__csrf" 2>/dev/null)" || { echo none; return 0; }
    _their_id="$(printf '%s' "$_body" | sed -n 's/.*"project_id"[[:space:]]*:[[:space:]]*"\([0-9a-f]*\)".*/\1/p' | head -1)"
    if [ -z "$LOCAL_ID" ] || [ "$_their_id" = "$LOCAL_ID" ]; then echo ours; else echo other; fi
    return 0
  fi
  if command -v nc >/dev/null 2>&1; then
    # nc can see the port but not whose server holds it: take a live one as ours.
    if nc -z 127.0.0.1 "$1" >/dev/null 2>&1; then echo ours; else echo none; fi
    return 0
  fi
  # Cannot probe → treat as free. serve-dashboards.py already recovers from a
  # busy port (v0.205.3) rather than crashing, so this is safe.
  echo none
}

# Scan the same port..port+10 window the server falls back through. Scan it ALL:
# ours may already be on a later port (it started while an earlier one was busy).
LAUNCH_PORT=""
OTHER_PORTS=""
_i=0
while [ "$_i" -le 10 ]; do
  _cand=$((PORT + _i))
  case "$(_dash_owner "$_cand")" in
    ours)
      printf '%s\n' "RavenClaude dashboard already live at http://127.0.0.1:${_cand}/ — not starting a second one." >&2
      exit 0
      ;;
    other)
      OTHER_PORTS="$OTHER_PORTS $_cand"
      ;;
    *)
      if [ -z "$LAUNCH_PORT" ]; then LAUNCH_PORT="$_cand"; fi
      ;;
  esac
  _i=$((_i + 1))
done
if [ -z "$LAUNCH_PORT" ]; then
  printf '%s\n' "RavenClaude dashboard autostart: ports ${PORT}-$((PORT + 10)) are held by other projects' dashboards — not starting one." >&2
  exit 0
fi

# Resolve the launcher relative to THIS hook (hooks-20): the dev-mirror wiring in
# .claude/settings.json runs it by ${CLAUDE_PROJECT_DIR} path, where
# CLAUDE_PLUGIN_ROOT is unset, so the old "${CLAUDE_PLUGIN_ROOT}/bin/rc" became
# "/bin/rc" and the hook exited silently. The hook's own ../bin/rc is right on both
# the installed-plugin and the dev-mirror path.
LAUNCHER="${RC_DASH_AUTOSTART_LAUNCHER:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/bin/rc}"
if [ ! -x "$LAUNCHER" ]; then
  printf '%s\n' "RavenClaude dashboard autostart (mode=$MODE): launcher not found or not executable at $LAUNCHER — not starting the dashboard." >&2
  exit 0
fi

LOG_DIR="$PROJECT_DIR/.ravenclaude/runs"
mkdir -p "$LOG_DIR" 2>/dev/null || true

# NOTE: deliberately no --project-root. serve-dashboards.py resolves the project
# from Path.cwd() and `rc` preserves the caller's cwd, so a plain `cd` targets the
# right repo — while --project-root is HARD-GUARDED to refuse a path inside the
# marketplace checkout (v0.44.0), which would make this hook a no-op in the
# marketplace repo itself.
set -- dashboard --port "$LAUNCH_PORT"
if [ "$MODE" = "serve" ]; then
  # `&&` here would be a set -e landmine: on MODE=open the test returns 1, the
  # whole line returns 1, the shell exits, and the trap silently swallows it —
  # so the server would never launch in the mode that most wants it.
  set -- "$@" --no-open
fi

cd "$PROJECT_DIR" 2>/dev/null || true
nohup "$LAUNCHER" "$@" >>"$LOG_DIR/dashboard-autostart.log" 2>&1 &

if [ -n "$OTHER_PORTS" ]; then
  printf '%s\n' "RavenClaude dashboard: port(s)${OTHER_PORTS} serve another project's dashboard — not adopting it." >&2
fi
printf '%s\n' "RavenClaude dashboard starting (mode=$MODE) on http://127.0.0.1:${LAUNCH_PORT}/" >&2
exit 0
