#!/usr/bin/env bash
# flag-brand-antipatterns.sh
# PostToolUse hook for Edit | Write | MultiEdit on brand-conventional files.
# ADVISORY ONLY — prints warnings to stderr so Claude and the user both see them,
# but ALWAYS exits 0 so the edit is never blocked. Per the marketplace pattern,
# fail-closed hooks are infra-only (enforce-layout, route-decision-review); domain
# hooks like this one are advisory. The real workflow gates are the skill
# preconditions in plugins/brand-identity-studio/CLAUDE.md §4.
#
# Flags mechanically-detectable violations of the brand team constitution
# (see plugins/brand-identity-studio/CLAUDE.md §4 gates and §5 house opinions):
#
#   1. A non-self-hostable font (Adobe Fonts / Typekit / Monotype) referenced in a
#      brand / token / export-conventional file — those can't ship in a self-hosted
#      token export (§4 font-license class).
#   2. An un-curated concept marker in a client-facing brand file — a raw concept
#      must pass the human-curation gate before client handoff (§4 curation gate).
#   3. A logo regeneration-in-Firefly marker — the deliverable is the curated
#      vector, never a Firefly regen (§5.2 curate the vector).
#   4. Trademarkability / IP-transfer asserted without a security-reviewer / counsel
#      route in the same file (§5.5 route IP claims to security-reviewer).

set -euo pipefail

file="${1:-}"
# The edited file's path arrives via the canonical stdin JSON contract
# (.tool_input.file_path). hooks.json passes NO positional arg — there is no real
# Claude Code hook variable for it — so stdin is the sole source. ($1 is still read
# first for direct/manual invocation, but is empty under Claude Code.)
if [[ -z "$file" ]] && [[ ! -t 0 ]] && command -v jq >/dev/null 2>&1; then
  payload="$(cat 2>/dev/null || true)"
  if [[ -n "$payload" ]]; then
    file="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)"
  fi
fi
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

# Only run on brand-conventional files. Conservative — unrelated edits aren't flagged.
case "$file" in
  *brand*|*identity*|*token*|*brand-book*|*font*|*logo*|*palette*) ;;
  */brand/*|*/brand-identity/*|*/identity/*) ;;
  *) exit 0 ;;
esac

violations=()

# --- Check 1: non-self-hostable font referenced in a brand/token/export file ---
if grep -Eni 'fonts\.adobe\.com|use\.typekit\.net|typekit\.com|fast\.fonts\.net|fonts\.net/monotype' "$file" >/dev/null 2>&1; then
  violations+=("  [non-self-hostable-font] $file references an Adobe Fonts / Typekit / Monotype webfont. Those forbid or meter self-hosting — block them from the token export and record the class in the font-license-tracker (CLAUDE.md §4). Route the license claim to security-reviewer.")
fi

# --- Check 2: un-curated concept marker in a client-facing brand file ---
case "$file" in
  *brand-book*|*identity*|*brand*)
    if grep -Eni 'TODO:? *curate|un-?curated|raw concept|not (yet )?curated' "$file" >/dev/null 2>&1; then
      violations+=("  [un-curated-concept] $file carries an un-curated-concept marker. A raw concept must pass the human-curation + authorship gate (/curate-concepts) before client handoff (CLAUDE.md §4).")
    fi
    ;;
esac

# --- Check 3: logo regeneration-in-Firefly marker ---
if grep -Eni 'regenerat[a-z]* .*firefly|firefly .*(logo|wordmark|mark)|re-?generate .*(logo|wordmark)' "$file" >/dev/null 2>&1; then
  violations+=("  [logo-firefly-regen] $file suggests regenerating a logo/wordmark in Firefly. The deliverable is the CURATED VECTOR — never regenerate it (CLAUDE.md §5.2). Firefly-default is for fill/photographic imagery only.")
fi

# --- Check 4: trademarkability / IP-transfer asserted without a counsel route ---
if grep -Eni 'trademarkabl|you (now )?own the copyright|IP (transfers?|assignment)|is trademarked|copyright transfers?' "$file" >/dev/null 2>&1; then
  if ! grep -Eqi 'security-reviewer|counsel|not legal advice|clearance search' "$file" 2>/dev/null; then
    violations+=("  [ip-claim-unrouted] $file asserts an IP/trademarkability/ownership claim with no security-reviewer / counsel / not-legal-advice line in the same file. Route every client-facing IP claim to security-reviewer (CLAUDE.md §5.5).")
  fi
fi

# --- Report (advisory; never blocks) ---
if [[ ${#violations[@]} -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  Brand house-opinion check flagged ${#violations[@]} issue(s) in:
       $file

EOF
  for v in "${violations[@]}"; do
    echo "$v" >&2
  done
  cat >&2 <<'EOF'

  See plugins/brand-identity-studio/CLAUDE.md §4 (gates) and §5 (house
  opinions). This hook is ADVISORY — the edit was not blocked. The real
  workflow gates are the skill preconditions, not this hook.
────────────────────────────────────────────────────────────────────

EOF
fi

exit 0
