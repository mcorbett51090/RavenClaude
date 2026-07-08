#!/usr/bin/env bash
# claim-grounding-lint.sh
# PostToolUse hook for Edit | Write | MultiEdit. ADVISORY nudge (never blocks)
# when an UNHEDGED ABSOLUTE capability claim is written into a knowledge/ or
# docs/ markdown file without an inline provenance marker. Implements the
# enforced-complement of the Claim Grounding & Source Honesty protocol
# (plugins/ravenclaude-core/CLAUDE.md): a confident-wrong "you can't…" baked into
# a knowledge file becomes a durable false prior the next session trusts.
#
# HONEST SCOPE (read this): this hook can only see WRITTEN FILE CONTENT — never the
# chat answer, which is where the confident error usually lands. It is one narrow,
# defense-in-depth surface (the durable-artifact case), not a control. It is
# ADVISORY (exit 0 always), OPT-IN (no-op unless the project has a
# .ravenclaude/comfort-posture.yaml), and FAIL-SAFE (any error -> exit 0).
#
# False-positive discipline (Panel C): scoped to knowledge/**+docs/** .md only
# (excludes *.svg + concepts/visuals/**); skips YAML frontmatter, fenced code
# blocks, and blockquotes (where bad-examples are quoted); suppresses conditional
# phrasings ("if you can't…"); honors an inline `claim-lint-ok` escape comment;
# and matches a SPECIFIC set of absolute phrasings, not a generic "cannot".

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

# Path scope: only knowledge/ or docs/ markdown. Accept absolute (Claude Code) or
# relative (test) paths. Exclude generated SVGs and the visuals dir.
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

# OPT-IN: no-op unless the project has adopted a comfort-posture. Walk up from the
# file's directory looking for .ravenclaude/comfort-posture.yaml (bounded).
posture_found=0
dir="$(cd "$(dirname "$file")" 2>/dev/null && pwd || true)"
for _ in 1 2 3 4 5 6 7 8 9 10; do
  [[ -z "$dir" ]] && break
  if [[ -f "$dir/.ravenclaude/comfort-posture.yaml" ]]; then posture_found=1; break; fi
  [[ "$dir" == "/" ]] && break
  dir="$(dirname "$dir")"
done
[[ "$posture_found" -eq 0 ]] && exit 0

# Specific unhedged-absolute capability phrasings (NOT a generic "cannot").
phrase='(you can'\''?t|it'\''?s impossible|impossible to|there'\''?s no way|there is no way|cannot be done|isn'\''?t possible|is not possible|not possible to|never works)'
# A conditional lead earlier on the line makes the phrase legitimate guidance.
conditional='\b(if|when|whenever|unless|because|since|until)\b'

violations=()
in_fence=0
in_frontmatter=0
lineno=0
first_nonblank_seen=0

while IFS= read -r line || [[ -n "$line" ]]; do
  lineno=$((lineno + 1))

  # YAML frontmatter: a leading `---` as the very first non-blank line opens it;
  # the next `---` closes it.
  if [[ "$first_nonblank_seen" -eq 0 && -n "${line// /}" ]]; then
    first_nonblank_seen=1
    if [[ "$line" == "---" ]]; then in_frontmatter=1; continue; fi
  fi
  if [[ "$in_frontmatter" -eq 1 ]]; then
    [[ "$line" == "---" ]] && in_frontmatter=0
    continue
  fi

  # Fenced code blocks (``` or ~~~) — toggle and skip their contents.
  if [[ "$line" =~ ^[[:space:]]*(\`\`\`|~~~) ]]; then
    in_fence=$((1 - in_fence)); continue
  fi
  [[ "$in_fence" -eq 1 ]] && continue

  # Blockquotes often quote bad examples / external text — skip.
  [[ "$line" =~ ^[[:space:]]*\> ]] && continue

  # Markdown headings are titles, not consequential platform claims (and often
  # carry idioms like "you can't manage what you don't track") — skip.
  [[ "$line" =~ ^[[:space:]]*#{1,6}[[:space:]] ]] && continue

  # Inline escape hatch.
  echo "$line" | grep -qiF 'claim-lint-ok' && continue

  # Does the line contain an absolute phrasing?
  if echo "$line" | grep -qiE "$phrase"; then
    # Suppress if it's a conditional ("if you can't…").
    echo "$line" | grep -qiE "$conditional" && continue
    # Suppress if the claim already carries a provenance marker on the line.
    echo "$line" | grep -qiE '\[unverified|verified this session|verified against' && continue
    trimmed="$(echo "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    violations+=("  $file:$lineno: $trimmed")
  fi
done < "$file"

if [[ ${#violations[@]} -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  Claim-grounding nudge — ${#violations[@]} unhedged absolute claim(s) written to:
       $file
EOF
  count=0
  for v in "${violations[@]}"; do
    echo "$v" >&2
    count=$((count + 1))
    [[ $count -ge 10 ]] && { echo "  …(more elided)" >&2; break; }
  done
  cat >&2 <<'EOF'

  An absolute capability claim in a knowledge/doc file becomes a durable PRIOR
  that the next session reads as verified fact. If you verified it THIS session,
  cite the check inline (the command + output, or file:line). If it's training
  knowledge, mark it `[unverified — training knowledge]` so the provenance is
  persisted — the marker spoken only in chat does not travel into the file.
  See plugins/ravenclaude-core/CLAUDE.md § "Claim Grounding & Source Honesty".

  Add `claim-lint-ok` on the line to suppress (e.g. a verified platform fact or a
  quoted example). This hook is ADVISORY — the write was not blocked.
────────────────────────────────────────────────────────────────────

EOF
fi

exit 0
