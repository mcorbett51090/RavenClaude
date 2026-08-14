#!/usr/bin/env bash
# claim-grounding-lint.sh
# PostToolUse hook for Edit | Write | MultiEdit. ADVISORY nudge (never blocks)
# when an UNHEDGED ABSOLUTE capability claim is written into a knowledge/ or
# docs/ markdown file without an inline provenance marker. Implements the
# enforced-complement of the Claim Grounding & Source Honesty protocol
# (plugins/ravenclaude-core/CLAUDE.md): a confident-wrong "you can't…" baked into
# a knowledge file becomes a durable false prior the next session trusts.
#
# It carries TWO independent checks over the same scan:
#   1. UNHEDGED ABSOLUTE  — "you can't…", "it's impossible…" with no marker.
#   2. CONTRACT PROVENANCE (added by PR 9 / defect P15 "building to an unverified
#      contract") — a capability/contract claim about some OTHER system ("X does
#      not support Y", "Z is supported", "W has no public API") written down with
#      no inline provenance marker. That is the shape that turns an unverified
#      belief into a durable contract the next session builds against.
#
# HONEST SCOPE (read this — it bounds BOTH checks): this hook can only see
# WRITTEN FILE CONTENT — never the chat answer, which is where the confident
# error usually lands. It is one narrow, defense-in-depth surface (the
# durable-artifact case), NOT a control, and specifically NOT contract
# verification: it cannot tell a true claim from a false one, only a *marked*
# claim from an unmarked one. A hook that claimed to verify contracts would
# itself be exactly the false claim this protocol exists to stop. It is ADVISORY
# (exit 0 always), OPT-IN (no-op unless the project has a
# .ravenclaude/comfort-posture.yaml), and FAIL-SAFE (any error -> exit 0).
#
# Deliberately OUT OF SCOPE for check 2 (stated so the gap is not mistaken for
# coverage): generators and other non-markdown sources. Detecting a claim inside
# a .py/.sh comment needs a second, code-shaped skip machinery, and the whole
# point of this hook's low false-positive rate is the markdown machinery below.
# Check 2 is the durable-artifact subset only.
#
# False-positive discipline (Panel C): scoped to knowledge/**+docs/** .md only
# (excludes *.svg + concepts/visuals/**); skips YAML frontmatter, fenced code
# blocks, and blockquotes (where bad-examples are quoted); suppresses conditional
# phrasings ("if you can't…"); honors an inline `claim-lint-ok` escape comment;
# and matches a SPECIFIC set of absolute phrasings, not a generic "cannot".
# Check 2's pattern set + its two extra suppressions were derived from a dry run
# over the whole live knowledge/+docs/ tree (1,162 files) with every finding
# hand-classified — not from invented fixtures. See the header of the
# contract-provenance block below for what that measurement threw out.

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
# SELF-NON-RECURSION (deliberate + visible). This hook's own source and its
# sibling hooks are not lintable material: this file's header necessarily SPELLS
# OUT the very phrasings it matches ("does not support …"), so a lint that ever
# reached it would flag itself forever. The .md scope above already excludes .sh,
# so this case is belt-and-suspenders — it stays because the failure it prevents
# is silent and self-inflicted. Do not delete it when widening the scope.
case "$file" in
  */hooks/claim-grounding-lint.sh | */hooks/*) exit 0 ;;
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

# ── Check 2: contract-provenance (PR 9 / P15) ────────────────────────────────
# A SPECIFIC set of capability/contract phrasings, not a generic "supports".
# Everything below survived a hand-classified dry run over the live tree; the
# candidates it THREW OUT are the useful part of the record:
#   "natively" (58 hits, ~all prose), "defaults to"/"the default is" (31 hits,
#   ~13% precision — mostly our own flags), "(supports|accepts|returns) only"
#   (32 hits, ~all `grep` result counts), "added/introduced in <version>" (3
#   hits, all doc-changelog rows). Each was measured, not guessed, and each was
#   dropped for precision. Do not re-add one without re-running the dry run.
contract='(does not|doesn'\''?t|do not|don'\''?t) support|(is|are|was|were) (not )?supported|ha(s|ve) no (native|public|documented|official|supported)'
# Inline provenance markers that make the claim grounded. `[verify-at-…` and a
# bare ISO date are here because the dry run produced REAL false positives on
# lines that carried them — this repo already writes provenance in those forms.
provenance='\[docs-verified|\[verify-at-|\[unverified|\bverified\b|20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
# Sense disambiguation: "supported BY evidence/sources/documents" is the
# evidentiary sense of the word, not a capability claim. 4 real hits.
contract_sense='supported by'
# Elided-object rule: a genuine contract claim NAMES what is unsupported ("does
# not support MERGE", "does not support PCRE lookahead"). When the verb ends the
# clause with no object, the sense is evidentiary/rhetorical ("a count the
# sources don't support."). Measured: suppresses 3 real false positives and
# ZERO true findings.
contract_elided='support(ed)?[[:space:])".,;:]*$'

violations=()
contract_violations=()
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

  # Check 2 — contract provenance. Independent of check 1 (a line can trip both
  # or either). Uses the same $file the stdin/arg parse already resolved above
  # — no second stdin read (a duplicate parse would desync the two checks).
  # Ordered cheapest-first: the contract match gates every other subprocess,
  # so a non-matching line costs exactly one grep.
  if echo "$line" | grep -qiE "$contract"; then
    # Same conditional carve-out as check 1 ("when X doesn't support Y" is
    # guidance, not an asserted contract).
    echo "$line" | grep -qiE "$conditional" && continue
    # Already carries an inline provenance marker -> grounded, stay silent.
    echo "$line" | grep -qiE "$provenance" && continue
    # "supported by <evidence>" — wrong sense of the word.
    echo "$line" | grep -qiE "$contract_sense" && continue
    # Verb ends the clause with no object -> evidentiary/rhetorical sense.
    echo "$line" | grep -qiE "$contract_elided" && continue
    trimmed2="$(echo "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    contract_violations+=("  $file:$lineno: $trimmed2")
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

if [[ ${#contract_violations[@]} -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  Contract-provenance nudge — ${#contract_violations[@]} unmarked capability/contract claim(s) in:
       $file
EOF
  count=0
  for v in "${contract_violations[@]}"; do
    echo "$v" >&2
    count=$((count + 1))
    [[ $count -ge 10 ]] && { echo "  …(more elided)" >&2; break; }
  done
  cat >&2 <<'EOF'

  A claim about ANOTHER system's contract ("X does not support Y", "Z is
  supported", "W has no public API") is the shape that gets BUILT AGAINST. Once
  it is in a knowledge/doc file it reads as verified fact, and the code written
  to it inherits the error silently.

  Mark the provenance INLINE, on the line, so it travels with the claim:
    • `[docs-verified 2026-08-13]`  — you read the vendor's docs this session
    • `<url> (retrieved 2026-08-13)` — a source plus the date you fetched it
    • `[unverified — training knowledge]` — you are recalling it, not checking it
    • `[verify-at-use — 2026-08-13]`  — true when written, re-check before acting
  A marker spoken only in chat does not travel into the file.

  THIS HOOK DOES NOT VERIFY ANYTHING. It cannot tell a true claim from a false
  one — only a marked claim from an unmarked one. It is ADVISORY; the write was
  not blocked. Add `claim-lint-ok` on the line to suppress.
────────────────────────────────────────────────────────────────────

EOF
fi

exit 0
