#!/usr/bin/env bash
# delegation-nudge.sh
# PostToolUse hook for Edit | Write | MultiEdit. ADVISORY nudge (never blocks)
# when a "tell the user to manually check / open the portal" phrasing is written
# into a knowledge/ or docs/ markdown file. Implements the written-artifact
# enforced-complement of the Capability Grounding Protocol's clause
# "Consult your access inventory before telling the user to check or do something"
# (plugins/ravenclaude-core/CLAUDE.md): a delegated check baked into a knowledge
# file becomes a durable prior that teaches the next session to over-defer.
#
# HONEST SCOPE (read this — it is NOT a control): this hook can only see WRITTEN
# FILE CONTENT, never the chat answer — and the chat answer is where "go check the
# portal" almost ALWAYS lands. It is one narrow, defense-in-depth surface (the
# durable-artifact subset), not coverage of the failure mode. The real fix is the
# inventory (.ravenclaude/environment-context.md "Self-serve checks" + the
# capability banner) + the behavioral CGP clause. Do not mistake this hook for
# enforcement of the chat surface. It is ADVISORY (exit 0 always), OPT-IN (no-op
# unless the project has a .ravenclaude/comfort-posture.yaml), FAIL-SAFE (any
# error -> exit 0).
#
# False-positive discipline (mirrors claim-grounding-lint.sh): scoped to
# knowledge/**+docs/** .md only (excludes *.svg + concepts/visuals/**); skips YAML
# frontmatter, fenced code blocks, blockquotes, and headings; SUPPRESSES a line
# that carries a genuine hand-back reason ("unless you lack…", "because…") or that
# already cites a held route (Web API / GET / pac / az / gh); honors an inline
# `delegation-nudge-ok` escape comment.

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
  *.md) ;;
  *) exit 0 ;;
esac
case "$file" in
  */concepts/visuals/*) exit 0 ;;
esac
case "$file" in
  */knowledge/*|knowledge/*|*/docs/*|docs/*) ;;
  *) exit 0 ;;
esac

# OPT-IN: no-op unless the project has adopted a comfort-posture (bounded walk-up).
posture_found=0
dir="$(cd "$(dirname "$file")" 2>/dev/null && pwd || true)"
for _ in 1 2 3 4 5 6 7 8 9 10; do
  [[ -z "$dir" ]] && break
  if [[ -f "$dir/.ravenclaude/comfort-posture.yaml" ]]; then posture_found=1; break; fi
  [[ "$dir" == "/" ]] && break
  dir="$(dirname "$dir")"
done
[[ "$posture_found" -eq 0 ]] && exit 0

# Specific delegation phrasings (NOT a generic "check"). Three shapes:
#  (a) sending the user to a portal/UI; (b) "you/the user should manually check/verify…";
#  (c) "check the run history" / "go check…".
phrase='((open|go to|navigate to|log ?in to|sign ?in to)[^.]{0,40}(portal|admin center|maker portal|power automate|azure portal|the ui)|(you|the user|please)[[:space:]]+([a-z]+[[:space:]]+){0,3}(manually[[:space:]]+)?(check|verify|look at|review|inspect)\b|(check|view|inspect|review)[[:space:]]+the[[:space:]]+run[[:space:]]+history|\bgo[[:space:]]+(check|look|verify)\b)'
# A genuine hand-back reason on the line legitimizes the delegation (CGP Rule 4).
# Must be the ACCESS-LACKING shape — a bare "if/when" would over-suppress (e.g.
# "to see if it failed, open the portal" is NOT a hand-back reason).
reason='(unless you|if you (lack|don'\''?t|do not|can'\''?t|cannot)|because you (lack|don'\''?t|do not|can'\''?t|cannot)|\bcannot\b|\bcan'\''?t\b|do(n'\''?t| not) hold|no (access|route|permission|spn|token)|not authoriz)'
# A line that already cites a held route is documenting the self-serve path, not delegating.
route='(Web API|GET |POST |PATCH |DELETE |pac |az |gh |/api/data/|curl )'

violations=()
in_fence=0
in_frontmatter=0
lineno=0
first_nonblank_seen=0

while IFS= read -r line || [[ -n "$line" ]]; do
  lineno=$((lineno + 1))

  if [[ "$first_nonblank_seen" -eq 0 && -n "${line// /}" ]]; then
    first_nonblank_seen=1
    if [[ "$line" == "---" ]]; then in_frontmatter=1; continue; fi
  fi
  if [[ "$in_frontmatter" -eq 1 ]]; then
    [[ "$line" == "---" ]] && in_frontmatter=0
    continue
  fi

  if [[ "$line" =~ ^[[:space:]]*(\`\`\`|~~~) ]]; then
    in_fence=$((1 - in_fence)); continue
  fi
  [[ "$in_fence" -eq 1 ]] && continue

  [[ "$line" =~ ^[[:space:]]*\> ]] && continue
  [[ "$line" =~ ^[[:space:]]*#{1,6}[[:space:]] ]] && continue

  echo "$line" | grep -qiF 'delegation-nudge-ok' && continue

  if echo "$line" | grep -qiE "$phrase"; then
    # Suppress: a genuine hand-back reason, or a line that cites a held route.
    echo "$line" | grep -qiE "$reason" && continue
    echo "$line" | grep -qE "$route" && continue
    trimmed="$(echo "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    violations+=("  $file:$lineno: $trimmed")
  fi
done < "$file"

if [[ ${#violations[@]} -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  Delegation nudge — ${#violations[@]} "tell the user to manually check / open the portal" phrasing(s) written to:
       $file
EOF
  count=0
  for v in "${violations[@]}"; do
    echo "$v" >&2
    count=$((count + 1))
    [[ $count -ge 10 ]] && { echo "  …(more elided)" >&2; break; }
  done
  cat >&2 <<'EOF'

  Before delegating a check to the user, consult your access inventory
  (.ravenclaude/environment-context.md "Self-serve checks" + the capability banner):
  if you hold the route, run the check YOURSELF and report the answer. If this IS a
  genuine hand-back, say WHY (the route/permission you lack) — that phrasing, or a
  line citing the route, suppresses this nudge.
  See plugins/ravenclaude-core/CLAUDE.md § "Consult your access inventory…".

  Add `delegation-nudge-ok` on the line to suppress. This hook is ADVISORY — the
  write was not blocked, and it cannot see the chat answer (the primary surface).
────────────────────────────────────────────────────────────────────

EOF
fi

exit 0
