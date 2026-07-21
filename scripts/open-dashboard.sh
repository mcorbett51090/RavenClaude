#!/usr/bin/env bash
# open-dashboard.sh — one command to (re)launch the comfort-posture dashboard.
#
#   1. kills any dashboard server already running,
#   2. starts a fresh one on port 8000 (background, survives this script),
#   3. opens the dashboard in your browser automatically.
#
# Run it however is easiest:
#   - VS Code: Ctrl/Cmd+Shift+B  (this is the default build task)
#   - VS Code: Terminal → Run Task → "RavenClaude: Open dashboard"
#   - Terminal: bash scripts/open-dashboard.sh
#
# This launches the MARKETPLACE's own dashboard (edits this repo's
# .ravenclaude/comfort-posture.yaml). Consumer repos use .ravenclaude/dashboard.sh.
set -euo pipefail

PORT="${1:-8000}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Root dev server serves the repo root, so /index.html (the unified portal
# with the dashboard + catalog folded in) is reachable with live /__* endpoints.
SERVER="$ROOT/scripts/serve-dashboards.py"
# Create the log via mktemp (O_EXCL, unpredictable suffix) rather than a fixed,
# world-predictable /tmp path opened with ">" — a plain redirect follows a symlink,
# so a local attacker pre-planting /tmp/rc-dashboard-<port>.log could redirect the
# write. LOG is only the redirect target + the informational echo below (the restart
# uses pkill, not this path), so a fresh unique file per run is safe.
LOG="$(mktemp "/tmp/rc-dashboard-${PORT}-XXXXXX.log" 2>/dev/null)" || LOG="/tmp/rc-dashboard-${PORT}.$$.log"

[ -f "$SERVER" ] || { echo "dashboard server not found: $SERVER" >&2; exit 1; }

# 1. Kill any server already bound to THIS port (ignore "no match"). The port is
#    end-anchored (\$) and the dot is escaped so `--port 800` can't substring-match
#    a running `--port 8000` — pkill -f is an unanchored regex over the whole
#    command line, and the nohup line below puts --port last, so `$` is exact.
pkill -f "serve-dashboards\.py --port ${PORT}\$" 2>/dev/null || true
sleep 1

# 2. Start fresh in the background, fully detached so it outlives this script.
nohup python3 "$SERVER" --port "$PORT" >"$LOG" 2>&1 &
disown 2>/dev/null || true

# 3. Wait until it answers, discovering the ACTUAL bound port. serve-dashboards.py
#    falls back through PORT..PORT+5 when the requested port is busy, so never
#    assume $PORT bound — probe the range and adopt the first port that responds.
#    Reporting/opening the wrong port is exactly what orphans a dead tab whose
#    Save then reports "no local server".
bound_port=""
for _ in $(seq 1 10); do
  for cand in $(seq "$PORT" $((PORT + 5))); do
    if curl -fsS -o /dev/null "http://127.0.0.1:${cand}/index.html" 2>/dev/null; then
      bound_port="$cand"
      break 2
    fi
  done
  sleep 1
done
PORT="${bound_port:-$PORT}"

if [ -n "${CODESPACE_NAME:-}" ]; then
  URL="https://${CODESPACE_NAME}-${PORT}.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}/index.html"
else
  URL="http://127.0.0.1:${PORT}/index.html"
fi

# 4. Open it in a browser — but ONLY when attached to an interactive terminal.
#    Under postStartCommand there is no controlling TTY (stdout is redirected to a
#    log) and $BROWSER isn't populated yet (the VS Code client hasn't attached), so
#    the fallback below would launch a terminal browser (www-browser) that never
#    exits and hangs the whole lifecycle command. Codespaces already auto-opens the
#    forwarded port via onAutoForward: openBrowser, so skipping here loses nothing.
if [ -t 1 ]; then
  # Resolve the first word of $BROWSER via PATH (not as a cwd-relative path), so a bare
  # command name (BROWSER=firefox) is honored, not just an absolute path. `command -v`
  # handles both a PATH name and an absolute path uniformly (Finding 24).
  browser_bin="$(command -v "${BROWSER%% *}" 2>/dev/null)"
  if [ -n "${BROWSER:-}" ] && [ -n "$browser_bin" ]; then
    read -ra browser_cmd <<<"$BROWSER"
    "${browser_cmd[@]}" "$URL" >/dev/null 2>&1 || true
  else
    # Time-bound so a terminal-browser fallback can never block, even interactively.
    # `timeout` is absent on stock macOS (exit 127); a bare `timeout 5 …` there fails
    # command-not-found and the `|| true` swallows it, so the tab silently never opens.
    # Guard it (the inline pattern scripts/notify.sh uses); degrade to an unbounded open.
    if command -v timeout >/dev/null 2>&1; then
      timeout 5 python3 -m webbrowser "$URL" >/dev/null 2>&1 || true
    else
      python3 -m webbrowser "$URL" >/dev/null 2>&1 || true
    fi
  fi
fi

echo "Dashboard: $URL"
echo "(server log: $LOG — press the same task/command again to restart it)"
