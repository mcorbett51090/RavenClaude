#!/usr/bin/env bash
# Shim — the canonical script ships inside the plugin (plugins/ravenclaude-core/scripts/).
# Root copy kept so the marketplace's own AGENTS.md / CI references keep resolving.
exec bash "$(git rev-parse --show-toplevel)/plugins/ravenclaude-core/scripts/branch-hygiene.sh" "$@"
