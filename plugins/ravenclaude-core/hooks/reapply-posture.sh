#!/usr/bin/env bash
# reapply-posture.sh
# SessionStart hook. Regenerates the comfort-posture permission rules from the
# project's .ravenclaude/comfort-posture.yaml at the start of every session, so
# the posture a user composed in the dashboard is active without anyone having
# to run /set-posture by hand.
#
# Why this exists (the Claude-Code-on-the-web case): the cloud container is
# ephemeral and only committed files survive a fresh clone. So the committed
# project-layer .claude/settings.json is the only posture that persists across
# web sessions. Keeping the human-editable YAML as the single source of truth
# and regenerating settings.json from it here means a user edits the dashboard
# YAML, commits it, and the rules stay in sync — no generated file to hand-edit.
#
# Scope: project layer only (--scope project). That layer (a) is the one that
# persists on web, (b) is the shared, committed baseline, and (c) does NOT touch
# the machine-wide ~/.claude/settings.json, so opening one project never rewrites
# another project's posture. The personal local layer (.claude/settings.local.json)
# is left to an explicit /set-posture run.
#
# Idempotent: the translator OVERWRITES permissions.{allow,ask,deny}
# deterministically, so re-running against an unchanged YAML yields identical
# content (no spurious git diff). No posture file -> silent no-op, so consumers
# who never set a posture see nothing. Always exits 0: a posture-apply failure
# must never block a session from starting.
#
# Timing note: this runs during session start. Whether the rewritten file is
# picked up by the *current* session or only the *next* one depends on Claude
# Code's settings-load vs hook-run order; either way the next session is correct.
# Committing the generated settings.json alongside the YAML guarantees the
# current session loads the right rules natively; this hook then keeps the two
# in sync and self-heals a YAML edit that skipped /set-posture.

set -euo pipefail

# Resolve the project root. SessionStart sets CLAUDE_PROJECT_DIR; fall back to CWD.
project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
posture="$project_dir/.ravenclaude/comfort-posture.yaml"

# No posture configured -> nothing to do. Stay silent.
[[ -f "$posture" ]] || exit 0

# Need python3 to run the translator. Degrade gracefully if it is absent.
if ! command -v python3 >/dev/null 2>&1; then
  echo "ravenclaude: comfort posture found but python3 is unavailable; skipping auto-apply. Run /set-posture once python3 is on PATH." >&2
  exit 0
fi

# Locate the translator. ${CLAUDE_PLUGIN_ROOT} is set when this fires as an
# installed plugin hook; fall back to the in-repo path for the marketplace-dev
# mirror, where the hook runs straight from the working tree.
translator="${CLAUDE_PLUGIN_ROOT:-}/scripts/apply-comfort-posture.py"
if [[ ! -f "$translator" ]]; then
  scripts_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../scripts" 2>/dev/null && pwd || true)"
  translator="${scripts_dir:-}/apply-comfort-posture.py"
fi
[[ -f "$translator" ]] || exit 0

# Regenerate the project-layer rules from the YAML. Success is silent; only a
# failure is surfaced (to stderr) so the user knows to run /set-posture by hand.
if ! out="$(python3 "$translator" --project-root "$project_dir" --scope project --source reapply 2>&1)"; then
  {
    echo "ravenclaude: could not auto-apply comfort posture from .ravenclaude/comfort-posture.yaml"
    printf '%s\n' "$out" | sed 's/^/  /'
    echo "  Run /set-posture to apply it manually."
  } >&2
fi

exit 0
