#!/usr/bin/env bash
# validate-flow-action-names.sh
# PostToolUse hook for Edit | Write | MultiEdit on Power Automate cloud-flow JSON
# (files under a workflows/ directory, e.g. solution-exported `*/workflows/*.json`).
#
# Flags actions left with their AUTO-GENERATED default names — `Compose_2`,
# `Apply_to_each_3`, `Condition`, `HTTP`, `Parse_JSON`, etc. Power Automate names every
# new action after its type; a maintainable flow renames them descriptively (see
# best-practices/name-flow-actions-descriptively.md). Default `_N` names make a flow
# unreadable, hostile to diff review, and brittle when expressions reference them.
#
# DETERMINISTIC + ADVISORY: fires on a structural pattern (an action key matching a
# default-name shape), not by LLM judgment. Prints warnings to stderr so Claude and the
# user both see them, but exits 0 — never blocks (to enforce, flip the final exit 0 to 1).
# FAIL-SAFE: any parse/IO error exits 0. Discovery-credit: the agentic Power Automate
# build/validate pattern this supports is from Flow Studio
# (https://github.com/ninihen1/power-automate-mcp-skills) + standard Flow-Checker/BPA
# guidance — re-implemented here in our own words against the flow-definition JSON shape.
#
# HONEST SCOPE: a single-file structural check on action *names* only. It does not
# validate flow logic, connection references, error handling, or trigger config (those
# are covered by check-house-opinions.sh §5/§6 and agent judgment).

set -euo pipefail

file="${1:-}"
# $CLAUDE_TOOL_FILE_PATH (passed as $1 by hooks.json) is NOT a real Claude Code
# hook variable, so under Claude Code the arg is empty and the path arrives only
# via the canonical stdin JSON contract. Fall back to it — same dual-source
# pattern regen-on-manifest-change.sh / guard-destructive.sh already use.
if [[ -z "$file" ]] && [[ ! -t 0 ]] && command -v jq >/dev/null 2>&1; then
  payload="$(cat 2>/dev/null || true)"
  if [[ -n "$payload" ]]; then
    file="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)"
  fi
fi
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0
case "$file" in
  */workflows/*.json|*/Workflows/*.json) ;;
  *) exit 0 ;;
esac

warnings="$(
python3 - "$file" <<'PY' 2>/dev/null || true
import json, re, sys

try:
    with open(sys.argv[1], encoding="utf-8") as f:
        doc = json.load(f)
except Exception:
    sys.exit(0)

# Auto-generated names: the action TYPE (underscored), optionally with a `_N` suffix.
DEFAULT_BARE = {
    "Compose", "Condition", "Switch", "Scope", "Until", "Apply_to_each", "For_each",
    "HTTP", "Response", "Request", "Initialize_variable", "Set_variable",
    "Increment_variable", "Decrement_variable", "Append_to_string_variable",
    "Append_to_array_variable", "Parse_JSON", "Select", "Filter_array", "Join",
    "Create_HTML_table", "Create_CSV_table", "Delay", "Terminate",
}
SUFFIX_N = re.compile(r"_\d+$")          # Compose_2, Apply_to_each_3, Condition_2 …

flagged = []

def walk(node):
    if isinstance(node, dict):
        acts = node.get("actions")
        if isinstance(acts, dict):
            for name in acts:
                if SUFFIX_N.search(name) or name in DEFAULT_BARE:
                    flagged.append(name)
        for v in node.values():
            walk(v)
    elif isinstance(node, list):
        for v in node:
            walk(v)

walk(doc)
# dedupe, keep order
seen = set()
for n in flagged:
    if n not in seen:
        seen.add(n)
        print("  action %r — auto-generated default name; rename descriptively" % n)
PY
)"

if [[ -n "$warnings" ]]; then
  {
    echo "⚠️  Power Automate action naming (advisory) — $file"
    echo "$warnings"
    echo "  → rename auto-named actions to describe what they do (not their type)."
    echo "    See plugins/power-platform/best-practices/name-flow-actions-descriptively.md."
  } >&2
fi

exit 0
