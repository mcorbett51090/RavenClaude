#!/usr/bin/env bash
# enforce-layout.sh
# PreToolUse hook for Write | Edit | MultiEdit.
#
# Reads .repo-layout.json from the consumer's project root. If absent, no-ops
# silently (allow everything). If present, checks the target path against the
# allowed_globs / forbidden_globs allow-list and denies off-pattern writes
# with a helpful message including a suggested correct location.
#
# Deny mechanism: emits hookSpecificOutput JSON to stdout (the modern, more
# reliable form per Claude Code issue #40580) AND exits 2 (belt-and-suspenders
# for older clients). Hook input arrives as $1 (file path), matching the
# convention used by the other hooks in this plugin.

set -euo pipefail
shopt -s extglob globstar nullglob

file="${1:-}"
[[ -z "$file" ]] && exit 0

project_root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
manifest="$project_root/.repo-layout.json"

# No layout policy in this project → allow everything.
[[ ! -f "$manifest" ]] && exit 0

# Layout policy exists but jq missing → fail open with a stderr note.
if ! command -v jq >/dev/null 2>&1; then
  echo "[enforce-layout] jq not found; skipping layout check. Install jq to enable enforcement." >&2
  exit 0
fi

# Convert to a path relative to project root.
if [[ "$file" == "$project_root"* ]]; then
  rel_path="${file#$project_root/}"
else
  # File is outside the project root — not our policy to enforce.
  exit 0
fi

emit_deny() {
  local reason="$1"
  # JSON output is preferred form; quote the reason safely via jq.
  jq -n --arg r "$reason" \
    '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
  echo "[enforce-layout] BLOCKED: $reason" >&2
  exit 2
}

# Defense-in-depth: refuse any path containing '..' before the allow-list check.
# A glob like 'plugins/*/agents/**' would otherwise accept the *string form*
# of 'plugins/x/agents/../../etc/passwd' because '*' inside [[ == ]] matches '/'.
# The hook can only be invoked by an agent that already has Write access, so
# this is low-severity, but the check is cheap and the failure mode is real.
if [[ "$rel_path" == *..* ]]; then
  emit_deny "Layout policy: path '$rel_path' contains '..' — refused as a path-traversal scrub."
fi

# Read patterns once.
# Matching note: this script uses bash `[[ string == pattern ]]` semantics,
# which is *pattern matching*, NOT filename expansion. Two consequences:
#   1. A single '*' inside [[ == ]] matches any string including '/'.
#   2. `shopt -s globstar` is inert inside [[ == ]] — '**' collapses to two
#      consecutive '*' metacharacters. So 'plugins/*/agents/**' matches
#      'plugins/foo/agents/sub/x.md' because the first '*' accepts the slash,
#      not because globstar is doing recursion.
# If you ever refactor this to use `find` or filename expansion, re-test
# every pattern — the semantics differ. See bash(1) "Pattern Matching" and
# "Filename Expansion" sections for details.
mapfile -t forbidden < <(jq -r '.forbidden_globs[]?' "$manifest" 2>/dev/null)
mapfile -t allowed < <(jq -r '.allowed_globs[]?' "$manifest" 2>/dev/null)

# Forbidden takes precedence.
for pat in "${forbidden[@]:-}"; do
  [[ -z "$pat" ]] && continue
  if [[ "$rel_path" == $pat ]]; then
    suggestion=$(jq -r --arg p "$pat" '.suggestions[$p] // empty' "$manifest")
    emit_deny "Layout policy: '$rel_path' matches forbidden pattern '$pat'.${suggestion:+ ${suggestion}}"
  fi
done

# If no allowed_globs are declared, treat the manifest as "forbid-only" policy.
if [[ "${#allowed[@]}" -eq 0 ]]; then
  exit 0
fi

# Otherwise require a match.
for pat in "${allowed[@]}"; do
  if [[ "$rel_path" == $pat ]]; then
    exit 0
  fi
done

# No match — deny with a generic suggestion.
generic=$(jq -r '.suggestions["New top-level directory"] // empty' "$manifest")
emit_deny "Layout policy: '$rel_path' does not match any allowed_globs in .repo-layout.json. ${generic:-Add the glob to .repo-layout.json first if this location is intentional.}"
