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
# NEVER DUPLICATES. It probes 127.0.0.1:<port> first; if a dashboard already
# answers there it does nothing at all — no second server, no second tab. That is
# deliberate: several concurrent sessions in one project must not each spawn a
# server and steal focus with a new tab.
#
# HONEST LIMIT (stated, not glossed). The probe answers "is a dashboard live on
# this port?", NOT "is it THIS project's dashboard". If another project's
# dashboard already holds the port, this hook stands down rather than starting a
# competing one; open yours explicitly with `rc dashboard --port N`.
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

# ── Liveness probe ───────────────────────────────────────────────────────────
# /__csrf is the same same-origin signal the dashboard's own served-mode probe
# uses, so a 200 here means a real RavenClaude dashboard, not just an open port.
# The two FORCE_* knobs are hidden test seams (precedent: reset-plugin-cache.py's
# --cache-root); they are never surfaced to users.
_dash_is_live() {
  if [ -n "${RC_DASH_AUTOSTART_FORCE_LIVE:-}" ]; then return 0; fi
  if [ -n "${RC_DASH_AUTOSTART_FORCE_DEAD:-}" ]; then return 1; fi
  if command -v curl >/dev/null 2>&1; then
    curl -sf -m 2 -o /dev/null "http://127.0.0.1:${PORT}/__csrf" >/dev/null 2>&1
    return $?
  fi
  if command -v nc >/dev/null 2>&1; then
    nc -z 127.0.0.1 "$PORT" >/dev/null 2>&1
    return $?
  fi
  # Cannot probe → treat as dead. serve-dashboards.py already recovers from a
  # busy port (v0.205.3) rather than crashing, so this is safe.
  return 1
}

if _dash_is_live; then
  printf '%s\n' "RavenClaude dashboard already live at http://127.0.0.1:${PORT}/ — not starting a second one." >&2
  exit 0
fi

LAUNCHER="${RC_DASH_AUTOSTART_LAUNCHER:-${CLAUDE_PLUGIN_ROOT:-}/bin/rc}"
[ -x "$LAUNCHER" ] || exit 0

LOG_DIR="$PROJECT_DIR/.ravenclaude/runs"
mkdir -p "$LOG_DIR" 2>/dev/null || true

# NOTE: deliberately no --project-root. serve-dashboards.py resolves the project
# from Path.cwd() and `rc` preserves the caller's cwd, so a plain `cd` targets the
# right repo — while --project-root is HARD-GUARDED to refuse a path inside the
# marketplace checkout (v0.44.0), which would make this hook a no-op in the
# marketplace repo itself.
set -- dashboard --port "$PORT"
if [ "$MODE" = "serve" ]; then
  # `&&` here would be a set -e landmine: on MODE=open the test returns 1, the
  # whole line returns 1, the shell exits, and the trap silently swallows it —
  # so the server would never launch in the mode that most wants it.
  set -- "$@" --no-open
fi

cd "$PROJECT_DIR" 2>/dev/null || true
nohup "$LAUNCHER" "$@" >>"$LOG_DIR/dashboard-autostart.log" 2>&1 &

printf '%s\n' "RavenClaude dashboard starting (mode=$MODE) on http://127.0.0.1:${PORT}/" >&2
exit 0
