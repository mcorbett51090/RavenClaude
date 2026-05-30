#!/usr/bin/env bash
# guard-recursive-spawn.sh
# PostToolUse hook for Edit | Write | MultiEdit on agent definition files
# (plugins/*/agents/*.md). Warns when an agent's prompt instructs *itself*
# to spawn another sub-agent.
#
# Why this matters
# ----------------
# RavenClaude follows the hierarchical orchestrator-worker pattern documented in
# plugins/ravenclaude-core/CLAUDE.md and plugins/ravenclaude-core/skills/spawn-team.md:
# only the Team Lead (the top-level Claude session) dispatches sub-agents. A
# specialist that spawns its own peers turns the call graph from a tree into a
# DAG-or-worse, breaks observability, and risks infinite loops on bad briefs.
#
# Detection
# ---------
# Conservative grep for tokens that look like the agent is *instructing itself*
# to spawn another agent. These are the patterns Claude Code's own agent SDK
# and the Anthropic Agent tool use:
#
#   - `Agent(`             — Anthropic Agent tool call
#   - `Task(`              — historical / SDK alias for Agent
#   - `subagent_type:`     — Agent tool param naming the agent to spawn
#   - `spawn an agent`     — natural-language dispatch
#   - `dispatch a sub-agent` / `dispatch the <role>-agent`
#   - `dispatch <role>` where <role> is an agent name from this plugin's roster
#
# False-positive guard: we ignore matches inside lines marked as escalation
# *recommendations* (those describe handoffs the Team Lead would make, which is
# fine) — heuristic: skip lines that contain "escalate", "handoff", "Team Lead",
# or "the Team Lead".
#
# Behavior
# --------
# Advisory by default — prints warnings to stderr and exits 0. To enforce
# hard-block on violations, flip the final `exit 0` to `exit 1` (or set
# RC_GUARD_RECURSIVE_SPAWN_STRICT=1 in the environment).

set -euo pipefail

# Structured event log (P0.2). No-op fallback first so a missing helper can never
# abort this hook under `set -e`; the sourced helper overrides the stub.
_emit_hook_event() { :; }
_HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd 2>/dev/null)" || _HOOK_DIR=""
# shellcheck source=/dev/null
[ -n "$_HOOK_DIR" ] && [ -f "$_HOOK_DIR/_emit-event.sh" ] && . "$_HOOK_DIR/_emit-event.sh"

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

# Only scrutinize files that look like agent definitions inside a plugin.
# Accept both absolute paths (Claude Code passes absolute) and relative ones
# (so the hook can be tested by `./guard-recursive-spawn.sh plugins/.../foo.md`).
case "$file" in
  */plugins/*/agents/*.md) ;;
  plugins/*/agents/*.md) ;;
  *) exit 0 ;;
esac

# Patterns suggesting recursive spawn — matched case-insensitively.
patterns=(
  'Agent\('
  'Task\('
  'subagent_type[[:space:]]*[:=]'
  'spawn[[:space:]]+(an?|another)[[:space:]]+(sub-?)?agent'
  'dispatch[[:space:]]+(an?|another|the)[[:space:]]+(sub-?)?agent'
  'invoke[[:space:]]+(an?|another)[[:space:]]+(sub-?)?agent'
  'delegate[[:space:]]+to[[:space:]]+(an?|another)[[:space:]]+(sub-?)?agent'
)

violations=()

for pat in "${patterns[@]}"; do
  # grep -EnI: extended regex, line numbers, skip binary; -i: case-insensitive
  while IFS= read -r match; do
    # match looks like "42:  Agent(role=foo) — spawn"
    # Skip lines that read as escalation recommendations to the Team Lead, which
    # are allowed (the agent suggests a handoff; the Team Lead decides).
    if echo "$match" | grep -qiE '(escalat|hand[- ]?off|team[- ]?lead|recommend.*specialist|suggested[[:space:]]+specialist|^\s*>\s*)'; then
      continue
    fi
    violations+=("  [$pat] $file:$match")
  done < <(grep -EnIi "$pat" "$file" 2>/dev/null || true)
done

if [[ ${#violations[@]} -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  Recursive-spawn check flagged ${#violations[@]} potential issue(s) in:
       $file

EOF
  # Show at most the first 10 violations to keep output readable.
  count=0
  for v in "${violations[@]}"; do
    echo "$v" >&2
    count=$((count + 1))
    [[ $count -ge 10 ]] && { echo "  …(more elided)" >&2; break; }
  done
  cat >&2 <<'EOF'

  Why this matters: only the Team Lead dispatches sub-agents in
  RavenClaude. A specialist whose prompt instructs itself to spawn
  another agent breaks the hierarchical dispatch pattern documented in
  plugins/ravenclaude-core/CLAUDE.md and skills/spawn-team.md.

  If your agent legitimately needs to *recommend* a handoff to another
  specialist, phrase it as an Escalation note for the Team Lead (see
  the Output Contract section of the agent's CLAUDE.md). Lines that
  mention "escalate", "handoff", or "the Team Lead" are not flagged.

  This hook is advisory — the edit was not blocked. To enforce, set
  RC_GUARD_RECURSIVE_SPAWN_STRICT=1 or change `exit 0` to `exit 1` at
  the bottom of this script.
────────────────────────────────────────────────────────────────────

EOF
  if [[ "${RC_GUARD_RECURSIVE_SPAWN_STRICT:-0}" == "1" ]]; then
    _emit_hook_event "guard-recursive-spawn.sh" "deny" "${CLAUDE_TOOL_NAME:-Edit/Write/MultiEdit}" "$file" "recursive-spawn" 1
    exit 1
  fi
  # Advisory (non-blocking) path — logged as a warn for telemetry.
  _emit_hook_event "guard-recursive-spawn.sh" "warn" "${CLAUDE_TOOL_NAME:-Edit/Write/MultiEdit}" "$file" "recursive-spawn" 0
fi

exit 0
