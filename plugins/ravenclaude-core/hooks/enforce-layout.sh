#!/usr/bin/env bash
# enforce-layout.sh
# PreToolUse hook for Write | Edit | MultiEdit.
#
# Enforces TWO independent, optional, fail-safe path policies on every write:
#
#   1. Repo layout (.repo-layout.json) — repo STRUCTURE: where files may live
#      (allowed_globs / forbidden_globs). The marketplace's own discipline.
#   2. Task scope (.ravenclaude/task-scope.json) — the CURRENT TASK's declared
#      blast radius: {"in_scope":[globs], "spec":"SPEC.md"}. A write touching a
#      path that matches no in_scope glob is denied — this is Gap 6 of the
#      command-review gap-closure plan: it bounds an agent's exploration BREADTH
#      (the runaway-brake bounds DEPTH, the DoD gate bounds correctness). The
#      file is dashboard/owner-authored per task and deleted when the task ends.
#
# Both policies are independent: either, both, or neither may be present, and an
# absent file is a silent no-op (allow). Both compose — a write must satisfy
# whichever policies ARE configured. This hook is already wired PreToolUse on
# Write|Edit|MultiEdit under both hosts (Claude via hooks.json, Copilot via the
# adapter's file-pretool mode), so task-scope ships with ZERO new wiring.
#
# Deny mechanism: emits hookSpecificOutput JSON to stdout (the modern, more
# reliable form per Claude Code issue #40580) AND exits 2 (belt-and-suspenders
# for older clients). Hook input arrives as $1 (file path), matching the
# convention used by the other hooks in this plugin.

set -euo pipefail
shopt -s extglob globstar nullglob

# Structured event log (P0.2). No-op fallback first so a missing helper can never
# abort this guard under `set -e`; the sourced helper overrides the stub.
_emit_hook_event() { :; }
_HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd 2>/dev/null)" || _HOOK_DIR=""
# shellcheck source=/dev/null
[ -n "$_HOOK_DIR" ] && [ -f "$_HOOK_DIR/_emit-event.sh" ] && . "$_HOOK_DIR/_emit-event.sh"

file="${1:-}"
[[ -z "$file" ]] && exit 0

project_root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
manifest="$project_root/.repo-layout.json"
task_scope="$project_root/.ravenclaude/task-scope.json"

# Neither policy configured in this project → allow everything.
[[ ! -f "$manifest" && ! -f "$task_scope" ]] && exit 0

# A policy exists but jq missing → fail open with a stderr note.
if ! command -v jq >/dev/null 2>&1; then
  echo "[enforce-layout] jq not found; skipping layout/scope checks. Install jq to enable enforcement." >&2
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
  local rule="${2:-layout-policy}"
  # JSON output is preferred form; quote the reason safely via jq.
  jq -n --arg r "$reason" \
    '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
  echo "[enforce-layout] BLOCKED: $reason" >&2
  _emit_hook_event "enforce-layout.sh" "deny" "${CLAUDE_TOOL_NAME:-Write/Edit/MultiEdit}" "${rel_path:-$file}" "$rule" 2
  exit 2
}

# Defense-in-depth: refuse any path containing '..' before the allow-list check.
# A glob like 'plugins/*/agents/**' would otherwise accept the *string form*
# of 'plugins/x/agents/../../etc/passwd' because '*' inside [[ == ]] matches '/'.
# The hook can only be invoked by an agent that already has Write access, so
# this is low-severity, but the check is cheap and the failure mode is real.
if [[ "$rel_path" == *..* ]]; then
  emit_deny "Layout policy: path '$rel_path' contains '..' — refused as a path-traversal scrub." "path-traversal"
fi

# ── Task-scope check (Gap 6) ────────────────────────────────────────────────
# Bounds the CURRENT task's write blast radius. Runs BEFORE the layout check so
# it is never short-circuited by the layout's forbid-only `exit 0`. Fail-safe:
# an absent file, an absent/empty in_scope list, or unparseable JSON → no-op.
if [[ -f "$task_scope" ]]; then
  mapfile -t in_scope < <(jq -r '.in_scope[]?' "$task_scope" 2>/dev/null)
  if [[ "${#in_scope[@]}" -gt 0 ]]; then
    scope_ok=0
    for pat in "${in_scope[@]}"; do
      [[ -z "$pat" ]] && continue
      if [[ "$rel_path" == $pat ]]; then
        scope_ok=1
        break
      fi
    done
    if [[ "$scope_ok" -eq 0 ]]; then
      spec="$(jq -r '.spec // empty' "$task_scope" 2>/dev/null)"
      emit_deny "Task scope: '$rel_path' is outside this task's declared in_scope set (.ravenclaude/task-scope.json).${spec:+ Task spec: ${spec}.} If this write is genuinely part of the task, add the glob to in_scope (or clear task-scope.json when the task is done)." "task-scope"
    fi
  fi
fi

# ── Repo-layout check ───────────────────────────────────────────────────────
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
    emit_deny "Layout policy: '$rel_path' matches forbidden pattern '$pat'.${suggestion:+ ${suggestion}}" "forbidden-glob"
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
emit_deny "Layout policy: '$rel_path' does not match any allowed_globs in .repo-layout.json. ${generic:-Add the glob to .repo-layout.json first if this location is intentional.}" "off-allow-list"
