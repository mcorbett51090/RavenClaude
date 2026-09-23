#!/usr/bin/env bash
# Shim — the canonical script ships inside the plugin (plugins/ravenclaude-core/scripts/).
# Root copy kept so the marketplace's own AGENTS.md / CI references keep resolving.
root="$(git rev-parse --show-toplevel 2>/dev/null)" || root=""
if [ -z "$root" ]; then
  echo "cleanup-branches: must be run from inside the RavenClaude git work tree" >&2
  exit 1
fi
exec bash "$root/plugins/ravenclaude-core/scripts/cleanup-branches.sh" "$@"
