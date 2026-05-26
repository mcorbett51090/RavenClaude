#!/usr/bin/env bash
# capability-orientation.sh
# SessionStart hook. Injects a short "capability banner" into the session context
# so the agent opens every session AWARE of (a) what external surfaces this repo
# touches, (b) what auth/credentials it holds (names/presence only — never
# values), and (c) what its comfort-posture permissions already allow. This is
# the enforced-firing complement to the Capability Grounding Protocol's
# behavioral "read the posture at session start" instruction, which the model
# often skips. It does NOT enforce anything (the permission rules in
# .claude/settings.json do); it raises salience so the agent stops acting as if
# it has no access.
#
# Output contract (SessionStart, verified against code.claude.com/docs/en/hooks):
#   On exit 0, stdout is parsed as JSON; we emit
#     {"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":...}}
#   and Claude Code adds additionalContext to the session context. A SessionStart
#   hook can NOT block a session; non-zero exits are non-blocking. So we always
#   exit 0 and simply stay silent when there is nothing to say or anything fails.
#
# Cheap + local by contract: the assembler runs no network calls and no CLI
# subprocesses (it inspects local credential paths + env-var NAMES + settings.json).
# Deep environment enumeration stays the confirmation-gated environment-discovery
# skill, which the banner points to.

set -euo pipefail

# Project root. SessionStart sets CLAUDE_PROJECT_DIR; fall back to CWD.
project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"

# python3 is required to assemble the banner. Absent -> stay silent (never block).
command -v python3 >/dev/null 2>&1 || exit 0

# Locate the assembler. ${CLAUDE_PLUGIN_ROOT} is set when this fires as an
# installed plugin hook; fall back to the in-repo path for the marketplace-dev
# mirror, where the hook runs straight from the working tree.
assembler="${CLAUDE_PLUGIN_ROOT:-}/scripts/capability-orientation.py"
if [[ ! -f "$assembler" ]]; then
  scripts_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../scripts" 2>/dev/null && pwd || true)"
  assembler="${scripts_dir:-}/capability-orientation.py"
fi
[[ -f "$assembler" ]] || exit 0

# Emit the assembler's JSON verbatim. Any failure -> silent no-op (the assembler
# already fails closed to empty output, but guard the subprocess too).
out="$(python3 "$assembler" --root "$project_dir" 2>/dev/null || true)"
[[ -n "$out" ]] && printf '%s\n' "$out"

exit 0
