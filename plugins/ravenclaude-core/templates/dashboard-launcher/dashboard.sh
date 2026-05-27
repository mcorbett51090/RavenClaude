#!/usr/bin/env bash
# RavenClaude comfort-posture dashboard — launcher for THIS repo.
#
# Dropped into <repo>/.ravenclaude/ by `ravenclaude setup`. Opens the point-and-click
# comfort-posture dashboard scoped to THIS repo: it resolves its own repo root from this
# script's location, so it can only ever edit this repo's .ravenclaude/ — never the
# marketplace clone. (The server also hard-refuses a --project-root inside the marketplace.)
# Save & apply writes .ravenclaude/comfort-posture.yaml and updates .claude/settings.json.
#
# Usage:  bash .ravenclaude/dashboard.sh [--port 8000]
# Stop:   Ctrl+C
set -euo pipefail

# .ravenclaude/.. == the repo root. Derived from THIS script's location, not the CWD,
# so the dashboard is correctly scoped no matter where you launch it from.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# The marketplace clone (override with RAVENCLAUDE_DIR if you cloned it elsewhere).
RC_DIR="${RAVENCLAUDE_DIR:-$HOME/RavenClaude}"
SERVER="$RC_DIR/plugins/ravenclaude-core/scripts/serve-dashboards.py"

if [ ! -f "$SERVER" ]; then
  echo "ERROR: RavenClaude marketplace not found at $RC_DIR." >&2
  echo "       Set RAVENCLAUDE_DIR to your clone path, then re-run." >&2
  exit 1
fi

echo "Opening the RavenClaude comfort-posture dashboard for: $REPO_ROOT"
echo "(Codespace: use the Ports panel -> Open in Browser. Press Ctrl+C to stop.)"
exec python3 "$SERVER" --project-root "$REPO_ROOT" "$@"
