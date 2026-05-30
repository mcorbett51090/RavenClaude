#!/usr/bin/env bash
# flag-copilot-anti-patterns.sh
# PostToolUse hook for Write | Edit on Microsoft 365 Copilot extensibility source files.
# Catches the mechanically-detectable violations of the team constitution
# (see plugins/microsoft-365-copilot/CLAUDE.md §3 "house opinions"):
#
#   1. Declarative-agent manifest with no pinned $schema / version — §3 #2.
#   2. Manifest `instructions` block over the ~8,000-char budget — §3 #3 / #12.
#   3. Copilot-connector schema property with no semantic label — §3 #6.
#   4. Org-data grounding / connector design doc with no "Licensing impact" line — §3 #8.
#   5. RSS / RCD (Restricted SharePoint Search / Restricted Content Discovery)
#      described as a security boundary — §3 #9.
#
# Advisory by default: prints warnings to stderr so Claude and the user both see them,
# but exits 0 so the edit is not blocked. Set M365_COPILOT_STRICT=1 to make it BLOCK
# (exit 1) on any violation.

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

# Only run on Copilot-ish files: JSON/YAML manifests + Markdown design docs.
case "$file" in
  *.json|*.yaml|*.yml|*.md) ;;
  *) exit 0 ;;
esac

violations=()

# --- Helper: does this JSON look like a declarative-agent manifest? ---
# Heuristic: references the copilot/declarative-agent schema, or carries the
# declarative-agent shape (instructions + conversation_starters / capabilities).
is_da_manifest() {
  grep -Eqi 'declarative-?agent|copilot/extensibility|"conversation_starters"|"instructions"[[:space:]]*:' "$1" 2>/dev/null
}

# --- Helper: does this JSON look like a Copilot connector schema? ---
is_connector_schema() {
  grep -Eqi '"externalConnectors"|"semanticLabels?"|"propertyType"|microsoft\.graph\.externalItem|"labels"[[:space:]]*:[[:space:]]*\[' "$1" 2>/dev/null
}

# --- Check 1: DA manifest without a pinned $schema / version (§3 #2) ---
case "$file" in
  *.json)
    if is_da_manifest "$file"; then
      # A pinned manifest names a concrete version: $schema URL ending in vN.N(.N) or a
      # "schema_version"/"version" field with a dotted version literal.
      if ! grep -Eqi '("\$schema"[^,]*v[0-9]+\.[0-9]+|"schema_version"[[:space:]]*:[[:space:]]*"[0-9]+\.[0-9]+|"version"[[:space:]]*:[[:space:]]*"[0-9]+\.[0-9]+)' "$file" 2>/dev/null; then
        violations+=("  [unpinned-manifest-schema] $file looks like a declarative-agent manifest but has no pinned \$schema / schema_version (e.g. v1.7). 'latest' is a moving target — the manifest ships ~monthly. Pin it. See CLAUDE.md §3 #2.")
      fi
    fi
    ;;
esac

# --- Check 2: instructions block over the ~8,000-char budget (§3 #3 / #12) ---
# Mechanical proxy: the value of an "instructions" string field. We measure the
# longest single "instructions": "..." literal on one logical region.
case "$file" in
  *.json)
    if is_da_manifest "$file"; then
      # Extract the instructions value (single-line JSON literal) and measure length.
      longest=$(grep -Eo '"instructions"[[:space:]]*:[[:space:]]*"([^"\\]|\\.)*"' "$file" 2>/dev/null \
                | awk '{ print length, $0 }' | sort -rn | head -1 | cut -d' ' -f1)
      if [[ -n "${longest:-}" && "$longest" -gt 8000 ]]; then
        violations+=("  [instructions-over-budget] $file has an \"instructions\" value ~${longest} chars — over the ~8,000-char declarative-agent budget. Trim or move detail to grounding. See CLAUDE.md §3 #3 / #12.")
      fi
    fi
    ;;
esac

# --- Check 3: Copilot-connector schema property with no semantic label (§3 #6) ---
# Mechanical proxy: a connector schema that declares properties but never declares a
# label / labels attribute anywhere. Semantic labels (title/url/createdBy/...) are
# mandatory for ranking + citation.
case "$file" in
  *.json)
    if is_connector_schema "$file"; then
      if grep -Eqi '"properties?"[[:space:]]*:' "$file" 2>/dev/null; then
        if ! grep -Eqi '"labels?"[[:space:]]*:|"semanticLabels?"' "$file" 2>/dev/null; then
          violations+=("  [connector-no-semantic-labels] $file looks like a Copilot connector schema with properties but no semantic labels (title/url/createdBy/...). Semantic labels are mandatory — they carry ranking + citation. See CLAUDE.md §3 #6.")
        fi
      fi
    fi
    ;;
esac

# --- Check 4: org-data grounding / connector design doc with no licensing line (§3 #8) ---
# Mechanical proxy: a Markdown doc that talks about grounding on org data
# (connector / SharePoint knowledge / OneDrive) but never says "Licensing impact".
case "$file" in
  *.md)
    if grep -Eqi 'copilot connector|graph connector|sharepoint knowledge|onedrive knowledge|ground(ing)? on (org|tenant|company) data|knowledge source' "$file" 2>/dev/null; then
      if ! grep -qi 'Licensing impact' "$file" 2>/dev/null; then
        violations+=("  [missing-licensing-impact] $file discusses grounding on org data but has no 'Licensing impact:' line. Org-data grounding is license-gated — state the license story. See CLAUDE.md §3 #8.")
      fi
    fi
    ;;
esac

# --- Check 5: RSS / RCD sold as a security boundary (§3 #9) ---
case "$file" in
  *.md)
    if grep -Eni '(restricted (sharepoint )?search|restricted content discovery|\bRSS\b|\bRCD\b)[^.\n]{0,80}(security boundary|access control|prevents access|blocks access|stops (a )?user)' "$file" >/dev/null 2>&1; then
      while IFS= read -r line; do
        violations+=("  [rss-rcd-not-a-boundary] $file: $line")
      done < <(grep -Eni '(restricted (sharepoint )?search|restricted content discovery|\bRSS\b|\bRCD\b)[^.\n]{0,80}(security boundary|access control|prevents access|blocks access|stops (a )?user)' "$file" | head -5)
      violations+=("  ^ RSS/RCD are NOT security boundaries — they reduce Copilot's reach, not a user's existing access. See CLAUDE.md §3 #9.")
    fi
    ;;
esac

# --- Report ---
if [[ ${#violations[@]} -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  M365 Copilot house-opinion check flagged ${#violations[@]} issue(s) in:
       $file

EOF
  for v in "${violations[@]}"; do
    echo "$v" >&2
  done
  cat >&2 <<'EOF'

  See plugins/microsoft-365-copilot/CLAUDE.md §3 (house opinions) and §4
  (anti-patterns) for the full rules. This hook is advisory — the edit was
  not blocked. Set M365_COPILOT_STRICT=1 to make it blocking.
────────────────────────────────────────────────────────────────────

EOF
  if [[ "${M365_COPILOT_STRICT:-0}" == "1" ]]; then
    exit 1
  fi
fi

exit 0
