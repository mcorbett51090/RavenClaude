#!/usr/bin/env bash
# plugin-lifecycle-telemetry.sh — bumps a plugin's last_used_at when one of its
# skills / agents / slash commands is actually invoked.
#
# Wired to PostToolUse(Agent|Task|Skill) and UserPromptSubmit. The engine derives
# (plugin, signal) from the payload:
#   Agent/Task -> signal=agent, plugin = subagent_type prefix before ':'
#   Skill      -> signal=skill, plugin = skill/command prefix before ':'
#   /ns:cmd    -> signal=slash, plugin = leading-token prefix before ':'
# A built-in agent/skill with no plugin namespace (general-purpose, claude, a
# bare /clear) has no ':' prefix and is a silent no-op — presence is never a use.
#
# ⛔ SessionStart presence and dashboard-open are NOT wired here, deliberately:
# only a real invocation counts as a use (M7 tracking, but never "it loaded").
#
# OPT-IN, absent => inert: no comfort-posture file is a no-op after one test -f.
# Lives under scripts/ (invoked via `bash`), matching ask-on-ambiguity.sh — the
# executable-bit-on-a-new-hooks-file constraint.
#
# FAIL-SAFE: EXIT trap armed first; always exits 0 (never blocks a tool call or
# a prompt). PORTABILITY: bash 3.2-safe; no GNU-only tools.

trap 'exit 0' EXIT
set -uo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
CFG="$PROJECT_DIR/.ravenclaude/comfort-posture.yaml"
[ -f "$CFG" ] || exit 0

ENGINE="${CLAUDE_PLUGIN_ROOT:-}/scripts/plugin-lifecycle.py"
if [ ! -f "$ENGINE" ]; then
  SELF_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
  ENGINE="$SELF_DIR/plugin-lifecycle.py"
fi
[ -f "$ENGINE" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

# Per-session mid-flight marker (AppSec 2): a plugin used this session is skipped
# from uninstall by the sweep.
SESSION_MARKER=""
if [ -n "${CLAUDE_SESSION_ID:-}" ]; then
  SESSION_MARKER="$PROJECT_DIR/.ravenclaude/runs/${CLAUDE_SESSION_ID}/plugin-lifecycle-used.txt"
fi

# The engine reads the raw hook payload on stdin, derives (plugin, signal), and
# records it. It no-ops when tracking is off or no plugin prefix resolves.
python3 "$ENGINE" --project "$PROJECT_DIR" telemetry \
  ${SESSION_MARKER:+--session-marker "$SESSION_MARKER"} >/dev/null 2>&1 || exit 0

exit 0
