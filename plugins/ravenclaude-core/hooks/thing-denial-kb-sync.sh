#!/usr/bin/env bash
# thing-denial-kb-sync.sh — Stop hook.
#
# After a turn, materialise any NEW tribunal denials/defers into this project's
# denial knowledge base (thing-denial-kb.py sync). Hot-path-safe: it only READS
# the Sága audit records the Thing already wrote under .ravenclaude/runs/thing/ —
# it never touches the tribunal's live PreToolUse emit path, so it cannot change
# a verdict or corrupt a hook's stdout.
#
# Opt-in + fail-safe: no-op unless the project uses RavenClaude comfort posture;
# never writes to stdout; ALWAYS exits 0 so it can never block the stop.
set -euo pipefail

root="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -f "${root}/.ravenclaude/comfort-posture.yaml" ] || exit 0

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
kb="${here}/../scripts/thing-denial-kb.py"
[ -f "$kb" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

python3 "$kb" --root "$root" sync >/dev/null 2>&1 || true
exit 0
