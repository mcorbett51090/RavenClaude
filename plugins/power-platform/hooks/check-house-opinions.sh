#!/usr/bin/env bash
# check-house-opinions.sh
# PostToolUse hook for Edit | Write | MultiEdit on Power Platform source files.
# Catches the most common, mechanically-detectable violations of the Power Platform
# team constitution (see plugins/power-platform/CLAUDE.md §3 "house opinions"):
#
#   1. GUIDs hard-coded in Power Fx canvas YAML — should look up by name or alt key.
#   2. Default publisher prefix (`cr_`, `crXXX_`, `new_`) in solution / customization XML.
#   3. Hard-coded tenant URLs (.sharepoint.com / .crm*.dynamics.com / .api.crm*.dynamics.com)
#      in any source file — should be in an environment variable.
#
# Advisory by default: prints warnings to stderr so Claude and the user both see them,
# but exits 0 so the edit is not blocked. To make this hook BLOCK on violation, change
# the final `exit 0` to `exit 1`.

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

# Only run on files in a Power Platform project. Heuristic: file lives under one of
# these conventional folders, OR has a Power-Platform-specific extension.
case "$file" in
  *CanvasApps/Src/*|*Solutions/*|*SolutionPackage/*|*src/*Solution*/*) ;;
  *.fx.yaml|*.pa.yaml|*solution.xml|*customizations.xml|*.cdsproj|*.msapp) ;;
  *) exit 0 ;;
esac

violations=()

# --- Check 1: GUIDs in Power Fx canvas YAML ---
# Power Fx convention: look up records by name or alternate key, never by GUID.
# Limit to canvas-app source so we don't false-flag metadata files where GUIDs are legitimate.
case "$file" in
  *.fx.yaml|*.pa.yaml|*CanvasApps/Src/*)
    if grep -Eni '"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"' "$file" >/dev/null 2>&1; then
      while IFS= read -r line; do
        violations+=("  [GUID-in-formula] $file: $line")
      done < <(grep -En '"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"' "$file" | head -5)
    fi
    ;;
esac

# --- Check 2: Default publisher prefix in solution / customization XML ---
case "$file" in
  *solution.xml|*customizations.xml)
    if grep -Eni '<CustomizationPrefix>(cr|crXXX|new)</CustomizationPrefix>' "$file" >/dev/null 2>&1; then
      violations+=("  [default-publisher-prefix] $file uses the default 'cr'/'new' publisher prefix. Pick something specific to your org (e.g. 'rvn', 'mc') — see CLAUDE.md §3 #5.")
    fi
    ;;
esac

# --- Check 3: Hard-coded tenant URLs in any Power Platform source file ---
# These should be in environment variables (see CLAUDE.md §3 #2).
if grep -Eni 'https?://[a-zA-Z0-9.-]+\.(sharepoint\.com|crm[0-9]*\.dynamics\.com|api\.crm[0-9]*\.dynamics\.com)' "$file" >/dev/null 2>&1; then
  while IFS= read -r line; do
    violations+=("  [hardcoded-tenant-url] $file: $line")
  done < <(grep -En 'https?://[a-zA-Z0-9.-]+\.(sharepoint\.com|crm[0-9]*\.dynamics\.com|api\.crm[0-9]*\.dynamics\.com)' "$file" | head -5)
fi

# --- Report ---
if [[ ${#violations[@]} -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  Power Platform house-opinion check flagged ${#violations[@]} issue(s) in:
       $file

EOF
  for v in "${violations[@]}"; do
    echo "$v" >&2
  done
  cat >&2 <<'EOF'

  See plugins/power-platform/CLAUDE.md §3 (house opinions) and §4
  (anti-patterns) for the full rules. This hook is advisory — the
  edit was not blocked. To enforce, change `exit 0` to `exit 1` at
  the bottom of plugins/power-platform/hooks/check-house-opinions.sh.
────────────────────────────────────────────────────────────────────

EOF
fi

exit 0
