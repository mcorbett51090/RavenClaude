#!/usr/bin/env bash
# explore-tier-pin.sh
# PreToolUse hook for Agent (matcher also accepts the pre-rename name Task).
# The PREVENTION leg of plugins/ravenclaude-core/knowledge/model-tier-delegation.md:
# when the Team Lead dispatches the built-in `Explore` WITHOUT a `model`, this
# hook rewrites the tool input to add `model: haiku` (posture-tunable) BEFORE
# the sub-agent starts — via PreToolUse `hookSpecificOutput.updatedInput`
# `[docs-verified 2026-09-14]`.
#
# WHY. Since Claude Code v2.1.198 an un-pinned Explore inherits the main
# conversation's model, so on an Opus session every "go find X" is an Opus
# dispatch whose whole job is reading. handoff-tax-meter.sh (PostToolUse)
# already names this `frontier_readonly` — after the tokens are spent. This
# hook moves the fix to the one moment it is free: the dispatch call itself.
#
# WHAT IT NEVER DOES:
#   * emit a permissionDecision — the consumer's comfort-posture category
#     `subagent_dispatch` (allow / ask) still gates the call unchanged;
#   * touch a dispatch that names a model (any string, including "inherit");
#   * touch anything but Explore (scout pins haiku in its own frontmatter;
#     general-purpose / Plan do real work);
#   * pin when CLAUDE_CODE_SUBAGENT_MODEL is set (the fleet-wide route wins);
#   * block, deny, or fail the dispatch — every error path is exit 0 with no
#     stdout, so Claude's original input runs.
#
# OPT-IN by comfort-posture PRESENCE (same rule as every advisory/rewrite hook
# in this plugin). Knob: `handoff_tax: { pin_explore: haiku | sonnet | off }`;
# `handoff_tax: off` disables it together with the meter's advisory.
#
# The decision lives in scripts/explore-tier-pin.py (stdlib only, --self-test);
# this wrapper is the hook contract: cheap greps -> python -> JSON on stdout
# -> one hook-event line. It writes its own JSON envelope, so it must NOT
# source _advise.sh (which would emit a second object on the same stdout).

set -euo pipefail

_rc_hd="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || printf '.')"
if [ -f "$_rc_hd/_emit-event.sh" ]; then . "$_rc_hd/_emit-event.sh"; fi
command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }

command -v python3 >/dev/null 2>&1 || exit 0
[ -t 0 ] && exit 0
payload="$(cat 2>/dev/null || true)"
[ -n "$payload" ] || exit 0

# Cheap greps before any python spawn: only the dispatch tool, only an Explore.
printf '%s' "$payload" | grep -Eq '"tool_name"[[:space:]]*:[[:space:]]*"(Agent|Task)"' || exit 0
printf '%s' "$payload" | grep -Eiq '"subagent_type"[[:space:]]*:[[:space:]]*"([^"]*:)?explore"' || exit 0

# Fleet-wide route already set -> the per-invocation pin would override it. Stand down.
[ -n "${CLAUDE_CODE_SUBAGENT_MODEL:-}" ] && exit 0

# Project root: CLAUDE_PROJECT_DIR, else the payload's cwd, else $PWD.
root="${CLAUDE_PROJECT_DIR:-}"
if [ -z "$root" ] && command -v jq >/dev/null 2>&1; then
  root="$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null || true)"
fi
[ -n "$root" ] || root="$PWD"

# OPT-IN: no-op unless the project has adopted a comfort-posture (bounded walk-up).
posture_found=0
dir="$root"
for _ in 1 2 3 4 5 6 7 8 9 10; do
  [ -z "$dir" ] && break
  if [ -f "$dir/.ravenclaude/comfort-posture.yaml" ]; then posture_found=1; root="$dir"; break; fi
  [ "$dir" = "/" ] && break
  dir="$(dirname "$dir")"
done
[ "$posture_found" -eq 0 ] && exit 0

pin="$_rc_hd/../scripts/explore-tier-pin.py"
[ -f "$pin" ] || exit 0

out="$(printf '%s' "$payload" | python3 "$pin" --project-root "$root" 2>/dev/null || true)"
[ -n "$out" ] || exit 0

tier="$(printf '%s' "$out" | sed -n 's/.*"model":"\([a-z]*\)".*/\1/p' | head -n 1)"
_emit_hook_event "explore-tier-pin.sh" "warn" "Agent" "Explore" "pinned:${tier:-unknown}" "0" || true
printf '%s\n' "$out"
exit 0
