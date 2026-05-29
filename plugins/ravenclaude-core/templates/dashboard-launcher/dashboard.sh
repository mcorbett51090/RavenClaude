#!/usr/bin/env bash
# RavenClaude comfort-posture dashboard — launcher for THIS repo.
#
# Dropped into <repo>/.ravenclaude/ by `ravenclaude setup`. Opens the point-and-click
# comfort-posture dashboard scoped to THIS repo: it resolves its own repo root from this
# script's location, so it can only ever edit this repo's .ravenclaude/ — never the
# marketplace clone. (The server also hard-refuses a --project-root inside the marketplace.)
# Save & apply writes .ravenclaude/comfort-posture.yaml and updates .claude/settings.json.
#
# Like the marketplace's own open-dashboard.sh, this:
#   1. kills any dashboard server already running,
#   2. starts a fresh one (background, survives this script),
#   3. resolves the right URL for THIS environment (Codespace-forwarded or localhost),
#   4. opens it in your browser, and prints the URL.
# The URL is computed at launch, so there is never a baked-in link to go stale.
#
# Usage:  bash .ravenclaude/dashboard.sh [PORT]   (default 8000)
# Stop:   run it again to restart, or:  pkill -f serve-dashboards.py
set -euo pipefail

PORT="${1:-8000}"

# .ravenclaude/.. == the repo root. Derived from THIS script's location, not the CWD,
# so the dashboard is correctly scoped no matter where you launch it from.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# The marketplace clone (override with RAVENCLAUDE_DIR if you cloned it elsewhere).
RC_DIR="${RAVENCLAUDE_DIR:-$HOME/RavenClaude}"
SERVER="$RC_DIR/plugins/ravenclaude-core/scripts/serve-dashboards.py"
LOG="/tmp/rc-dashboard-${PORT}.log"

if [ ! -f "$SERVER" ]; then
  echo "ERROR: RavenClaude marketplace not found at $RC_DIR." >&2
  echo "       Set RAVENCLAUDE_DIR to your clone path, then re-run." >&2
  exit 1
fi

# 1. Kill any server already bound to this dashboard (ignore "no match").
pkill -f "serve-dashboards.py" 2>/dev/null || true
sleep 1

# 2. Start fresh in the background, scoped to THIS repo, fully detached so it outlives us.
nohup python3 "$SERVER" --project-root "$REPO_ROOT" --port "$PORT" >"$LOG" 2>&1 &
disown 2>/dev/null || true

# 3. Resolve the URL for this environment, then wait until the server actually answers.
if [ -n "${CODESPACE_NAME:-}" ]; then
  URL="https://${CODESPACE_NAME}-${PORT}.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}/dashboard.html"
else
  URL="http://127.0.0.1:${PORT}/dashboard.html"
fi
for _ in $(seq 1 10); do
  if curl -fsS -o /dev/null "http://127.0.0.1:${PORT}/dashboard.html" 2>/dev/null; then break; fi
  sleep 1
done

# 4. Open it in a browser. In a Codespace, $BROWSER is the VS Code helper that opens the
#    forwarded port in your real browser; fall back to python's opener elsewhere.
if [ -n "${BROWSER:-}" ] && [ -x "${BROWSER%% *}" ]; then
  "$BROWSER" "$URL" >/dev/null 2>&1 || true
else
  python3 -m webbrowser "$URL" >/dev/null 2>&1 || true
fi

echo "Dashboard for: $REPO_ROOT"
echo "Dashboard URL: $URL"
echo "(Codespace: if the tab doesn't open, use the Ports panel -> port ${PORT} -> Open in Browser.)"
echo "(server log: $LOG — run this again to restart, or 'pkill -f serve-dashboards.py' to stop.)"
