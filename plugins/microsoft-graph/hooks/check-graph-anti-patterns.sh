#!/usr/bin/env bash
# check-graph-anti-patterns.sh
# PreToolUse hook for Edit | Write | MultiEdit on Graph code / request files
# (.cs/.ts/.tsx/.js/.jsx/.py/.ps1/.http). Flags four mechanically-detectable
# violations of the microsoft-graph team constitution (see CLAUDE.md §3/§4):
#
#   1. `/beta` endpoint shipped to code (graph.microsoft.com/beta) — never ship beta
#      to production without flagging it (#9). [verify-at-build]
#   2. Hardcoded client secret in source (client_secret/ClientSecret = "<literal>")
#      — secrets are certificates/managed identity, never strings in code (#8). [security]
#   3. A write-`.All` / `Directory.*.All` permission scope — confirm least-privilege;
#      prefer delegated + the narrowest/resource-scoped permission (#1). [security]
#   4. An advanced query ($search= or $count=true) with no `ConsistencyLevel: eventual`
#      — the classic Graph 400; advanced queries require the eventual header + $count (#3/#4).
#
# Advisory by default: prints to stderr, exits 0. Set MSGRAPH_STRICT=1 to block (exit 2).
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

base_lc=$(basename "$file" | tr '[:upper:]' '[:lower:]')
case "$base_lc" in
  *.cs | *.ts | *.tsx | *.js | *.jsx | *.py | *.ps1 | *.http) ;;
  *) exit 0 ;;
esac

violations=()

# --- Check 1: /beta endpoint in code (#9) ---
if grep -Eiq 'graph\.microsoft\.com/beta' "$file"; then
  violations+=("[beta-endpoint] A /beta Graph endpoint is referenced. Don't ship /beta to production without flagging it — pin /v1.0, or document why beta is required + the retrieval date (CLAUDE.md §3 #9).")
fi

# --- Check 2: hardcoded client secret (#8) [security] ---
# A client_secret / ClientSecret assigned a non-empty quoted/!-env literal (not a
# variable reference, env lookup, or Key Vault / managed-identity placeholder).
if grep -Eiq '(client_secret|clientsecret)["'\'' ]*[=:][[:space:]]*["'\''][^"'\''$%{[:space:]][^"'\'' ]{6,}' "$file"; then
  violations+=("[hardcoded-secret] A client secret looks hardcoded in source. Secrets are certificates / managed identity, never strings in code or a notification URL (CLAUDE.md §3 #8). Escalate to ravenclaude-core/security-reviewer.")
fi

# --- Check 3: write-.All / Directory.*.All over-privilege (#1) [security] ---
if grep -Eoq '\b(Directory|Group|User|Application|RoleManagement|Sites|Files|Mail)\.[A-Za-z]*ReadWrite[A-Za-z.]*\.All\b|\bDirectory\.[A-Za-z.]*\.All\b' "$file"; then
  violations+=("[over-privilege] A broad write-'.All' permission scope is present. Confirm least-privilege: prefer delegated over application, and the narrowest or resource-scoped permission that works — never .ReadWrite.All where .Read or a resource scope suffices (CLAUDE.md §3 #1). This is a security control.")
fi

# --- Check 4: advanced query without ConsistencyLevel: eventual (#3/#4) ---
if grep -Eiq '\$search=|\$count=true' "$file" && ! grep -Eiq 'consistencylevel|eventual' "$file"; then
  violations+=("[advanced-query] An advanced query (\$search / \$count=true) is used without 'ConsistencyLevel: eventual'. Graph returns 400 for advanced queries that omit the eventual consistency header (and \$count). Add the header + \$count=true (CLAUDE.md §3 #3/#4).")
fi

[[ ${#violations[@]} -eq 0 ]] && exit 0

{
  echo "⚠️  microsoft-graph anti-pattern check — $file"
  for v in "${violations[@]}"; do echo "  • $v"; done
  echo "  Advisory by default. Set MSGRAPH_STRICT=1 to make these blocking."
} >&2

if [[ "${MSGRAPH_STRICT:-0}" == "1" ]]; then
  exit 2
fi
exit 0
