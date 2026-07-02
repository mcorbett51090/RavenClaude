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
LOG="/tmp/rc-dashboard-$PORT.log"

[ -f "$SERVER" ] || { echo "dashboard server not found: $SERVER" >&2; exit 1; }

# 1. Kill any server already bound to THIS PORT (ignore "no match"). Narrowed to
#    --port "$PORT" so restarting on one port doesn't kill dashboards on others.
pkill -f "serve-dashboards.py --port $PORT" 2>/dev/null || true
sleep 1

# 2. Start fresh in the background, fully detached so it outlives this script.
nohup python3 "$SERVER" --port "$PORT" >"$LOG" 2>&1 &
disown 2>/dev/null || true

# 3. Wait until it actually answers (up to ~10s), then resolve the URL.
if [ -n "${CODESPACE_NAME:-}" ]; then
  URL="https://${CODESPACE_NAME}-${PORT}.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}/index.html"
else
  URL="http://127.0.0.1:${PORT}/index.html"
fi
for _ in $(seq 1 10); do
  if curl -fsS -o /dev/null "http://127.0.0.1:${PORT}/index.html" 2>/dev/null; then break; fi
  sleep 1
done

# 4. Open it in a browser. In a Codespace, $BROWSER is the VS Code helper that
#    opens the forwarded port in your real browser; fall back to python's opener.
if [ -n "${BROWSER:-}" ] && [ -x "${BROWSER%% *}" ]; then
  read -ra browser_cmd <<<"$BROWSER"
  "${browser_cmd[@]}" "$URL" >/dev/null 2>&1 || true
else
  python3 -m webbrowser "$URL" >/dev/null 2>&1 || true
fi

echo "Dashboard: $URL"
echo "(server log: $LOG — press the same task/command again to restart it)"
